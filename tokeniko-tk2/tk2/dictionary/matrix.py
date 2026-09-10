"""THE MATRIX — what a square base matrix IS, and the door it is kept behind.

R and D are two matrices of the same shape over ONE key space, so the shape belongs to neither of
them: `relations.py` fills R, `distribution.py` fills D, and both produce what is defined here. The
architecture in one line, because forgetting it costs a billion cells: these matrices are square
over BASE keys — thousands, not the ~197k senses. A sense rides ON the base (tkzip req. 11).

SPARSE, AND NOT AS AN OPTIMISATION. The prototype stored a dense `vector` per row because 983
dimensions made it free; at the full base a dense row is 4,445 floats and the collection is a
hundred and fifty megabytes of mostly zero. R is a sparse geometry by nature — a cell exists because
a NAMED relation put it there — so a row is its cells, and the zero is the absence of a statement
rather than a stored one. The dense vector is reconstructed in memory by whoever wants to multiply.

PROVENANCE PER CELL is R's whole contract (requirement 18), and it is why `Cell` carries `via` and
not only the winning relation: a cell that `causes` set at 0.85 while `entails` also held is a
different fact from one that only `causes` could have made, and both curation and a later retreat
read exactly that difference. The winner is what the geometry uses; `via` is what a reader argues
with.

THE STORE IS A DOOR, not a base class. `MatrixStore` is what the pure builders are handed — the
in-memory one below is what the tests use, and the mongo-backed one lives in `tk2/datatier`, because
nothing in this package imports a database. A build writes through the migration door like every
other logic-class row; the body reads the base and never writes it.

ONE HAZARD, inherited from `keys.py` and repeated here because this is where it would bite: KEYS
CONTAIN DOTS. A cell may never be stored as a mongo field name (`edges.sleep.v` is a nested
document, not the cell you meant), which is why a row's cells are a LIST of subdocuments keyed by a
`column` VALUE.
"""

import hashlib
import json
from dataclasses import dataclass, field
from math import sqrt
from typing import Iterable, Iterator, Protocol, runtime_checkable

from tk2.dictionary import keys

# ------------------------------------------------------------------------------------------------
# where a cell came from
# ------------------------------------------------------------------------------------------------

#: The resource spoke: a named relation between two synsets the two dimensions speak for.
SOURCE_MINED = "mined"

#: A hand spoke, under the Captain's ruling of 2026-08-12 — analytic, stated in a definition, and
#: approved by him. Distinguishable from a mined cell FOREVER, which is the point of the field.
SOURCE_CURATED = "curated"

#: Neither: the diagonal. A dimension owns its own axis, and a matrix whose diagonal is zero has no
#: self-similarity — its cosines stop meaning what they look like. It is its own source so that a
#: density count can never accidentally include it.
SOURCE_AXIS = "axis"


@dataclass(frozen=True, slots=True)
class Provenance:
    """One relation that spoke about a pair, and what it was worth."""

    relation: str
    weight: float


@dataclass(frozen=True, slots=True)
class Cell:
    """One non-zero entry of a row: what the row key says ABOUT the column key.

    Asymmetric on purpose. Row X, column Y is X's relation TO Y, which is what keeps the antonym
    column-read (`row[X][index(W)] < 0`) working and what makes `entails` / `entailed_by` two
    different statements rather than one symmetric number.
    """

    column: str
    weight: float
    #: The relation that SET the value — the strongest claim, or the one the declared order believes
    #: first when two are equally strong.
    relation: str
    source: str = SOURCE_MINED
    #: Every relation that held between these two, strongest first. Includes the winner.
    via: tuple[Provenance, ...] = ()
    #: For a curated cell: the definition that justified it, VERBATIM (requirement 20). A paraphrase
    #: is the curator arguing rather than the dictionary speaking.
    evidence: str = ""

    def as_row(self) -> dict:
        """The stored shape. `via` travels as a list of pairs because it is read, not queried."""
        stored = {
            "column": self.column,
            "w": self.weight,
            "rel": self.relation,
            "src": self.source,
            "via": [[p.relation, p.weight] for p in self.via],
        }
        if self.evidence:
            stored["evidence"] = self.evidence
        return stored

    @classmethod
    def from_row(cls, stored) -> "Cell":
        return cls(
            column=stored["column"],
            weight=stored["w"],
            relation=stored["rel"],
            source=stored.get("src", SOURCE_MINED),
            via=tuple(Provenance(rel, weight) for rel, weight in stored.get("via", ())),
            evidence=stored.get("evidence", ""),
        )


@dataclass(frozen=True, slots=True)
class MatrixRow:
    """One dimension's row: its index in the key space, and every cell it states."""

    key: str
    index: int
    cells: tuple[Cell, ...] = ()

    @property
    def weights(self) -> dict[str, float]:
        return {cell.column: cell.weight for cell in self.cells}

    def cell(self, column: str) -> Cell | None:
        for cell in self.cells:
            if cell.column == column:
                return cell
        return None

    @property
    def is_silent(self) -> bool:
        """Nothing but its own axis: a base key no named relation reaches. Worth a name because it
        is a FINDING about the resource, not a detail — a dimension that can only ever be reached
        through D is a word R has nothing to say about."""
        return not [cell for cell in self.cells if cell.source != SOURCE_AXIS]


# ------------------------------------------------------------------------------------------------
# the matrix
# ------------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Matrix:
    """A square matrix over a key space, with its rows in dimension order.

    `keys` IS the dimension order and it is carried with the rows rather than re-derived: an index
    is only meaningful against the key space it was computed in, and two collections sharing one
    order is the whole reason R and D can be read cell for cell.
    """

    name: str
    keys: tuple[str, ...]
    rows: tuple[MatrixRow, ...] = ()
    #: What the build wants recorded beside the counts — the note a manifest reads.
    note: str = ""
    _by_key: dict[str, MatrixRow] = field(default_factory=dict, repr=False, compare=False)

    def __post_init__(self):
        by_key = {row.key: row for row in self.rows}
        if len(by_key) != len(self.rows):
            raise ValueError(f"{self.name}: two rows claim one key")
        object.__setattr__(self, "_by_key", by_key)

    def row(self, key: str) -> MatrixRow | None:
        return self._by_key.get(key)

    def cell(self, row_key: str, column_key: str) -> Cell | None:
        row = self.row(row_key)
        return row.cell(column_key) if row else None

    def cosine(self, a: str, b: str) -> float | None:
        """The angle between two rows — `None` when either key is not a dimension.

        `None` rather than 0.0 because «these two are unrelated» and «one of them is not in the base»
        are different answers, and a bar that scored the second as the first would report a
        membership defect as a geometry result (requirement 15).
        """
        row_a, row_b = self.row(a), self.row(b)
        if row_a is None or row_b is None:
            return None
        return cosine(row_a.weights, row_b.weights)

    def stats(self) -> dict:
        """The shape of what was built, counted the way a reader has to be able to ask it.

        The curated cells are counted APART from the mined ones for the reason `recount_R` gave in
        the prototype: the whole claim of R is that a cell can be asked where it came from, and a
        headline density that hides the hand is the first step back to a matrix nobody can audit.
        """
        by_relation: dict[str, int] = {}
        by_source: dict[str, int] = {}
        negative = 0
        stated = 0
        for row in self.rows:
            for cell in row.cells:
                if cell.source == SOURCE_AXIS:
                    continue
                stated += 1
                by_relation[cell.relation] = by_relation.get(cell.relation, 0) + 1
                by_source[cell.source] = by_source.get(cell.source, 0) + 1
                if cell.weight < 0:
                    negative += 1
        n = len(self.keys)
        off_diagonal = n * (n - 1)
        return {
            "dimensions": n,
            "off_diagonal": off_diagonal,
            "nonzero": stated,
            "density_pct": round(100 * stated / off_diagonal, 4) if off_diagonal else 0.0,
            "negative": negative,
            "silent_rows": sum(1 for row in self.rows if row.is_silent),
            "by_relation": dict(sorted(by_relation.items(), key=lambda item: -item[1])),
            "by_source": by_source,
        }


# ------------------------------------------------------------------------------------------------
# THE DUAL READ — two geometries, one number, and the parameter that says how much of each
# ------------------------------------------------------------------------------------------------
#
# R and D are two matrices on purpose (finding 4 of the 2026-08-12 review) and nothing in the build
# blends them. A READER may still want one number — the acceptance bar at T5 does — and this is the
# only shape in which that is honest: the two rows are CONCATENATED into one vector over 2n columns
# (R's columns, then D's, scaled by `mix`), and the cosine is taken over the whole of it. No cell is
# averaged with another, no matrix is rewritten, and `mix = 0` is R alone.
#
# READ THE WARNING BEFORE USING IT. The review measured the failure this parameter can reproduce:
# `enter~leave` reads -0.331 on relations alone and +0.519 once a gloss tail is mixed in, because
# opposites are defined in the same words. A blend high enough to let D speak is a blend high enough
# to bury R's sign, and the sign is the antonym column-read primitive.
#
# `mix` IS RULED AND IT IS A ROW (0.5, the Captain, 2026-09-09 — `ReadingPolicy`, db/0010), measured
# at the full base: at 1.0 `enter~leave` turns positive at +0.063 and the bar reads 60 of 80; at 0.5
# the sign survives at -0.059 and the bar peaks at 64. There is STILL no default in this module and
# there never will be: every function here takes the mix as an argument, because a reading is what a
# CALLER declares, and a default here would let a variant sweep and the standing reading present the
# same number under two different meanings.


def blended_row(relational: MatrixRow | None, distributional: MatrixRow | None, mix: float) -> dict[str, float]:
    """One dimension's row across both geometries, as one sparse vector over 2n named columns.

    The columns are prefixed rather than added together — `r/eat.v` and `d/eat.v` are two different
    axes — which is what keeps a positive gloss overlap from cancelling a negative relation instead
    of sitting beside it.
    """
    out: dict[str, float] = {}
    if relational is not None:
        for cell in relational.cells:
            out[f"r/{cell.column}"] = cell.weight
    if distributional is not None and mix:
        for cell in distributional.cells:
            out[f"d/{cell.column}"] = mix * cell.weight
    return out


def blended_cosine(relational: Matrix, distributional: Matrix, a: str, b: str, mix: float) -> float | None:
    """The angle between two dimensions read across both matrices — `None` when either key is not a
    dimension, for `Matrix.cosine`'s reason (a membership defect must not be reported as geometry).

    Refuses two different key spaces: a blend across two orders would be arithmetic over columns
    that are not the same words.
    """
    if relational.keys != distributional.keys:
        raise ValueError(
            f"{relational.name} and {distributional.name} are over different key spaces "
            f"({len(relational.keys)} and {len(distributional.keys)} dimensions); there is no "
            f"shared column to blend."
        )
    if relational.row(a) is None or relational.row(b) is None:
        return None
    left = blended_row(relational.row(a), distributional.row(a), mix)
    right = blended_row(relational.row(b), distributional.row(b), mix)
    return cosine(left, right)


def cosine(a: dict[str, float], b: dict[str, float]) -> float:
    """Cosine over two sparse rows. Written here rather than reached for from numpy because the
    rows ARE sparse maps: densifying 4,445 floats twice per pair to multiply a dozen shared columns
    is the kind of arithmetic that turns a bar run into a coffee break."""
    if not a or not b:
        return 0.0
    small, large = (a, b) if len(a) <= len(b) else (b, a)
    dot = sum(weight * large[column] for column, weight in small.items() if column in large)
    if not dot:
        return 0.0
    norm_a = sqrt(sum(weight * weight for weight in a.values()))
    norm_b = sqrt(sum(weight * weight for weight in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# ------------------------------------------------------------------------------------------------
# WHAT A MATRIX HASHES TO — the number a stored copy is checked against
# ------------------------------------------------------------------------------------------------


def fingerprint(matrix: Matrix) -> str:
    """sha256 over a matrix's whole content: its name, its dimension order, and every cell of every
    row exactly as `Cell.as_row` stores it.

    THE POINT IS THE ROUND TRIP. A build writes two hundred megabytes across a network into rows
    nobody will ever read whole again, and «the copy is the matrix» has to be a checkable claim
    rather than a hope — a truncated batch, a re-ordered key space and a silently coerced weight all
    produce a base that looks perfectly healthy. So the writer records this and a reader can
    recompute it from the stored rows (`tools/verify_base.py`).

    Hashed row by row rather than over one serialised blob, because the blob would be a second copy
    of the base in memory to compute a number about the first. The row's own dict is canonicalised
    (sorted keys, no whitespace) so the hash is a function of the CONTENT and not of how python felt
    about ordering a dictionary that day.
    """
    digest = hashlib.sha256()
    digest.update(json.dumps({"name": matrix.name, "keys": list(matrix.keys)},
                             sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    for row in matrix.rows:
        digest.update(json.dumps(
            {"key": row.key, "index": row.index, "cells": [cell.as_row() for cell in row.cells]},
            sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        ).encode("utf-8"))
    return digest.hexdigest()


def cell_count(matrix: Matrix) -> int:
    """Every cell the matrix holds, the diagonal included. `Matrix.stats()['nonzero']` counts what
    was STATED and excludes the axis; this counts what is stored, which is what a stored copy can be
    compared against without rebuilding the base to interpret it."""
    return sum(len(row.cells) for row in matrix.rows)


# ------------------------------------------------------------------------------------------------
# the store — a door, and the in-memory one behind it
# ------------------------------------------------------------------------------------------------


@runtime_checkable
class MatrixStore(Protocol):
    """Where a built matrix is kept. Injected, exactly as the gloss provider is.

    Deliberately small. A store puts a whole build away and hands rows back; it does not know what a
    relation is, and the builders do not know what a collection is. The mongo-backed implementation
    lives in `tk2.datatier.matrix_store` — outside this package, which imports no database.
    """

    def write(self, matrix: Matrix, build: str) -> int:
        """Store every row of `matrix` under the label `build`. Returns how many rows were written.

        A build LABEL rather than an implicit «the current one»: two builds must be able to sit in
        one database while the manifest says which is which, and a writer that replaced the base in
        place would make a comparison impossible exactly when it is most wanted.
        """
        ...

    def keys(self, build: str, name: str) -> tuple[str, ...]:
        """THE dimension order of a stored build."""
        ...

    def rows(self, build: str, name: str) -> Iterator[MatrixRow]:
        ...

    def row(self, build: str, name: str, key: str) -> MatrixRow | None:
        ...


class InMemoryMatrixStore:
    """The store the tests use — and the one a dry run writes to, so «what would be written» is
    produced by the same code path that writes it."""

    def __init__(self):
        self._matrices: dict[tuple[str, str], Matrix] = {}

    def write(self, matrix: Matrix, build: str) -> int:
        self._matrices[(build, matrix.name)] = matrix
        return len(matrix.rows)

    def matrix(self, build: str, name: str) -> Matrix:
        try:
            return self._matrices[(build, name)]
        except KeyError:
            raise KeyError(f"no matrix {name!r} stored under build {build!r}") from None

    def keys(self, build: str, name: str) -> tuple[str, ...]:
        return self.matrix(build, name).keys

    def rows(self, build: str, name: str) -> Iterator[MatrixRow]:
        return iter(self.matrix(build, name).rows)

    def row(self, build: str, name: str, key: str) -> MatrixRow | None:
        return self.matrix(build, name).row(key)


# ------------------------------------------------------------------------------------------------


def assert_square(matrix: Matrix) -> None:
    """Every key has a row, every cell points at a key, and no key is a stranger.

    Called by the builders before a matrix leaves them. A cell naming a column that is not a
    dimension is the failure mode this catches: it would be a statement about an axis that does not
    exist, which is precisely what requirement 15 calls a membership defect and what the prototype
    printed as «not a dimension of the base — no axis to write to».
    """
    space = set(matrix.keys)
    if len(space) != len(matrix.keys):
        raise ValueError(f"{matrix.name}: the key space repeats a dimension")
    missing = space - {row.key for row in matrix.rows}
    if missing:
        raise ValueError(f"{matrix.name}: {len(missing)} dimensions have no row, e.g. {sorted(missing)[:5]}")
    for row in matrix.rows:
        if row.key not in space:
            raise ValueError(f"{matrix.name}: row {row.key!r} is not a dimension of the key space")
        for cell in row.cells:
            if cell.column not in space:
                raise ValueError(
                    f"{matrix.name}: {row.key} -> {cell.column} names a column that is not a "
                    f"dimension. There is no axis to write it to."
                )


def diff(before: Matrix, after: Matrix) -> dict:
    """What changed between two matrices over ONE key space — the instrument a variant is read with.

    Written for the lemma-scope A/B and kept because every later question has this shape: the
    `derivational` down-weight (T4), a curation batch, a resource bump. A count alone answers «how
    many moved» and never «which», and the whole claim of R is that a cell can be asked what made
    it — so the cells themselves come back, not a tally of them.

    Refuses two different key spaces rather than comparing what it can: a diff across two orders
    would report every dimension as changed and none of it would mean anything.
    """
    if before.keys != after.keys:
        raise ValueError(
            f"{before.name} and {after.name} are over different key spaces "
            f"({len(before.keys)} and {len(after.keys)} dimensions); there is nothing to compare "
            f"cell for cell."
        )
    removed: list[tuple[str, Cell]] = []
    added: list[tuple[str, Cell]] = []
    changed: list[tuple[str, Cell, Cell]] = []
    for row in before.rows:
        other = after.row(row.key)
        for cell in row.cells:
            twin = other.cell(cell.column) if other else None
            if twin is None:
                removed.append((row.key, cell))
            elif (twin.weight, twin.relation) != (cell.weight, cell.relation):
                changed.append((row.key, cell, twin))
    for row in after.rows:
        other = before.row(row.key)
        for cell in row.cells:
            if (other.cell(cell.column) if other else None) is None:
                added.append((row.key, cell))
    return {"removed": removed, "added": added, "changed": changed}


def dimension_index(dimensions: Iterable[str]) -> dict[str, int]:
    """The key space as a lookup. Rejects anything that is not a base key, because a sense key here
    would be a dimension the architecture does not have (`keys.py`, both levels)."""
    index: dict[str, int] = {}
    for position, key in enumerate(dimensions):
        if not keys.is_base_key(key):
            raise keys.InvalidKey(f"{key!r} is not a base key and cannot be a dimension")
        index[key] = position
    return index
