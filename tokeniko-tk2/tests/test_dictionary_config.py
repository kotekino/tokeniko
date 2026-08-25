"""The declared policy: the bar's words are seeds by construction, and a variant cannot hide."""

import pytest

from tk2.dictionary import config as config_module
from tk2.dictionary.config import STANDING, BarPair, ClosurePolicy, DictionaryConfig, bar_words


def test_the_bars_own_words_are_seeds():
    """Requirement 12 enforced in code rather than by care. Run r1 of the prototype scored only 12
    of 18 pairs because `kill`, `water` and `swallow` were never reached — a subset that cannot
    score its own bar is not a test."""
    seeds = STANDING.seeds
    for word in ("kill", "water", "swallow", "runway", "die", "state"):
        assert word in seeds, f"{word} is named by the bar and must be seeded"


def test_bar_words_strip_the_pos_and_keep_first_mention_order():
    """Closure is about MEMBERSHIP, which is a property of words; the POS split decides dimensions
    afterwards. So a bar pair on `eat.v` seeds `eat`."""
    pairs = (BarPair("eat.v", "food.n", "NEAR", "why"), BarPair("food.n", "hungry.a", "NEAR", "why"))
    assert bar_words(pairs) == ("eat", "food", "hungry")


def test_the_declared_families_come_first_and_nothing_repeats():
    """`leave` is both a motion seed and a bar word. It is seeded once, in the order it was first
    declared — the seed list is a statement, and a statement with duplicates reads as an argument."""
    seeds = STANDING.seeds
    assert seeds[:3] == ("want", "must", "try")
    assert len(seeds) == len(set(seeds))
    assert seeds.index("leave") < seeds.index("kill")


def test_the_fingerprint_changes_when_the_policy_changes():
    """Policy before results: the manifest records this hash, so two builds with the same
    fingerprint were measured under the same policy. That is the whole claim."""
    deeper = STANDING.with_closure(max_depth=3)
    assert deeper.fingerprint() != STANDING.fingerprint()
    assert deeper.closure.max_depth == 3
    assert STANDING.closure.max_depth == 2, "a variant must not mutate the standing policy"


def test_the_fingerprint_is_stable_across_equal_configs():
    assert DictionaryConfig().fingerprint() == DictionaryConfig().fingerprint()


def test_the_canonical_form_carries_the_policy_itself_not_only_its_hash():
    """A later reader must be able to DIFF two builds' policies instead of trusting two hashes to
    differ for the reason he assumes."""
    blob = STANDING.as_dict()
    assert blob["closure"]["max_depth"] == 2
    assert blob["bar"][0]["a"] == "eat.v"
    assert "why" in blob["bar"][0], "a bar pair's reason is part of the declaration"


def test_the_reductions_own_law_is_inside_the_fingerprint():
    """The gap this closes: on 2026-08-25 the mining law moved (requirement 21's repair, and the
    ruling that lexicon membership outranks the stop list) without one field of the config moving
    with it — so two builds measured under different reductions could have presented the same hash
    and the manifest would have sworn they were comparable."""
    blob = STANDING.as_dict()
    assert blob["reduction_rules"] == config_module.REDUCTION_RULES
    before = STANDING.fingerprint()
    config_module.REDUCTION_RULES = "1999-01-01"
    try:
        assert STANDING.fingerprint() != before
    finally:
        config_module.REDUCTION_RULES = blob["reduction_rules"]
    assert STANDING.fingerprint() == before


def test_extra_seeds_are_a_runs_own_argument():
    """Kept apart from the standing declaration so the standing one stays readable — and visible in
    the fingerprint, so the run cannot pretend it was the standard one."""
    variant = STANDING.with_closure(extra_seeds=("runway",))
    assert variant.seeds[-1] == "runway"
    assert variant.fingerprint() != STANDING.fingerprint()


@pytest.mark.parametrize("bad", [{"max_depth": -1}, {"max_size": 0}, {"senses": "some"}])
def test_an_impossible_policy_is_refused_at_declaration(bad):
    with pytest.raises(ValueError):
        ClosurePolicy(**bad)
