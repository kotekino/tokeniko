"""0009 — policy version 6: D's gloss walk, declared before it measures anything.

**WHAT THIS IS.** T4 builds D — the gloss-overlap matrix, square over the very same base keys R is
square over — and the standing law of 2026-08-25 decides where its parameters live: «the relation
weights you write in T3: they land as rows from the start, never as a table in `config.py`». D's
walk is the same category-2 set for the same reason, so it arrives as rows on its first day rather
than being moved into them later.

**THE VALUES ARE THE PROTOTYPE'S, VERBATIM**, and that is deliberate for T4b-i's reason: «today's
values migrate across VERBATIM — a value edited here would corrupt the comparison». `docs/dictionary/origin-prototype/`
is where every one of them comes from (`tk2_config.py`: `WEIGHTS["identity"] = 1.0`,
`GLOSS_JACCARD_CAP = 0.5`, `GLOSS_JACCARD_FLOOR = 0.1`, the `jaccard * 5` of `tk2_matrix.cell`, its
`len(inter) >= 2`, and `_lemmas_in_base`'s base-word vocabulary), and the notes below record what
each one MEASURES at the full base beside what it was worth at 983 dimensions. Three of them do not
survive the change of scale intact, and the notes say so in numbers rather than in adjectives —
the ruling on each is the Captain's, and this migration is what makes the ruling comparable.

**WHAT MOVES.** The policy gains nine rows and nothing else changes: the seeds, the closure cuts,
the relation weights, the lemma scope, the antonym reading, the curated vocabulary, the alphabet and
the bar are v5's, read off `db/0008` and re-stamped at version 6. Membership does not move — the
closure reads WORDS' definitions and D reads KEYS', and nothing here touches the digraph — so the
base stays 3,095 words / 4,445 dimensions and R stays 50,108 cells. The config fingerprint moves,
because a build that measured D and one that did not must not be able to present the same hash.

**WHAT IT IS NOT.** It declares no acceptance floor and no way of reading R and D together: both are
T5's, and the second of them (the `mix` of the dual read) is measured at T4 and ruled by the Captain
before it can be a row at all. A migration that quietly declared either would be the threshold
question answering itself.

**NOT APPLIED BY THE OFFICER.** This file is written and reported; the apply is the Captain's hand.
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, DictionaryPolicyDoc
from tk2.dictionary import policy
from tk2.dictionary.config import DictionaryConfig, DistributionPolicy
from tk2.migrations import ensure_collections

POLICY_VERSION = 6


def _version_5():
    """`db/0008`, loaded as the runner loads it — the chain every version since 0005 has used. The
    half of the policy that did not move is READ, never re-typed."""
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 8), None)
    if found is None:
        raise RuntimeError("migration 0008 is gone — it holds the policy version 6 carries forward")
    return found.load()


V5 = _version_5()


# ------------------------------------------------------------------------------------------------
# the nine values D's walk is made of
# ------------------------------------------------------------------------------------------------

DISTRIBUTION = DistributionPolicy(
    senses="primary",
    vocabulary="base",
    measure="jaccard",
    weighting="uniform",
    min_shared=2,
    scale=5.0,
    cap=0.5,
    floor=0.1,
    identity=1.0,
)

NOTES = {
    "senses": (
        "which senses of a dimension write its definition. `primary` = the first synset of its part "
        "of speech (what the Jurassic build and the prototype used, and what the closure's own cut "
        "declares beside this one); `all` = every reading. D's OWN row rather than a reuse of the "
        "closure's, because they are the same question asked of two different things: the closure's "
        "cut decides which senses earn a word its MEMBERSHIP, this decides which senses place a "
        "dimension in the geometry. MEASURED at the full base, 4,445 dimensions: `primary` gives "
        "gloss sets of 5.3 words on average and 835k pairs that share at least one; `all` gives "
        "15.5 words and 3.85M such pairs, with `in` rising from 19% of rows to 43% of them. The "
        "Captain's parked question (a) is about this row and the closure's together"
    ),
    "vocabulary": (
        "which words a definition may be counted as naming. `base` = the closure's own words — the "
        "prototype's reading (`tk2_common._lemmas_in_base`), and the one the subset's whole "
        "argument supports: the base was chosen for defining itself. `lexicon` = every word the "
        "resource knows, so two definitions may share a word the base does not contain. MEASURED at "
        "the full base: the two agree almost exactly — 835,145 overlapping pairs under `base` "
        "against 835,871 under `lexicon` (+0.09%), because the words the base lacks are rare and "
        "shared by nobody. The visible difference is elsewhere: 35 dimensions have an EMPTY gloss "
        "vector under `base` and 4 under `lexicon`"
    ),
    "measure": (
        "how much of two definitions is «the same»: `jaccard` = shared / union (the prototype's, "
        "and the harshest — it punishes a long definition met by a short one), `dice` = "
        "2*shared / (a + b), `cosine` = shared / sqrt(a*b), the gentlest. All three are one "
        "statement measured three ways and none of them is a threshold; which is right is a "
        "curated decision and this row is where it is written down"
    ),
    "weighting": (
        "what ONE shared gloss word is worth. `uniform` = one word, one vote (the prototype's, and "
        "what a plain Jaccard means). `idf` = log(1 + N/df) over the base's own rows, so a word "
        "half the base uses counts for almost nothing and a word two rows share counts for nearly "
        "everything. The Captain's parked question (b) is this row: after the name refusal removed "
        "Oregon's `or` from 57.8% of the base's rows, the loudest words left are REAL function "
        "words — `in` on 19% of them, `by` 10%, `be` 9%, `as` 8% — and that is a weighting question "
        "rather than a membership one, because `in` is a word the base admits on purpose. The "
        "smoothing is log(1 + N/df) rather than log(N/df) so that a word every row names is worth "
        "little and never worth nothing: at zero it would leave the union as well as the "
        "intersection, and two definitions sharing nothing but it would score a perfect 0/0"
    ),
    "min_shared": (
        "how many words two definitions must share before D says anything. The prototype asked two "
        "(`len(inter) >= 2`) and at this scale it is doing most of the sizing: of the 835,145 pairs "
        "that share at least one word, 76,915 share two and 9,762 share three. One shared word is a "
        "coincidence here — `in` alone joins a fifth of the base"
    ),
    "scale": (
        "the multiplier on the measure. NOT cosmetic and not free: the diagonal is a declared 1.0, "
        "so what an off-diagonal cell is worth AGAINST its own axis is what decides every row "
        "cosine. The prototype's 5 was calibrated at 983 dimensions with the Jurassic gloss sets; "
        "MEASURED at this base it saturates almost everything — a Jaccard of 0.1 already reaches "
        "the cap, and the mean gloss set holds 5.3 words, so two definitions sharing two words are "
        "usually past it. See the `cap` row for what that does to D"
    ),
    "cap": (
        "the ceiling a scaled overlap saturates at (the Jurassic `GLOSS_JACCARD_CAP`). Together "
        "with `scale` = 5 it means every pair whose Jaccard reaches 0.1 records the same number, "
        "which at this base is most of them — D becomes very nearly a BINARY matrix at 0.5. That "
        "was a reasonable shape at 983 dimensions and it is a finding at 4,445; the alternatives "
        "(raise the cap, drop the scale to 1 and let Jaccard speak) are measured in T4's report and "
        "the ruling is the Captain's"
    ),
    "floor": (
        "below this, no cell is written (the Jurassic `GLOSS_JACCARD_FLOOR`). A noise floor by "
        "intent and a SIZE RAIL in effect: D is dense where R is sparse, and this row plus "
        "`min_shared` are what decide whether the collection is a hundred thousand cells or ten "
        "million. It is not the acceptance floor and must not be read as one — the bar's scoring "
        "floors are T5's and the Captain's"
    ),
    "identity": (
        "D's diagonal: a dimension owns its own axis, and a matrix whose diagonal is zero has no "
        "self-similarity — its cosines stop meaning what they look like. Declared here rather than "
        "borrowed from R's `identity` weight (which is also 1.0 today) because R and D are two "
        "geometries, and a shared row would tie one matrix's axis to the other's weight table"
    ),
}


# ------------------------------------------------------------------------------------------------
# the rows
# ------------------------------------------------------------------------------------------------

DECLARED = DictionaryConfig(
    closure=V5.DECLARED.closure,
    declared_seeds=V5.DECLARED.declared_seeds,
    bar=V5.DECLARED.bar,
    relations=V5.DECLARED.relations,
    alphabet=V5.DECLARED.alphabet,
    distribution=DISTRIBUTION,
)

FAMILY_OF = V5.FAMILY_OF

POLICY_ROWS = policy.policy_rows_of(DECLARED, POLICY_VERSION, FAMILY_OF)

#: v5's reasons, carried with v5's values.
_CARRIED_NOTES = {(row["kind"], row["name"]): row["note"] for row in V5.POLICY_ROWS}

for _row in POLICY_ROWS:
    _key = (_row["kind"], _row["name"])
    # A KeyError here is the point, as it was in 0006, 0007 and 0008: every row of a curated policy
    # explains itself, and a kind that arrived without a reason should fail at import rather than
    # reach the database mute.
    _row["note"] = NOTES[_row["name"]] if _row["kind"] == policy.KIND_DISTRIBUTION else _CARRIED_NOTES[_key]


# ------------------------------------------------------------------------------------------------
# what 0005 knew, still readable from the newest policy file
# ------------------------------------------------------------------------------------------------

STRUCTURAL_K = V5.STRUCTURAL_K
STRUCTURAL_SEEDS = V5.STRUCTURAL_SEEDS
derive_structural_seeds = V5.derive_structural_seeds


def up(writer, db) -> None:
    # `base_d` is created HERE and filled by a build, for `base_r`'s reason at 0006: a build that
    # had to create its own collection would be a build doing a deploy's job.
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(DictionaryPolicyDoc, POLICY_ROWS)
