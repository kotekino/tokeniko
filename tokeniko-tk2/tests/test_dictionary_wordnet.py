"""The WordNet adapter, spot-verified against facts about the real resource.

These are not "does the code run" tests. Each one names a WordNet fact the engine's correctness
depends on, so that the day nltk or the corpus moves under us, the thing that breaks says which
belief broke rather than which line did.

Marked `wordnet` and skipped when the corpus is not on the machine: the pure engine has to stay
testable without it, which is the whole reason the provider is injected.
"""

import pytest

wn_adapter = pytest.importorskip("tk2.dictionary.wordnet", reason="nltk is not installed")

from tk2.dictionary import closure, keys  # noqa: E402
from tk2.dictionary.config import ClosurePolicy  # noqa: E402

pytestmark = pytest.mark.wordnet


@pytest.fixture(scope="module")
def provider():
    try:
        wn_adapter.ensure_corpora()
    except wn_adapter.CorpusMissing as exc:
        pytest.skip(str(exc))
    # A small, declared lexicon: the words the review's own findings are about. The lexicon is an
    # ARGUMENT — a provider that defaulted to all of WordNet would decide the base by omission.
    return wn_adapter.WordNetProvider(
        ["eat", "food", "solid", "take", "sleep", "bed", "land", "left", "leave", "right", "use"]
    )


# ------------------------------------------------------------------------------------------------
# the facts the engine leans on
# ------------------------------------------------------------------------------------------------


def test_eats_primary_gloss_is_the_one_the_review_quotes(provider):
    """«take in solid food» — the sentence that made the point that a gloss's words are the edges."""
    assert provider.gloss("eat") == "take in solid food"


def test_primary_means_the_first_synset_per_pos(provider):
    """What the Jurassic build used. `land` has a noun and a verb, so its primary gloss has two
    halves; `all` has many more."""
    assert provider.gloss("land").count(" ; ") == 1
    assert len(provider.gloss("land", "all")) > len(provider.gloss("land"))


def test_the_pos_lists_are_the_ones_the_pos_split_was_measured_on(provider):
    assert provider.parts_of_speech("eat") == ("v",)
    assert provider.parts_of_speech("land") == ("n", "v")
    assert provider.parts_of_speech("left") == ("n", "v", "a", "r")


def test_the_satellite_adjective_arrives_as_an_adjective(provider):
    """`hungry` has an `s` synset in WordNet. If it leaked through as its own POS the base would
    grow a fifth kind of dimension without anyone deciding to."""
    assert wn_adapter.WordNetProvider(["hungry"]).parts_of_speech("hungry") == ("a",)


def test_morphy_lands_an_inflection_on_its_lemma(provider):
    """«takes in solid food» must reach `take`, or half the definition digraph is silent."""
    assert "take" in provider.lemmas("takes")


def test_left_is_leaves_participle_and_wordnet_knows_it_REQUIREMENT_21(provider):
    """The whole of requirement 21 in one fact: morphy('left', 'v') is `leave`, and morphy('left',
    'n') is `left`. Both answers are correct; the defect is that the miner picks by surface form
    first and so takes the direction every time. `use`/`used` is the same disease."""
    assert provider.lemmas("left")[0] == "leave"      # verbs are tried first
    assert "use" in provider.lemmas("used")


def test_the_lexicon_is_what_was_handed_in(provider):
    assert "eat" in provider.lexicon()
    assert "hungry" not in provider.lexicon()


# ------------------------------------------------------------------------------------------------
# THE FINDING: the real stop list eats the Captain's own example
# ------------------------------------------------------------------------------------------------


def test_nltks_stop_list_contains_the_words_the_closure_example_is_made_of(provider):
    """`me`, `you`, `not` and `be` are all nltk stop words, so on the real resource the Captain's
    closure example (me -> not you | you -> not me | not -> negation) cannot form: its edges are
    filtered out before the lexicon is consulted.

    Pinned as a fact, not fixed here — whether the stop list should yield to lexicon membership is a
    ruling, and the prototype's order (stop words first) is what every measured result so far was
    produced under.
    """
    stops = provider.stopwords()
    assert {"me", "you", "not", "be"} <= stops
    assert "same" in stops and "different" not in stops


# ------------------------------------------------------------------------------------------------
# the sense-key convention against the real sense inventory
# ------------------------------------------------------------------------------------------------


def test_sense_keys_are_word_anchored_because_wordnets_names_are_not(provider):
    """The argument for the convention, made against the resource: `left`'s verb senses are called
    `leave.v.01`, `exit.v.01`, `bequeath.v.01` — WordNet names a synset after whichever lemma heads
    it. Those names do not truncate to `left.v`, and truncation to the base key is the operation the
    ride-on-the-base architecture performs constantly. So the key is ours and the synset name is
    kept beside it as provenance."""
    senses = wn_adapter.WordNetProvider(["left"]).sense_keys("left")
    verb_senses = [s for s in senses if s["base"] == "left.v"]
    assert verb_senses[0]["key"] == "left.v.01"
    assert verb_senses[0]["synset"] == "leave.v.01"
    assert {s["synset"] for s in verb_senses} & {"exit.v.01", "bequeath.v.01"}
    assert all(keys.base_of(s["key"]) == s["base"] for s in senses)


def test_the_sense_numbering_restarts_per_pos(provider):
    senses = wn_adapter.WordNetProvider(["left"]).sense_keys("left")
    first_of = {}
    for sense in senses:
        first_of.setdefault(sense["base"], sense["key"])
    assert first_of == {
        "left.n": "left.n.01",
        "left.v": "left.v.01",
        "left.a": "left.a.01",
        "left.r": "left.r.01",
    }


def test_a_dimension_asks_wordnet_only_about_its_own_pos(provider):
    """`land.v` is «reach or come to rest» — no ground in it. That fact is why the curated edge
    could not close land.n~land.v and the fix has to be a down-weight instead."""
    verb = provider.synsets_of_key("land.v")[0]
    assert verb.pos() == "v"
    assert "ground" not in verb.definition()


# ------------------------------------------------------------------------------------------------
# the engine, end to end, on the real resource
# ------------------------------------------------------------------------------------------------


def test_the_engine_runs_on_the_real_provider(provider):
    """Small, but it is the seam under test: the pure engine and the real resource, meeting only
    through the protocol."""
    graph = closure.build_digraph(provider)
    assert graph["eat"] == {"take", "solid", "food"}   # «take in solid food», `in` dropped as a stop word
    result = closure.seed_closure(graph, ("eat",), ClosurePolicy(max_depth=1))
    assert set(result.words) == {"eat", "take", "solid", "food"}


def test_the_at_scale_lexicon_is_single_words_only():
    """A compound is the atom of the DERIVED space (requirement 6, layer two). Admitting `take_in`
    here would put layer two's atoms into layer one's dimensions before the layer exists."""
    try:
        lexicon = wn_adapter.wordnet_lexicon()
    except wn_adapter.CorpusMissing as exc:
        pytest.skip(str(exc))
    assert not any("_" in w for w in lexicon)
    assert "eat" in lexicon and "take_in" not in lexicon
    # Order of magnitude, not a fixed count: the assertion is that this is a LEXICON-scale build,
    # thousands of dimensions, never the ~197k senses. A number that drifts with the corpus is
    # checked as a magnitude on purpose.
    assert 50_000 < len(lexicon) < 150_000
