"""The field conventions, defined ONCE.

These are plain pydantic models, not bunnet Documents, and that is deliberate twice over: pydantic is
the single source of shape (data-modeling req. 6), and a shape that needs a live database to be
instantiated is a shape nobody can test. A collection model mixes these in beside its Document base.

Mixins are OPT-IN. A row carries `Provenance` because it is derived, not because every row should
look the same — the micro-nn's weights are the standing example of a row that must NOT carry it
(micro-nn req. 7: no provenance ⇒ never a belief; the instinct fence is structural, not a promise).
"""

import time
from typing import Annotated

from bunnet import PydanticObjectId
from pydantic import BaseModel, Field


class Parent(BaseModel):
    """One named ancestor: which collection, which row.

    A bare id would be ambiguous the moment two collections hold one — and the retreat cascade has
    to be able to FOLLOW this reference, not merely record that something existed.
    """

    collection: str = Field(min_length=1)
    id: PydanticObjectId


class Provenance(BaseModel):
    """Every derived thing names its parents (data-modeling req. 5).

    This is not bookkeeping. It is the mechanism of retreat: when a belief falls, what was built on
    it has to fall with it — a summary retreats with its parents (brain req. 4). A derived row that
    cannot name where it came from is a row that can never be revised, only deleted, and deleting is
    not something this project does to a biography.

    Both fields are REQUIRED and `parents` is non-empty on purpose: mixing this in is a claim that
    the row is derived, and a derived row with no parents is the claim contradicting itself.
    """

    parents: Annotated[list[Parent], Field(min_length=1)]

    # tk1's proven `method` field, carried and renamed for what it is. The value names the producer
    # AND its version ("differentia-v1"), because a rebuild replaces one producer's output wholesale:
    # this is the key that makes a whole derived tier revocable in one sweep.
    derived_by: str = Field(min_length=1)


class EpochStamped(BaseModel):
    """The layer version that computed this value (tkzip req. 16, micro-nn reqs. 4 & 8).

    Derived points are stored beside the zip as a cheap cosine index, and the layer that produced
    them DRIFTS — the figurative layer moves with experience, a micro-nn's weights move with
    training. So a stored point is only meaningful against the version that made it.

    A row behind the current epoch is STALE, not WRONG: the sleep phase re-derives stale points
    lazily, never a full recompute. Nothing here deletes anything.

    NOT a timestamp. `Timestamped.created_at` below is the clock; this is the version counter. The
    two are kept apart by name because tk1 calls its unix-seconds column an epoch too, and one
    confused comparison between a version and a wall clock would be unreadable.
    """

    epoch: int = Field(ge=0)

    def is_stale(self, current_epoch: int) -> bool:
        """Whether this value predates the layer as it stands now.

        The caller supplies the current epoch because there is more than one counter in the body —
        the dictionary layer has one, every micro-nn instance has its own — and this mixin has no
        business guessing which one it is being asked about.
        """
        return self.epoch < current_epoch


def now_seconds() -> int:
    """Unix seconds, UTC. The one place the clock is read, so there is one answer to «what time is
    stored»."""
    return int(time.time())


class Updated(BaseModel):
    """When the row last CHANGED. Same representation as `created_at`, different question.

    Added in T4, when the heart's tables made the gap obvious: a level row is created once and
    rewritten forever, so `created_at` alone answers «when did this pole start existing», which
    nobody asks, and cannot answer «when did he last feel this», which is the whole point.

    Carried BESIDE `Timestamped`, not instead of it. Both stamps are meaningful on a long-lived
    state row, and collapsing them would lose the row's age — which the temperament tier, whose
    whole subject is drift over a lifetime, is going to want.

    The writer sets it; nothing here can enforce that, because a pydantic default only fires at
    construction. The datatier's writers are the place to make it automatic if we ever want it to
    be, and that is a decision for whoever needs it first.
    """

    updated_at: int = Field(default_factory=now_seconds)


class Timestamped(BaseModel):
    """When the row was written. INT SECONDS since the unix epoch — never a datetime.

    tk1 stores `theorems.createdAt` as int seconds while other collections store datetimes, and
    pymongo hands those back naive (no tzinfo), so a comparison between two tk1 rows can quietly
    mean nothing. tk2 picks one representation and keeps it: an integer, UTC by construction,
    comparable and sortable with no timezone to lose.

    Same-second writes are common and int seconds cannot order them — sort by `-_id` as the
    tiebreaker, exactly as the tk1 probes learned to.
    """

    created_at: int = Field(default_factory=now_seconds)
