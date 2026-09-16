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
- [x] **⚑ the UD gate OPENS** — `tools/ud_gate.py`, offline by default: **19 answered · 0 wrong ·
      6 abstained** over 25 cases reaching 16 of the 37 relations (16/0/9 when it opened). It found
      five defects nobody would have read off the code, the newest being `of` under a noun compiling
      to a box instead of the possessor FIELD. *(The 21 unreached relations are printed every run.)*
- [ ] **the UD gate COMPLETED** — the remaining 21 relations, each with a transcribed case
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
- [ ] **embedded questions** — «if you know WHO did it»: neither a root-clause interrogative nor a
      relative, and R5 rightly says «not the root clause» without being enough to compile it
- [x] **the thirteen ambiguous markers** — closed classes v6 (`db/0012`). **Not the geometry
      `db/0008` predicted**: «is a pool a place?» is a hypernymy question and cosine does not answer
      taxonomy. It is **WordNet's supersense** — 26 noun + 15 verb classes, published and closed, so
      the table can be COMPLETE (the UD gate's argument, a second time). Benched on 52 cases:
      supersense **11/11** independent · geometry 6 with 3 wrong and 14 mute · first-candidate 7 with
      4. A `default` now fills its box and is COUNTED, never silent. **22 of 25 UD cases whole, mean
      98.4%**
- [ ] **`amod`** — «Last night» leaves `Last` unplaced: an adjectival modifier is not compiled yet
- [ ] **`mark` under a reporting verb opens a POV**, not a join (E2 made attitude a prefix element)
- [ ] renderer (same lib)
- [ ] confidence scalar (coverage + repairs; round-trip escalation-only)
- [ ] drill automated = acceptance gate

## E3b — the name *(opened 2026-09-16 — the parked hole, reopened and widened)*
- [ ] **is it a name at all?** — stanza NER vs spaCy NER measured on the same text; `PROPN` and
      CASING as separate weak evidence. tk1's gate failed BOTH ways: it minted individuals from OOV
      gibberish spaCy labelled `GPE`, and refused «kotekino», lower case and known. *(Not a reopening
      of req 2: NER is not a UD task and has no UD relation.)*
- [ ] **a name of what?** — the kinds as a closed set: person · public figure · organization · place ·
      work · event · none; tk1's nine NER→type-centroid senses as the starting position
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
- [ ] **⚑ which one? — THE FIRST MICRO-NN** — «Paris, France» or «Paris, Ontario»: tk1 logged it and
      never solved it. The first case to pass micro-nn req 9's two tests — curation cannot finish AND
      the answer moves over time. Ranks the curated table's candidates, never mints one
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
- [ ] the lib (features → ranking/scalar; weights as epoch-stamped rows)
- [ ] instance registry + structural fence
- [ ] first instances: station calibration · evaluator ordering

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
