# dictionary — THE PLACEMENT FLOOR, MEASURED AND REFUSED, 2026-09-19 15:00

*Roadmap: `E3.6`*

*E3 task 6 asked for a floor fitted to the sense layer, because the base's +0.15 reads NEAR for 99.5%
of placements and «a floor that says NEAR to everything is not a floor». The bench was built first,
forty placements were ruled, and the answer is that **the floor is not the instrument**. No number is
proposed, and that is the result.*

**116,725 placed senses measured · 40 ruled by the Captain · NO GAP in either half.**

---

## THE POPULATION FIRST — WHAT A PLACEMENT'S COSINE LOOKS LIKE

Every placed sense on build `969766250c02`, projected and ranked in the half that placed it:

    half             n        p1      p10     p25     p50     p75     p90     p99
    relational      72,059   +0.272  +0.363  +0.415  +0.482  +0.558  +0.639  +0.894
    distributional  44,666   +0.118  +0.153  +0.184  +0.236  +0.312  +0.385  +0.632

    the base's floor (+0.15) reads NEAR for 99.5% of R and 91.1% of D

**Two populations, not one.** R's median sits at +0.482 and D's at +0.236, so a single threshold
cannot read both — which already made «the placement floor» at least two floors, before any pair was
ruled.

## THE BAR — FORTY, STRATIFIED, AND WHY THEY ARE NOT `dictionary_bar` ROWS

Sampled by half and by cosine band (p0-10 … p80-100) so no band could be argued away, and restricted
to senses WordNet's corpus attests (SemCor ≥ 2) because the station meets words people SAY. The
Captain ruled all forty against the QM's own lean, agreeing with each: *«I tried to disagree on
some… but your judgement is not different than mine»*.

They live in `tests/fixtures/placement_bar.py`, for two reasons either of which is sufficient:

- **they are EVIDENCE** — curated circumstances that JUDGE the app, isolated from it (the third
  kingdom, 2026-09-17), never read at runtime;
- **and `dictionary_bar` would have eaten them.** Every bar word becomes a SEED (req 12), so
  declaring these pairs there would pull *involve*, *abbot* and *wary* into the base as DIMENSIONS.
  A placement that becomes a dimension is no longer a placement: the bar would have destroyed its own
  subject, moved membership, and invalidated build `969766250c02`. `db/0007` wrote that warning down
  — *«growing the bar makes every bar word a seed»* — and this is the first case that met it.

## THE MEASUREMENT — THE VERDICTS INTERLEAVE WITH THE COSINE

    RELATIONAL      14 NEAR · 6 FAR       highest FAR +0.4454   lowest NEAR +0.2606   THEY CROSS
    DISTRIBUTIONAL   2 NEAR · 18 FAR      highest FAR +0.3780   lowest NEAR +0.1654   THEY CROSS

    the best floor possible for R   +0.4555   and it still gets 3 of 20 wrong
    the best floor possible for D   +1.0000   and it still gets 2 of 20 wrong

**Read the second line twice.** The optimal threshold for the distributional half is ONE — reject
everything — and even that is not free, because two placements in the sample are right. The bench's
own optimum says D alone should abstain, and it says so without anybody having argued it.

**And the lowest cosine in the entire sample is a perfect placement**: `involve.v.05 → include.v` at
+0.2606, «contain as a part». Any floor able to cut R's six FARs would throw it away.

*`db/0002`'s lesson, generalised: a threshold belongs in the middle of a real gap. Where the declared
verdicts interleave there is no gap, and a number chosen anyway is the APPEARANCE of a measurement —
which is worse than no number at all, because it would have been quoted.*

## WHY THEY INTERLEAVE — EACH HALF FAILS IN EXACTLY ONE WAY

**R ranks CONCENTRATION, not correctness.** A relations-projected sense rides the edges it states, so
the cosine measures how much of its profile sits on one dimension. When the edge it states points at
something that is NOT a dimension, the projection falls to siblings, and a sibling of a sibling says
nothing: `metamorphose → warm` (both under «change»), `idler → closer` (both «person who —s»). Those
are the six FARs, and they sit in the MIDDLE of the range, not the bottom.

**D reads the definition's GRAMMAR.** `mark.v` is rank 1 for three unrelated senses — *marked by
attention*, *marked by sensationalism*, *marked by caution*. So is *given to*, *in accordance with*,
*the act of*. The gloss's function words carry more weight than its content:

    inquiring.a.01   -> give.n        «GIVEN to inquiry»              `inquiry.n` was rank 2
    strategical.a.01 -> concern.v     «CONCERNED with strategy»       «strategy» appears nowhere
    transcendental.a.01 -> accordance.n  «NOT IN ACCORDANCE with nature»   the negation is invisible
    fin.n.01         -> four.a        «the sum of FOUR and one»       off by one, by definition-word

**A NAMED DEFECT FOR E1, and not a threshold's business**: D's gloss reading admits function words
and the frame words of a definition («marked by», «given to», «relating to»). Repairing that is a
build question — a stop-list is the obvious wrong answer (it is a set in code), and the right shape
is likely the same one req 15 used: read what the resource STATES about a word rather than which
words a sentence happens to contain. Recorded here, owed by E1.

## WHAT REPLACED THE NUMBER — RULED AND BUILT THE SAME DAY

The first proposal was **«R is trusted, D abstains»**, and the Captain approved it. Then one more
measurement was run before it was written into code, and it changed the rule: **«R placed it» and «R
STATES that edge» are not the same claim.**

    R states the edge         4 of 4 declared NEAR      no false trust anywhere in the bar
    R, no stated edge        10 NEAR / 6 FAR            a coin flip — the SIBLING FALLBACK
    D                         2 NEAR / 18 FAR           and it can never state an edge (below)

All six relational failures are the sibling fallback, so the approved two-way rule would have carried
**six wrong trusts in twenty** — wrongly-understood, the sin parser-compiler req 8 names, against a
fitted floor's three. Reported rather than built, and the Captain ruled the three-way version *«if
coverage allows»*:

    R STATES an edge to that dimension   ->  NEAR       trust it
    R placed it, no stated edge          ->  ABSTAIN    the sibling of a sibling
    D placed it                          ->  ABSTAIN    structurally, it has nothing to state

**COVERAGE WAS THE DECIDING NUMBER, AND IT ALLOWS**: 31.5% of relations placements state their
nearest dimension (22,692 of 72,059) — 19.4% of all placements. **D is 0.0% of 44,666 and cannot be
otherwise**: a sense reaches D precisely BECAUSE it states no relations, which is what `projection`'s
own fallback rule means. So D's abstention is not a policy applied to D; it is what the rule says
when D is what placed the sense.

**Built in `DictionarySpace.place`** (`placement_verdict`), which no longer issues the base floor's
verdict on a population it was never fitted to. **`FAR` is never issued for a placement**: «I cannot
vouch for this» and «the resource says these are opposed» are different statements, and a sense that
states nothing states nothing in either direction.

*One in five readings of an unknown word gets a trusted placement and four in five abstain. That is
the honest shape of what this geometry knows, and it is knowable only because forty placements were
ruled first.*

## AND WHAT IS STILL OWED

- **E1 owes the gloss defect** (dictionary req 23) — D's reading admits the definition's frame words.
  Repairing it would raise D's placements out of ABSTAIN on their own merit rather than by a rule.
- **The sibling fallback is not wrong, it is UNVOUCHED.** Ten of the bar's fourteen good relational
  placements come from it, and they are abstained on today. If E1 ever gives R a way to say «this
  sense is a KIND OF a thing this dimension is also a kind of», those ten become statable.
- **Nothing consumes `place()` yet.** The confidence scalar (parser-compiler req 4) is the first
  caller, and it now has a verdict that means something to read.
