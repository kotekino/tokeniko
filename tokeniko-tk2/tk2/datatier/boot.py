"""Booting the tier: one guarded database, the ODM initialised, the r-tier snapshotted.

Boot = load the r-tables; a slow tick reconciles (body req. 4). This is the first half — the second
half is whoever owns the loop calling `RCache.maybe_refresh()` on every tick.
"""

from typing import Sequence

from bunnet import init_bunnet
from pymongo.database import Database

from tk2.core.documents import TkDocument
from tk2.datatier.client import database
from tk2.datatier.rcache import RCache


def boot_datatier(
    models: Sequence[type[TkDocument]],
    db_name: str | None = None,
) -> tuple[Database, RCache]:
    """Open the database, register the models, take the first r-tier snapshot.

    Every model is registered with the ODM; only the r-class ones are cached. Returns the database
    alongside the cache because migrations and raw probes need the handle, and reaching for a second
    one would be reaching around the guard.
    """
    db = database(db_name)
    init_bunnet(database=db, document_models=list(models))

    cache = RCache([m for m in models if not m.write_class.writable])
    cache.load()
    return db, cache
