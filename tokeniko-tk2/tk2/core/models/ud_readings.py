"""HOW THE STATION READS A UD LABEL — the exceptions, and only the exceptions.

**A UD LABEL DOES NOT ALWAYS MEAN FOR US WHAT IT NAMES.** Most do: `nsubj` IS a subject, `acl` IS a
clausal modifier of a noun, and reading the tree's shape that way is frame (the Captain,
2026-09-18). These rows are the handful where the station makes a JUDGEMENT on top of the label —
and a judgement is knowledge, by the standing rule.

**THE DEFAULT IS NOT A ROW**, which is `db/0013`'s shape and the reason it works: the table holds
what differs, a miss is an ANSWER rather than an absence, and the ordinary reading costs nothing.

    compiles_to_content   default TRUE   — `vocative` is false: «Guys, take it easy» is an
                                           instruction to a room, and the room is not a participant
    opens_clause          default TRUE   — `xcomp` is false: «you like TO SWIM» is one predication
                                           with a controlled subject, and nobody asserts that you
                                           swim. UD calls it a clause; tkzip does not make it a row
    states_number         default FALSE  — `NOUN` is true: a speaker who says «cats» CHOSE the
                                           plural. UD tags every `PROPN` `Number=Sing` by default
                                           morphology rather than on evidence, so a name states
                                           nothing and the zip must not record that it did
    admits_roles          default NONE   — no constraint. `case` admits the role markers, `det` the
                                           determiner jobs, `compound:prt` only the verb particle
                                           (`db/0034`). A SET: the ranking it once carried in code
                                           was deleted, and a tie nobody settles abstains
    adverbial_gap         default NONE   — no rule, so every zero relative whose gap the tree leaves
                                           unnamed is withheld. `acl:relcl` names which circumstance
                                           its antecedent is — «the DAY I slept» a time — in
                                           `MarkerSelector`'s rule vocabulary (`db/0038`)

**WHY EACH OF THESE IS A ROW AND NOT A SET IN CODE** — E3's frame/knowledge audit, 2026-09-22
(`docs/E3-parser-compiler/202609220930_the-frame-knowledge-audit.md`). Each was a frozenset whose
membership encoded an argument: «a vocative is addressing, not content» is an E2 ruling, «nobody
asserts that you swim» is a semantic judgement about English complementation, and «a proper noun's
number is not evidence» is a claim about how stanza tags. **A one-member set is never a set — it is
a decision with brackets round it.**
"""

from typing import Annotated, Any

from bunnet import Indexed
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from tk2.core.documents import LogicDocument
from tk2.core.mixins import Timestamped


class UdReadingDoc(LogicDocument, Timestamped):
    """logic (r) — one exception to the ordinary reading of one UD label."""

    #: Versioned whole, for `ClosedClassDoc`'s reason: a parse must be able to say which table it
    #: read, and a number that cannot name its rows is not reproducible.
    version: Annotated[int, Indexed()] = Field(ge=1)

    #: Which UD inventory the label comes from — `relation` (the 37) or `pos` (the 17). Both are
    #: published and closed; this column only says which one to look in.
    inventory: str = Field(min_length=1)

    #: The label itself, spelled as UD spells it: `vocative`, `xcomp`, `NOUN`.
    label: str = Field(min_length=1)

    #: What the station reads it as, where that differs from the ordinary reading. One key per
    #: question a caller can ask; a question with no key here is answered by the default.
    reads: dict[str, Any] = Field(default_factory=dict)

    #: Where the reading came from — the ruling or the measurement it rests on.
    source: str = Field(min_length=1)

    note: str = ""

    position: int = Field(ge=0)

    class Settings:
        name = "language_ud_readings"
        indexes = [
            IndexModel([("version", ASCENDING), ("inventory", ASCENDING), ("label", ASCENDING)],
                       unique=True),
        ]
