"""0006 — policy version 13: `derivational` is mined at PRIMARY-SENSE resolution. Requirement 16.

**REQUIREMENT 16, OPEN SINCE 2026-08-12.** *«The POS split is necessary and NOT sufficient —
`land.n~land.v` still 0.410 split, re-merged by `derivational`. The fix (down-weighting that edge)
is OPEN, a value review, not an addition.»*

**THE PROPOSED FIX WAS MEASURED IMPOSSIBLE.** The bar declares seven POS siblings, and
`derivational` holds for all seven: `fast` · `buy` · `cause` NEAR, `compass` · `land` · `play` ·
`state` FAR. A weight is a monotone rescale — every pair moves together and the ORDER never changes —
and `compass.n~compass.v` (FAR) sits above `buy` and `cause` (both NEAR) at every scale swept from
0.25 to 2.0. No weight separates them.

**A D THRESHOLD FAILED TOO.** It separated the seven by a gap of 0.020 — and across all 1,626 sibling
pairs in the base that threshold lands on the POPULATION MEDIAN (0.0185), with 46.4% of pairs above
it. Seven pairs were thin evidence; the whole population said so.

**THE DEFECT IS A RESOLUTION MISMATCH.** The closure reads `senses = "primary"`, so a base dimension
IS its primary sense. `derivational` was mined across EVERY sense of the word. WordNet states
derivation between LEMMAS OF SENSES and already knows the answer:

    cause   NEAR   cause.n.01   <-> cause.v.01     LINKED
    fast    NEAR   fast.n.01    <-> fast.v.01      LINKED
    buy     NEAR   bargain.n.02 <-> buy.v.01       LINKED
    land    FAR    land.n.01    <-> land.v.01      not linked
    compass FAR    compass.n.01 <-> compass.v.01   not linked
    play    FAR    play.n.01    <-> play.v.01      not linked
    state   FAR    state.n.01   <-> state.v.01     not linked

Over every POS-sibling pair in the base: **24.1% linked · 75.9% not · 0% unanswerable.** A binary
fact the resource states, with no threshold and no fitted number. That is requirement 16's own
sentence coming true: the split happened at the KEY level while the edge kept being mined word-wide.

**WHAT IT DOES, measured on the sealed build with cells filtered (an APPROXIMATION of a rebuild):**
4,198 of 5,964 `derivational` cells are mined at the wrong resolution. `land.n~land.v` +0.167 ->
+0.034 · `compass.n~compass.v` +0.273 -> +0.095 · `play.n~play.v` +0.124 -> 0.000.

**`compass` WAS THE WALL THE NEAR FLOOR WAS FITTED AGAINST** (`db/0002`). With it gone, the same
approximation puts the best zero-wrong floor at **0.10, on a plateau that holds to 0.20**, deciding
19 of 37 with everything E1d built — against 0.28 on a knife-edge.

**THE FLOOR DOES NOT MOVE IN THIS FILE, and that is the Captain's ruling rather than caution for its
own sake.** The 0.10 is measured on an approximation — cells dropped from a stored matrix — while a
real rebuild re-runs the walk, and cell WINNERS can change. `db/0002`'s lesson is exactly this: a
floor must be fitted to the base that actually exists. Declare the mining fix → apply → rebuild →
re-measure the frontier → then rule the floor. Until then 0.28 stands and merely costs abstentions.

**NOT APPLIED BY THE QM.** Written and reported; the apply and the rebuild are the Captain's hand.
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, DictionaryPolicyDoc
from tk2.dictionary import policy
from tk2.dictionary.config import DERIVATIONAL_PRIMARY_SENSE, DictionaryConfig, RelationPolicy
from tk2.migrations import ensure_collections

POLICY_VERSION = 13


def _previous():
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 4), None)
    if found is None:
        raise RuntimeError("0004 is gone — it holds the version this one carries forward")
    return found.load()


PREVIOUS = _previous()
_RELATIONS = PREVIOUS.DECLARED.relations

# EVERY field named, on purpose: the first draft of `db/0004` rebuilt this object field by field,
# dropped `defaults`, and silently un-declared six rows. A test now counts kinds across versions.
RELATIONS = RelationPolicy(
    weights=_RELATIONS.weights,
    curated=_RELATIONS.curated,
    reciprocal_weight=_RELATIONS.reciprocal_weight,
    cues=_RELATIONS.cues,
    defaults=_RELATIONS.defaults,
    lemma_scope=_RELATIONS.lemma_scope,
    antonym_symmetry=_RELATIONS.antonym_symmetry,
    derivational_resolution=DERIVATIONAL_PRIMARY_SENSE,
)

DECLARED = DictionaryConfig(
    closure=PREVIOUS.DECLARED.closure,
    declared_seeds=PREVIOUS.DECLARED.declared_seeds,
    bar=PREVIOUS.DECLARED.bar,
    relations=RELATIONS,
    alphabet=PREVIOUS.DECLARED.alphabet,
    distribution=PREVIOUS.DECLARED.distribution,
    reading=PREVIOUS.DECLARED.reading,
)

RESOLUTION_NOTE = (
    "AT WHICH SENSE RESOLUTION `derivational` is mined. RULED `primary_sense` on 2026-09-14, "
    "closing requirement 16 (open since 2026-08-12). THE DEFECT WAS A RESOLUTION MISMATCH: the "
    "closure reads senses='primary', so a dimension IS its primary sense, while `derivational` was "
    "mined across EVERY sense of the word. WordNet states derivation between lemmas of senses and "
    "already knows land.n.01 is not derived from land.v.01. MEASURED over all 1,626 POS-sibling pairs: "
    "24.1% linked at primary resolution, 75.9% not, 0% unanswerable; on the bar it separates all "
    "seven declared siblings — cause/fast/buy NEAR linked, land/compass/play/state FAR unlinked — "
    "with no threshold. Requirement 16's own proposed fix, down-weighting the edge, was measured "
    "IMPOSSIBLE: a weight is a monotone rescale and compass.n~compass.v (FAR) sits above buy and "
    "cause (NEAR) at every scale. A D threshold also failed: it landed on the population median "
    "(0.0185) with 46.4% of sibling pairs above it. On an approximation of the rebuild, 4,198 of 5,964 "
    "derivational cells go, compass.n~compass.v falls +0.273 -> +0.095, and the best zero-wrong NEAR "
    "floor moves 0.28 -> 0.10 on a plateau to 0.20 — but THE FLOOR IS NOT MOVED HERE: it is ruled "
    "after the rebuild, against the base that actually exists (db/0002's lesson)"
)

FAMILY_OF = {row["name"]: row["family"]
             for row in PREVIOUS.POLICY_ROWS
             if row["version"] == PREVIOUS.POLICY_VERSION and row["kind"] == policy.KIND_SEED}

POLICY_ROWS = policy.policy_rows_of(DECLARED, POLICY_VERSION, FAMILY_OF)

_CARRIED = {(row["kind"], row["name"]): row["note"]
            for row in PREVIOUS.POLICY_ROWS if row["version"] == PREVIOUS.POLICY_VERSION}

for _row in POLICY_ROWS:
    _key = (_row["kind"], _row["name"])
    _row["note"] = (RESOLUTION_NOTE if _key == (policy.KIND_RELATION_SETTING, "derivational_resolution")
                    else _CARRIED[_key])


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(DictionaryPolicyDoc, POLICY_ROWS)
