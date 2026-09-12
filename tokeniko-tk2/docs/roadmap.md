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
- [x] closure engine (keys as law, ring boundary visible, policy fingerprinted) — `34e43c8`
- [x] inflection-collision fix (req 21) + stop list yields to membership — `fe73d40`
- [x] proper-noun/abbreviation refusal (`or`=Oregon out of the base) — `1e7cad3`
- [x] policy as rows — the mechanism (collection, bar ledger, manifest, offline snapshot) — `e480ccd`
- [x] policy as rows — the ruling: k=200, rail 25,000, closed classes as typed KB rows — `a6acefb`
- [x] R at scale + curation pipeline (Captain's hand on approve) — `f71baa3`
- [x] lemma scope ruled (v4) + inferred opposition ruled (v5) — `7da676f`
- [x] D at scale + the dual read ruled (min_shared 1 · derivational 0.45 · mix 0.5) — `b8f325e`
- [x] the bar grown 18 → 37 as rows; the closed-class filter and the mix re-ruled against it — `e1dbdd2`
- [x] the seal, the verifier, the map — a base can say "I am complete" — `a4b13f1`
- [x] acceptance floors ruled: NEAR ≥ +0.27 · FAR < 0 · ABSTAIN between — `0678054`
- [x] **THE BASE IS BUILT AND SEALED ON THE BODY** (4,555 dims · R 51,564 · D 473,262 ·
      `9824ef46…`, applied by the Captain 2026-09-10, read back whole)

*Scope note: E1 built the BASE (4,555 POS-split keys), not the sense layer. The resource's 68,779
words / 120,475 senses ride ON it and are **not built** — an open dictionary task with no epic yet
(`plan.md` § E1, «what E1 did not build»).*

## E1b — the names ✅ 2026-09-10 — see `landed.md`
- [x] every collection prefixed by the component that owns it (`dictionary_base_*`, `heart_*`,
      `language_`, `senses_`, `tkzip_`, `body_params`)
- [x] `tokeniko_tk2_body` → **`tokeniko_tk2`**; the 983-dim prototype that held the name, dropped
- [x] thirteen migrations → one baseline; all nine policy versions carried with their notes verbatim
- [x] rebuilt and proved: `9824ef46…` reproduces, every collection identical row by row

## E1c — the sense layer ✅ 2026-09-10 — see `landed.md`
- [x] the sense vector ruled: BOTH floors — gloss over base dims, and the synset's own relations
- [x] sense selection ruled: `senses="primary"` stands — the base is the frame, the senses the content
- [x] **120,475 senses placed (96.9%), 816,309 cells, sealed and read back whole**
- [x] the manifest names its own build (a T5 finding that became real when two builds shared a policy)

## E2 — the format (tkzip v2)
- [x] **role inventory CLOSED** — 17 boxes + the predicate, cut from VerbNet (29 roles) ·
      PropBank (112,917 annotated sentences) · FrameNet (1,221 frames), cross-checked against the
      Captain's own first draft; noun-phrase record = 5 fields; OQ2/3/4/5/13 answered, OQ7 part
- [x] **named rows & scope DONE** — flat list + Tseitin; row order = scope with a FIVE-element
      prefix (quantifier · negation · modality · attitude · domain); CAUSE/RESULT/PURPOSE all
      dissolve into IMPLY + the theatre; the operator set is the TEN truth functions, frame;
      OQ6/OQ8 answered, req 6 satisfied with no new machinery
- [x] **binding states & moods DONE** — **mood is not a field**: question = something OPEN,
      imperative = POV(want), supposition = POV(suppose), forecast = a future theatre; irony goes
      to the figurative layer. Net addition: binding state (BOUND · OPEN · EMPTY) on any slot,
      a prior on open slots, and the record's sixth field (`sense`)
- [x] **confidence + provenance DONE** — net addition is ONE field (`parse_confidence`, one
      scalar per zip, may be EMPTY); provenance / `derived_by` / `original` / forecast resolution
      are all document-level and already built at E0. Two findings handed to data-modeling and
      datatier (their req 7 each)
- [x] **storage DONE (OQ9)** — sparse (measured: ~80% of every row is EMPTY); the KEY is the
      truth and the VECTOR an epoch-stamped cache, so a dictionary rebuild never touches the
      biography; ~60× smaller than v1 per sentence; seventh record field `marker` added
- [ ] ⚑ fifty-sentence drill BY HAND — bar set in advance, schema frozen v2.0

## E3 — the station (parser/compiler)
- [ ] skeleton adapter (stanza, swappable)
- [ ] compile core (anchors migrated; senses open; context argument; partial zips)
- [ ] renderer (same lib)
- [ ] confidence scalar (coverage + repairs; round-trip escalation-only)
- [ ] drill automated = acceptance gate

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
- [ ] no-regression ratchet green
- [ ] the migration night of sleep — observed

## E10 — the embodiment & the window
- [ ] interpreter runtime on the mini (process split; runbook)
- [ ] cutover (guard boundary moved; v1 kept runnable)
- [ ] window rewire (mock → live KPIs)
- [ ] observability (probes, bars, maps, heart dashboard)
