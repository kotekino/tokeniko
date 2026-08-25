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

---

## STANDING LAW — where a closed set may live *(the Captain's ruling, 2026-08-25)*

Hand-picked lists in code are how load-bearing knowledge hides. Everything-is-rows already said so
for the KB; this states the test that decides it in every other case, existing and future. Before
writing an enumerated set, name which of the three it is — and if the answer is 3, it is not a set at
all.

**1 — FRAME.** Not «what we are sure of» — *the shape in which anything can be stated at all*: the
key grammar (a key is a word plus a part of speech), the write-class taxonomy, the guard and the db
whitelist, the logic floor. Stays in **code**, and moves only by migration under the Captain's hand.
It must pass BOTH tests:

  1. *Does changing it change the SHAPE of rows, keys or operations — or only their content?*
     Shape is frame; content never is.
  2. *Could evidence revise it?* If yes it is empirical, and **empirical is knowledge** — however
     certain we are today. A closed grammatical class (the pronouns of English, the wh-words) feels
     like law and is not: it is a contingent fact about one language, dialect-varying and revisable,
     and this being is meant to LEARN language rather than be issued it.

**2 — CURATION.** Authorized judgment: the dictionary seeds, the relation weights, the closure cuts,
thresholds, rosters — **and the acceptance bar**. Lives in the **db**, maintainable there, and it
must be **as complete as we can make it**; since completeness is reached iteratively, the medium has
to be the one that supports iteration. Three obligations come with it: the build manifest records
the set it used and its fingerprint, incompleteness is visible rather than implied, and it grows
**generated-then-curated** (propose → simulate → the Captain approves), never typed by hand until it
looks long enough.

  *Why the bar is not an exception* — the first draft of this law kept `BAR_PAIRS` in code, on the
  argument that a bar editable after seeing the results is not a bar. The Captain dissolved it: that
  threat model needs a team with an incentive to move the goalposts, and there is no team — only him,
  the QM, and (when the behaviour layer allows) tokeniko. The property actually wanted was never the
  medium but **the ledger**: bar rows epoch-stamped and append-mostly, every build recording the bar
  version and fingerprint it was measured against. That makes «was this pair declared before the
  run?» machine-checkable, where git made it only human-checkable. And eighteen pairs is a draft:
  each discovered failure should add one.

**3 — OPEN.** Which words are near, which sense a gloss meant, which behaviour fires, whether a verb
takes a subject-control reading. **Never a list, in code or in rows** — geometry decides, with a
small anchor set and a nearest-anchor fallback so nothing can be missed (the semantic catch). A
hand list here is a bug wearing a shortcut's clothes: it is right for the words someone thought of
and silently wrong for every other.

**A SECOND LAW, ruled 2026-08-25 — content is defined, structure is compiled.** Content words are
DEFINED: they earn a dimension in the dictionary. Function words are COMPILED: they become structure
in the zip — roles, quantifiers, moods, negation, binding — and never need a vector at all. A
pronoun is indexical (`me` means whoever is speaking), so it is resolved to an ENTITY at parse time
and the dictionary is never asked; the self-model is carried by `kotekino` and `tokeniko` as named
individuals (uid + type-centroid), not by a pronoun's dimension. This kills the `in` = *inch* /
`at` = *the Lao kip* class of defect at the root rather than by filtering: a function word never asks
the dictionary a question. The concept keeps its dimension where one exists — `not` compiles,
**`negation`** is a word he can reason about.

**A closed class is typed, not flat.** The one KB collection that replaces tk1's four code lists
(`_ANAPHORIC_PRONOUNS`, `_QUANTIFIER_*`, `_WH_*`, `_RELATIVE_PRONOUNS`) carries a TYPE per row,
because "pronoun" is three jobs: **referential** (I, you, them, himself → an entity resolved from
context) · **quantificational** (somebody, nobody, everyone → a quantifier, not a referent) ·
**interrogative/relative** (who, what, whose → an unbound variable + question mood). Prepositions
join it as role markers. Curated and exhaustive — English's closed classes are genuinely finite.
An unresolvable `they` stays legal: unbound variable, low confidence, the brain may ask.

**A category-2 set stated in code is a defect even when its contents are correct** — that is what the
dictionary's `SEEDS_*` were, and E1 moves them.

**What the 2026-08-25 audit found.** E0's model layer is clean: it already argues its own categories
— `OutputKind` states why it is frame and what would move it, `reward_source` is a string because the
roster grows, the channel registers are learned rows. In the dictionary, the seeds, the closure cuts,
**the bar**, and — when they land — the relation weights are category 2, and E1 moves them; test 2
also catches `POS_ORDER`, which is WordNet's answer rather than the grammar itself, so it travels
with the policy rows (confirmed with the Captain at that task's dispatch). **The concentration is in
tk1's LLC layer** (~40 hand lists in `lib/llc/constants.py` and its neighbours): the grammatical
classes (pronouns, wh-words, quantifiers) are **KB, not frame** — rows, with geometry answering what
the rows do not cover; the weights (`_CONTENT_WEIGHTS`, `_ITEM_WEIGHTS`, `_ATTITUDE_DEFAULT`) are
category 2; and the content lists (`_SUBJECT_CONTROL_VERBS`, `_COMPARISON_AFFIRMATIVE`,
`_IMPLICATION_VERBS`, `_ROOM_WORDS`) are category 3 wearing a list's clothes. **E2/E3 rebuild that
layer and may not port them as written** — that is the law's first real bill, and it is priced there,
not here.

---

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

**Tasks** *(build order revised 2026-08-25: 1 → 4 → the name refusal → 6a → 6b → 2 → 3 → 5, so R
and D are built once, against a base whose policy is already settled.)*
1. **Full-lexicon subset closure** — the definition digraph at scale; seed policy; the depth cut
   revisited (the `right`-ring lesson, req 21's sibling).
2. **R at scale** — all named WordNet relations + the curated-edge pipeline
   (propose/simulate/approve, reciprocal 0.60, analytic-only, the Captain's hand on approve).
3. **D at scale** — gloss overlap over POS-split keys; derivational down-weight DECIDED here (the
   land.n~land.v OPEN item); membership repair with POS-aware lemmas. **Two questions parked here by
   the Captain, 2026-08-25:** (a) **the sense mode** — the closure mines `senses="primary"`, so for
   every polysemous word the edges come from whichever sense WordNet ordered first, and that is
   frequently not the sense that made the word frequent (`small` = «the slender part of the back»,
   `large` = «a garment size», `plant` = «buildings for industrial labor», `state` = «the territory
   occupied by…»); measure `senses="all"` against edges, base size and the bar before ruling.
   (b) **high-frequency dimensions** — after the name refusal the residual gloss-overlap floor is
   real function words (`in` 27% of base rows, `be` 14%, `by` 14%, `as` 10%), which is a WEIGHTING
   question (IDF-shaped down-weight), not a membership one.
4. **Inflection-collision fix** — req 21 proper (`left`/leave, `use.v`/`used.v`): lemma-normalize at
   gloss-mining time.
5. **The bar, grown** — the 18-pair bar becomes a curated regression suite **as rows** (standing
   law, category 2): epoch-stamped, append-mostly, every build recording the bar version and
   fingerprint it was measured against, so «declared before the run» is machine-checkable rather
   than trusted. The offline suite reads a snapshot pinned by that fingerprint, so the acceptance
   tests keep running without the body. New pairs added only BEFORE runs; the map regenerated as the
   standing visual check.
6. **The policy becomes rows** (standing law, category 2 — added 2026-08-25), **split in two and
   moved AHEAD of R and D** (Captain, 2026-08-25: a seed ruling that changes membership would
   otherwise force the matrices to be built twice):
   - **6a — the mechanism, code only.** A `dictionary_policy` logic collection through the migration
     door; the bar as **epoch-stamped, append-mostly rows** carrying their `why` verbatim; the
     manifest gaining the policy and bar version+fingerprint a build was measured against; an offline
     snapshot pinned by fingerprint so the acceptance suite still runs without the body. Today's
     values migrate across VERBATIM — a value edited here would corrupt the comparison 6b is about
     to make. `DictionaryConfig` stays the pure value object, now constructed FROM ROWS; the
     dictionary package keeps its purity (rows arrive injected, same seam as the gloss provider).
   - **6b — the Captain's ruling.** *Proposal measured 2026-08-25, ahead of the mechanism:*
     **purpose ∪ structure** — purpose = the declared families (in-scope-by-construction), structure
     = the definitional core by in-degree over the whole digraph (`manner person act form cause
     quality resemble consist characterize property unit shape result process position substance`).
     Purpose alone closes at 913 words and stops on DEPTH, not size; the union scales smoothly
     (top-50 → 1,651 words · **top-100 → 2,181 words / 3,188 keys, the QM's recommendation** ·
     top-200 → 2,995 · top-400 → 3,773). **Two rots the ranking exposes:** six of the top hundred are
     inflection artifacts ranked by grammar (`used being are made lacking marked` — `are`'s gloss is
     «a unit of surface area equal to 100 square meters»), which a de-inflection guard fixes; and the
     function words cannot be fixed at all — `in` is #1 with 14,408 in-edges and means *inch*, `at`
     is #19 and means *the Lao kip*. Frequency earned by grammar, meaning supplied by a homograph.
     **Superseded the same day by the second standing law:** function words and pronouns are neither
     mined NOR curated in — they are COMPILED (see «content is defined, structure is compiled»
     above). So the whole `in/at/by/as/on/through/over/up/but` head of the ranking is excluded by
     PRINCIPLE, not by a guard, and `me`/`you` leave `SEEDS_IDENTITY` because they were never
     dictionary business: a pronoun resolves to an entity before the dictionary is consulted.
     `not` goes with them (pure structure) while **`negation` stays** — the concept he reasons
     about. The de-inflection guard is still needed for `used/being/are/made/lacking/marked`.
     **RULED 2026-08-25 (all five, on measured numbers):** `max_size` = **25,000, a safety rail**
     (the depth cut is the policy — under the old 400 cap, k=50 gave a base of 588 words, SMALLER
     than seeding nothing structural at all, because the cap deletes a whole ring instead of
     trimming) · **k = 200** → 3,095 words / 4,445 keys, bar 23/23 · `must`/`need` keep **both** the
     closed-class row and the dimension (a row is about a FORM's structural job, membership is about
     a READING) · `one` excluded as a pronoun while `two` is a candidate — **accepted** as consistent
     · degree and `-ly` adverbs stay **content** (`especially`, `usually`, `very` keep dimensions;
     revisit only if the zip grows a degree operator at E2). Policy v2 lands as migration 0005;
     v1 stays where it is — the collection is a ledger, not an edit.
     Seeds **grown generated-then-curated** (candidates proposed from
     resource centrality + the bar + tk1's own biography vocabulary, the closure each produces
     simulated, the Captain approving — never typed longer), **with `max_size` ruled in the same
     breath**: 400 was arbitrary and the base overshoots it regardless (a ring lands whole or not at
     all), so the seed set and the size cut are ONE decision measured together — and the measurement
     already says **`max_size` should stop being a design knob**: every candidate configuration
     overshoots it and WHICH ring gets truncated is arbitrary (the top-50 union under the 400 cap
     lands at 471 words and loses `right`; lift the cap and the same seeds give 1,651 and keep it).
     The depth cut is the policy; the size cut becomes a safety rail set far above any intended base. **The pronouns are
     curated IN**: WordNet has none — `me`, `you`, `it`, `who` are all name-only spellings there — so
     `SEEDS_IDENTITY` cannot be satisfied by mining and the resource cannot be the only source.
     **`POS_ORDER` travels with the policy rows** by test 2 — it is WordNet's answer, not the key
     grammar (the Captain ruled it 2026-08-25; what stays in code is that a key IS word-plus-POS,
     never which parts of speech exist).

**Done when:** the full base builds reproducibly from scripts; bar green on both reads; the policy
the build used is readable as rows and recorded in its manifest; the Captain has walked the map
without finding a new `left`.

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
interfaces — **and its ~40 hand lists die with them**: the standing law above prices this epic's
first bill, so every ported set arrives as rows (the grammatical classes and the weights alike — they
are knowledge, not frame) or as geometry with a nearest-anchor fallback (the content lists). A list
copied across as written is a rebuild that inherited the defect.

**Answers to:** parser-compiler reqs 1–10 · rag reqs (the in-fence) · senses req 7 (dumb ear feeds
it).

**Tasks**
0. **The closed classes as typed KB rows** — ONE collection replacing tk1's four code lists, each row
   carrying its type and its compiled meaning: referential (→ entity, resolved from context) ·
   quantificational (→ quantifier) · interrogative/relative (→ unbound variable + question mood) ·
   prepositions (→ role markers). Curated and exhaustive. It is born earlier if E1 needs it to
   exclude function words from its seed ranking — one table, two consumers.
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
  `tokeniko-tk1/doc/roadmap.md`, never here. tk1 stops growing; it keeps witnessing.
- **The multi-body horizon, open-world growth** (captain-hunches) — awareness only.
- **Anything the register doesn't hold** — the list is closed; extending it takes an argument.
