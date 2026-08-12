# scripts/tk2 — the dictionary-review instrument

The tokeniko-2 blueprint's first **measuring** tool. Conception lives in `tokeniko/doc/tk2/`; this
directory is what settles the doubts that conception raises — the Captain's ruling of 2026-08-12:
*verify instead of guessing; code, drafts and tests are allowed as instruments for DEFINING
requirements.*

**Safety.** Read-only on the body's knowledge base (`tokeniko.base`, `tokeniko.dictionary`). Every
write is fenced into the sandbox `tokeniko_tk2` by a guard that refuses any other database name. No
biography is touched, ever.

## The loop

```bash
# 1. the subset — definition graph, closed sets, seed closure, what the POS split costs
python scripts/tk2/tk2_subset.py                    # report only
python scripts/tk2/tk2_subset.py --apply --name v1  # store it

# 2. the matrix — rows = dimensions, POS-split, every cell tagged with the relation that made it
python scripts/tk2/tk2_matrix.py --subset v1 --run r1 --note "all relations on" --apply
python scripts/tk2/tk2_matrix.py --subset v1 --run r2-nogloss --weight gloss_overlap=0 --apply

# 3. the bar — declared in tk2_config.PAIRS BEFORE any matrix existed
python scripts/tk2/tk2_probe.py --run r1 --compare r2-nogloss

# 4. the two-matrix base — the prototype that finding 4 forced (stage 2b)
python scripts/tk2/tk2_build2.py --apply

# 5. interrogate it — the draft of the tk2 API surface
python scripts/tk2/tk2.py bar
python scripts/tk2/tk2.py near sleep.v
python scripts/tk2/tk2.py rel eat.v food.n
python scripts/tk2/tk2.py opposite leave
python scripts/tk2/tk2.py effect eat
```

Iterating means editing **`tk2_config.py` only** — seeds, relation weights, the bar — or passing
`--weight rel=value` for a one-off run. Runs are named and kept side by side, so a change is
*compared* rather than remembered.

## What lives where

| file | what it decides |
|---|---|
| `tk2_config.py` | seeds · relation weights · the bar. The only file you edit between iterations. |
| `tk2_common.py` | mongo plumbing + the sandbox guard, the base, definition-to-base-words reduction, POS keys |
| `tk2_subset.py` | stage 1 — the cherry-picked subset (the Captain's method, implemented literally) |
| `tk2_matrix.py` | stage 2 — the candidate matrix, with per-cell provenance |
| `tk2_probe.py` | stage 3 — scores the bar, Jurassic base vs candidate runs |
| `tk2_build2.py` | stage 2b — the TWO-matrix base (R relational + D distributional) over one key space |
| `tk2.py` | the CLI over the two-matrix base — `near` / `rel` / `opposite` / `effect` / `bar` |

## Sandbox collections (`tokeniko_tk2`)

- `subsets` — `{name, words, keys, seeds, senses, depth}`
- `base_candidate` — one doc per dimension per run: `{run, key, word, pos, index, vector, edges}`,
  where `edges[other] = {w, rel}` names the relation that produced the value
- `runs` — the manifest of each iteration: weights, density, per-relation cell counts
- `base_relational` / `base_distributional` — the two-matrix base: same shape as `base_candidate`,
  keyed on `base` instead of `run`. **R** is named WordNet edges only (signed, ~1.0% dense); **D** is
  gloss overlap only (unsigned, ~24% dense). One key space, one dimension order, both.
- `base2_manifest` — the shared manifest of a two-matrix base: the ordered key list, the two weight
  dicts, the density stats, the wup decision, and `added_words` — every dimension the membership
  repair introduced, declared rather than smuggled (requirement 15).

## The rule that makes the numbers worth anything

**The bar is declared before the matrix exists.** `tk2_config.PAIRS` was written from the dialogue,
not from a result. Changing a pair after seeing a score is how a review talks itself into success —
if a pair must change, change it and say so out loud in the notes.

## Stage 2b — why there are two matrices

Finding 4 of the review is not a tuning problem, it is a contradiction: **`eat` and `food` have no
WordNet relation**, so a relations-only matrix scores them 0.000, and requirement 2 (eat stays near
food) cannot hold in the same matrix as requirement 10 (density from relations, never co-occurrence).
Blending them into one float destroys the antonym sign *and* hides the provenance.

`tk2_build2.py` therefore builds both geometries over **one key space**, and `tk2.py` consults them
separately. Every answer the CLI prints names the matrix that gave it — R, D, or J (the Jurassic
2925, shown only for comparison). Where R has nothing to say, it says so; it never falls back to D
and hands back a topicality score dressed as a relation. That rule is the point of the prototype.

The membership repair (`tk2_config.BASE2_ADDED_WORDS`) adds `want`, `swallow`, `chew`, `runway`,
`negation` as dimensions — words the bar names that the Jurassic 2925 lacks. It is a legitimate
prototype move **only because it is declared**: the builder writes each one into the manifest's
`added_words`, so no result can quietly rest on a word that was smuggled in.
