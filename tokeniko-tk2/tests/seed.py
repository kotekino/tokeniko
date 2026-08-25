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


# ------------------------------------------------------------------------------------------------
# 0004 — the closed classes, as typed rows
# ------------------------------------------------------------------------------------------------
#
# Same argument again: the inventory is the migration's, so the tests read the migration. It needs
# no database and no WordNet, which is what lets the completeness cross-checks run anywhere.


def closed_class_rows() -> list[dict]:
    return [dict(row) for row in migration(4).ROWS]


def closed_class_forms() -> tuple[str, ...]:
    """The single-word forms — what E1's seed proposal excludes with."""
    return tuple(migration(4).FORMS)


# ------------------------------------------------------------------------------------------------
# 0005 — the ruled policy, version 2
# ------------------------------------------------------------------------------------------------
#
# Read off the migration for the third time, and here it buys the most: the 200 structural seeds are
# DERIVED (from a digraph over the whole WordNet lexicon), so the only way to check the rows without
# re-deriving them is to read the file that will write them.


def policy_rows_v2() -> list[dict]:
    return [dict(row) for row in migration(5).POLICY_ROWS]


def ruled_config():
    """The policy v2 writes — purpose ∪ structure, the cap demoted to a rail, bar v1 unchanged."""
    return migration(5).DECLARED


def structural_seeds() -> tuple[tuple[str, int, int], ...]:
    """`(word, rank, in_degree)` — the cut of the structural ranking the Captain ruled at k=200."""
    return tuple(migration(5).STRUCTURAL_SEEDS)
