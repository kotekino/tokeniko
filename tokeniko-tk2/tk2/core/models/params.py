"""The parameter store — the r-class table the whole body tunes itself from.

Everything that is a rate, a cap, a threshold or an interval ends up here rather than in code, which
is what makes the body an interpreter of the db (body req. 2) instead of a program with settings.
The r-cache reads this collection at boot and reconciles it on the slow tick, so an edit lands live
(datatier req. 3, body req. 4).
"""

from typing import Annotated, Any

from bunnet import Indexed
from pydantic import Field

from tk2.core import constants
from tk2.core.documents import ParamDocument
from tk2.core.mixins import Timestamped, Updated


class ParamDoc(ParamDocument, Timestamped, Updated):
    """param (r) — a parameter the body could rewrite is a parameter the body could drift on.

    The field names are not free: the r-cache indexes this collection by
    `constants.PARAM_KEY_FIELD` / `PARAM_VALUE_FIELD`, and `RCache` refuses at registration if they
    are missing. They are asserted against the constants in the tests, so the seam cannot drift by
    someone renaming one side.

    Keys follow the house convention ruled 2026-08-23: `component.concern.setting` — dotted, most
    general first, so the store sorts into its own natural sections and a prefix query returns one
    component's whole surface (`datatier.rcache.refresh_seconds`).
    """

    key: Annotated[str, Indexed(unique=True)]
    value: Any = None

    # A number with no explanation is a mystery the next reader has to reverse-engineer from the
    # code that consumes it — and these rows are seeded by migrations and read by human probes, so
    # the next reader is a person. Not speculative: it is what makes an r-table auditable at all.
    note: str = Field(default="")

    class Settings:
        name = "params"


# Asserted at import so a rename of either side is caught here, at the seam, rather than as an empty
# parameter store at boot.
assert constants.PARAM_KEY_FIELD in ParamDoc.model_fields
assert constants.PARAM_VALUE_FIELD in ParamDoc.model_fields
