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
    """`left` is the exception and the exception is requirement 21: WordNet answers `wn.synsets`
    with all nineteen of `leave`'s verb senses, having walked back through morphy on its own. Since
    the repair the provider reports only the POS `left` is a base form of, so `left.v` — a duplicate
    of `leave.v` — is not among the dimensions it costs."""
    assert provider.parts_of_speech("eat") == ("v",)
    assert provider.parts_of_speech("land") == ("n", "v")
    assert provider.parts_of_speech("left") == ("n", "a", "r")


def test_the_satellite_adjective_arrives_as_an_adjective(provider):
    """`hungry` has an `s` synset in WordNet. If it leaked through as its own POS the base would
    grow a fifth kind of dimension without anyone deciding to."""
    assert wn_adapter.WordNetProvider(["hungry"]).parts_of_speech("hungry") == ("a",)


def test_morphy_lands_an_inflection_on_its_lemma(provider):
    """«takes in solid food» must reach `take`, or half the definition digraph is silent."""
    assert "take" in provider.lemmas("takes")


def test_left_is_leaves_participle_and_wordnet_knows_it_REQUIREMENT_21(provider):
    """The whole of requirement 21 in one fact: morphy('left', 'v') is `leave`, and morphy('left',
    'n') is `left`. Both answers are correct — which is why the repair asks per POS and keeps both
    readings, instead of the old «surface form first, then stop» that took the direction every time.
    `use`/`used` is the same disease: read as a verb, `used` is `use`."""
    assert provider.lemma("left", "v") == "leave"
    assert provider.lemma("left", "n") == "left"
    assert provider.lemmas("left") == ("left", "leave")
    assert provider.lemma("used", "v") == "use"
    assert provider.lemma("used", "a") == "used"


def test_wordnets_own_senses_are_the_only_ones_a_word_speaks_for_REQUIREMENT_21(provider):
    """Where the duplicate dimension actually died. `wn.synsets("used")` hands back `use`'s six verb
    senses; a provider that repeated them would mint `used.v` and give `use.v` a second name — and
    would write `use`'s definitions into `used`'s row of the definition digraph.

    What survives is `used` the genuine adjective. Note the parallel fact on the other collision:
    `left`'s adjective sense IS `leftover.s.01`, «not used up» — «something left over» was an
    adjective all along, and the repair keeps that reading while refusing the verb one.
    """
    assert provider.parts_of_speech("used") == ("a",)
    assert "use" not in provider.gloss("used")
    assert [s.name() for s in provider.lemma_synsets("used")] == [
        "used.a.01", "exploited.s.01", "secondhand.s.02",
    ]
    assert "leftover.s.01" in [s.name() for s in provider.lemma_synsets("left")]


def test_the_lexicon_is_what_was_handed_in(provider):
    assert "eat" in provider.lexicon()
    assert "hungry" not in provider.lexicon()


# ------------------------------------------------------------------------------------------------
# THE RULING (2026-08-25): lexicon membership outranks the stop list
# ------------------------------------------------------------------------------------------------


def test_a_stop_word_that_is_a_dimension_still_speaks_THE_RULING():
    """`in` is an nltk stop word AND a WordNet lemma, so where it is a lexicon word it names its
    dimension. This is the ruling's mechanism on the real resource: 69 of nltk's 198 English stop
    words are WordNet lemmas, and the list may no longer delete any of them.

    The same provider without `in` in its lexicon still drops the token — because it is not a word
    of that base, which is the honest reason, not a filter's opinion.
    """
    with_in = wn_adapter.WordNetProvider(["eat", "take", "solid", "food", "in"])
    without = wn_adapter.WordNetProvider(["eat", "take", "solid", "food"])
    assert "in" in with_in.stopwords()
    assert closure.build_digraph(with_in)["eat"] == {"take", "solid", "food", "in"}
    assert closure.build_digraph(without)["eat"] == {"take", "solid", "food"}


def test_the_captains_closure_example_cannot_form_on_wordnet_AND_WHY(provider):
    """Measured 2026-08-25, because the answer moved and the old reason is no longer the reason.

    His example is me -> not you | you -> not me | not -> negation | negation -> not. The stop list
    was blamed for it (`me`, `you`, `not` and `be` are all nltk stop words) and the ruling has now
    taken that objection away. It still cannot form, for two facts about the RESOURCE:

      - `you` is not a WordNet lemma at all. It has no synsets, so it is not in the 83,082-word
        lexicon and the closure reports it as a missing seed rather than a word it declined to
        reach. WordNet has no pronouns to speak of.
      - WordNet's `me` is the state of Maine, `be` is beryllium, `or` is Oregon. The lemma inventory
        answers a function word with whatever proper noun or chemical symbol is spelled that way.

    The example is a statement of the METHOD (definitions written in the lexicon's own words close
    on themselves), and the method is sound; what WordNet cannot supply is the vocabulary it was
    stated in.
    """
    stops = provider.stopwords()
    assert {"me", "you", "not", "be"} <= stops          # the list still says so
    assert "you" not in wn_adapter.wordnet_lexicon()    # no synsets: not a word of the base at all
    # `you` cannot be a member of a WordNet-derived lexicon, so the world his example needs is
    # already impossible; what the other three do is the rest of the answer.
    small = wn_adapter.WordNetProvider(["me", "not", "negation"])
    assert small.gloss("me") == "a state in New England"
    graph = closure.build_digraph(small)
    assert graph["me"] == set()
    assert graph["not"] == {"negation"}                 # «negation of a word or group of words»
    assert graph["negation"] == set()                   # names statement, denial, refusal — never `not`
    assert closure.seed_closure(graph, ("me", "you")).missing == ("you",)


# ------------------------------------------------------------------------------------------------
# the sense-key convention against the real sense inventory
# ------------------------------------------------------------------------------------------------


def test_sense_keys_are_word_anchored_because_wordnets_names_are_not(provider):
    """The argument for the convention, made against the resource: WordNet names a synset after
    whichever lemma heads it, so `left`'s fourth noun sense is called `left_field.n.01` and its
    second adjective sense `leftover.s.01`. Neither truncates to `left.n` or `left.a`, and
    truncation to the base key is the operation the ride-on-the-base architecture performs
    constantly. So the key is ours and the synset name is kept beside it as provenance."""
    senses = wn_adapter.WordNetProvider(["left"]).sense_keys("left")
    named = {s["key"]: s["synset"] for s in senses}
    assert named["left.n.04"] == "left_field.n.01"
    assert named["left.a.02"] == "leftover.s.01"
    assert all(keys.base_of(s["key"]) == s["base"] for s in senses)
    # And the senses that are not this word's at all are gone: `leave.v.01` is `leave`'s key, not a
    # sense of `left` (requirement 21).
    assert not any(s["base"] == "left.v" for s in senses)


def test_the_sense_numbering_restarts_per_pos(provider):
    senses = wn_adapter.WordNetProvider(["left"]).sense_keys("left")
    first_of = {}
    for sense in senses:
        first_of.setdefault(sense["base"], sense["key"])
    assert first_of == {
        "left.n": "left.n.01",
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
    assert graph["eat"] == {"take", "solid", "food"}   # «take in solid food» — `in` is not a word of this base
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
