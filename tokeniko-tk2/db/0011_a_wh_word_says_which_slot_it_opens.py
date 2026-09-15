"""0011 — closed classes version 5: a wh-word says WHICH slot it opens.

**«THERE IS NO MOOD FIELD»** (E2): a question is *something OPEN*. Version 4 says that much — every
wh-word compiles to `{"kind": "open"}` — and stops exactly where the compiler needs it to go on:
**which** slot. «When do you sleep?» opens the TIME box; «Who sleeps?» opens a participant; and the
station could not tell them apart, so it left the wh-word unplaced and the question unasked.

**WORKING OUT THE ANSWER SPLIT THE WH-WORDS FIVE WAYS, NOT ONE.** That is the finding, and three of
the five do not open a box at all:

    box          when · where · how · whither · whence     -> time, location, manner, …
    participant  who · whom · what · which                 -> the DEPENDENCY decides
    truth        whether                                   -> the row's own truth slot
    antecedent   why                                       -> an OPEN row implying this one
    field        whose                                     -> the possessor, inside the record

**`why` IS THE ONE WORTH THE PARAGRAPH.** There is no cause box to open, because **there is no CAUSE
relation** (req 37): *a cause is `IMPLY` read with the theatre's arrow of time.* So «why do you
sleep?» is not a question about a slot — it asks for an unknown ANTECEDENT: a content row with
everything open, implying the row that was asserted.

    r0  you sleep                 CLAIMED
    r1  (predicate OPEN, no boxes)
    j0  IMPLY (r1, r0)            CLAIMED

*The collapse pays for itself here.* Had `CAUSE` survived as a relation, «why» would have wanted a
cause box, that box would have needed a filler that is a whole proposition, and the format would have
grown a second way of saying what `IMPLY` already says. Instead the shape was already there.

**`who` AND `what` NEED NO ROLE IN THE ROW**, and that is the mapping's two halves again
(parser-compiler req 12): a participant's role arrives by RELATION — `nsubj` → agent, `obj` →
patient, `iobj` → recipient — so the row says «a participant» and the compiler reads the dependency
it already reads for every other nominal. A role written here would be a third place the same fact
lives.

**`whether` OPENS THE TRUTH SLOT**, which is the polar question E2 already ruled: *«Is the cat
hungry?» has every box bound and its truth open.* The word is simply the subordinate spelling of it.

**THE RELATIVE READINGS ARE UNTOUCHED.** `who` as a relative binds an antecedent and opens nothing —
«the cat that sleeps» is one cat described twice, not a question — and those rows keep
`binds: "antecedent"` exactly as version 4 wrote them. Only the INTERROGATIVE and free-relative
readings gain `opens`.

**Nothing else moves**: no form arrives or leaves, no role is re-typed, and the single-word FORMS are
identical — that set is the dictionary's gloss-word exclusion, and a migration that moved it would
move D and the sealed base with it.

**Written by the QM on 2026-09-15, on the Captain's «go with wh-words».**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, ClosedClassDoc
from tk2.migrations import ensure_collections

VERSION = 5

#: The wh-words that open a named BOX — the role is a property of the word.
OPENS_BOX = {
    "when": "time",
    "where": "location",
    "how": "manner",
    "whither": "destination",
    "whence": "source",
}

#: The wh-words that open a PARTICIPANT — the dependency says which one, exactly as it does for
#: every other nominal. `which` is here rather than in OPENS_BOX because «which cat sleeps?» asks
#: about a participant and restricts it; the restriction rides on the box it determines.
OPENS_PARTICIPANT = ("who", "whom", "what", "which", "whoever", "whomever", "whatever", "whichever")

#: The polar question, in its subordinate spelling.
OPENS_TRUTH = ("whether",)

#: No cause box exists to open (req 37) — this asks for an unknown antecedent.
OPENS_ANTECEDENT = ("why",)

#: The possessor is a FIELD of the record (req 26), never a box of the clause.
OPENS_FIELD = ("whose",)


def opens_for(row: dict) -> dict | None:
    """What this form leaves open, or None if the question does not arise for it.

    **INTERROGATIVE AND FREE-RELATIVE READINGS ONLY.** A relative `who` binds an antecedent and asks
    nothing; giving it `opens` would turn «the cat that sleeps» into a question about the cat.
    """
    if row["role"] not in ("interrogative", "free_relative"):
        return None
    form = row["form"]
    if form in OPENS_BOX:
        return {"opens": "box", "role": OPENS_BOX[form]}
    if form in OPENS_PARTICIPANT:
        return {"opens": "participant"}
    if form in OPENS_TRUTH:
        return {"opens": "truth"}
    if form in OPENS_ANTECEDENT:
        return {"opens": "antecedent"}
    if form in OPENS_FIELD:
        return {"opens": "field", "field": "relation"}
    return None


def build_rows(previous: list[dict]) -> list[dict]:
    """Version 5 = version 4 with `opens` on the interrogative readings. Nothing else changes."""
    out = []
    for row in previous:
        if row.get("version") != 4:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = VERSION
        opens = opens_for(row)
        if opens is not None:
            new["compiled"] = {**new["compiled"], **opens}
            if opens["opens"] != "box":
                new["note"] = (row.get("note") or "") + (
                    f" — v5: opens={opens['opens']}. "
                    + {"participant": "the role arrives by RELATION, as it does for every nominal.",
                       "truth": "the polar question — every box bound and the truth open.",
                       "antecedent": "there is no cause box to open (req 37): it asks for an "
                                     "unknown row implying this one.",
                       "field": "the possessor is a field of the record, never a box."}[
                        opens["opens"]])
        out.append(new)
    return out


def _previous_rows():
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 10), None)
    if found is None:
        raise RuntimeError("0010 is gone — it holds the version this one extends")
    return found.load().CLOSED_CLASS_ROWS


CLOSED_CLASS_ROWS = build_rows(_previous_rows())

#: Unchanged by this version — and checked, because it is the dictionary's exclusion set.
CLOSED_CLASS_FORMS = tuple(
    sorted({row["form"] for row in CLOSED_CLASS_ROWS if " " not in row["form"]})
)


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(ClosedClassDoc, CLOSED_CLASS_ROWS)
