"""0010 — closed classes version 4: «if» and «because» stop being the same row.

**THE GAP, found while building the many-rows compiler on 2026-09-15.** Version 3 gives both of them
exactly `{"kind": "join", "operator": "imply"}` — and E2's central ruling is that the operator is
where they AGREE. What separates them is the **truth slot**:

    «if it rains, I stay home»          join CLAIMED, both halves EMPTY
    «I stayed home because it rained»   join CLAIMED, both halves CLAIMED
    «it rained and I stayed home»       AND,          both halves CLAIMED

*«That last line is what separates «because» from «if» (req 38): same IMPLY, rows claimed or not»* —
`_Claimable`'s own docstring, and the Captain's own argument at E2: **«only because» is the
biconditional, «because» is not «and»**, and the difference is carried by assertion rather than by a
relation. The compiler cannot infer it: nothing in the dependency tree distinguishes the two
sentences except the word itself, so it is knowledge about the WORD and belongs in the row.

**WHAT THIS ADDS.** One field, `asserts`, on every subordinator and coordinator:

    "both"   — both halves are claimed. «because», «although», «since», «after», and every
               coordinator: «it rained AND I stayed home» asserts both.
    "neither"— the halves are stated and not claimed. «if», «unless», «whether», «in case» — the
               hypotheticals, which is exactly the shape the HEART reads as supposition (heart 16).
    "matrix" — the main clause is claimed and the subordinate one is not: «he says THAT you swim»
               claims the saying, not the swimming. This is the POV case and the reason a reporting
               `that` cannot be a plain join.

**«WHEN» IS GENUINELY AMBIGUOUS AND SAYS SO.** «When it rains I stay home» asserts no rain — it is a
generic conditional. «When I arrived she left» asserts the arrival. Same word, same relation, and
only the tense and the theatre tell them apart. It carries `asserts: "ambiguous"` with both readings
named, for the same reason `'d` does: a row that picked one would be a lie the compiler could not
detect, and the station abstaining is the honest output.

**NOTHING ELSE MOVES.** No form arrives, no form leaves, no role is re-typed, and the single-word
FORMS are identical — which matters because that set is the dictionary's gloss-word exclusion, and a
migration that moved it would move D and the sealed base with it.

**Written by the QM on 2026-09-15 while building the many-rows compiler, which could not be written
correctly without it.**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, ClosedClassDoc
from tk2.migrations import ensure_collections

VERSION = 4

BOTH = "both"           # «because it rained» — the speaker claims the rain
NEITHER = "neither"     # «if it rains» — stated, not claimed; the supposition shape
MATRIX = "matrix"       # «he says that you swim» — the saying is claimed, the swimming is not
AMBIGUOUS = "ambiguous"  # «when» — the theatre decides, and the station abstains

#: The hypotheticals. A clause under one of these is STATED AND NOT CLAIMED, which is the reading
#: the heart fires on as imagination (heart 16) and the evaluator must not enter into the KB.
ASSERTS_NEITHER = (
    "if", "unless", "whether", "in case", "supposing", "provided", "providing", "assuming",
    "lest", "as if", "as though", "even if", "on condition that", "in the event that",
)

#: The reporting complementizer. Not a hypothesis and not a plain conjunction: it opens a POINT OF
#: VIEW, and E2 made the attitude a prefix element with its own holder rather than a join.
ASSERTS_MATRIX = ("that", "whether or not", "how", "why", "where", "what", "who", "when that")

#: Same word, two readings, and only the theatre separates them.
ASSERTS_EITHER = ("when", "whenever", "once", "as soon as", "the moment")


def asserts_for(row: dict) -> str | None:
    """What a joining word claims about its halves, or None where the question does not arise."""
    if row["role"] not in ("subordinator", "coordinator"):
        return None
    form = row["form"]
    if form in ASSERTS_NEITHER:
        return NEITHER
    if form in ASSERTS_MATRIX:
        return MATRIX
    if form in ASSERTS_EITHER:
        return AMBIGUOUS
    # Every coordinator, and every factual subordinator: «because», «although», «since», «after».
    return BOTH


def build_rows(previous: list[dict]) -> list[dict]:
    """Version 4 = version 3 with `asserts` added to the joining words. Nothing else changes."""
    out = []
    for row in previous:
        if row.get("version") != 3:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = VERSION
        asserts = asserts_for(row)
        if asserts is not None:
            compiled = dict(new["compiled"])
            compiled["asserts"] = asserts
            new["compiled"] = compiled
            if asserts != BOTH:
                new["note"] = (row.get("note") or "") + (
                    f" — v4: asserts={asserts}. "
                    + {NEITHER: "the halves are STATED, never claimed — the supposition shape.",
                       MATRIX: "the main clause is claimed and the subordinate one is not: it opens "
                               "a POV, not a join.",
                       AMBIGUOUS: "both readings are real and only the theatre separates them; the "
                                  "station abstains rather than picking."}[asserts])
        out.append(new)
    return out


def _previous_rows():
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 9), None)
    if found is None:
        raise RuntimeError("0009 is gone — it holds the version this one extends")
    return found.load().CLOSED_CLASS_ROWS


CLOSED_CLASS_ROWS = build_rows(_previous_rows())

#: Unchanged by this version — and checked, because it is the dictionary's exclusion set.
CLOSED_CLASS_FORMS = tuple(
    sorted({row["form"] for row in CLOSED_CLASS_ROWS if " " not in row["form"]})
)


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(ClosedClassDoc, CLOSED_CLASS_ROWS)
