"""0002 — policy version 10: the NEAR floor moves to +0.28, and the coupling that moved it is named.

**A DEFECT, FOUND BY THE BENCH ON ITS FIRST RUN, AND IT WAS THE QM'S.** `compass.n ~ compass.v` is a
declared FAR and it read **+0.2721** against a NEAR floor of **+0.27** — so the standing policy called
it NEAR, and the bar read one wrong where the ruling that set the floor had measured zero.

**WHY, AND IT IS THE PART WORTH KEEPING.** The floor was fitted on 2026-09-10 to sit just above that
same pair, which then read +0.2668 — MEASURED ON A 4,445-DIMENSION BASE. The base that was applied has
**4,555** dimensions, because requirement 12 makes every bar word a seed and bar v2 (0011 of the
archived chain) added nineteen pairs whose words joined the closure. The base grew by 110 dimensions,
every row's norm changed with it, and the wall the floor was fitted to moved out from under it.

**THE BAR AND THE FLOORS ARE NOT INDEPENDENT.** That is the lesson and it is worth more than the
number: growing the bar changes MEMBERSHIP, membership changes every cosine, and a floor fitted before
the growth describes a base that no longer exists. Any future bar growth invalidates this row. The
order that works is: grow the bar → apply → re-measure the frontier → then rule the floor.

**THE NEW WINDOW, measured on the applied base.** Zero-error floors run from **+0.2843** upward; the
wall below is `compass.n~compass.v` at **+0.2721** and the lowest declared NEAR above it is
`kill.v~die.v` at +0.2843. **0.28 is chosen for the GAP** rather than for either endpoint — a floor
sitting exactly on the lowest NEAR is a floor that fails the moment that pair moves by a thousandth,
which is precisely how the last one failed. 12 of 37 pairs decided, 0 wrong.

**WHAT DOES NOT MOVE.** The FAR ceiling stays 0.0 and stays a theorem: D is unsigned, so nothing but
R's sign can put a reading below zero, and no measurement can move that. Only the fitted half moved,
which is the half that was always going to.

**NOT APPLIED BY THE QM.** Written and reported; the apply is the Captain's hand.
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, DictionaryPolicyDoc
from tk2.dictionary import policy
from tk2.dictionary.config import DictionaryConfig, ReadingPolicy
from tk2.migrations import ensure_collections

POLICY_VERSION = 10


def _version_9():
    """The baseline, which carries all nine versions the archived chain wrote."""
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 1), None)
    if found is None:
        raise RuntimeError("the baseline is gone — it holds the ledger this version carries forward")
    return found.load()


BASELINE = _version_9()

READING = ReadingPolicy(
    mix=BASELINE.DECLARED.reading.mix,
    near_floor=0.28,
    far_ceiling=BASELINE.DECLARED.reading.far_ceiling,
)

NEAR_FLOOR_NOTE = (
    "at or above this, the dual read's verdict is NEAR. RE-RULED +0.27 -> +0.28 on 2026-09-10, "
    "hours after the first value, because the first value was WRONG and the bench caught it: "
    "`compass.n~compass.v` is a declared FAR and read +0.2721 against a floor of +0.27, so the "
    "policy called it NEAR. THE FLOOR HAD BEEN FITTED TO A BASE THAT NO LONGER EXISTED — that same "
    "pair read +0.2668 on the 4,445-dimension base the frontier was measured on, and the APPLIED "
    "base has 4,555 dimensions because requirement 12 makes every bar word a seed and bar v2 added "
    "nineteen pairs whose words joined the closure. THE BAR AND THE FLOORS ARE COUPLED: growing the "
    "bar changes membership, membership changes every cosine, and a floor fitted before the growth "
    "describes a base that is gone. The order that works is grow the bar -> apply -> re-measure the "
    "frontier -> rule the floor, and ANY FUTURE BAR GROWTH INVALIDATES THIS ROW. Re-measured on the "
    "applied base: zero-error floors run from +0.2843 up, the wall below is `compass.n~compass.v` at "
    "+0.2721, and 0.28 is chosen for the GAP between them rather than for either endpoint — a floor "
    "sitting exactly on the lowest declared NEAR (`kill.v~die.v`, +0.2843) is a floor that fails "
    "when that pair moves by a thousandth, which is how the last one failed. 12 of 37 decided, "
    "0 wrong. The FAR ceiling did not move and cannot: it is a theorem, not a fit"
)


DECLARED = DictionaryConfig(
    closure=BASELINE.DECLARED.closure,
    declared_seeds=BASELINE.DECLARED.declared_seeds,
    bar=BASELINE.DECLARED.bar,
    relations=BASELINE.DECLARED.relations,
    alphabet=BASELINE.DECLARED.alphabet,
    distribution=BASELINE.DECLARED.distribution,
    reading=READING,
)

#: The families the newest carried version filed its rows under, read off the rows themselves — the
#: baseline holds the ledger rather than a `FAMILY_OF` table, and a second copy typed here would be
#: a family map that could disagree with the rows it describes.
FAMILY_OF = {row["name"]: row["family"]
             for row in BASELINE.POLICY_ROWS
             if row["version"] == BASELINE.POLICY_VERSION and row["kind"] == policy.KIND_SEED}

POLICY_ROWS = policy.policy_rows_of(DECLARED, POLICY_VERSION, FAMILY_OF)

_CARRIED = {(row["kind"], row["name"]): row["note"]
            for row in BASELINE.POLICY_ROWS if row["version"] == BASELINE.POLICY_VERSION}

for _row in POLICY_ROWS:
    _key = (_row["kind"], _row["name"])
    _row["note"] = (NEAR_FLOOR_NOTE if _key == (policy.KIND_READING, "near_floor")
                    else _CARRIED[_key])


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(DictionaryPolicyDoc, POLICY_ROWS)
