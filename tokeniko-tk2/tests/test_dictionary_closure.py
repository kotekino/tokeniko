"""The closure engine on the handcrafted world — every number here is checkable by hand.

The fixture (`tests/lexicon_fixture.py`) is sixteen words and its whole shape is documented there.
Three things are under test: the reduction of a definition to lexicon words, the closed sets, and
the seed closure's two cuts — with THE `right` RING as a named regression.
"""

import pytest

from tests.lexicon_fixture import LEXICON, FixtureGlossProvider
from tk2.dictionary import closure, glosses
from tk2.dictionary.config import ClosurePolicy


@pytest.fixture
def provider():
    return FixtureGlossProvider()


@pytest.fixture
def graph(provider):
    return closure.build_digraph(provider)


# ------------------------------------------------------------------------------------------------
# the reduction
# ------------------------------------------------------------------------------------------------


def test_a_definition_becomes_the_lexicon_words_it_names(graph):
    assert graph["sleep"] == {"rest", "bed"}
    assert graph["bed"] == {"furniture", "place", "sleep"}


def test_the_self_reference_is_dropped(provider):
    """«land: the land on which real estate is located» states nothing about two concepts. Mining it
    is how a POS-split base gets re-merged by an edge that only says a word is itself."""
    lexicon = frozenset(LEXICON)
    assert "work" not in glosses.definition_in_lexicon("work", lexicon, provider)


def test_an_inflected_token_lands_on_its_lemma(graph):
    """«the line along which something *moves*» reaches `move`. Without this the digraph is a
    surface-form graph and half the definitions are silent."""
    assert graph["direction"] == {"move"}


def test_a_definition_that_names_no_lexicon_word_is_silent(graph):
    """These can never belong to a closed set, and counting them is how you find out that a lexicon's
    definitions are written in some other vocabulary."""
    assert graph["furniture"] == set()
    assert closure.digraph_stats(graph)["silent"] == 2


def test_a_stop_word_never_becomes_an_edge():
    """The filter runs before the lexicon check — which is exactly why the real adapter cannot
    reproduce the Captain's own closure example (nltk's English stop list contains `me`, `you` and
    `not`). Here the mechanism is pinned on a stop list this test controls."""
    plain = FixtureGlossProvider()
    muted = FixtureGlossProvider(stopwords=plain.stopwords() | {"rest"})
    assert closure.build_digraph(plain)["sleep"] == {"rest", "bed"}
    assert closure.build_digraph(muted)["sleep"] == {"bed"}


def test_the_sense_mode_reaches_the_resource(provider):
    """`work` is silent on its primary sense and names `place` on its second. A build that changed
    `senses` and got the same graph would mean the mode never left the config."""
    assert closure.build_digraph(provider, ClosurePolicy(senses="primary"))["work"] == set()
    assert closure.build_digraph(provider, ClosurePolicy(senses="all"))["work"] == {"place"}


# ------------------------------------------------------------------------------------------------
# closed sets — the Captain's method
# ------------------------------------------------------------------------------------------------


def test_the_captains_example_is_closed(graph):
    """me -> not you | you -> not me | not -> negation | negation -> not. His own words,
    2026-08-12: the set defines itself and never leaves."""
    assert closure.is_closed(graph, {"me", "not", "you", "negation"}) is True


def test_the_captains_example_is_not_MINIMAL(graph):
    """`me` and `you` reach `not` without `not` reaching back, so the minimal closed set inside his
    example is {not, negation}. Both facts are true, and the difference is why `is_closed` (ask it
    about a set you propose) and `closed_sets` (the floor) are two functions."""
    assert closure.is_closed(graph, {"me", "you"}) is False
    multiword = [c for c in closure.closed_sets(graph) if len(c) > 1]
    assert multiword == [["negation", "not"]]


def test_a_silent_word_is_a_closed_set_of_one(graph):
    """Trivially — it names nothing, so nothing leaves. Worth pinning because it is the reason the
    interesting closed sets are the ones with more than one word."""
    assert ["work"] in closure.closed_sets(graph)


def test_components_are_deterministic(graph):
    """Same graph, same components, same order — neighbours are walked sorted. A subset that
    reshuffled between runs would make every later measurement incomparable."""
    assert closure.strongly_connected_components(graph) == closure.strongly_connected_components(graph)


def test_words_outside_the_graph_cannot_break_closure(graph):
    """A word that is not a node was never an edge to leave to."""
    assert closure.is_closed(graph, {"not", "negation", "unheard-of"}) is True


# ------------------------------------------------------------------------------------------------
# the seed closure and its two cuts
# ------------------------------------------------------------------------------------------------

SEEDS = ("sleep", "leave")


def test_the_closure_grows_ring_by_ring(graph):
    result = closure.seed_closure(graph, SEEDS, ClosurePolicy(max_depth=2))
    assert result.layers[0] == ("leave", "sleep")
    assert result.layers[1] == ("bed", "go", "place", "rest")
    assert result.layers[2] == ("furniture", "left", "move", "work")
    assert set(result.words) == {
        "bed", "furniture", "go", "leave", "left", "move", "place", "rest", "sleep", "work",
    }


def test_a_seed_the_lexicon_lacks_is_reported_not_dropped(graph):
    """Requirement 15: membership is a defect too, and a seed that is not a word is the first place
    to look for one. Silence here is how run r1 scored 12 of 18 pairs and nobody knew why."""
    result = closure.seed_closure(graph, ("sleep", "runway"), ClosurePolicy(max_depth=1))
    assert result.missing == ("runway",)
    assert "runway" not in result.words


def test_the_depth_cut_is_a_parameter(graph):
    """Not a constant. The number is the thing the Captain moves when he disagrees with the boundary
    it draws — so it has to be reachable from the policy and visible in its fingerprint."""
    sizes = [
        len(closure.seed_closure(graph, SEEDS, ClosurePolicy(max_depth=d)).words)
        for d in (0, 1, 2, 3)
    ]
    assert sizes == [2, 6, 10, 12]


def test_a_closure_that_exhausts_the_graph_says_so(graph):
    """«we stopped» and «there was nothing left» are different facts and `stopped` must not blur
    them: only the first one means a boundary was drawn."""
    result = closure.seed_closure(graph, SEEDS, ClosurePolicy(max_depth=9))
    assert result.stopped == "exhausted"
    assert result.unexpanded == ()


def test_the_size_cap_admits_a_whole_ring_or_none_of_it(graph):
    """Trimming a ring alphabetically would make membership depend on spelling. A run that hits the
    cap says `size` and the answer is a different policy, not a smaller alphabet."""
    result = closure.seed_closure(graph, SEEDS, ClosurePolicy(max_depth=9, max_size=3))
    assert result.stopped == "size"
    assert len(result.words) == 6          # the ring that broke the cap came in whole
    assert result.layers[-1] == ("bed", "go", "place", "rest")


# --- THE `right` RING — the review's finding of 2026-08-12, pinned ------------------------------


def test_the_last_ring_is_admitted_but_never_expanded(graph):
    """The depth cut's actual mechanism, stated. `left` is IN the subset and its own definition was
    never followed."""
    result = closure.seed_closure(graph, SEEDS, ClosurePolicy(max_depth=2))
    assert "left" in result.words
    assert result.stopped == "depth"
    assert result.unexpanded == ("furniture", "left", "move", "work")


def test_right_sits_exactly_one_ring_past_the_cut(graph):
    """THE regression. The Captain found this by looking at the map: `left` inside, `right` outside,
    named only by a word the subset already had. The boundary is allowed to be there — it is not
    allowed to be invisible, so the closure reports its own ring."""
    result = closure.seed_closure(graph, SEEDS, ClosurePolicy(max_depth=2))
    assert "right" not in result.words
    assert result.one_ring_past(graph) == ("direction", "right")


def test_one_more_ring_takes_right_in(graph):
    """The cut is the only thing keeping it out — which is what makes it a policy question rather
    than a defect."""
    result = closure.seed_closure(graph, SEEDS, ClosurePolicy(max_depth=3))
    assert "right" in result.words


def test_left_enters_through_an_inflection_REQUIREMENT_21(graph):
    """`go`'s definition says «as when one has *left*» — *leave*'s participle. The engine mints
    `left` the DIRECTION from it, because the surface form is itself a lexicon word and the surface
    form is tried first.

    This test pins TODAY's behaviour, and today's behaviour is the defect requirement 21 names. When
    the POS-aware repair lands, this test is REWRITTEN (the assertion inverts), never deleted: the
    fixture's lemma table already knows `left -> leave` and nothing consults it yet.
    """
    assert graph["go"] == {"move", "left"}
    assert "leave" in FixtureGlossProvider().lemmas("left")


# ------------------------------------------------------------------------------------------------
# the per-seed cost
# ------------------------------------------------------------------------------------------------


def test_per_seed_cost_separates_cheap_seeds_from_expensive_ones(graph):
    """The QM's counter, quantified: function words close cheaply, the content words pull in the
    world. Measured rather than assumed — that was the whole point of the instrument."""
    costs = dict(closure.per_seed_cost(graph, ("not", "sleep", "runway"), ClosurePolicy(max_depth=2)))
    assert costs["not"] == 2               # not -> negation -> not, and it is done
    assert costs["sleep"] > costs["not"]
    assert costs["runway"] is None         # not a lexicon word: a membership question, not a cost
