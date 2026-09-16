# tokeniko 2 — ROADMAP

*The concise mirror of `plan.md` — where we are, what's ahead. One item, one status; done moves to
`landed.md`. ⚑ = vertical proof slice under the Captain's eye.*

> ### ⚠ THE ROADMAP IS THE OVERARCHING PLAN ONLY
> **The reasoning that decides anything lives in `docs/<chapter>/`** — `requirements.md`, the dated
> `_notes.md` beside it, and any `origin-*.md`. That is the **decision record**, not background:
> a great deal of argument between the Captain and the QM is there and nowhere else, including
> positions tried and refuted. **Read the chapter, in full, before elaborating any point in it.**
> *(The Captain's ruling, 2026-09-11 — see `CLAUDE.md` for what produced it.)*

*Standing law since 2026-08-25 (`plan.md`, before the epics): a closed set is **frame** (code — the
shape in which things are stated, revisable only by migration), **curation** (db rows,
generated-then-curated, recorded in the manifest — the bar included), or **open** (geometry with a
nearest-anchor fallback — never a list). Empirical is knowledge, however certain: a closed
grammatical class is KB, not frame. E3 pays the first real bill.*

## E0 — the keel ✅ 2026-08-23 — see `landed.md`

## E1 — the dictionary at scale ✅ COMPLETE 2026-09-10 — see `landed.md`

## E1b — the names, and one baseline ✅ 2026-09-10 — see `landed.md`

## E1c — the sense layer ✅ 2026-09-10 — see `landed.md`

## E1d — the audit's repairs ✅ 2026-09-14 — see `landed.md`

## E1e — the tests, isolated *(opened 2026-09-17 — runs AFTER E3 closes)*

- [ ] **⚑ SWEEP E0 → E3 FOR TEST MATERIAL LEAKING INTO THE BL** *(the Captain, 2026-09-17)*.
      *«Tests should be the gate for each dev step, but WELL isolated from the BL… look into
      everything we have done from E0 to E3 and see if tests, somehow, are leaking into the BL code
      (at least from a formal order point of view).»* The known case is `dictionary_bar`, which is
      not only stored in the body but wired into the runtime config: `DictionaryConfig.seeds`
      forces the bar's own words into every subset (req 8), so **the acceptance test injects its
      vocabulary into the artifact it judges** and rides in the fingerprint every consumer reads
- [ ] **THE THIRD KINGDOM** — frame (law) · knowledge (revisable facts the app reasons with) ·
      **evidence** (curated circumstances that JUDGE the app; isolated, never read at runtime).
      *«A test is by its nature a curated set of circumstances: it can't be knowledge.»* Evidence
      keeps the LEDGER properties — versioned, append-mostly, `why` verbatim — which are separable
      from which database. `closed_classes` is NOT in this kingdom: the station reads it at runtime
- [ ] `dictionary_bar` out of the body; the body keeps only `bar_version` + `bar_fingerprint` as
      provenance, checkable against the hash-pinned `bar_snapshot.json` that already exists
- [ ] bar words become `extra_seeds` on a measuring run, not standing seeds. **Cost: this moves the
      config fingerprint**, so builds recorded under the old one stop being directly comparable —
      E9-shaped, not a free edit
- [ ] the doctrine line in `core/models/__init__.py` calls policy, bar and closed classes one thing;
      it is three things now
- [ ] **THE PACING RULE** *(the same ruling)*: during development run only the subset that STEERS
      the next decision; **the full suite runs once, at the commit gate**. *«Burdening every single
      move with a gargantuan suite for each micro step is really slow — many work remotely on the
      body, so there is latency.»*

## E2 — the format (tkzip v2) ✅ COMPLETE 2026-09-14 — see `landed.md`

## E3 — the station (parser/compiler)
- [ ] **the placement floor** — inherited from E1c/E1d, measured 2026-09-14: the base's +0.15 was
      fitted on base-to-base cosines (p90 +0.000) and says NEAR to **99.7%** of relations-placed
      senses. A placement needs a floor fitted to placements, and a bar to fit it against
- [x] **task 0 — the closed classes' SEMANTICS** — 383 rows carry a complete `compiled`; 41 re-typed
      at v2 (`db/0008`) and 11 corrected at v3 (`db/0009`), both applied. `tk2/language/closed.py`
      reads them: longest-first for the 63 multi-word forms, UD deciding the job for the 45
      ambiguous ones
- [x] **skeleton adapter** — stanza behind the lib boundary (`tk2/language/skeleton.py`); `Skeleton`
      and `Word` hold UD strings and nothing above imports spacy, stanza or torch
- [x] **⚑ the UD gate OPENS** — `tools/ud_gate.py`, offline by default. It has found **nine** defects
      nobody would have read off the code
- [x] **⚑ the gate SCORES THE ZIP, not the table** *(2026-09-16)* — it was measuring half a station,
      and the relations still unreached were almost all COMPILER questions. Needed
      `Compiled.placement` first: a per-token record of WHERE each word went (`box:location`,
      `prefix`, `join`, `predicate:r1`, `field:relation`, `structure`), which is also what req 4's
      confidence scalar reads. **It found four defects before a single new case was added** — three
      words «reaching no part of the zip» in sentences that compiled at 100%, «the cafe up beside the
      lookout» read as a POSSESSOR, «out of the box» throwing its marker's meaning into the default,
      and a vocative merely unplaced rather than deliberately dropped
- [x] **⚑ the UD gate COMPLETED — EVERY ONE OF THE 37** *(2026-09-16)*: 43 cases · **30 answered ·
      0 WRONG · 13 abstained**. 34 relations have a case, **2 do not arise in English** (`clf`,
      `dislocated` — UD's own pages print no English example) and **1 is UD's own abstention**
      (`dep`). Three states, never two: folding «not in English» into «not yet reached» makes the
      coverage number a lie in the flattering direction.
      **AND A SECOND PROVIDER MEASUREMENT (req 2): stanza produces 15 of the 18 relations UD
      publishes on these sentences.** The three it does not — `goeswith`, `orphan`, `reparandum` —
      are one family: a typo, a gapping, a self-correction. The station will never meet them labelled
- [x] **`amod` — attributive adjectives are SECOND ROWS** *(2026-09-16, tkzip req 70)*: «a human
      body» is ∃B(body(B) ∧ human(B)) — and the shape was not designed here, the drill hand-compiled
      it at E2. The adjective row has NO predicate (req 31), its subject is the PATIENT, and **the
      binder scopes the JOIN** because the variable lives in both rows. **An adjective forces a
      binder even with no quantifier word**: a row saying `patient=body.n, complement=human.a` would
      claim BODIES are human. And the modifier joins **chain per clause into ONE tree** — two
      modified nouns first produced two joins both naming the content row, which is sound and is not
      what the drill does. **Ratchet 23/25 at 98.9%; frontier 7/18 at 80.8%; gate 31 answered,
      0 WRONG.** Record: `202609161215_the-attributive-adjective.md`
- [x] **the copular subject is the PATIENT, not the topic** — a compile-core slip found by reading
      the drill while building `amod`. `topic` in this inventory is SUBJECT MATTER («a lecture ON
      physics») and the drill uses it for that alone, three times, while hand-compiling the copular
      row as patient + complement **43 times**. E2 ruled the shape outright
- [x] **⚑ THE TWO GATES MEET — `tools/drill_gate.py`, req 18** *(2026-09-16)*. It scores AGREEMENT,
      not equality: most of the drill needs features E3 has not built, so a zip-equality check would
      fail all 78 and teach nothing. Rows pair on their predicate (a copular row on its complement),
      boxes on their HEAD — so `patient: sue.n` against `topic: sue.n` is one filler under two names,
      which is the defect it was built for. A VARIABLE is never a conflict.
      **IT CRASHED THE COMPILER BEFORE IT COULD SCORE**: six of the Captain's own sentences stopped
      the station dead — a `SPACE` token (his «[de dicto]» annotations leave whitespace stanza tags
      outside UD's seventeen) and **two rows called `m0`**, which no UD sentence could produce because
      none carries both a modal and an attributive adjective.
      **SIX DISAGREEMENTS → FOUR.** Two were curation errors (`db/0015`); the four that remain are
      questions the project has NAMED. **38 sentences agreed · 4 DISAGREED · 91 of 126 rows paired ·
      64 of 123 roles agreed**, and the four are a RATCHET held by a test.
      **WIDENED TWICE ON 2026-09-17, both times because the quotation block walked past it.** It
      passed NO CONTEXT, so every pronoun in the drill compiled to itself and the person axis was
      invisible by construction — it now passes the drill's own convention (`speaker="me.n"`,
      `addressee="you.n"`), which leaves every unrotated sentence compiling exactly as before. And it
      could see only half a disagreement: it paired boxes by FILLER and asked about the ROLE, the
      shape of the `topic`/`patient` defect it was built for, and was blind to the mirror — **the
      right role holding the wrong somebody**, which is the only shape the person axis fails in.
      **47 agreed · 15 DISAGREED · 98 of 129 roles**; 11 of the 15 were always there
- [x] **`db/0015` — a MARKED phrase has an endpoint** — «I walk TOWARD the station» compiled a
      DIRECTION and the drill says DESTINATION, across three hand-compiled rows differing only by
      marker (req 65 exists so they share a box). **The principle is sharper than the witnesses**:
      req 67's `direction` is *a direction with NO ENDPOINT*, and a marked phrase has one — the
      nominal IS the endpoint. Five rows corrected, and the migration refuses to apply if any marker
      offers `direction` alone. Plus **«She turned LEFT» read as MANNER — the sentence req 67 was
      written for** — because `db/0013`'s direction list held `sideways` and not `left`
- [ ] **the subject's role depends on WHAT IS PREDICATED of it** — one question: «God exists» is a
      PATIENT, «the cat is hungry» an EXPERIENCER, «Sue is a teacher» a patient.
      `RELATION_FILLS_ROLE`'s own comment defers it to the geometry — *«a head-verb question, and a
      station that guessed would be doing the compile core's job badly»*. **THREE WITNESSES BECAME
      NINE on 2026-09-17** (`exist-3` `t-ws-1` `t-ws-8` `t-dc-4` `t-mo-1` `t-of-1` `aw-11` `aw-16`
      `aw-20`), when the gate was given a context and the pronoun subjects it had never compared —
      «I go to sleep because I'm tired», «You learn only from minds you trust» — became comparable.
      The largest single family in the ratchet, which is an argument about WHEN, not about what
- [x] **content ADVERBS — requirement 23's four scopes, as rows** *(2026-09-16, `db/0013` + `db/0014`)*.
      **The resource cannot answer this**: WordNet files every adverb under ONE class (`adv.all`) and
      adverbs have NO hypernyms, so the supersense that settled the markers gives nothing. It is
      curation — and curatable only because **manner is the DEFAULT**: 79% of English's 3,767 adverbs
      are `-ly` and describe the action, so the table holds the 106 EXCEPTIONS. A default is COUNTED,
      never silent.
      **A SEPARATE TABLE, on the Captain's ruling**: «however» is a join like «because» and belongs in
      the closed classes by principle, but those forms filter D's vocabulary and 60 new ones would
      desynchronise the sealed base. Cost paid by making only the ROSTER second — `compiled` here is
      the closed classes' own vocabulary, so a reader cannot tell which table answered.
      **Frontier 9/18 at 82.2%; ratchet unmoved; gate 31 answered, 0 WRONG.**
- [x] **`db/0014` — the two gaps the clash check found** — it refused 11 forms already in the closed
      classes, and **10 were already compiled CORRECTLY there** (`so`, `yet` as joins;
      `anywhere`/`everywhere` as quantifiers over places; `inside`/`outside` as location boxes). The
      other two are real: `however` held only its free-relative reading, and `here`/`now`/`then`/
      `there` said `entity, resolve: context` without ever saying WHICH BOX. **Repairing them is
      FREE** — the exclusion set is a set of FORMS, so an edited `compiled` and a second row for an
      existing form both leave it at **268**
- [x] **the dirty-check gained a fourth field** *(the Captain: «fix it now, before any v7»)* — the
      closed-class forms filter D's vocabulary, and `SpaceOrigin` recorded build · seals · policy and
      NOT which table filtered it. A migration could move under a sealed base with nothing anywhere
      disagreeing. Recorded, not enforced: a table may legitimately run ahead of a base
- [x] **compile core — ONE content row** (`tk2/language/compile.py`): the relation half and the
      marker half of the mapping, quantifier binders, possessors inside the record, senses OPEN.
      **18 of 25 UD cases at 100% coverage, mean 89.5%**
- [x] **compile core — MANY rows**: one content row per clause, related by joins, attitudes and
      shared variables. **«if» / «because» / «and» are three distinguishable zips** (req 38, from a
      real parse). Needed closed classes v4 (`db/0010`) first: «if» and «because» had identical
      rows. **20 of 25 UD cases whole, mean 95.8%**
- [x] **the wh-word's box** — closed classes v5 (`db/0011`): five kinds, not one. `when`/`where`
      open a BOX · `who`/`what` a PARTICIPANT (the relation decides) · `whether` the TRUTH ·
      **`why` an ANTECEDENT** (there is no cause box — req 37 paying for itself) · `whose` a FIELD.
      **21 of 25 UD cases whole, mean 96.8%**
- [x] **`nummod` — the box's own `count` field** *(2026-09-16, tkzip req 26)*: `quantity`, `count`
      and `determination` are three ORTHOGONAL fields, so a numeral raises no binder and changes no
      scope — it is a field of the record, exactly as the possessor is. **Frontier 10/19 at 83.2%;
      gate 32 answered, 0 WRONG.**
- [x] **NUMBER WORDS — `word2number` admitted** *(the Captain, 2026-09-16)*, the fifth dependency
      and on `nltk`'s terms: **one door**, `compile.numeral_value`, so a machine without the package
      still parses and only the count abstains. The library is not trusted blindly — it returns **0**
      for some non-numerals, so a zero no word in the phrase asked for is refused. UD's own case
      arrived ABSTAINING and answered within the hour. **Frontier 11/19 at 84.5%; gate 33 answered,
      0 WRONG**
- [ ] **⚑ THE PERSON AXIS — E3 SCOPE** *(the Captain, 2026-09-16 — asked, answered NO, placed)* *(req 20, record
      `202609161349_the-person-axis.md`)*: «John said to Marie: YOU are a clever girl» — the `you`
      must rotate to Marie. tk1 managed all of it; **tk2 has one sentence saying a pronoun is
      indexical and nothing saying the context CHANGES inside a POV**. Four gaps: no person axis at
      all (`compile()` takes no context argument — req 7 written, not built) · the ADDRESSEE is a
      slot tkzip does not have, so where it lives is a FORMAT ruling under a frozen schema · stanza
      SPLITS a quote into its own sentence and the station has no multi-sentence path · and neither
      gate tests it (the drill has no quoted speech; the QM transcribed `ccomp` as the INDIRECT form
      and passed over UD's own direct-quote examples). **A wrong rotation is a wrong BELIEF, not a
      wrong parse** — well-formed, coherent, about the wrong person, and the evaluator cannot catch
      it. **Four sub-tasks in `plan.md` task 2b**, and the first two are DONE 2026-09-16:
      ~~context-as-argument~~ (req 7 built at last — the axis had its data since v1 and no caller to
      supply the other end; without a context nothing changes) · ~~multi-sentence input~~
      (`compile_utterance` — the drill gate reported five sentences half-read and now reads them
      whole) · ~~the FORMAT ruling~~ **RULED (a): the format gains the field — `SCHEMA_VERSION = 3`,
      `addressee` on `Pov` and `AttitudeRow`, THE FIRST MIGRATION OF THE FROZEN SCHEMA.** The
      alternative asked the resolver to know that saying-verbs are special, a closed set of verbs in
      code · ~~the rotation~~ **DONE: «John said to Marie "You are a clever girl"» — the `you` is
      MARIE.** «John thinks I am wrong» still means the speaker, because thinking addresses nobody
      and EMPTY is what carries that. A conditional does not rotate.
      · ~~the quote as CONTENT~~ **DONE: «John said the sky is green» does not assert that the sky
      is green.** The quote goes under an attitude and its rows go EMPTY — `ccomp`'s own shape,
      across a sentence boundary — and the attitude scopes the outermost JOIN so «clever» is not
      left asserted outside the quotation. **UD's direct-quote case found a defect on arrival**:
      `that` is OPTIONAL and without it nothing raised the POV, so «I asked: "Do you know the muffin
      man?"» CLAIMED that you know him. **2b IS COMPLETE** — and the drill, which owed hand-compiled
      quotation, now has nine sentences of it
- [x] **⚑ THE ROTATION WAS INVERTED — found AND fixed 2026-09-17** *(record
      `202609170533_the-quotation-block.md`)*. «John said to Marie **that** you are late» is about
      the LISTENER and the station said Marie; «John said to Marie **"You are late"**» is about
      Marie and the station said the listener. **Both wrong, in opposite directions**: quotation
      preserves the original speaker's deictic centre, reporting does not, because the reporter has
      already moved the pronouns into his own frame. The rotation was keyed on the joiner's
      `asserts: matrix`, which lives on the word «that» — present exactly where rotating is wrong.
      **THE QM ASKED THE WRONG QUESTION AND THE CAPTAIN REFUSED IT**: *«I find it weak to care about
      what a quotation symbol is; spacy-stanza already has the tooling to isolate the quote, and the
      input is always English»*. Measured, and he was right — a quoted complement's SPAN is
      bracketed by `punct` and a reported one is not, so **the station never reads a character** and
      curly quotes work for free. *The rule's failure mode is not only hard-coding a set; it is
      NEEDING one.* Two more things the fix needed, both measured: the rotation must **NEST**
      (depth two named the narrator), and it must name the same somebody the ROWS do (`i.n` where
      the box held `me.n`). `q-4` `q-7` `q-9` resolved; `q-2`'s rotation is right and what is left
      of it is the subject-role question
- [x] **the truth slot under an attitude — RULED 2026-09-17: the rows KEEP their truth.** The
      station emptied it, the drill never has (`dere-1` carries a cat at truth 1.0 under «he thinks»
      and asserts no cat). The PREFIX keeps a row out of the world; the truth slot says what the
      HOLDER does with it — and blanking it flattened three speech acts: said-assertion (`q-8`,
      1.0) · said-question (`q-7`, an OPEN box) · said-command (`aw-21`, None). «John told me X»,
      «John asked me X» and «John told me to do X» are three different things to the brain
- [ ] **⚑ A POLAR QUESTION NEVER OPENS ITS TRUTH** *(found 2026-09-17, by fixing the slot above)*.
      «Is the cat hungry?» compiles at **truth 1.0**, where the schema's own docstring says it *«has
      every box bound and its truth OPEN»*. Wh-questions open a box and are fine; `whether` opens
      the truth from its marker row; the bare AUX-fronted polar has nothing that fires. **It was
      invisible while everything under an attitude was blanked anyway** — a mood question, not a
      truth-slot one. *Making a slot mean something is how you find out who was not filling it*
- [x] **embedded questions** *(2026-09-16)* — **a wh-word has THREE readings and R5's binary test
      conflated the last pair.** R5 asks «is this the root clause» and answers the MOOD question
      rightly; it was then read as «therefore relative», and an embedded question opens its slot
      exactly as a root one does. **UD marks the difference and nothing else does**: a relative
      clause modifies a NOUN (`acl:relcl`), an embedded question is a clausal COMPLEMENT
- [x] **UNASSERTION PROPAGATES into an enclosed clause** — a TRUTH error found by the above:
      «if you know WHO DID IT, tell me» claimed that somebody did it, because the `ccomp`'s AND
      asserted its operand while the other half of the same conditional was explicitly not claimed.
      The whole antecedent is supposed, and a clause inside it is inside the supposition
- [x] **a compiled form no longer ALSO abstains** — `if` sat in the abstention list of a sentence
      whose IMPLY it had built, because the per-clause walk meets a joiner before `_relate` runs.
      A report that cries wolf is worse than no report.
      **Ratchet 24/25 at 99.4% — a new high; gate 33 answered, 0 WRONG**
- [x] **the thirteen ambiguous markers** — closed classes v6 (`db/0012`). **Not the geometry
      `db/0008` predicted**: «is a pool a place?» is a hypernymy question and cosine does not answer
      taxonomy. It is **WordNet's supersense** — 26 noun + 15 verb classes, published and closed, so
      the table can be COMPLETE (the UD gate's argument, a second time). Benched on 52 cases:
      supersense **11/11** independent · geometry 6 with 3 wrong and 14 mute · first-candidate 7 with
      4. A `default` now fills its box and is COUNTED, never silent. **22 of 25 UD cases whole, mean
      98.4%**
- [ ] **`mark` under a reporting verb opens a POV**, not a join (E2 made attitude a prefix element)
- [ ] renderer (same lib)
- [ ] confidence scalar (coverage + repairs; round-trip escalation-only)
- [ ] drill automated = acceptance gate
- [ ] **⚑ THE FRAME/KNOWLEDGE AUDIT — E3's closing act** *(the Captain, 2026-09-16)*: walk every set
      this epic put in code and re-ask the FRAME test. Already suspect: `RELATION_FILLS_ROLE`
      (`nsubj → agent` is a declined judgement), `CLAUSE_DEPS` (`xcomp` deliberately absent — an
      argued exclusion is a ruling), `UD_DEP_TO_ROLE` (best-first is a claim about English),
      `UD_POS_TO_WORD_CLASS`, `CLAIMED = 1.0` (a threshold in code is what `db/0002` refuses)

## E3b — the name *(opened 2026-09-16 — the parked hole, reopened and widened)*
- [ ] **is it a name at all?** — stanza NER vs spaCy NER measured on the same text; `PROPN` and
      CASING as separate weak evidence. tk1's gate failed BOTH ways: it minted individuals from OOV
      gibberish spaCy labelled `GPE`, and refused «kotekino», lower case and known. *(Not a reopening
      of req 2: NER is not a UD task and has no UD relation.)*
- [ ] **a name of what? — OUR kinds, as ROWS not code** *(the Captain, 2026-09-16, req 17: «everything
      is KB — if we rely on a third party we lose the ability to modify it»)*: two tables, the KINDS
      (person · organization · place · work · event · none) and the LABEL MAP (NER label → kind), so a
      model's new label is a migration and not a release. tk1's nine mappings are the starting
      position. **Prominence is a scalar, not a kind** — it is what the net ranks
- [ ] **the places table, INHERITED** — measured 2026-09-16: **4,674,701** author-curated rows,
      `path_admin` + `path_geo` containment chains, a `type` column of **exactly 21** values that is
      an `is_a`, a second axis `category`, coordinates on 99.9%. Read LAZILY, never materialized
      (the cascade-noise ruling, applied there already)
- [ ] **the names list, INHERITED — and it cannot be a TEST** — `tokeniko.names`: 21,975 rows, one
      column. It holds `anna` and would fix the bench on the spot — but **28.1% of it is also a place
      name** (`paris` included) and 15.2% a WordNet common noun. Evidence, never a test: which is the
      measurement that forces the net
- [ ] **have I met it?** — recognition against a names table; tk1's preference order inherited whole,
      «genuinely ambiguous → never guess» included. The MECHANISM is E3b's, the ROWS are E9's
- [ ] **⚑ the MICRO-NN ABSTRACTION — brought forward from E5** *(the Captain, 2026-09-16: the epic
      stays in E5, the machinery comes here because it is propaedeutic to closing the name hole)*:
      the lib (features → ranking/scalar, weights as epoch-stamped rows, deterministic per epoch) and
      the instance registry, with the fence enforced STRUCTURALLY. Built to serve the next line and
      generalized against it, never before it
- [ ] **⚑ which one? — THE FIRST INSTANCE** — «Paris, France» or «Paris, Ontario»: tk1 logged it and
      never solved it. The first case to pass micro-nn req 9's two tests — curation cannot finish AND
      the answer moves over time. Ranks the curated tables' candidates, never mints one. **The 28.1%
      collision above is the brief**: strong signals that contradict each other
- [ ] **what a name is in a zip** — type centroid = SEMANTIC, uid = IDENTITY, never merged
- [ ] **the markers' third reading** — «went with Anna» goes comitative because Anna is a PERSON, with
      no rule about Anna anywhere. That is E3b's acceptance test, and the marker bench already holds it

## E4 — the evaluator
- [ ] verdict shape (pure; truth · status · bindings · derivation)
- [ ] form kernel (logic floor migrated)
- [ ] bind-and-ground (one search; dual read; ABSTAIN first-class)
- [ ] chaining migrated + generalized
- [ ] budget + micro-nn ordering hook
- [ ] stake resolution
- [ ] ⚑ PROOF SLICE 1: text → zip → verdict, end-to-end on sandbox

## E5 — the instinct middleware (parallel after E0)
*The MACHINERY moved to E3b (the Captain, 2026-09-16) — it is propaedeutic to the name hole, and a
framework that meets a real case before it is declared general is the one failure mode «one
abstraction, many instances» is most exposed to. The epic stays here; the two lines below are E3b's
and are listed with a pointer, never repeated.*
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
- [ ] no-regression ratchet green — the log is `tkzipdebug`: 529 clean journeys, **209 v1 read
      wrong** (read them with `tools/journey_ledger.html`)
- [ ] the migration night of sleep — observed

## E10 — the embodiment & the window
- [ ] interpreter runtime on the mini (process split; runbook)
- [ ] cutover (guard boundary moved; v1 kept runnable)
- [ ] window rewire (mock → live KPIs)
- [ ] observability (probes, bars, maps, heart dashboard)
