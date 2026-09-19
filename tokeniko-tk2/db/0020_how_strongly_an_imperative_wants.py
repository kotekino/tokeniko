"""0020 — attitude strengths v1: **how strongly an imperative wants** (parser-compiler req 23).

**THE FIRST OF TASK 2d's TWO PARKED QUESTIONS, ANSWERED BY THE CAPTAIN ON 2026-09-19.** The drill
hand-compiles «Close the door!» as POV(me · want) at `strength=0.9` (`aw-21`), and the station wrote
nothing there — the tree states no such number, and its own comment said the 0.9 was a question for
the Captain before it was a number in code. His ruling: **knowledge** — *«the heart can influence the
base value, staying on the knowledge, but let's see when we do the heart»*.

**IT IS A ROW BECAUSE IT IS A FACT ABOUT ENGLISH, NOT ABOUT LOGIC.** How hard a bare imperative wants
is the baseline that «please», «kindly» and «would you mind» move away from — the gradation tkzip
req 51 gave the slot for. A constant in the compiler would have made every one of those a code
change; a row makes them migrations, on the day each has a witness.

**ONE ROW, AND THE SECOND WITNESS IS NAMED AND NOT WRITTEN.** `t-md-4` («I WOULD LIKE to know what
you think») is hand-compiled at 0.6, and there is no row for it, because the station has no
desiderative path to read «would like» with — that arrives with req 55's attitude verbs. *A row
nothing can read is not knowledge, it is a note in the wrong place.* Likewise no softener row: a
class enters on a witness, not on a principle (the standing law of 2026-09-18), and the drill holds
no «please».

**WHAT THIS CLOSES**: `aw-21` went red at the drill gate's fourth widening (2026-09-19), which put
the prefix inside the instrument for the first time — the number and the thing that can measure it
arrived in the right order. The gate compares the SLOT and never the magnitude, so a later
re-curation of 0.9 is a migration and not a red gate.

**NAMED FOR THE FRAME/KNOWLEDGE AUDIT, NOT MOVED HERE**: `IMPERATIVE_VERB = "want.v"` — that an
imperative is a WANT is the other half of this row's fact, and it is still in code. It belongs to
E3's closing audit with the rest of the list, and it is written down here so the audit finds it.

**Written by the QM on 2026-09-19, on the Captain's «1. knowledge».**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, AttitudeStrengthDoc
from tk2.migrations import ensure_collections

VERSION = 1

ATTITUDE_STRENGTH_ROWS = [
    {
        "version": VERSION,
        "shape": "imperative",
        "compiled": {"strength": 0.9},
        "source": ("the drill's `aw-21`, «Close the door!», hand-compiled at E2 with no parser "
                   "involved; the Captain's ruling of 2026-09-19 that the number is knowledge"),
        "note": ("the BARE imperative — «please», «kindly» and «would you mind» soften it and have "
                 "no witness in the drill, so they have no row yet"),
        "position": 0,
    },
]


def _check() -> None:
    shapes = [r["shape"] for r in ATTITUDE_STRENGTH_ROWS]
    if sorted(shapes) != sorted(set(shapes)):
        raise ValueError(f"one row per shape of wanting — got {shapes}")
    for row in ATTITUDE_STRENGTH_ROWS:
        strength = row["compiled"].get("strength")
        if not isinstance(strength, (int, float)) or not 0.0 <= strength <= 1.0:
            raise ValueError(f"{row['shape']}: {strength!r} is not a strength in [0, 1]")


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(AttitudeStrengthDoc, ATTITUDE_STRENGTH_ROWS)
