"""0040 — adverb kinds v5: **a focus word whose meaning is not settled says so, and the station
abstains** (parser-compiler, `E3.12.5.9.3.1` — the Captain's ruling of 2026-09-26, replacing
`E3.12.5.9.12` (5)).

**THE RULING, AS THE QM RELAYED IT** *(the Captain, 2026-09-26, «accepted all leans»)*:

    KEEP the manner default; each focus word met gets its OWN row in the adverb kinds (`focus`
    kind). Where the meaning is not settled, the row says ABSTAIN — a compiled meaning the station
    reads as «abstain, recorded» — designed in the rows, no word list in code. Known now: «even»,
    «strictly», «simply». «strictly if» must stop being a wrong claim.

**WHAT IT REPLACES.** Ruling 5 of `E3.12.5.9.12` asked the station to keep the manner default «inside
the population it was measured on», and the population would not define itself: `db/0013` measured
the default on all 3,767 of WordNet's single-word adverbs, «only» among them, and neither fact the
resource states separates a focus particle from a manner adverb — «only», «just» and «even» have no
pertainym, «exactly», «strictly», «simply» and «solely» each have one (measured 2026-09-26, the 1st
Officier's `E3.12.5.9` report). So the default stays what it was, and a focus word leaves it the only
way any word leaves it: by having a row. **A miss is still an answer: `manner`.**

**WHAT THE STATION DID WITH THE THREE, MEASURED BEFORE THIS WAS WRITTEN:**

    I stay home strictly if it rains    «strictly» hangs off the MATRIX, a second manner beside
                                        «home», unplaced — and IMPLY(rain, stay) claimed: «if it rains
                                        I stay home». The sentence says S → R, or R ↔ S; a WRONG CLAIM
    Even cats eat fish                  a manner box, «in an even manner»
    It is simply true                   likewise

**ABSTAIN IS A MEANING, AND IT IS WRITTEN AS ONE.** `compiled: {"kind": "abstain"}` — in the
vocabulary both rosters share (`db/0013`), so any row, of either table, may say it, and a reader asking
«what does this word compile to» gets the honest answer: *nothing I may write down*. The station
reads it as it reads every word it cannot place — the word is left UNPLACED, with the reason in
`abstained` — and then judges what remains by the exit bar's rule: what remains must be ENTAILED
(`E3.12.5` (1)). For a focus particle that has a consequence the particle's own row cannot carry and
the tree can: a particle whose meaning is not settled, over a condition or over a verb with a
condition in its reach, leaves the DIRECTION of that condition unsettled — «strictly if» may be
«only if» — so the conditional is withheld rather than claimed forward. That is logic
(`Compiler._focus`), and it is why the rows say `focus` in the `kind` column and `abstain` in
`compiled`: the first says what the word IS (a particle with an associate), the second what the
station may DO with it (nothing, yet).

**WHY THESE THREE ARE NOT SETTLED**, one line each, so the rows can be argued with:

    even       scalar and additive: «even cats eat fish» claims that cats do AND that they were the
               least likely — the second is not a truth function of anything the zip holds
    strictly   «strictly if» is «only if» to some and «if and only if» to others (the bench's
               «marginal English»), and «strictly speaking» is a frame, not a focus
    simply     «simply because» is exclusive («only because»), «it is simply true» an intensifier

**NO VOICE.** Nothing is said back as «even»: a word the station never wrote into a zip is never read
out of one, so no row here is `spoken`.

**Written by the 1st Officier on 2026-09-26, on the Captain's ruling of the same day. Nothing is
applied until the Captain says so.**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, AdverbKindDoc
from tk2.migrations import ensure_collections

ADVERB_VERSION = 5

#: The adverb kind these rows are — `db/0039`'s fifth kind, a name and not a roster.
FOCUS = "focus"

#: **THE MEANING «ABSTAIN»** — the station leaves the word unplaced and records why. A name in the
#: vocabulary both rosters share; which words carry it is the rows' business below.
ABSTAIN = {"kind": "abstain"}

_RULING = ("the Captain, 2026-09-26 (E3.12.5.9.3.1, replacing E3.12.5.9.12 (5)): keep the manner "
           "default; each focus word met gets its own row in the adverb kinds; where the meaning is "
           "not settled, the row says ABSTAIN")

#: form -> why its meaning is not settled. The three the ruling names, and no fourth.
UNSETTLED = {
    "even": "scalar and additive — «even cats eat fish» claims that cats do AND that they were the "
            "least likely, and the second is not a truth function of anything the zip holds",
    "strictly": "«strictly if» is «only if» to some readers and «if and only if» to others, and "
                "«strictly speaking» is a frame and not a focus",
    "simply": "«simply because» is exclusive, «it is simply true» an intensifier — two meanings and "
              "nothing in the tree to choose",
}


def build_adverbs(previous: list[dict]) -> list[dict]:
    out = []
    for row in previous:
        if row.get("version") != ADVERB_VERSION - 1:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = ADVERB_VERSION
        out.append(new)
    position = 1 + max(r["position"] for r in out)
    for form, why in UNSETTLED.items():
        out.append({
            "version": ADVERB_VERSION,
            "form": form,
            "kind": FOCUS,
            "compiled": dict(ABSTAIN),
            "source": _RULING,
            "note": why,
            "position": position,
            "spoken": False,
        })
        position += 1
    return out


def _previous(number: int, attribute: str):
    # **BY NUMBER**, never through `newest_migration_declaring` — that walks and loads every file in
    # `db/`, this one included, and `db/0013`'s first draft recursed until the stack died.
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == number), None)
    if found is None:
        raise RuntimeError(f"{number:04d} is gone — it holds the version this one extends")
    return getattr(found.load(), attribute)


ADVERB_KIND_ROWS = build_adverbs(_previous(39, "ADVERB_KIND_ROWS"))


def _meaning(row: dict) -> tuple:
    """An adverb row's VOICE — `Decompiler._key(None, compiled)`, `db/0035`'s key."""
    compiled = row.get("compiled") or {}
    return (None, tuple(sorted((k, str(v)) for k, v in compiled.items())), None, None)


def _check() -> None:
    earlier = [r for r in _previous(39, "ADVERB_KIND_ROWS") if r.get("version") == ADVERB_VERSION - 1]
    if len(ADVERB_KIND_ROWS) != len(earlier) + len(UNSETTLED):
        raise ValueError(f"this migration adds exactly the {len(UNSETTLED)} unsettled particles")
    if any({k: v for k, v in row.items() if k != "version"} !=
           {k: v for k, v in was.items() if k not in ("version", "_id")}
           for row, was in zip(ADVERB_KIND_ROWS, earlier)):
        raise ValueError("an existing adverb row moved — this migration only adds")
    added = ADVERB_KIND_ROWS[len(earlier):]
    if {r["form"] for r in added} != set(UNSETTLED) \
            or any(r["kind"] != FOCUS or r["compiled"] != ABSTAIN or r["spoken"] for r in added):
        raise ValueError("the rows added are not the three unsettled focus words, abstaining, mute")
    if len({r["position"] for r in ADVERB_KIND_ROWS}) != len(ADVERB_KIND_ROWS):
        raise ValueError("two adverb rows share a position")

    # **THE TABLE'S LAWS, RE-RUN IN FULL** (`db/0015`: a check travels with the data it guards). The
    # closed classes read by number — v21, the newest that declares them.
    closed = {row["form"] for row in _previous(39, "CLOSED_CLASS_ROWS")}
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

    # **ONE VOICE PER MEANING** — and «abstain» has none: nothing the station never wrote is said.
    spoken = [r for r in ADVERB_KIND_ROWS if r.get("spoken")]
    if len({_meaning(row) for row in spoken}) != len(spoken):
        raise ValueError("two flagged adverbs share a meaning — one of them would never be spoken")
    if any(r["compiled"] == ABSTAIN for r in spoken):
        raise ValueError("«abstain» is voiced — a meaning the station never writes has no voice")


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(AdverbKindDoc, ADVERB_KIND_ROWS)
