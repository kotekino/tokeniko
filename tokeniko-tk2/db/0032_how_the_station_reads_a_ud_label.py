"""0032 — UD readings v1: **how the station reads a UD label**, where it differs (req 9, E3 task 8).

**E3's FRAME/KNOWLEDGE AUDIT, ACTED ON.** Three frozensets in `tk2/language/compile.py` each
encoded an argument, and an argument is knowledge:

    DEPS_THAT_COMPILE_TO_NOTHING = {"vocative"}   «a vocative is addressing, not content»
    CLAUSE_DEPS, with `xcomp` ABSENT              «nobody asserts that you swim»
    NUMBERED_UPOS = {"NOUN"}                      «a proper noun's number is not evidence»

**A ONE-MEMBER SET IS NEVER A SET — it is a decision with brackets round it.** And the other two are
the same thing wearing more members: what made them suspect was never the brackets, it was that the
membership could not be derived from UD's own definitions.

*The sets that COULD be — `SUBJECT_DEPS`, `OBJECT_DEPS`, `NOMINAL_DEPS` and the rest — stay in code
and the audit says why: every member is a relation whose UD definition already names the structural
kind, so the reading is transcription. Reading the tree's shape is frame (the Captain, 2026-09-18).*

---

**THE DEFAULT IS NOT A ROW** — `db/0013`'s shape, and it is what makes this table small enough to
curate. A label with no row is read the ordinary way; a row is an EXCEPTION. So a miss is an ANSWER
and not an absence, exactly as a missing adverb kind means `manner`.

    vocative   compiles_to_content: false    E2's ruling, made in the drill
    xcomp      opens_clause: false           `xcomp` is UD's «open clausal complement» and UD is
                                             right to call it a clause — we decline to make it a ROW
    NOUN       states_number: true           everything else states none

**AND `CLAUSE_DEPS` GETS BIGGER, WHICH IS THE POINT.** It used to exclude `xcomp` silently; it now
holds every relation UD names as a clause — `xcomp` included — and the compiler asks this table
which of them opens a row. The set became pure transcription and the judgement became a row, which
is the split the audit found and the reason the migration is worth making at all. *A row that the
code could not consult would be decoration.*

**WHY `NOUN` AND NOT `PROPN`** — measured, 2026-09-21: taking a proper noun's `Number` cost the
fixpoint a sentence it could never close (`q-9`), because the same referent reaches a box by two
routes — «John told ME» and «John told MARIE» — and only the name carried a number. UD tags every
`PROPN` `Number=Sing` by default morphology rather than on evidence. Dropping it: **65 → 66 of 87**,
and nothing else moved. *«The Alps are beautiful» loses its agreement, and names are E3b.*

**`SAYING_VERBS` IS NOT HERE AND MUST NOT BE.** It is the fourth thing the audit found, and req 55
already rules its replacement: nearest-anchor geometry over a small anchor set, *«so the
classification never misses the verb nobody thought of»*, owned by E4. Writing nine verb keys into
rows now would move a closed set rather than remove one.

**Written by the QM on 2026-09-22, on the Captain's «reconcile the plan's table, then go for the
migration».**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, UdReadingDoc
from tk2.migrations import ensure_collections

VERSION = 1

UD_READING_ROWS = [
    {
        "version": VERSION,
        "inventory": "relation",
        "label": "vocative",
        "reads": {"compiles_to_content": False},
        "source": "E2's ruling, made in the drill: «the vocative is addressing, not content»",
        "note": "«Guys, take it easy» is an instruction to a room, and the room is not a "
                "participant in it. The token is ACCOUNTED FOR and dropped on purpose — a word "
                "merely left out and a word that compiles to nothing are different answers, and "
                "`Zip.unplaced` is for the first (req 21).",
        "position": 0,
    },
    {
        "version": VERSION,
        "inventory": "relation",
        "label": "xcomp",
        "reads": {"opens_clause": False},
        "source": "parser-compiler req 38 and the truth slot: an unasserted proposition in the zip "
                  "with nothing marking it unasserted is the one thing that slot exists to prevent",
        "note": "«You like TO SWIM» is one predication with a controlled subject, not two claims: "
                "nobody asserts that you swim. UD names it an OPEN CLAUSAL COMPLEMENT and is right "
                "to — the judgement here is ours, that it does not earn a row of its own, and it "
                "stays inside its matrix clause until there is a reason it cannot.",
        "position": 1,
    },
    {
        "version": VERSION,
        "inventory": "pos",
        "label": "NOUN",
        "reads": {"states_number": True},
        "source": "measured 2026-09-21 — `NOUN`+`PROPN` gave fixpoint 65 of 87, `NOUN` alone 66, "
                  "and nothing else moved",
        "note": "«cats» is plural because the SPEAKER chose that word — a fact about the utterance, "
                "which is what schema v6's `Box.number` records. «Marie» is singular because Marie "
                "is one person, a fact about the REFERENT, and UD tags every proper noun "
                "`Number=Sing` by default morphology rather than on evidence. A referent's number "
                "arrives when the referent does, which is E3b.",
        "position": 2,
    },
]


def _check() -> None:
    seen = set()
    for row in UD_READING_ROWS:
        key = (row["inventory"], row["label"])
        if key in seen:
            raise ValueError(f"{key} is read twice — the index refuses it and so does sense")
        seen.add(key)
        if row["inventory"] not in ("relation", "pos"):
            raise ValueError(f"{row['label']!r} names no UD inventory: {row['inventory']!r}")
        if not row["reads"]:
            raise ValueError(f"{row['label']!r} states no reading — then it is not an exception")
        if not row["source"]:
            raise ValueError(f"{row['label']!r} has no source: a ruling with no origin is a guess")

    # **EVERY ROW MUST DIFFER FROM THE DEFAULT**, or it is noise the table has to carry forever.
    # This is `db/0013`'s discipline: the table holds what differs and nothing else.
    defaults = {"compiles_to_content": True, "opens_clause": True, "states_number": False}
    for row in UD_READING_ROWS:
        for question, answer in row["reads"].items():
            if question not in defaults:
                raise ValueError(f"{question!r} has no default — a reader could not know what a "
                                 f"label with no row means")
            if answer == defaults[question]:
                raise ValueError(f"{row['label']!r} says {question}={answer}, which IS the default: "
                                 f"the table holds what differs")


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(UdReadingDoc, UD_READING_ROWS)
