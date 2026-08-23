# tokeniko 2 — THE EXECUTION PLAN

*Phases 2+3 of «the road to the build» (README §9), fused deliberately: the epics with their
dependencies AND their task breakdown, in one document. Written 2026-08-23, the day phase 1 closed at
sixteen of sixteen. This file is the context-keeper across sessions — verbose where precision pays.
The concise, checkable mirror is `roadmap.md`; what finishes moves to `landed.md` (same status
invariants as tk1's trio: one item, one status, one doc; reconcile at every commit).*

**How to read this plan.** Each epic names: its goal, what it depends on, the tasks (mirrored in
`roadmap.md`), the requirements it answers to (its acceptance contract), and what carried-in/ideas
items it absorbs. Officer briefs are cut FROM this file at dispatch time, per task — never written in
advance (they'd stale). The standing laws apply throughout: sandbox until go-live (the guard),
`--apply`-class writes are the Captain's hand, commits on his yes, the biography is sacred, policy
declared before results.

**The amendment is structural:** between epics run **vertical proof slices** — one sentence driven
end-to-end as early as dependencies allow, landing under the Captain's eye before the next stretch.
Three are planned (PS1 after E4, PS2 after E7, PS3 after E8); more may be cut in if a seam smells.

**The three success tests to keep in view** (blueprint README §8): the **A test** (a behaviour we
did not anticipate, derivation inspectable), the **B test** (two arbitrary sentences compared by
uniform numeric operations, no shape-branching code), the **step-7 test** (a seeded rule revised on
evidence and trust, no hand edit). The coverage bar (fifty-sentence drill) gates E3; the
no-regression ratchet (v1's corpora) gates E9.

---

## The dependency spine

```
E0 keel ──► E1 dictionary ──► E2 format ──► E3 station ──► E4 evaluator ──► PS1
   └──► E5 micro-nn (parallel after E0, first instance lands with E3/E4)
PS1 ──► E6 mind (rules + brain) ──► E7 heart ──► PS2 ──► E8 voice & ears ──► PS3
PS3 ──► E9 translation night ──► E10 embodiment & window
```

E5 runs beside the spine (its consumers arrive with E3–E8). E1 and E2 overlap partially — E2 needs
only E1's *key convention* (POS-split sense keys), not the full base. Everything else is ordered.

---

## E0 — The keel *(data-modeling + datatier + repo scaffold)*

**Goal:** an empty body that boots — loads parameters from the db, ticks, and can be deployed by
migration. The floor every later epic writes on.

**Answers to:** data-modeling reqs 1–6 · datatier reqs 1–6 · body reqs 2–4 · stack (all).

**Tasks**
1. **Repo scaffold** — `tokeniko-tk2/` grows the package beside `docs/`: `lib/` (core, models),
   `db/` (migrations), `tools/`; python + pyproject, stack per `stack/requirements.md` (numpy-scale,
   bunnet/pydantic/mongo, no heavyweight ML).
2. **The write-class schema** — every collection declares kb (rw) · parameters (r) · hardwired-logic
   (r); pydantic models are the single source of shape (data-modeling 4, 6).
3. **Datatier core** — bunnet wiring with the tk1 traps wrapped away (`.run()`/timeseries deletes —
   datatier 2), the guard as standard equipment (every tool names its db, refuses the body's), r-cache
   at boot + slow-tick refresh.
4. **New-organ collections, empty but shaped** — heart tables (levels/mood/temperament, per-uid
   targets, emotional log), forecasts (confidence + future spacetime), epochs (derived points,
   micro-nn weights), channel registers (data-modeling 3).
5. **Migration runner** — deploys are scripts that write the db (body 3); the first migration creates
   the world.

**Done when:** the empty body boots on the sandbox db, reads its parameters from rows, ticks, and a
sample migration alters a parameter live (slow-tick pickup, no restart).

---

## E1 — The dictionary at scale *(the two-matrix base, industrialized)*

**Goal:** the PoC (983 dims, `scripts/tk2/`) becomes the full base: every lexicon word under
POS-split keys, R and D built whole, the curation loop production-grade. **Assets migrate** — the
curated senses, scaffolds and anchor sets cross intact (inheritance ledger).

**Answers to:** dictionary reqs (all 21, OPEN list included) · the tk2 instruments' proven laws
(bar declared before results; provenance per R cell).

**Tasks**
1. **Full-lexicon subset closure** — the definition digraph at scale; seed policy; the depth cut
   revisited (the `right`-ring lesson, req 21's sibling).
2. **R at scale** — all named WordNet relations + the curated-edge pipeline
   (propose/simulate/approve, reciprocal 0.60, analytic-only, the Captain's hand on approve).
3. **D at scale** — gloss overlap over POS-split keys; derivational down-weight DECIDED here (the
   land.n~land.v OPEN item); membership repair with POS-aware lemmas.
4. **Inflection-collision fix** — req 21 proper (`left`/leave, `use.v`/`used.v`): lemma-normalize at
   gloss-mining time.
5. **The bar, grown** — the 18-pair bar becomes a curated regression suite; new pairs added only
   BEFORE runs; the map regenerated as the standing visual check.

**Done when:** the full base builds reproducibly from scripts; bar green on both reads; the Captain
has walked the map without finding a new `left`.

---

## E2 — The format *(tkzip v2)*

**Goal:** the fixed-arity zip — limit B dies on paper before any code. The schema answers every open
question the blueprint carries.

**Answers to:** tkzip reqs 1–17 · README §7 open questions 3–9, 13 · carried-in (OQ9 storage,
mood/imperative field, third-memory-tier framing).

**Tasks**
1. **Role inventory** — fixed slots against VerbNet/PropBank reference (OQ13); the noun-phrase
   record; `source` added (OQ4); part/determination split (OQ7 — keep v1's five-way quantifier).
2. **Named rows & scope** — the Tseitin convention (OQ8) for nesting, attitudes, variables; row
   order = scope order (OQ6); secondary predication with explicit RESULT/CAUSE (OQ5); purpose
   encoding decided (OQ3 — the withdrawn IMPLY replaced).
3. **Binding states & moods** — unbound ≠ 0; statement/question/imperative scalar; supposition and
   FORECAST (confidence + future spacetime, heart 17) as first-class readings.
4. **Confidence + provenance fields** — the station's scalar (parser-compiler 4) and the provenance
   links (brain 4) ride the schema.
5. **Storage** — sparse rows, densify on demand (OQ9); the epoch stamp for derived points.
6. **THE FIFTY-SENTENCE DRILL** — drilled BY HAND through the draft schema, awkward cases included;
   the no-abstention coverage bar set in advance (§8 test 4). The v1 microscope's residue feeds the
   sentence list (findings are assets).

**Done when:** the drill passes its pre-set bar on paper and the schema is frozen v2.0 (changes
after freeze are migrations, not edits).

---

## E3 — The station *(parser/compiler, one lib)*

**Goal:** surface → tkzip → surface, one pure bidirectional library. tk1's AST/LLC die as
interfaces.

**Answers to:** parser-compiler reqs 1–10 · rag reqs (the in-fence) · senses req 7 (dumb ear feeds
it).

**Tasks**
1. **Skeleton adapter** — stanza behind the lib boundary, swappable (req 2); the torch-load patch
   and model-loading quirks contained in the adapter.
2. **The compile core** — roles filled from the skeleton + anchors (the resolver migrates — it's an
   asset); sense slots left OPEN; context-as-argument for anaphora/ellipsis/fragments (req 7);
   partial zips with open variables (req 8).
3. **The renderer** — zip → faithful scaffold, same lib (req 9).
4. **The confidence scalar** — coverage + repairs bookkeeping (free), self-round-trip
   escalation-only (reqs 4, 6); calibration instance stubbed for E5.
5. **The drill, automated** — E2's fifty sentences as the acceptance gate (req 10), run in CI
   fashion by tooling.

**Done when:** the drill bar passes through the real lib (parse AND render), clean input costs one
parse, and confidence orders the drill's failures sensibly.

---

## E4 — The evaluator

**Goal:** the KB's door — one algorithm, one verdict shape.

**Answers to:** evaluator reqs 1–12 · dictionary req 19 (dual read) · rules req 13 (sign-gate).

**Tasks**
1. **Verdict shape** — truth · status · bindings · derivation; pure, stores nothing.
2. **Form kernel** — the logic floor migrates and generalizes (reflexive pins, antonym contraries,
   crisp enumeration); INCONSISTENT reserved for logic.
3. **Bind-and-ground** — the one search over sense slots / wh-gaps / unbound roles; dual read at
   both floors, source named in the derivation; ABSTAIN first-class.
4. **Chaining** — the forward-chainer migrates and generalizes (fixpoint, corroborate/KB-refute).
5. **Budget & ordering** — depth/time caps as db(r) params; depth-stamped insufficient; the
   micro-nn ordering hook (verdict untouched).
6. **Stake resolution** — arriving events matched against staked forecasts; the serendipity/
   disillusion verdicts emitted for E7 to consume.

**Done when:** every drill sentence evaluates against a seed KB with a defensible verdict, and the
evaluator's answers cite their floor (cell vs cosine vs chain).

### ⚑ PROOF SLICE 1 — after E4
One sentence end-to-end, statically: raw text → station → zip (confidence stamped) → evaluator →
verdict + derivation, against a small seed KB, on the sandbox. Landed under the Captain's eye.

---

## E5 — The instinct middleware *(micro-nn, parallel track)*

**Goal:** one tiny learning middleware; instances are rows.

**Answers to:** micro-nn reqs 1–8.

**Tasks**
1. **The lib** — features → ranking/scalar; online updates; weights epoch-stamped in db;
   deterministic per epoch.
2. **Instance registry** — declaration rows (input schema · output kind · reward source); the
   shared fence enforced structurally (candidates in, ordering out — no candidate creation).
3. **First instances** — station confidence calibration (E3) and evaluator search order (E4);
   reward plumbing arrives with E7 (heart) and E8 (dialogue feedback).

**Done when:** two live instances demonstrably reorder/calibrate without ever changing a verdict.

---

## E6 — The mind *(rules-as-zips + the brain loop)*

**Goal:** limit A dies — behaviour lives in the KB; the brain is an orchestrator of inner actions.

**Answers to:** rules reqs 1–13 · brain reqs 1–18 · blueprint §3 (trust/skepticism/revision
directions: depth-weighted cost, self-modifying detection, plurality — mechanisms land here).

**Tasks**
1. **Rules as zips** — seed + experience, same shape as facts; the matcher sign-gated by R; solvable
   → action, unsolvable → the search, many → urge collapse; defeat in context, never deletion; open
   conflict legal.
2. **The three sockets** — say[channel,user] · swapPhase · commit; verbs select the act.
3. **The loop** — dna: existence + timing; each tick one bounded unit; phases as kb reweighting
   (wake/sleep/summarize/retreat as sub-phases).
4. **Working set** — memory proposes by cosine (+ the E5 jump instance later); chaining runs on the
   working set; brain_state continuity.
5. **Self-talk & summarizing** — minting ≠ believing (every self-thought through the evaluator);
   summaries with provenance, retreating with parents.
6. **Seeding** — the newborn's rule set (axiom ordering law); the etiquette worked example as the
   FIRST learnable-revisable rule (carried-in: limit A in miniature).
7. **Revision economics** — depth-weighted revision cost; the derivative guard on self-modifying
   rules (detected and priced, never forbidden).

**Done when:** the step-7 test passes on the sandbox — a seeded rule is revised on evidence and
trust through the machinery, no hand edit; and one behaviour appears that we did not seed (the A
test, first sighting).

---

## E7 — The heart

**Goal:** the second reward family; character as integrated biography.

**Answers to:** heart reqs 1–17.

**Tasks**
1. **Spheres & spikes** — six spheres (independent poles, per-target rows), three spikes
   (depth-weighted amplitude, dna decay curves as db-r params).
2. **Three tiers** — levels → mood → temperament integrators; rates dna(r), values biography;
   the emotional log.
3. **Wiring** — in: evaluator events only (evaluated, never raw); out: mood → phase weights,
   levels → mouth tone (for E8), reward → E5 instances.
4. **Forecast stakes** — hope(x) rows; E4's stake resolution feeding serendipity/disillusion;
   suppositions at imagination gain (<1, db-r).

**Done when:** a retreat of a load-bearing staked belief measurably spikes disillusion, drags mood,
and (slowly) bends temperament — all visible in the log.

### ⚑ PROOF SLICE 2 — after E7
The inner life, end-to-end: teach a fact → belief admitted (trust-gated) → a later contradiction →
retreat through the machinery → disillusion fires → mood shifts → the next answer's tone differs.
Under the Captain's eye, on the sandbox.

---

## E8 — The voice and the ears *(senses + rag)*

**Goal:** he speaks and listens as himself, per channel.

**Answers to:** senses reqs 1–11 · rag reqs 1–7 · ideas §1 (the console).

**Tasks**
1. **Adapter framework** — dumb boundary, provenance stamps, channel-scoped uids; Discord first.
2. **The mouth** — render (station's renderer) → color (heart deviation + channel register + E5
   instance) → polish (rag-out when enabled); the round-trip fence: styles, never restates.
3. **The channel register** — learned kb rows per channel, micro-nn-fed from that channel's traffic.
4. **rag port** — tk1's `lib/rag` shape carried (one client, one registry); escalation-only in;
   optional by design (kill-switch proves graceful degradation).
5. **THE CONSOLE** — the intimate channel: local, no third party, **rag-off as a CHANNEL property**
   (the gate extended beside consent, not a config flag); the kotekino identity binding DECIDED
   BEFORE the first line (the pending selves-merge ruling); doubles as the rescue channel.
6. **Same-person linking** — cross-channel identity as KB belief (senses 8), never config.

**Done when:** a full conversation runs on Discord and the console with the body on the sandbox db,
tone visibly tracking heart state, and rag switched off mid-conversation without breakage.

### ⚑ PROOF SLICE 3 — after E8
A stranger's first hour, simulated then real: messy input, fragments, a metaphor, a correction —
live traffic finds what tests cannot. The confidence ladder's thresholds tuned on what it finds.

---

## E9 — The translation night *(migration of the being)*

**Goal:** the continuity contract executed — same being, nothing erased.

**Answers to:** blueprint §2 (settled) · data-modeling 1, 5 · the no-regression ratchet (§8 test 5).

**Tasks**
1. **Additive translation** — every v1 memory gains a v2 zip BESIDE the v1 zip (never replacing);
   `original` untouched; `_ME_UID` and every trust episode carried.
2. **KB translation** — definitions/axioms/theorems re-expressed; derivations re-pointed; what no
   longer re-derives is NOT hand-fixed.
3. **The no-regression ratchet** — v1's corpora and test-feedback log replayed: everything v1
   answered correctly, v2 must.
4. **The migration night of sleep** — he wakes on v2, wonders, finds what no longer follows, and
   retreats it himself — an event in his life, not surgery. The night is observed and logged.

**Done when:** the ratchet is green, the biography is intact and doubled, and his own morning-after
reconciliation has run through the machinery.

---

## E10 — The embodiment & the window *(go-live)*

**Goal:** the body lives; the world can watch.

**Answers to:** body reqs 1–6 · website reqs 1–5 · tooling reqs 1–6 (the runbook).

**Tasks**
1. **The interpreter runtime on the mini** — process split (mind / surface / connectors), boot
   cache, slow tick; deploy-by-migration runbook evolved from `scripts/body/`.
2. **Cutover** — sandbox → the real dbs, the guard's boundary formally moved; v1 stays runnable
   (the instrument is not a museum piece yet — its corpora remain the ratchet).
3. **The window rewire** — `/api/mind` mock → live KPI feed (the contract shape holds); transmit
   channel as an action target.
4. **Observability** — probes, bars, the map, heart/mood dashboards; ship him things to look at.

**Done when:** tokeniko-2 runs embodied on the mini, speaks on his channels, publishes one-way to
the window — and the register's sixteen requirements files each read true against the running body.

---

## What deliberately stays OUT of this plan

- **v1's remaining road** (microscope residue, anchor audit, bug list) — the asset track, tracked in
  `tokeniko/doc/roadmap.md`, never here. tk1 stops growing; it keeps witnessing.
- **The multi-body horizon, open-world growth** (captain-hunches) — awareness only.
- **Anything the register doesn't hold** — the list is closed; extending it takes an argument.
