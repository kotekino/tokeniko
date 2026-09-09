"""0010 — policy version 7: the dual read gets a home, and three numbers move on evidence.

**ONE RULING, THREE VALUES (the Captain, 2026-09-09), made on the T4 sweeps.** `min_shared` 2 -> 1,
`derivational` 0.90 -> 0.45, and `mix` — which had no home at all — becomes 0.5 and becomes a row.
The three are one decision because they were measured as one: the gate of two was choking D, and
what D can say is exactly what lets R's POS collapse be pulled apart by evidence instead of by
silence, which is what makes a halved `derivational` an improvement rather than a retreat.

**WHY `min_shared` MOVED.** It was doing most of D's sizing and most of D's silencing. Swept at the
full base: 1 -> 1,670,286 cells, 41% at the cap, 41 silent rows, D ALONE ordering 47 of 80; 2 ->
153,830 cells, 87% at the cap, 809 silent rows, 26 of 80; 3 -> 19,524 cells, 98.7% at the cap,
2,285 silent rows, 8 of 80. At two the cap swallowed 87% of what survived, D stopped saying HOW MUCH,
and `measure` and `vocabulary` became literally unobservable behind it — dice, cosine and `lexicon`
all returned the identical bar. The coincidence argument that asked for two (`in` alone joins a fifth
of the base) is real and it is answered by measurement: admitting those pairs costs less than the
evidence the gate was suppressing.

**WHY `derivational` MOVED, AND ONLY HALFWAY.** `land.n~land.v` is a declared FAR pair and
`cause.n~cause.v` a declared NEAR one, and R gives them the IDENTICAL `derivational` cell — a
collapse R has no evidence to resolve. Swept at the ruled gate and the ruled mix (global of 80):
0.90 -> 64 · 0.75 -> 65 · 0.60 -> 65 · **0.45 -> 67, local 5/7** · 0.30 -> 66, local 4/7 · 0.15 ->
66, local 4/7 · 0.00 -> 66, local 4/7. **0.45 is a peak, not a slope**: below it the global stops
improving and the local order breaks. Killing the relation would cost more than halving it — the
derivation is a real thing WordNet states, and what separates the two pairs now is D's own reading
(`cause.n~cause.v` +0.050 against `land.n~land.v` +0.024, twice as near).

**WHY THE MIX IS 0.5 AND WHY IT IS A ROW.** v6 declared D and deliberately said nothing about how
to hear it — «measured at T4 and ruled by the Captain before it can be a row at all». It is ruled
now. At mix 1.0 the same base reads 60 of 80 and `enter~leave`, a FAR pair R states as an
OPPOSITION, turns POSITIVE at +0.063: D drowns the sign, which is the 2026-08-12 review's own
failure reproduced at the full base. At 0.5 the sign survives at -0.059 and the score peaks. (Those
four numbers are the sweep's, taken at `derivational` 0.90 because that is what was standing while
the mix was being swept; re-read under the whole ruling they are 61 and 67 of 80, +0.065 and -0.062,
and they say the same thing.) R stays the louder floor; D advises. **There is no code default for
it**, the same law the lemma scope and the antonym reading carry: an undeclared mix is a refusal,
never a silent 1.0.

**WHAT THE THREE BUY, against the standing v6 reading (min_shared 2, mix 1.0, derivational 0.90):
58/80 -> 67/80 global, local 4/7 -> 5/7, MUTE 7 -> 0.** The seven mute pairs are the topical
nearnesses R cannot state at all (finding 4 of the review); at the old gate D could not state them
either, and now it can.

**TWO PARKED QUESTIONS CLOSE, both by rejection.** (a) `senses="all"` — the key space goes 4,445 ->
12,925, `enter~leave` reads +0.759 and the local order collapses to 1 of 7. (b) `idf` — it moves
junk's share of the shared mass 35.7% -> 22.5%, does not move the pairs resting on nothing but junk
(10.4% either way, which is membership and only a filter could move it), and makes the bar slightly
worse (58 -> 57). Both are written into the rows they belong to, in numbers, so a later reader does
not re-litigate them blind.

**WHAT MOVES.** Two values, one new kind of row, and nothing else: the seeds, the closure cuts, the
other eighteen relation weights, the curated vocabulary, the miner's guess, the lemma scope, the
antonym reading, the alphabet, the rest of the gloss walk and the bar are v6's, read off `db/0009`
and re-stamped at version 7 with their reasons intact. Membership does not move — neither ruled
value is read by the closure — so the base stays 3,095 words / 4,445 dimensions. The config
fingerprint moves, and v1-v6 keep theirs.

**WHAT IT IS NOT.** It declares no acceptance floor. The bar's scoring floors are T5's and the
Captain's, and they are the same category as the mix — a reading of two matrices rather than a
property of either — so `ReadingPolicy` is where they will land, and this migration deliberately
does not land them.

**NOT APPLIED BY THE OFFICER.** This file is written and reported; the apply is the Captain's hand.
"""

from dataclasses import replace

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, DictionaryPolicyDoc
from tk2.dictionary import policy
from tk2.dictionary.config import DictionaryConfig, ReadingPolicy
from tk2.migrations import ensure_collections

POLICY_VERSION = 7


def _version_6():
    """`db/0009`, loaded as the runner loads it — the chain every version since 0005 has used. The
    part of the policy that did not move is READ, never re-typed."""
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 9), None)
    if found is None:
        raise RuntimeError("migration 0009 is gone — it holds the policy version 7 carries forward")
    return found.load()


V6 = _version_6()


# ------------------------------------------------------------------------------------------------
# the three values that moved
# ------------------------------------------------------------------------------------------------

#: One shared word is enough for D to say something. The gate of two was not a noise floor at this
#: scale — it was a mute.
MIN_SHARED = 1

#: A derivation is halved, not killed: `land.n` and `land.v` share a real WordNet edge, and what
#: has to separate them from `cause.n`/`cause.v` is evidence rather than R's silence.
DERIVATIONAL = 0.45

#: How loudly D speaks in the dual read. R stays the louder floor and the antonym sign survives.
MIX = 0.5

#: The name whose weight moved. Named rather than typed into the tuple comprehension below, so the
#: one relation this migration touches is greppable from the file that touches it.
DERIVATIONAL_RELATION = "derivational"


def _reweighted(weights):
    """R's weights with exactly one number changed, in the SAME declared order.

    The order is the cell walk's precedence, so a rebuild of the tuple that reordered it would move
    which relation wins a tie — a silent second change riding along with the ruled one.
    """
    out = tuple(
        (name, DERIVATIONAL if name == DERIVATIONAL_RELATION else weight)
        for name, weight in weights
    )
    if not any(name == DERIVATIONAL_RELATION for name, _weight in out):
        raise RuntimeError(
            f"policy v6 declares no {DERIVATIONAL_RELATION!r} weight — this migration halves a "
            f"number that is no longer there"
        )
    return out


RELATIONS = replace(V6.DECLARED.relations, weights=_reweighted(V6.DECLARED.relations.weights))

DISTRIBUTION = replace(V6.DISTRIBUTION, min_shared=MIN_SHARED)

READING = ReadingPolicy(mix=MIX)


# ------------------------------------------------------------------------------------------------
# what the three ruled rows now say, and what the measured-and-standing ones now say
# ------------------------------------------------------------------------------------------------

MIN_SHARED_NOTE = (
    "how many words two definitions must share before D says anything. RULED 1 by the Captain on "
    "2026-09-09, down from the prototype's two (`len(inter) >= 2`), because at this base it was "
    "doing most of D's sizing AND most of D's silencing. SWEPT at the full base, three ways: "
    "1 -> 1,670,286 cells, 41% of them at the cap, 41 silent rows, D ALONE ordering 47 of 80 "
    "NEAR/FAR comparisons; 2 -> 153,830 cells, 87% at the cap, 809 silent rows, 26 of 80; "
    "3 -> 19,524 cells, 98.7% at the cap, 2,285 silent rows, 8 of 80. At two the cap swallowed 87% "
    "of what survived the gate, so D had stopped saying HOW MUCH — and `measure` and `vocabulary` "
    "were unobservable behind it, dice and cosine and `lexicon` all returning the identical bar. "
    "At one D SEPARATES WHAT R CANNOT: `cause.n~cause.v` reads +0.050 against `land.n~land.v` "
    "+0.024, twice as near, where R gives the two the identical `derivational` cell. The seven bar "
    "pairs R is mute about (the topical nearnesses of review finding 4) were mute in D as well at "
    "the old gate and are stated now. The coincidence argument that asked for two — `in` alone "
    "joins a fifth of the base — is true and is ANSWERED BY MEASUREMENT rather than repealed: "
    "admitting those pairs costs less than the evidence the gate was suppressing (D alone 26 -> 47 "
    "of 80). It also costs SIZE, and the number is the honest one to remember: D is 1.67 MILLION "
    "cells, an order of magnitude past v6's 153,830"
)

DERIVATIONAL_NOTE = (
    "able -> ability. Cross-POS by nature, which is half of why the base splits by part of speech "
    "at all. RULED 0.45 by the Captain on 2026-09-09, HALVED from the prototype's 0.90. THE "
    "PROBLEM it answers: `land.n~land.v` is a declared FAR pair and `cause.n~cause.v` a declared "
    "NEAR one, and R states the IDENTICAL cell for both — a POS collapse R has no evidence to "
    "resolve. SWEPT at the ruled gate (min_shared 1) and the ruled mix (0.5), global order out of "
    "80: 0.90 -> 64 (local 5/7) · 0.75 -> 65 · 0.60 -> 65 · 0.45 -> 67 (local 5/7) · 0.30 -> 66 "
    "(local 4/7) · 0.15 -> 66 (local 4/7) · 0.00 -> 66 (local 4/7). 0.45 IS A PEAK AND NOT A "
    "SLOPE: below it the global stops improving and the LOCAL order breaks, so killing the relation "
    "costs more than halving it. Halved and not killed on purpose — the derivation is a real edge "
    "WordNet states, and what pulls the two pairs apart now is EVIDENCE (D reads them +0.050 "
    "against +0.024) rather than R's silence. IT ALSO MOVES PROVENANCE, NOT ONLY WEIGHT, and the "
    "count is here so nobody rediscovers it as a bug: R's total is unchanged at 50,108 cells, but "
    "101 of them change WHICH RELATION THEY CLAIM. At 0.90 a derivation outranked `attribute` "
    "(0.70) wherever both held the same cell; at 0.45 it no longer does, so the walk hands those "
    "cells to the stronger claim — `derivational` 5,870 -> 5,769, `attribute` 302 -> 400, "
    "`hyponym_1` +2, `hypernym_1` +1. That is the precedence rule working as designed and it is "
    "arguably the better reading (a stated adjective-noun `attribute` is the axis R is quietest "
    "about), but a weight ruling that silently re-labels cells is the kind of thing a later reader "
    "must be told rather than left to find"
)

MIX_NOTE = (
    "HOW LOUDLY D SPEAKS when the two geometries are read as one number: D's columns are scaled by "
    "this, the two rows are CONCATENATED (never averaged — see `config.READING_RULES`) and one "
    "cosine is taken over the whole vector. `0` is R alone and would be a real declaration. RULED "
    "0.5 by the Captain on 2026-09-09, and it is load-bearing in both directions. UPWARD, measured "
    "at the ruled gate and the PRE-ruling `derivational` 0.90 (which is where the mix was swept): "
    "at mix 1.0 the same base reads 60 of 80 against 0.5's 64, and `enter~leave` — a FAR pair R "
    "states as an OPPOSITION — turns POSITIVE at +0.063, because opposites are defined in the same "
    "words. That is the 2026-08-12 review's own failure reproduced at the full base, and the sign "
    "is the antonym column-read primitive, so burying it is not a worse score but a BROKEN "
    "INSTRUMENT. At 0.5 it survives at -0.059 and the bar peaks. RE-READ under the whole ruling "
    "(derivational 0.45) the two columns are 61 and 67 of 80 and `enter~leave` is +0.065 against "
    "-0.062: the numbers move a little, the conclusion does not move at all. DOWNWARD: R stays the "
    "louder floor and D advises rather than votes. THERE IS NO DEFAULT FOR THIS IN CODE — an "
    "undeclared mix is a refusal, the same law the lemma scope and the antonym reading carry — "
    "because a round number in a tool is not a declaration: the sweep ran for a fortnight under a "
    "printed 1.0 nobody had ruled. THE WHOLE RULING, against the standing v6 reading (min_shared 2, "
    "mix 1.0, derivational 0.90): 58/80 -> 67/80 global, local 4/7 -> 5/7, MUTE 7 -> 0"
)


def _carried(kind: str, name: str) -> str:
    """v6's own reason for a row, to be extended rather than re-typed.

    The rows that did not move keep their notes verbatim (0009's mechanism below); these are the
    rows whose VALUE did not move but about which something was MEASURED, and a note that dropped
    what v6 said in order to add what T4 found would lose the argument the value was made on.
    """
    for row in V6.POLICY_ROWS:
        if row["kind"] == kind and row["name"] == name:
            return row["note"]
    raise RuntimeError(f"policy v6 has no {kind}/{name} row to carry a reason forward from")


#: The values T4 measured and did NOT move. Their notes GAIN the measurement — never lose the
#: argument the value was made on — because a question that was asked and answered must not read
#: like a question nobody has looked at.
MEASURED_AND_STANDING = {
    (policy.KIND_DISTRIBUTION, "measure"): (
        " MEASURED at the old gate (min_shared 2) and found UNOBSERVABLE: `dice` and `cosine` "
        "return the IDENTICAL bar to `jaccard` (D alone 26/80, R+D 58/80), because at that gate the "
        "cap saturated 87% of the surviving cells and all three measures reached it. Not a decision "
        "of 2026-09-09 and not a settled one either — at the ruled gate of 1 only 41% of cells are "
        "capped, so this is a question that can now be asked and has not been"
    ),
    (policy.KIND_DISTRIBUTION, "vocabulary"): (
        " MEASURED at the old gate and unobservable for `measure`'s reason: `lexicon` returns the "
        "identical bar to `base` (D alone 26/80, R+D 58/80), which the +0.09% in overlapping pairs "
        "above already predicts. `base` stands, unmoved and unruled"
    ),
    (policy.KIND_DISTRIBUTION, "senses"): (
        " CLOSED on 2026-09-09: `all` was measured whole — both cuts move together, so it is a "
        "different BASE and not a different reading of one — and REJECTED. The key space goes "
        "4,445 -> 12,925 dimensions, and the geometry goes with it: `enter~leave` reads +0.759, an "
        "opposition R states drowned by a topical overlap, and the local order collapses to 1 of 7. "
        "`primary` stands"
    ),
    (policy.KIND_DISTRIBUTION, "weighting"): (
        " MEASURED on 2026-09-09, at the then-standing gate of 2, and `idf` NOT ADOPTED. It does "
        "what it claims — junk's share of the shared mass falls 35.7% -> 22.5% — but the pairs "
        "resting on NOTHING BUT junk do not move (10.4% either way: that figure is membership, and "
        "only a filter could move it), and "
        "the bar gets slightly WORSE (58 -> 57 of 80). A weighting that improves the diagnostic "
        "figure and not the reading is not a reason to move a curated value. "
        "RE-MEASURED on 2026-09-09 at the RULED gate of one, because the first measurement was "
        "taken under conditions the same day's ruling repealed — at the new gate junk carries 62.9% "
        "of the shared mass rather than 35.7%, so the case for `idf` was materially stronger and "
        "had to be put again rather than inherited. The verdict is UNCHANGED and the numbers are "
        "larger on both sides: `idf` cuts junk's share of the shared mass 62.9% -> 45.7% (a bigger "
        "win than at the old gate), the only-junk pairs still do not move (63.5% either way — "
        "membership again), and the reading still gets WORSE, 67 -> 65 of 80. Pair by pair it "
        "trades rather than improves: `eat~hungry` +0.111 -> +0.174 and `cause.n~cause.v` "
        "+0.050 -> +0.056, against `eat~food` +0.166 -> +0.131 and `bed.n~cause.n` — D's worst "
        "false positive, a declared FAR — getting LOUDER at +0.338 -> +0.352. Parked question (b), "
        "answered twice under two different gates: `uniform` stands"
    ),
    (policy.KIND_DISTRIBUTION, "cap"): (
        " RE-MEASURED after the `min_shared` ruling: at the gate of one, 41% of D's cells sit at "
        "the cap rather than 87%, so most of D can say how much again — which is most of what that "
        "ruling bought. The pair (scale 5, cap 0.5) is still the prototype's and still unruled; it "
        "is now a question with room to be asked"
    ),
    (policy.KIND_CLOSURE, "senses"): (
        ". MEASURED on 2026-09-09 and `all` REJECTED: it takes the base from 4,445 dimensions to "
        "12,925 and the bar's local order to 1 of 7 (`enter~leave` +0.759). The parked question (a) "
        "of 2026-08-25 was about this row and D's `senses` together, and it is closed on both"
    ),
}


# ------------------------------------------------------------------------------------------------
# the rows
# ------------------------------------------------------------------------------------------------

DECLARED = DictionaryConfig(
    closure=V6.DECLARED.closure,
    declared_seeds=V6.DECLARED.declared_seeds,
    bar=V6.DECLARED.bar,
    relations=RELATIONS,
    alphabet=V6.DECLARED.alphabet,
    distribution=DISTRIBUTION,
    reading=READING,
)

FAMILY_OF = V6.FAMILY_OF

POLICY_ROWS = policy.policy_rows_of(DECLARED, POLICY_VERSION, FAMILY_OF)

#: v6's reasons, carried with v6's values.
_CARRIED_NOTES = {(row["kind"], row["name"]): row["note"] for row in V6.POLICY_ROWS}

_NEW_NOTES = {
    (policy.KIND_DISTRIBUTION, "min_shared"): MIN_SHARED_NOTE,
    (policy.KIND_RELATION_WEIGHT, DERIVATIONAL_RELATION): DERIVATIONAL_NOTE,
    (policy.KIND_READING, "mix"): MIX_NOTE,
    **{key: _carried(*key) + added for key, added in MEASURED_AND_STANDING.items()},
}

for _row in POLICY_ROWS:
    _key = (_row["kind"], _row["name"])
    # A KeyError here is the point, as it was in 0006, 0007, 0008 and 0009: every row of a curated
    # policy explains itself, and a kind that arrived without a reason should fail at import rather
    # than reach the database mute.
    _row["note"] = _NEW_NOTES[_key] if _key in _NEW_NOTES else _CARRIED_NOTES[_key]


# ------------------------------------------------------------------------------------------------
# what 0005 knew, still readable from the newest policy file
# ------------------------------------------------------------------------------------------------

STRUCTURAL_K = V6.STRUCTURAL_K
STRUCTURAL_SEEDS = V6.STRUCTURAL_SEEDS
derive_structural_seeds = V6.derive_structural_seeds


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(DictionaryPolicyDoc, POLICY_ROWS)
