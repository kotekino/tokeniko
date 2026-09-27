"""HOW STRONGLY A QUESTION EXPECTS ITS ANSWER — the prior the tree does not state (tkzip req 50).

**«It's cold, isn't it?» and «Is it cold?» ask the same thing with two expectations**, and tkzip has
the slot for the difference: `Open.prior`, «a [0,1] expectation of how it will bind» — the one
genuinely new scalar the drill bench found (req 50). Nothing in a dependency tree is that number.
The Captain ruled it **knowledge with a counted default, exactly as `strength` is** (2026-09-27,
`E3.3.11.2.21`): the tag's SHAPE is read off the tree, and how much a shape expects is a row.

**ONE ROW PER SHAPE OF ASKING THAT EXPECTS.** A shape is what the station can RECOGNISE — a tag of
the opposite polarity to its host, today, because that is req 50's own witness. A tag of the same
polarity («So she slept, did she?») is a recognisable shape with no row: it may expect, infer or
doubt, and *a class enters on a witness, not on a principle* (the standing law of 2026-09-18), so
the station withholds it rather than invent a number.

**AND THE VALUE IS NEVER A GATE** — the gates compare the SLOT, stated against unstated, as they do
for `AttitudeStrengthDoc`: re-curating the number is a migration and not a red gate.
"""

from typing import Annotated, Any

from bunnet import Indexed
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from tk2.core.documents import LogicDocument
from tk2.core.mixins import Timestamped


class OpenPriorDoc(LogicDocument, Timestamped):
    """logic (r) — how strongly one recognisable shape of asking expects its answer to be *yes*."""

    #: Versioned whole, for `ClosedClassDoc`'s reason: a parse must be able to say which rule it read.
    version: Annotated[int, Indexed()] = Field(ge=1)

    #: The shape of asking this row settles — `reversed_tag` is the only one with a witness.
    shape: str = Field(min_length=1)

    #: `{"prior": 0.8}`. A dict for `AttitudeStrengthDoc.compiled`'s reason: the day a shape needs a
    #: second fact read with it, the row grows it, and a schema change is a worse way to learn one.
    compiled: dict[str, Any] = Field(default_factory=dict)

    #: Where the number came from — the witness, and the ruling that made it knowledge.
    source: str = Field(min_length=1)

    note: str = ""

    position: int = Field(ge=0)

    class Settings:
        name = "language_open_priors"
        indexes = [
            IndexModel([("version", ASCENDING), ("shape", ASCENDING)], unique=True),
        ]
