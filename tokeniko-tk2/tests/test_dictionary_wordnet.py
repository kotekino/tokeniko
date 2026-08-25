"""The WordNet adapter, spot-verified against facts about the real resource.

These are not "does the code run" tests. Each one names a WordNet fact the engine's correctness
depends on, so that the day nltk or the corpus moves under us, the thing that breaks says which
belief broke rather than which line did.

Marked `wordnet` and skipped when the corpus is not on the machine: the pure engine has to stay
testable without it, which is the whole reason the provider is injected.
"""

import pytest

wn_adapter = pytest.importorskip("tk2.dictionary.wordnet", reason="nltk is not installed")

from tk2.dictionary import closure, glosses, keys  # noqa: E402
from tk2.dictionary.config import ClosurePolicy  # noqa: E402

pytestmark = pytest.mark.wordnet


def small_policy(max_depth: int = 2, max_size: int = 100, senses: str = "primary") -> ClosurePolicy:
    """The policy these small-lexicon runs measure under, stated rather than defaulted.

    Since T4b the standing values are rows (`db/0003`) and `ClosurePolicy` has no defaults in code —
    a default would be a second declaration of a number the Captain moves in the db. These worlds
    are a dozen words wide, so the cap never fires and the depth is the only cut in play.
    """
    return ClosurePolicy(max_depth=max_depth, max_size=max_size, senses=senses)


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
    assert closure.build_digraph(with_in, small_policy())["eat"] == {"take", "solid", "food", "in"}
    assert closure.build_digraph(without, small_policy())["eat"] == {"take", "solid", "food"}


def test_the_captains_closure_example_cannot_form_on_wordnet_AND_WHY(provider):
    """Measured 2026-08-25, twice, because the answer moved twice and the old reasons are no longer
    the reason.

    His example is me -> not you | you -> not me | not -> negation | negation -> not. The stop list
    was blamed for it first (`me`, `you`, `not` and `be` are all nltk stop words) and the membership
    ruling took that objection away. What replaced it was WordNet's `me` — the state of Maine — and
    with option C that reading is refused as the name it is, which takes `me` out of the lexicon
    entirely. So the reason is now ONE fact, and it is the cleanest of the three:

        WORDNET HAS NO PRONOUNS. Not `you`, not `me`, not `it`, not `who` — every one of those
        spellings is either absent or an acronym (`IT` the discipline, `WHO` the agency).

    The example is a statement of the METHOD (definitions written in the lexicon's own words close
    on themselves), and the method is sound; what WordNet cannot supply is the vocabulary it was
    stated in. That is a MEMBERSHIP finding for whoever chooses the base's seeds, not a defect of
    the engine — which is why the closure reports both as missing rather than quietly skipping them.
    """
    stops = provider.stopwords()
    assert {"me", "you", "not", "be"} <= stops          # the list still says so
    lexicon = wn_adapter.wordnet_lexicon()
    for pronoun in ("you", "me", "it", "who"):
        assert pronoun not in lexicon
    assert wn_adapter.folded_synsets("you") == ()       # no synsets at all
    assert wn_adapter.is_name_only("me") is True        # one synset, and it is Maine

    # `not` and `negation` are real words and behave; the two pronouns are simply not there.
    small = wn_adapter.WordNetProvider(["not", "negation"])
    graph = closure.build_digraph(small, small_policy())
    assert graph["not"] == {"negation"}                 # «negation of a word or group of words»
    assert graph["negation"] == set()                   # names statement, denial, refusal — never `not`
    assert closure.seed_closure(graph, ("me", "you", "not"), small_policy()).missing == ("me", "you")


# ------------------------------------------------------------------------------------------------
# OPTION C (2026-08-25): a name is not a word
# ------------------------------------------------------------------------------------------------


def test_the_capital_is_the_resources_own_statement_OPTION_C():
    """The fact the whole refusal rests on. nltk's lemma INDEX is case-folded, so `wn.synsets("or")`
    hands back Oregon; the SYNSETS keep the lexicographer's spelling, and it is `OR`. Folding the
    case invented a homograph English does not have, and the stop-list ruling then let it into the
    base as a dimension.

    Both facts are asserted together on purpose: the criterion is not «`or` is a bad word», it is
    «the resource never spells this reading the way the lexicon does».
    """
    assert [s.name() for s in wn_adapter.folded_synsets("or")] == ["oregon.n.01", "operating_room.n.01"]
    assert wn_adapter.spelled_synsets("or") == ()
    spellings = {l.name() for s in wn_adapter.folded_synsets("or") for l in s.lemmas()}
    assert "OR" in spellings and "or" not in spellings
    assert wn_adapter.is_name_only("or") is True


def test_a_name_only_spelling_is_not_a_word_of_the_base_OPTION_C():
    """Membership, the first of the two places the refusal lands. These five were dimensions of the
    T2 base: `or` = Oregon, `me` = Maine, `an` = Associate in Nursing, `it` = information
    technology, `who` = the World Health Organization. `or` alone was named by 57.8% of the base's
    rows — D is gloss overlap, so its loudest signal would have been «both definitions used the word
    *or*»."""
    lexicon = wn_adapter.wordnet_lexicon()
    for name in ("or", "me", "an", "it", "who", "isn", "shan", "america", "paris", "kafka"):
        assert name not in lexicon, f"{name} is a name, not a word"
    # Magnitude, not a fixed count — it drifts with the corpus. Measured 2026-08-25: 83,082 lemma
    # names in, 68,779 words out; 14,303 refused.
    assert 60_000 < len(lexicon) < 75_000


def test_only_the_name_reading_goes_when_the_word_is_real_OPTION_C():
    """The case that decides whether this is a refusal or a purge. A word is removed only when EVERY
    reading is a name, and where one reading is real the word stays and loses the dimension the name
    was occupying:

      - `be` keeps thirteen verb senses and loses `be.n`, which was beryllium's symbol `Be`;
      - `in` keeps its adjective and adverb senses AND `inch` (WordNet spells that abbreviation in
        lower case, so it is not refused) and loses indium `In` and Indiana `IN`;
      - `as` keeps the adverb and loses arsenic `As` and American Samoa `AS`.

    A rule that dropped the whole spelling would have deleted the copula to be rid of a chemical
    symbol.
    """
    provider = wn_adapter.WordNetProvider(["be", "in", "as"])
    assert provider.is_name_only("be") is False
    assert provider.parts_of_speech("be") == ("v",)
    assert "beryllium" not in provider.gloss("be", "all")
    assert [s.name() for s in wn_adapter.folded_synsets("be")
            if s not in wn_adapter.spelled_synsets("be")] == ["beryllium.n.01"]
    assert provider.parts_of_speech("in") == ("n", "a", "r")
    assert provider.parts_of_speech("as") == ("r",)


def test_the_membership_rulings_win_survives_the_refusal_OPTION_C():
    """The containment. The stop-list ruling was made to buy real function-word dimensions, and the
    refusal must not take them back — these nine are members with the same dimensions they had after
    T2. `not` is the sharpest of them: a function word, an nltk stop word, and a perfectly real
    adverb, so it passes both laws for two different reasons."""
    lexicon = wn_adapter.wordnet_lexicon()
    provider = wn_adapter.WordNetProvider(lexicon)
    expected = {
        "not": ("r",), "no": ("n", "a", "r"), "some": ("a", "r"), "other": ("a",),
        "own": ("v", "a"), "will": ("n", "v"), "very": ("a", "r"), "same": ("a",),
        "different": ("a",),
    }
    for word, dims in expected.items():
        assert word in lexicon, f"the ruling's win must survive: {word}"
        assert glosses.dimension_parts_of_speech(word, provider) == dims


def test_the_capital_beats_the_instance_flag_AND_HERE_IS_WHY():
    """Why the criterion is the lexicographer's spelling and not `instance_hypernyms`, stated as the
    counter-example that killed the alternative: WordNet marks `earth.n.01`, `sun.n.01` and
    `moon.n.01` as INSTANCES of their hypernyms. A refusal built on that flag would start refusing
    readings of `earth`, `sun` and `moon` — while still missing every acronym (`AN`, `ISN`) and every
    Latin genus, which carry no instance flag at all.

    The two agree where it matters, which is the point: 5,504 of the 14,303 refused words carry an
    instance hypernym, so the flag is a second, independent witness to the same judgement — just not
    a usable criterion on its own.
    """
    for word in ("earth", "sun", "moon"):
        assert wn_adapter.wn.synset(f"{word}.n.01").instance_hypernyms()
        assert word in wn_adapter.wordnet_lexicon()
    assert wn_adapter.is_name_only("an") is True
    assert not wn_adapter.wn.synset("associate_in_nursing.n.01").instance_hypernyms()


def test_morphology_is_untouched_by_the_refusal_OPTION_C():
    """The refusal is about what a spelling MEANS, never about how it inflects. `ate` is a name-only
    spelling — WordNet's `Ate` is the Greek goddess of infatuation — and a gloss saying «ate» must
    still reach `eat`, which is a word and survives. Only the goddess is refused."""
    provider = wn_adapter.WordNetProvider(["eat", "ate"])
    assert wn_adapter.is_name_only("ate") is True
    assert provider.lemma("ate", "v") == "eat"          # morphy answers exactly as before
    assert glosses.analyses_of("ate", provider) == ("eat",)


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
    policy = small_policy(max_depth=1)
    graph = closure.build_digraph(provider, policy)
    assert graph["eat"] == {"take", "solid", "food"}   # «take in solid food» — `in` is not a word of this base
    result = closure.seed_closure(graph, ("eat",), policy)
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
