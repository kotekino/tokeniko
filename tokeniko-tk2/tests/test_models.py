"""The collection register: write-classes declared, shapes honest, closed sets where they belong."""

import pytest
from pydantic import ValidationError

from tk2.core import constants
from tk2.core.models import (
    ALL_MODELS,
    KB_MODELS,
    LOGIC_MODELS,
    PARAM_MODELS,
    R_MODELS,
    ChannelRegisterDoc,
    DerivedPointDoc,
    EmotionalLogDoc,
    ForecastDoc,
    HeartAnatomyDoc,
    HeartLevelDoc,
    HeartMoodDoc,
    HeartTargetDoc,
    HeartTemperamentDoc,
    MicroNnInstanceDoc,
    MicroNnWeightsDoc,
    OutputKind,
    ParamDoc,
    StakeStatus,
)
from tk2.core.write_class import WriteClass
from tk2.datatier import traps
from tk2.datatier.migration_writer import shape_of


# ------------------------------------------------------------------------------------------------
# the register
# ------------------------------------------------------------------------------------------------


def test_every_model_declares_a_write_class():
    for model in ALL_MODELS:
        assert isinstance(model.write_class, WriteClass)


def test_the_three_tiers_of_the_register():
    assert all(m.write_class is WriteClass.PARAM for m in PARAM_MODELS)
    assert all(m.write_class is WriteClass.LOGIC for m in LOGIC_MODELS)
    assert all(m.write_class is WriteClass.KB for m in KB_MODELS)
    assert R_MODELS == PARAM_MODELS + LOGIC_MODELS
    assert ALL_MODELS == R_MODELS + KB_MODELS


def test_nothing_in_the_r_tier_is_writable_by_the_body():
    for model in R_MODELS:
        assert model.write_class.writable is False


def test_collection_names_are_unique():
    names = [m.Settings.name for m in ALL_MODELS]
    assert len(names) == len(set(names))


def test_the_named_collections_are_all_present():
    assert {m.Settings.name for m in ALL_MODELS} == {
        "params",
        "heart_anatomy",
        "micro_nn_instances",
        "heart_levels",
        "heart_targets",
        "heart_mood",
        "heart_temperament",
        "emotional_log",
        "forecasts",
        "derived_points",
        "micro_nn_weights",
        "channel_registers",
    }


def test_the_architecture_is_rows_not_code():
    """The Captain's seam: even invariant data is r-rows. Both the heart's anatomy and the micro-nn
    declarations are `logic` — changing either is a migration, never a new binary."""
    assert {m.Settings.name for m in LOGIC_MODELS} == {"heart_anatomy", "micro_nn_instances"}


# ------------------------------------------------------------------------------------------------
# params — the seam the r-cache reads
# ------------------------------------------------------------------------------------------------


def test_params_uses_the_field_names_the_rcache_indexes_by():
    assert constants.PARAM_KEY_FIELD in ParamDoc.model_fields
    assert constants.PARAM_VALUE_FIELD in ParamDoc.model_fields


def test_the_rcache_accepts_the_whole_r_tier():
    """The cache refuses a kb model and a shapeless param model; these are the models it will
    actually be handed, logic tables included."""
    from tk2.datatier.rcache import RCache

    assert RCache(R_MODELS).models == tuple(R_MODELS)


def test_the_rcache_only_demands_key_value_of_param_tables():
    """A logic table is a table, not a key/value store — it must not have to pretend otherwise."""
    from tk2.datatier.rcache import RCache

    assert RCache(LOGIC_MODELS).models == tuple(LOGIC_MODELS)


# ------------------------------------------------------------------------------------------------
# the heart's tables
# ------------------------------------------------------------------------------------------------


def test_the_anatomy_is_a_logic_table():
    assert HeartAnatomyDoc.write_class is WriteClass.LOGIC
    assert HeartAnatomyDoc.write_class.writable is False


def test_no_enum_survives_in_the_heart_models():
    """The anatomy moved to rows: a `pole` column typed as an enum would have put the legal set
    back into the binary, which is the thing the ruling removed."""
    for model in (HeartLevelDoc, HeartMoodDoc, HeartTemperamentDoc, HeartTargetDoc):
        assert model.model_fields["pole"].annotation is str


def test_the_sphere_is_not_stored_on_a_level():
    """Derived from the anatomy, never duplicated onto the row — redundancy that can disagree."""
    assert "sphere" not in HeartLevelDoc.model_fields


def test_levels_are_bounded():
    shape = shape_of(HeartLevelDoc)
    shape.model_validate({"pole": "joy", "level": 0.5})
    for bad in (-0.1, 1.1):
        with pytest.raises(ValidationError):
            shape.model_validate({"pole": "joy", "level": bad})


def test_the_state_tables_carry_both_stamps():
    """A level row is created once and rewritten forever: `created_at` alone cannot answer «when did
    he last feel this», and `updated_at` alone loses the row's age."""
    for model in (HeartLevelDoc, HeartMoodDoc, HeartTemperamentDoc, HeartTargetDoc):
        assert "created_at" in model.model_fields
        assert "updated_at" in model.model_fields


def test_the_emotional_log_is_a_timeseries():
    assert traps.is_timeseries(EmotionalLogDoc) is True
    assert EmotionalLogDoc.Settings.timeseries.time_field == "at"


def test_the_log_has_one_clock():
    assert "created_at" not in EmotionalLogDoc.model_fields


# ------------------------------------------------------------------------------------------------
# forecasts and derived points
# ------------------------------------------------------------------------------------------------


def test_forecasts_carry_provenance_and_a_confidence():
    assert "parents" in ForecastDoc.model_fields
    assert "derived_by" in ForecastDoc.model_fields
    assert "confidence" in ForecastDoc.model_fields


def test_a_forecast_starts_staked():
    row = shape_of(ForecastDoc).model_validate(
        {
            "parents": [{"collection": "memory", "id": "68a0000000000000000000aa"}],
            "derived_by": "forecaster-v1",
            "confidence": 0.6,
            "expected_at": 1_800_000_000,
        }
    )
    assert row.status is StakeStatus.STAKED
    assert row.resolved_at is None


def test_a_forecast_has_no_zip_and_no_depth():
    """Both absences are rulings: the zip shape is E2's to freeze, and depth changes as the KB grows
    around a belief, so it is computed at resolution rather than frozen at staking."""
    assert "zip" not in ForecastDoc.model_fields
    assert "depth" not in ForecastDoc.model_fields


def test_derived_points_are_stamped_and_parented():
    assert "epoch" in DerivedPointDoc.model_fields
    assert "parents" in DerivedPointDoc.model_fields


def test_nothing_epoch_stamped_names_its_layer():
    """THE T2 ruling, settled in T4: the collection (or the owning instance) already scopes the
    counter, so a column would restate it on every row — redundancy that can disagree with itself."""
    for model in (DerivedPointDoc, MicroNnWeightsDoc):
        assert "epoch_layer" not in model.model_fields


def test_a_migration_shape_carries_fields_but_not_behaviour():
    """A limit of `shape_of` worth pinning: the derived twin is built from `model_fields`, so it
    validates a row's SHAPE and has none of the model's methods."""
    assert "epoch" in shape_of(DerivedPointDoc).model_fields
    assert not hasattr(shape_of(DerivedPointDoc), "is_stale")


# ------------------------------------------------------------------------------------------------
# the micro-nn split
# ------------------------------------------------------------------------------------------------


def test_the_declaration_is_logic_and_the_weights_are_kb():
    """THE ruling: the two halves have opposite write-classes, so they are two collections."""
    assert MicroNnInstanceDoc.write_class is WriteClass.LOGIC
    assert MicroNnWeightsDoc.write_class is WriteClass.KB


def test_the_body_cannot_rewrite_its_own_declarations():
    from tk2.core.write_class import WriteClassViolation

    with pytest.raises(WriteClassViolation):
        MicroNnInstanceDoc.insert_one({"name": "x"})


def test_neither_micro_nn_table_carries_provenance():
    """THE FENCE, structurally: no provenance ⇒ it can never mint or admit a belief (req. 7). Not a
    comment — the absence of two fields."""
    for model in (MicroNnInstanceDoc, MicroNnWeightsDoc):
        assert "parents" not in model.model_fields
        assert "derived_by" not in model.model_fields


def test_the_output_kind_is_the_frameworks_one_shape():
    """Features in → a ranking or a scalar in [0,1] out; nothing else (req. 2)."""
    assert {k.value for k in OutputKind} == {"ranking", "scalar"}


def test_a_declaration_needs_a_schema_a_kind_and_a_reward():
    shape = shape_of(MicroNnInstanceDoc)
    shape.model_validate(
        {
            "name": "evaluator-order",
            "input_schema": ["depth", "recency"],
            "output_kind": "ranking",
            "reward_source": "intellectual",
        }
    )
    for bad in (
        {"name": "x", "input_schema": [], "output_kind": "ranking", "reward_source": "heart"},
        {"name": "x", "input_schema": ["a"], "output_kind": "vibes", "reward_source": "heart"},
        {"name": "x", "input_schema": ["a"], "output_kind": "scalar", "reward_source": ""},
    ):
        with pytest.raises(ValidationError):
            shape.model_validate(bad)


def test_weights_name_the_instance_that_owns_them():
    """The epoch's scope: this counter belongs to the owning instance and to no other, and
    `instance` is what says so."""
    assert "instance" in MicroNnWeightsDoc.model_fields
    assert "epoch" in MicroNnWeightsDoc.model_fields


# ------------------------------------------------------------------------------------------------
# the channel register
# ------------------------------------------------------------------------------------------------


def test_the_channel_register_is_learnable():
    """A row that could only be present or absent could never be reinforced or worn down by the
    traffic that teaches it."""
    assert "strength" in ChannelRegisterDoc.model_fields


def test_the_state_tables_claim_no_parents_they_do_not_have():
    for model in (HeartLevelDoc, HeartMoodDoc, HeartTemperamentDoc, ChannelRegisterDoc):
        assert "parents" not in model.model_fields
