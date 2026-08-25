"""THE SEED PROPOSAL on the handcrafted worlds — every number checkable by hand.

The proposal is the PROPOSE half of «generated-then-curated», so what has to be right here is not
which words it picks (that is the Captain's) but that its labels are honest: the ranking is the
whole ranking, an excluded word says why, and `k` counts seeds rather than rows.

The sixteen-word world (`tests/lexicon_fixture.py`) already contains the shape both exclusions are
about — `not` is a function word and `left` is `leave`'s participle — so the two are testable at a
scale a person can verify, and the `use`/`used` world holds requirement 21's other reported form.
"""

import pytest

from tests.lexicon_fixture import FixtureGlossProvider, use_used_provider
from tk2.dictionary import closure, proposal
from tk2.dictionary.config import ClosurePolicy


def fixture_policy(max_depth: int = 2, max_size: int = 1000, senses: str = "primary"):
    """The sixteen-word world's own policy, stated rather than defaulted — `test_dictionary_
    closure.py`'s argument, and since T4b there is no default anywhere in code to fall back on."""
    return ClosurePolicy(max_depth=max_depth, max_size=max_size, senses=senses)


@pytest.fixture
def provider():
    return FixtureGlossProvider()


@pytest.fixture
def graph(provider):
    return closure.build_digraph(provider, fixture_policy())


# ------------------------------------------------------------------------------------------------
# the ranking number
# ------------------------------------------------------------------------------------------------


def test_in_degree_counts_the_definitions_that_name_a_word(graph):
    counts = proposal.in_degrees(graph)
    # `not` is named by `me`, `you` and `negation`; `place` by `leave`, `bed` and `move`.
    assert counts["not"] == 3
    assert counts["place"] == 3
    assert counts["right"] == 1


def test_every_node_is_counted_even_at_zero(graph):
    """A word nothing defines is a fact about the resource. A Counter that omitted it would answer
    the same as one that had never heard of the word."""
    counts = proposal.in_degrees(graph)
    assert set(counts) == set(graph)


# ------------------------------------------------------------------------------------------------
# the de-inflection guard
# ------------------------------------------------------------------------------------------------


def test_an_inflection_names_the_word_it_is_a_form_of(graph, provider):
    lexicon = frozenset(graph)
    assert proposal.inflection_of("left", lexicon, provider) == ("leave",)
    assert proposal.inflection_of("right", lexicon, provider) == ()


def test_used_is_uses_inflection_in_requirement_21s_other_world():
    """The second reported collision, and the reason the guard exists: `used` ranks on the token
    `used`, and every gloss holding that token gave `use` an in-edge too."""
    provider = use_used_provider()
    graph = closure.build_digraph(provider, fixture_policy())
    assert proposal.inflection_of("used", frozenset(graph), provider) == ("use",)
    assert proposal.inflection_of("use", frozenset(graph), provider) == ()


def test_a_lemma_outside_the_lexicon_is_not_an_inflection_link(graph, provider):
    """The link has to land on a word that is really a node, or the in-degree it is accused of
    borrowing does not exist."""
    lexicon = frozenset(graph) - {"leave"}
    assert proposal.inflection_of("left", lexicon, provider) == ()


def test_the_share_says_which_spelling_is_the_real_word(graph, provider):
    """`left`'s share of `leave` is 1.0 here — every in-edge `leave` has came through the token
    `left` — which is the `number`/`numb` shape the guard gets backwards at scale. The number is
    reported so the cost is visible; where the line falls is the Captain's."""
    counts = proposal.in_degrees(graph)
    assert proposal.inflection_share("left", ("leave",), counts) == pytest.approx(1.0)
    assert proposal.inflection_share("right", (), counts) is None


# ------------------------------------------------------------------------------------------------
# the ranking, labelled
# ------------------------------------------------------------------------------------------------


def test_the_whole_ranking_comes_back_with_its_exclusions_named(graph, provider):
    """What was excluded and at what rank is the most argued-about part of a proposal. A function
    that returned only the survivors would be asking to be trusted."""
    ranking = proposal.structural_ranking(graph, provider, closed_forms=("not",))
    assert len(ranking) == len(graph)
    assert [c.in_degree for c in ranking] == sorted((c.in_degree for c in ranking), reverse=True)

    by_word = {c.word: c for c in ranking}
    assert by_word["not"].excluded == proposal.CLOSED_CLASS
    assert by_word["left"].excluded == proposal.INFLECTION
    assert by_word["left"].inflection_of == ("leave",)
    assert by_word["place"].is_candidate


def test_a_candidate_carries_what_the_ruling_is_made_on(graph, provider):
    """The gloss column is not a debug print: it is what exposed `in` = *inch* and `are` = a unit of
    area, and the dimensions say how many axes seeding the word would really add."""
    ranking = proposal.structural_ranking(graph, provider)
    place = next(c for c in ranking if c.word == "place")
    assert place.gloss.startswith("an area where")
    assert place.dimensions == ("n", "v")

    # `left` is not a base form of a verb, so it mints no `left.v` — requirement 21 at the key,
    # visible here as a dimension count that disagrees with the resource's POS list.
    left = next(c for c in ranking if c.word == "left")
    assert "v" not in left.dimensions


def test_k_counts_seeds_and_not_rows(graph, provider):
    """«Top 100» must mean a hundred seeds, never «a hundred rows of which sixty were function
    words» — that is the number the Captain is ruling on."""
    ranking = proposal.structural_ranking(graph, provider, closed_forms=("not", "place"))
    seeds = proposal.structural_seeds(ranking, 3)
    assert len(seeds) == 3
    assert "not" not in seeds and "place" not in seeds
    assert all(next(c for c in ranking if c.word == w).is_candidate for w in seeds)


def test_asking_for_more_than_there_are_gives_what_there_is(graph, provider):
    ranking = proposal.structural_ranking(graph, provider)
    assert len(proposal.structural_seeds(ranking, 10_000)) == len(
        [c for c in ranking if c.is_candidate]
    )


def test_the_excluded_head_is_the_price_of_one_exclusion(graph, provider):
    ranking = proposal.structural_ranking(graph, provider, closed_forms=("not", "me"))
    closed = proposal.excluded_head(ranking, proposal.CLOSED_CLASS)
    assert [c.word for c in closed] == ["not", "me"]
    assert [c.word for c in proposal.excluded_head(ranking, proposal.INFLECTION)] == ["left"]
    assert proposal.excluded_head(ranking, proposal.CLOSED_CLASS, limit=1) == closed[:1]


# ------------------------------------------------------------------------------------------------
# at scale: the ruled seed list is a DERIVATION, not a paste
# ------------------------------------------------------------------------------------------------


@pytest.mark.wordnet
def test_the_ruled_structural_seeds_re_derive_exactly():
    """Migration 0005 writes 200 structural seeds as a literal, and a literal nobody can regenerate
    is a paste. This runs the migration's own `derive_structural_seeds()` — the same
    `structural_ranking` and `structural_seeds` the tool calls, over the whole WordNet digraph — and
    demands the same 200 words with the same ranks and the same in-degrees.

    It is the most expensive test in the suite (~7s: the digraph is 68,779 nodes) and it earns it.
    Everything else about the ruled policy is checked on the ROWS, which cannot notice that the rows
    were derived from a ranking that no longer says what they claim — a WordNet upgrade, a change in
    `glosses.py`, a widened closed-class table would all move this list silently.
    """
    from tests.seed import migration

    module = migration(5)
    assert module.derive_structural_seeds() == tuple(
        tuple(entry) for entry in module.STRUCTURAL_SEEDS
    )
