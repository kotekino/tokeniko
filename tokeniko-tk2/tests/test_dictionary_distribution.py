"""D ON THE HANDCRAFTED WORLD — every overlap checkable by reading the sixteen glosses.

R's test file says what it is not testing and this one says the same: the parameters of the walk are
the Captain's and they are ROWS; what is held to account here is that the walk honours them. The
world is the closure engine's own (`tests/lexicon_fixture.py`), because D is built from exactly the
reduction the closure is built from — requirement 21's repair, the stop-list ruling and the name
refusal all reach D through `glosses.lexicon_words_in`, and a D with its own tokeniser would re-open
all three quietly.

The sixteen glosses are small enough that a shared-word set can be written out by hand, which is the
whole reason the numbers below are literals: `walk.v ~ run.v` at the real base is a measurement, and
`go.v ~ move.v` here is an arithmetic anybody can check against the table in the fixture.
"""

import math

import pytest

from tests.lexicon_fixture import LEXICON, FixtureGlossProvider
from tests.seed import closed_class_forms, distribution_policy, reading_policy
from tk2.dictionary import distribution, glosses, matrix
from tk2.dictionary.config import DistributionPolicy


@pytest.fixture
def world():
    return FixtureGlossProvider()


@pytest.fixture
def dimensions(world):
    return tuple(glosses.dimensions_of(LEXICON, world))


@pytest.fixture
def walk():
    """THE standing walk, read from the migration that declares it — and nothing else.

    Under v6 this fixture lowered `min_shared` to one and said so: the declared two was a SCALE
    decision about the real base (where one shared word is `in` joining a fifth of the rows), and a
    world whose definitions are five words long would only have proved that the floor refuses
    everything. The Captain ruled one on 2026-09-09 — measured, and the gate of two turned out to be
    silencing D rather than cleaning it — so the divergence closed itself and the fixture and the
    body now run the same walk.
    """
    return distribution_policy()


@pytest.fixture
def closed():
    """The closed-class forms, injected exactly as a build injects them.

    The standing walk reads structure as `compiled` since 2026-09-10, and `vocabulary_of` REFUSES
    that reading with nothing injected rather than quietly admitting the words — so a fixture that
    left this out would be testing a walk the body does not run.
    """
    return closed_class_forms()


@pytest.fixture
def D(dimensions, world, walk, closed):
    return distribution.build(dimensions, world, walk, closed=closed)


# ------------------------------------------------------------------------------------------------
# the shape
# ------------------------------------------------------------------------------------------------


def test_the_matrix_is_square_over_the_dimensions_it_was_given(D, dimensions):
    assert D.keys == dimensions
    assert [row.key for row in D.rows] == list(dimensions)
    assert all(row.index == dimensions.index(row.key) for row in D.rows)


def test_a_dimension_owns_its_own_axis(D, walk):
    """A matrix whose diagonal is zero has no self-similarity and its cosines stop meaning what they
    look like. D declares its own diagonal rather than borrowing R's identity weight."""
    cell = D.cell("sleep.v", "sleep.v")
    assert cell.weight == walk.identity
    assert cell.source == matrix.SOURCE_AXIS


def test_overlap_is_symmetric_and_R_is_not(D):
    """«These two definitions share these words» is ONE statement about a pair. R's asymmetry exists
    because `entails` and `entailed_by` are two different claims; overlap has no such direction."""
    for row in D.rows:
        for cell in row.cells:
            twin = D.cell(cell.column, row.key)
            assert twin is not None, f"{row.key} -> {cell.column} has no mirror"
            assert twin.weight == cell.weight


def test_nothing_in_D_is_ever_negative(D):
    """The sign is R's alone — it is the antonym column-read primitive — and a D cell must never be
    mistakable for one. There is no negative overlap: two definitions share words or they do not."""
    assert all(cell.weight > 0 for row in D.rows for cell in row.cells)
    assert D.stats()["negative"] == 0


def test_every_cell_names_the_one_relation_D_can_state(D):
    """`gloss_overlap`, and it is deliberately NOT one of R's: co-occurrence is the claim R refuses
    to make, and a cell that could carry either name would blur the seam the split exists for."""
    stated = [cell for row in D.rows for cell in row.cells if cell.source != matrix.SOURCE_AXIS]
    assert stated and all(cell.relation == distribution.GLOSS_OVERLAP for cell in stated)
    assert set(D.stats()["by_relation"]) == {distribution.GLOSS_OVERLAP}


# ------------------------------------------------------------------------------------------------
# the vectors — what a definition contributes
# ------------------------------------------------------------------------------------------------


def test_a_dimensions_gloss_is_read_through_the_closures_own_reduction(dimensions, world, walk, closed):
    """«to go away from a place» names `go` and `place`, and the reduction is the one the digraph
    is built from — so requirement 21, the stop-list ruling and the name refusal hold here too."""
    vectors = distribution.gloss_vectors(dimensions, world, walk, closed)
    assert vectors["leave.v"] == frozenset({"go", "place"})
    # `left` is `leave`'s participle AND a word of its own: the token names both, and no winner is
    # picked at this layer (requirement 21, at the gloss level rather than at the key).
    assert vectors["go.v"] == frozenset({"move", "leave", "left"})


def test_a_dimension_drops_its_own_word_from_its_own_definition(dimensions, world, walk, closed):
    """A tautology states nothing about two concepts — and counting it would hand every POS-sibling
    pair a free shared word, which is exactly the pair (`land.n ~ land.v`) under review."""
    vectors = distribution.gloss_vectors(dimensions, world, walk, closed)
    for key, words in vectors.items():
        assert key.rsplit(".", 1)[0] not in words


def test_the_gloss_is_the_KEYs_and_not_the_words(world, walk):
    """A dimension whose POS the resource does not report speaks nothing at all. The fixture gives
    one gloss per word, so what is checked here is the ASKING — `gloss_of_key` refuses a POS the
    word is not, which is what keeps a refused reading out of D as well as out of the closure."""
    assert world.gloss_of_key("bed.n", "primary") == world.gloss("bed")
    assert world.gloss_of_key("bed.v", "primary") == ""


def test_the_vocabulary_is_the_base_or_the_lexicon_and_says_which(dimensions, world, walk, closed):
    """Under `base` the words counted are the base's own — the prototype's reading, and the one the
    subset's whole argument supports; under `lexicon` a definition may name a word the base lacks."""
    from dataclasses import replace

    words = frozenset(key.rsplit(".", 1)[0] for key in dimensions)
    structural = frozenset(w for w in words if w in closed)
    assert structural, "the fixture world has to contain some function words or this proves nothing"

    base = distribution.vocabulary_of(dimensions, world, walk, closed)
    assert base == words - structural

    whole = distribution.vocabulary_of(dimensions, world, replace(walk, vocabulary="lexicon"), closed)
    assert whole == frozenset(LEXICON) - structural
    assert base <= whole


def test_a_function_word_is_not_a_word_two_definitions_can_share(dimensions, world, walk, closed):
    """The Captain's ruling of 2026-09-10, on the fixture: `me`, `not` and `you` are closed-class
    forms AND dimensions of this little world, and under `compiled` they leave the vocabulary D
    computes overlap from. They keep their own rows — a function word can still BE a dimension; it
    just stops being evidence that two other dimensions are alike.

    On the real base this is the difference between `agreeably.r ~ unpleasantly.r` reading +0.916
    and reading -0.274: stated opposites whose glosses share `in a manner`.
    """
    from dataclasses import replace

    admitted = distribution.vocabulary_of(dimensions, world, replace(walk, structure="admitted"), closed)
    compiled = distribution.vocabulary_of(dimensions, world, walk, closed)

    assert walk.structure == "compiled"
    assert {"me", "not", "you"} <= admitted
    assert not ({"me", "not", "you"} & compiled)
    assert compiled < admitted


def test_a_compiled_reading_with_nothing_injected_is_refused(dimensions, world, walk):
    """Never a silent `admitted`: a build that would be CHANGED by the answer must not be given one
    nobody declared. Same law as the lemma scope and the antonym mode."""
    with pytest.raises(distribution.DistributionIncoherent):
        distribution.vocabulary_of(dimensions, world, walk, None)


def test_a_policy_from_before_the_question_reads_as_it_always_read(dimensions, world, walk):
    """`None` is UNDECLARED, and it is not the same statement as `admitted`. Policy versions 6 and
    7 were written before the question existed; they must keep building the D they always built, or
    their recorded fingerprints stop naming what was measured."""
    from dataclasses import replace

    older = distribution.vocabulary_of(dimensions, world, replace(walk, structure=None), None)
    admitted = distribution.vocabulary_of(
        dimensions, world, replace(walk, structure="admitted"), None
    )

    assert older == admitted
    assert {"me", "not", "you"} <= older


def test_the_sense_cut_reaches_the_resource(dimensions, world, walk, closed):
    """`work`'s second reading is «the place where one labors», and under `all` it is part of the
    definition D is built from. The closure's cut governs membership; this one governs the geometry,
    and they are two rows because they are two questions about the same word."""
    from dataclasses import replace

    primary = distribution.gloss_vectors(dimensions, world, walk, closed)
    every = distribution.gloss_vectors(dimensions, world, replace(walk, senses="all"), closed)
    assert "place" not in primary["work.n"]
    assert "place" in every["work.n"]


# ------------------------------------------------------------------------------------------------
# the measure, the floors and the ceiling
# ------------------------------------------------------------------------------------------------


def test_the_three_measures_are_one_statement_measured_three_ways():
    """Hand arithmetic: two definitions of four and six words sharing two. Jaccard is the harshest,
    cosine the gentlest, and dice sits between them — which is the whole reason the choice is a row."""
    jaccard = distribution.overlap(2, 4, 6, "jaccard")
    dice = distribution.overlap(2, 4, 6, "dice")
    cosine = distribution.overlap(2, 4, 6, "cosine")

    assert jaccard == pytest.approx(2 / 8)
    assert dice == pytest.approx(4 / 10)
    assert cosine == pytest.approx(2 / math.sqrt(24))
    assert jaccard < dice < cosine


def test_a_shared_nothing_is_not_a_cell(walk):
    assert distribution.overlap(0, 5, 5, "jaccard") == 0.0
    assert distribution.value_of(0, 5, 5, walk) == 0.0


def test_the_order_is_measure_then_scale_then_cap_then_floor(walk):
    """A floor applied before the scale would be a floor on a different number. At the standing walk
    a Jaccard of 0.1 already saturates — which is the finding the cap row carries."""
    from dataclasses import replace

    assert distribution.value_of(1, 5, 6, walk) == pytest.approx(walk.cap)
    raw = replace(walk, scale=1.0, cap=1.0, floor=0.0)
    assert distribution.value_of(1, 5, 6, raw) == pytest.approx(1 / 10)


def test_below_the_floor_nothing_is_written(walk):
    from dataclasses import replace

    high = replace(walk, floor=0.49)
    assert distribution.value_of(1, 50, 50, high) == 0.0
    assert distribution.value_of(5, 5, 5, high) == pytest.approx(high.cap)


def test_min_shared_counts_WORDS_and_not_weight(dimensions, world, walk, closed):
    """The floor that does the sizing at the real base. It is a count of shared words on purpose: a
    mass floor would move every time the weighting did, and «how much evidence is there» is not the
    same question as «how much is that evidence worth»."""
    from dataclasses import replace

    one = distribution.build(dimensions, world, walk, closed=closed)
    two = distribution.build(dimensions, world, replace(walk, min_shared=2), closed=closed)
    assert two.stats()["nonzero"] < one.stats()["nonzero"]

    vectors = distribution.gloss_vectors(dimensions, world, walk, closed)
    for row in two.rows:
        for cell in row.cells:
            if cell.source == matrix.SOURCE_AXIS:
                continue
            assert len(distribution.shared_words(vectors, row.key, cell.column)) >= 2


# ------------------------------------------------------------------------------------------------
# the weighting — the Captain's parked question (b), in its mechanism
# ------------------------------------------------------------------------------------------------


def test_uniform_means_one_word_one_vote(dimensions, world, walk, closed):
    assert distribution.word_weights(distribution.gloss_vectors(dimensions, world, walk, closed), walk) == {}


def test_idf_weighs_a_rare_word_above_a_common_one(dimensions, world, walk, closed):
    from dataclasses import replace

    vectors = distribution.gloss_vectors(dimensions, world, walk, closed)
    weights = distribution.word_weights(vectors, replace(walk, weighting="idf"))
    frequency = distribution.document_frequency(vectors)

    common = max(frequency, key=lambda word: frequency[word])
    rare = min(frequency, key=lambda word: frequency[word])
    assert weights[rare] > weights[common]


def test_a_word_nobody_can_avoid_is_worth_little_and_never_nothing(dimensions, world, walk):
    """The smoothing, and the reason for it: at log(N/df) a word every row names weighs exactly
    zero, which deletes it from the UNION as well as the intersection — and two definitions sharing
    nothing but it would then score a perfect 0/0."""
    from dataclasses import replace

    everywhere = {key: frozenset({"in"}) for key in dimensions}
    weights = distribution.word_weights(everywhere, replace(walk, weighting="idf"))
    assert weights["in"] > 0
    assert weights["in"] == pytest.approx(math.log(2.0))


# ------------------------------------------------------------------------------------------------
# the pollution figure — what a weighting can reach and what it cannot
# ------------------------------------------------------------------------------------------------


def test_the_pair_figure_is_membership_and_the_mass_figure_is_weighting(dimensions, world, walk, closed):
    """Two numbers rather than one, because they answer different questions: which pairs rest on
    nothing but the words everybody uses (a weighting cannot move it — only a filter could), and how
    much of the shared mass those words carry (which is exactly what a weighting moves)."""
    from dataclasses import replace

    vectors = distribution.gloss_vectors(dimensions, world, walk, closed)
    frequency = distribution.document_frequency(vectors)
    # The world's OWN loudest words, so the fixture is asking the question the real base asks: at
    # the full base these are `in`, `by`, `be`, `as`, and what makes them junk is their frequency.
    junk = frozenset(sorted(frequency, key=lambda word: (-frequency[word], word))[:2])
    idf = distribution.word_weights(vectors, replace(walk, weighting="idf"))

    uniform = distribution.junk_pollution(vectors, junk)
    weighted = distribution.junk_pollution(vectors, junk, weights=idf)

    assert uniform["pairs_only_junk"] == weighted["pairs_only_junk"]
    assert weighted["mass_from_junk_pct"] < uniform["mass_from_junk_pct"]


# ------------------------------------------------------------------------------------------------
# the dual read — two geometries, one number, and the parameter that says how much of each
# ------------------------------------------------------------------------------------------------


def _relational(dimensions):
    """A tiny R over the same key space: one opposition, stated both ways."""
    from tk2.dictionary.matrix import Cell, Matrix, MatrixRow, Provenance

    opposed = {"left.n": "right.n", "right.n": "left.n"}
    rows = []
    for index, key in enumerate(dimensions):
        cells = [Cell(column=key, weight=1.0, relation="identity", source=matrix.SOURCE_AXIS,
                      via=(Provenance("identity", 1.0),))]
        if key in opposed:
            cells.append(Cell(column=opposed[key], weight=-1.0, relation="antonym",
                              via=(Provenance("antonym", -1.0),)))
        rows.append(MatrixRow(key=key, index=index, cells=tuple(cells)))
    return Matrix(name="dictionary_base_relations", keys=tuple(dimensions), rows=tuple(rows))


def test_a_mix_of_zero_is_R_alone(dimensions, D):
    R = _relational(dimensions)
    for a, b in (("left.n", "right.n"), ("go.v", "move.v"), ("bed.n", "sleep.v")):
        assert matrix.blended_cosine(R, D, a, b, 0.0) == pytest.approx(R.cosine(a, b))


def test_the_blend_concatenates_and_never_averages(dimensions, D):
    """R's columns and D's are two different axes, which is what keeps a positive gloss overlap
    sitting BESIDE a stated opposition instead of cancelling it. `left.n ~ right.n` is defined in
    the same words — «the direction opposite to …» — so this is the review's own failure case."""
    R = _relational(dimensions)
    assert R.cosine("left.n", "right.n") < 0
    assert D.cosine("left.n", "right.n") > 0

    blended = [matrix.blended_cosine(R, D, "left.n", "right.n", mix) for mix in (0.0, 0.5, 1.0, 4.0)]
    assert blended[0] < 0
    assert blended == sorted(blended), "a louder D can only ever pull the reading upward"
    assert blended[-1] > 0, "and far enough up it buries the sign — which is why nobody has ruled it"


def test_the_ruled_mix_keeps_R_the_louder_geometry(dimensions, D):
    """The ruling of 2026-09-09 as a PROPERTY and not a number: at the declared mix a stated
    opposition still reads as one, even between two definitions written in the same words.

    `left.n ~ right.n` is this world's version of `enter ~ leave` — «the direction opposite to …» —
    which is the pair that turns positive at +0.063 at the full base under mix 1.0 and survives at
    -0.059 under 0.5. The number is the migration's; what belongs here is that the reading the rows
    declare does not bury the sign the antonym column-read primitive depends on.
    """
    R = _relational(dimensions)
    ruled = reading_policy()
    assert D.cosine("left.n", "right.n") > 0, "the topical overlap is really there"
    assert matrix.blended_cosine(R, D, "left.n", "right.n", ruled.mix) < 0


def test_a_blend_across_two_key_spaces_is_refused(dimensions, D):
    """Arithmetic over columns that are not the same words. Refused rather than computed."""
    R = _relational(dimensions[:-1])
    with pytest.raises(ValueError):
        matrix.blended_cosine(R, D, "go.v", "move.v", 1.0)


def test_a_key_that_is_not_a_dimension_reads_as_none_and_not_as_zero(dimensions, D):
    """Requirement 15: «these two are unrelated» and «one of them is not in the base» are different
    answers, and a bar that scored the second as the first would report a membership defect as a
    geometry result."""
    R = _relational(dimensions)
    assert matrix.blended_cosine(R, D, "go.v", "elephant.n", 1.0) is None


# ------------------------------------------------------------------------------------------------
# the policy refuses what it cannot build
# ------------------------------------------------------------------------------------------------


def test_a_walk_the_engine_has_no_measure_for_is_refused():
    with pytest.raises(ValueError):
        DistributionPolicy(senses="primary", vocabulary="base", measure="euclidean",
                           weighting="uniform", min_shared=2, scale=5.0, cap=0.5, floor=0.1,
                           identity=1.0)


def test_a_floor_at_or_above_the_cap_is_refused():
    """Every cell D could write would be refused — a policy that declares an empty matrix by
    accident rather than on purpose."""
    with pytest.raises(ValueError):
        DistributionPolicy(senses="primary", vocabulary="base", measure="jaccard",
                           weighting="uniform", min_shared=2, scale=5.0, cap=0.1, floor=0.5,
                           identity=1.0)


def test_min_shared_below_one_is_not_a_floor_at_all():
    with pytest.raises(ValueError):
        DistributionPolicy(senses="primary", vocabulary="base", measure="jaccard",
                           weighting="uniform", min_shared=0, scale=5.0, cap=0.5, floor=0.1,
                           identity=1.0)
