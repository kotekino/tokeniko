# tokeniko 2 — ROADMAP

*The checkable mirror of `plan.md`: **one line per item**, one item one status, done moves to
`landed.md`. ⚑ = vertical proof slice under the Captain's eye.*

> **EVERY ITEM HAS A NESTED, IMMUTABLE ID** *(the Captain, 2026-09-25)* — `E3.3.2.5` is the fifth
> thing found under `E3.3.2`, which is under `E3.3`, under E3. The id is an IDENTITY, not a position:
> never renumbered, never reused, identical in `plan.md` and in the chapter notes that elaborate it.
> The ORDER of a list is execution order, so ids need not be sequential. A moved item takes a new id
> in its new home and the old one keeps a pointer. Drill case ids (`t-ng-4`) name evidence, not work.

> **The reasoning is NOT here.** It lives in `docs/<chapter>/` — `requirements.md`, the dated
> `_notes.md` beside it, any `origin-*.md` — and in `plan.md` for the epics' tasks. A line here says
> *what* and points at *where*; a roadmap that grows prose is one nobody can read at a glance.

## E0 — the keel ✅ 2026-08-23 — see `landed.md`
## E1 — the dictionary at scale ✅ 2026-09-10 — see `landed.md`
## E1b — the names, and one baseline ✅ 2026-09-10 — see `landed.md`
## E1c — the sense layer ✅ 2026-09-10 — see `landed.md`
## E1d — the audit's repairs ✅ 2026-09-14 — see `landed.md`

## E1e — the tests, isolated *(opened 2026-09-17 — runs AFTER E3 closes)*
- [x] `E1e.8` **the pacing rule** *(answered 09-22, and the answer REVERSED it)* — the gate is
      `pytest -m spine` plus the section; the full suite is a DEPLOY condition, on the body. And the
      suite was slow by DEFECT: `Migration.load` re-ran the chain, now memoised (186s → 0.2s). Root
      `CLAUDE.md` holds the rule, `tokeniko-tk2/CLAUDE.md` the commands. Record `202609220900_…`
- [x] `E1e.8.1 · E1e.8.2` **the gate's contract, leaking** *(09-26)* — the spine no longer reaches WordNet; 16 stanza tests marked `skeleton`
- [x] `E1e.9` **a tool read the biography around the guard — disabled** *(09-26)*; its door waits on `E3b.3.2`
- [x] `E1e.6.1` **the drill amended to the purpose ruling** *(09-26, brought forward by the Captain)* — `t-ws-1`, `aw-6` agree;
      drill gate 65 · 6 · 16 → 67 · 4 · 16, the ratchet green. Bar doc `E2-tkzip/202609140917_…` AMENDMENTS
- [ ] `E1e.1` **⚑ sweep E0 → E3 for test material leaking into the BL** — formal order included
- [ ] `E1e.6` **the triage — tests follow decisions** *(09-25)* — on the closed E3: (a) code wrong → code · (b) expectation wrong → test · (c) agree → keep
- [ ] `E1e.6.2` the drill's «If I tell you something…» row has no `know.v`
- [ ] `E1e.10` **a held-out check for every exception row a gate justified** — proposed standing rule *(for the Captain)*
- [ ] `E1e.8.3` `test_migrations` is DB-bound at ~40 min inside the datatier's section gate
- [ ] `E1e.7` **the third kingdom** — frame · knowledge · **evidence**; evidence keeps the ledger properties
      but never runs in the app
- [ ] `E1e.2 · E1e.3` `dictionary_bar` out of the body; only `bar_version` + `bar_fingerprint` stay, as provenance
- [ ] `E1e.4` bar words become `extra_seeds` on a measuring run — **cost: moves the config fingerprint**
- [ ] `E1e.5` the doctrine line in `core/models/__init__.py` calls three things one thing

## E2 — the format (tkzip v2) ✅ 2026-09-14 — see `landed.md`

## E3 — the station (parser/compiler)
- [x] `E3.0` **the closed classes' SEMANTICS** — 383 rows carry a complete `compiled` (`db/0008`,
      `db/0009`)
- [x] `E3.1` **skeleton adapter** — stanza behind the lib boundary; nothing above imports spacy or torch
- [x] `E3.5.1.1` **⚑ the UD gate opens** — `tools/ud_gate.py`; nine defects nobody would have read off the code
- [x] `E3.5.1.2` **⚑ the gate scores the ZIP, not the table** *(09-16)* — needed `Compiled.placement`; four
      defects before one new case was added
- [x] `E3.5.1.3` **⚑ the UD gate reaches all 37 relations** *(09-16)* — 43 cases · 30 answered · 0 wrong · 13
      abstained; stanza produces 15 of UD's 18. Record `202609161050_…`
- [x] `E3.2.4` **compile core — one content row** — 18/25 UD cases whole, mean 89.5%
- [x] `E3.2.5` **compile core — many rows** — «if»/«because»/«and» are three zips (req 38, `db/0010`); 20/25
- [x] `E3.2.6` **the wh-word's box** — five kinds, not one (`db/0011`); 21/25 whole
- [x] `E3.2.7` **the thirteen ambiguous markers** — WordNet **supersense**, not geometry (`db/0012`); benched
      11/11 vs 6-with-3-wrong. 22/25 whole. Record `202609160929_…`
- [x] `E3.2.8` **content ADVERBS** — req 23's four scopes as rows; manner is the counted DEFAULT, the table
      holds the 106 exceptions (`db/0013`, `db/0014`). Record `202609161251_…`
- [x] `E3.2.8.1` **`db/0014` — the two gaps the clash check found**; repairing them left the exclusion set at 268
- [x] `E3.2.8.2` **the dirty-check gained a fourth field** — which table filtered D's vocabulary is now recorded
- [x] `E3.2.9` **`amod` — attributive adjectives are SECOND ROWS** *(req 70)* — an adjective forces a binder;
      modifier joins chain per clause. Record `202609161215_…`
- [x] `E3.2.10` **the copular subject is the PATIENT, not the topic** — a slip against 43 hand-compiled rows
- [x] `E3.2.11` **`nummod` — the box's own `count` field** *(req 26)* — a numeral raises no binder
- [x] `E3.2.11.1` **number words — `word2number` admitted** — one door, so a machine without it only abstains
- [x] `E3.2.12` **embedded questions** — a wh-word has three readings; UD marks the difference and nothing else
- [x] `E3.2.12.1` **unassertion propagates into an enclosed clause** — a truth error found by the above
- [x] `E3.2.13` **a compiled form no longer ALSO abstains** — ratchet 24/25 at 99.4%
- [x] `E3.2.14` **`db/0015` — a marked phrase has an endpoint** — `direction` is a direction with NO endpoint
- [x] `E3.5.2` **⚑ the two gates meet — `tools/drill_gate.py`, req 18** *(09-16)* — it scores agreement, not
      equality. Widened twice on 09-17 (a context, and the mirror test). Record `202609161502_…`
- [x] `E3.2.1` **⚑ the person axis — the rotation under a point of view** *(req 20)* —
      context-as-argument · multi-sentence input · **schema v3: `addressee`** · the rotation · the
      quote as unclaimed content. Records `202609161349_…`, `202609161544_…`
- [x] `E3.2.1.1` **⚑ the rotation was INVERTED — found and fixed** *(09-17)* — quotation rotates, reporting does
      not; the signal is structural and no character is ever read. Record `202609170533_…`
- [x] `E3.2.1.2` **the truth slot under an attitude — RULED: the rows keep their truth** *(09-17)*
- [x] `E3.2.2` **⚑ a polar question opens its truth** *(09-18, req 21)* — the `?` decides, per statement. Record `202609180900_…`
- [x] `E3.2.3` **⚑ the imperative is a want, not a claim** *(09-18)* — `Mood=Imp`; `aw-21` agrees. `strength` and «Suppose…» asked
- [x] `E3.2.2.1` **`whether` / `if` on a complement ask** *(09-18, `db/0016`)* — the clause decides: `ccomp` asks, `advcl` supposes
- [x] `E3.2.15` **`or` / `nor` claim only the join** *(09-18, `db/0017`)* — the Captain's (b)
- [x] `E3.2.15.1` **free choice under a modal** *(09-18)* — both halves under «can»/«may» are claimed; `t-ws-7` is a stanza misparse, abstained
- [x] `E3.2.16` **the subject's role depends on WHAT IS PREDICATED of it** *(09-18, req 22, `db/0018`)* — a
      supersense rule as rows; twelve drill roles amended; the ratchet falls to three
- [x] `E3.5.2.1` **⚑ the drill gate sees the PREFIX** *(09-19, req 18's fourth widening)* — 89 prefix rows and
      50 joins enter the instrument; attitudes pair on their verb. Record `202609190900_…`
- [x] `E3.2.16.1` **⚑ a coin toss in the station's own reading** *(09-19)* — NLTK keeps synset pointers in a
      `set`; `derived_supersense` now reads the whole relation and abstains when it disagrees
- [x] `E3.2.3.1` **the imperative's two questions — `strength` is knowledge, an imperative does not collapse**
      *(09-19, reqs 23-24)* — `db/0019` and `db/0020` applied; `aw-20` a named divergence on req 55
- [x] `E3.6` **⚑ the placement floor — MEASURED AND REFUSED** *(09-19)* — 40 placements ruled; the
      verdicts interleave with the cosine in both halves, so no floor separates them. Record
      `202609191500_…`
- [x] `E3.3.3` **the TENSE and the VOICE, which the station never wrote** *(09-20, reqs 25/26)* — theatre from
      UD's finite `Tense`, topicality from `nsubj:pass`; `db/0024` past + participle, 862 rows
- [x] `E3.3.3.1` **SCHEMA v5 — the theatre is a field PER ROW** *(the Captain, 09-20)* — one slot per zip could
      not say «I went to Rome and I WILL GO to Genoa»; on a content row and on an attitude
- [x] `E3.3.4` **a zip came out a DAG where a sentence is a tree** *(09-20)* — coordination binds tighter, so
      a `conj` replaces the clause it extends; an attitude's own clause dissolves into it
- [x] `E3.2.16.2` **`look` → agent · `die` → patient** *(09-20, `db/0025`, req 22)* — exposed when the station
      stopped compiling an unresolved pronoun as OPEN, which the gate had been abstaining on
- [x] `E3.6.1` **⚑ the placement rule, in place of a number** *(09-19, dictionary req 22)* — a stated
      edge is trusted, the sibling fallback and D abstain; 19.4% coverage, 0 wrong trusts
- [x] `E3.2.1.3` **`mark` under a reporting verb opens a POV**, not a join — built with `db/0010`'s `asserts: matrix`; ticked 09-18
- [x] `E3.3` **the DECOMPILER** *(renamed from «renderer/scaffold» by the Captain, 09-19, req 9)* — joins ·
      quantifiers · prefix · questions · the person axis · tense · voice all built; fixpoint 24 → 68
      of 87 on 09-20, **76 · 11 · 0 and 66 of 72 read whole by 09-25**. Record `202609201100_…`
- [x] `E3.3.1` **SCHEMA v4 — an OPEN slot says what is known about the unknown** *(the Captain, 09-20, req 27)*
      — `sort`·`person`·`number`·`gender`; three kinds of unknown, no heuristic. `db/0026`. **And
      tkzip req 73 rewritten: there are no frozen schemas in a blueprint**
- [x] `E3.3.5` **⚑ `fused_quantifier` — «no» takes a noun and «nobody» IS one** *(09-21, req 9)* — `db/0028`
      flagged five voices onto three occupied index slots in silence; the role now splits them and
      the ratchet is a count. Record `202609210900_…`
- [x] `E3.3.6` **SCHEMA v6's compiler half — `Box.number` from UD's `Number`** *(09-21, 1st Officier, req 26)*
      — `t-md-1` «Software can be minds» round-trips at last; a PROPER noun takes none, because its
      number is a fact about the REFERENT and names are E3b. `db/0027`'s plurals are live
- [x] `E3.3.6.1` **⚑ the existential copula agrees with what it displaced** *(09-21, found by the 1st Officier)*
      — «There is no cats», then «There be no cats»: `be` was on the regular-verb path, where a
      non-third-singular is spoken as the bare lemma. An existential is not flagged copular (req 31)
- [x] `E3.3.7` **⚑ SILENT 1 → 3 and 69 → 67 whole were ONE fact, and the instrument's** *(09-21)* —
      `aw-13`/`aw-14` went MOVED → SILENT; a silent case printed only under `--all` and was
      SUBTRACTED from the read-whole population. The honest denominator is 70 and always was
- [x] `E3.3.8` **⚑ `aw-13`/`aw-14` — «All that glitters is not gold» binds the quantifier to the PREDICATE
      NOMINAL** and orphans the relative clause's row; the first 1st-Officier task — the COMPILER
      half is fixed and both agree at the gate; ticked 09-21
- [x] `E3.3.5.1` **⚑ a quantifier's voice depends on the NUMBER of its noun** *(the Captain, 09-21, req 9)* —
      «every cat» · «all cats»: `db/0029`, measured on 547 tk1 journeys (every 7–0 sg, all 24–0 pl).
      `takes_number`, NOT `number` — that column is the unknown's own and the gate caught the clash
- [x] `E3.3.5.2` **⚑ SCHEMA v7 — a number is `sg`·`pl`·`either`, and the format refuses the rest** *(the
      Captain, 09-21, req 2)* — `both`·`neither`·`either`·`each other` said `number: dual` meaning
      HOW MANY, and `_unknown` wrote it into zips. `db/0030` moves it to `count`. 4th same defect
- [x] `E3.3.8.1` **⚑ SCHEMA v8 + the relative clause's COMPILER half** *(the Captain, 09-21, req 36)* — a
      binder may introduce a variable without QUANTIFYING it; «the cat that sleeps» minted a free
      variable and threw `cat.n` away. 0 of 87 zips now name a variable nothing binds
- [x] `E3.3.8.2` **⚑ the relative clause's DECOMPILER half** *(09-22, req 36)* — an unasserted row sharing a
      binder's variable IS that binder's relative clause; dropping it claims MORE than the zip.
      `db/0031` speaks it with «that». **`aw-13`/`aw-14` fixed — SILENT 3 → 1** (it absorbed «a binder
      the decompiler cannot say», the same item under a second name)
- [x] `E3.5` **drill automated = acceptance gate** *(ticked 09-20 — it was already met)* — `tests/test_drill.py`
      scores the bar, keeps the forced-change ledger and prints the report on every suite run
- [x] `E3.8` **⚑ the frame/knowledge audit — E3's closing act** *(09-22)* — 52 constants walked, four move,
      two of the plan's own suspects cleared as STALE. The flagged family was two: reading the tree's
      shape is frame, ruling what a shape MEANS is not. Record `202609220930_…`
- [x] `E3.8.1` **the audit's migration — `db/0032`, three arguments out of code** *(09-22)* — `vocative`
      compiles to nothing · `xcomp` opens no row · only a NOUN states a number. `CLAUSE_DEPS` got
      BIGGER and is now pure transcription. Measurements unmoved. `SAYING_VERBS` waits for E4
- [x] `E3.9` **⚑ THE DOMAIN, the fifth prefix element, built at last** *(09-22, rules reqs 6-7)*
      — the station had NEVER raised a `DomainRow`; the schema, the decompiler and three drill
      cases were all waiting. Two signals, measured clean in both directions on
      `tools/domain_bench.py`: a fronted `as` (a capacity) and a fronted phrase whose BOX IS
      CONTESTED. **`aw-15` green, and France stopped being `unplaced`** — a word lost, not misfiled
- [x] `E3.9.1` **a bare fronted locative is IRREDUCIBLE and the station abstains** *(09-22, a RESULT)* —
      «Legally, in Italy, he is still married» (DOMAIN) and «In France, I ate well» (LOCATION) are
      identical on every fact the parse gives. `aw-17` stays red honestly rather than green on a
      rule that would invent domains elsewhere
- [x] `E3.3.9` **⚑ «An animal is.» was the MATCHER eating a noun** *(09-22)* — not a quantifier defect at
      all: `select` returned a single-row form without ever consulting the POS, so the NOUN «being»
      matched the copula's participle, read as structure, and took the subject with it. **221 of
      331 forms are single-row and ≥17 are ordinary words** — «the BACK of the house», «a CAN of
      soup», «the WILL of the people» each lost a noun. Read-whole 72 → 73. Record `202609221200_…`
- [x] `E3.3.10` **⚑ `as far as` — a curation row AND a reader defect** *(09-22)* — `db/0033` supplies the
      marker `db/0015` named and the table never had. But the row alone made it WORSE: stanza reads
      the phrase two ways and in the past tense the nominal hangs off a token INSIDE the marker,
      with no `case` child. Reading the marker's SPAN holds under both. Read-whole 73 → 74
- [x] `E3.8.2` **⚑ `UD_DEP_TO_ROLE` unwelded — the order never decided, and frame is not «what goes in code»**
      *(the Captain, 09-24)* — benched: reversing every tuple moved nothing. The sets are rows
      (`db/0034`), the ranking is deleted, a tie nobody settles abstains. `t-ng-4`'s «No» stops being
      a quantifier: drill 66 → 67, read-whole 74 → 73. Record `202609240900_…`
- [x] `E3.3.2.5` **⚑ the relative gap OVERWROTE the clause's subject, and a crash** *(09-24)* — «the
      fish that the cat ate» claimed the fish ate. The gap now takes its position's role; a gap nobody can
      place WITHHOLDS the clause. Read-whole population 73 → 71, honestly. Record `202609241130_…`
- [x] `E3.3.2.2` · `E3.3.2.3` · `E3.3.2.4` **⚑ a sentence is a tree, «the result OF perception», and no relative
      clause lost in silence** *(09-24)* — a tree ratchet over the drill; a consumed row is said or named in
      `unsaid`. Read-whole FIXED 62 → 63 of 71. Record `202609241130_…`
- [x] `E3.3.2.10` **⚑ «not necessarily», said at last** *(09-24)* — the decompiler reads the adverb table
      backwards (`db/0035` flags `necessarily`); SILENT 1 → 0, read-whole FIXED 63 → 64 of 71
- [x] `E3.3.2.10.1` **⚑ MODAL SCOPE — seven wrong claims, none left** *(09-24)* — an adverb scopes by its order
      against «not» (frame); where «not» falls after an auxiliary is per word (`db/0036`); «may
      not» withholds its clause. Record `202609241130_…`
- [x] `E3.3.2.1` · `E3.3.2.7` · `E3.3.2.9` · `E3.3.2.2.1` **⚑ purpose · the understood «to» · a supposed AND · «and
      therefore»** *(09-25)* — purpose is `imply(act, end)` (`db/0037`), the understood «to» is stored (schema v9), a supposed AND is supposed, a causal adverb replaces the
      «and». Every drill zip is a TREE. Read-whole 64 → 65 of 71. Record `202609241130_…`
- [x] `E3.3.2.5.1` **⚑ the zero relative — the gap's role when frames and supersense AGREE** *(09-25)* — `db/0038`;
      held-out 23 fresh cases: 7 right, 0 wrong. Read-whole 66 of 72. Record `202609241130_…`
- [x] `E3.3.11` **⚑ the fixpoint sees SCOPE** *(09-25)* — one `sorted()` erased prefix order; each
      target's prefix is now an ordered stack. Nothing was hiding: 76 · 11 · 0. Record `202609241130_…`
- [x] `E3.2.1.4` **⚑ TRUTH ERROR — quotes rotated only under nine listed verbs** *(09-26, the course check)* — «John
      exclaimed to Marie "You are late"» made the listener late; `_contexts` now asks what `_relate` asks. Record `202609260900_…`
- [x] `E3.2.1.5` **⚑ TRUTH ERROR — «She lives here» came back «Where does she live?»** *(09-26)* — schema v10:
      an `Open` keeps `deixis`·`distance` and is said, never asked. Context-vs-field is the Captain's
- [x] `E3.2.7.1` **WordNet through its one door** *(09-26)* — `supersense`, `frames` no longer import nltk; the `lexname` rebuild still owed
- [x] `E3.2.1.6` **⚑ TRUTH ERROR — «This is good» came back «Who is good?»** *(09-26, the QA)* — a pointed slot is said
      back from the rows on the features it carries; «These ARE mine»
- [x] `E3.1.1` **the provider pinned** *(09-26)* — a `station` optional group in `pyproject.toml`, `spacy` included
- [x] `E3.7` → moved to `E4.3.1` *(09-26)*: which sense a word has is not the station's (req 11)
- [x] `E3.12` **⚑ E3's EXIT RULED — honesty in full, coverage as a ratchet** *(the Captain, 09-26)* — wrong claims = 0 ·
      silent losses = 0 · quality ratcheted · `E3.8.3` · then the quality items move to `E3c` and E3 closes. Record `202609261100_…`
- [x] `E3.12.4` **proof slice 1 stays at `E4.7`** *(ruled 09-26)* — the fresh set is the outside check

### still open — in the order they are to be done, and nothing waits on anything below it

- [ ] `E3.12.1` **the open list sorted: wrong claim · silent loss · quality** — wrong claims: `E3.3.11.1` · `E3.3.11.2` · `E3.3.12` · `E3.3.2.1.1` · `E3.3.2.7.1` (to verify); silent losses: `E3.3.2.10.2` · `E3.3.2.4.2` · `E3.2.1.6.1` · `E3.2.1.6.3` (to verify)
- [ ] `E3.2.1.6.1` **⚑ «That» as a pronoun is lost in silence** *(09-26)* — «That is a cat» → «A cat is.»; the `relative` row places nothing
- [ ] `E3.2.1.6.3` «I saw that cat» → «I saw cat» — the demonstrative determiner leaves no trace *(a silent loss if unrecorded)*
- [ ] `E3.3.11.1` · `E3.3.11.2` **⚑ TWO TRUTH ERRORS: a negation and an attitude** *(09-25)* — «I think that he
      does not sleep» puts ¬ OUTSIDE the thinking; «I do not think that he sleeps» claims both.
      Neg-raising is a reading for the Captain. Record `202609241130_…`
- [ ] `E3.3.12` **⚑ «I remember the day I slept» is a WRONG COMPLETE ZIP** *(09-25)* — stanza's `obl:tmod` on the
      matrix; the withheld clause used to hide it. Seven bench cases. Record `202609241130_…`
- [ ] `E3.12.2` **⚑ the fresh set** — 100 UD-EWT sentences frozen before the run; every complete zip judged for wrong claims and silent losses
- [ ] `E3.8.3` **the frame/knowledge audit, re-run at E3's real close** *(09-26)* — ten constants arrived after it
- [ ] `E3.12.3` **at E3's close, every open quality item moves to `E3c`** — below this line, quality only, except the wrong claims and silent losses `E3.12.1` names inside `E3.3.2`
- [ ] `E3.2.1.6.2` «I was happy» decompiles as «I were happy» *(09-26)*
- [ ] `E3.2.1.6.4` «What is this?» comes back «Is this what?» *(09-26, the QA of `9b0eb7c`)*
- [ ] `E3.3.11.3` … `E3.3.11.8` **the scope reading's smaller findings** — `E3.3.11.3` the fixpoint blind to a chain's
      truth (a ruling) · `E3.3.11.4` the drill gate blind to prefix order · `E3.3.11.5` «by by» · `E3.3.11.6` «need not» read as a verb ·
      `E3.3.11.7` no domain before a modal · `E3.3.11.8` a modal carries no theatre. Record `202609241130_…`
- [ ] `E3.3.2` **the fixpoint's 6 remaining** — `E3.3.2.8` correct English the provider misreads (a bench
      against the 66 FIXED first) · `E3.3.2.6` → `E3b.6.1` · first-leg misparses · `E3.3.2.4.1` · `E3.3.2.4.2`
      two bookkeeping defects · `E3.3.2.10.2` «So» / «and so» lost in silence · `E3.3.2.1.1` «so»
      claims its consequence backwards. Record `202609241130_…`
- [ ] `E3.4` **confidence scalar — MEASURED AND DEFERRED** *(09-20, req 4)* — no band is decisive
      (`tools/confidence_bench.py`); 5 negatives only, and the round trip still measures the
      DECOMPILER. Bookkeeping kept, scalar EMPTY. **Waits on `E3.3.2`**
- [ ] `E3.9.2` **the domain's two open halves** *(09-22, both measured or reasoned, neither guessed)* — a
      fronted ADVERB («Legally,») needs `legally` → `law.n`, a derivation the compiler has no reader
      for and which the decompiler already refuses to say · a NON-fronted `as` («I work as a
      teacher») was never benched, and may be the job rather than the frame
- [ ] **the side findings, numbered 09-26** — `E3.3.2.12` expletive · `E3.3.2.13` agreement ·
      `E3.3.2.1.2` purpose under an imperative · `E3.3.2.7.1` «asked Anna where» · `E3.3.2.10.3` `closed_forms` ·
      `E3.3.2.10.4` «can't» · `E3.3.2.10.5` «could» · `E3.3.2.10.6` `_withhold` · `E3.3.2.10.7` archaic question ·
      `E3.3.2.5.1.1` stative subject · `E3.3.2.5.1.2` «she bore» · `E3.3.2.5.1.3` «i». Listed in `plan.md` `E3.3`; record `202609241130_…`
- [ ] `E2.3.1` **two spellings of one attitude — `Pov` and `AttitudeRow`** *(09-26, for the Captain)* — before E4 compares zips
- [ ] `E3.3.4.1` **the format enforces less than the ratchets test** *(09-26, for the Captain)* — free variables, tree-ness, `Ref` placement
- [ ] `E3.10` **a compiled zip cannot say what compiled it** *(09-26, data-modeling req 7)* — before the first zip is stored
- [ ] `E3.11` **the station reads its knowledge from migration FILES** *(09-26)* — the r-cache at PS1 / E10
- [ ] `E3.13` **ten carried-in features placed nowhere** *(09-26)* — an epic each, or «stays OUT» with a reason
- [ ] `E3.2.17` **the compile core's shape** *(09-26)* — one state, one module per pass; at E3's close
- [ ] `E3.3.13` **FIVE SMALL THINGS RECORDED RATHER THAN FIXED** *(09-21/24)* — none load-bearing, each named
      where it was found: a DEFINITE's relative clause is a presupposition and is kept claimed so
      the brain gets the fact · a quantifier's DOMAIN CARDINALITY is not in the zip, so «Neither is
      late» reads back a bare negative (`Box.count` is where it goes) · «one another» keeps
      `number: pl`, the same column confusion as `dual` but admissible · a clause-headed phrase
      takes the PLURAL universal on the QM's grammar, not on evidence · discourse «No» (an answer
      particle) has no reading and now goes unplaced — `t-ng-4`, 09-24

## E3c — the station's long tail *(opened 2026-09-26 by `E3.12` — runs beside E4)*
- [ ] its tasks arrive at E3's close (`E3.12.3`): every open quality item, `E3.2.17`, `E3.4`

## E3b — the name *(opened 2026-09-16 — the parked hole, reopened and widened)*
- [ ] `E3b.1` **is it a name at all?** — stanza vs spaCy NER measured; `PROPN` and casing as weak evidence
- [ ] `E3b.2` **a name of what? — OUR kinds, as ROWS not code** — two tables, so a model's new label is a
      migration and not a release
- [ ] `E3b.3` **the places table, INHERITED** — 4,674,701 curated rows, a 21-value `type` that is an `is_a`;
      read lazily, never materialized
- [ ] `E3b.3.1` **the names list, INHERITED — and it cannot be a TEST** — 21,975 rows, **28.1% also place
      names**. Evidence, never a test: it is the measurement that forces the net
- [ ] `E3b.3.2` **the door to tk1's rows** *(09-26, for the Captain)* — snapshot from tk1's side, or a read-only datatier door; serves `E3b.3` · `E3b.3.1` · `E3b.4`, `E9.3`, `E1e.9`
- [ ] `E3b.4` **have I met it?** — recognition; the mechanism is E3b's, the rows are E9's
- [ ] `E3b.5.1` **⚑ the MICRO-NN abstraction — brought forward from E5**; built to serve the next line and
      generalized against it, never before it
- [ ] `E3b.5` **⚑ which one? — the first instance** — «Paris, France» or «Paris, Ontario»: the first case
      where curation cannot finish AND the answer moves over time
- [ ] `E3b.6` **what a name is in a zip** — type centroid = SEMANTIC, uid = IDENTITY, never merged
      · `E3b.6.1` *(was `E3.3.2.6`, moved 09-25)*: nothing in a zip says a head is a name, so «marie» loses
      its capital and stanza reads «to marie» as an infinitive — `q-1`, and part of `q-7` · `aw-6`
- [ ] `E3b.7` **the markers' third reading** — «went with Anna» is comitative because Anna is a PERSON, with
      no rule about Anna anywhere. E3b's acceptance test, and the drill gate's red `aw-19`
- [ ] `E3b.8` **anaphora** *(moved from E3, the Captain 09-20)* — «she» has its features since v4; what is
      missing is that Marie is feminine, a named individual's ATTRIBUTE. The drill gate's reds `q-6` ·
      `t-dc-5` (the fourth, `t-ws-7`, is a stanza misparse the station abstains on)

## E4 — the evaluator
- [ ] `E4.1` verdict shape (pure; truth · status · bindings · derivation)
- [ ] `E4.2` form kernel (logic floor migrated)
- [ ] `E4.3` bind-and-ground (one search; dual read; ABSTAIN first-class)
- [ ] `E4.3.1` the unplaced sense — 3.1% placed by neither half *(was `E3.7`)*
- [ ] `E4.4` chaining migrated + generalized
- [ ] `E4.5` budget + micro-nn ordering hook
- [ ] `E4.6` stake resolution
- [ ] `E4.8` **⚑ LIMIT B has no owner** *(09-26, for the Captain)* — no task builds the zip's geometry (tkzip reqs 11–17); req 11 flagged since 09-14
- [ ] `E4.7` ⚑ PROOF SLICE 1: text → zip → verdict, end-to-end on sandbox

## E5 — the instinct middleware (parallel after E0)
*The MACHINERY moved to E3b (2026-09-16): a framework that meets a real case before it is declared
general is the failure mode «one abstraction, many instances» is most exposed to.*
- [ ] `E5.1 · E5.2` ~~the lib~~ · ~~instance registry + structural fence~~ — **BUILT IN E3b**
- [ ] `E5.3` instance breadth: station calibration · evaluator ordering · then the sites that need an organ
      · «I promised her TO go» = WE go: control beyond the complement rule *(09-25, `202609241130_…`)*
- [ ] `E5.4` reward plumbing (intellectual + heart families) — arrives with E7 and E8

## E6 — the mind (rules + brain)
- [ ] `E6.1` rules as zips (sign-gated matcher; urge collapse; defeat in context)
- [ ] `E6.2` the three sockets (say · swapPhase · commit)
- [ ] `E6.3` the loop (dna) + phases as kb reweighting
- [ ] `E6.4` working set (cosine proposal; brain_state)
- [ ] `E6.5` self-talk + summarizing (provenance, retreat with parents)
- [ ] `E6.6` seeding + the etiquette worked example
- [ ] `E6.7` revision economics (depth-weighted cost; derivative guard)
- [ ] `E6.8` step-7 test green (seeded rule revised, no hand edit)

## E7 — the heart
- [ ] `E7.1` spheres & spikes tables (dna curves as db-r)
- [ ] `E7.2` three tiers + emotional log
- [ ] `E7.3` wiring (evaluator in; mood → phases; tone out; reward → E5)
- [ ] `E7.4` forecast stakes (hope(x); imagination gain)
- [ ] `E7.5` ⚑ PROOF SLICE 2: teach → contradict → retreat → disillusion → tone shift

## E8 — the voice and the ears
- [ ] `E8.1` adapter framework + Discord
- [ ] `E8.2` the mouth (render · color · polish; the fence)
- [ ] `E8.3` channel register (learned rows)
- [ ] `E8.4` rag port (escalation-only; kill-switch proven)
- [ ] `E8.5` THE CONSOLE (rag-off channel property; identity binding decided FIRST)
- [ ] `E8.6` same-person linking as KB belief
- [ ] `E8.7` ⚑ PROOF SLICE 3: a stranger's first hour, messy input live

## E9 — the translation night
- [ ] `E9.1` additive translation (v2 zips BESIDE v1; biography intact)
- [ ] `E9.2` KB translation (no hand-fixes)
- [ ] `E9.3` no-regression ratchet green — `tkzipdebug`: 529 clean journeys, 209 v1 read wrong
- [ ] `E9.4` the migration night of sleep — observed

## E10 — the embodiment & the window
- [ ] `E10.1` interpreter runtime on the mini (process split; runbook)
- [ ] `E10.2` cutover (guard boundary moved; v1 kept runnable)
- [ ] `E10.3` window rewire (mock → live KPIs)
- [ ] `E10.4` observability (probes, bars, maps, heart dashboard)
