"""THE MIGRATION DOOR — the only writer of the r-classes.

The Captain's ruling of 2026-08-23: a separately-named writer, validating through the pydantic
model, writing through raw pymongo, never calling `assert_writable`, and never a global toggle.
**Migrations must never look like the app.**

The reasoning is worth keeping where the code is. The tempting design is one writer with a flag —
`save(doc, allow_r=True)`, or a context manager that opens the r-classes for a while. Both are the
same mistake: a permission that the calling side can switch off is not a permission, and a global
flag makes the question «could this row have been written by the body?» unanswerable by reading the
code. Two doors with different names keep the answer visible at the call site forever.

So this module does not import `assert_writable` and does not need to: it never uses the ODM's write
path at all, which is exactly why the r-classes' own refusals (`tk2.core.documents`) do not stand in
its way. It is not sneaking past that lock — it is not on that door.

**Validation still goes through the model**, because pydantic is the single source of shape
(data-modeling req. 6) and a migration that wrote an unvalidated dict would be the fastest way to
put a row in the world that no model can read back. The validator is DERIVED from the model's own
fields rather than being the model itself: constructing a bunnet `Document` requires an initialised
collection, and a migration is a script against a database, not an application with an ODM booted.
The derived twin carries every constraint the real model declares — including the mixins' — and
carries no database machinery at all.
"""

from functools import lru_cache
from typing import Any, Iterable

from pydantic import BaseModel, create_model
from pymongo.database import Database

from tk2.core.documents import TkDocument

# bunnet's own bookkeeping columns. `id` is mongo's `_id`, which the server assigns; `revision_id`
# belongs to the ODM's optimistic locking, which a migration is not participating in.
_ODM_FIELDS = ("id", "revision_id")


@lru_cache(maxsize=None)
def shape_of(model: type[TkDocument]) -> type[BaseModel]:
    """A plain pydantic twin of `model`, for validating rows without booting the ODM.

    Cached per model: building it is cheap but not free, and a migration that writes ten thousand
    rows should pay for the schema once.
    """
    fields: dict[str, Any] = {
        name: (field.annotation, field)
        for name, field in model.model_fields.items()
        if name not in _ODM_FIELDS
    }
    return create_model(f"{model.__name__}Shape", **fields)


class MigrationWriter:
    """Writes rows on behalf of a migration. Holds a guarded `Database` and a pymongo handle.

    It takes the database rather than reaching for one, so a migration cannot be run against a
    database nobody named — the guard has already spoken by the time this object exists.
    """

    def __init__(self, database: Database):
        self._db = database

    @property
    def database(self) -> Database:
        return self._db

    def collection(self, model: type[TkDocument]):
        """The raw pymongo collection behind a model. The collection NAME comes off the model, so
        a migration and the body can never disagree about where the rows live."""
        return self._db[model.Settings.name]

    def validate(self, model: type[TkDocument], row: dict[str, Any]) -> dict[str, Any]:
        """Run a row through the model's shape and hand back what should be stored.

        `exclude_unset` is deliberately NOT used: a migration writing a row wants the model's
        defaults materialised in the database, so the stored row is complete and readable by anyone
        who has never seen the model.
        """
        return shape_of(model).model_validate(row).model_dump()

    def insert(self, model: type[TkDocument], row: dict[str, Any]) -> Any:
        """One validated row. Returns the new `_id`."""
        return self.collection(model).insert_one(self.validate(model, row)).inserted_id

    def insert_many(self, model: type[TkDocument], rows: Iterable[dict[str, Any]]) -> list[Any]:
        """Many validated rows. Every row is validated BEFORE any row is written, so a bad row at
        the end of a batch does not leave the first half of it in the database."""
        documents = [self.validate(model, row) for row in rows]
        if not documents:
            return []
        return list(self.collection(model).insert_many(documents).inserted_ids)

    def upsert(
        self,
        model: type[TkDocument],
        match: dict[str, Any],
        row: dict[str, Any],
    ) -> bool:
        """Write a row, replacing whatever already matched. True if it created a new one.

        The workhorse of a parameter migration: `match` is the key, `row` is the whole document.
        Replace rather than `$set` — a partial update against a validated shape could leave a row
        that is half one version and half another, which is exactly the state migrations exist to
        prevent.
        """
        result = self.collection(model).replace_one(match, self.validate(model, row), upsert=True)
        return result.upserted_id is not None

    def delete(self, model: type[TkDocument], match: dict[str, Any]) -> int:
        """Remove rows. Returns how many went — a migration that deletes nothing should be able to
        notice, for the same reason the datatier's deletes return their counts."""
        return self.collection(model).delete_many(match).deleted_count
