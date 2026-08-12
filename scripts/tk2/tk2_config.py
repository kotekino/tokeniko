# tk2 / dictionary review — the ONE file you edit between iterations.
#
# Everything tunable lives here: the seeds, the relation weights, and the BAR. The three stages
# (tk2_subset / tk2_matrix / tk2_probe) read this and nothing else, so an iteration is a config edit
# plus two commands — never a code change.
#
# Requirement 12: THE BAR IS SET BEFORE THE MATRIX IS BUILT. Editing PAIRS after seeing a result is
# how a review talks itself into success; if a pair must change, change it and say so out loud.

import os

from dotenv import load_dotenv

# the body's .env lives in the package dir, not the repo root — load it here, before the first
# os.getenv below, so these scripts run from any working directory.
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tokeniko", ".env"))

# ------------------------------------------------------------------------------------------------
# databases — read-only on the body, writes ONLY to the tk2 sandbox
# ------------------------------------------------------------------------------------------------

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27018/?directConnection=true")
SRC_DB = os.getenv("MONGO_DB_NAME", "tokeniko")   # read-only: base + dictionary
TK2_DB = "tokeniko_tk2"                            # the sandbox; the guard refuses anything else

# ------------------------------------------------------------------------------------------------
# STAGE 1 — the cherry-picked subset
# ------------------------------------------------------------------------------------------------

# The Captain's method: reduce a base word's DEFINITION to base words only, then look for the places
# where the intersections are smallest — a set whose definitions never leave the set. Formally a
# CLOSED set in the definition digraph (defs(S) subset-of S); the minimal ones are the sink SCCs.
#
# His trivial example: me (not you) / you (not me) / not (negation) / negation (not) -> closed.

# Requirement 8: the sensitive families are in scope BY CONSTRUCTION, not by luck. Closure alone
# will happily return a clique of function words; these seeds force the verbs that select actions.
SEEDS_VOLITIONAL = ["want", "must", "try", "decide", "choose", "need", "wish", "intend", "refuse"]
SEEDS_MOTION     = ["go", "come", "walk", "run", "enter", "arrive", "leave", "land", "fall", "move"]
SEEDS_EFFECT     = ["eat", "food", "hungry", "sleep", "tired", "bed", "drink", "thirsty"]
SEEDS_IDENTITY   = ["me", "you", "not", "negation", "be", "same", "different"]

SEEDS = SEEDS_VOLITIONAL + SEEDS_MOTION + SEEDS_EFFECT + SEEDS_IDENTITY

# ...plus every word named in the BAR below. Run r1 scored only 12 of 18 pairs because `kill`,
# `water`, `swallow` were base words that the seed closure never reached: a subset that cannot score
# its own bar is not a test. This is requirement 12 enforced in code rather than by care.
def _bar_words():
    ws = []
    for a, b, _e, _w in PAIRS:
        for k in (a, b):
            w = k.rsplit(".", 1)[0] if k.rsplit(".", 1)[-1] in ("n", "v", "a", "r") else k
            if w not in ws:
                ws.append(w)
    return ws

# How far the seed closure is allowed to run before we call it exploded. The QM's stated counter is
# that `closed` and `sensitive` will fight: function words close cheaply, `eat` pulls in the world.
# This number is the instrument that MEASURES that fight rather than assuming it.
SEED_CLOSURE_MAX_DEPTH = 2
SEED_CLOSURE_MAX_SIZE = 400

# Which senses of a base word contribute its definition. "primary" = the first synset per POS (what
# the Jurassic build used); "all" = every sense (denser, noisier).
DEFINITION_SENSES = "primary"

# ------------------------------------------------------------------------------------------------
# STAGE 2 — the matrix
# ------------------------------------------------------------------------------------------------

# Requirement 9: the base must split by POS. A collapsed dimension merges two different relation
# sets — `cause` the noun and `cause` the verb do not have the same neighbours.
SPLIT_BY_POS = True

# Requirement 10: density comes from RELATIONS, never co-occurrence. Every weight below names a
# WordNet edge. `gloss_overlap` is the one co-occurrence-flavoured survivor from the Jurassic build,
# kept ONLY so the comparison is honest — set it to 0.0 to see the relations-only geometry.
#
# Set a weight to 0.0 to switch that relation off for a run. Provenance is stored per cell, so after
# a run you can ask which relation actually carried each value.
WEIGHTS = {
    # --- carried over from the Jurassic build (scripts/base.py) ---
    "identity":            1.0,    # X is X
    "synonym":             1.0,    # shared synset
    "antonym":            -1.0,    # lemma antonym  (the sign IS the antonym column-read primitive)
    "derivational":        0.9,    # able -> ability

    # --- NEVER MINED (the point of this review) ---
    "entails":             0.8,    # eat -> chew, swallow          (verb)
    "entailed_by":         0.6,    # the reverse read
    "causes":              0.85,   # kill -> die                   (verb)
    "caused_by":           0.6,
    "troponym":            0.7,    # eat -> devour, slurp          (verb hyponym = manner-of)
    "troponym_of":         0.7,
    "verb_group":          0.75,   # eat.v.01 <-> eat.v.02
    "similar_to":          0.8,    # hungry -> peckish, famished   (adj satellite)
    "attribute":           0.7,    # hot <-> temperature           (adj <-> noun)
    "also_see":            0.5,
    "meronym":             0.6,    # part/member/substance
    "holonym":             0.6,

    # --- taxonomy + the fallbacks ---
    "hypernym_1":          0.7,
    "hyponym_1":           0.7,
    "hypernym_2":          0.5,
    "wup":                 1.0,    # multiplier on the Wu-Palmer score, gated by WUP_FLOOR
    "gloss_overlap":       1.0,    # multiplier on the Jurassic jaccard*5 capped at 0.5
}

WUP_FLOOR = 0.65              # Jurassic threshold; below it Wu-Palmer contributes nothing
GLOSS_JACCARD_CAP = 0.5       # Jurassic cap
GLOSS_JACCARD_FLOOR = 0.1     # Jurassic noise floor

# Cross-POS cells: the Jurassic build compared same-POS only (its Wu-Palmer step did). Relations
# like `attribute` and `derivational` are inherently cross-POS — allowing them is the whole reason
# to split by POS in the first place.
ALLOW_CROSS_POS = True

# ------------------------------------------------------------------------------------------------
# STAGE 2b — THE TWO-MATRIX BASE  (the ruling that finding 4 forced: two layers, not one number)
# ------------------------------------------------------------------------------------------------

# Finding 4 of the 2026-08-12 review: `eat` and `food` have NO WordNet relation, so a relations-only
# matrix scores them 0.000 — requirement 2 (eat stays near food) and requirement 10 (density from
# relations, never co-occurrence) cannot both hold in ONE matrix. The prototype's answer is to stop
# blending them into a single float and build TWO collections over ONE key space:
#
#   R — base_relational      named WordNet edges only.  SIGNED (antonyms survive), sparse (~1.3%),
#                            accountable per cell.  Answers: opposition, entailment, causation,
#                            is-a, manner.
#   D — base_distributional  gloss overlap only.  Unsigned, dense (~25%), topical.
#                            Answers: aboutness, relatedness — the nearness `eat~food` lives in.
#
# A query consults the matrix that can honestly answer it, and the CLI always says WHICH one spoke.

# R takes every named relation in WEIGHTS except these two. `gloss_overlap` is co-occurrence, which
# is D's whole job. `wup` is excluded for a different reason — see MATRIX_WUP_NOTE below.
MATRIX_R_EXCLUDE = ("gloss_overlap", "wup")

# D takes gloss overlap, plus `identity` so a dimension still owns its own axis (a matrix whose
# diagonal is zero has no self-similarity and its cosines stop meaning what they look like).
MATRIX_D_INCLUDE = ("identity", "gloss_overlap")

# THE WUP DECISION, recorded here because the manifest quotes it and a later reader will ask.
# Wu-Palmer is dropped from BOTH matrices. It belongs to neither side of the seam: it is not a named
# edge (R's criterion — requirement 18 wants a cell to name the relation that made it, and "wup" names
# a *score over* the taxonomy, not a relation between the two words), and it is not co-occurrence
# (D's criterion). Keeping it would blur exactly the boundary this split exists to sharpen. It is a
# graded taxonomy proxy and is recoverable later as its own third layer if a question needs it.
MATRIX_WUP_NOTE = (
    "wup dropped from BOTH matrices: not a named edge (fails R's provenance criterion) and not "
    "co-occurrence (fails D's). Recoverable later as a separate graded-taxonomy layer."
)

# Requirement 15 — MEMBERSHIP IS A DEFECT TOO. These words are named by the bar or by the relations
# the review is about, and are NOT in the Jurassic 2925, so the edges that reach them are currently
# inexpressible (`eat entails swallow` has no target axis). The prototype adds them as dimensions.
# This is a legitimate move ONLY because it is declared: the builder records every one of them in the
# manifest under `added_words`, so no result can quietly rest on a word that was smuggled in.
BASE2_ADDED_WORDS = [
    ("want",     "the most volitional verb in English, and the bar tests want~need / want~refuse"),
    ("swallow",  "the target of `eat entails swallow` — the pair the bar declares NEAR"),
    ("chew",     "the second half of the same entailment; without it `effect eat` is half-blind"),
    ("runway",   "the bar's control pair tired.a~runway.n, and the «land on the runway» example"),
    ("negation", "the Captain's own closure example (me/not/you/negation) names it; not a base word"),
]

# The name of the built two-matrix base. Runs of the single-matrix instrument (r1, r2-nogloss) live
# in `base_candidate`/`runs` and are untouched; the two-matrix base has its own collections.
BASE2_NAME = "b1"


# ------------------------------------------------------------------------------------------------
# STAGE 3 — THE BAR  (declared before the matrix exists)
# ------------------------------------------------------------------------------------------------

# Each pair: (a, b, verdict, why). Verdict is FAR or NEAR. Keys may be bare words (any POS) or
# POS-qualified as `word.v`. Compounds (`land on the runway`) are layer two and NOT tested here —
# what IS tested is whether the single words carry enough to make the compound separable later.
PAIRS = [
    # --- the nearnesses we must NOT lose (Cap's refutation of the split-the-space proposal) ---
    ("eat.v",   "food.n",     "NEAR", "the Captain's line: eat and food are geometrically similar, do not lose it"),
    ("drink.v", "water.n",    "NEAR", "same shape, second witness"),
    ("sleep.v", "bed.n",      "NEAR", "the «land on your bed» -> sleep chain has to have a hook"),

    # --- the effect axis: what the Jurassic base cannot see ---
    ("eat.v",   "hungry.a",   "NEAR", "the effect is already NAMEABLE in the 2925 — so this is a wrong-VALUE test, not a missing-axis test"),
    ("sleep.v", "tired.a",    "NEAR", "same: effect nameable in base"),
    ("kill.v",  "die.v",      "NEAR", "pure `causes` edge — unreachable without the unmined relations"),
    ("eat.v",   "swallow.v",  "NEAR", "pure `entails` edge"),

    # --- POS collapse: the defect Cap found this session ---
    ("cause.n", "cause.v",    "NEAR", "similar, and the base cannot even ask the question today"),
    ("land.n",  "land.v",     "FAR",  "ground vs. touching down — the collapse that costs us"),
    ("state.n", "state.v",    "FAR",  "condition vs. to say"),

    # --- the volitional family must be resolvable against each other ---
    ("want.v",  "need.v",     "NEAR", "action selection reads these"),
    ("want.v",  "refuse.v",   "FAR",  "opposite volitional polarity"),

    # --- motion must not collapse into one blob ---
    ("arrive.v", "leave.v",   "FAR",  "opposite endpoints of the same motion"),
    ("walk.v",  "run.v",      "NEAR", "manner siblings"),
    ("enter.v", "leave.v",    "FAR",  "opposite direction"),

    # --- controls: things that must stay far, or a denser matrix is just noise ---
    ("eat.v",   "arrive.v",   "FAR",  "control — density must not smear everything together"),
    ("bed.n",   "cause.n",    "FAR",  "control"),
    ("tired.a", "runway.n",   "FAR",  "control"),
]

# The bar itself. A run PASSES a pair when it lands on the right side of these.
NEAR_FLOOR = 0.30      # a NEAR pair must reach at least this cosine
FAR_CEILING = 0.15     # a FAR pair must stay at or below this cosine
# And the separation that matters more than either absolute: every NEAR pair must out-score every
# FAR pair that shares a word with it. Absolute thresholds drift between runs; the ORDER should not.
REQUIRE_LOCAL_ORDER = True

# the bar's own words are seeds too (defined above, resolved here now that PAIRS exists)
SEEDS = SEEDS + [w for w in _bar_words() if w not in SEEDS]
