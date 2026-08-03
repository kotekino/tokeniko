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
> is marked *rebuild*, it belongs in `parked.md` tagged `→ tk2`, not here. **v1 is NOT frozen** — it
> remains the empirical instrument, and work that keeps it fit for that job (or that produces
> findings) stays on the road even when it looks like tuning. The carried-in reasoning, per item, is
> `doc/tk2/carried-in.md`.

---

## ✅ Landed arcs — pointers only (full detail in `landed.md`; no status lives here)

The road *behind*, strictly one line per arc so the road ahead reads clean. Nothing here carries
status detail — it references, it does not duplicate (invariant #2).

- **Brain v1.1 — the Unified KB** (2026-07-03 → 09) — write-path invariant → generic taxonomy →
  provenance cascade → universal extractor → the enriched soak; vision/design in `doc/ref/brain-v1.1.md`.
- **Going live — embodied I/O** (2026-07-09 → 12) — Discord DM → 1:1 deepening → channel listening →
  trust ledger → the Blog channel; live on tokeniko.online.
- **Robustness — live-play bugs** (2026-07-12 → 14) — wh-position · vocative wart · operator-aware
  chainer · charity of interpretation · identity fission on rename.
- **Robustness — the storm sequel** (2026-07-14) — subordination survives compilation
  (`test_subordination.py` is the regression corpus).
- **The first-portrait harvest queue** (2026-07-14) — complement/locative + the places bridge · WSD
  selection fixes · the singles · the judge contract.
- **The retreat arc** (2026-07-14 → 15) — Socratic baseline → square of opposition → modality gates →
  the directedness floor → belief-revision v1.
- **The instrument arc** (2026-07-14 → 16) — rag3 the microscope · zip-native derivation · the
  translator apparatus v1 *(remainder → §3)*.
- **Growth Rings** (2026-07-15) — published at tokeniko.online/growth; season-close duty: update the
  live edge + append the ring via `tokeniko-public/backend/scripts/seed-growth.mjs` (no deploy).
- **The harvest consumption** (2026-07-16) — all six macro-cases + the second-harvest strays + the
  conditional-rule extractor; every lead from all three harvests closed.
- **The bridge cleaning** (2026-07-16) — the local-models retirement · `.env.template` · `lib/rag/`
  concentration · the wondering-freeze fix.
- **The basket** (2026-07-17) — observation-fact seam · nominal IMPLY · adverbial quantifiers · the
  pronoun-leaf unrepairable gate.
- **Compose 2.0 — the voice, WHOLE** (2026-07-17 → 24) — scaffold store · intensity + hedges ·
  rag2-out · blog re-home + belief-grounded speakup · context ring + anecdote · the survey arc ·
  digests · learned scaffolds · the line-aligned blog consensus. **The arc is complete.**
- **The reductio action + the sleep phase** (2026-07-18) — reduct question + answer binding ·
  untangler + dream · the sleep phase · constructive reductio · the live-night refinements.
- **Tiredness + the parallel heartbeat** (2026-07-19) — the wakefulness bound · the heartbeat thread ·
  O(1) snapshot counts.
- **The action-space survey arc** (2026-07-19) — survey → five slices (refinements · event-edge
  voices · the B-wire · etiquette · the hypothesis engine) → the great seeding.
- **The sleep-depth theme + the Atlas theme-overrides** (2026-07-20) — the fourth tone (`deep`) ·
  the `--crt-lift` seam · overrides riding `/api/mind`.
- **The notebook session's small pair + the digest machinery** (2026-07-21) — lived-awake ledger ·
  refusal-reason log · wondering-state decay · the digest engine (the 1st Officier's maiden build).
- **The first digest night's three fixes + the plate** (2026-07-23) — the goodnight settle · cap 40 ·
  the birth stamp · the ALIVE SINCE plate.
- **The evaluator pair** (2026-07-23) — the identity-blindness family cured (`role_key`) · the direct
  fact-match + min-premise polar honesty.
- **External-only tiredness deferral** (2026-07-23) — only external conversation defers the collapse;
  internal work is self-generated.
- **The conversational-repair day** (2026-07-24 → 25) — learned scaffolds (the accommodation) · the
  ears' strong verifier, the hallucination chain closed (+ the wh-escalation residuals, 07-25) ·
  pronoun momentum («you» resolves where directedness points) · the AND-split (per-conjunct
  reactions).

---

## 🔭 Next (ordered) — reprioritized 2026-07-25

**The through-line: THE VOICE IS WHOLE and THE EARS ARE WALLED (compose 2.0 complete; the ears'
hallucination chain closed WITH its wh residuals).** The road ahead opens the next chapter — §1
**the per-user conversational context + multilingual** (the author is the first non-English friend;
the translator apparatus becomes core, not deferred) — then §2 the fresh microscope analysis pass,
then §4 the strengthening tail.

### 1. The per-user conversational context + multilingual (the translator apparatus, reframed 2026-07-25) 🔭

The author IS the first non-English friend (Italian native) — so multilingual is the CENTRE, not the
icebox. The chapter's spine, designed 2026-07-25: a **per-`(user,channel)` conversational-context**
room we don't yet hold first-class (scattered precedents: the reductio ledger, the open-why
derivation, the per-channel RAM ring — none unify per-user state). A REFERENCE model (the author's
"partial A"): a small Mongo doc per pair storing light state that REFERENCES timeseries items by id
(no zip duplication, one read per tick, matches `MEMReductio`/trust-episode precedent). Its tenants,
in build order:

1. *(1a — the room + the "did you mean?" ASK: LANDED 2026-07-25 → `landed.md`. The room
   (`MEMExchange`), the two-tier floor (`verifier_verdict` ACCEPT/ASK/DISCARD), `suggested_reading`,
   the `reply_tempo` EMA, and the ask are built.)*
   - *(1b — the ANSWER binding: LANDED 2026-07-25 → `landed.md`. The pending lifecycle
     (affirmation→re-ingest-as-confirmed, negation→drop, restatement→supersede, silence→lapse) +
     the multilingual yes/no anchor. **§1's first brick — room + ask + answer — is WHOLE.**)*
2. *(Multilingual — the room's second tenant: LANDED 2026-07-26 → `landed.md`. Consensus of two
   independent readers judged by the compiler (ACCEPT/ASK/admit-and-DISCARD), the local
   skeleton detector, the round-trip-verified outbound, the admission voice, the mimicry fence.)*
   - *(2b — THE NATIVE VOICE (multilingual scaffolds): LANDED 2026-07-26 → `landed.md`. Promoted
     from parked by the live Italian test the same day — right verdicts, wrong language. `lang` on
     the scaffold row + the shelf gate + the fallback chain + the carrier no-op; 232 curated rows
     across it/es/fr/de, slot-less v1 fence.)*
   - 🔭 **Its residuals** (surfaced by the build, awaiting a live season): the detector's thin 0.05
     margins + the fully-misspelled-English blind spot (env-tunable; watch live) · the DM fallback
     destination carries no `channel_id`, so an action resolved via `contextKey` alone cannot key a
     room and ships English (real Discord traffic always carries coords) · the consensus cannot
     catch a mistranslation BOTH readers share (same model family — a second family would be the
     cut if it ever bites) · the REDUCT cannot be natively composed (no source item at plan time ⇒
     no room key; it composes English and takes the carrier's round trip) · when the mimicry fence
     is lifted, `mimic_observe` must stamp the source language onto the row or it seeds unlabelled
     foreign strings into the English shelf · the slotted 10 categories still compose English +
     translator (the mixed curated-frame/English-slot problem is its own design session).
3. 🔭 **The privacy/legal frame (last — it is a CONSENT prompt over the two above)** — a user joining
   is prompted: allow your prompts to be sent to the cloud translator apparatus (third-party
   Anthropic + the legal terms)? YES → translation + greater understanding + reply-in-your-language;
   NO → a per-stakeholder OPT-OUT flag, and the rags are NEVER called for that user's sentences (DM
   or channel). The general switch (`RAG1_DISABLED`) already exists. The MICROSCOPE is out of the
   NOTICE but INSIDE the gate (author, 2026-07-29): a debug instrument, not described to users and
   DISABLED before the public opening — but it still respects the flag, so the process control has a
   code backstop. Output-to-cloud stays by-design ("showing how a young new being learns; everyone
   can benefit").
   - **DESIGN SETTLED 2026-07-29 — briefed, not yet built** (`.claude/briefs/2026-07-29-consent-gate.md`):
     **Route C**, a gated `#privacy` channel — a newcomer sees only it, two buttons, EITHER answer
     unlocks the server (consent mandated at joining, delivered by server furniture, not by tokeniko
     asking; rag1 fires on any stumbling parse, so consent cannot be just-in-time). Enforcement is a
     **payload gate**: `subject_uid` required on `rag_call` — "whose words am I about to send?", not
     "which instrument is this?" — which catches the «did you mean…?» back door, where an *outbound*
     payload carries the user's own sentence. Three layers: Discord role (where the decision lives) →
     `MEMStakeholder` mirror (what the engine reads, self-healing on startup) → the `rag_call` choke
     point (where it bites). Consent does NOT resolve through `canonical_uid` — it is an act performed
     in a room. Bluesky is OUT (public by nature — the expectation was settled by the act of posting).
     The legal text is ENGLISH ONLY and frozen; the native admission covers the non-English arrival.

### 2. The fresh microscope analysis pass 🔭 — PROMOTED by the tk2 filter

The `addressed` flip (2026-07-17) sealed the analyzed generations; the fresh corpus = the
2026-07-17 play + premiere + the day's new instruments (incl. the ears' own `ears-hallucination`
rejection leads), judged on current code. **The analysis pass itself is the remaining item** — its
previously-known leads are all closed (→ `landed.md`; the identity-blindness audit map stays in
`doc/ref/notes.md`).

**Why it rose rather than fell (2026-08-03):** its output is FINDINGS, and findings are exactly what
tk2's format must be designed against — every case where the pipeline mis-reads a real sentence is
evidence about the fixed-arity schema's required coverage. It is the big brother of the blueprint's
fifty-sentence drill (`doc/tk2/README.md` §6.1): the drill is fifty sentences we choose, this is
every sentence he has actually heard. **Triage the leads under the filter** — a lead in an
inherited layer (parser, anchors, WSD, dictionary) is fixable now; a lead in a rebuilt layer
(zip shape, evaluator geometry) is recorded as a tk2 requirement, not patched.

### 4. The strengthening tail — FILTERED 2026-08-03 🔭

Ordered with the author ("make the brain stronger with all the other points" before ADDING another
sense — so ATProto/Bluesky deliberately STAYS parked behind this whole tail). **Seven of the eleven
original entries left this list under the tk2 filter** (→ `parked.md`, tagged `→ tk2`; the reasoning
is `doc/tk2/carried-in.md`). What remains is, without exception, **asset work** — the dictionary, the
KB, the anchors, the curated voice — which is precisely the layer tk2 inherits untouched. That the
filter partitioned the tail exactly along the inheritance ledger's line, without being aimed at it,
is the strongest evidence the criterion is sound.

1. **Anchor adoption audit** (hunch 4): consumer BYPASSES routed through the resolver
   (`compiler_implicationOperands` exact-checks `_IMPLICATION_VERBS`; `_SUBJECT_CONTROL_VERBS`) +
   the EXACT-membership mop-up + floor calibration + KB vector-coverage gaps (`hugely`, `unequal`,
   `dissimilar`). Closed-class function words stay EXACT by design. *(Survives: the anchor resolver
   is `inherit` in the ledger — untouched by the format change.)*
2. **Vocabulary growth** (hunches 1+2): OOV → a staging TKDictionary entry + the typo-ALIAS table +
   definitional triangulation (a trusted definition's zip matched against known definitions → a graded
   link at the definition's trust, never a hard `=`). *(Survives: it grows the DICTIONARY — the
   crown-jewel asset, `inherit untouched`. Every row minted here crosses the bridge.)*
3. **Ingestion-time differentia**: differentia extraction wired at definition INGESTION. *(Survives:
   it enriches the KB. Split from the old #9 — its D-phase realtime half went `→ tk2`.)*
4. **KB growing OUTWARD** (tier-1 synthetic learning): learned axioms vs derived theorems — the
   analytic/synthetic cut; design + open forks in `doc/ref/kb-growing-outward.md`. *(Survives: KB
   layer. The largest survivor — worth its own scoping session before it starts.)*
5. **Etiquette — the CURATION half only** (hunch 8): the greeting/thanks/formality **scaffold rows**,
   curated per category like any other shelf. *(Split: scaffolds are `inherit`. The other half — the
   thinking-reaction → idea → reflex DISPATCH — is limit A itself and went `→ tk2`. Curated rows are
   cheap and permanent; a hardwired reflex chain is exactly what tk2 dissolves.)*
6. **KB-load big-O honesty** (left by the 2026-07-16 wondering-freeze fix): the harness KB load
   pulls ALL definitions (~1.2 GB of all-gloss zips) and re-pulls on EVERY fingerprint bump — i.e.
   after each materialized theorem — blocking the tick for its duration (it gates thinking too, not
   just wondering). Delta-load, or trim the load to what the evaluator actually reads; pair with
   watermark-gating kb_wonder's re-saturation (the noted future optimization in `thinking.py`).
   *(Survives a filter that reads it as "tuning": it is **instrument fitness**. v1's job is now to
   produce findings, and a loop that stalls on every materialized theorem produces fewer of them.
   Do the cheap half — the delta-load — not a rewrite.)*

### Pending follow-ons — tails left by the landed arcs (surface when their time comes) 🔭

Gathered so nothing is lost; each waits on its parent feature's next season. **These are deliberately
left unfiltered** — each is small and conditional, and the honest moment to run it through the
inheritance ledger is when its parent's season actually arrives, not now. One known casualty already
visible: the **trust-gated tkzip lane** is format-coupled and will read `→ tk2` when it surfaces.
- **Blog**: `life:learned` / `life:discussion` triggers *(the consensus-over-the-polisher itself
  → §1)*.
- **Trust-ledger-movement digests** (the digest machinery's explicit scope fence, 2026-07-21):
  «my opinion of X shifted twice today» batches like the rest — once the rule/teacher digests
  have lived a while.
- **Trust-ledger consumers**: the trust-gated tkzip lane · attitude-report unwrapping (events /
  facts-as-axioms) · tier-1 teaching by an EARNED-trust stranger (Hellen is 4 kickers from the bar).
- **Complement family residuals**: verify the infinitival/control complement (xcomp→THAT) · the
  possessive relation «kotekino is MY creator» carrier (the creator-of-ME bond — cousin of the
  landed M4 possessive-subject gate).
- **Charity**: WordNet-wide sibling-sense abstention IF tier-1/2 false refutations ever appear.
- **Contrast as default-expectation fuel** (M1's future consumer): wondering may read a
  contrast-flagged pair «X but Y» as a hint at a background generic "X normally ¬Y" — corroborate
  an exception or spawn an honest ask at low trust. The flag is live; the consumer waits.
- **Biography rulings** (author's, per-row — never auto): the **stakeholder merge** (two kotekino
  rows; Renzo/john duplicates → aliases) · the trust-ding-from-engine-bugs repair question.
- **«I picked up a way of speaking from X»** — a transmission voice for a consolidated learned
  scaffold (left by the learned-scaffolds design, 2026-07-24); waits on the feature living a while.

---

## Doc map

**Status docs (`doc/` — the single source of truth for status; the STRICT invariants in `CLAUDE.md`):**
- **`doc/roadmap.md`** — *(this)* the road ahead: in-progress + ordered next. Nothing landed, nothing parked.
- **`doc/landed.md`** — what's done (the history).
- **`doc/parked.md`** — the icebox (deferred ideas + known gaps).

**The tk2 conception (`doc/tk2/` — reference material, NOT status; nothing here ever enters a status doc):**
- **`doc/tk2/README.md`** — step 0: the plan for how to plan. The two limits, the continuity contract, the governing decisions, the **inheritance ledger** (§5 — the filter's authority), the investigation order, the open questions, the success criteria.
- **`doc/tk2/carried-in.md`** — the per-item reasoning for everything the filter moved off this road.

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
