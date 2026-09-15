"""0009 — closed classes version 3: three mappings the UD gate found wrong within the hour.

**WHY A NEW VERSION AND NOT AN EDIT.** `db/0008` was applied on 2026-09-15 and the gate found these
three the same afternoon. The QM tried to fix the file and re-run it. **The runner refused, and it
was right to:**

    0008_the_closed_classes_learn_what_they_compile_to has changed since it was applied.
    An applied migration is immutable: the database already holds what the old file did, so this
    ledger row now describes something that no longer exists. Write a NEW migration to correct it.

The checksum is over the file's BYTES, so even reverting the logic and leaving a changed docstring
trips it — which is the guard being stricter than the intention behind it, and correct. `0008` is now
restored byte-exact to what was applied (`bcbc2ad`), including the parts of it that are wrong.

`ClosedClassDoc`'s own docstring says how a change goes instead: *«A change is a new version written
whole; the old version stays readable beside it.»* So version 2 stays on the body exactly as it
landed, this is version 3, and **0008 keeps saying what it said** — a ledger entry must describe
something that actually ran.

**WHAT THE GATE IS.** `tools/ud_gate.py` scores the station against Universal Dependencies' own
published examples — the Captain's ruling of 2026-09-15, and the reason it beats more of our own
sentences: our fixtures encode OUR habits, UD's examples are strangers'. All three corrections below
were found by it, and none of them by reading the code.

---

**1. THE POSSESSIVE CLITIC WAS TYPED AS GLUE.** UD's `case` page analyses «the Chair **'s** office»
as `case('s)` + `nmod(office, Chair)` — **and pairs it explicitly with «the office OF the Chair»**,
the same relation in two spellings. v2 compiled `'s` to `structure`, so one of those two spellings
threw the possessor away entirely. tkzip keeps the possessor INSIDE the record as `Box.relation`
(req 26, the Captain's own noun-phrase draft), so it fills a **FIELD** — not a box, and not nothing.

*The pairing is what makes this a defect rather than a preference: UD states the two forms mean the
same thing, and the table made one of them vanish.*

**2. PLAIN COPULAR `be` WAS MOVING THE THEATRE.** Requirement 31, and the Captain's first draft
verbatim: «the cat is cute» is ***cat + cute, no verb***. v2 typed every form of `be` as
`tense_aspect` → theatre, which quietly gave the copula a job it does not have.

It compiles **conditionally** now, because one row cannot tell the three `be`s apart and should not
pretend to:

    «Sue is a teacher»      cop     -> STRUCTURE   glue; the predicate is `teacher`
    «she is running»        aux     -> theatre     progressive; it moves the theatre
    «there is a cat»        (root)  -> theatre     EXISTENTIAL `be` is content (req 31 names it)

The row states both readings and **names the dependency that chooses** (`when: "cop"`). That keeps
the seam where the standing law puts it: the knowledge is in the row, the selection is in the code,
and neither is guessing at the other's job.

**3. ~~The wh-word and the double-object recipient~~ — NOT ROWS AT ALL, and that is the finding.**
The gate's first transcription expected `time` from «when» and `recipient` from «me», and both were
the QM asking the marker table a question it cannot hold. **The 37 → 18 mapping has two halves**: a
role arriving with a MARKER is these rows' business, a role arriving by RELATION (`agent`,
`patient`, `recipient`) is the compile core's. The table proves the split by holding no marker for
`patient` or `experiencer` — English has none. Nothing changes here; the corpus was corrected and
the split is now parser-compiler requirement 12.

---

**Written by the QM on the Captain's ruling of 2026-09-15: «commit, then re-apply 0008 to the body»,
answered with the three ways that could go — and he chose the new version.**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, ClosedClassDoc
from tk2.migrations import ensure_collections

VERSION = 3

#: The forms of `be`. Copular `be` is glue; the same spellings under `aux` move the theatre, and
#: existential `be` is content. One row cannot decide which — the dependency can, so the row carries
#: all three readings and the condition that picks.
COPULAR_BE = ("be", "is", "am", "are", "was", "were", "been", "being", "'s", "'re", "'m")

#: `'s` under `case` is the possessor, and the possessor is a FIELD of the record rather than a box.
POSSESSIVE = {"kind": "field", "field": "relation", "was": "structure"}


def corrected(row: dict) -> dict | None:
    """The new `compiled` for a row, or None where version 2 was already right.

    One function, so the migration's claim is auditable: everything it changes passes through here
    and everything else is carried forward untouched.
    """
    if row["role"] == "genitive":
        return dict(POSSESSIVE)
    if row["role"] == "tense_aspect" and row["form"] in COPULAR_BE:
        return {"kind": "structure", "when": "cop", "otherwise": "theatre", "was": "theatre"}
    return None


def build_rows(previous: list[dict]) -> list[dict]:
    """Version 3 = version 2, with three mappings corrected and every other row carried whole."""
    out = []
    for row in previous:
        if row.get("version") != 2:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = VERSION
        fixed = corrected(row)
        if fixed is not None:
            new["compiled"] = fixed
            new["note"] = (row.get("note") or "") + (
                " — CORRECTED at v3 by the UD gate: "
                + ("the possessive marks a POSSESSOR and v2 compiled it to glue."
                   if row["role"] == "genitive" else
                   "plain copular `be` is STRUCTURE (req 31) and v2 made every `be` move the theatre.")
            )
        out.append(new)
    return out


def _previous_rows():
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 8), None)
    if found is None:
        raise RuntimeError("0008 is gone — it holds the version this one corrects")
    return found.load().CLOSED_CLASS_ROWS


#: Declared under the name the readers look for, so `newest_migration_declaring` finds THIS file.
CLOSED_CLASS_ROWS = build_rows(_previous_rows())

#: The single-word forms — unchanged by this version, and rebuilt here so the dictionary's offline
#: exclusion reads the newest declaration rather than a stale copy. A CORRECTION THAT MOVED THIS SET
#: WOULD MOVE THE BASE: D is built from gloss words minus these, so the build would change under a
#: policy nobody re-ruled. It does not move, and `tests/test_closed_classes.py` holds that.
CLOSED_CLASS_FORMS = tuple(
    sorted({row["form"] for row in CLOSED_CLASS_ROWS if " " not in row["form"]})
)


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(ClosedClassDoc, CLOSED_CLASS_ROWS)
