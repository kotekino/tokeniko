"""0008 — policy version 5: an opposition the resource never wrote down, and the name it carries.

**THE RULING (the Captain, 2026-08-26), made on the measured three readings.** WordNet states an
antonymy once, on one lemma of one pair, so `leave -> enter` can exist while `enter -> leave` does
not. From v5 R completes the pair — but only where it has nothing else to say, and the completed
cell says out loud that we inferred it.

His reasoning, in the shape the rows have to keep it: the bar reads IDENTICALLY under all three
readings (sixteen of eighteen pairs unmoved, and the two that move are FAR pairs that were already
right), so this was never a measurement question. It is whether this being may hold an opposition
the resource never typed. **It may** — `acquire -> lose`, `broad -> narrow`, `cease -> begin` are
true whether or not a lexicographer wrote the reverse — and the reading that admits them destroys
nothing and labels the inference forever.

**TWO ROWS, AND THEY ARE ONE DECISION.** The mode (`add_only`) and the weight of the relation it
mints (`antonym_inferred`, -1.00). Neither is meaningful alone, and the engine says so rather than
trusting this file: a policy declaring the mode without the weight is refused at `assert_coherent`
(a relation the walk produces and nobody weighted), and one declaring the weight without the mode
is refused just as loudly (a weight for a relation nothing produces). The pairing is a property of
the code, not a convention of the author.

**THE THIRD READING WAS ORDERED BECAUSE THE SECOND WENT WRONG.** `overwrite` — state the reverse
wherever an antonymy exists — added the same 143 cells and destroyed four stated ones doing it,
`dark.n -> day.n` among them: a holonym at +0.60 replaced by an antonym at -1.00, which is the very
cell the lemma-scope ruling of the same day had just repaired. `add_only` is the same completion
with that failure made impossible: a pair may hold an antonymy one way and something else the other,
and R is asymmetric precisely so it can carry both.

**WHAT MOVES.** R 49,965 -> **50,108** cells (+143, and NOTHING overwritten). Negatives 663 -> 806
(the four that `overwrite` also flipped are exactly the damage, and they do not happen here). Silent
rows 353 -> 346, the seven recovered dimensions all adjectives and adverbs — the two parts of speech
R is quietest about. Membership does not move: 3,095 words / 4,445 dimensions, the closure reading
glosses, which no reading of antonymy can touch. The fingerprints move, and v1-v4 keep theirs.

**WHAT DID NOT MOVE.** The weights, the curated vocabulary, the miner's guess, the alphabet, the
lemma scope, the seeds, the closure cuts and the bar. The rows below are `db/0007`'s own — read off
that file's declaration and re-stamped at version 5, notes and all.

**NOT APPLIED BY THE OFFICER.** This file is written and reported; the apply is the Captain's hand.
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, DictionaryPolicyDoc
from tk2.dictionary import policy, relations
from tk2.dictionary.config import DictionaryConfig, RelationPolicy
from tk2.migrations import ensure_collections

POLICY_VERSION = 5


def _version_4():
    """`db/0007`, loaded as the runner loads it — the chain every version since 0005 has used. The
    half of the policy that did not move is READ, never re-typed."""
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 7), None)
    if found is None:
        raise RuntimeError("migration 0007 is gone — it holds the policy version 5 carries forward")
    return found.load()


V4 = _version_4()


# ------------------------------------------------------------------------------------------------
# the two values that moved
# ------------------------------------------------------------------------------------------------

#: Complete a one-sided antonymy ONLY where R is silent for that ordered pair.
ANTONYM_SYMMETRY = relations.SYMMETRY_ADD_ONLY

#: What an inferred opposition is worth: exactly what a stated one is. The claim is the SAME claim —
#: `enter` and `leave` are opposed — and the only thing that differs is who noticed.
INFERRED_WEIGHT = -1.00

SYMMETRY_NOTE = (
    "how a ONE-SIDED antonymy is read. WordNet states an antonymy once, on one lemma of one pair, "
    "so `leave -> enter` can exist while `enter -> leave` does not. `stated` = leave it one-sided; "
    "`overwrite` = state the reverse always; `add_only` = complete the pair ONLY where R is silent "
    "for that ordered pair, as the separate relation `antonym_inferred`. RULED `add_only` by the "
    "Captain on 2026-08-26. MEASURED, all three over one key space: add_only writes 143 new cells "
    "and overwrites 0, against overwrite's 143 new and 4 DESTROYED — `dark.n -> day.n` (holonym "
    "+0.60 becoming antonym -1.00), `engage.v -> fire.v`, `get.v -> leave.v`, `go.v -> stop.v`. "
    "The first of those is the cell the lemma-scope ruling of the same day had just repaired, which "
    "is why overwrite was refused. Negatives 663 -> 806; silent rows 353 -> 346, and all seven "
    "recovered dimensions are adjectives and adverbs, the two parts of speech R is quietest about; "
    "membership unmoved at 3,095 words / 4,445 dimensions. THE BAR READS IDENTICALLY UNDER ALL "
    "THREE (16 of 18 pairs unmoved; `enter~leave` gains its reverse cell and `arrive~leave` moves "
    "-0.263 -> -0.258 as the norms grow), so this ruling rests on the PRINCIPLE and not on the bar: "
    "the question was never which reading measures better but whether this being may hold an "
    "opposition the resource never wrote down. It may — `acquire -> lose`, `broad -> narrow`, "
    "`cease -> begin` are true whether or not a lexicographer typed the reverse"
)

INFERRED_WEIGHT_NOTE = (
    "the weight of an opposition WE inferred rather than one WordNet stated — same sign, same "
    "strength, different name. It is NOT called `antonym`, because a cell whose whole contract is "
    "that it can say what made it must not answer «WordNet» when the answer is «we did»; the same "
    "principle keeps a curated cell distinguishable from a mined one. It is not `antonym_of` and it "
    "carries no `_reciprocal` suffix either: both of those already mean «the weaker reverse read of "
    "a directional relation» (`entailed_by` 0.60, `used_for_reciprocal` 0.60), and an inferred "
    "opposition is the SAME claim at the SAME strength, merely not written down. Minted only under "
    "the `add_only` reading, and only into a cell R had nothing else to say about"
)


# ------------------------------------------------------------------------------------------------
# the rows
# ------------------------------------------------------------------------------------------------

RELATIONS = RelationPolicy(
    # The new weight lands at the END of the declared order, which is also its PRECEDENCE: an
    # inferred opposition is believed last among equals. It can only ever occupy a cell nothing
    # else claimed, so the position never decides anything — and that is the honest place for it.
    weights=V4.RELATIONS.weights + ((relations.ANTONYM_INFERRED, INFERRED_WEIGHT),),
    curated=V4.RELATIONS.curated,
    reciprocal_weight=V4.RELATIONS.reciprocal_weight,
    cues=V4.RELATIONS.cues,
    defaults=V4.RELATIONS.defaults,
    lemma_scope=V4.RELATIONS.lemma_scope,
    antonym_symmetry=ANTONYM_SYMMETRY,
)

DECLARED = DictionaryConfig(
    closure=V4.DECLARED.closure,
    declared_seeds=V4.DECLARED.declared_seeds,
    bar=policy.snapshot_bar(),
    relations=RELATIONS,
    alphabet=V4.DECLARED.alphabet,
)

FAMILY_OF = {**V4.V3.FAMILY_OF, relations.ANTONYM_INFERRED: "lexical"}

POLICY_ROWS = policy.policy_rows_of(DECLARED, POLICY_VERSION, FAMILY_OF)

#: v4's reasons, carried with v4's values.
_CARRIED_NOTES = {(row["kind"], row["name"]): row["note"] for row in V4.POLICY_ROWS}

_NEW_NOTES = {
    (policy.KIND_RELATION_WEIGHT, relations.ANTONYM_INFERRED): INFERRED_WEIGHT_NOTE,
    (policy.KIND_RELATION_SETTING, "antonym_symmetry"): SYMMETRY_NOTE,
}

for _row in POLICY_ROWS:
    _key = (_row["kind"], _row["name"])
    # A KeyError here is the point, as it was in 0006 and 0007: every row of a curated policy
    # explains itself, and a kind that arrived without a reason should fail at import rather than
    # reach the database mute.
    _row["note"] = _NEW_NOTES[_key] if _key in _NEW_NOTES else _CARRIED_NOTES[_key]


# ------------------------------------------------------------------------------------------------
# what 0005 knew, still readable from the newest policy file
# ------------------------------------------------------------------------------------------------

STRUCTURAL_K = V4.STRUCTURAL_K
STRUCTURAL_SEEDS = V4.STRUCTURAL_SEEDS
derive_structural_seeds = V4.derive_structural_seeds


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(DictionaryPolicyDoc, POLICY_ROWS)
