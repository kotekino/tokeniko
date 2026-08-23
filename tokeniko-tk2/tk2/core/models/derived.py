"""Derived points — the cosine index of the figurative layer, stored beside the zips they came from.

The two-step made law (tkzip req. 16): store the derived point for the cheap cosine find, recompute
on the found few at use. And because the layer that computed them DRIFTS, every stored point carries
the version that made it; the sleep phase re-derives stale points lazily, never a full recompute.

--------------------------------------------------------------------------------------------------
THE EPOCH-LAYER RULING (T2's open question, settled here 2026-08-23 as instructed)
--------------------------------------------------------------------------------------------------

The question: `EpochStamped` carries a bare `epoch: int`, but there is more than one counter in the
body — the derived/figurative layer has one, and every micro-nn instance has its own (micro-nn
req. 8). Should a row also name WHICH counter its number belongs to?

**Ruling: no `epoch_layer` column.** In every case the counter is already identified by something
the row carries as part of its own identity:

  - a derived point is stamped against the layer that computes derived points, and this collection
    holds nothing else — the COLLECTION is the scope;
  - a micro-nn's weights are stamped against that instance's training history — the OWNING INSTANCE
    is the scope, and a weights row that did not name its instance would be unreadable anyway.

A separate column would therefore restate, on every row, something the row already establishes. That
is redundancy that can DISAGREE with itself, and a stamp whose two halves disagree is worse than no
stamp: the reader has no way to tell which half is lying. The same argument already settled `sphere`
on the heart's poles, and it settles this.

What the ruling costs is that `is_stale(current_epoch)` trusts its caller to pass the right counter.
That cost is real but it is bounded and it is at the CALL site, where the scope is visible — as
opposed to a stored column, whose wrongness travels with the row forever. The mitigation is that
each counter has exactly one place to be read from, and for this layer that place should be a param
row under the house convention (`dictionary.layer.epoch` or similar) seeded by a migration.
"""

from typing import Annotated

from bunnet import Indexed

from tk2.core.documents import KbDocument
from tk2.core.mixins import EpochStamped, Provenance, Timestamped


class DerivedPointDoc(KbDocument, Provenance, EpochStamped, Timestamped):
    """kb — a derived point is something he computed about his own thoughts; the body writes it, and re-writes it when it goes stale.

    `Provenance` is not decoration here: «stored BESIDE the zip» is the requirement, and `parents` is
    what makes «beside» a followable link rather than a hope. `derived_by` names the composer and its
    version, so a change to the composition operators can revoke exactly the points it invalidated.

    The point's representation is a dense list today. E2 rules on sparse storage with densify-on-
    demand (its task 5, OQ9); if it lands sparse, that is a migration on this column, not a redesign
    — which is the whole reason a dimension change is a migration and never a cast.
    """

    point: list[float]

    # The find is a cosine over this index, and the index is only meaningful within one epoch —
    # so the epoch is the first thing any query narrows by.
    epoch: Annotated[int, Indexed()]

    class Settings:
        name = "derived_points"
