"""R ON THE HANDCRAFTED WORLD — every cell checkable by reading the fixture table.

The eleven-dimension relation world (`tests/lexicon_fixture.py`) holds one instance of each thing
the cell walk has to get right, at a scale a person can verify: a shared synset, a pair with TWO
relations, the one negative weight, a cross-POS cell, a reverse read, a relation pointing outside
the base, and a silent row. What is NOT tested here is which weights are correct — those are the
Captain's and they are rows; what is tested is that the walk honours them.

The weights come from the migration that declares them (policy v3, `db/0006`), not from numbers
retyped here. A test with its own copy of a curated value is a test that keeps passing after the
Captain moves it.
"""

import pytest

from tests.lexicon_fixture import FixtureRelationProvider
from tests.seed import relation_policy
from tk2.dictionary import keys, matrix, relations
from tk2.dictionary.config import RelationPolicy

KEYS = (
    "chew.v",
    "devour.v",
    "die.v",
    "eat.v",
    "food.n",
    "full.a",
    "hot.a",
    "hungry.a",
    "kill.v",
    "swallow.v",
    "temperature.n",
)


@pytest.fixture
def provider():
    return FixtureRelationProvider()


@pytest.fixture
def policy():
    return relation_policy()


@pytest.fixture
def R(provider, policy):
    return relations.build(KEYS, provider, policy)


# ------------------------------------------------------------------------------------------------
# the shape
# ------------------------------------------------------------------------------------------------


def test_the_matrix_is_square_over_the_dimensions_it_was_given(R):
    """Never over senses. `devour.v` speaks two senses and is ONE row: the whole architecture is
    that a sense rides on the base, and a senses x senses matrix is the billion-cell mistake."""
    assert R.keys == KEYS
    assert [row.key for row in R.rows] == list(KEYS)
    assert all(row.index == KEYS.index(row.key) for row in R.rows)


def test_a_dimension_owns_its_own_axis(R, policy):
    """A matrix whose diagonal is zero has no self-similarity and its cosines stop meaning what they
    look like. The diagonal is its own SOURCE so a density count can never swallow it."""
    cell = R.cell("eat.v", "eat.v")
    assert cell.weight == policy.weight_of("identity")
    assert cell.source == matrix.SOURCE_AXIS
    assert R.stats()["by_source"] == {matrix.SOURCE_MINED: R.stats()["nonzero"]}


def test_a_relation_pointing_outside_the_base_writes_no_cell(R):
    """`eat.v` names `consume.v.01` as its hypernym and no dimension of this world speaks it. There
    is no axis to write to, and inventing one would be membership by side effect."""
    assert "hypernym_1" not in relations.relations_of(R, "eat.v")
    assert all(cell.column in KEYS for row in R.rows for cell in row.cells)


def test_a_dimension_no_relation_reaches_is_silent_and_says_so(R):
    """`food.n` states nothing and nothing states it. A finding about the resource, not a defect —
    at the full base 318 dimensions are silent and 141 of them are adverbs."""
    assert R.row("food.n").is_silent
    assert not R.row("eat.v").is_silent
    assert R.stats()["silent_rows"] == 1


# ------------------------------------------------------------------------------------------------
# the relations themselves
# ------------------------------------------------------------------------------------------------


def test_two_dimensions_that_share_a_sense_are_synonyms(R, policy):
    """The one relation the builder computes rather than asks for: `eat.v` and `devour.v` share
    `eat.v.01`, and that IS synonymy. Both directions, because both speak it."""
    assert R.cell("eat.v", "devour.v").weight == policy.weight_of("synonym")
    assert R.cell("devour.v", "eat.v").relation == "synonym"


def test_synonymy_answers_first_and_the_loser_is_still_recorded(R, policy):
    """`eat.v` also states `devour.v.02` as a troponym, so two relations hold. The cell is
    synonymy's — the prototype's precedence, kept — and `via` carries both, because «synonym, and
    also a troponym» is a different fact from «synonym alone» and curation reads exactly that."""
    cell = R.cell("eat.v", "devour.v")
    assert cell.relation == "synonym"
    assert [p.relation for p in cell.via] == ["synonym", "troponym"]
    assert cell.via[1].weight == policy.weight_of("troponym")


def test_the_antonym_cell_is_negative_and_the_sign_is_the_point(R, policy):
    """`row[X][index(W)] < 0` is how opposition is asked. Nothing here averages it away."""
    cell = R.cell("hungry.a", "full.a")
    assert cell.weight == policy.weight_of("antonym") < 0
    assert R.cell("full.a", "hungry.a").weight < 0
    assert R.stats()["negative"] == 2


def test_a_reverse_read_is_its_own_weaker_cell(R, policy):
    """The relation is DIRECTIONAL: «eat entails swallow» and «swallow is entailed by eat» are two
    statements of different strength, not one symmetric number."""
    assert R.cell("eat.v", "swallow.v").relation == "entails"
    assert R.cell("swallow.v", "eat.v").relation == "entailed_by"
    assert policy.weight_of("entailed_by") < policy.weight_of("entails")
    assert R.cell("kill.v", "die.v").relation == "causes"
    assert R.cell("die.v", "kill.v").relation == "caused_by"


def test_a_cell_may_cross_the_pos_boundary(R):
    """`attribute` (hot ~ temperature) and `derivational` (able ~ ability) are cross-POS by nature,
    and a same-POS-only matrix could not state them at all — which is half of why the base splits by
    part of speech in the first place. Not a knob: a knob here would be a second base."""
    assert keys.pos_of("hot.a") != keys.pos_of("temperature.n")
    assert R.cell("hot.a", "temperature.n").relation == "attribute"


def test_every_cell_can_say_which_relation_made_it(R):
    """Requirement 18, as a property of every cell rather than of the ones anybody looked at."""
    for row in R.rows:
        for cell in row.cells:
            assert cell.relation
            assert cell.via and cell.via[0].relation
            assert cell.source in (matrix.SOURCE_MINED, matrix.SOURCE_AXIS)


# ------------------------------------------------------------------------------------------------
# the tie-break
# ------------------------------------------------------------------------------------------------


def test_two_equally_strong_relations_resolve_by_the_declared_order(policy):
    """The reason a weight row carries a `position`. `troponym` and `hyponym_1` are both 0.70; the
    cell must not be free to pick either because a dict happened to iterate one way today."""
    senses = {"a.v": ("a.v.01",), "b.v": ("b.v.01",)}
    edges = {"a.v": {"troponym": frozenset({"b.v.01"}), "hyponym_1": frozenset({"b.v.01"})}}
    built = relations.build(
        ("a.v", "b.v"), FixtureRelationProvider(senses=senses, edges=edges), policy
    )
    cell = built.cell("a.v", "b.v")

    assert policy.weight_of("troponym") == policy.weight_of("hyponym_1")
    assert policy.precedence("troponym") < policy.precedence("hyponym_1")
    assert cell.relation == "troponym"
    assert [p.relation for p in cell.via] == ["troponym", "hyponym_1"]


def test_a_relation_switched_off_writes_no_cell(policy):
    """A weight of 0.0 is a DECLARATION that a relation does not count — the prototype's own
    mechanism, and the only way to switch one off. It is not the same as an absent row."""
    off = RelationPolicy(
        weights=tuple((name, 0.0 if name == "entails" else weight) for name, weight in policy.weights),
        curated=policy.curated,
        reciprocal_weight=policy.reciprocal_weight,
        cues=policy.cues,
        defaults=policy.defaults,
    )
    built = relations.build(KEYS, FixtureRelationProvider(), off)
    assert built.cell("eat.v", "swallow.v") is None
    assert built.cell("swallow.v", "eat.v").relation == "entailed_by"   # the reverse still counts


# ------------------------------------------------------------------------------------------------
# the two sides have to name the same relations
# ------------------------------------------------------------------------------------------------


def test_a_relation_the_policy_does_not_weight_is_refused(policy):
    """The silent no-op in its matrix form: a mined relation nobody weighted would be a cell quietly
    dropped, and R would be denser or sparser than the policy beside it claims."""
    provider = FixtureRelationProvider(relations=("antonym", "sibling_of"))
    with pytest.raises(relations.RelationsIncoherent) as excinfo:
        relations.build(("hungry.a", "full.a"), provider, policy)
    assert "sibling_of" in str(excinfo.value)


def test_a_weight_for_a_relation_nothing_produces_is_refused(policy):
    """The other direction: a curated decision that never takes effect is one nobody can see
    failing. `RelationsIncoherent` says which side is short."""
    weights = policy.weights + (("smells_like", 0.4),)
    with pytest.raises(relations.RelationsIncoherent) as excinfo:
        relations.build(KEYS, FixtureRelationProvider(), RelationPolicy(weights=weights))
    assert "smells_like" in str(excinfo.value)


def test_a_sense_key_can_never_be_a_dimension(policy):
    """Both levels of the key convention, enforced where the axes are named: `eat.v.01` is a SENSE
    and senses ride on the base. A matrix over them is the billion-cell mistake."""
    with pytest.raises(keys.InvalidKey):
        relations.build(("eat.v.01",), FixtureRelationProvider(), policy)


# ------------------------------------------------------------------------------------------------
# reading it back
# ------------------------------------------------------------------------------------------------


def test_both_directions_are_read_because_r_is_asymmetric(R):
    """A reader that took whichever direction it found first would report `kill -> die` and
    `die -> kill` as the same statement."""
    forward, reverse = relations.stated_between(R, "kill.v", "die.v")
    assert (forward.relation, reverse.relation) == ("causes", "caused_by")
    mute = relations.stated_between(R, "food.n", "die.v")
    assert mute == (None, None), "an absent cell is MUTE — not a pass, not a miss"


def test_the_cosine_says_none_when_a_key_is_not_a_dimension(R):
    """«these two are unrelated» and «one of them is not in the base» are different answers, and a
    bar that scored the second as the first would report a membership defect as a geometry result."""
    assert R.cosine("eat.v", "runway.n") is None
    assert R.cosine("food.n", "die.v") == 0.0
    assert R.cosine("eat.v", "devour.v") > 0


def test_a_row_survives_the_stored_shape(R):
    """The cells have to cross into mongo and back unchanged — including `via`, which is what a
    later retreat reads. A key contains a dot, so a cell is a VALUE in a list and never a field."""
    for row in R.rows:
        for cell in row.cells:
            assert matrix.Cell.from_row(cell.as_row()) == cell


def test_the_in_memory_store_hands_back_what_it_was_given(R):
    store = matrix.InMemoryMatrixStore()
    assert store.write(R, build="test") == len(KEYS)
    assert store.keys("test", R.name) == KEYS
    assert store.row("test", R.name, "eat.v") == R.row("eat.v")
    assert len(list(store.rows("test", R.name))) == len(KEYS)


# ------------------------------------------------------------------------------------------------
# reading two matrices against each other
# ------------------------------------------------------------------------------------------------


def test_a_diff_names_the_cells_that_moved_and_not_only_how_many(R, provider, policy):
    """The instrument every later question needs: the lemma-scope A/B, T4's `derivational`
    down-weight, a curation batch, a resource bump. A tally answers «how many moved» and never
    «which», and the whole claim of R is that a cell can be asked what made it."""
    quieter = relations.build(
        KEYS,
        FixtureRelationProvider(edges={k: v for k, v in provider._edges.items() if k != "hot.a"}),
        policy,
    )
    moved = matrix.diff(R, quieter)

    assert [(row, cell.column) for row, cell in moved["removed"]] == [("hot.a", "temperature.n")]
    assert moved["added"] == [] and moved["changed"] == []


def test_a_diff_across_two_key_spaces_is_refused(R, provider, policy):
    """It would report every dimension as changed and none of it would mean anything."""
    smaller = relations.build(KEYS[:3], provider, policy)
    with pytest.raises(ValueError):
        matrix.diff(R, smaller)
