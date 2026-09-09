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


# ------------------------------------------------------------------------------------------------
# 0006 — R's weights, the curated vocabulary and the alphabet: policy version 3
# ------------------------------------------------------------------------------------------------
#
# Read off the migration for the fourth time, and here it buys what it bought at 0005: the values
# under test are the ones that will be written, so a test cannot keep passing after the Captain
# moves a weight. Nothing here needs a database or a corpus.


def policy_rows_v3() -> list[dict]:
    return [dict(row) for row in migration(6).POLICY_ROWS]


def declared_config_v3():
    """The whole policy v3 declares — v2's seeds and cuts, plus R's weights and the alphabet."""
    return migration(6).DECLARED


def relation_policy():
    """R's declared weights AS THEY STAND — the newest policy version, whichever that is.

    Found by asking the files rather than by naming a migration, for `tools/propose_seeds.py`'s
    reason: a fixture with a version number in it would have to be edited every time the Captain
    rules, and the edit that got forgotten would leave a test measuring a superseded policy. The
    version-specific helpers below are for the tests that are ABOUT a particular ruling.
    """
    from tk2.datatier.policy_source import newest_policy_migration

    return newest_policy_migration()[1].DECLARED.relations


def alphabet():
    """The parts of speech policy v3 declares."""
    return migration(6).ALPHABET


# ------------------------------------------------------------------------------------------------
# 0007 — the lemma scope ruled: policy version 4
# ------------------------------------------------------------------------------------------------


def policy_rows_v4() -> list[dict]:
    return [dict(row) for row in migration(7).POLICY_ROWS]


def relation_policy_v4():
    """R's declared weights at v4 — including whose lemma may speak."""
    return migration(7).DECLARED.relations


def declared_config_v4():
    """The policy v4 writes — v3's whole declaration, plus whose lemma may speak."""
    return migration(7).DECLARED


# ------------------------------------------------------------------------------------------------
# 0008 — the inferred opposition admitted: policy version 5
# ------------------------------------------------------------------------------------------------


def policy_rows_v5() -> list[dict]:
    return [dict(row) for row in migration(8).POLICY_ROWS]


def declared_config_v5():
    """The policy v5 writes — v4's whole declaration, plus how a one-sided antonymy is read."""
    return migration(8).DECLARED


def relation_policy_v5():
    return migration(8).DECLARED.relations


# ------------------------------------------------------------------------------------------------
# 0009 — D's gloss walk declared: policy version 6
# ------------------------------------------------------------------------------------------------


def policy_rows_v6() -> list[dict]:
    return [dict(row) for row in migration(9).POLICY_ROWS]


def declared_config_v6():
    """The policy v6 writes — v5's whole declaration, plus the nine parameters D is built from."""
    return migration(9).DECLARED


def distribution_policy():
    """D's declared walk AS IT STANDS — the newest policy version, whichever that is.

    Found by asking the files rather than by naming a migration, for `relation_policy`'s reason: a
    fixture with a version number in it would have to be edited every time the Captain rules.
    """
    from tk2.datatier.policy_source import newest_policy_migration

    return newest_policy_migration()[1].DECLARED.distribution


# ------------------------------------------------------------------------------------------------
# 0010 — the dual read ruled, and three values moved: policy version 7
# ------------------------------------------------------------------------------------------------


def policy_rows_v7() -> list[dict]:
    return [dict(row) for row in migration(10).POLICY_ROWS]


def declared_config_v7():
    """The policy v7 writes — v6's whole declaration with two numbers moved, plus the mix."""
    return migration(10).DECLARED


def reading_policy():
    """The dual read AS IT STANDS — the newest policy version, whichever that is, for
    `distribution_policy`'s reason: a fixture with a version number in it would have to be edited
    every time the Captain rules."""
    from tk2.datatier.policy_source import newest_policy_migration

    return newest_policy_migration()[1].DECLARED.reading
