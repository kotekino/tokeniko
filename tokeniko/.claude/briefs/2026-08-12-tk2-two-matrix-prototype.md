# BRIEF — tk2 prototype: the two-matrix base + a CLI to interrogate it

*Captain's ask, 2026-08-12, at the end of the dictionary-review session. Scope is PROTOTYPE: quick,
throwaway-able, in the sandbox. It exists to make the two-matrix idea touchable before it is ruled on.*

## Why this exists (read `doc/tk2/dictionary-review/` first — notes + requirements)

The measurement that forced it: **`eat` and `food` have NO WordNet relation between them.** A
relations-only matrix scores them 0.000; the whole nearness the Captain refused to lose is carried by
gloss overlap, i.e. co-occurrence. So requirement 2 (eat stays near food) and requirement 10 (density
from relations, never co-occurrence) cannot both hold in ONE matrix.

The proposal on the table — **two matrices, consulted for different questions**:

| | R — relational | D — distributional |
|---|---|---|
| source | WordNet edges only (`entails`, `causes`, troponymy, `verb_group`, `similar_to`, `attribute`, antonym, derivational, taxonomy) | gloss overlap (co-occurrence) |
| density (measured, 975 dims) | 1.30% | 24.9% |
| sign | **signed** — antonyms are negative and SURVIVE | unsigned, positive mass only |
| answers | opposition, entailment, causation, is-a, manner | topicality, aboutness, relatedness |
| measured failure | `eat~food` = 0.000 | `enter~leave` = **+0.519** (the antonym sign is drowned) |

Both already exist as runs in the sandbox: `r1` (blended) and `r2-nogloss` (R alone). The prototype's
job is to stop treating them as two settings of one thing and build them as **two collections**.

## Deliverable A — the new base, in `tokeniko_tk2`

- Two collections, e.g. `base_relational` / `base_distributional`, same key space (POS-split keys:
  `eat.v`, `food.n`), same dimension order, so a query can consult either or both.
- Keep the per-cell provenance already in `scripts/tk2/tk2_matrix.py` (`edges[other] = {w, rel}`) —
  requirement 18: every cell states which relation produced it.
- Membership defect is IN SCOPE if it is cheap: `want`, `swallow`, `chew`, `negation`, `runway` are
  not base words, so `eat entails swallow` is currently inexpressible. Adding the bar's missing words
  as dimensions is a legitimate prototype move — but SAY SO in the run manifest, do not smuggle it.
- Read-only on `tokeniko`. The sandbox guard in `tk2_common.tk2_db()` stays.

## Deliverable B — the CLI, which is the real point

**This is the prototype of the tk2 API surface.** Use cases to expose, one subcommand each:

1. `near <word>` — nearest neighbours, and **from which matrix**. The interesting output is where R
   and D disagree.
2. `rel <a> <b>` — the relation between two words: the signed R value, the D value, and the named
   edge that produced each. This is the interrogation requirement made usable.
3. `opposite <word>` — the antonym column-read, on R (where the sign survives). Compare against the
   live `utils_antonyms` on the Jurassic base.
4. `effect <verb>` — what the verb ENTAILS/CAUSES. Expect mostly empty: the measured finding is that
   the effect axis does not exist in WordNet. An honest empty is the correct output, not a fallback.
5. `bar` — re-score `tk2_config.PAIRS` against whatever the base currently is.

Design the subcommands as if they were endpoints, because they are the draft of the tk2 API. Honest
abstention over a plausible number, everywhere (the charter's invariant).

## Rules that do not bend

- **The bar (`tk2_config.PAIRS`) was declared before any matrix existed.** Do not edit a pair to make
  a result look better. If a pair is genuinely wrong, change it and say so out loud.
- Writes only to `tokeniko_tk2`. The biography is never touched.
- Nothing here enters `roadmap.md` / `landed.md` / `parked.md` — `doc/tk2/` is reference material.
- Prototype means quick. It does NOT mean cheapening the artifact — if a shortcut hides a real
  finding, it is the wrong shortcut.
