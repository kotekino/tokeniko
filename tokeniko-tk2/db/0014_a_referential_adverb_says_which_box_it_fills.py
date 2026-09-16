"""0014 — closed classes version 7: a referential adverb says WHICH BOX it fills, and «however» gains
its discourse reading.

**BOTH REPAIRS WERE FOUND BY THE ADVERB WORK (`db/0013`), AND NEITHER BELONGS IN THAT TABLE.** The
adverb-kinds table holds forms the closed classes do NOT hold — its own check refuses an overlap,
because two rosters answering for one form is the cost of a second table turning into a defect. So a
closed-class form that is missing a job gets that job WHERE IT ALREADY LIVES.

**AND THAT IS FREE, WHICH IS THE POINT.** `CLOSED_CLASS_FORMS` — the dictionary's gloss-word
exclusion set, which filters D's vocabulary and therefore the sealed base — is a set of **FORMS**.
Editing a row's `compiled` column does not move it, and neither does adding a SECOND ROW for a form
already in it. **268 before, 268 after.** That is why the Captain's ruling against putting sixty NEW
adverbs here does not apply to these two: no form arrives.

**ONE — `here`, `now`, `then`, `there` FILL A BOX AND NEVER SAID WHICH.** Their rows read
`{"kind": "entity", "resolve": "context"}`, which is right about the HEAD — they are indexical, so
the filler is resolved from context and never earns a dimension (the second standing law) — and
silent about the ROLE. «They come HERE» left `here` unplaced in a sentence otherwise understood,
because the compiler had no role to put an entity in and `advmod` is not a nominal relation.

    here · there   -> location        now · then   -> time

*The `resolve: context` half is untouched.* These rows now say both things: WHICH box, and that its
head is OPEN until the caller's context says otherwise (parser-compiler req 7 — context is an
argument, never state).

**TWO — `however` HAS A DISCOURSE READING AND HELD ONLY ITS FREE-RELATIVE ONE.** The single row is
`pronoun / free_relative / open`, which is «however you do it». «HOWEVER, he left» is a different
job: a connective relating two rows, truth-functionally AND with the concession parked — exactly
what `db/0008` ruled for the concessive prepositions and `db/0013` for the other connectives. **One
form, several jobs, several rows** is what this table has done since v1 for 45 forms; `however` is
the 46th, and UD names the difference outright with its own `discourse` relation.

**Written by the QM on 2026-09-16, completing the adverb piece.**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, ClosedClassDoc
from tk2.migrations import ensure_collections

VERSION = 7

#: form -> the box a referential adverb fills. The head stays OPEN and context resolves it.
REFERENTIAL_BOX = {"here": "location", "there": "location", "now": "time", "then": "time"}

#: «HOWEVER, he left» — the connective reading, which the free-relative row does not cover.
HOWEVER_DISCOURSE = {
    "version": VERSION,
    "form": "however",
    "word_class": "adverb",
    "role": "coordinator",
    "features": {},
    "compiled": {"kind": "join", "operator": "and", "pragmatic": "concessive"},
    "source": "tk1 `lib/llc/constants.py`, the hand list this table retires — reading added by "
              "db/0014 after db/0013's clash check found the gap",
    "note": "the CONNECTIVE reading, beside the free-relative «however you do it». Truth-functionally "
            "AND; the defeated expectation is not truth-functional and is parked by name, exactly as "
            "db/0008 parked the concessive prepositions. UD's `discourse` relation names it",
}


def build_rows(previous: list[dict]) -> list[dict]:
    """Version 7 = version 6, four rows given their box, plus one new row. Nothing else changes."""
    out = []
    for row in previous:
        if row.get("version") != 6:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = VERSION
        if row["role"] == "referential" and row["form"] in REFERENTIAL_BOX:
            role = REFERENTIAL_BOX[row["form"]]
            new["compiled"] = {**new["compiled"], "roles": [role]}
            new["note"] = (row.get("note") or "") + (
                f" — v7: fills the {role} box, head OPEN until context resolves it. It is indexical, "
                f"so the filler never earns a dimension (the second standing law) and the ROLE is "
                f"what the compiler was missing.")
        out.append(new)

    position = 1 + max(r["position"] for r in out if r["word_class"] == "adverb")
    out.append({**HOWEVER_DISCOURSE, "position": position})
    return out


def _previous_rows():
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 12), None)
    if found is None:
        raise RuntimeError("0012 is gone — it holds the version this one extends")
    return found.load().CLOSED_CLASS_ROWS


CLOSED_CLASS_ROWS = build_rows(_previous_rows())

#: **UNCHANGED BY THIS VERSION, AND THAT IS THE MIGRATION'S WHOLE LICENCE TO EXIST.** The exclusion
#: set is a set of FORMS: a row's `compiled` column may be edited and a second row may be added for a
#: form already present, and neither moves it. A NEW form would, and would take D and the sealed base
#: with it — which is why `db/0013`'s sixty adverbs are a separate table.
CLOSED_CLASS_FORMS = tuple(
    sorted({row["form"] for row in CLOSED_CLASS_ROWS if " " not in row["form"]})
)


def _check() -> None:
    previous = {row["form"] for row in _previous_rows() if " " not in row["form"]}
    if set(CLOSED_CLASS_FORMS) != previous:
        arrived = sorted(set(CLOSED_CLASS_FORMS) - previous)
        left = sorted(previous - set(CLOSED_CLASS_FORMS))
        raise ValueError(
            f"THE EXCLUSION SET MOVED — arrived {arrived}, left {left}. D's vocabulary filter would "
            f"change and the sealed base would be built against a different set of function words."
        )
    for form, role in REFERENTIAL_BOX.items():
        row = next(r for r in CLOSED_CLASS_ROWS
                   if r["form"] == form and r["role"] == "referential")
        if row["compiled"].get("roles") != [role]:
            raise ValueError(f"{form!r} did not gain its box")


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(ClosedClassDoc, CLOSED_CLASS_ROWS)
