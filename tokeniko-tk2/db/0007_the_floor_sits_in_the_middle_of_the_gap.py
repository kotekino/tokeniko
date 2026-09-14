"""0007 — policy version 14: the NEAR floor moves from +0.28 to +0.15, fitted to the base that exists.

**THE ORDER THAT WORKS, FOLLOWED THIS TIME.** `db/0002` wrote down the lesson after the floor had been
fitted to a base that no longer existed: *grow the bar → apply → rebuild → re-measure the frontier →
then rule the floor.* Requirement 16's repair (`db/0006`, policy v13) moved the wall, and the Captain
ruled that the floor wait for the rebuild. Migrations 0003–0006 were applied on 2026-09-14, the base
was rebuilt as `969766250c02`, read back whole against all four seals — and only then was the floor
measured.

**WHY IT CAN MOVE AT ALL.** `compass.n~compass.v` is a declared FAR and it was the wall `db/0002`
fitted +0.28 against, at +0.2721. It read positive because `derivational` was mined across every sense
of the word; mined at primary-sense resolution (v13) it reads **+0.095**.

**THE MEASUREMENT, through the verdict reader, on the stored build `969766250c02`, policy v13 from the
body's own rows, bar v2 (37 pairs):**

    floor   decided  wrong
    0.05      20       1    compass.n~compass.v
    0.08      19       1    compass.n~compass.v
    0.10–0.20 19       0
    0.22      18       0    walk.v~run.v falls below
    0.25–0.28 17       0

**THE FLOOR GOVERNS ONE GAP**, and both walls are named:

    below   compass.n~compass.v   declared FAR    +0.0948
    above   walk.v~run.v          declared NEAR   +0.2116

**0.15 IS CHOSEN FOR THE MIDDLE OF THE GAP**, with about 0.055 of room below and 0.062 above — not
for either endpoint. That is `db/0002`'s other lesson: the floor it replaced sat 0.0079 above a FAR
pair, and failed the first time the base moved by less than that.

**WHAT IT DECIDES.** At 0.15, `walk.v~run.v` (+0.212) and `buy.n~buy.v` (+0.246) read NEAR, and
`compass` and `land` stay ABSTAIN. **19 of 37 decided, 0 wrong** — against 13 when the E1 audit
opened E1d.

**WHAT DOES NOT MOVE.** The FAR ceiling stays 0.0: a theorem, not a fit. Under separate reads only R
is read, so a reading below zero is the resource's own statement of opposition.

**NO REBUILD IS OWED.** The floor is a READING of the base, not a property of it — `db/0002` moved it
the same way. The manifest of `969766250c02` records policy v13; the dirty-check will name v14 as
having moved, and it moved the reading and nothing the build wrote.

**ANY FUTURE CHANGE TO MEMBERSHIP OR TO R INVALIDATES THIS ROW.** Growing the bar makes every bar word
a seed, so it moves membership; a new relation moves R. Either way, re-measure before trusting 0.15.

**Applied by the QM on the Captain's explicit order, 2026-09-14: «0.15, write 0007 and apply it».**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, DictionaryPolicyDoc
from tk2.dictionary import policy
from tk2.dictionary.config import DictionaryConfig, ReadingPolicy
from tk2.migrations import ensure_collections

POLICY_VERSION = 14
NEAR_FLOOR = 0.15


def _previous():
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 6), None)
    if found is None:
        raise RuntimeError("0006 is gone — it holds the version this one carries forward")
    return found.load()


PREVIOUS = _previous()
_READING = PREVIOUS.DECLARED.reading

# Every field named, on purpose — `db/0004`'s first draft dropped one by rebuilding field by field.
READING = ReadingPolicy(
    mix=_READING.mix,
    near_floor=NEAR_FLOOR,
    far_ceiling=_READING.far_ceiling,
    mode=_READING.mode,
    cell_decides=_READING.cell_decides,
    structural_relations=_READING.structural_relations,
    reference_relations=_READING.reference_relations,
)

DECLARED = DictionaryConfig(
    closure=PREVIOUS.DECLARED.closure,
    declared_seeds=PREVIOUS.DECLARED.declared_seeds,
    bar=PREVIOUS.DECLARED.bar,
    relations=PREVIOUS.DECLARED.relations,
    alphabet=PREVIOUS.DECLARED.alphabet,
    distribution=PREVIOUS.DECLARED.distribution,
    reading=READING,
)

NEAR_FLOOR_NOTE = (
    "at or above this, R's cosine reads NEAR when no stated cell decides. RE-RULED +0.28 -> +0.15 on "
    "2026-09-14, FITTED TO THE BASE THAT EXISTS: migrations 0003-0006 applied, the base rebuilt as "
    "969766250c02 and read back whole against all four seals, and only then measured — the order "
    "db/0002 wrote down after its own floor had been fitted to a base that no longer existed. "
    "compass.n~compass.v (declared FAR) was the wall +0.28 was fitted against, at +0.2721; with "
    "derivational mined at primary-sense resolution (v13) it reads +0.0948. The floor governs one gap: "
    "compass.n~compass.v FAR +0.0948 below, walk.v~run.v NEAR +0.2116 above. Swept through the verdict "
    "reader: 0.10-0.20 all decide 19 of 37 with 0 wrong; 0.08 gets compass wrong; 0.22 loses walk~run. "
    "0.15 is chosen for the MIDDLE of the gap (~0.055 below, ~0.062 above), never an endpoint — the "
    "floor it replaces sat 0.0079 above a FAR pair and failed the first time the base moved. At 0.15 "
    "walk.v~run.v and buy.n~buy.v read NEAR. Any change to membership or to R invalidates this row"
)

FAMILY_OF = {row["name"]: row["family"]
             for row in PREVIOUS.POLICY_ROWS
             if row["version"] == PREVIOUS.POLICY_VERSION and row["kind"] == policy.KIND_SEED}

POLICY_ROWS = policy.policy_rows_of(DECLARED, POLICY_VERSION, FAMILY_OF)

_CARRIED = {(row["kind"], row["name"]): row["note"]
            for row in PREVIOUS.POLICY_ROWS if row["version"] == PREVIOUS.POLICY_VERSION}

for _row in POLICY_ROWS:
    _key = (_row["kind"], _row["name"])
    _row["note"] = (NEAR_FLOOR_NOTE if _key == (policy.KIND_READING, "near_floor")
                    else _CARRIED[_key])


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(DictionaryPolicyDoc, POLICY_ROWS)
