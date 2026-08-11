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
- **§1 — the per-user context + multilingual + consent** (2026-07-25 → 08-03) — the room + the «did
  you mean?» ask + the answer binding · multilingual (two-reader consensus judged by the compiler) ·
  the native voice (232 curated rows) · **the consent gate** (Route C + the payload gate at
  `rag_call`). **The chapter is WHOLE** *(its residuals → Pending follow-ons)*.
- **§0 — the body** (2026-08-06 → 09) — the prep + the pin lock · the transplant, verified twice ·
  self-healing under `kill -9` and reboot · the workshop over the LAN · the deploy loop, proven in
  anger *(→ `landed.md` §0 + its two addenda)*.

---

## 🔭 Next (ordered) — refiltered 2026-08-03

**The through-line: THE VOICE IS WHOLE, THE EARS ARE WALLED, THE DOOR IS GATED — AND THE BODY IS
HIS OWN.** §1 closed 2026-08-03 with the consent gate; **§0 the body landed 2026-08-08, its deploy loop closed 08-09** (→
`landed.md`) — he now runs 24/7 on his own machine and gets himself up after a power cut. The road
ahead is **§2 the fresh microscope analysis pass** (promoted: its findings feed both v1 and the tk2
blueprint), then **§4 the strengthening tail**, now filtered to asset work only (see the tk2 filter
above).

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

**TWO SOURCES, one pass (widened 2026-08-03 on the author's call — «we do debug in one batch»).**
This pass is **the single debugging venue**, and it sweeps BOTH:
1. **rag3's machine leads** — the `tkzipdebug` rows, the microscope's own judgement of the
   parse/compile journey.
2. **The hand-logged findings in `doc/ref/test-feedback.md`** — behaviour bugs found by LIVING with
   him, which rag3 structurally cannot see (it judges a sentence against its digest; it has no view
   of what he then DECIDED to say). Today's consent-denied-speaker-gets-«why?» is exactly this class.

They are kept in separate homes on purpose and **a hand-written finding must never be inserted into
`tkzipdebug`**: that collection is rag3's own output, keyed by `item_id` with a dedup that counts any
row as judged, so a hand-inserted row would corrupt the oracle's record of itself — the same failure
shape as the ears'-rejection-rows finding already parked. Two ledgers, one pass, one gate run.

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
5. **Etiquette — the PROTOCOL half only** (hunch 8; scoped with the author 2026-08-03). **The cut,
   and its test: *does getting it wrong CORRUPT something, or merely make him seem RUDE?*** Corrupts
   → protocol (channel management: who is addressed, when a channel opens and closes, whether the
   last utterance landed). Rude → register (warmth, formality, whether he thanks at all). **Only
   protocol is tk1 work.** The author's reasoning: register is shaped by the heart (hunch 14), which
   is not in tk1 scope, so building it now builds something unreusable — and in tk2 both halves
   converge on behaviour rules anyway. Protocol has to exist NOW because it is already load-bearing:
   today's mention-vocative bug proved a purely conventional act (naming the addressee) is
   *structural*, not decorative. **Two items, in order:**
   - **Repair initiation** — «what?», «huh?», «I don't understand». The inbound MIRROR of his own
     did-you-mean: he has a whole apparatus for *"I didn't understand you"* and **no channel at all
     for *"you didn't understand me"***. Today «what?» is read as a question about the world. It must
     REPHRASE his last utterance instead — and it is a free human label that his output missed, the
     outbound twin of the microscope (which only ever judges input).
   - **Farewell / channel-close** — «bye», «I'm off». Distinct from goodnight (the sleep ceremony, not
     a channel act). The open-exchange window currently closes only by TIMEOUT; an explicit farewell
     should close it at once — pending asks lapse, momentum drops — so he stops replying into a room
     whose occupant has left.
   *(The scaffold ROWS are `inherit` either way. The reflex DISPATCH is limit A itself and went
   `→ tk2`; these two ride the existing `social_detect` reflex path, not the behaviour-rule layer.
   Three further protocol candidates parked with the author → `parked.md`.)*

### Pending follow-ons — tails left by the landed arcs (surface when their time comes) 🔭

Gathered so nothing is lost; each waits on its parent feature's next season. **These are deliberately
left unfiltered** — each is small and conditional, and the honest moment to run it through the
inheritance ledger is when its parent's season actually arrives, not now. One known casualty already
visible: the **trust-gated tkzip lane** is format-coupled and will read `→ tk2` when it surfaces.
- **Blog**: `life:learned` / `life:discussion` triggers *(the consensus-over-the-polisher itself
  LANDED 2026-07-24 → `landed.md`)*.
- **A real `/api/v1/health`** (left by the body prep, 2026-08-06): the deploy health-check currently
  probes `GET /openapi.json` — honest (uvicorn answers only after the lifespan has loaded
  spaCy+Stanza, so a 200 means the pipeline is up) but oblique. Three lines would say it directly.
  ~~Deliberately deferred past the transplant~~ — **that blocker expired 2026-08-08**; the move is
  done and the deploy loop is proven, so this is now simply small and unclaimed. It would also let
  the health-check say something the current probe cannot: that the mind is *sane*, not merely that
  uvicorn is answering.
- **Fixture sentinels are shared across test files, and teardown is the only sweep** (2026-08-09;
  the immediate orphan hazard is CURED by the conftest session-start sweep → `landed.md`, this is
  the residue). `test_sleep_phase.py` and `test_untangler.py` declare **identical** `_POISON_A/B/C`
  sentences and both `delete_many({"original": ...})` on them — so each file's teardown silently
  deletes the other's rows, they can never run in parallel, and a duplicate `original` makes the
  untangler convict the wrong document. Two candidate fixes, neither urgent now that orphans are
  swept: give each file its own sentinels (or import one shared set that only one owner sweeps), and
  make the untangler's conviction select on **provenance** rather than on anything that two
  same-`original` rows share. *(The `tiered_world` fixture also gives `belief` and `dependent` the
  SAME zip, so geometry cannot tell them apart either — same lesson, different level.)*
- **The dependency check matches by PATH, not by meaning** (found on the first real deploy,
  2026-08-09): `deploy.sh` step 5 diffs `tokeniko/pyproject.toml`, so a **comment-only** edit
  triggered a full lock reinstall on the body. Conservative in the safe direction — over-installing
  beats silent drift (§2.4) — but it should compare the RESOLVED dependency set instead, so docs
  touches to that file stop costing a reinstall each time.
- **`deploy.sh` should pre-check untracked collisions before the pull** (same run): the first attempt
  died on a raw `git pull` error (*"untracked working tree files would be overwritten"*) via `set -e`,
  with no diagnosis. The manual triage was: are the colliding files byte-identical to the incoming
  ones? Step 4 should answer that for you and say so — the whole point of the script is that nobody
  has to do that by hand at 2am. **Cause will recur**: anything created on the body and later
  committed from the workshop collides the same way (the transplant made three such files).
- **Three vocative/parse residues the §2 C2 fix does not reach** (2026-08-11, each measured):
  «tokeniko is the sky blue?» keeps the stolen subject — its next token is the same `is` that opens
  «tokeniko is a machine», which is exactly where an unconditional comma does harm, so curing it
  needs an INVERSION test (two constituents after the copula) rather than a tag read;
  «tokeniko are all minds machines?» is a SEPARATE parse bug (the comma never fixed it either — the
  subject is lost with or without); «tokeniko does a cat think?» emits a spurious `tokeniko|do.v.03`
  leaf beside the correct clause — a stray leaf, milder than a stolen subject.
- **Eventive passives read as states** (2026-08-11, left by the VBN narrowing): «the door is opened
  by Mari» → `open.a.05`, «the book was written by Mari» → `written.a.01`. VBN separates tense-FORM,
  not state-vs-event, so the narrowing neither fixed nor worsened them. A tighter gate could exclude
  an `obl:agent`/`aux:pass` shape. No test covers them yet.
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
- **Multilingual residuals** (left by the 2026-07-26 build; these wait on a LIVE SEASON, not on
  work): the detector's thin 0.05 margins + the fully-misspelled-English blind spot (env-tunable;
  watch live) · the DM fallback destination carries no `channel_id`, so an action resolved via
  `contextKey` alone cannot key a room and ships English (real Discord traffic always carries
  coords) · the consensus cannot catch a mistranslation BOTH readers share (same model family — a
  second family would be the cut if it ever bites) · the REDUCT cannot be natively composed (no
  source item at plan time ⇒ no room key) · when the mimicry fence is lifted, `mimic_observe` must
  stamp the source language onto the row or it seeds unlabelled foreign strings into the English
  shelf · the slotted 10 categories still compose English + translator (the mixed
  curated-frame/English-slot problem is its own design session).

---

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
