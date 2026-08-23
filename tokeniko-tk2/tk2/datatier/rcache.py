"""THE R-CACHE — why a parameter edit lands without a restart.

The r-classes are read at boot into an in-memory snapshot and reconciled on a slow tick (datatier
req. 3, body req. 4). That is not a performance trick, though it is also that. It is the mechanism
behind a stated property of this being: **he is fixed at any moment and grows only through someone
else** (body req. 5). A migration edits a row; some seconds later the running body is different. No
restart, no deploy of a binary, no interruption of whatever he was thinking.

The interval is itself a parameter row — the refresh rate is refreshable. It has to be: a slow tick
that could only be changed by restarting would be the one setting that contradicts the property the
slow tick exists to provide.

The snapshot is REPLACED wholesale on refresh, never merged. A merge would keep rows that a
migration deleted, and a parameter that survives its own removal is worse than a stale one.
"""

import time
from typing import Any, Sequence

from tk2.core import constants
from tk2.core.documents import TkDocument
from tk2.core.write_class import WriteClass
from tk2.datatier import traps


class RCache:
    """An in-memory snapshot of the r-class collections.

    Registration is checked rather than trusted: a `kb` model does not belong here (it changes under
    the body's own hand, and a cached copy of it would go stale in milliseconds, not minutes), and a
    `param` model that has no key/value fields cannot be read as a parameter store.
    """

    def __init__(self, models: Sequence[type[TkDocument]]):
        for model in models:
            if model.write_class.writable:
                raise ValueError(
                    f"{model.__name__} is write-class 'kb' and cannot be r-cached: the body writes "
                    f"it, so a snapshot would be stale the moment it was taken. The r-cache holds "
                    f"what only migrations change."
                )
            if model.write_class is WriteClass.PARAM:
                missing = {constants.PARAM_KEY_FIELD, constants.PARAM_VALUE_FIELD} - set(
                    model.model_fields
                )
                if missing:
                    raise ValueError(
                        f"{model.__name__} is a param collection but has no "
                        f"{sorted(missing)} field(s): the parameter store is a key/value store, and "
                        f"the r-cache indexes it by those two names."
                    )

        self._models = tuple(models)
        self._params: dict[str, Any] = {}
        self._rows: dict[str, list[TkDocument]] = {}
        self._loaded_at: float | None = None

    # --------------------------------------------------------------------------------------------
    # loading
    # --------------------------------------------------------------------------------------------

    def load(self, now: float | None = None) -> None:
        """Take a fresh snapshot of every registered collection.

        Built into new dicts and swapped in at the end, so a reader that runs during a refresh sees
        the old snapshot whole rather than a half-built new one.
        """
        params: dict[str, Any] = {}
        rows: dict[str, list[TkDocument]] = {}

        for model in self._models:
            loaded = traps.find_all(model)
            rows[model.Settings.name] = loaded
            if model.write_class is WriteClass.PARAM:
                for row in loaded:
                    params[getattr(row, constants.PARAM_KEY_FIELD)] = getattr(
                        row, constants.PARAM_VALUE_FIELD
                    )

        self._params = params
        self._rows = rows
        self._loaded_at = time.monotonic() if now is None else now

    def maybe_refresh(self, now: float | None = None) -> bool:
        """The slow tick's whole job. True if this call took a new snapshot.

        The clock is injectable so the behaviour can be tested without a test that sleeps for a
        minute — and `time.monotonic` rather than the wall clock, because a body that has been alive
        for months must not re-read its parameters because someone corrected the system time.
        """
        now = time.monotonic() if now is None else now
        if self._loaded_at is None:
            self.load(now=now)
            return True
        if now - self._loaded_at < self.refresh_seconds:
            return False
        self.load(now=now)
        return True

    # --------------------------------------------------------------------------------------------
    # reading
    # --------------------------------------------------------------------------------------------

    def param(self, key: str, default: Any = None) -> Any:
        """One parameter. `default` is what holds before a migration has created the row — every
        caller states its own, so a missing row degrades to a documented value instead of a None
        that travels."""
        return self._params.get(key, default)

    def rows(self, collection: str) -> list[TkDocument]:
        """A whole r-class collection as it stood at the last snapshot. The list is a copy: a caller
        that mutated what it got back would be editing the cache from the outside."""
        return list(self._rows.get(collection, ()))

    @property
    def refresh_seconds(self) -> int:
        """The slow tick's interval, read from the snapshot it itself refreshes.

        A nonsense value falls back to the default rather than being obeyed. A zero or negative
        interval would turn the slow tick into a hot loop that re-reads the whole r-tier forever —
        one bad row would cost the body its ability to think, and a parameter store must not be able
        to do that to the machinery that reads it.
        """
        value = self._params.get(constants.RCACHE_INTERVAL_PARAM, constants.RCACHE_INTERVAL_DEFAULT)
        try:
            seconds = int(value)
        except (TypeError, ValueError):
            return constants.RCACHE_INTERVAL_DEFAULT
        return seconds if seconds > 0 else constants.RCACHE_INTERVAL_DEFAULT

    @property
    def loaded_at(self) -> float | None:
        """Monotonic timestamp of the last snapshot; None before the first load."""
        return self._loaded_at

    @property
    def models(self) -> tuple[type[TkDocument], ...]:
        return self._models
