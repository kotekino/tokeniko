"""0033 — closed classes v18: **«as far as» marks an ENDPOINT** (parser-compiler req 65, `db/0015`).

**«I walked as far as the bridge» was compiling to «I walked far.»** The bridge was gone — and
BOTH instruments called it fine. The fixpoint reported `dir-3` **FIXED**, because a truncated
sentence recompiles to the same truncated zip; the drill gate reported *no common ground*, because
a row that is MISSING is not a row that CONFLICTS. A sentence losing its object, green twice over.

**THE DRILL HAS SAID SO SINCE THE FIRST RUN.** `db/0015` names this exact phrase, in the ruling that
created `destination`:

    dir-1  I walk to the station          destination = station.n, marker «to»
    dir-2  I walk toward the station      destination = station.n, marker «toward»
    dir-3  I walked as far as the bridge  destination = bridge.n, marker «as far as»

Requirement 65 is why they share a box: *«same box, different marker — and the marker row is where
«no arrival entailed» lives»*. «as far as» is the third of those markers and the only one nobody
wrote down. The table already holds `as for` · `as from` · `as of` · `as to` · `as if` ·
`as long as` · `as soon as` · `as though`; this is the gap in a family that is otherwise complete.

**WITHOUT IT THE BARE `as` ANSWERS, AND ANSWERS WRONGLY.** `as` alone is `roles: [manner, measure]`
with a selector, so «as far as the station» read the station as a MEASURE — «I walk as far as the
station» came back «I walk the station far». The multi-word row outranks it because matching is
longest-first (`tk2/language/closed.py`), which is what that discipline is for.

*`complex: true` and `word_class: preposition`, as every other multi-word marker in this table
carries — the note «multi-word: one marker» is `db/0008`'s own wording for the family.*

**Written by the QM on 2026-09-22, the third item of E3's remaining tail.**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, ClosedClassDoc
from tk2.migrations import ensure_collections

VERSION = 18

#: The one row this migration adds, at a position after everything v17 holds.
AS_FAR_AS = {
    "version": VERSION,
    "form": "as far as",
    "role": "role_marker",
    "word_class": "preposition",
    "compiled": {"kind": "box", "roles": ["destination"]},
    "features": {"complex": True},
    "source": "the drill, `dir-3`, hand-compiled by the Captain — and `db/0015`'s ruling that a "
              "marked phrase with an endpoint is a DESTINATION, the marker carrying the entailment",
    "note": "multi-word: one marker. «no arrival entailed» lives in the marker (req 65), not in "
            "the role — which is exactly why `toward` and `as far as` share `destination` with `to`.",
    "position": 135,
    "spoken": False,
}


def build_rows(previous: list[dict]) -> list[dict]:
    out = []
    for row in previous:
        if row.get("version") != 17:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = VERSION
        out.append(new)
    out.append(dict(AS_FAR_AS))
    return out


def _previous_rows():
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 31), None)
    if found is None:
        raise RuntimeError("0031 is gone — it holds the version this one extends")
    return found.load().CLOSED_CLASS_ROWS


CLOSED_CLASS_ROWS = build_rows(_previous_rows())

#: **THE EXCLUSION SET IS UNCHANGED, AND THAT IS NOT LUCK.** It holds only single-word forms — it
#: is what filters D's vocabulary — and every form this migration adds has a space in it.
CLOSED_CLASS_FORMS = tuple(
    sorted({row["form"] for row in CLOSED_CLASS_ROWS if " " not in row["form"]})
)


def _check() -> None:
    before = _previous_rows()
    if {r["form"] for r in before if " " not in r["form"]} != set(CLOSED_CLASS_FORMS):
        raise ValueError("THE EXCLUSION SET MOVED — D's vocabulary filter would change with it")
    if len(CLOSED_CLASS_ROWS) != len(before) + 1:
        raise ValueError("this migration adds exactly one row")
    if any(row.get("compiled") != was.get("compiled") or row.get("role") != was.get("role")
           for row, was in zip(CLOSED_CLASS_ROWS, before)):
        raise ValueError("an existing meaning moved — this migration only ADDS")

    if any(r["form"] == "as far as" for r in before):
        raise ValueError("«as far as» is already in the table")
    if AS_FAR_AS["position"] in {r.get("position") for r in before}:
        raise ValueError("the new row's position collides with an existing one")

    # **THE MARKER CARRIES THE ENTAILMENT AND THE ROLE DOES NOT** (req 65, `db/0015`): every one of
    # these markers reaches the SAME box, and a role that differed between them would put «no
    # arrival entailed» in the one place that ruling says it must not be.
    # REACHES it, not «is only it»: `to` is `[destination, recipient]` behind a selector, because
    # «I walk TO the station» and «she gave it TO me» are one marker and two boxes.
    endpoints = {r["form"] for r in CLOSED_CLASS_ROWS
                 if "destination" in ((r.get("compiled") or {}).get("roles") or [])}
    for expected in ("to", "toward", "up to", "as far as"):
        if expected not in endpoints:
            raise ValueError(f"{expected!r} does not reach `destination` — req 65's family is broken")


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(ClosedClassDoc, CLOSED_CLASS_ROWS)
