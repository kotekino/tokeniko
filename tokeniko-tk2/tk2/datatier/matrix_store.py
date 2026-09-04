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
"""

from typing import Iterator

from pymongo.database import Database

from tk2.core.models import BaseKeyDoc, BaseRelationDoc
from tk2.datatier.migration_writer import MigrationWriter
from tk2.dictionary import keys
from tk2.dictionary.matrix import Cell, Matrix, MatrixRow

#: Which collection holds which matrix. `base_d` joins at T4 — one line, because the shape is the
#: same and the difference between R and D is what fills them, never how they are kept.
MATRIX_MODELS = {
    BaseRelationDoc.Settings.name: BaseRelationDoc,
}


class KeySpaceConflict(RuntimeError):
    """A build already has a dimension order, and this matrix disagrees with it."""


class MongoMatrixStore:
    """Keeps built matrices in a named database. The caller has already guarded the name."""

    def __init__(self, database: Database):
        self._db = database
        self._writer = MigrationWriter(database)

    # -- writing -------------------------------------------------------------------------------

    def write(self, matrix: Matrix, build: str) -> int:
        """Store a matrix under a build label, replacing that build's copy of it.

        Replacing rather than appending: a build label names one measurement, and two half-written
        copies under one label would be a base nobody could read. The registry is written first,
        because a matrix whose dimensions are not recorded is a set of numbers with no meaning.
        """
        model = self._model(matrix.name)
        self.write_keys(matrix.keys, build)

        collection = self._writer.collection(model)
        collection.delete_many({"build": build})
        rows = [
            {
                "build": build,
                "key": row.key,
                "index": row.index,
                "cells": [cell.as_row() for cell in row.cells],
            }
            for row in matrix.rows
        ]
        self._writer.insert_many(model, rows)
        return len(rows)

    def write_keys(self, dimensions, build: str) -> int:
        """THE dimension order of a build. Idempotent, and loud when it is asked to change.

        Returns how many rows were written — zero when the registry was already there and agreed,
        which is the normal case for the second matrix of a build.
        """
        dimensions = tuple(dimensions)
        existing = self.keys(build)
        if existing:
            if existing != dimensions:
                raise KeySpaceConflict(
                    f"build {build!r} already holds {len(existing)} dimensions and this matrix has "
                    f"{len(dimensions)} in a different order. R and D share ONE key space; two "
                    f"orders would make every cell of every row point at another word."
                )
            return 0

        rows = []
        for index, key in enumerate(dimensions):
            word, pos = keys.split_key(key)
            rows.append({"build": build, "key": key, "word": word, "pos": pos, "index": index})
        self._writer.insert_many(BaseKeyDoc, rows)
        return len(rows)

    # -- reading -------------------------------------------------------------------------------

    def keys(self, build: str, name: str | None = None) -> tuple[str, ...]:
        """The build's dimension order. `name` is accepted and ignored on purpose: the store's
        protocol asks per matrix, and the honest answer here is that a build has ONE key space."""
        found = self._writer.collection(BaseKeyDoc).find({"build": build}, {"key": 1, "index": 1})
        return tuple(row["key"] for row in sorted(found, key=lambda row: row["index"]))

    def rows(self, build: str, name: str) -> Iterator[MatrixRow]:
        collection = self._writer.collection(self._model(name))
        for stored in collection.find({"build": build}).sort("index", 1):
            yield _row_of(stored)

    def row(self, build: str, name: str, key: str) -> MatrixRow | None:
        stored = self._writer.collection(self._model(name)).find_one({"build": build, "key": key})
        return _row_of(stored) if stored else None

    def matrix(self, build: str, name: str) -> Matrix:
        """The whole matrix back in memory — for a bar run, which needs every row's neighbours."""
        return Matrix(name=name, keys=self.keys(build), rows=tuple(self.rows(build, name)))

    def builds(self, name: str | None = None) -> tuple[str, ...]:
        """Every build label present, so a reader never has to guess one."""
        model = self._model(name) if name else BaseKeyDoc
        return tuple(sorted(self._writer.collection(model).distinct("build")))

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


def _row_of(stored) -> MatrixRow:
    return MatrixRow(
        key=stored["key"],
        index=stored["index"],
        cells=tuple(Cell.from_row(cell) for cell in stored.get("cells", ())),
    )
