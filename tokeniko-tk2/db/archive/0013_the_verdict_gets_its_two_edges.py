"""0013 — policy version 9: NEAR, ABSTAIN, FAR. The bar's readings finally become verdicts.

**THE LAST RULING OF E1, AND THE ONE HELD BACK LONGEST.** Every reading in this epic was
threshold-free on purpose — cosine, cells, MUTE, local order — because a number fitted to the wrong
evidence is worse than no number. The prototype's 0.30/0.15 were calibrated at 983 dimensions and
were never inherited: measured at 4,445 against the eighteen-pair bar they got **5 of 14 decided
pairs WRONG**, and the reciprocal-0.60 justification they came with had already failed to reproduce
(`sleep~bed` was 0.353 at 983 dims and 0.154 here).

**THE SHAPE IS THREE-VALUED, and that is the ruling before any number is.** Two-valued was measured
and cannot be made to work: no single threshold decides all thirty-seven pairs, and forcing the
undecidable ones buys errors where a silence costs nothing. ABSTAIN is first-class everywhere else
in this project — it is the evaluator's own verdict, «half-understood is legal, wrongly-understood
is the sin» — and it is first-class here.

**FAR IS A THEOREM, NOT A CALIBRATION.** D is unsigned by construction, so nothing but R's sign can
put a reading below zero: a negative dual read IS a stated opposition, at first or second order.
Zero survives a rebuild, a re-scale and a change of dimensionality, which no fitted number does. It
is written as a row anyway, because a later ruling may want a margin below zero rather than zero
itself — and a threshold that lives in code is the defect the standing law of 2026-08-25 exists to
prevent.

**NEAR = +0.27, and it is the only fitted number here.** Measured against the grown bar under the
ruled walk (`structure = compiled`, `mix` 0.15): the zero-error frontier runs from **13 pairs
decided at +0.2698** up to 0 decided, and every configuration on it has a FAR ceiling at or below
zero. Dropping the floor to +0.2476 decides four more and gets one wrong. So the floor sits just
above the wall.

**THE WALL IS `compass.n ~ compass.v` AT +0.2668** — a declared FAR that reads nearer than 99.77% of
the base, over the same `derivational` cell that `land.n ~ land.v` sits on. It is the POS collapse D
still cannot resolve, and **the NEAR floor is fitted to that ONE pair**: eleven declared NEAR pairs
read below it and are what a safe floor cannot decide. If the collapse is ever fixed, this number is
re-measured and not inherited. That sentence is the point of writing it down.

**WHAT THE FLOOR ADMITS**, because a verdict is issued over a population and not over a bar:
23,000 pairs, 0.22% of the base, 48% of them with a real R cell — and **0.0% resting on nothing but
function words**, where before the structure ruling the same measurement read 60.6%. Twenty drawn at
random: `energy.n~vigor.n` +0.644, `conveyance.n~transfer.n` +0.553, `channel.v~transport.v` +0.585,
`quantify.v~weigh.v` +0.350. That reads like a dictionary rather than like noise, which is the
strongest thing that can honestly be said for a fitted threshold.

**ABSTAINING ON 24 OF 37 IS THE HONEST STATE OF THIS GEOMETRY**, not a weakness of the floors: R is
mute on seventeen of them. A floor that decided more would be inventing.

**WHAT MOVES.** Two rows. Everything else is v8's, read off `db/0012` and re-stamped with its notes.

**NOT APPLIED BY THE OFFICER OR THE QM.** Written and reported; the apply is the Captain's hand.
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, DictionaryPolicyDoc
from tk2.dictionary import policy
from tk2.dictionary.config import DictionaryConfig, ReadingPolicy
from tk2.migrations import ensure_collections

POLICY_VERSION = 9


def _version_8():
    """`db/0012`, loaded as the runner loads it — the chain every version since 0005 has used."""
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 12), None)
    if found is None:
        raise RuntimeError("migration 0012 is gone — it holds the policy version 9 carries forward")
    return found.load()


V8 = _version_8()


# ------------------------------------------------------------------------------------------------
# the two values that arrive
# ------------------------------------------------------------------------------------------------

READING = ReadingPolicy(mix=V8.READING.mix, near_floor=0.27, far_ceiling=0.0)


NEAR_FLOOR_NOTE = (
    "at or above this, the dual read's verdict is NEAR. RULED +0.27 by the Captain on 2026-09-10, "
    "and it is the ONLY fitted number in the acceptance function — the FAR edge is a theorem, see "
    "its row. MEASURED against the grown bar of thirty-seven under the ruled walk (structure "
    "compiled, mix 0.15): the zero-error frontier runs from 13 pairs decided at +0.2698 up to none "
    "decided, and dropping to +0.2476 decides four more and gets one WRONG. THE WALL IS "
    "`compass.n~compass.v` AT +0.2668 — a declared FAR reading nearer than 99.77% of the base, over "
    "the same derivational cell `land.n~land.v` sits on — so this floor is fitted to ONE pair, and "
    "eleven declared NEAR pairs read below it and are what it cannot decide. IF THE POS COLLAPSE IS "
    "EVER FIXED THIS NUMBER IS RE-MEASURED, NOT INHERITED. What it admits: 23,000 pairs, 0.22% of "
    "the base, 48% of them with a real R cell, and 0.0% resting on nothing but function words "
    "(60.6% before the structure ruling). The prototype's 0.30 is not its ancestor: measured here "
    "with 0.15 beneath it, that pair got 5 of 14 decided pairs wrong"
)

FAR_CEILING_NOTE = (
    "below this, the verdict is FAR. RULED 0.0, and it is a THEOREM rather than a calibration: D is "
    "unsigned by construction, so nothing but R's SIGN can put a dual read below zero — a negative "
    "reading IS a stated opposition, at first order or at second through a shared antonym column. "
    "Zero survives a rebuild, a re-scale and a change of dimensionality, which no fitted number "
    "does, and every zero-error configuration on the frontier has its FAR edge at or below it. "
    "Written as a ROW even so, for two reasons: a later ruling may want a margin below zero rather "
    "than zero itself (the five oppositions D still lifts — `left.a~right.a`, `high.a~low.a`, "
    "`black.n~white.n`, `foot.n~head.n`, `draw.v~push.v` — all had R barely below zero to begin "
    "with, and a margin is one way to answer them), and a threshold that lives in code is precisely "
    "the defect the standing law of 2026-08-25 exists to prevent. Between the two edges the verdict "
    "is ABSTAIN, which is first-class here as it is in the evaluator: 24 of the bar's 37 pairs fall "
    "in the band, and that is the honest state of a geometry whose R is mute on seventeen of them"
)


# ------------------------------------------------------------------------------------------------
# the rows
# ------------------------------------------------------------------------------------------------

DECLARED = DictionaryConfig(
    closure=V8.DECLARED.closure,
    declared_seeds=V8.DECLARED.declared_seeds,
    bar=V8.DECLARED.bar,
    relations=V8.DECLARED.relations,
    alphabet=V8.DECLARED.alphabet,
    distribution=V8.DECLARED.distribution,
    reading=READING,
)

FAMILY_OF = V8.FAMILY_OF

POLICY_ROWS = policy.policy_rows_of(DECLARED, POLICY_VERSION, FAMILY_OF)

_CARRIED_NOTES = {(row["kind"], row["name"]): row["note"] for row in V8.POLICY_ROWS}

_NEW_NOTES = {
    (policy.KIND_READING, "near_floor"): NEAR_FLOOR_NOTE,
    (policy.KIND_READING, "far_ceiling"): FAR_CEILING_NOTE,
}

for _row in POLICY_ROWS:
    _key = (_row["kind"], _row["name"])
    # A KeyError here is the point, as it was in 0006 through 0012: every row of a curated policy
    # explains itself, and a kind that arrived without a reason should fail at import rather than
    # reach the database mute.
    _row["note"] = _NEW_NOTES[_key] if _key in _NEW_NOTES else _CARRIED_NOTES[_key]


# ------------------------------------------------------------------------------------------------
# what 0005 knew, still readable from the newest policy file
# ------------------------------------------------------------------------------------------------

STRUCTURAL_K = V8.STRUCTURAL_K
STRUCTURAL_SEEDS = V8.STRUCTURAL_SEEDS
derive_structural_seeds = V8.derive_structural_seeds


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(DictionaryPolicyDoc, POLICY_ROWS)
