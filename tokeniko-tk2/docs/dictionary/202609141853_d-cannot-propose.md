# dictionary — D'S NEIGHBOURHOOD CANNOT BE TUNED, 2026-09-14 18:53

*Found at E1d T2 and benched here on the Captain's order. Brain req 12 says «memory proposes by
cosine»; the question this answers is WHICH cosine — and the answer is not D's.*

---

## THE SYMPTOM

```
neighbours('eat.v')   via D                    via R
   lead.v      +0.728      consume.v   +0.559
   bring.v     +0.728      deplete.v   +0.610
   overfamiliar.a +0.728   feed.v      +0.341
   cotton.v    +0.714      crop.v      +0.344
   except.v    +0.716      drink.v     ...
```

## THE CAUSE, measured

D's cosine asks *«which common gloss word do you contain»*. `eat.v` («take in solid food») shares
**49 of its ~50 columns** with `lead.v` and `bring.v`, because all three definitions contain **«take»**.
And **62% of D's cells sit at the cap** (293,994 of 473,262 at exactly 0.5), so the ranking has almost
nothing to order by. D's own row degree is mean 104, median 79 — and `sleep.v` has **two** cells.

## THE BENCH *(approved by the Captain before any candidate was tested)*

1 precision@10 against gold · 2 junk rate · 3 tiny-gloss keys · 4 out-of-base placement ·
5 the bar must not degrade · 6 speed.

**Gold is SYNONYMS and SAME-HYPERNYM SIBLINGS** over 300 sampled keys (3,542 keys have gold, median
11 neighbours). **Junk** = the pair's only shared gloss words are in the loudest 1% of the gloss
vocabulary (`use`, `make`, `act`, `especially`, `person`, `state`).

| candidate | precision@10 | junk@10 | tiny-gloss | ms |
|---|---|---|---|---|
| D cosine (today) | 5.9% | 36.6% | 40/40 | 1.6 |
| A — direct D cell | 4.2% | 31.5% | 39/40 | 0.0 |
| B — `min_shared=2` | 4.7% | **9.1%** | 40/40 | 1.7 |
| C — uncapped (`scale=1, cap=1, floor=0`) | 6.3% | 33.8% | 40/40 | 1.6 |
| D — `idf` | 6.0% | 35.8% | 40/40 | 1.5 |
| E — sense projection | 3.1% | **1.4%** | 39/40 | 1.5 |
| **F — R cosine** | **28.7%** | 9.8% | 40/40 | 2.0 |

**NO VARIANT OF D HELPS.** Every one lands within noise of today: the best, uncapped, is 6.3% against
5.9%. **This independently confirms the 2026-08-25 IDF verdict at a second and different gate** — it
was rejected then on the bar, and it is no better here on neighbour quality.

**THE CAVEAT, stated rather than buried:** the gold is built from WordNet relations and R is built
from WordNet relations, so **F is advantaged by construction**. Siblings are not direct R edges (they
emerge at second order), but the gold is still R-shaped. The eyeball test agrees with the number,
which is the most that can be said: R proposes *consume, eating, deplete, drink, crop, waste, feed*
for `eat.v`, and D proposes *lead, bring, overfamiliar, except, dispute, cotton*.

**AND THE SENSE PROJECTION IS THE CLEANEST BY FAR ON JUNK — 1.4%** — at the lowest precision. It is
also the only candidate that works for a word the base does not contain, which is what `place()` and
the semantic catch already do.

## WHAT IT COSTS TO ACT ON

R is silent on **343 of 4,555 rows (7.5%)**, so an R-first proposer needs a fallback for those. D
remains the only thing that speaks there — which is the argument for keeping it as fallback rather
than removing it.

## THE CONSEQUENCE BEYOND THE DICTIONARY

**tkzip requirement 11** says a role stores the D-side geometry and that retrieval is topical cosine
over it. If D's cosine is this noisy, that requirement rests on something that does not hold —
flagged in `../tkzip/requirements.md` rather than designed around quietly at E3.

*The measurement is `$CLAUDE_JOB_DIR/tmp/dbench.py`'s; it reads the body read-only and rebuilds each
candidate D through `distribution.build`, so every column is the real builder rather than a
re-implementation.*

---

## THE RULING — R ONLY, NO FALLBACK *(the Captain, 2026-09-14)*

Asked whether to adopt R-first with D as the fallback, or R alone: **«R only, no D fallback».**

**AND THE MEASUREMENT VINDICATES IT.** The fallback was worth less than the earlier figure suggested:

- **R is silent on 14 of 4,555 dimensions — 0.3%**, not the 7.5% first quoted. That number was the
  manifest's `r_silent_rows`, counted BEFORE gloss references were mined into R; most of those rows
  now state something. The fourteen: `bitter.r · boiling.r · east.r · express.r · first.r · iron.a ·
  last.r · little.r · model.a · precious.r · sand.v · signal.a · surface.a · though.r`.
- **For those fourteen, D's cosines are +0.000.** The «fallback» was `argmax` over zeros — the first
  candidate, dressed as a measurement. Removing it costs nothing and stops one class of wrong answer.

**WHAT CHANGED IN THE CODE.** `neighbours()` defaults to R and returns EMPTY where R is silent;
`nearest_anchor()` follows the same rule and returns `None`. D is still reachable by asking for it,
because «whose definitions look like this one» is a real question — nothing defaults to it.

**THIS NARROWS «NEVER-MISS», deliberately.** The semantic catch used to name an anchor whatever
happened. It now refuses where R is silent, joining the two refusals it already had (the key is not a
dimension; no anchor is). A caller that must always have an answer has the sense layer, which is
where arbitrary input belongs anyway.

**NOT A COST OF THIS RULING, and worth stating because it looks like one:** `dog.n`, `happy.a` and
`devour.v` propose nothing — they are **not dimensions**. The base is 4,555 closure keys, not all of
English, and those words reach the space through `place()` and the sense layer. That is a different
fact from R being silent.

**STILL OPEN, flagged rather than decided:** `place()` and `project()` still read the DISTRIBUTIONAL
half of a sense, because **40.2% of senses carry no relations at all** (48,416 of 120,475). Reading
them relations-only would place nothing for two senses in five — a different and much larger silence
than 0.3%, and its own ruling.
