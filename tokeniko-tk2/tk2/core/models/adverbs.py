"""THE ADVERB KINDS — which of requirement 23's four scopes an open-class adverb takes.

**WHY THIS IS A SECOND TABLE AND NOT MORE CLOSED-CLASS ROWS** *(the Captain, 2026-09-16)*. «however»
compiles to a JOIN exactly as «because» does, and «probably» to a MODALITY exactly as «may» does, so
on the second standing law they are structure and the closed-class table is where structure lives.
They are not there for one reason, and it is a cost rather than a principle: **the closed-class
forms are a STRUCTURE FILTER on D's vocabulary.** Adding sixty forms would shrink what D is built
from, and the sealed base was built against the set as it stands. The Captain ruled the cheaper
side — the base is untouched and the closed classes stay at 383 rows, v6.

**THE COST HE NAMED, AND HOW IT IS PAID.** «What does this word compile to» now has two tables to
ask, and a second home for one kind of fact is the category error requirement 12 is about. The
mitigation is that **only the ROSTER is second — the ANSWER is the same**: this table's `compiled`
column holds the identical vocabulary `ClosedClassDoc.compiled` holds (`kind` of join · prefix · box,
with `operator`, `roles`, `modality`), so a reader asks one table, misses, asks the other, and the
shape it gets back never changes. One vocabulary, two rosters, one reader. **If the exclusion set
ever stops being load-bearing, these rows merge into the closed classes and nothing above notices.**

**MANNER IS THE DEFAULT AND NEEDS NO ROW.** 79% of WordNet's 3,767 single-word adverbs end in `-ly`
and 73% carry a pertainym — they are derived from adjectives and describe the action. So this table
holds only the EXCEPTIONS, which is why a set that could not be enumerated is enumerable after all:
the epistemic, the evaluative, the discourse connectives, and the non-`-ly` circumstantials.

**AND THE RESOURCE CANNOT ANSWER THIS, WHICH IS WHY IT IS CURATION.** Measured 2026-09-16:
**WordNet files every adverb under ONE lexicographer class, `adv.all`** — so the supersense that
settled the thirteen ambiguous markers says nothing here. **And adverbs have NO HYPERNYMS at all**,
so R is structurally thin for them and the taxonomy walk that would answer «is this a time adverb»
does not exist in the resource. What remains is the pertainym — the adjective an `-ly` adverb is
derived from — and it separates derived from underived, not manner from epistemic: `quickly` and
`probably` both have one.
"""

from typing import Annotated, Any

from bunnet import Indexed
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from tk2.core.documents import LogicDocument
from tk2.core.mixins import Timestamped


class AdverbKindDoc(LogicDocument, Timestamped):
    """logic (r) — one adverb that is NOT a manner adverb, and what it is instead."""

    #: Versioned whole, for `ClosedClassDoc`'s reason: a parse that read these rows must stay able to
    #: say WHICH set it read, and a set edited in place makes every earlier record a description of
    #: something that no longer exists.
    version: Annotated[int, Indexed()] = Field(ge=1)

    #: The surface form, lower case.
    form: str = Field(min_length=1)

    #: WHICH of requirement 23's four scopes. `manner` is deliberately not a value — it is the
    #: DEFAULT and a row asserting it would be a roster of the open class this table exists to avoid.
    #:
    #:   `epistemic`      — «probably», «certainly»: a claim about the claim. A prefix element.
    #:   `evaluative`     — «luckily», «sadly»: the speaker's attitude to the claim. A prefix element.
    #:   `discourse`      — «however», «therefore»: it relates two ROWS, so it is a join.
    #:   `circumstantial` — «yesterday», «abroad»: it fills a box, and `compiled.roles` says which.
    #:   `focus`          — «only», «exactly» (`db/0039`): which thing satisfies the frame, the
    #:                      particle's associate; `compiled.focus` names the meaning.
    kind: str = Field(min_length=1)

    #: What it compiles to, in **`ClosedClassDoc.compiled`'s own vocabulary** — that identity is what
    #: keeps the two rosters from becoming two formats. A reader that missed in one table and hit in
    #: the other must not be able to tell which answered.
    compiled: dict[str, Any] = Field(default_factory=dict)

    #: Where the row came from, so «is this list complete?» is answerable by re-walking the source.
    source: str = Field(min_length=1)

    #: **THE FORM THIS MEANING IS SPOKEN WITH** — `ClosedClassDoc.spoken`, for the second roster
    #: (`db/0035`). The same many-to-one and the same answer: ten adverbs all compile to a necessity,
    #: so the backward reading is a CHOICE, and a choice is curation. At most one row per meaning
    #: carries it.
    #:
    #: **A meaning here is asked for only where the closed classes cannot voice it**, and that is
    #: position, not vocabulary: an auxiliary stands before «not», so «must not» can only put the
    #: negation inside; an adverb stands after it, so «not necessarily» is the one place a negation
    #: outside a modality can be said. Word order, therefore frame — no column says where it sits.
    spoken: bool = False

    #: Why this row is here, or what is odd about it — the forms that are also something else.
    note: str = ""

    #: Declared order within (version, kind), so the rows read back grouped as written.
    position: int = Field(ge=0)

    class Settings:
        name = "language_adverb_kinds"
        indexes = [
            IndexModel([("version", ASCENDING), ("form", ASCENDING), ("kind", ASCENDING)],
                       unique=True),
            IndexModel([("version", ASCENDING), ("kind", ASCENDING)]),
        ]
