"""The field conventions: provenance that cannot be empty, an epoch that is not a clock, a clock
that is not a datetime."""

import time

import pytest
from bunnet import PydanticObjectId
from pydantic import BaseModel, ValidationError

from tk2.core import EpochStamped, Parent, Provenance, Timestamped, now_seconds


def _an_id() -> PydanticObjectId:
    return PydanticObjectId()


# ------------------------------------------------------------------------------------------------
# provenance
# ------------------------------------------------------------------------------------------------


def test_a_parent_names_its_collection_and_its_row():
    p = Parent(collection="memory", id=_an_id())
    assert p.collection == "memory"


def test_a_parent_without_a_collection_is_not_a_reference():
    """A bare id cannot be followed, and the retreat cascade's whole job is following."""
    with pytest.raises(ValidationError):
        Parent(collection="", id=_an_id())


def test_provenance_carries_parents_and_the_producer():
    prov = Provenance(
        parents=[Parent(collection="memory", id=_an_id())],
        derived_by="summarizer-v1",
    )
    assert len(prov.parents) == 1
    assert prov.derived_by == "summarizer-v1"


def test_a_derived_row_with_no_parents_is_refused():
    """Mixing Provenance in is a claim that the row is derived; an empty parent list is that claim
    contradicting itself — and the row could never be retreated, only deleted."""
    with pytest.raises(ValidationError):
        Provenance(parents=[], derived_by="summarizer-v1")


def test_the_producer_must_be_named():
    """tk1's lesson: a rebuild replaces one producer's output wholesale, so the producer's name and
    version is the key that makes a derived tier revocable in one sweep."""
    with pytest.raises(ValidationError):
        Provenance(parents=[Parent(collection="memory", id=_an_id())], derived_by="")


def test_provenance_takes_many_parents():
    """A summary compresses many zips and retreats with all of them."""
    prov = Provenance(
        parents=[Parent(collection="memory", id=_an_id()) for _ in range(4)],
        derived_by="summarizer-v1",
    )
    assert len(prov.parents) == 4


# ------------------------------------------------------------------------------------------------
# the epoch stamp
# ------------------------------------------------------------------------------------------------


def test_a_stamp_behind_the_layer_is_stale():
    assert EpochStamped(epoch=3).is_stale(current_epoch=4) is True


def test_a_current_stamp_is_not_stale():
    assert EpochStamped(epoch=4).is_stale(current_epoch=4) is False


def test_a_stamp_ahead_of_the_layer_is_not_stale():
    """Not an error either. The counters are per-layer and the caller says which one it is asking
    about; a stamp that reads ahead means the caller passed the wrong layer's number, and this
    mixin is in no position to know that."""
    assert EpochStamped(epoch=9).is_stale(current_epoch=4) is False


def test_the_epoch_is_required_and_non_negative():
    with pytest.raises(ValidationError):
        EpochStamped()
    with pytest.raises(ValidationError):
        EpochStamped(epoch=-1)


def test_staleness_never_deletes_anything():
    """Stale is not wrong: the sleep phase re-derives lazily, never a full recompute. The mixin
    reports, it does not act — there is no discard path here to reach for."""
    assert not hasattr(EpochStamped(epoch=1), "discard")


# ------------------------------------------------------------------------------------------------
# the clock
# ------------------------------------------------------------------------------------------------


def test_created_at_defaults_to_now_in_seconds():
    before = int(time.time())
    stamped = Timestamped()
    assert before <= stamped.created_at <= int(time.time())


def test_created_at_is_an_int_never_a_datetime():
    """The tk1 trap: `theorems.createdAt` is int seconds while other collections hold datetimes,
    and pymongo returns those naive — so two tk1 rows can be compared and mean nothing. One
    representation, no timezone to lose."""
    assert isinstance(Timestamped().created_at, int)


def test_the_clock_is_read_in_one_place():
    assert isinstance(now_seconds(), int)
    assert abs(now_seconds() - int(time.time())) <= 1


# ------------------------------------------------------------------------------------------------
# the mixins compose
# ------------------------------------------------------------------------------------------------


def test_a_model_can_wear_several_conventions_at_once():
    """The point of defining them once: a derived point is provenanced AND epoch-stamped AND
    timestamped, and picks all three up without restating a field."""

    class DerivedPointish(Provenance, EpochStamped, Timestamped, BaseModel):
        value: float

    row = DerivedPointish(
        parents=[Parent(collection="memory", id=_an_id())],
        derived_by="composer-v1",
        epoch=2,
        value=0.5,
    )
    assert row.is_stale(current_epoch=3) is True
    assert isinstance(row.created_at, int)
    assert row.derived_by == "composer-v1"


def test_the_conventions_are_opt_in():
    """A micro-nn's weights must NOT carry provenance — no provenance ⇒ never a belief (micro-nn
    req. 7). The fence is structural: nothing forces these fields onto a model that should not
    have them."""

    class WeightsIsh(EpochStamped, BaseModel):
        weights: list[float]

    row = WeightsIsh(epoch=7, weights=[0.1, 0.2])
    assert row.epoch == 7
    assert "parents" not in WeightsIsh.model_fields
    assert "derived_by" not in WeightsIsh.model_fields
