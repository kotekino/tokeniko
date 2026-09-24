# The welded table — an order that never decided, and a frame that belongs in the db

*2026-09-24. The frame/knowledge audit (`202609220930_…`) left `UD_DEP_TO_ROLE` split and waiting
on the Captain: WHICH roles a UD relation admits read as frame, the BEST-FIRST ORDER of each tuple
as a claim about English. Before he ruled, the order was benched.*

## The bench — `tools/dep_order_bench.py`

`select()` uses each tuple twice: as a FILTER (only admissible roles survive) and as a TIE-BREAK
(`sorted(kept, key=allowed.index)`, then `narrowed[0]`). The bench re-derives `select()` step by step
(0 mismatches with the real one over 1116 live calls) and separates two kinds of tie:

- **TUPLE tie** — survivors with different roles, decided by `allowed.index`
- **TABLE tie** — same role, or no dep constraint, or a filter that emptied and fell back: decided
  by the migration's ROW ORDER, which nothing documents as meaningful

| run | drill | fixpoint | UD gate |
|---|---|---|---|
| baseline | 66 · 4 · 17 | 69 · 17 MOVED · 1 SILENT · 74 whole | 34 · 0 wrong · 11 |
| tuple tie refused | no change | no change | no change |
| **every tuple reversed** | **no change** | **no change** | **no change** |
| any tie refused | 67 · 4 · 16 | 69 · 17 · 1 · 73 whole | no change |

**The order never decides.** Four live calls were tuple-decided, all the same `who` (`dere-4`,
`ud-13`), and `read()` re-picked every one by clause before the compiler saw it. Statically, 14 of
the 28 order-decided groups are the wh-trio and unreachable on the skeleton path; the other 14 speak
only when the tagger and the table disagree about a label.

**The one wrong pick is a table tie, not a tuple one.** `t-ng-4` «No, some software is a mind and
some is not»: stanza reads «No» as `INTJ`/`discourse`; `discourse` is not mapped and `INTJ` empties
the POS filter, so the first row wins and «No» becomes a NEGATIVE QUANTIFIER over `mind.n`. The
forgiveness the header extends to a «genuine label disagreement» produced a confident wrong reading
— what req 8 forbids. The read-whole population counted it as whole.

## The ruling — frame is not «what goes in code» *(the Captain)*

> *«Frame can also be db, nothing forbids it. The difference between frame and knowledge is: frame
> will change ONLY if we discover a bug or malfunction or a wrong assumption, so we have to FIX it.
> Knowledge changes over time based on learning, experience and how tk2 changes his mind. So you
> need to make me understand why code would be better than db, even if we assume that it's frame.»*

The QM's case for code was proximity to the one reader and a db-free test — conveniences, not
arguments about what the thing is. The case for the db was concrete and already paid for: the tuples
name OUR roles, which are rows, so `db/0028`'s `fused_quantifier` needed a code edit before the
station admitted it; and every other fact about a UD relation already lives in
`language_ud_readings` (`db/0032`). Written into the root `CLAUDE.md`.

**Ruled:**
1. the admissible sets move to `language_ud_readings` as a fourth question, `admits_roles` (`db/0034`)
2. the ranking is DELETED, not moved — nothing measured supports it
3. a tie that neither the table nor the clause settles ABSTAINS, the emptied-filter fallback
   included; `read()` chooses among the candidates rather than correcting one pick

**Cost, stated:** read-whole 74 → 73 (`t-ng-4`'s «No» goes unplaced — the 74 was counting a
misreading), and every former quiet pick is now an abstention. **Parked:** whether discourse «No»
(an answer particle) needs a reading of its own — knowledge, a later migration; and `t-ng-4`'s
second conjunct «some is not», lost in every run — recorded; with «No» unplaced it has left the read-whole population.

## Built — the same day *(1st Officier)*

`db/0034` (UD readings v2: v1 carried forward, 19 `admits_roles` rows checked against the deleted
map) · `UdReadings.admits_roles` with the subtype fallback decided per QUESTION, not per row ·
`ClosedClasses.candidates()`; `select()` = candidates, then settled only if one reading survives ·
`read()` lets the clause settle the wh-trio among the candidates.

| | before | after |
|---|---|---|
| drill | 66 · 4 · 17 | **67 · 4 · 16** — only `t-ng-4` moved |
| fixpoint | 69 · 17 · 1 · 74 whole | **69 · 17 · 1 · 73 whole** — `t-ng-4` leaves the population |
| UD gate | 34 · 0 · 11 | 34 · 0 · 11, case by case identical |

**Every change is a removal**: statically 43,422 (form × dep × upos × context) combinations go from
a pick to an abstention and ZERO change a role. Live, 12 calls leave several readings: 7 settled by
the clause (`who`), 5 abstain (`t-ng-4`'s `no`, `t-dc-5`'s `where` — the latter's zip byte-identical,
the root predicate path reads `where.r` itself).

**A reading is `(role, compiled)`**, the stricter definition — measured equal to `role` alone on
today's table (no form has two same-role rows with different `compiled`), so a future one abstains.

**One deviation — CONFIRMED by the Captain, 09-24.** The clause may settle the wh-trio with a row OUTSIDE
the dep's admissible set — today's behaviour. Confining it breaks «whether»/«if» on a complement
(`mark` does not admit `interrogative`) and «the day WHEN…» (`advmod` does not admit `relative`); on
the three corpora it moves nothing. Read plainly: **the clause is the stronger witness, and the two
sets are incomplete curation.** Left unconfined; the alternative is two curation rows.

**Recorded, not acted on:** only 5 of the 19 sets earn their keep on the corpora (`advmod` · `mark` ·
`case` · `compound:prt` · `expl`) — a curation question, not evidence against the rest · `mark`
names `complementizer`, which no row holds, transcribed verbatim and inert · the `Compiler` reads the
migration's readings even when handed a live table — pre-existing.
