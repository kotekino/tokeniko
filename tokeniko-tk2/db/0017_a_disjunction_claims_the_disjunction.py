"""0017 — closed classes v10: **a disjunction claims the disjunction, not its halves.**

**FOUND ON E3 TASK 2c's BENCH** (2026-09-18). `db/0010` gave every coordinator `asserts: both` — right
for «and», «but», «yet», and wrong for the two that are not conjunctions of claims:

    «The cat is hungry or tired»            hungry CLAIMED · tired CLAIMED · OR CLAIMED
    «The cat is neither hungry nor tired»   hungry CLAIMED · tired CLAIMED · NOR CLAIMED

The first claims more than the speaker said: «hungry or tired» does not tell you it is hungry. The
second **contradicts itself** — NOR is true only when both halves are false, and the zip claimed both
true beside it. The logic kernel would have refused the belief; the station should never have built
it.

**Both become `asserts: neither`**, the shape `if` already has: the halves are STATED and not claimed,
and the JOIN carries the claim. Nothing in the compiler changes — `_relate` has read `neither` since
`db/0010`.

**THE EXCEPTION, RULED AND NOT BUILT — FREE CHOICE UNDER A MODAL** (the Captain, 2026-09-18). The
drill's only disjunction is `t-ws-7`: *«It doesn't contradict, because a mind CAN be an animal or a mind
CAN be a software»* — and it holds both halves at 1.0 **deliberately**: under a possibility modal the
speaker means both possibilities hold, which is why «it doesn't contradict». That is a property of
`or` under `can`, not of `or`, so it does not keep every other disjunction claiming its halves.
`t-ws-7` becomes a named disagreement in the drill gate's ratchet.

**Nothing else moves**: no form arrives or leaves, so D's gloss-word exclusion is untouched.

**Written by the QM on 2026-09-18, on the Captain's ruling «(b), go with the fix».**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, ClosedClassDoc
from tk2.migrations import ensure_collections

VERSION = 10

#: The coordinators whose halves are STATED, not claimed — the join is the claim.
CLAIMS_ONLY_THE_JOIN = ("or", "nor")


def build_rows(previous: list[dict]) -> list[dict]:
    out = []
    for row in previous:
        if row.get("version") != 9:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = VERSION
        compiled = new.get("compiled") or {}
        if (row["role"] == "coordinator" and row["form"] in CLAIMS_ONLY_THE_JOIN
                and compiled.get("kind") == "join"):
            new["compiled"] = {**compiled, "asserts": "neither"}
            new["note"] = (row.get("note") or "") + (
                " — v10: asserts=neither. A disjunction claims the disjunction, not its halves; "
                "`nor` claiming both halves contradicted its own join.")
        out.append(new)
    return out


def _previous_rows():
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 16), None)
    if found is None:
        raise RuntimeError("0016 is gone — it holds the version this one extends")
    return found.load().CLOSED_CLASS_ROWS


CLOSED_CLASS_ROWS = build_rows(_previous_rows())

#: Unchanged, and checked — this migration edits `compiled` and adds no form.
CLOSED_CLASS_FORMS = tuple(
    sorted({row["form"] for row in CLOSED_CLASS_ROWS if " " not in row["form"]})
)


def _check() -> None:
    before = _previous_rows()
    if {r["form"] for r in before if " " not in r["form"]} != set(CLOSED_CLASS_FORMS):
        raise ValueError("THE EXCLUSION SET MOVED — D's vocabulary filter would change with it")
    if len(before) != len(CLOSED_CLASS_ROWS):
        raise ValueError("a row was added or lost — this migration only edits")

    # Every form it names must actually have been changed: a row renamed upstream would otherwise
    # make this migration a silent no-op that still claims to have fixed the disjunction.
    for form in CLAIMS_ONLY_THE_JOIN:
        joins = [r for r in CLOSED_CLASS_ROWS if r["form"] == form and r["role"] == "coordinator"]
        if len(joins) != 1 or joins[0]["compiled"].get("asserts") != "neither":
            raise ValueError(f"{form!r} must be exactly one coordinator, asserting neither half")


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(ClosedClassDoc, CLOSED_CLASS_ROWS)
