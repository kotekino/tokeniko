"""THE SUBJECT'S ROLE — what an `nsubj` IS, given what is predicated of it (parser-compiler req 22).

**`nsubj` IS A POSITION, NOT A ROLE.** «The cat CHASED the dog» has an agent, «I LOVE the dog» an
experiencer, «God EXISTS» a patient — the same relation three times. UD names the position and leaves
the role to the predicate, so the station must ask the predicate.

**WHY ROWS.** Which predicates make an experiencer is a revisable fact about English and about the
resource that classifies it — knowledge, by the standing rule. The station holds only the READER
(`tk2.language.subjects`, which runs `MarkerSelector`'s rule vocabulary); these rows hold the rule.

**ONE ROW PER KIND OF PREDICATE**, because the evidence differs by kind:

  `verb`     — the verb's own supersense: `verb.emotion`/`cognition`/`perception` → experiencer,
               `verb.stative` → patient, otherwise agent — plus EXCEPTION rules by lemma where the
               resource files a word against its meaning («disagree» is `verb.communication` and a
               held position).
  `copular`  — the complement: a noun is a patient («Sue is a teacher»); an adjective is read through
               its related noun, because WordNet files almost every adjective under one class
               (`adj.all`) — *hungry* → *hunger* is `noun.state`, an experiencer; *green* →
               *greenness* is `noun.attribute`, a patient.

**MEASURED BEFORE IT WAS RULED** (2026-09-18, on every subject the drill holds): the copular half
separated perfectly; the verb half did not by any published instrument, and three of the drill's own
rows turned out to be errors — record `docs/E3-parser-compiler/202609181400_the-subject-role.md`.
"""

from typing import Annotated, Any

from bunnet import Indexed
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from tk2.core.documents import LogicDocument
from tk2.core.mixins import Timestamped


class SubjectRoleDoc(LogicDocument, Timestamped):
    """logic (r) — the rule that settles a subject's role, for one kind of predicate."""

    #: Versioned whole, for `ClosedClassDoc`'s reason: a parse must be able to say which rule it read.
    version: Annotated[int, Indexed()] = Field(ge=1)

    #: `verb` or `copular` — which kind of predicate this rule reads.
    predicate: str = Field(min_length=1)

    #: `{"selector": [...]}` in `ClosedClassDoc.compiled`'s own selector vocabulary — an ORDERED list,
    #: first match wins, ending in a default. The same vocabulary the ambiguous markers use, so one
    #: reader runs both and a rule reads the same wherever it is written.
    compiled: dict[str, Any] = Field(default_factory=dict)

    #: Where the rule came from — the measurement and the ruling it rests on.
    source: str = Field(min_length=1)

    note: str = ""

    position: int = Field(ge=0)

    class Settings:
        name = "language_subject_roles"
        indexes = [
            IndexModel([("version", ASCENDING), ("predicate", ASCENDING)], unique=True),
        ]
