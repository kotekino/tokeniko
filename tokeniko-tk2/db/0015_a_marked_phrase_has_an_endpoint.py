"""0015 — closed classes v8 and adverb kinds v2: **`direction` is for what a MARKER cannot mark.**

**FOUND BY THE DRILL GATE ON ITS FIRST RUN** (`tools/drill_gate.py`, requirement 18 — the control
that finally made the station's output meet the Captain's own hand-compiled zips). Two of its six
disagreements were curation errors, and they are the same error seen from both ends.

**ONE — «I walk TOWARD the station» compiled a DIRECTION and the drill says DESTINATION.** The drill
is explicit, across three hand-compiled rows:

    dir-1  I walk to the station            destination = station.n, marker «to»
    dir-2  I walk toward the station        destination = station.n, marker «toward»
    dir-3  I walked as far as the bridge    destination = bridge.n, marker «as far as»

and dir-2's own note says why: *«same box, different marker — and the marker row is where "no
arrival entailed" lives»*. **Requirement 65 exists so that these share a box.** Typing `toward` as a
direction put the entailment in the ROLE, which is the one place req 65 says it must not be.

**THE PRINCIPLE, WHICH IS SHARPER THAN THE THREE CASES.** Requirement 67 defines `direction` as *«a
direction with NO ENDPOINT — «He looked up», «She turned left» — which is not a destination, not a
path and not a manner»*. **A marked phrase HAS an endpoint: the nominal IS the endpoint.** «Toward
the station» names the station; «onto the table» names the table. So a `role_marker` can never
produce `direction` — the role exists precisely for the case where there is no nominal to mark, and
what fills it is a bare particle or adverb. Five rows are corrected on that principle, not on three
witnesses:

    toward · towards · onto · unto   ->  destination   (the nominal is the endpoint)
    out                              ->  path          («out the door» is the route, not the goal)

`up`, `down` and `off` keep `direction` in their candidate lists and lose nothing: they are
`ambiguous` markers whose `db/0012` selector already sends a MARKED phrase to `location` or `source`,
and their bare particle readings are separate rows that this migration does not touch.

**TWO — «She turned LEFT» compiled a MANNER, and it is the sentence requirement 67 WAS WRITTEN FOR.**
`db/0013` holds the four-way adverb split and its `direction` list has `backwards`, `forwards`,
`sideways`, `upwards`… **and not `left`, `right` or any compass point** — so the manner default
answered, which is what a default is for and it was wrong here. The very words that forced the
eighteenth role into the format were missing from the table that routes them to it.

*Both errors are of one kind: a role and a marker drifting apart from what E2 hand-compiled, in a
direction no existing gate could see. That is what req 18 said would happen and it happened on the
first run.*

**Written by the QM on 2026-09-16, on the drill gate's own report.**
"""

from tk2.core.models import (
    ALL_MODELS,
    BASE_MODELS,
    LEDGER_MODELS,
    AdverbKindDoc,
    ClosedClassDoc,
)
from tk2.migrations import ensure_collections

CLOSED_VERSION = 8
ADVERB_VERSION = 2

#: form -> the role it actually marks. Every one of these marks a NOMINAL, and the nominal is the
#: endpoint — so none of them is a `direction` under req 67's own definition.
MARKER_CORRECTIONS = {
    "toward": ["destination"],
    "towards": ["destination"],
    "onto": ["destination"],
    "unto": ["destination"],
    # «he went OUT the door» is the route taken, not the goal reached — the door is not where he
    # ended up. `out of` is a separate multi-word row and already marks `source`.
    "out": ["path"],
}

#: The direction adverbs `db/0013` missed — including the two req 67 was written for. `northwards`
#: and its compass siblings are NOT here: v1 already has them, and the check below is what said so.
DIRECTION_ADVERBS = (
    "left", "right", "north", "south", "east", "west",
    "leftwards", "rightwards", "inwards", "outwards", "skywards",
)


def build_closed(previous: list[dict]) -> list[dict]:
    out = []
    for row in previous:
        if row.get("version") != 7:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = CLOSED_VERSION
        compiled = new.get("compiled") or {}
        if (row["role"] == "role_marker" and compiled.get("kind") == "box"
                and row["form"] in MARKER_CORRECTIONS
                and compiled.get("roles") == ["direction"]):
            new["compiled"] = {**compiled, "roles": list(MARKER_CORRECTIONS[row["form"]])}
            new["note"] = (row.get("note") or "") + (
                " — v8: a MARKED phrase has an endpoint (the nominal IS the endpoint), and req 67's "
                "`direction` is for a direction with NONE. The drill hand-compiles «to», «toward» "
                "and «as far as» into one DESTINATION box differing only by marker (req 65).")
        out.append(new)
    return out


def build_adverbs(previous: list[dict]) -> list[dict]:
    out = []
    for row in previous:
        if row.get("version") != 1:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = ADVERB_VERSION
        out.append(new)

    position = 1 + max(r["position"] for r in out)
    for form in DIRECTION_ADVERBS:
        out.append({
            "version": ADVERB_VERSION,
            "form": form,
            "kind": "circumstantial",
            "compiled": {"kind": "box", "roles": ["direction"]},
            "source": "the drill gate, 2026-09-16 — «She turned left» is req 67's own witness",
            "note": "req 67's eighteenth role, and «left» is one of the two sentences that forced it "
                    "into the format. v1 held `backwards` and `sideways` and missed these",
            "position": position,
        })
        position += 1
    return out


def _previous(number: int, attribute: str):
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == number), None)
    if found is None:
        raise RuntimeError(f"{number:04d} is gone — it holds the version this one extends")
    return getattr(found.load(), attribute)


CLOSED_CLASS_ROWS = build_closed(_previous(14, "CLOSED_CLASS_ROWS"))
ADVERB_KIND_ROWS = build_adverbs(_previous(13, "ADVERB_KIND_ROWS"))

#: Unchanged, and checked — this migration edits `compiled` and adds no FORM to the closed classes.
CLOSED_CLASS_FORMS = tuple(
    sorted({row["form"] for row in CLOSED_CLASS_ROWS if " " not in row["form"]})
)


def _check() -> None:
    before = {row["form"] for row in _previous(14, "CLOSED_CLASS_ROWS") if " " not in row["form"]}
    if set(CLOSED_CLASS_FORMS) != before:
        raise ValueError("THE EXCLUSION SET MOVED — D's vocabulary filter would change with it")

    # **NO ROLE MARKER MAY PRODUCE `direction` ALONE.** The invariant this migration exists to
    # establish, checked rather than asserted: req 67's role is for a direction with NO endpoint, and
    # a marker always has one. `up`/`down`/`off` keep it as a CANDIDATE — their selectors route a
    # marked phrase elsewhere — so the refusal is on a row that offers nothing else.
    for row in CLOSED_CLASS_ROWS:
        compiled = row.get("compiled") or {}
        if row["role"] == "role_marker" and compiled.get("roles") == ["direction"]:
            raise ValueError(
                f"{row['form']!r} marks a nominal and would produce `direction` alone — but the "
                f"nominal IS the endpoint, and req 67's role is for a direction with none"
            )

    # **THE ADVERB TABLE'S LAWS, RE-RUN IN FULL — BOTH OF THEM.** This migration's first draft
    # checked only the clash with the closed classes and shipped a DUPLICATE: `northwards` is
    # already a v1 direction adverb, and the unique index (version, form, kind) refused the write
    # with a `BulkWriteError` that took 39 tests down with it.
    #
    # **A CHECK MUST TRAVEL WITH THE DATA IT GUARDS.** `db/0013` had this check and `db/0015` added
    # rows to the same table without it, which is how an invariant that was written once stops
    # holding. Every migration that touches a table re-runs that table's laws.
    closed = {row["form"] for row in CLOSED_CLASS_ROWS}
    clash = sorted({row["form"] for row in ADVERB_KIND_ROWS} & closed)
    if clash:
        raise ValueError(f"{clash} are in BOTH rosters and a reader could not tell which answers")

    seen = set()
    for row in ADVERB_KIND_ROWS:
        key = (row["form"], row["kind"])
        if key in seen:
            raise ValueError(f"{row['form']!r} appears twice as {row['kind']} — the unique index is "
                             f"(version, form, kind) and the write would be refused")
        seen.add(key)
    if any(row["kind"] == "manner" for row in ADVERB_KIND_ROWS):
        raise ValueError("`manner` is the DEFAULT and may not be a row")


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(ClosedClassDoc, CLOSED_CLASS_ROWS)
    writer.insert_many(AdverbKindDoc, ADVERB_KIND_ROWS)
