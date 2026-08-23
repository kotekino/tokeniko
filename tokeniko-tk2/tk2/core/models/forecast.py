"""Forecasts — the staked future half of his timeline.

«Forecast is memory's mirror: same zip shape, spacetime in the future, confidence where truth will
later sit. The two together are his timeline — settled behind, staked ahead» (heart req. 17).

Expectation needs no new organ (heart req. 15): the expectation itself is a future-tensed belief,
and what makes it HOPE is the row below — the heart's stake on it. x closing raises joy; x breaking
spikes disillusion, at an amplitude weighted by how load-bearing the belief was (heart req. 9).
"""

from typing import Annotated

from bunnet import Indexed
from pydantic import Field

from tk2.core.documents import KbDocument
from tk2.core.mixins import Provenance, Timestamped

from enum import Enum


class StakeStatus(str, Enum):
    """A stake is open until the world settles it, and then it is never re-opened — the resolution
    is an event in his life, and E4's stake resolution emits the serendipity or the disillusion that
    the heart consumes."""

    STAKED = "staked"
    CLOSED = "closed"
    BROKEN = "broken"


class ForecastDoc(KbDocument, Provenance, Timestamped):
    """kb — a staked expectation is a belief about the future, held by him and retreatable like any other.

    It carries `Provenance` because a forecast is DERIVED and pre-filled at input: `urge(say
    something) → expectation(consequence(say something))`. Naming its parents is what lets a stake
    retreat when the reasoning that raised it falls (data-modeling req. 5).

    **The zip is not here, and its absence is deliberate.** «Same zip shape» is tkzip v2, which E2
    freezes; a placeholder column now would be a guess that every later row inherits. Adding the
    payload once the schema exists is a migration, which is exactly the normal direction of travel
    (data-modeling req. 6). What this table shapes today is the half that is settled: the stake.

    **Depth is not stored either.** Spike amplitude is depth-weighted (heart req. 9), but how
    load-bearing a belief is changes as the KB grows around it — a depth frozen at staking time
    would be stale by the moment it mattered. It is computed at resolution, from the graph.
    """

    # Where truth will later sit. The one number that makes a forecast a forecast rather than a
    # prediction: he does not merely expect, he expects to a degree.
    confidence: float = Field(ge=0.0, le=1.0)

    # The future spacetime. Int seconds like every other stamp in tk2; `expected_place` is optional
    # because most expectations are about a time and not a place.
    expected_at: int
    expected_place: str | None = None

    status: Annotated[StakeStatus, Indexed()] = StakeStatus.STAKED
    resolved_at: int | None = None

    class Settings:
        name = "forecasts"
