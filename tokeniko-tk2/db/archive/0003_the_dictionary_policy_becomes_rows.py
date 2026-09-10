"""0003 — the dictionary's policy leaves the code and becomes rows.

The standing law of 2026-08-25, applied to E1: the seeds, the closure cuts and the acceptance bar
are CURATION — «authorized judgment, as complete as we can make it», grown generated-then-curated
and never finished — and «a category-2 set stated in code is a defect even when its contents are
correct». Until this migration they were `tk2/dictionary/config.py`'s `DECLARED_SEEDS`,
`ClosurePolicy`'s defaults and `BAR_PAIRS`. After it they are `dictionary_policy` and
`dictionary_bar`, and the module holds only their shape.

**NOTHING IS CHANGED HERE.** Every value below is the one committed at `1e7cad3` (E1 T2b), carried
across character for character — the seed families in their declared order, `max_depth=2`,
`max_size=400`, `senses="primary"`, and the eighteen bar pairs with their reasons verbatim. The
Captain rules on the values themselves in the next task, and a value edited in the same breath as
the mechanism would have destroyed the comparison he is about to make: the whole claim of this
migration is that the base it produces is byte-identical to the one T2b measured, and
`tests/test_dictionary_policy.py` holds that claim as a regression against the fingerprint
`79fdfa9c…`.

Version 1 of both, and version is not decoration. A change to any policy entry is version 2 written
WHOLE, never an edit of these rows: the manifest's promise is that a recorded fingerprint identifies
the policy a past build actually ran, and a version edited in place makes every earlier manifest row
a description of something that no longer exists. The bar is different in kind and says so in its
own table — it is APPEND-mostly, so its version 2 will be these eighteen rows plus the nineteenth.
"""

from tk2.core.models import ALL_MODELS, LEDGER_MODELS, DictionaryBarDoc, DictionaryPolicyDoc
from tk2.dictionary import policy
from tk2.dictionary.config import BarPair, ClosurePolicy, DictionaryConfig
from tk2.migrations import ensure_collections

POLICY_VERSION = 1
BAR_VERSION = 1

# ------------------------------------------------------------------------------------------------
# THE SEEDS — requirement 8: the sensitive families are in scope BY CONSTRUCTION, not by luck
# ------------------------------------------------------------------------------------------------

# Closure alone will happily return a clique of function words. These force the verbs that select
# actions into every subset, whatever the definition digraph happens to feel like doing. The FAMILY
# travels with each word into its row, because the family is the argument for the word being there.
SEED_FAMILIES = {
    "volitional": ("want", "must", "try", "decide", "choose", "need", "wish", "intend", "refuse"),
    "motion": ("go", "come", "walk", "run", "enter", "arrive", "leave", "land", "fall", "move"),
    "effect": ("eat", "food", "hungry", "sleep", "tired", "bed", "drink", "thirsty"),
    "identity": ("me", "you", "not", "negation", "be", "same", "different"),
}

#: The declared order, which is hashed as a list and must survive the move.
DECLARED_SEEDS = tuple(word for family in SEED_FAMILIES.values() for word in family)

FAMILY_OF = {word: family for family, words in SEED_FAMILIES.items() for word in words}

# ------------------------------------------------------------------------------------------------
# THE CLOSURE CUTS
# ------------------------------------------------------------------------------------------------

# `max_size = 400` is carried across as it stands and is KNOWN to be overshot — the base lands at
# 1,220 words because the cap admits a whole ring or none of it, and a ring lands whole. That is
# the Captain's to rule on, next; this migration's job is to put the number where he can move it.
CLOSURE = ClosurePolicy(max_depth=2, max_size=400, senses="primary")

# ------------------------------------------------------------------------------------------------
# THE BAR — declared before anything is built (requirement 12)
# ------------------------------------------------------------------------------------------------

# Carried from the review's declaration, unedited. Compounds (`land on the runway`) are layer two
# and NOT tested here; what IS tested is whether the single words carry enough to make the compound
# separable later. The grouping comments are the bar's own argument and travel as the row order.
BAR_PAIRS = (
    # --- the nearnesses we must NOT lose ---
    BarPair("eat.v", "food.n", "NEAR", "the Captain's line: eat and food are geometrically similar, do not lose it"),
    BarPair("drink.v", "water.n", "NEAR", "same shape, second witness"),
    BarPair("sleep.v", "bed.n", "NEAR", "the «land on your bed» -> sleep chain has to have a hook"),
    # --- the effect axis: what the Jurassic base cannot see ---
    BarPair("eat.v", "hungry.a", "NEAR", "the effect is already NAMEABLE in the 2925 — a wrong-VALUE test, not a missing-axis test"),
    BarPair("sleep.v", "tired.a", "NEAR", "same: effect nameable in base"),
    BarPair("kill.v", "die.v", "NEAR", "pure `causes` edge — unreachable without the unmined relations"),
    BarPair("eat.v", "swallow.v", "NEAR", "pure `entails` edge"),
    # --- POS collapse ---
    BarPair("cause.n", "cause.v", "NEAR", "similar, and the base cannot even ask the question today"),
    BarPair("land.n", "land.v", "FAR", "ground vs. touching down — the collapse that costs us"),
    BarPair("state.n", "state.v", "FAR", "condition vs. to say"),
    # --- the volitional family must be resolvable against each other ---
    BarPair("want.v", "need.v", "NEAR", "action selection reads these"),
    BarPair("want.v", "refuse.v", "FAR", "opposite volitional polarity"),
    # --- motion must not collapse into one blob ---
    BarPair("arrive.v", "leave.v", "FAR", "opposite endpoints of the same motion"),
    BarPair("walk.v", "run.v", "NEAR", "manner siblings"),
    BarPair("enter.v", "leave.v", "FAR", "opposite direction"),
    # --- controls: things that must stay far, or a denser matrix is just noise ---
    BarPair("eat.v", "arrive.v", "FAR", "control — density must not smear everything together"),
    BarPair("bed.n", "cause.n", "FAR", "control"),
    BarPair("tired.a", "runway.n", "FAR", "control"),
)

# ------------------------------------------------------------------------------------------------
# the rows
# ------------------------------------------------------------------------------------------------

#: The policy exactly as `config.py` held it, so the rows are read OFF the declaration rather than
#: retyped beside it — the one way to carry a set across a medium without a transcription error.
DECLARED = DictionaryConfig(closure=CLOSURE, declared_seeds=DECLARED_SEEDS, bar=BAR_PAIRS)

POLICY_ROWS = policy.policy_rows_of(DECLARED, POLICY_VERSION, FAMILY_OF)
BAR_ROWS = policy.bar_rows_of(BAR_PAIRS, BAR_VERSION)

#: The notes are the reasons the rows exist, in the medium the rows have for them. A curated value
#: with no reason attached is a value nobody can later argue with (`ParamDoc.note`'s argument).
CLOSURE_NOTES = {
    "max_depth": "the depth cut: how many rings the seed closure expands. At 2 the word `right` sits "
                 "exactly one ring outside the subset — see SeedClosure.one_ring_past",
    "max_size": "the size cap. A ring is admitted whole or not at all, so this is overshot by "
                "construction: the 2026-08-25 base lands at 1,220 words under a cap of 400",
    "senses": "which senses of a word contribute its definition — `primary` (first synset per POS, "
              "what the Jurassic build used) or `all` (denser, noisier)",
}

for _row in POLICY_ROWS:
    if _row["kind"] == policy.KIND_CLOSURE:
        _row["note"] = CLOSURE_NOTES[_row["name"]]
    else:
        _row["note"] = f"seed, {_row['family']} family — requirement 8: in scope by construction"


def up(writer, db) -> None:
    # The three tables are new since 0001 created the world, so their shape has to be made here.
    # The ledger is included and is deliberately not in `ALL_MODELS` — see `LEDGER_MODELS`.
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS])

    writer.insert_many(DictionaryPolicyDoc, POLICY_ROWS)
    writer.insert_many(DictionaryBarDoc, BAR_ROWS)
