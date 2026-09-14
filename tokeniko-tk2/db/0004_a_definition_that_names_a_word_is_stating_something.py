"""0004 — policy version 12: gloss references become R cells, and a STATED CELL may decide.

**REQUIREMENT 2 WAS REFUTED AT SCALE AND THIS IS THE REPAIR.** «`eat` stays near `food`» was marked
PROVEN at +0.405 on the 975-dimension prototype; the E1 audit of 2026-09-14 measured it on the base
that was actually built and found **D cosine +0.0484, D DIRECT CELL 0.0000.** Their definitions share
no words at all. D measures *what two definitions SHARE*; the relation between eat and food is that
**eat's definition NAMES food** — a different question, which D was never going to answer:

    eat.v.01     take in solid FOOD
    bed.n.01     a piece of furniture that provides a place to SLEEP
    hungry.a.01  feeling a need or desire to EAT food

**Both edges the Captain curated by hand in August are instances of that one rule**, and the signal
was already being computed by `distribution.gloss_vectors` and thrown away for R's purposes.

**TWO THINGS ARRIVE, AND THE SECOND IS THE ONE THAT ACTUALLY CLOSES IT.**

**1. `gloss_reference` as an R relation** at **0.9** — near `synonym` rather than near `derivational`,
because a definitional reference is a strong, stated, quotable claim. Its reciprocal is **0.54**
(0.9 x the 0.60 convention requirement 20 already ruled for curated edges), and it is what carries
`sleep.v ~ bed.n`, where only *bed*'s gloss speaks.

**2. `cell_decides`** — a stated cell may now issue a verdict. Requirement 19 has always said a
verdict reads BOTH the cosine and the direct cell; the reader used the cell only to decide whether R
*spoke*, never what it *said*. That is why a mined `eat.v -> food.n` at 0.9 still abstained: one cell
among 6.8 gloss references per row barely moves a cosine.

**ONLY AN UNAMBIGUOUS REFERENCE MAY DECIDE.** `lexicon_words_in` keeps no tagger on purpose, so a
gloss word names every dimension it could be: «express in words» names `express.n/v/a/r`, of which
one is meant, and **69% of mined references are ambiguous that way.** Harmless for D, where overlap
is symmetric and the noise averages; not harmless for a cell that decides. So the ambiguous ones are
RECORDED — at their honest share, `weight / n` — under `gloss_reference_ambiguous`, which this
policy does not admit as a decider. They are evidence, and they are what a curator's hand promotes.

Measured against the alternative (splitting the weight and fitting a deciding floor): **both score 0
wrong; the split scores one pair better and costs three fitted numbers governing 31,086 edges on the
evidence of 37 bar pairs.** The Captain ruled the rule with one number over the rule with three.

**`derivational` MAY NOT DECIDE EITHER**, and it is the same category: it states «same root», not
«same meaning». It is exactly why `land.n~land.v`, `compass.n~compass.v` and `play.n~play.v` are
declared FAR and read positive. Both names are declared in `structural_relations`.

**REFERENCE CELLS DO NOT ENTER THE RELATIONAL COSINE**, and that is measured rather than preferred:
with them in the cosine and the reciprocal on, `land.n~land.v`, `state.n~state.v` and
`play.n~play.v` **all flip to a wrong NEAR**, because reciprocal references inflate POS-sibling
profiles. A reference is a claim about a PAIR, not a statement about a key's relational profile.

**THE MEASUREMENT, on the sealed build, under policy v11's separate reads:**

    baseline                                     13 decided ·  0 wrong · 24 abstain
    with gloss references, cell-first, v12       17 decided ·  0 wrong · 20 abstain

    eat.v ~ food.n        NEAR via cell  <-- REQUIREMENT 2, CLOSED
    eat.v ~ hungry.a      NEAR via cell  <-- the Captain's curated edge, MINED
    food.n ~ hungry.a     NEAR via cell  <-- a pair nobody curated
    bed.n ~ cause.n       ABSTAIN        <-- correctly NOT a false positive

`sleep.v ~ bed.n` stays open on purpose: «sleep» is two dimensions and the gloss does not say which,
so the mine records the claim and refuses to decide it. **That is the pair E1d T5's curation exists
for — which is where the Captain's own hand put it in August.**

**THE NUMBERS ARE NOT APPLIED UNTIL THE BASE IS REBUILT.** The cells arrive from a build; this row
set declares what a build must mine and how it is to be read. **Written and reported; the apply and
the rebuild are the Captain's hand.**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, DictionaryPolicyDoc
from tk2.dictionary import policy, references
from tk2.dictionary.config import DictionaryConfig, ReadingPolicy, RelationPolicy
from tk2.migrations import ensure_collections

POLICY_VERSION = 12

GLOSS_REFERENCE_WEIGHT = 0.9
GLOSS_REFERENCE_RECIPROCAL_WEIGHT = 0.54


def _previous():
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 3), None)
    if found is None:
        raise RuntimeError("0003 is gone — it holds the version this one carries forward")
    return found.load()


PREVIOUS = _previous()
_READING = PREVIOUS.DECLARED.reading
_RELATIONS = PREVIOUS.DECLARED.relations

#: Recorded, never a decider — so it needs a declared weight for the walk to name it by, and the
#: value is the BASE the honest share is taken from (`weight / n` per reference), not a weight any
#: single cell carries.
AMBIGUOUS_BASE_WEIGHT = GLOSS_REFERENCE_WEIGHT

RELATIONS = RelationPolicy(
    weights=(*_RELATIONS.weights,
             (references.GLOSS_REFERENCE, GLOSS_REFERENCE_WEIGHT),
             (references.GLOSS_REFERENCE_RECIPROCAL, GLOSS_REFERENCE_RECIPROCAL_WEIGHT),
             (references.GLOSS_REFERENCE_AMBIGUOUS, AMBIGUOUS_BASE_WEIGHT)),
    curated=_RELATIONS.curated,
    reciprocal_weight=_RELATIONS.reciprocal_weight,
    cues=_RELATIONS.cues,
    # `defaults` was dropped by the first draft of this file and the six `curation_default` rows
    # vanished with it — caught by counting rows per kind against v11 rather than by reading the
    # code. Every field is named here on purpose: a reconstruction that omits one is a version
    # silently un-declaring something the ledger already carried.
    defaults=_RELATIONS.defaults,
    lemma_scope=_RELATIONS.lemma_scope,
    antonym_symmetry=_RELATIONS.antonym_symmetry,
)

READING = ReadingPolicy(
    mix=_READING.mix,
    near_floor=_READING.near_floor,
    far_ceiling=_READING.far_ceiling,
    mode=_READING.mode,
    cell_decides=True,
    structural_relations=("derivational", references.GLOSS_REFERENCE_AMBIGUOUS),
    reference_relations=(references.GLOSS_REFERENCE,
                         references.GLOSS_REFERENCE_RECIPROCAL,
                         references.GLOSS_REFERENCE_AMBIGUOUS),
)

DECLARED = DictionaryConfig(
    closure=PREVIOUS.DECLARED.closure,
    declared_seeds=PREVIOUS.DECLARED.declared_seeds,
    bar=PREVIOUS.DECLARED.bar,
    relations=RELATIONS,
    alphabet=PREVIOUS.DECLARED.alphabet,
    distribution=PREVIOUS.DECLARED.distribution,
    reading=READING,
)

NOTES = {
    (policy.KIND_READING, "cell_decides"): (
        "whether a STATED CELL may issue a verdict on its own. RULED True at v12 (2026-09-14). "
        "Requirement 19 has always said a verdict reads BOTH the cosine and the direct cell, and "
        "the reader used the cell only to decide whether R SPOKE, never what it SAID — which is why "
        "a mined eat.v->food.n at 0.9 still abstained: one cell among 6.8 gloss references per row "
        "barely moves a cosine. Closing it is what finally satisfies requirement 2, refuted at scale "
        "by the E1 audit (D cosine +0.0484, D direct cell 0.0000 — their definitions share nothing)"
    ),
    (policy.KIND_READING, "structural_relations"): (
        "relations whose cells may NEVER decide, though they still build the cosine. `derivational` "
        "states 'same root', not 'same meaning', and is exactly why land.n~land.v, "
        "compass.n~compass.v and play.n~play.v are declared FAR and read positive. "
        "`gloss_reference_ambiguous` is a claim about one of several readings the gloss does not "
        "choose between: lexicon_words_in keeps no tagger on purpose, so 'express in words' names "
        "express.n/v/a/r and 69% of mined references are ambiguous that way. Harmless for D, where "
        "overlap is symmetric; not harmless for a cell that decides. Measured against the "
        "alternative of splitting the weight and fitting a deciding floor: both score 0 wrong, the "
        "split scores ONE pair better, and costs THREE fitted numbers governing 31,086 edges on the "
        "evidence of 37 bar pairs"
    ),
    (policy.KIND_READING, "reference_relations"): (
        "relations whose cells are claims about a PAIR rather than statements about a key's "
        "relational profile, and which therefore never enter the relational cosine. MEASURED, not "
        "preferred: with reference cells in the cosine and the reciprocal on, land.n~land.v, "
        "state.n~state.v and play.n~play.v ALL flip to a wrong NEAR, because reciprocal references "
        "inflate POS-sibling profiles"
    ),
    (policy.KIND_RELATION_WEIGHT, references.GLOSS_REFERENCE): (
        "'A's definition NAMES B' — stated, directional, accountable per cell, evidence quotable. "
        "0.9, near `synonym` rather than near `derivational`, because a definitional reference is a "
        "strong claim. Requirement 2's repair: eat.v.01 is 'take in solid FOOD'. The signal was "
        "already computed by distribution.gloss_vectors and thrown away for R's purposes"
    ),
    (policy.KIND_RELATION_WEIGHT, references.GLOSS_REFERENCE_RECIPROCAL): (
        "the back-reference, 0.9 x the 0.60 convention requirement 20 already ruled for curated "
        "edges, so a mined reference is shaped like the curated edges it sits beside. It is what "
        "carries the direction where only ONE gloss speaks"
    ),
    (policy.KIND_RELATION_WEIGHT, references.GLOSS_REFERENCE_AMBIGUOUS): (
        "recorded, never a decider. The stored value is the honest SHARE (weight / n) and this row "
        "is the base it is taken from: a claim spread over four readings is a quarter of a claim, "
        "and a number saying otherwise would hide the ambiguity inside an accurate-looking cell. "
        "sleep.v~bed.n is one of these — 'sleep' is two dimensions — which is why it stays open for "
        "the curator's hand rather than being decided by a guess"
    ),
}

FAMILY_OF = {row["name"]: row["family"]
             for row in PREVIOUS.POLICY_ROWS
             if row["version"] == PREVIOUS.POLICY_VERSION and row["kind"] == policy.KIND_SEED}

POLICY_ROWS = policy.policy_rows_of(DECLARED, POLICY_VERSION, FAMILY_OF)

_CARRIED = {(row["kind"], row["name"]): row["note"]
            for row in PREVIOUS.POLICY_ROWS if row["version"] == PREVIOUS.POLICY_VERSION}

for _row in POLICY_ROWS:
    _key = (_row["kind"], _row["name"])
    _row["note"] = NOTES.get(_key) or _CARRIED[_key]


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(DictionaryPolicyDoc, POLICY_ROWS)
