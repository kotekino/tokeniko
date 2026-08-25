"""Reach into migration 0001 for the rows it will really write.

The anatomy used to live beside the tests as a copy. Now that 0001 owns it, the tests load the
migration itself — so what is checked for coherence is the seed that will actually create the world,
not a second copy of it that could drift.
"""

from functools import lru_cache
from types import ModuleType

from tk2.migrations import discover


@lru_cache(maxsize=None)
def migration(number: int) -> ModuleType:
    """Load one migration by number, as the runner does."""
    found = next((m for m in discover() if m.number == number), None)
    assert found is not None, f"no migration numbered {number:04d}"
    return found.load()


def anatomy_rows() -> list[dict]:
    return list(migration(1).ANATOMY_ROWS)


def param_rows() -> list[dict]:
    return list(migration(1).PARAM_ROWS)


def all_poles() -> list[str]:
    return list(migration(1).ALL_POLES)


def sphere_poles() -> list[str]:
    return list(migration(1).SPHERE_POLES)


# ------------------------------------------------------------------------------------------------
# 0003 — the dictionary's policy, as rows
# ------------------------------------------------------------------------------------------------
#
# Same argument as the anatomy's: the values are the migration's, so the tests read the migration.
# Here it buys something extra — the row constants are readable with NO database and no WordNet, so
# the load-bearing regression (these rows still fingerprint to the base T2b measured) runs offline.


def policy_rows() -> list[dict]:
    return [dict(row) for row in migration(3).POLICY_ROWS]


def bar_rows() -> list[dict]:
    return [dict(row) for row in migration(3).BAR_ROWS]


def declared_config():
    """The policy 0003 writes, as the object `config.py` used to hold."""
    return migration(3).DECLARED
