"""0030 — closed classes v16: **how many is not which number** (tkzip req 2, schema v7).

**«I saw both» compiled to `Open(number='dual')`, and «They praised each other» did the same.** A
value the field does not admit, sitting in a zip, with nothing able to say it back — both sentences
decompiled to the empty string.

`Compiler._unknown()` copies a row's `number` into the OPEN that a described unknown carries (schema
v4: «she» is an unknown the sentence said three things about). That column means **the grammatical
number the speaker marked on this word** — `this`/`these`, `was`/`were`, the whole pronoun paradigm.

On four rows it meant something else entirely:

    both        the domain has exactly TWO
    neither     ... and neither of them
    either      ... and one of them
    each other  the reciprocal group is two, against «one another» for more

That is **how many things are in the set this word is about** — a fact about the SET, not the
grammatical number of anything — and the column for it already exists and is already used:

    once   count: 1        twice   count: 2

`count` is read by `Decompiler._fused()`, which refuses a word carrying one because it says more
than a bare quantity does (req 8, the same reason «often» is not the existential's voice). Nothing
on the unknown's path reads it. So the fact keeps its meaning, stops travelling into zips, and lands
in the column whose name already says what it is.

**THE FOURTH TIME IN TWO DAYS THAT ONE COLUMN CARRIED TWO FACTS** — after `no`/`nobody` sharing a
`compiled` (`db/0028`), a determiner's number against an unknown's own (`db/0029`, which is why that
one is `takes_number`), and the described unknown itself (schema v4). Every one was written by a
writer who meant something else, and every one stayed invisible until something downstream choked.
Schema v7 is the other half of this fix: `number` is now a `Literal["sg", "pl"]`, so the next such
value raises where it is WRITTEN instead of travelling to where it cannot be read.

*«one another» keeps `number: pl` and is NOT touched. `pl` is a value the field admits and «one
another is plural» is at least arguable, so changing it would be a judgement on no evidence — which
is the thing this migration exists to undo. It is named on the roadmap instead.*

**A KNOWN LOSS, RECORDED RATHER THAN PAPERED OVER**: the zip still does not carry a quantifier's
domain cardinality, so «Neither is late» reads back as a bare negative — it is now WELL-FORMED and
silent, where it was malformed and silent. `Box.count` is where it would go when it is built, and
that wants the decompiler to have a voice for it first.

**Written by the QM on 2026-09-21, on the Captain's «we should tackle it asap».**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, ClosedClassDoc
from tk2.migrations import ensure_collections

VERSION = 16

#: `(role, form, position)` -> the cardinality that used to be spelled `number: "dual"`.
#: Every one of these is a word about exactly two things.
CARDINALITY = {
    ("quantificational", "both", 16): 2,
    ("quantificational", "neither", 24): 2,
    ("quantificational", "either", 25): 2,
    ("reciprocal", "each other", 34): 2,
}


def build_rows(previous: list[dict]) -> list[dict]:
    out = []
    for row in previous:
        if row.get("version") != 15:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = VERSION
        count = CARDINALITY.get((row["role"], row["form"], row.get("position")))
        if count is not None:
            features = {**(row.get("features") or {})}
            features.pop("number", None)
            features["count"] = count
            new["features"] = features
        out.append(new)
    return out


def _previous_rows():
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 29), None)
    if found is None:
        raise RuntimeError("0029 is gone — it holds the version this one extends")
    return found.load().CLOSED_CLASS_ROWS


CLOSED_CLASS_ROWS = build_rows(_previous_rows())

#: Unchanged, and checked — this migration moves one feature to another and touches no spelling.
CLOSED_CLASS_FORMS = tuple(
    sorted({row["form"] for row in CLOSED_CLASS_ROWS if " " not in row["form"]})
)


def _check() -> None:
    before = _previous_rows()
    if {r["form"] for r in before if " " not in r["form"]} != set(CLOSED_CLASS_FORMS):
        raise ValueError("THE EXCLUSION SET MOVED — D's vocabulary filter would change with it")
    if len(before) != len(CLOSED_CLASS_ROWS):
        raise ValueError("a row was added or lost — this migration moves one feature")
    if any(row.get("compiled") != was.get("compiled") or row.get("role") != was.get("role")
           or row.get("spoken") != was.get("spoken")
           for row, was in zip(CLOSED_CLASS_ROWS, before)):
        raise ValueError("a meaning, a role or a voice moved — this migration is about `features`")

    placed = {(row["role"], row["form"], row.get("position")) for row in CLOSED_CLASS_ROWS}
    missing = [key for key in CARDINALITY if key not in placed]
    if missing:
        raise ValueError(f"{missing} name no row")

    touched = sorted(row["form"] for row, was in zip(CLOSED_CLASS_ROWS, before)
                     if row.get("features") != was.get("features"))
    if touched != sorted(form for _, form, _ in CARDINALITY):
        raise ValueError(f"{touched} changed features and the migration names "
                         f"{sorted(f for _, f, _ in CARDINALITY)}")

    # **THE THING THIS MIGRATION EXISTS FOR.** `Compiler._unknown()` copies `number` into an OPEN,
    # and schema v7 admits exactly two values there. A row carrying any other is a row that writes a
    # zip nothing can read — which is what «I saw both» did until today.
    from tk2.tkzip.schema import Number
    from typing import get_args

    legal = set(get_args(Number))
    illegal = [(row["form"], (row["features"] or {}).get("number")) for row in CLOSED_CLASS_ROWS
               if (row.get("features") or {}).get("number") not in (None, *legal)]
    if illegal:
        raise ValueError(f"{illegal} carry a `number` schema v7 refuses — `_unknown` would write it "
                         f"into an OPEN and the zip would not validate")

    # And the fact was MOVED, not dropped: each of them still says «two», in the column for it.
    for (role, form, position), count in CARDINALITY.items():
        row = next(r for r in CLOSED_CLASS_ROWS
                   if (r["role"], r["form"], r.get("position")) == (role, form, position))
        if (row["features"] or {}).get("count") != count:
            raise ValueError(f"{form!r} lost its cardinality instead of moving it")


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(ClosedClassDoc, CLOSED_CLASS_ROWS)
