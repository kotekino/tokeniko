"""THE FORMS A WORD TAKES — where English's spelling rule is wrong (parser-compiler req 9).

**THE DECOMPILER MUST INFLECT, AND IT WAS MEASURED BEFORE IT WAS BUILT.** A zip holds lemmas, and a
sentence of lemmas is not English: «A calculator never thinks» decompiled as «Think.» is read back by
our own `Mood=Imp` rule as a COMMAND — 26 of the round trip's 32 failures, all one artefact. Tense
and person are not decoration; they carry mood and voice.

**THE RULE IS FRAME, THE EXCEPTIONS ARE ROWS.** Adding `-s`, `-es` after a sibilant and `-ies` after a
consonant-plus-`y` is orthography, and orthography is frame for the same reason punctuation is: the
compiler reads it as structure and never as vocabulary. Which words that rule gets WRONG is a
revisable fact about English, so it lives here.

**MEASURED OVER EVERY VERB WORDNET HOLDS** (20,364 lemmas, 2026-09-19): the rule is right for all but
43, and 22 of those 43 are defects in the instrument that found them rather than facts about English
— `ghostwrite → ghost-writes`, `overshoot → over shoots`, `jell → gels`, `okay → o.k.'s`. Curated
down to 21 rows. *The instrument (`lemminflect`) generated the candidates offline and does not ship:
it is used the way WordNet is used to build the base, and its errors are caught by curation, which is
what curation is for.*

**ONE ROW PER (lemma, tag)**, the tag being the Penn tag the form answers to — `VBZ` today, because
the decompiler renders the present. `VBD` and `VBN` join it when the theatre is read and a sentence
can be spoken in the past; each is its own generation and its own curation.
"""

from typing import Annotated

from bunnet import Indexed
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from tk2.core.documents import LogicDocument
from tk2.core.mixins import Timestamped


class InflectionDoc(LogicDocument, Timestamped):
    """logic (r) — one word whose inflected form the spelling rule cannot produce."""

    #: Versioned whole, for `ClosedClassDoc`'s reason: a sentence must be able to say which roster
    #: it was spoken from.
    version: Annotated[int, Indexed()] = Field(ge=1)

    #: The lemma as a zip holds it, without the POS suffix — `go`, not `go.v`.
    lemma: str = Field(min_length=1)

    #: The Penn tag this form answers to. `VBZ` is the third person singular present.
    tag: str = Field(min_length=1)

    #: What the word actually is in that form — `goes`, `is`, `quizzes`.
    form: str = Field(min_length=1)

    #: What the spelling rule would have produced, kept so a reader can see WHY the row exists and
    #: so a later change to the rule can be checked against every exception it claims to need.
    instead_of: str = Field(min_length=1)

    source: str = Field(min_length=1)

    note: str = ""

    position: int = Field(ge=0)

    class Settings:
        name = "language_inflections"
        indexes = [
            IndexModel(
                [("version", ASCENDING), ("lemma", ASCENDING), ("tag", ASCENDING)], unique=True
            ),
        ]
