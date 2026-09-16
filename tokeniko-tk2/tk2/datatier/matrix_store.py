"""THE BASE'S DOOR — a `MatrixStore` that keeps R (and, at T4, D) in the body's database.

It lives HERE and not in `tk2/dictionary/` for the reason the whole package is arranged around:
the dictionary is pure logic and imports no database, so the store it writes through is injected.
This is that store, on the mongo side of the seam.

IT WRITES THROUGH THE MIGRATION DOOR. The base is `logic` — the body reads it and never writes it —
so its only writer is a build, and a build reaches r-class rows the way a deploy does: validated by
the model, executed by raw pymongo, never through the ODM's write path. There is no flag here that
could let a running body through; there is no path here that a running body calls.

ONE KEY SPACE PER BUILD, enforced rather than assumed. R and D are two matrices over ONE order, and
that shared order is the only reason a reader can compare them cell for cell. So the registry is
written once per build and a second matrix that disagrees with it is refused — an unnoticed
disagreement would not look like an error, it would look like every cell being about another word.

**A MATRIX IS SEALED, OR IT DOES NOT EXIST (T5).** D is 218 MB of BSON that pymongo splits into
several wire messages, sent over a network to a body in another room; an interruption anywhere in
that leaves a partial matrix under a build label, and a partial matrix does not look wrong. Every
row is valid, the registry is there, the manifest is simply missing — and nothing ever asked. So the
write has three properties now, and all three are the same idea:

  1. it goes out in CHUNKS, each one small enough to be a single wire message, so a failure names a
     place rather than a two-hundred-megabyte range;
  2. the seal — `base_seals`, one row per (build, matrix) — is written LAST, after the stored rows
     have been counted BACK OUT of the database and agreed with what was sent;
  3. every reader here refuses a build whose matrix has no seal.

The consequence is the property worth having: an interrupted apply produces a base that does not
READ, rather than a base that reads wrong. Re-running the write is then the whole recovery — it
breaks the seal first, so a rewrite in progress is unreadable for exactly as long as it is partial.
"""

import hashlib
from typing import Iterator

from pymongo.database import Database

from tk2.core.models import BaseDistributionDoc, BaseKeyDoc, BaseRelationDoc, BaseSealDoc
from tk2.datatier.migration_writer import MigrationWriter
from tk2.dictionary import keys, matrix as matrix_module
from tk2.dictionary.senses import SENSE_LAYER, fingerprint as sense_fingerprint
from tk2.dictionary.matrix import Cell, Matrix, MatrixRow

#: Which collection holds which matrix. D joined at T4 — one line, because the shape is the same
#: and the difference between R and D is what fills them, never how they are kept.
MATRIX_MODELS = {
    BaseRelationDoc.Settings.name: BaseRelationDoc,
    BaseDistributionDoc.Settings.name: BaseDistributionDoc,
}

#: How much of a matrix goes out in one `insert_many`. Eight megabytes is chosen against the wire
#: rather than against the disk: mongo's message limit is 48 MB, so a chunk this size is ALWAYS one
#: message and never a split pymongo performs on its own — which is what makes «the write stopped
#: after chunk 14» a true statement rather than a guess about the driver's batching. It also caps
#: what the validator holds in memory at one chunk instead of the whole matrix.
CHUNK_BYTES = 8 * 1024 * 1024

#: A ceiling in rows as well, because the estimate below is an estimate: a build whose rows are all
#: tiny would otherwise send one enormous chunk on the strength of an arithmetic that was wrong.
CHUNK_ROWS = 500

#: What one stored cell is reckoned to cost on the wire, for the chunker's arithmetic only. A cell
#: is a subdocument of five short fields plus a `via` list; ~120 bytes is the measured order of it
#: at this base (218.8 MB over 1.72 M stored cells). Nothing depends on it being right — it decides
#: how big a chunk is, never whether a write is correct.
CELL_BYTES = 120

#: And what a row costs before its cells: `_id`, the build label, the key, the index.
ROW_BYTES = 96


class KeySpaceConflict(RuntimeError):
    """A build already has a dimension order, and this matrix disagrees with it."""


class BaseIncomplete(RuntimeError):
    """A matrix was asked for that no seal vouches for.

    Raised on READ, which is the whole point: a partial base must be unreadable rather than
    plausible. Either the write never finished (re-run it — a build is reproducible from its policy
    rows, which is what the fingerprint in the manifest is for), or the rows were written by
    something that is not this store.
    """


class MongoMatrixStore:
    """Keeps built matrices in a named database. The caller has already guarded the name."""

    def __init__(self, database: Database):
        self._db = database
        self._writer = MigrationWriter(database)

    @property
    def database(self) -> Database:
        """The handle this store was given. A tool that verifies a base also reads the LEDGER beside
        it, and reaching through the writer for that would be a caller using a private door."""
        return self._db

    # -- writing -------------------------------------------------------------------------------

    def write(self, matrix: Matrix, build: str, progress=None) -> int:
        """Store a matrix under a build label, replacing that build's copy of it, and SEAL it.

        Replacing rather than appending: a build label names one measurement, and two half-written
        copies under one label would be a base nobody could read. The registry is written first,
        because a matrix whose dimensions are not recorded is a set of numbers with no meaning.

        THE ORDER OF THE FOUR STEPS IS THE DESIGN. The seal goes first — before a single row is
        touched — so that a rewrite is unreadable from its first moment rather than from its first
        failure; the old rows go next; the new ones go out in chunks; and the seal is re-made only
        after the database has been asked how many rows it actually holds. A writer that sealed from
        its own count would be vouching for what it believed it sent.

        `progress` is called with (chunk, chunks, rows so far) — a build tool has a person watching
        two hundred megabytes cross a network, and silence for four minutes is indistinguishable
        from a hang.
        """
        model = self._model(matrix.name)
        self.write_keys(matrix.keys, build)

        self._break_seal(build, matrix.name)
        collection = self._writer.collection(model)
        collection.delete_many({"build": build})

        rows = matrix.rows
        chunks = list(_chunked(rows, cost=lambda row: ROW_BYTES + CELL_BYTES * len(row.cells)))
        written = 0
        for position, chunk in enumerate(chunks, start=1):
            # The documents are made HERE, one chunk at a time, and not in one list before the loop:
            # the matrix is already in memory once, and a second whole copy of it as dicts is what
            # made the T4 apply's peak what it was.
            self._writer.insert_many(model, [
                {
                    "build": build,
                    "key": row.key,
                    "index": row.index,
                    "cells": [cell.as_row() for cell in row.cells],
                }
                for row in chunk
            ])
            written += len(chunk)
            if progress is not None:
                progress(position, len(chunks), written)

        stored = collection.count_documents({"build": build})
        if stored != len(rows):
            raise BaseIncomplete(
                f"{matrix.name} under build {build!r} was sent {len(rows):,} rows and the database "
                f"holds {stored:,}. NOT SEALED: an incomplete matrix stays unreadable rather than "
                f"becoming a base that reads wrong. Re-run the write."
            )

        self._writer.insert(
            BaseSealDoc,
            {
                "build": build,
                "name": matrix.name,
                "rows": stored,
                "cells": matrix_module.cell_count(matrix),
                "fingerprint": matrix_module.fingerprint(matrix),
                "note": f"{len(chunks)} chunk(s) of at most {CHUNK_ROWS} rows / "
                        f"{CHUNK_BYTES // (1024 * 1024)} MB",
            },
        )
        return len(rows)

    def write_senses(self, placed, build: str, progress=None) -> int:
        """Store the SENSE LAYER under a build label, and seal it like a matrix.

        Same four steps in the same order as `write`, for the same reason: seal off, delete, chunk,
        count back, seal. A sense layer is not a matrix — it is not square and never will be — but a
        half-written one is exactly as unreadable as a half-written matrix, so it earns the same
        protection rather than a lighter one because its shape is different.

        Chunked by the cells a row actually carries, not by a row count: a sense placed by fourteen
        base words and one by none are two very different documents, and a fixed chunk size would be
        sized for the wrong one.
        """
        from tk2.core.models import SenseVectorDoc

        self._break_seal(build, SENSE_LAYER)
        collection = self._writer.collection(SenseVectorDoc)
        collection.delete_many({"build": build})

        chunks = list(_chunked(
            list(placed),
            cost=lambda s: ROW_BYTES + CELL_BYTES * (len(s.distribution) + len(s.relations)),
        ))
        written = cells = 0
        for position, chunk in enumerate(chunks, start=1):
            self._writer.insert_many(SenseVectorDoc, [
                {
                    "build": build,
                    "key": sense.key,
                    "base": sense.base,
                    "ordinal": sense.ordinal,
                    "synset": sense.synset,
                    "definition": sense.definition,
                    "distribution": [cell.as_row() for cell in sense.distribution],
                    "relations": [cell.as_row() for cell in sense.relations],
                }
                for sense in chunk
            ])
            written += len(chunk)
            cells += sum(len(s.distribution) + len(s.relations) for s in chunk)
            if progress is not None:
                progress(position, len(chunks), written)

        stored = collection.count_documents({"build": build})
        self._writer.insert_many(BaseSealDoc, [{
            "build": build,
            "name": SENSE_LAYER,
            "rows": stored,
            "cells": cells,
            "fingerprint": sense_fingerprint(placed),
        }])
        return stored

    def origin(self, build: str, policy_version: int | None = None,
               closed_class_version: int | None = None):
        """THE DIRTY-CHECK: what a loaded space would have to match to still be current.

        ONE query over `dictionary_base_seals`, which is three or four rows — measured at about the
        cost of a single row read (6.8 ms against the body over the network) against the seven
        seconds a reload costs. That ratio is the whole reason this exists: a tick can afford to ASK
        every time and no tick can afford to reload, so the question and the answer live apart.

        The seals are the right thing to compare, and not the build label alone, because a curated
        edge changes a matrix's content UNDER the same label — `curate_dictionary.py approve` calls
        `write`, and `write` re-seals. A check that watched only the label would go on serving a
        base the Captain had already corrected by hand.

        `closed_class_version` is the fourth thing that moves it, added 2026-09-16 on the Captain's
        «fix it now, before any v7»: the closed-class forms filter D's vocabulary, so a table
        migration changes what D would be built from — and no seal, label or policy version records
        it. Passed in rather than read here, because this store holds matrices and the closed
        classes are the language package's table; a store that went looking for them would be
        reaching across a seam this file does not own.
        """
        from tk2.dictionary.space import SpaceOrigin

        found = self.seals(build)
        return SpaceOrigin(
            build=build,
            seals=tuple(sorted((name, seal.get("fingerprint", "")) for name, seal in found.items())),
            policy_version=policy_version,
            closed_class_version=closed_class_version,
        )

    def senses(self, build: str, base: str | None = None) -> list[dict]:
        """The sense layer back, or just the readings of one base dimension.

        REFUSES AN UNSEALED LAYER, exactly as a matrix read does. «Every sense of `small.a`» is the
        question the station will ask most, so `base` is a first-class argument rather than a filter
        the caller is left to write — and the index is built for it.
        """
        from tk2.core.models import SenseVectorDoc

        self._require_seal(build, SENSE_LAYER)
        query = {"build": build}
        if base is not None:
            query["base"] = base
        return list(
            self._db[SenseVectorDoc.Settings.name]
            .find(query, {"_id": 0})
            .sort([("base", 1), ("ordinal", 1)])
        )

    def write_keys(self, dimensions, build: str) -> int:
        """THE dimension order of a build. Idempotent, and loud when it is asked to change.

        Returns how many rows were written — zero when the registry was already there and agreed,
        which is the normal case for the second matrix of a build.

        Sealed like a matrix, and for the same reason with one extra edge: the registry is what
        every cell's column MEANS, so a half-written one is not a smaller key space, it is a base
        whose rows point at the wrong words. Its seal carries no fingerprint — the registry is its
        own content, and it is compared as the ordered list it is.
        """
        dimensions = tuple(dimensions)
        existing = self._stored_keys(build)
        if existing:
            if existing != dimensions:
                raise KeySpaceConflict(
                    f"build {build!r} already holds {len(existing)} dimensions and this matrix has "
                    f"{len(dimensions)} in a different order. R and D share ONE key space; two "
                    f"orders would make every cell of every row point at another word."
                )
            if self.seal(build, BaseKeyDoc.Settings.name) is None:
                # An interrupted write left a registry nobody vouched for, and this call has just
                # PROVED it is the right one — `existing == dimensions` is the whole key space in
                # index order, so a missing or re-ordered row could not have got here. A writer can
                # heal that and a reader cannot, which is exactly why the refusal lives on the read.
                self._seal_registry(build, len(existing), "the dimension order, re-sealed")
            return 0

        self._break_seal(build, BaseKeyDoc.Settings.name)
        collection = self._writer.collection(BaseKeyDoc)
        collection.delete_many({"build": build})
        rows = []
        for index, key in enumerate(dimensions):
            word, pos = keys.split_key(key)
            rows.append({"build": build, "key": key, "word": word, "pos": pos, "index": index})
        for chunk in _chunked(rows):
            self._writer.insert_many(BaseKeyDoc, chunk)

        stored = collection.count_documents({"build": build})
        if stored != len(rows):
            raise BaseIncomplete(
                f"the dimension registry of build {build!r} was sent {len(rows):,} rows and the "
                f"database holds {stored:,}. NOT SEALED — see BaseIncomplete."
            )
        self._seal_registry(build, stored, "the dimension order")
        return len(rows)

    def _seal_registry(self, build: str, rows: int, note: str) -> None:
        self._writer.insert(
            BaseSealDoc,
            {"build": build, "name": BaseKeyDoc.Settings.name, "rows": rows, "cells": 0,
             "fingerprint": "", "note": note},
        )

    def drop(self, build: str) -> dict[str, int]:
        """Remove a build entirely — its seals first, then its rows. THE RECOVERY, as a method.

        First because the order is `write`'s own: a build stops being readable before it stops being
        there, so a drop that is itself interrupted leaves an unreadable partial rather than a
        readable half. Returns what went, by collection, because a drop that removed nothing is a
        build label somebody mistyped.
        """
        from tk2.core.models import SenseVectorDoc

        self._writer.collection(BaseSealDoc).delete_many({"build": build})
        gone = {}
        # THE SENSE LAYER IS PART OF A BUILD AND WAS MISSING FROM THIS LIST until 2026-09-14, when
        # dropping the superseded build left 120,475 orphaned sense rows behind — rows under a build
        # label whose keys, matrices and seals were gone, which no reader can use and no verifier
        # would ever mention. `MATRIX_MODELS` is the two SQUARE matrices by design (the sense layer
        # rides on the dimensions and is never square), so it is named here explicitly.
        for model in (BaseKeyDoc, *MATRIX_MODELS.values(), SenseVectorDoc):
            gone[model.Settings.name] = self._writer.collection(model).delete_many(
                {"build": build}
            ).deleted_count
        return gone

    # -- the seal ------------------------------------------------------------------------------

    def seal(self, build: str, name: str) -> dict | None:
        """The seal on one matrix of one build, or `None` when there is none — which is the same
        answer as «that matrix is not there», and deliberately so."""
        return self._writer.collection(BaseSealDoc).find_one({"build": build, "name": name})

    def seals(self, build: str) -> dict[str, dict]:
        """Every seal a build holds, by matrix name. What a verifier lists and what a reader checks."""
        return {row["name"]: row
                for row in self._writer.collection(BaseSealDoc).find({"build": build})}

    def is_sealed(self, build: str, name: str) -> bool:
        return self.seal(build, name) is not None

    def _break_seal(self, build: str, name: str) -> None:
        """Take the seal off before touching a row. A matrix being rewritten is not readable, and
        the window in which that is true has to start before the first `delete_many`, not after the
        last insert fails."""
        self._writer.collection(BaseSealDoc).delete_many({"build": build, "name": name})

    def _require_seal(self, build: str, name: str) -> dict:
        found = self.seal(build, name)
        if found is None:
            raise BaseIncomplete(
                f"no seal for {name!r} under build {build!r}: nothing vouches that this matrix "
                f"arrived whole, so it does not read. A build seals each matrix after counting its "
                f"rows back out of the database ({self._db.name}.{BaseSealDoc.Settings.name}); "
                f"either the write was interrupted, or these rows were not written by this store."
            )
        return found

    # -- reading -------------------------------------------------------------------------------

    def keys(self, build: str, name: str | None = None) -> tuple[str, ...]:
        """The build's dimension order. `name` is accepted and ignored on purpose: the store's
        protocol asks per matrix, and the honest answer here is that a build has ONE key space."""
        self._require_seal(build, BaseKeyDoc.Settings.name)
        return self._stored_keys(build)

    def _stored_keys(self, build: str) -> tuple[str, ...]:
        """The registry as it stands, seal or no seal — for the writer, which is the one caller that
        has to be able to look at a half-written build."""
        found = self._writer.collection(BaseKeyDoc).find({"build": build}, {"key": 1, "index": 1})
        return tuple(row["key"] for row in sorted(found, key=lambda row: row["index"]))

    def stored_rows(self, build: str, name: str) -> int:
        """How many rows are actually there — seal or no seal.

        The one count that must work on a build nothing vouches for: a verifier has to be able to
        say «this build holds 2,140 rows of base_d and no seal», which is precisely the state the
        seal exists to make visible.
        """
        model = BaseKeyDoc if name == BaseKeyDoc.Settings.name else self._model(name)
        return self._writer.collection(model).count_documents({"build": build})

    def rows(self, build: str, name: str) -> Iterator[MatrixRow]:
        self._require_seal(build, name)
        collection = self._writer.collection(self._model(name))
        for stored in collection.find({"build": build}).sort("index", 1):
            yield _row_of(stored)

    def row(self, build: str, name: str, key: str) -> MatrixRow | None:
        self._require_seal(build, name)
        stored = self._writer.collection(self._model(name)).find_one({"build": build, "key": key})
        return _row_of(stored) if stored else None

    def matrix(self, build: str, name: str) -> Matrix:
        """The whole matrix back in memory — for a bar run, which needs every row's neighbours."""
        return Matrix(name=name, keys=self.keys(build), rows=tuple(self.rows(build, name)))

    def builds(self, name: str | None = None) -> tuple[str, ...]:
        """Every build label present, so a reader never has to guess one. Sealed or not: a verifier
        has to be able to FIND the partial build in order to say that it is one."""
        model = self._model(name) if name else BaseKeyDoc
        return tuple(sorted(self._writer.collection(model).distinct("build")))

    # -- verifying -----------------------------------------------------------------------------

    def verify(self, build: str, name: str) -> dict:
        """Read a stored matrix back and check it against its own seal.

        THE ROUND TRIP, and it is not what the reader does on every call: reading 4,445 rows and
        hashing 1.7 million cells is a minute's work, and a check that expensive on every read would
        simply stop being run. So the cheap invariant (a seal exists) guards every read, and this is
        the instrument that answers «and is it the matrix that left?» — after an apply, and whenever
        a number looks wrong.
        """
        sealed = self._require_seal(build, name)
        stored = Matrix(name=name, keys=self._stored_keys(build),
                        rows=tuple(_row_of(row) for row in
                                   self._writer.collection(self._model(name))
                                   .find({"build": build}).sort("index", 1)))
        recomputed = matrix_module.fingerprint(stored)
        cells = matrix_module.cell_count(stored)
        return {
            "build": build,
            "name": name,
            "rows": len(stored.rows),
            "rows_sealed": sealed["rows"],
            "cells": cells,
            "cells_sealed": sealed["cells"],
            "fingerprint": recomputed,
            "fingerprint_sealed": sealed["fingerprint"],
            "whole": (len(stored.rows) == sealed["rows"] and cells == sealed["cells"]
                      and recomputed == sealed["fingerprint"]),
        }

    def verify_keys(self, build: str) -> dict:
        """The dimension registry against its seal: the count, and that the indices are 0..n-1 with
        no gap. A registry with a hole is a key space in which every index past the hole means the
        wrong word, and no cell would look wrong."""
        sealed = self._require_seal(build, BaseKeyDoc.Settings.name)
        dimensions = self._stored_keys(build)
        indices = sorted(row["index"] for row in
                         self._writer.collection(BaseKeyDoc).find({"build": build}, {"index": 1}))
        contiguous = indices == list(range(len(indices)))
        return {
            "build": build,
            "name": BaseKeyDoc.Settings.name,
            "rows": len(dimensions),
            "rows_sealed": sealed["rows"],
            "contiguous": contiguous,
            "digest": hashlib.sha256("\n".join(dimensions).encode("utf-8")).hexdigest(),
            "whole": len(dimensions) == sealed["rows"] and contiguous,
        }

    # ------------------------------------------------------------------------------------------

    @staticmethod
    def _model(name: str):
        try:
            return MATRIX_MODELS[name]
        except KeyError:
            raise KeyError(
                f"no collection is declared for a matrix named {name!r}; known: "
                f"{sorted(MATRIX_MODELS)}"
            ) from None


def _chunked(rows, cost=None, chunk_bytes: int | None = None, chunk_rows: int | None = None):
    """The rows in pieces, each small enough to be one message on the wire.

    Budgeted by an ESTIMATE of the encoded size rather than by encoding twice: the wire is the
    authority on what a document costs, and the only thing riding on this arithmetic is how many
    pieces there are. A row wider than the whole budget still goes out on its own, because the
    alternative — refusing it — would be this function inventing a size limit mongo does not have.

    `cost` lets the caller chunk the objects it has rather than the documents it has not built yet;
    without one, a row is a plain document and its cells are counted off it.
    """
    if cost is None:
        def cost(row):
            return ROW_BYTES + CELL_BYTES * len(row.get("cells", ()))

    # Read off the module rather than bound as defaults: the budget is a constant a test has to be
    # able to move, and a default argument would freeze it at import.
    chunk_bytes = CHUNK_BYTES if chunk_bytes is None else chunk_bytes
    chunk_rows = CHUNK_ROWS if chunk_rows is None else chunk_rows

    current: list = []
    size = 0
    for row in rows:
        weight = cost(row)
        if current and (size + weight > chunk_bytes or len(current) >= chunk_rows):
            yield current
            current, size = [], 0
        current.append(row)
        size += weight
    if current:
        yield current


def _row_of(stored) -> MatrixRow:
    return MatrixRow(
        key=stored["key"],
        index=stored["index"],
        cells=tuple(Cell.from_row(cell) for cell in stored.get("cells", ())),
    )
