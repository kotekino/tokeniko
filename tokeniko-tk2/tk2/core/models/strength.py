"""HOW STRONGLY AN ATTITUDE WANTS — the gradation the tree does not state (parser-compiler req 23).

**«Close the door!» and «would you mind closing the door?» are the same want at two strengths**, and
tkzip has the slot for it: `Pov.strength` / `AttitudeRow.strength`, «the strength of the wanting, not
a mood scalar» (tkzip req 51). Nothing in a dependency tree is that number. The drill hand-compiles
0.9 for a bare imperative (`aw-21`) and 0.6 for «I WOULD LIKE to know…» (`t-md-4`), and the station
wrote neither — its own comment deferred the question to the Captain, who ruled it **knowledge**
(2026-09-19): *«the heart can influence the base value, staying on the knowledge, but let's see when
we do the heart»*.

**ONE ROW PER SHAPE OF WANTING.** A shape is what the station can RECOGNISE — today only the bare
imperative, because that is the only one the drill witnesses and the only one the compile path
reaches. `please`, «kindly» and «would you mind» soften a want and have no row, because *a class
enters on a witness, not on a principle alone* (the standing law of 2026-09-18); «would like» has a
witness and no path, and its row arrives with the desiderative verb (req 55).

**AND THE VALUE IS NEVER A GATE.** The drill gate compares the SLOT — stated against unstated — and
never the magnitude, so re-curating 0.9 is a migration and not a red gate.
"""

from typing import Annotated, Any

from bunnet import Indexed
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from tk2.core.documents import LogicDocument
from tk2.core.mixins import Timestamped


class AttitudeStrengthDoc(LogicDocument, Timestamped):
    """logic (r) — how strongly one recognisable shape of wanting wants."""

    #: Versioned whole, for `ClosedClassDoc`'s reason: a parse must be able to say which rule it read.
    version: Annotated[int, Indexed()] = Field(ge=1)

    #: The shape of wanting this row settles — `imperative` is the only one the station reaches.
    shape: str = Field(min_length=1)

    #: `{"strength": 0.9}`. A dict rather than a float column because the day a softener has a
    #: witness this row grows the rule that reads it, exactly as `ClosedClassDoc.compiled` does —
    #: and a schema change is a worse way to learn a new fact than a migration is.
    compiled: dict[str, Any] = Field(default_factory=dict)

    #: Where the number came from — the hand-compiled case, and the ruling that made it knowledge.
    source: str = Field(min_length=1)

    note: str = ""

    position: int = Field(ge=0)

    class Settings:
        name = "language_attitude_strengths"
        indexes = [
            IndexModel([("version", ASCENDING), ("shape", ASCENDING)], unique=True),
        ]
