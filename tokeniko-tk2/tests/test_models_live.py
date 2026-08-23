"""The register against a real database: it registers, it round-trips, and the seams hold."""

from datetime import datetime, timezone

import pytest

from tk2.core import constants
from tk2.core.models import (
    ALL_MODELS,
    LOGIC_MODELS,
    PARAM_MODELS,
    ChannelRegisterDoc,
    DerivedPointDoc,
    EmotionalLogDoc,
    ForecastDoc,
    HeartAnatomy,
    HeartAnatomyDoc,
    HeartLevelDoc,
    HeartTargetDoc,
    MicroNnInstanceDoc,
    MicroNnWeightsDoc,
    ParamDoc,
    StakeStatus,
    UnknownPole,
)
from tk2.core.write_class import WriteClassViolation
from tk2.datatier import boot_datatier, traps
from tk2.datatier.migration_writer import MigrationWriter
from tests.seed import anatomy_rows

pytestmark = pytest.mark.mongo


@pytest.fixture
def world(test_db):
    """The real register, booted on the test db and emptied for one test."""
    _db, cache = boot_datatier(ALL_MODELS, db_name=test_db.name)
    for model in ALL_MODELS:
        test_db[model.Settings.name].delete_many({})
    cache.load()
    return test_db, cache


@pytest.fixture
def seeded(world):
    """...with the anatomy in place, as migration 0001 will leave it."""
    db, cache = world
    MigrationWriter(db).insert_many(HeartAnatomyDoc, anatomy_rows())
    cache.load()
    return db, cache


def test_the_whole_register_boots(world):
    """Every model registers with the ODM, indexes and timeseries collections included."""
    db, _cache = world
    names = set(db.list_collection_names())
    for model in ALL_MODELS:
        assert model.Settings.name in names


def test_the_whole_r_tier_is_cached(world):
    """Params AND logic: the cache snapshots everything migrations own, not only the tunables."""
    _db, cache = world
    cached = {m.Settings.name for m in cache.models}
    assert cached == {m.Settings.name for m in PARAM_MODELS + LOGIC_MODELS}


# ------------------------------------------------------------------------------------------------
# params
# ------------------------------------------------------------------------------------------------


def test_a_seeded_param_reaches_the_cache(world):
    db, cache = world
    MigrationWriter(db).insert(
        ParamDoc,
        {
            "key": "heart.spike.decay_seconds",
            "value": 90,
            "note": "how fast a startle falls back to baseline",
        },
    )
    cache.load()
    assert cache.param("heart.spike.decay_seconds") == 90


def test_the_house_key_convention_survives_a_round_trip(world):
    db, cache = world
    MigrationWriter(db).insert(ParamDoc, {"key": constants.RCACHE_INTERVAL_PARAM, "value": 30})
    cache.load()
    assert cache.refresh_seconds == 30


def test_params_cannot_be_written_by_the_body(world):
    with pytest.raises(WriteClassViolation):
        traps.insert(ParamDoc(key="k", value=1))
    with pytest.raises(WriteClassViolation):
        ParamDoc.insert_one({"key": "k", "value": 1})


# ------------------------------------------------------------------------------------------------
# the anatomy, live
# ------------------------------------------------------------------------------------------------


def test_the_anatomy_loads_from_rows_through_the_cache(seeded):
    """The whole point of the ruling: the heart's shape is read from the database, not from an
    enum in the binary."""
    _db, cache = seeded
    heart = HeartAnatomy(cache.rows("heart_anatomy"))

    heart.check_coherent()
    assert len(heart.spheres()) == 6
    assert len(heart.spikes()) == 3
    assert heart.opposite_of("joy") == "sadness"


def test_the_anatomy_cannot_be_written_by_the_body(seeded):
    """A new sphere is a migration, never something he does to himself."""
    with pytest.raises(WriteClassViolation):
        HeartAnatomyDoc.insert_one({"pole": "smugness", "targets": ["self"]})
    with pytest.raises(WriteClassViolation):
        traps.insert(HeartAnatomyDoc(pole="smugness", targets=["self"]))


def test_a_new_sphere_arrives_by_migration_and_lands_live(seeded):
    """Body growth through someone else's hands (body req. 5) — and the slow tick means he does not
    have to be restarted to grow a feeling."""
    db, cache = seeded
    writer = MigrationWriter(db)
    writer.insert_many(
        HeartAnatomyDoc,
        [
            {"pole": "awe", "sphere": "awe-contempt", "opposite": "contempt", "targets": ["idea"]},
            {"pole": "contempt", "sphere": "awe-contempt", "opposite": "awe", "targets": ["idea"]},
        ],
    )

    cache.maybe_refresh(now=1e9)
    heart = HeartAnatomy(cache.rows("heart_anatomy"))

    heart.check_coherent()
    assert len(heart.spheres()) == 7
    assert heart.validate_pole("awe") == "awe"


def test_the_write_time_seam_refuses_a_pole_the_anatomy_lacks(seeded):
    _db, cache = seeded
    heart = HeartAnatomy(cache.rows("heart_anatomy"))
    with pytest.raises(UnknownPole):
        heart.validate_pole("smugness")


# ------------------------------------------------------------------------------------------------
# the heart's own tables
# ------------------------------------------------------------------------------------------------


def test_the_heart_writes_its_own_levels(seeded):
    traps.insert(HeartLevelDoc(pole="joy", level=0.4))
    stored = traps.find_one(HeartLevelDoc, HeartLevelDoc.pole == "joy")
    assert stored.level == 0.4
    assert stored.created_at and stored.updated_at


def test_a_spike_is_a_level_row_like_any_other(seeded):
    traps.insert(HeartLevelDoc(pole="startle", level=0.86))
    assert traps.find_one(HeartLevelDoc, HeartLevelDoc.pole == "startle").level == 0.86


def test_one_level_per_pole(seeded):
    from pymongo.errors import DuplicateKeyError

    traps.insert(HeartLevelDoc(pole="calm", level=0.5))
    with pytest.raises(DuplicateKeyError):
        traps.insert(HeartLevelDoc(pole="calm", level=0.9))


def test_love_and_hate_co_fire_at_the_same_person(seeded):
    """Opposition is stated, never arithmetic — independent pole levels are the whole ruling."""
    for pole, level in (("love", 0.9), ("hate", 0.7)):
        traps.insert(
            HeartTargetDoc(target_kind="person", target_ref="uid-a", pole=pole, level=level)
        )
    rows = {r.pole: r.level for r in traps.find(HeartTargetDoc, HeartTargetDoc.target_ref == "uid-a")}
    assert rows == {"love": 0.9, "hate": 0.7}


def test_curiosity_can_target_an_idea(seeded):
    _db, cache = seeded
    heart = HeartAnatomy(cache.rows("heart_anatomy"))
    heart.validate_target("curiosity", "idea")

    traps.insert(
        HeartTargetDoc(target_kind="idea", target_ref="kb:geometry", pole="curiosity", level=0.6)
    )
    assert traps.find_one(HeartTargetDoc, HeartTargetDoc.target_ref == "kb:geometry").level == 0.6


def test_the_emotional_log_appends_and_deletes_the_honest_way(seeded):
    now = datetime.now(timezone.utc)
    for level in (0.2, 0.5, 0.9):
        traps.insert(EmotionalLogDoc(at=now, pole="joy", level=level))
    assert traps.count(EmotionalLogDoc) == 3

    with pytest.raises(WriteClassViolation):
        traps.delete_many(EmotionalLogDoc)

    assert traps.delete_timeseries_rows(EmotionalLogDoc, {}) == 3


# ------------------------------------------------------------------------------------------------
# forecasts, derived points, micro-nn, registers
# ------------------------------------------------------------------------------------------------


def test_a_forecast_is_staked_then_resolved(world):
    forecast = traps.insert(
        ForecastDoc(
            parents=[{"collection": "memory", "id": "68a0000000000000000000aa"}],
            derived_by="forecaster-v1",
            confidence=0.7,
            expected_at=1_800_000_000,
        )
    )
    assert forecast.status is StakeStatus.STAKED
    assert len(traps.find(ForecastDoc, ForecastDoc.status == StakeStatus.STAKED)) == 1

    forecast.status = StakeStatus.BROKEN
    forecast.resolved_at = 1_800_000_100
    traps.save(forecast)

    assert traps.find_one(ForecastDoc).status is StakeStatus.BROKEN


def test_a_derived_point_round_trips_with_its_stamp(world):
    traps.insert(
        DerivedPointDoc(
            parents=[{"collection": "memory", "id": "68a0000000000000000000aa"}],
            derived_by="composer-v1",
            epoch=2,
            point=[0.1, 0.2, 0.3],
        )
    )
    stored = traps.find_one(DerivedPointDoc)
    assert stored.epoch == 2
    assert stored.is_stale(current_epoch=5) is True


def test_an_instance_is_declared_by_migration_and_trained_by_him(world):
    """THE split, end to end: the declaration comes through the migration door, the weights through
    the body's."""
    db, cache = world
    MigrationWriter(db).insert(
        MicroNnInstanceDoc,
        {
            "name": "evaluator-order",
            "input_schema": ["depth", "recency", "cosine"],
            "output_kind": "ranking",
            "reward_source": "intellectual",
        },
    )
    cache.load()
    assert len(cache.rows("micro_nn_instances")) == 1

    traps.insert(MicroNnWeightsDoc(instance="evaluator-order", epoch=1, weights=[0.1, 0.2, 0.3]))

    stored = traps.find_one(MicroNnWeightsDoc)
    assert stored.instance == "evaluator-order"
    assert stored.is_stale(current_epoch=2) is True


def test_training_adds_an_epoch_rather_than_overwriting(world):
    """«Same features, same epoch, same output» is only checkable if the epochs are still there."""
    for epoch, weights in ((1, [0.1]), (2, [0.4])):
        traps.insert(MicroNnWeightsDoc(instance="mouth-colour", epoch=epoch, weights=weights))
    assert traps.count(MicroNnWeightsDoc) == 2


def test_one_weight_vector_per_instance_per_epoch(world):
    from pymongo.errors import DuplicateKeyError

    traps.insert(MicroNnWeightsDoc(instance="mouth-colour", epoch=1, weights=[0.1]))
    with pytest.raises(DuplicateKeyError):
        traps.insert(MicroNnWeightsDoc(instance="mouth-colour", epoch=1, weights=[0.9]))


def test_the_channel_register_holds_one_value_per_trait(world):
    from pymongo.errors import DuplicateKeyError

    traps.insert(
        ChannelRegisterDoc(channel="discord:general", trait="brevity", value=0.3, strength=0.5)
    )
    with pytest.raises(DuplicateKeyError):
        traps.insert(
            ChannelRegisterDoc(channel="discord:general", trait="brevity", value=0.9, strength=0.9)
        )


def test_migrations_can_seed_kb_tables_too(seeded):
    """Migration 0001 creates the WORLD — the newborn's heart needs its levels to exist before the
    first tick reads them."""
    db, _cache = seeded
    MigrationWriter(db).insert_many(
        HeartLevelDoc, [{"pole": "pride", "level": 0.0}, {"pole": "shame", "level": 0.0}]
    )
    assert traps.count(HeartLevelDoc) == 2
