# tokeniko — roadmap (the road ahead)

> One ordered place for *what's in flight and what's next* — the REAL pipeline, nothing else. **History
> → `landed.md`** · **icebox → `parked.md`** · **design detail → `doc/ref/notes.md`**. The **why** is
> `VISION.md`; the **how** lives in `CLAUDE.md`, `brain/README.md`, `doc/ref/notes.md`, and the code. When
> status and any other doc disagree, **this file (+ `landed.md`) wins** — check/update it after **every
> commit**. Keep entries **terse** (one line of what + the key term/file).

Legend: 🔄 in progress · 🔭 next · ✅ done  ·  *(done → `landed.md` · parked → `parked.md`)*

> **⚠️ THE tk2 FILTER (author's ruling, 2026-08-03) — read before adding anything here.** Since
> `doc/tk2/` opened, this road is filtered by ONE criterion: **work that builds an ASSET migrates to
> tokeniko 2; work that builds MACHINERY gets rebuilt there.** Assets = the dictionary, curated
> senses/scaffolds, the KB, the anchors, findings, tests. Machinery = anything coupled to the TKZip
> format or to hardwired behaviour (the two limits — `doc/tk2/README.md` §1). Before an item enters
> this file, run it through the inheritance ledger (`doc/tk2/README.md` §5): if the layer it touches
> is marked *rebuild*, it belongs in `parked.md` tagged `→ tk2`, not here.
>
> **SHARPENED 2026-08-12 (the author):** the filter now has a second, simpler blade — **what makes v1
> better and BUG-FREE is welcome; NEW FEATURES go to tk2.** A repair keeps the empirical instrument
> fit; a new capability built here is built twice. This emptied §4 down to one item and moved five
> brain/behaviour follow-ons. **v1 is NOT frozen** — it
> remains the empirical instrument, and work that keeps it fit for that job (or that produces
> findings) stays on the road even when it looks like tuning. The carried-in reasoning, per item, is
> `doc/tk2/carried-in.md`.

---

## ✅ The road behind

In `landed.md`. Not mirrored here — the roadmap is the road *ahead*.

---

## 🔭 Next (ordered) — refiltered 2026-08-03

**The through-line: THE VOICE IS WHOLE, THE EARS ARE WALLED, THE DOOR IS GATED — AND THE BODY IS
HIS OWN.** §1 closed 2026-08-03 with the consent gate; **§0 the body landed 2026-08-08, its deploy loop closed 08-09** (→
`landed.md`) — he now runs 24/7 on his own machine and gets himself up after a power cut. The road
ahead is **§2 the fresh microscope analysis pass** — promoted because its output is FINDINGS, which
feed both v1 and the tk2 blueprint — then the single item left in **§4**. Since 2026-08-12 that is
nearly all of it: **tk1 stops growing and becomes only an instrument.** Every new capability lives in
the blueprint now; what remains here is the microscope, one audit, and a list of bugs.

### 2. The fresh microscope analysis pass 🔭 — IN FLIGHT since 2026-08-10

**113 real leads → 77.** Corpus: `tkzipdebug`, sealed by the `addressed` flip. Of 583 rows only the
`mismatch` ones are leads — the rest are journeys rag3 judged fine. Worked by severity × count ×
cheapness; closed clusters and their evidence → `landed.md`.

**Open, by cluster:** C4/C5 wrong-structure 21 *(the attitude-distribution and infinitival-IMPLY
halves are diagnosed → Pending follow-ons)* · C8 the 20 `ears-hallucination` rows — **not bugs**, rag1
correctly REFUSING, i.e. the parser-coverage corpus tk2 wants · C7/C9 dropped-content 8 · C6
missed-negation 5 («I am not» compiles as an affirmation) · 5 wrong-sense residues (three are `-ing`
nominalizations, one the identity bridge) · 4 old singletons.

**The operating rules** *(the general ones are under Standing practice)*:
- **Triage under the tk2 filter** — a lead in an inherited layer (parser · anchors · WSD · dictionary)
  is fixable now; one in a rebuilt layer (zip shape · evaluator geometry) becomes a tk2 requirement,
  never a patch. Its output is FINDINGS, and findings are what tk2's format must be designed against.
- **TWO SOURCES, one pass** (the author's «we do debug in one batch»): rag3's machine leads, and the
  hand-logged findings in `doc/ref/test-feedback.md` — behaviour bugs rag3 structurally cannot see,
  since it judges a sentence against its digest and never sees what he then DECIDED to say.
- **A hand-written finding must NEVER be inserted into `tkzipdebug`** — that collection is rag3's own
  output, and its dedup counts any row as judged, so a hand row corrupts the oracle's record of itself.
- **The corpus grows while we work** (he is alive and talking), so the raw count understates progress.

**A bar that cannot be raised by rule:** gerund-vs-progressive is NOT syntactically separable on this
pipeline — 95 sentences, every candidate signal killed by ordinary English («learning is happening» is
progressive; «my goal is learning japanese» is nominal *with* an object). Semantic, or → tk2.

### 4. The strengthening tail — ONE ITEM LEFT 🔭

*Emptied 2026-08-12 by the author's sharpened filter (see the header): **repairs keep the instrument
fit and stay; NEW CAPABILITY goes to tk2**. Vocabulary growth · ingestion-time differentia · KB
growing outward · etiquette-protocol all → `parked.md` tagged `→ tk2`, reasoning in
`doc/tk2/carried-in.md`. What survives is the one item that fixes something already built.*

1. **Anchor adoption audit** (hunch 4) — consumer BYPASSES still routed around the resolver
   (`compiler_implicationOperands`, `_SUBJECT_CONTROL_VERBS`) · the exact-membership mop-up · floor
   calibration · KB vector gaps (`hugely`, `unequal`, `dissimilar`). Closed-class words stay EXACT.
   *(A repair: the resolver exists and is inconsistently used.)*

### Pending follow-ons 🔭

*One line each: what + where. The reasoning lives in `landed.md`, the commit, or the code comment at
the site — never duplicated here. Each waits on its parent's next season; they are deliberately
UNFILTERED (the honest moment to run one through the inheritance ledger is when its season arrives).*

**Parser / WSD — the §2 residue**
- **The attitude scope does not distribute over coordination** (2026-08-12, diagnosed not fixed):
  `c_statements.py:333` sets `result[0].attitude` only, so a conjunct escapes the wrap and is
  asserted as FACT. «I think you are a software and you are a mind» · nominal coordination loses the
  attitude entirely · an explicit `that` changes nothing. `_stamp_cause` below it already solves the
  same traversal for the causal role. **Boundary risk: over-wrapping is worse than the bug.**
- **Infinitival «to» → spurious IMPLY** (2026-08-12, diagnosed): `constants.py:72` maps `to` to
  `FINAL` (purpose), but the same word is the bare infinitive marker. «I want to sleep», «nice to
  meet you» compile a conditional nobody uttered. `xcomp`/`acl` are safely separable (~13 hits in
  896 memory items); `advcl` is not — that half → tk2.
- **The modifier surface bypasses the WSD ladder — HELD** (measured 2026-08-12): wiring it in was a
  net regression, 21 fixed / 12 broken. Census + the three causes are in the code comment at
  `parser_getPropertyMeaning`. The real item is a **modifier-shaped ladder** (a Lesk floor for thin
  contexts, context-scoped curation). Batch 5 carries three rulings for it, inert until it lands.
- **The compound-participle bucket**: «the running water» → `run.n.05` *(American football)*,
  «a flying machine» → `fly.n.01` *(the insect)*. Tagged `NOUN/compound`, no modifier sense in the
  noun pool → only routing to the a/s pool can fix it. Also «the deceased person» (vector-fallback
  fabrication) and «the stolen bike» (mute, no rows in any POS).
- **A coordinated modifier resolves then is DROPPED** before the zip — compiler-side → dropped-content.
- **Eventive passives read as states**: «the door is opened by Mari» → `open.a.05`. VBN separates
  tense-form, not state-vs-event. A tighter gate could exclude `obl:agent`/`aux:pass`. No test yet.
- **Three vocative residues the C2 fix does not reach**: «tokeniko is the sky blue?» (needs an
  INVERSION test, not a tag read) · «tokeniko are all minds machines?» (a separate parse bug) ·
  «tokeniko does a cat think?» (a stray `do.v.03` leaf — milder).
- **Complement family**: verify xcomp→THAT. *(The possessive-relation carrier went `→ tk2` — a new
  carrier, not a repair.)*
- **Charity**: WordNet-wide sibling-sense abstention IF tier-1/2 false refutations appear.

**Tooling**
- **A real `/api/v1/health`** — the deploy probes `/openapi.json`: honest but oblique, and it cannot
  say the mind is *sane*. Three lines. Its "defer past the transplant" blocker expired 2026-08-08.
- **`deploy.sh`**: the dependency check matches `pyproject.toml` by PATH (a comment-only edit costs a
  full lock reinstall) · step 4 should pre-check untracked collisions instead of dying on a raw git
  error. **Recurs**: anything created on the body and later committed from the workshop collides.
- **Fixture sentinels are shared across test files** (the orphan hazard itself is cured): `_POISON_*`
  is identical in `test_sleep_phase`/`test_untangler` and both delete by it, so they can never run in
  parallel. Fix: own sentinels per file, and conviction selecting on **provenance**.

**Brain / behaviour**
- **Biography rulings** (author's, per-row, never auto): the stakeholder merge (two kotekino rows;
  Renzo/john duplicates → aliases) · the trust-ding-from-engine-bugs repair question.
- **Multilingual residuals** (wait on a LIVE SEASON, not on work): thin 0.05 detector margins + the
  fully-misspelled-English blind spot · the DM fallback carries no `channel_id` · the consensus
  cannot catch a mistranslation BOTH readers share · the REDUCT cannot be natively composed · when
  the mimicry fence lifts, `mimic_observe` must stamp the source language · the slotted 10 categories
  still compose English + translator.

**Standing practice** *(not a task — a rule the work earned)*
- **Before any curation batch reaches a deploy**: grep the suite for every DISPLACED sense and
  de-hardcode through the `sense_of` fixture. Batch 3 moved 21 lemmas; the fast lane was green and
  the deploy gate still caught 5 frozen `wrong.a.02` assertions.
- **Date-check to form a hypothesis, REPLAY to settle it.** `addressed=false` means nobody flipped
  the flag; a date proves nothing either way.
- **Build an adversarial set from the anchor table's own entries**, never from remembered words — a
  control has to contain the thing at risk.

## Doc map

**Status docs (`doc/` — the single source of truth for status; the STRICT invariants in `CLAUDE.md`):**
- **`doc/roadmap.md`** — *(this)* the road ahead: in-progress + ordered next. Nothing landed, nothing parked.
- **`doc/landed.md`** — what's done (the history).
- **`doc/parked.md`** — the icebox (deferred ideas + known gaps).

**The tk2 conception (`doc/tk2/` — reference material, NOT status; nothing here ever enters a status doc):**
- **`doc/tk2/README.md`** — step 0: the plan for how to plan. The two limits, the continuity contract, the governing decisions, the **inheritance ledger** (§5 — the filter's authority), the investigation order, the open questions, the success criteria.
- **`doc/tk2/carried-in.md`** — the per-item reasoning for everything the filter moved off this road.
- **`doc/tk2/ideas.md`** — the Captain's open bag of v2 conception ideas (no status, never scheduled here).

**Reference docs (`doc/ref/` — extended context per task + future-reference material; NOT status):**
- **`doc/ref/brain-v1.1.md`** — the Brain v1.1 **vision + design** (the Unified-KB reframe: everything-is-reasoned-over-TKZip, write-path invariant, universal gate, trust-by-source; + the #1–#6 findings). The conceptual center.
- **`doc/ref/notes.md`** — design notes & findings (phased plan + reasoning-engine brainstorm + parser/compiler review).
- **`doc/ref/test-feedback.md`** — the living empirical fragility log (observed → diagnosis → action).
- **`doc/ref/kb-growing-outward.md`** — the "synthetic learning" design (analytic/synthetic cut).
- **`doc/ref/paper_outline.md`** — the paper (external artifact).
- **`doc/ref/deploy-body.md`** — the RUNBOOK for tokeniko's own machine (the Mac mini body): all-in-Docker, LAN-only, the MacBook as workshop; the load-bearing facts, the biography transplant, the deploy loop.

**Root:**
- **`VISION.md`** — the why (north star).
- **`brain/README.md`** — the brain's orchestration + meta-language spec.
- **`CLAUDE.md`** — the architecture / code layout + ground rules (not status).
