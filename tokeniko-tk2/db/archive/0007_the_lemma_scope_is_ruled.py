"""0007 — policy version 4: whose lemma may speak, ruled `word` and written down.

**THE RULING (the Captain, 2026-08-26), made on the measured A/B.** Antonymy and derivation are the
two relations WordNet states between LEMMAS rather than between synsets. Until now a dimension
inherited them from every word it shares a synset with — `eat` carried `corrode`'s derivations,
`refuse` carried `reject`'s antonym, `abstract.v` was given a derivational edge to `sugar.n` lent by
`cabbage`. From v4 a dimension states only what the resource states of ITS OWN lemma.

His reasoning, kept verbatim in shape because the rows are where it has to survive: the synset-wide
reading **asserts edges WordNet never stated**; the 257 borrowed negatives are unaudited and at
least one is provably wrong; and **a wrong negative is worse than silence** — wrongly-understood is
the sin, ABSTAIN is first-class. What the narrow reading loses (`eat~food`, which fell from +0.048
to nothing) was never a relation at all: it is co-occurrence, and co-occurrence is D's job by
construction (requirement 10).

**IT IS A ROW BECAUSE IT IS CONTENT.** Both tests of the standing law say so — changing it changes
what the rows SAY and not the shape of anything, and evidence is exactly what revised it. So the
adapter no longer holds a default at all: a `WordNetProvider` built without a scope may mine glosses
and may not mine relations (`LemmaScopeUndeclared`), which is what keeps a value in code from
answering quietly on a day the rows are silent.

**WHAT MOVES AND WHAT DOES NOT.** Measured before and after, on this same policy:

  - MEMBERSHIP DOES NOT MOVE. The closure reads GLOSSES, which the scope cannot touch: 68,779
    lexicon words -> 3,095 closure words -> 4,445 dimensions, identical under both readings, with
    the bar's 23 words inside and `right` in.
  - R MOVES: 56,599 cells -> **49,965** (-6,634, and 0 cells gained: the narrow reading is a strict
    subset). Negatives 920 -> **663** (-257). Silent rows 318 -> **353** (+35, of which 27 are
    adjectives). `derivational` 12,296 -> 5,870; `antonym` 920 -> 663; every synset-to-synset
    relation is untouched. 49 cells change WINNER, because a borrowed 0.90 was masking a weaker real
    relation — `action.n -> active.a` is `attribute` and was reading as `derivational`.
  - THE WITNESS THE RULING NAMES: **`dark.n -> day.n` was an antonym at -1.00, lent by `night`**,
    and is a `holonym` at +0.60 once the borrowing stops. A borrowed opposition was overriding a
    stated part-of, with the sign — the primitive the whole matrix is signed for — pointing the
    wrong way.
  - THE FINGERPRINTS MOVE, all three, and that is the mechanism working: v4 is a different policy
    and hashes differently. v1, v2 and v3 are untouched and still hash as they did, so every
    manifest row naming one keeps meaning what it meant. `config.RELATION_RULES` deliberately does
    NOT move: the scope LEFT the code law and became a policy value, so the config fingerprint now
    covers it directly and a bump would claim the code changed its mind about something it no
    longer decides.

**WHAT DID NOT MOVE.** The weights, the curated vocabulary, the miner's guess, the alphabet, the
seeds, the closure cuts and the bar. The rows below are `db/0006`'s own — read off that file's
declaration and re-stamped at version 4, notes and all — because a policy version must be a WHOLE
policy (a build reads one version) and re-typing 267 rows to carry them forward is how a
transcription error enters a ledger.

**NOT APPLIED BY THE OFFICER.** This file is written and reported; the apply is the Captain's hand.
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, DictionaryPolicyDoc
from tk2.dictionary import policy
from tk2.dictionary.config import DictionaryConfig, RelationPolicy
from tk2.dictionary.wordnet import SCOPE_WORD
from tk2.migrations import ensure_collections

POLICY_VERSION = 4


def _version_3():
    """`db/0006`, loaded as the runner loads it — the same move 0006 made on 0005, and 0005 on 0004.
    The half of the policy that did not move is READ, never re-typed."""
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 6), None)
    if found is None:
        raise RuntimeError("migration 0006 is gone — it holds the weights version 4 carries forward")
    return found.load()


V3 = _version_3()


# ------------------------------------------------------------------------------------------------
# the one value that moved
# ------------------------------------------------------------------------------------------------

#: `word` — only the lemma spelled like this dimension states antonymy and derivation for it.
#: Imported from the adapter rather than typed, because the two readings are a closed vocabulary of
#: the code (which readings EXIST is frame; which one stands is this row).
LEMMA_SCOPE = SCOPE_WORD

LEMMA_SCOPE_NOTE = (
    "whose lemma may state antonymy and derivation for a dimension — the two relations WordNet "
    "states between LEMMAS rather than between synsets. `word` = its own only; `synset` = every "
    "lemma of the synset, which is what the base was built under until now and what gave `eat` "
    "`corrode`'s derivations and `refuse` `reject`'s antonym. RULED `word` by the Captain on "
    "2026-08-26 on the measured A/B: R goes from 56,599 cells to 49,965 (-6,634, and NOTHING "
    "gained — the narrow reading is a strict subset), negatives 920 -> 663 (-257), silent rows "
    "318 -> 353 (+35, 27 of them adjectives), while membership does not move at all (3,095 words / "
    "4,445 dimensions either way, the closure reading glosses). THE WITNESS: `dark.n -> day.n` was "
    "an antonym at -1.00 LENT BY `night` and is a holonym at +0.60 once the borrowing stops — a "
    "borrowed opposition overriding a stated part-of, with the sign pointing the wrong way. The "
    "synset-wide reading asserts edges WordNet never stated, its 257 borrowed negatives are "
    "unaudited, and a wrong negative is worse than silence: ABSTAIN is first-class. What the "
    "narrow reading loses (`eat~food`, +0.048 -> nothing) was never a relation — it is "
    "co-occurrence, which is D's job by construction (requirement 10)"
)


# ------------------------------------------------------------------------------------------------
# the rows
# ------------------------------------------------------------------------------------------------

RELATIONS = RelationPolicy(
    weights=V3.RELATIONS.weights,
    curated=V3.RELATIONS.curated,
    reciprocal_weight=V3.RELATIONS.reciprocal_weight,
    cues=V3.RELATIONS.cues,
    defaults=V3.RELATIONS.defaults,
    lemma_scope=LEMMA_SCOPE,
)

#: The whole policy v4, as the engine will receive it. Assembled as an OBJECT and written out as
#: rows for the reason every version before it gave: it is the one way to carry a set across a
#: medium without a transcription error, and it means `DECLARED.fingerprint()` is the fingerprint a
#: build will really record.
DECLARED = DictionaryConfig(
    closure=V3.DECLARED.closure,
    declared_seeds=V3.DECLARED.declared_seeds,
    bar=policy.snapshot_bar(),
    relations=RELATIONS,
    alphabet=V3.ALPHABET,
)

POLICY_ROWS = policy.policy_rows_of(DECLARED, POLICY_VERSION, V3.FAMILY_OF)

#: v3's reasons, carried with v3's values. A row that arrived at version 4 with its note dropped
#: would be a curated decision that lost the argument for itself on the way across.
_CARRIED_NOTES = {(row["kind"], row["name"]): row["note"] for row in V3.POLICY_ROWS}

for _row in POLICY_ROWS:
    _key = (_row["kind"], _row["name"])
    # A KeyError here is the point, as it was in 0006: every row of a curated policy explains
    # itself, and a kind that arrived without a reason should fail at import rather than reach the
    # database mute.
    _row["note"] = LEMMA_SCOPE_NOTE if _key == (policy.KIND_RELATION_SETTING, "lemma_scope") \
        else _CARRIED_NOTES[_key]


# ------------------------------------------------------------------------------------------------
# what 0005 knew, still readable from the newest policy file
# ------------------------------------------------------------------------------------------------
#
# `tools/propose_seeds.py` finds the migration declaring the NEWEST policy version and asks it to
# re-derive its structural seeds. That file is now this one. Re-exported rather than
# re-implemented: a second copy of a derivation is how two answers to one question get born.

STRUCTURAL_K = V3.STRUCTURAL_K
STRUCTURAL_SEEDS = V3.STRUCTURAL_SEEDS
derive_structural_seeds = V3.derive_structural_seeds


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(DictionaryPolicyDoc, POLICY_ROWS)
