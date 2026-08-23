"""tk2.datatier — how the rows MOVE.

Thin by charter (datatier req. 6): readers, writers, caches, guards. No business logic below the
model layer.

  - `guard.py`             THE GUARD, standard equipment: every entry point names its db, tk1's are
                           refused by name ahead of the whitelist, everything unlisted is refused.
  - `client.py`            one pooled client; `database()` is the only path to a handle, and it guards.
  - `traps.py`             the tk1 traps wrapped away — no caller ever holds a query, so no caller
                           can forget `.run()`; the timeseries delete is its own honest function.
  - `rcache.py`            the r-tier snapshot + the slow tick that makes a param edit land live.
  - `migration_writer.py`  the OTHER door: the only writer of param/logic rows. Raw pymongo,
                           pydantic-validated, no toggle.
  - `boot.py`              guarded db + ODM init + the first snapshot.

The two doors are the shape of this tier. The body comes through `traps`, where the write-class is
asked every time and the r-classes refuse. A migration comes through `migration_writer`, which does
not use the ODM at all. Which door a row came through is visible at every call site, forever.
"""

from tk2.datatier.boot import boot_datatier
from tk2.datatier.client import client, close, database
from tk2.datatier.guard import DatabaseRefused, guard_db_name
from tk2.datatier.migration_writer import MigrationWriter, shape_of
from tk2.datatier.rcache import RCache
from tk2.datatier.traps import (
    count,
    delete_many,
    delete_timeseries_rows,
    exists,
    find,
    find_all,
    find_one,
    get,
    insert,
    insert_many,
    is_timeseries,
    replace,
    save,
)

__all__ = [
    "DatabaseRefused",
    "MigrationWriter",
    "RCache",
    "boot_datatier",
    "client",
    "close",
    "count",
    "database",
    "delete_many",
    "delete_timeseries_rows",
    "exists",
    "find",
    "find_all",
    "find_one",
    "get",
    "guard_db_name",
    "insert",
    "insert_many",
    "is_timeseries",
    "replace",
    "save",
    "shape_of",
]
