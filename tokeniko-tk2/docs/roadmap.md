# tokeniko 2 — ROADMAP

*The checkable mirror of `plan.md`: **one line per item**, one item one status, done moves to
`landed.md`. ⚑ = vertical proof slice under the Captain's eye.*

> **The reasoning is NOT here.** It lives in `docs/<chapter>/` — `requirements.md`, the dated
> `_notes.md` beside it, any `origin-*.md` — and in `plan.md` for the epics' tasks. A line here says
> *what* and points at *where*; a roadmap that grows prose is one nobody can read at a glance.

## E0 — the keel ✅ 2026-08-23 — see `landed.md`
## E1 — the dictionary at scale ✅ 2026-09-10 — see `landed.md`
## E1b — the names, and one baseline ✅ 2026-09-10 — see `landed.md`
## E1c — the sense layer ✅ 2026-09-10 — see `landed.md`
## E1d — the audit's repairs ✅ 2026-09-14 — see `landed.md`

## E1e — the tests, isolated *(opened 2026-09-17 — runs AFTER E3 closes)*
- [ ] **⚑ sweep E0 → E3 for test material leaking into the BL** — formal order included
- [ ] **the third kingdom** — frame · knowledge · **evidence**; evidence keeps the ledger properties
      but never runs in the app
- [ ] `dictionary_bar` out of the body; only `bar_version` + `bar_fingerprint` stay, as provenance
- [ ] bar words become `extra_seeds` on a measuring run — **cost: moves the config fingerprint**
- [ ] the doctrine line in `core/models/__init__.py` calls three things one thing
- [ ] **the pacing rule** — subset while developing, full suite once at the commit gate

## E2 — the format (tkzip v2) ✅ 2026-09-14 — see `landed.md`

## E3 — the station (parser/compiler)
- [x] **task 0 — the closed classes' SEMANTICS** — 383 rows carry a complete `compiled` (`db/0008`,
      `db/0009`)
- [x] **skeleton adapter** — stanza behind the lib boundary; nothing above imports spacy or torch
- [x] **⚑ the UD gate opens** — `tools/ud_gate.py`; nine defects nobody would have read off the code
- [x] **⚑ the gate scores the ZIP, not the table** *(09-16)* — needed `Compiled.placement`; four
      defects before one new case was added
- [x] **⚑ the UD gate reaches all 37 relations** *(09-16)* — 43 cases · 30 answered · 0 wrong · 13
      abstained; stanza produces 15 of UD's 18. Record `202609161050_…`
- [x] **compile core — one content row** — 18/25 UD cases whole, mean 89.5%
- [x] **compile core — many rows** — «if»/«because»/«and» are three zips (req 38, `db/0010`); 20/25
- [x] **the wh-word's box** — five kinds, not one (`db/0011`); 21/25 whole
- [x] **the thirteen ambiguous markers** — WordNet **supersense**, not geometry (`db/0012`); benched
      11/11 vs 6-with-3-wrong. 22/25 whole. Record `202609160929_…`
- [x] **content ADVERBS** — req 23's four scopes as rows; manner is the counted DEFAULT, the table
      holds the 106 exceptions (`db/0013`, `db/0014`). Record `202609161251_…`
- [x] **`db/0014` — the two gaps the clash check found**; repairing them left the exclusion set at 268
- [x] **the dirty-check gained a fourth field** — which table filtered D's vocabulary is now recorded
- [x] **`amod` — attributive adjectives are SECOND ROWS** *(req 70)* — an adjective forces a binder;
      modifier joins chain per clause. Record `202609161215_…`
- [x] **the copular subject is the PATIENT, not the topic** — a slip against 43 hand-compiled rows
- [x] **`nummod` — the box's own `count` field** *(req 26)* — a numeral raises no binder
- [x] **number words — `word2number` admitted** — one door, so a machine without it only abstains
- [x] **embedded questions** — a wh-word has three readings; UD marks the difference and nothing else
- [x] **unassertion propagates into an enclosed clause** — a truth error found by the above
- [x] **a compiled form no longer ALSO abstains** — ratchet 24/25 at 99.4%
- [x] **`db/0015` — a marked phrase has an endpoint** — `direction` is a direction with NO endpoint
- [x] **⚑ the two gates meet — `tools/drill_gate.py`, req 18** *(09-16)* — it scores agreement, not
      equality. Widened twice on 09-17 (a context, and the mirror test). Record `202609161502_…`
- [x] **⚑ the person axis — the rotation under a point of view** *(req 20, `plan.md` task 2b)* —
      context-as-argument · multi-sentence input · **schema v3: `addressee`** · the rotation · the
      quote as unclaimed content. Records `202609161349_…`, `202609161544_…`
- [x] **⚑ the rotation was INVERTED — found and fixed** *(09-17)* — quotation rotates, reporting does
      not; the signal is structural and no character is ever read. Record `202609170533_…`
- [x] **the truth slot under an attitude — RULED: the rows keep their truth** *(09-17)*
- [x] **task 2c — ⚑ a polar question opens its truth** *(09-18, req 21)* — the `?` decides, per statement. Record `202609180900_…`
- [x] **task 2d — ⚑ the imperative is a want, not a claim** *(09-18)* — `Mood=Imp`; `aw-21` agrees. `strength` and «Suppose…» asked
- [x] **`whether` / `if` on a complement ask** *(09-18, `db/0016`)* — the clause decides: `ccomp` asks, `advcl` supposes
- [x] **`or` / `nor` claim only the join** *(09-18, `db/0017`)* — the Captain's (b)
- [x] **free choice under a modal** *(09-18)* — both halves under «can»/«may» are claimed; `t-ws-7` is a stanza misparse, abstained
- [x] **the subject's role depends on WHAT IS PREDICATED of it** *(09-18, req 22, `db/0018`)* — a
      supersense rule as rows; twelve drill roles amended; the ratchet falls to three
- [x] **⚑ the drill gate sees the PREFIX** *(09-19, req 18's fourth widening)* — 89 prefix rows and
      50 joins enter the instrument; attitudes pair on their verb. Record `202609190900_…`
- [x] **⚑ a coin toss in the station's own reading** *(09-19)* — NLTK keeps synset pointers in a
      `set`; `derived_supersense` now reads the whole relation and abstains when it disagrees
- [x] **task 2d's two questions — `strength` is knowledge, an imperative does not collapse**
      *(09-19, reqs 23-24)* — `db/0019` and `db/0020` applied; `aw-20` a named divergence on req 55
- [x] **⚑ the placement floor — MEASURED AND REFUSED** *(09-19)* — 40 placements ruled; the
      verdicts interleave with the cosine in both halves, so no floor separates them. Record
      `202609191500_…`
- [x] **⚑ the placement rule, in place of a number** *(09-19, dictionary req 22)* — a stated
      edge is trusted, the sibling fallback and D abstain; 19.4% coverage, 0 wrong trusts
- [x] **`mark` under a reporting verb opens a POV**, not a join — built with `db/0010`'s `asserts: matrix`; ticked 09-18
- [ ] renderer (same lib)
- [ ] confidence scalar (coverage + repairs; round-trip escalation-only)
- [ ] drill automated = acceptance gate
- [ ] **⚑ the frame/knowledge audit — E3's closing act.** Suspect already: `RELATION_FILLS_ROLE` ·
      `CLAUSE_DEPS` · `UD_DEP_TO_ROLE` · `UD_POS_TO_WORD_CLASS` · `CLAIMED = 1.0` · `SAYING_VERBS` ·
      `COORDINATE_DEPS` · `SUBJECT_DEPS` · `OBJECT_DEPS` · `COMPLEMENT_CLAUSE_DEPS` · `QUESTION_MARK` ·
      `IMPERATIVE_VERB` *(that an imperative is a WANT — the other half of `db/0020`'s fact)*

## E3b — the name *(opened 2026-09-16 — the parked hole, reopened and widened)*
- [ ] **is it a name at all?** — stanza vs spaCy NER measured; `PROPN` and casing as weak evidence
- [ ] **a name of what? — OUR kinds, as ROWS not code** — two tables, so a model's new label is a
      migration and not a release
- [ ] **the places table, INHERITED** — 4,674,701 curated rows, a 21-value `type` that is an `is_a`;
      read lazily, never materialized
- [ ] **the names list, INHERITED — and it cannot be a TEST** — 21,975 rows, **28.1% also place
      names**. Evidence, never a test: it is the measurement that forces the net
- [ ] **have I met it?** — recognition; the mechanism is E3b's, the rows are E9's
- [ ] **⚑ the MICRO-NN abstraction — brought forward from E5**; built to serve the next line and
      generalized against it, never before it
- [ ] **⚑ which one? — the first instance** — «Paris, France» or «Paris, Ontario»: the first case
      where curation cannot finish AND the answer moves over time
- [ ] **what a name is in a zip** — type centroid = SEMANTIC, uid = IDENTITY, never merged
- [ ] **the markers' third reading** — «went with Anna» is comitative because Anna is a PERSON, with
      no rule about Anna anywhere. E3b's acceptance test

## E4 — the evaluator
- [ ] verdict shape (pure; truth · status · bindings · derivation)
- [ ] form kernel (logic floor migrated)
- [ ] bind-and-ground (one search; dual read; ABSTAIN first-class)
- [ ] chaining migrated + generalized
- [ ] budget + micro-nn ordering hook
- [ ] stake resolution
- [ ] ⚑ PROOF SLICE 1: text → zip → verdict, end-to-end on sandbox

## E5 — the instinct middleware (parallel after E0)
*The MACHINERY moved to E3b (2026-09-16): a framework that meets a real case before it is declared
general is the failure mode «one abstraction, many instances» is most exposed to.*
- [ ] ~~the lib~~ · ~~instance registry + structural fence~~ — **BUILT IN E3b**
- [ ] instance breadth: station calibration · evaluator ordering · then the sites that need an organ
- [ ] reward plumbing (intellectual + heart families) — arrives with E7 and E8

## E6 — the mind (rules + brain)
- [ ] rules as zips (sign-gated matcher; urge collapse; defeat in context)
- [ ] the three sockets (say · swapPhase · commit)
- [ ] the loop (dna) + phases as kb reweighting
- [ ] working set (cosine proposal; brain_state)
- [ ] self-talk + summarizing (provenance, retreat with parents)
- [ ] seeding + the etiquette worked example
- [ ] revision economics (depth-weighted cost; derivative guard)
- [ ] step-7 test green (seeded rule revised, no hand edit)

## E7 — the heart
- [ ] spheres & spikes tables (dna curves as db-r)
- [ ] three tiers + emotional log
- [ ] wiring (evaluator in; mood → phases; tone out; reward → E5)
- [ ] forecast stakes (hope(x); imagination gain)
- [ ] ⚑ PROOF SLICE 2: teach → contradict → retreat → disillusion → tone shift

## E8 — the voice and the ears
- [ ] adapter framework + Discord
- [ ] the mouth (render · color · polish; the fence)
- [ ] channel register (learned rows)
- [ ] rag port (escalation-only; kill-switch proven)
- [ ] THE CONSOLE (rag-off channel property; identity binding decided FIRST)
- [ ] same-person linking as KB belief
- [ ] ⚑ PROOF SLICE 3: a stranger's first hour, messy input live

## E9 — the translation night
- [ ] additive translation (v2 zips BESIDE v1; biography intact)
- [ ] KB translation (no hand-fixes)
- [ ] no-regression ratchet green — `tkzipdebug`: 529 clean journeys, 209 v1 read wrong
- [ ] the migration night of sleep — observed

## E10 — the embodiment & the window
- [ ] interpreter runtime on the mini (process split; runbook)
- [ ] cutover (guard boundary moved; v1 kept runnable)
- [ ] window rewire (mock → live KPIs)
- [ ] observability (probes, bars, maps, heart dashboard)
