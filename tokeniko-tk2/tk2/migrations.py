"""THE MIGRATION RUNNER — deploys are scripts that write the db (body req. 3).

The machinery lives in the package because it is code the body ships with; the migrations themselves
live in `db/`, which is deliberately NOT a package. They are loaded BY PATH, one at a time, and that
is the point: a migration that could be imported is a migration someone imports, and importing one
would run it somewhere nobody meant it to run.

Every migration receives a `MigrationWriter` and writes through it — validated by pydantic, executed
by raw pymongo, never through the ODM's write path. That is what keeps the r-classes reachable to a
deploy and unreachable to the body, with no flag anywhere that could blur the two.

An applied migration is IMMUTABLE. Its checksum is recorded when it runs, and a later run that finds
the file changed refuses to continue: the database has already been altered by what that file used
to say, so the ledger would otherwise be a record of something that no longer exists. The fix for a
wrong migration is always a new migration.
"""

import hashlib
import importlib.util
import re
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

from pymongo.database import Database

from tk2.core.mixins import now_seconds
from tk2.core.models.migrations import MigrationDoc
from tk2.datatier.migration_writer import MigrationWriter

#: `0001_create_the_world.py`. The number is the order, and the order is the truth.
FILENAME = re.compile(r"^(\d{4})_([a-z0-9_]+)\.py$")

#: Where the migrations live, relative to the installed package: `tokeniko-tk2/db/`.
DEFAULT_DIRECTORY = Path(__file__).resolve().parent.parent / "db"


class MigrationError(RuntimeError):
    """The set of migrations on disk cannot be applied as it stands."""


@dataclass(frozen=True)
class Migration:
    number: int
    name: str
    path: Path

    @property
    def label(self) -> str:
        return f"{self.number:04d}_{self.name}"

    def checksum(self) -> str:
        """sha256 of the file's bytes — what makes «this migration has been edited» detectable."""
        return hashlib.sha256(self.path.read_bytes()).hexdigest()

    def load(self) -> ModuleType:
        """Import the file by path, under a private name so it can never collide with a package."""
        spec = importlib.util.spec_from_file_location(f"tk2_migration_{self.label}", self.path)
        if spec is None or spec.loader is None:
            raise MigrationError(f"{self.path} cannot be loaded as a python module.")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if not hasattr(module, "up"):
            raise MigrationError(
                f"{self.label} defines no up(writer, db): a migration is a function that changes "
                f"the world, and a file that changes nothing should not be numbered."
            )
        return module


def discover(directory: Path | None = None) -> list[Migration]:
    """Every migration on disk, in number order.

    Duplicate numbers are refused rather than ordered arbitrarily — two migrations claiming the same
    position have no defined order, and a deploy whose order is undefined is not a deploy.
    """
    directory = Path(directory) if directory is not None else DEFAULT_DIRECTORY
    if not directory.is_dir():
        raise MigrationError(f"no migration directory at {directory}")

    found: dict[int, Migration] = {}
    for path in sorted(directory.iterdir()):
        match = FILENAME.match(path.name)
        if not match:
            continue
        number = int(match.group(1))
        if number in found:
            raise MigrationError(
                f"two migrations numbered {number:04d}: {found[number].path.name} and "
                f"{path.name}. The number IS the order; two files cannot hold one position."
            )
        found[number] = Migration(number=number, name=match.group(2), path=path)

    return [found[n] for n in sorted(found)]


def _ledger(db: Database):
    return db[MigrationDoc.Settings.name]


def applied(db: Database) -> dict[int, dict]:
    """What this database says has already been run, by number."""
    return {row["number"]: row for row in _ledger(db).find({})}


def pending(db: Database, directory: Path | None = None) -> list[Migration]:
    """What has not run yet — and, on the way, the check that what HAS run still says what it said.

    The immutability check lives here rather than in `apply` because it must fire even when there is
    nothing left to apply: a body that boots against an edited history should say so at the first
    `migrate`, not at the next deploy.
    """
    done = applied(db)
    out: list[Migration] = []
    for migration in discover(directory):
        record = done.get(migration.number)
        if record is None:
            out.append(migration)
            continue
        if record.get("checksum") != migration.checksum():
            raise MigrationError(
                f"{migration.label} has changed since it was applied "
                f"({record.get('applied_at')}). An applied migration is immutable: the database "
                f"already holds what the old file did, so this ledger row now describes something "
                f"that no longer exists. Write a NEW migration to correct it."
            )
    return out


def apply(db: Database, migration: Migration) -> None:
    """Run one migration and record it. The record is written LAST, on purpose.

    If `up()` raises, nothing is recorded and the migration is still pending — a half-applied
    migration that claimed to be finished would be the worst possible state to leave a database in,
    and re-running is at least an option a person can reason about.
    """
    writer = MigrationWriter(db)
    module = migration.load()
    module.up(writer, db)
    writer.insert(
        MigrationDoc,
        {
            "number": migration.number,
            "name": migration.name,
            "checksum": migration.checksum(),
            "applied_at": now_seconds(),
        },
    )


def migrate(db: Database, directory: Path | None = None) -> list[Migration]:
    """Apply everything pending, in order. Returns what was applied."""
    run: list[Migration] = []
    for migration in pending(db, directory):
        apply(db, migration)
        run.append(migration)
    return run


def ensure_collections(db: Database, models) -> None:
    """Materialise collections and indexes from the models — DDL, not row writes.

    A migration calls this to create the world's shape. It goes through the ODM's initialisation
    because the models are where collection names, index definitions and the timeseries
    configuration already live, and re-deriving them by hand in a migration would be two sources of
    truth for one schema. Nothing here writes a ROW: the write-class locks are untouched, and every
    row this or any migration stores still goes through the migration writer.
    """
    from bunnet import init_bunnet

    init_bunnet(database=db, document_models=list(models))
