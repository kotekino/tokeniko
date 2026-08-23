"""The applied-migration ledger — the deploy's own bookkeeping.

Deliberately NOT in `ALL_MODELS`. The body never reads its own deploy history and has no use for
it: registering it would tell the ODM about a collection the interpreter does not interpret. It is
here, as a model, only so that the migration writer can validate its rows like any others — pydantic
stays the single source of shape even for the runner's own table.

It is a `logic` document all the same, so that EVERY collection in the body's database is governed
by the write-class seam with no exceptions. The body structurally cannot rewrite the record of what
was deployed to it, which is the correct relationship: a deploy is something that happens TO him.
"""

from typing import Annotated

from bunnet import Indexed

from tk2.core.documents import LogicDocument


class MigrationDoc(LogicDocument):
    """logic (r) — the record of what was deployed; the body is its subject, never its author."""

    number: Annotated[int, Indexed(unique=True)]
    name: str

    #: sha256 of the migration file as it was when it ran. An applied migration is IMMUTABLE — the
    #: database has already been changed by it, so editing the file makes the record a lie. The
    #: runner compares and refuses; the fix for a wrong migration is always a NEW migration.
    checksum: str

    applied_at: int

    class Settings:
        name = "migrations"
