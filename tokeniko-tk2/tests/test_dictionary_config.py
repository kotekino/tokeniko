"""The declared policy's SHAPE: the bar's words are seeds, and a variant cannot hide.

Every value these tests run on is stated here or read off migration 0003. Since T4b there is no
`STANDING` and no default in code to lean on — that is the point of the task, and a test that
reached for one would be reaching for the thing that was removed.
"""

import pytest

from tests.seed import declared_config
from tk2.dictionary import config as config_module
from tk2.dictionary.config import BarPair, ClosurePolicy, DictionaryConfig, bar_words


@pytest.fixture
def standing():
    """The policy as the rows declare it — migration 0003's own object, not a copy beside it."""
    return declared_config()


def test_the_bars_own_words_are_seeds(standing):
    """Requirement 12 enforced in code rather than by care. Run r1 of the prototype scored only 12
    of 18 pairs because `kill`, `water` and `swallow` were never reached — a subset that cannot
    score its own bar is not a test."""
    seeds = standing.seeds
    for word in ("kill", "water", "swallow", "runway", "die", "state"):
        assert word in seeds, f"{word} is named by the bar and must be seeded"


def test_bar_words_strip_the_pos_and_keep_first_mention_order():
    """Closure is about MEMBERSHIP, which is a property of words; the POS split decides dimensions
    afterwards. So a bar pair on `eat.v` seeds `eat`."""
    pairs = (BarPair("eat.v", "food.n", "NEAR", "why"), BarPair("food.n", "hungry.a", "NEAR", "why"))
    assert bar_words(pairs) == ("eat", "food", "hungry")


def test_the_declared_families_come_first_and_nothing_repeats(standing):
    """`leave` is both a motion seed and a bar word. It is seeded once, in the order it was first
    declared — the seed list is a statement, and a statement with duplicates reads as an argument."""
    seeds = standing.seeds
    assert seeds[:3] == ("want", "must", "try")
    assert len(seeds) == len(set(seeds))
    assert seeds.index("leave") < seeds.index("kill")


def test_the_fingerprint_changes_when_the_policy_changes(standing):
    """Policy before results: the manifest records this hash, so two builds with the same
    fingerprint were measured under the same policy. That is the whole claim."""
    deeper = standing.with_closure(max_depth=3)
    assert deeper.fingerprint() != standing.fingerprint()
    assert deeper.closure.max_depth == 3
    assert standing.closure.max_depth == 2, "a variant must not mutate the standing policy"


def test_the_fingerprint_is_stable_across_equal_configs(standing):
    twin = DictionaryConfig(
        closure=standing.closure, declared_seeds=standing.declared_seeds, bar=standing.bar
    )
    assert twin.fingerprint() == standing.fingerprint()


def test_the_canonical_form_carries_the_policy_itself_not_only_its_hash(standing):
    """A later reader must be able to DIFF two builds' policies instead of trusting two hashes to
    differ for the reason he assumes."""
    blob = standing.as_dict()
    assert blob["closure"]["max_depth"] == 2
    assert blob["bar"][0]["a"] == "eat.v"
    assert "why" in blob["bar"][0], "a bar pair's reason is part of the declaration"


def test_the_reductions_own_law_is_inside_the_fingerprint(standing):
    """The gap this closes: on 2026-08-25 the mining law moved (requirement 21's repair, and the
    ruling that lexicon membership outranks the stop list) without one field of the config moving
    with it — so two builds measured under different reductions could have presented the same hash
    and the manifest would have sworn they were comparable.

    It stays in CODE while the seeds and the bar leave, and the standing law is why: it names the
    shape a gloss is read under, not a value anyone curates.
    """
    blob = standing.as_dict()
    assert blob["reduction_rules"] == config_module.REDUCTION_RULES
    before = standing.fingerprint()
    config_module.REDUCTION_RULES = "1999-01-01"
    try:
        assert standing.fingerprint() != before
    finally:
        config_module.REDUCTION_RULES = blob["reduction_rules"]
    assert standing.fingerprint() == before


def test_extra_seeds_are_a_runs_own_argument(standing):
    """Kept apart from the standing declaration so the standing one stays readable — and visible in
    the fingerprint, so the run cannot pretend it was the standard one."""
    variant = standing.with_closure(extra_seeds=("runway",))
    assert variant.seeds[-1] == "runway"
    assert variant.fingerprint() != standing.fingerprint()


@pytest.mark.parametrize(
    "bad", [{"max_depth": -1}, {"max_size": 0}, {"senses": "some"}]
)
def test_an_impossible_policy_is_refused_at_declaration(bad):
    settings = {"max_depth": 2, "max_size": 400, "senses": "primary"} | bad
    with pytest.raises(ValueError):
        ClosurePolicy(**settings)


# ------------------------------------------------------------------------------------------------
# what T4b removed — the absence is the property
# ------------------------------------------------------------------------------------------------


def test_config_declares_no_curated_value_any_more():
    """The standing law of 2026-08-25: «a category-2 set stated in code is a defect even when its
    contents are correct». The seeds, the cuts and the bar are rows; this module holds their shape.

    Asserted as an ABSENCE because that is the only way to catch the regression that matters —
    someone re-adding a convenient default while the rows quietly say something else.
    """
    for gone in ("DECLARED_SEEDS", "BAR_PAIRS", "STANDING", "SEEDS_VOLITIONAL", "SEEDS_MOTION"):
        assert not hasattr(config_module, gone), f"{gone} is curation and belongs in `dictionary_policy`"


def test_a_closure_policy_cannot_be_constructed_without_stating_its_cuts():
    """A default in code is a second declaration of a curated number: the day the Captain moves
    `max_size` in a row, a bare `ClosurePolicy()` elsewhere would still answer 400 and nothing would
    say the two disagree."""
    with pytest.raises(TypeError):
        ClosurePolicy()


def test_a_config_cannot_be_constructed_without_a_policy_and_a_bar():
    with pytest.raises(TypeError):
        DictionaryConfig()
