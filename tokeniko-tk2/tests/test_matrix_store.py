"""THE BASE'S DOOR — a built matrix into mongo and back, cell for cell.

What has to be true here is not that rows can be written (every other collection proves that) but
that R survives the trip WHOLE: the sign, the provenance list, the curated evidence, and the
dimension order the indices are only meaningful against. A base that came back with its `via`
flattened or its columns re-sorted would look perfectly healthy and be wrong everywhere.

Live, and skipped without a local MongoDB, exactly like the rest of the datatier's tests. The pure
side runs on `InMemoryMatrixStore` next door, in `tests/test_dictionary_relations.py`.
"""

import pytest

from tests.lexicon_fixture import FixtureRelationProvider
from tests.seed import relation_policy
from tk2.dictionary import curation, matrix, relations
from tk2.dictionary.matrix import SOURCE_CURATED, Cell, Provenance

pytestmark = pytest.mark.mongo

KEYS = ("die.v", "eat.v", "food.n", "full.a", "hungry.a", "kill.v", "swallow.v")


@pytest.fixture
def policy():
    return relation_policy()


@pytest.fixture
def built(policy):
    senses = {key: (f"{key}.01",) for key in KEYS}
    senses["eat.v"] = ("eat.v.01",)
    provider = FixtureRelationProvider(
        senses=senses,
        edges={
            "eat.v": {"entails": frozenset({"swallow.v.01"})},
            "kill.v": {"causes": frozenset({"die.v.01"})},
            "hungry.a": {"antonym": frozenset({"full.a.01"})},
        },
    )
    return relations.build(KEYS, provider, policy)


@pytest.fixture
def store(clean_db):
    """`clean_db` empties the TEST models; the base's own collections are real ones and are emptied
    here, before rather than after, so a failing test leaves its rows behind to be looked at."""
    from tk2.core.models import BASE_MODELS
    from tk2.datatier.matrix_store import MongoMatrixStore

    for model in BASE_MODELS:
        clean_db[model.Settings.name].delete_many({})
    return MongoMatrixStore(clean_db)


def test_a_matrix_survives_the_trip_whole(store, built):
    assert store.write(built, build="t1") == len(KEYS)
    assert store.keys("t1") == KEYS
    assert store.matrix("t1", "base_r").rows == built.rows


def test_the_sign_and_the_provenance_come_back(store, built):
    store.write(built, build="t1")
    read = store.matrix("t1", "base_r")

    assert read.cell("hungry.a", "full.a").weight < 0, "the antonym sign is the whole primitive"
    assert read.cell("swallow.v", "eat.v").relation == "entailed_by"
    assert read.cell("eat.v", "swallow.v").via == built.cell("eat.v", "swallow.v").via


def test_a_curated_cell_keeps_its_hand_and_its_evidence(store, built, policy):
    """A curated cell is distinguishable from a mined one FOREVER, which means the field and the
    verbatim evidence have to survive storage — not only the number."""
    proposal = curation.Proposal(
        source_key="food.n",
        target_key="eat.v",
        relation="involves",
        weight=policy.curated_weight("involves"),
        sense="food.n.01",
        definition="any substance that can be eaten",
        naming_token="eaten",
    )
    applied = curation.apply(built, [proposal], policy)
    store.write(applied.matrix, build="t1")

    cell = store.matrix("t1", "base_r").cell("food.n", "eat.v")
    assert cell.source == SOURCE_CURATED
    assert cell.evidence == proposal.evidence
    assert cell.relation == "involves"


def test_a_key_with_a_dot_in_it_is_stored_as_a_value(store, built, clean_db):
    """The hazard recorded in `keys.py`: a base key contains a dot, and mongo reads a dotted field
    NAME as a path — a cells map would have written a nested `sleep` document instead of the cell
    anybody meant. The cells are a LIST, and this is what says so."""
    store.write(built, build="t1")
    stored = clean_db["base_r"].find_one({"build": "t1", "key": "eat.v"})

    assert isinstance(stored["cells"], list)
    assert all(isinstance(cell["column"], str) for cell in stored["cells"])
    assert "eat" not in stored, "a dotted key must never have become a field path"


def test_two_builds_can_sit_in_one_database(store, built):
    """A build LABEL rather than «the current base»: a before/after comparison is the thing most
    worth having, and a writer that replaced the base in place would make it impossible."""
    store.write(built, build="t1")
    store.write(built, build="t2")

    assert set(store.builds()) == {"t1", "t2"}
    assert store.row("t2", "base_r", "eat.v") == store.row("t1", "base_r", "eat.v")


def test_rewriting_a_build_replaces_it_rather_than_doubling_it(store, built, clean_db):
    store.write(built, build="t1")
    store.write(built, build="t1")
    assert clean_db["base_r"].count_documents({"build": "t1"}) == len(KEYS)


def test_a_second_matrix_may_not_disagree_about_the_dimensions(store, built):
    """R and D share ONE key space, and that is the only reason a reader can compare them cell for
    cell. Two orders would not look like an error — every cell would simply be about another word."""
    from tk2.datatier.matrix_store import KeySpaceConflict

    store.write(built, build="t1")
    shuffled = matrix.Matrix(
        name="base_r",
        keys=tuple(reversed(KEYS)),
        rows=tuple(
            matrix.MatrixRow(key=key, index=index, cells=())
            for index, key in enumerate(reversed(KEYS))
        ),
    )
    with pytest.raises(KeySpaceConflict):
        store.write(shuffled, build="t1")


def test_the_registry_records_the_dimension_order_and_its_indices(store, built, clean_db):
    """The index is stored rather than derived from a sort: it is the position a vector's column
    means, and two readers that sorted differently would read every cell at the wrong column."""
    store.write(built, build="t1")
    rows = sorted(clean_db["base_keys"].find({"build": "t1"}), key=lambda row: row["index"])

    assert [row["key"] for row in rows] == list(KEYS)
    assert [row["index"] for row in rows] == list(range(len(KEYS)))
    assert {row["pos"] for row in rows} == {"v", "n", "a"}


def test_a_stray_cell_never_reaches_the_database(store, policy):
    """`assert_square` runs before a matrix leaves the builder, and this is the shape it refuses: a
    cell naming a column that is not a dimension is a statement about an axis that does not exist."""
    stray = matrix.Matrix(
        name="base_r",
        keys=("eat.v",),
        rows=(
            matrix.MatrixRow(
                key="eat.v",
                index=0,
                cells=(Cell(column="runway.n", weight=0.5, relation="involves",
                            via=(Provenance("involves", 0.5),)),),
            ),
        ),
    )
    with pytest.raises(ValueError):
        matrix.assert_square(stray)


# ------------------------------------------------------------------------------------------------
# D beside R, under one build and one registry (T4)
# ------------------------------------------------------------------------------------------------


def _distributional():
    """A tiny D over the same key space — symmetric, unsigned, one relation."""
    from tk2.dictionary.distribution import GLOSS_OVERLAP

    shared = {("eat.v", "food.n"), ("food.n", "eat.v")}
    rows = []
    for index, key in enumerate(KEYS):
        cells = [Cell(column=key, weight=1.0, relation="identity", source=matrix.SOURCE_AXIS,
                      via=(Provenance("identity", 1.0),))]
        for row_key, column in sorted(shared):
            if row_key == key:
                cells.append(Cell(column=column, weight=0.4, relation=GLOSS_OVERLAP,
                                  via=(Provenance(GLOSS_OVERLAP, 0.4),)))
        rows.append(matrix.MatrixRow(key=key, index=index, cells=tuple(cells)))
    return matrix.Matrix(name="base_d", keys=KEYS, rows=tuple(rows))


def test_both_matrices_of_a_build_share_one_key_registry(store, built, clean_db):
    """The property the whole architecture rests on: R and D are two geometries over ONE dimension
    order, so the registry is written once and the second matrix does not add a row to it."""
    assert store.write(built, build="t1") == len(KEYS)
    written = clean_db["base_keys"].count_documents({"build": "t1"})

    assert store.write(_distributional(), build="t1") == len(KEYS)
    assert clean_db["base_keys"].count_documents({"build": "t1"}) == written
    assert store.keys("t1") == KEYS


def test_D_survives_the_trip_whole_and_stays_unsigned(store, built):
    store.write(built, build="t1")
    store.write(_distributional(), build="t1")

    read = store.matrix("t1", "base_d")
    assert read.rows == _distributional().rows
    assert read.cell("eat.v", "food.n").weight == 0.4
    assert read.cell("food.n", "eat.v").weight == 0.4, "overlap is symmetric"
    assert all(cell.weight > 0 for row in read.rows for cell in row.cells)
    # ...and R is untouched beside it: two collections, one build label.
    assert store.matrix("t1", "base_r").cell("hungry.a", "full.a").weight < 0


def test_a_D_that_disagrees_about_the_dimensions_is_refused_too(store, built):
    """The registry is written by whichever matrix lands first, and it binds the other."""
    from tk2.datatier.matrix_store import KeySpaceConflict

    store.write(built, build="t1")
    shuffled = matrix.Matrix(
        name="base_d",
        keys=tuple(reversed(KEYS)),
        rows=tuple(matrix.MatrixRow(key=key, index=index, cells=())
                   for index, key in enumerate(reversed(KEYS))),
    )
    with pytest.raises(KeySpaceConflict):
        store.write(shuffled, build="t1")
