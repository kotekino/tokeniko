"""0012 — policy version 8: a function word stops being evidence, and D is turned down to 0.15.

**ONE RULING, TWO VALUES, AND THEY WERE MEASURED TOGETHER** because they interact: the filter is
worth most where D is quietest, and D's loudness was itself ruled against a bar that could not see
the defect the filter fixes.

**WHY `structure = "compiled"`.** The standing law of 2026-08-25 says content words are DEFINED and
function words are COMPILED — they become structure in the zip and never need a vector. That law was
enforced where it was ruled, on the seed RANKING, and never on D's gloss vocabulary. So D went on
computing similarity out of words that carry no content by construction: 99 closed-class forms are
3.2% of D's vocabulary and fill **19.6% of all gloss mass**, `in` alone appearing in 843 of the
4,445 definitions. Two definitions being counted as sharing `in` is D DEFINING a word the law says
is compiled.

The witness is the pair that made the bar grow. `agreeably.r` («in an enjoyable manner») and
`unpleasantly.r` («in an unpleasant manner») are stated opposites, R −1.000, and they read
**+0.916** at the old mix because their glosses share `in`, `an`, `a` and `manner` — sentence frame,
not meaning. Under this ruling they read −0.274 at the same mix and −0.988 at the ruled one.

**WHAT IT COSTS, stated because a ruling that only lists its wins is an advertisement.** D loses
73% of its cells (1,674,731 → 456,095 at the time of measuring), 88 dimensions end with an empty
gloss vector, and four NEAR pairs lose the only thing that was holding them up: `eat.v~food.n`
+0.079 → +0.007, `sleep.v~bed.n` and `sleep.v~tired.a` and `intend.v~wish.v` to 0.000. `eat~food` is
the pair D was built for (review finding 4) and it is the hardest thing about this ruling. The
argument for taking it anyway: their glosses' only shared word was `in`. A pair held up by a
function word was a false positive that happened to point the right way, and D still has to earn
that pair honestly — through the sense mode, the vocabulary, or curation.

**WHY `mix` 0.5 → 0.15.** The 0.5 was ruled on 2026-09-09 against eighteen pairs whose only two
opposition pairs are verbs, and it was wrong for everything else: at 0.5, of the 427 pairs R states
an opposition for, **only 214 still read negative** — D lifts the rest to zero or above, because
adverbs and adjectives have short formulaic glosses that D dominates. Swept at the ruled filter
across 0.0–1.0 against the grown bar of thirty-seven, the global order is FLAT from 0.10 to 0.30
(276 · 276 · 276 · 277 · 275 of 336) while opposition survival falls monotonically the moment D gets
louder: **393 at 0.10 · 390 at 0.15 · 376 at 0.20 · 356 at 0.25 · 296 at 0.50**. The peak at 0.25 is
one comparison in 336 — noise — and it costs 34 oppositions against 0.15.

**0.15 is chosen for the plateau, not the peak**, and the Captain ruled it on that argument: the
sign is the one primitive in this geometry that is not a calibration (D is unsigned, so only R can
put a reading below zero), and buying +1/336 by burying 34 stated oppositions is the wrong side of
that trade. A value in the middle of a flat range also survives the bar growing again, which a
fitted peak does not.

**WHAT MOVES.** Two rows. Everything else is v7's, read off `db/0010` and re-stamped with its notes.
The bar does not move here — it moved at `0011`, deliberately first, because both of these values
were re-measured against the thirty-seven and neither could have been ruled against the eighteen.

**THE FORMS ARE NOT NAMED HERE.** `structure` says what to DO with a closed-class form; WHICH forms
are closed is `closed_classes`, the 383 typed rows migration 0004 wrote, and they reach D injected —
the dictionary package stays pure. A `compiled` reading with nothing injected is a refusal in
`distribution.vocabulary_of`, never a silent `admitted`.

**NOT APPLIED BY THE OFFICER OR THE QM.** Written and reported; the apply is the Captain's hand.
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, DictionaryPolicyDoc
from tk2.dictionary import policy
from tk2.dictionary.config import DictionaryConfig, DistributionPolicy, ReadingPolicy
from tk2.migrations import ensure_collections

POLICY_VERSION = 8


def _version_7():
    """`db/0010`, loaded as the runner loads it — the chain every version since 0005 has used."""
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 10), None)
    if found is None:
        raise RuntimeError("migration 0010 is gone — it holds the policy version 8 carries forward")
    return found.load()


V7 = _version_7()


# ------------------------------------------------------------------------------------------------
# the two values that moved
# ------------------------------------------------------------------------------------------------

DISTRIBUTION = DistributionPolicy(
    senses=V7.DISTRIBUTION.senses,
    vocabulary=V7.DISTRIBUTION.vocabulary,
    measure=V7.DISTRIBUTION.measure,
    weighting=V7.DISTRIBUTION.weighting,
    structure="compiled",
    min_shared=V7.DISTRIBUTION.min_shared,
    scale=V7.DISTRIBUTION.scale,
    cap=V7.DISTRIBUTION.cap,
    floor=V7.DISTRIBUTION.floor,
    identity=V7.DISTRIBUTION.identity,
)

READING = ReadingPolicy(mix=0.15)


STRUCTURE_NOTE = (
    "what D does with a word whose job is structural. RULED `compiled` by the Captain on "
    "2026-09-10, the standing law of 2026-08-25 applied where it had been skipped: content words "
    "are defined and function words are compiled, and two definitions counted as sharing `in` is D "
    "defining one. The law was enforced on the seed RANKING when it was ruled and never on D's "
    "vocabulary, so until today 99 closed-class forms — 3.2% of that vocabulary — filled 19.6% of "
    "all gloss mass, `in` appearing in 843 of 4,445 definitions. MEASURED against the grown bar of "
    "thirty-seven: `agreeably.r ~ unpleasantly.r`, stated opposites at R -1.000, read +0.916 "
    "admitted and -0.274 compiled at the same mix; `externally.r ~ internally.r` +0.111 -> -0.970. "
    "Globally the oppositions R states that still read negative go 302 -> 356 of 427 at mix 0.25 "
    "and 214 -> 296 at 0.5. THE COST, which is real: D loses 73% of its cells, 88 dimensions end "
    "with an empty gloss vector, and `eat.v~food.n` — the pair D exists for — falls +0.079 -> "
    "+0.007 because the only word its two definitions shared was `in`. Taken anyway: a pair held "
    "up by a function word is a false positive that happened to point the right way. WHICH forms "
    "are closed is not declared here — that is `closed_classes`, migration 0004's 383 typed rows, "
    "injected at build time because this package is pure"
)

MIX_NOTE = (
    " RE-RULED 0.5 -> 0.15 on 2026-09-10, and the first value is why the bar had to grow before "
    "this could be decided: 0.5 was measured against eighteen pairs whose only two oppositions are "
    "VERBS, and it is wrong for everything else — at 0.5 only 214 of the 427 pairs R states an "
    "opposition for still read negative, because adverbs and adjectives have short formulaic "
    "glosses that D dominates. SWEPT with `structure = compiled` against the thirty-seven, global "
    "order out of 336: 0.0 -> 239 · 0.10 -> 276 · 0.15 -> 276 · 0.20 -> 276 · 0.25 -> 277 · "
    "0.30 -> 275 · 0.50 -> 250 · 1.0 -> 227. FLAT from 0.10 to 0.30 — while opposition survival "
    "falls monotonically across the same range: 393 · 390 · 376 · 356 · 340 · 296 of 427. The peak "
    "at 0.25 is ONE comparison in 336 and costs 34 oppositions against 0.15. Chosen for the "
    "PLATEAU and not the peak: the sign is the one primitive here that is not a calibration (D is "
    "unsigned, so only R can put a reading below zero), and a value in the middle of a flat range "
    "survives the bar growing again where a fitted peak does not. Verified at 0.25 and holding at "
    "0.15: of the FAR pairs still reading at or above zero, NOT ONE has a stated opposition — what "
    "is left is the POS collapse (`land`, `compass`, `play` over a derivational cell) and noise "
    "below +0.06"
)


# ------------------------------------------------------------------------------------------------
# the rows
# ------------------------------------------------------------------------------------------------

DECLARED = DictionaryConfig(
    closure=V7.DECLARED.closure,
    declared_seeds=V7.DECLARED.declared_seeds,
    bar=V7.DECLARED.bar,
    relations=V7.DECLARED.relations,
    alphabet=V7.DECLARED.alphabet,
    distribution=DISTRIBUTION,
    reading=READING,
)

FAMILY_OF = V7.FAMILY_OF

POLICY_ROWS = policy.policy_rows_of(DECLARED, POLICY_VERSION, FAMILY_OF)

_CARRIED_NOTES = {(row["kind"], row["name"]): row["note"] for row in V7.POLICY_ROWS}

_NEW_NOTES = {
    (policy.KIND_DISTRIBUTION, "structure"): STRUCTURE_NOTE,
    (policy.KIND_READING, "mix"): _CARRIED_NOTES[(policy.KIND_READING, "mix")] + MIX_NOTE,
}

for _row in POLICY_ROWS:
    _key = (_row["kind"], _row["name"])
    # A KeyError here is the point, as it was in 0006 through 0010: every row of a curated policy
    # explains itself, and a kind that arrived without a reason should fail at import rather than
    # reach the database mute.
    _row["note"] = _NEW_NOTES[_key] if _key in _NEW_NOTES else _CARRIED_NOTES[_key]


# ------------------------------------------------------------------------------------------------
# what 0005 knew, still readable from the newest policy file
# ------------------------------------------------------------------------------------------------

STRUCTURAL_K = V7.STRUCTURAL_K
STRUCTURAL_SEEDS = V7.STRUCTURAL_SEEDS
derive_structural_seeds = V7.derive_structural_seeds


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(DictionaryPolicyDoc, POLICY_ROWS)
