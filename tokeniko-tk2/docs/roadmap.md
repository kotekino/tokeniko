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
- [x] **the pacing rule** *(answered 09-22, and the answer REVERSED it)* — the gate is
      `pytest -m spine` plus the section; the full suite is a DEPLOY condition, on the body. And the
      suite was slow by DEFECT: `Migration.load` re-ran the chain, now memoised (186s → 0.2s). Root
      `CLAUDE.md` holds the rule, `tokeniko-tk2/CLAUDE.md` the commands. Record `202609220900_…`
- [ ] **⚑ sweep E0 → E3 for test material leaking into the BL** — formal order included
- [ ] **the third kingdom** — frame · knowledge · **evidence**; evidence keeps the ledger properties
      but never runs in the app
- [ ] `dictionary_bar` out of the body; only `bar_version` + `bar_fingerprint` stay, as provenance
- [ ] bar words become `extra_seeds` on a measuring run — **cost: moves the config fingerprint**
- [ ] the doctrine line in `core/models/__init__.py` calls three things one thing

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
- [x] **the TENSE and the VOICE, which the station never wrote** *(09-20, reqs 25/26)* — theatre from
      UD's finite `Tense`, topicality from `nsubj:pass`; `db/0024` past + participle, 862 rows
- [x] **SCHEMA v5 — the theatre is a field PER ROW** *(the Captain, 09-20)* — one slot per zip could
      not say «I went to Rome and I WILL GO to Genoa»; on a content row and on an attitude
- [x] **a zip came out a DAG where a sentence is a tree** *(09-20)* — coordination binds tighter, so
      a `conj` replaces the clause it extends; an attitude's own clause dissolves into it
- [x] **`look` → agent · `die` → patient** *(09-20, `db/0025`, req 22)* — exposed when the station
      stopped compiling an unresolved pronoun as OPEN, which the gate had been abstaining on
- [x] **⚑ the placement rule, in place of a number** *(09-19, dictionary req 22)* — a stated
      edge is trusted, the sibling fallback and D abstain; 19.4% coverage, 0 wrong trusts
- [x] **`mark` under a reporting verb opens a POV**, not a join — built with `db/0010`'s `asserts: matrix`; ticked 09-18
- [x] **the DECOMPILER** *(renamed from «renderer/scaffold» by the Captain, 09-19, req 9)* — joins ·
      quantifiers · prefix · questions · the person axis · tense · voice all built; **fixpoint
      24 → 68 of 87** (58 of the 70 the compiler reads whole). Record `202609201100_…`
- [x] **SCHEMA v4 — an OPEN slot says what is known about the unknown** *(the Captain, 09-20, req 27)*
      — `sort`·`person`·`number`·`gender`; three kinds of unknown, no heuristic. `db/0026`. **And
      tkzip req 73 rewritten: there are no frozen schemas in a blueprint**
- [x] **⚑ `fused_quantifier` — «no» takes a noun and «nobody» IS one** *(09-21, req 9)* — `db/0028`
      flagged five voices onto three occupied index slots in silence; the role now splits them and
      the ratchet is a count. Record `202609210900_…`
- [x] **SCHEMA v6's compiler half — `Box.number` from UD's `Number`** *(09-21, 1st Officier, req 26)*
      — `t-md-1` «Software can be minds» round-trips at last; a PROPER noun takes none, because its
      number is a fact about the REFERENT and names are E3b. `db/0027`'s plurals are live
- [x] **⚑ the existential copula agrees with what it displaced** *(09-21, found by the 1st Officier)*
      — «There is no cats», then «There be no cats»: `be` was on the regular-verb path, where a
      non-third-singular is spoken as the bare lemma. An existential is not flagged copular (req 31)
- [x] **⚑ SILENT 1 → 3 and 69 → 67 whole were ONE fact, and the instrument's** *(09-21)* —
      `aw-13`/`aw-14` went MOVED → SILENT; a silent case printed only under `--all` and was
      SUBTRACTED from the read-whole population. The honest denominator is 70 and always was
- [x] **⚑ `aw-13`/`aw-14` — «All that glitters is not gold» binds the quantifier to the PREDICATE
      NOMINAL** and orphans the relative clause's row; the first 1st-Officier task — the COMPILER
      half is fixed and both agree at the gate; ticked 09-21
- [x] **⚑ a quantifier's voice depends on the NUMBER of its noun** *(the Captain, 09-21, req 9)* —
      «every cat» · «all cats»: `db/0029`, measured on 547 tk1 journeys (every 7–0 sg, all 24–0 pl).
      `takes_number`, NOT `number` — that column is the unknown's own and the gate caught the clash
- [x] **⚑ SCHEMA v7 — a number is `sg`·`pl`·`either`, and the format refuses the rest** *(the
      Captain, 09-21, req 2)* — `both`·`neither`·`either`·`each other` said `number: dual` meaning
      HOW MANY, and `_unknown` wrote it into zips. `db/0030` moves it to `count`. 4th same defect
- [x] **⚑ SCHEMA v8 + the relative clause's COMPILER half** *(the Captain, 09-21, req 36)* — a
      binder may introduce a variable without QUANTIFYING it; «the cat that sleeps» minted a free
      variable and threw `cat.n` away. 0 of 87 zips now name a variable nothing binds
- [x] **⚑ the relative clause's DECOMPILER half** *(09-22, req 36)* — an unasserted row sharing a
      binder's variable IS that binder's relative clause; dropping it claims MORE than the zip.
      `db/0031` speaks it with «that». **`aw-13`/`aw-14` fixed — SILENT 3 → 1** (it absorbed «a binder
      the decompiler cannot say», the same item under a second name)
- [x] **drill automated = acceptance gate** *(ticked 09-20 — it was already met)* — `tests/test_drill.py`
      scores the bar, keeps the forced-change ledger and prints the report on every suite run
- [x] **⚑ the frame/knowledge audit — E3's closing act** *(09-22)* — 52 constants walked, four move,
      two of the plan's own suspects cleared as STALE. The flagged family was two: reading the tree's
      shape is frame, ruling what a shape MEANS is not. Record `202609220930_…`
- [x] **the audit's migration — `db/0032`, three arguments out of code** *(09-22)* — `vocative`
      compiles to nothing · `xcomp` opens no row · only a NOUN states a number. `CLAUSE_DEPS` got
      BIGGER and is now pure transcription. Measurements unmoved. `SAYING_VERBS` waits for E4
- [x] **⚑ task 9 — THE DOMAIN, the fifth prefix element, built at last** *(09-22, rules reqs 6-7)*
      — the station had NEVER raised a `DomainRow`; the schema, the decompiler and three drill
      cases were all waiting. Two signals, measured clean in both directions on
      `tools/domain_bench.py`: a fronted `as` (a capacity) and a fronted phrase whose BOX IS
      CONTESTED. **`aw-15` green, and France stopped being `unplaced`** — a word lost, not misfiled
- [x] **a bare fronted locative is IRREDUCIBLE and the station abstains** *(09-22, a RESULT)* —
      «Legally, in Italy, he is still married» (DOMAIN) and «In France, I ate well» (LOCATION) are
      identical on every fact the parse gives. `aw-17` stays red honestly rather than green on a
      rule that would invent domains elsewhere
- [x] **⚑ «An animal is.» was the MATCHER eating a noun** *(09-22)* — not a quantifier defect at
      all: `select` returned a single-row form without ever consulting the POS, so the NOUN «being»
      matched the copula's participle, read as structure, and took the subject with it. **221 of
      331 forms are single-row and ≥17 are ordinary words** — «the BACK of the house», «a CAN of
      soup», «the WILL of the people» each lost a noun. Read-whole 72 → 73. Record `202609221200_…`
- [x] **⚑ `as far as` — a curation row AND a reader defect** *(09-22)* — `db/0033` supplies the
      marker `db/0015` named and the table never had. But the row alone made it WORSE: stanza reads
      the phrase two ways and in the past tense the nominal hangs off a token INSIDE the marker,
      with no `case` child. Reading the marker's SPAN holds under both. Read-whole 73 → 74
- [x] **⚑ `UD_DEP_TO_ROLE` unwelded — the order never decided, and frame is not «what goes in code»**
      *(the Captain, 09-24)* — benched: reversing every tuple moved nothing. The sets are rows
      (`db/0034`), the ranking is deleted, a tie nobody settles abstains. `t-ng-4`'s «No» stops being
      a quantifier: drill 66 → 67, read-whole 74 → 73. Record `202609240900_…`
- [x] **⚑ G5 — the relative gap OVERWROTE the clause's subject, and a crash** *(09-24)* — «the fish
      that the cat ate» claimed the fish ate. The gap now takes its position's role; a gap nobody can
      place WITHHOLDS the clause. Read-whole population 73 → 71, honestly. Record `202609241130_…`

### still open — in the order they are to be done, and nothing waits on anything below it

- [ ] **the fixpoint's 9 remaining — READ 09-24: ten mechanisms, G1–G10, G5 done** — not three
      causes. Four want the Captain (G1 · G6 · G7 · G9), plus the ZERO RELATIVE: «the fish the cat
      ate» vs «the day I slept» — only valency tells, and the station has none. Record `202609241130_…`
- [ ] **confidence scalar — MEASURED AND DEFERRED** *(09-20, req 4)* — no band is decisive
      (`tools/confidence_bench.py`); 5 negatives only, and the round trip still measures the
      DECOMPILER. Bookkeeping kept, scalar EMPTY. **Waits on the 11 above**
- [ ] **the domain's two open halves** *(09-22, both measured or reasoned, neither guessed)* — a
      fronted ADVERB («Legally,») needs `legally` → `law.n`, a derivation the compiler has no reader
      for and which the decompiler already refuses to say · a NON-fronted `as` («I work as a
      teacher») was never benched, and may be the job rather than the frame
- [ ] **FIVE SMALL THINGS RECORDED RATHER THAN FIXED** *(09-21/24)* — none load-bearing, each named
      where it was found: a DEFINITE's relative clause is a presupposition and is kept claimed so
      the brain gets the fact · a quantifier's DOMAIN CARDINALITY is not in the zip, so «Neither is
      late» reads back a bare negative (`Box.count` is where it goes) · «one another» keeps
      `number: pl`, the same column confusion as `dual` but admissible · a clause-headed phrase
      takes the PLURAL universal on the QM's grammar, not on evidence · discourse «No» (an answer
      particle) has no reading and now goes unplaced — `t-ng-4`, 09-24

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
      no rule about Anna anywhere. E3b's acceptance test, and the drill gate's red `aw-19`
- [ ] **anaphora** *(moved from E3, the Captain 09-20)* — «she» has its features since v4; what is
      missing is that Marie is feminine, a named individual's ATTRIBUTE. The drill gate's reds `q-6` ·
      `t-dc-5` (the fourth, `t-ws-7`, is a stanza misparse the station abstains on)

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
