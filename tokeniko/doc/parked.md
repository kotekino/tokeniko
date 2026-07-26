# tokeniko — parked (the icebox)

> Deliberately deferred — good ideas and known gaps that are **not** the current focus. Moved out of
> `roadmap.md` so the road ahead stays clean. Promote an item back to `roadmap.md` Next when its time
> comes. The active road is `roadmap.md`; history is `landed.md`.

---

*(Conversation momentum — PROMOTED and LANDED 2026-07-24 with the pronoun-momentum build: the
missing lift was felt as the bare-«you» pronoun defect; the landed design subsumes this entry —
ambient lifts to 0.85 inside an open exchange, derived from the timeseries as agreed here. See
`landed.md`.)*

**ATProto / Bluesky — a `senses` I/O channel (inbound carrier AND outbound)** — the account exists
(**@tokeniko.online**; app password to come) so wiring is quick later. Its original condition
(Discord + blog live) was met 2026-07-12, but the author RE-parked it at the 2026-07-14
reconciliation: "before ADDING another sense (with huge consequences, I'm sure of it) let's make
the brain stronger" — promote only after the roadmap's strengthening tail. Today: no send adapter;
`score_feasibility` already marks atproto-outward infeasible.

**Wondering-net structural polish (definitions-as-rules, step-4 residual)** — the ingestion extractor
gate is already conservative (main-clause genus only + redundancy/placeholder/cycle/reliable-tier
disjointness), so these were deferred: reject **circular nominalization** genera ("management→manage"),
and **flag-the-middle** (surface borderline extracted edges for review rather than silently accept).
Promote only if the enriched soak shows them biting.

**Sufficiency v1 residuals (Brain v1.1 step 4)** — conservative firsts, promote if the enriched soak
shows them worth it: (1) **derived properties as cond satisfiers** — sufficient rules currently match
the seed's stored property FACTS only; letting chainer-derived properties satisfy definiens conjuncts
(recognition over inferred traits) needs the fixpoint interleaved with property derivation. (2)
**adjective-definienda sufficiency** ("has merit → valuable" — the finding-#3 flagship) has NO fuel:
all glosses were "a/an X is …" noun-templated, so adjective definienda compile as noun-STRUCTURED
zips (the step-5.1 pin now labels their subjects with the true `.s.`/`.a.` sense, but the clause
shape stays noun-copular); needs per-POS gloss re-templating first. (3) **class-seed recognition** — sufficient rules fire only
on individuals (property facts are uid-keyed); a class satisfying a definiens via its own differentia
rules is a further unification.

**Differentia-rule VERB recovery (definitions-as-rules, step-5 residual)** — the strict differentia
gate (step 5.1) keeps only reliably-clean rules zip-only: adjective differentia ("all apples sweet") +
transitive verbs WITH a direct object ("all bathrooms contain a bathtub"). It conservatively DROPS the
verbs it can't disambiguate from the zip alone — **passive-voice reduced relatives** ("an airfield
**equipped** with…" → the class is the patient, not "airport equips") and **intransitive agentive
verbs** ("trained **to compete**"). Separating these needs **parser-level voice/agency detection** (the
reduced-participle vs finite-relative-with-nsubj distinction), adjacent to the parked D3a
subject-rebinding work. Would recover the verb bulk (~300 candidates) as clean differentia rules and
substantially grow the enriched-soak fuel. Promote when the parser voice signal is built.

**Performance (optimize-later)** — the fingerprint KB cache (`_kb_cache`) landed, but every
materialized theorem changes the fingerprint → the next tick still pays a FULL reload (3233
definition zips, tens of seconds) — an incremental/delta reload would cut soak tick cost ~10x.
Dual `en_core_web_lg` load (`parser.nlp` + `c_state.nlp`) → consolidate. *(TKZip binary
compaction was promoted OUT of here 2026-07-14 — roadmap strengthening-tail #1, author's call.)*

**WSD (deeper refinements)** — contextual WSD for ambiguous heads; co-predication hint (prefer
attribute-sharing adjective senses); graded attribute-contrariety (no crisp `antonym` edge).
*(The robin xfail formerly noted here HEALED 2026-07-14 — the Lesk self-mention fix; promoted to
a permanent regression test. The core selection fixes are in `landed.md`.)*

**Parser / Stanza** — concessive + resultative clause types (`although`→OTHER, `so`→AND today); D3a
relative-clause matrix subject (Stanza mis-root); `imply`→IMPLY parataxis robustness; clausal-subject
support ("to err is human"); negative-quantifier subject rewrite ("nobody").
- *(Property-restricted universal rules / cogito fork ii — un-parked and since **LANDED** with
  Brain v1.1 (the property-conditioned rule extractor in `kb_extract` — see `landed.md`).)*

**Evaluator** — geometric negation-awareness in `compareContent`; quantifier effect on the *geometric*
grounding; axiom/theorem `≡1` tautology creation guard; intrinsic comparison grounding (eq/noteq);
trust-weighted grounding + conflict arbitration; defeasibility of biological universals (crisp `all`
over-asserts — penguins don't fly).

**Cleanup / misc** — 1b **verbs** (the "means"-frame drags a spurious predicate); legacy `axioms` /
`names` collection cleanup; `@-1,0,0` spacetime artifact; t-norm / implication choice (Gödel vs
Łukasiewicz vs product — the one semi-arbitrary constant); coreference (pronoun → individual).

**Dev tooling** — `probe_brain.py` (live brain-loop integration probe: injects a multi-author batch
via `/input`, asserts the loop invariants) currently lives in the scratch dir — candidate to formalize
into `scripts/` or `tests/`.

**Dreaming (a hunch — future, biological-creature framing)** — a new brain **phase**: access RANDOM
memories and *distort / mix / shuffle* them (a blender over the memory log) into a new **`dreams`**
collection that mirrors the `memory` modeling (also a timeseries). During the dream phase **`senses`
is paused and the other brain loops are paused — only the dream loop runs**. Use is TBD (a hunch —
likely creativity / consolidation / novel-association later). Revisit after the logical brain (D) is
whole. See `VISION.md`.

**Plural-genus collection/member gate (enriched-soak specimen, 2026-07-09)** — "a forest is the
TREES and other plants in a large densely wooded area" minted tier edge `forest.n.01 is_a tree.n.01`
→ «a forest has trunk» @0.3. A PLURAL genus head ("the trees") defines a collection by its members —
that is collection-of/member-of, never is_a. Gate improvement for `extract_isa_edges`: reject (or
re-type) a plural-headed genus. Companion specimen: differentia OBJECT mis-sense («a sector
illustrates fabric» — "textual material" got the textile sense); the object-side WSD shares the
general differentia-WSD residual above.

**Symmetric disjointness (the mirror direction, 2026-07-11 follow-on)** — a negative copular
universal is consumed ONE-directionally (as a negated membership rule): «no mammal is a reptile»
refutes «a dog is a reptile» (subject-side closure walk) but NOT «an iguana is a mammal» — the
mirror claim needs the mirror axiom taught. True symmetric consumption = mine these into
pairwise-disjoint assertions feeding `relations_disjoint` (the refutation side of the graph reader,
symmetric to how affirmative copulars feed subsumption) instead of a rule. Promote when the
teaching workflow makes the double-teach feel like friction. *(Supersedes the step-2
`negated_skip` residual — the rule-side consumption landed 2026-07-11.)*

**The reciprocal thanks (survey slice 4 fork B, 2026-07-19)** — tokeniko THANKING a teacher after
a lesson (one rule on the `eval:learned` seam, beside the curiosity ask). Parked with the author:
the curiosity «why» is already his one reaction to a lesson — two reactions per lesson is chatter.
Promote if the etiquette family's live behavior makes his teachers feel unthanked.

**The `e_facts` repositioning question (2026-07-23, the fact-match build's finding)** — the direct
fact-match primitive is currently SHADOWED for the known specimens: the forward-chainer (class
subjects, via generic-rule re-expression) and `evaluator_groundIndividualFact` (individual
subjects) decide first, now honestly priced by min-premise trust (an exact-restatement chain
prices at the 0.7 generic-rule floor, not the theorem's 0.9 — conservative, never wrong-verdict).
The parked fork: reposition `e_facts` as the AUTHORITATIVE pricer ahead of the self-grounding
chainer — an exact restatement is a lookup, not a derivation, so arguably worth the fact's full
trust (0.9). Promote if live behavior makes the conservative pricing feel dishonest (answers
about well-trusted beliefs sounding oddly unsure).

**The ears' semantic floor — small invention-within-balloon (2026-07-24, the strong-verifier build's finding)** — the additive sound-only semantic centroid is weak when a small fluent invention rides beside true content: «a cat is a mammal → …and pigs fly» measures ~0.97 (+1 leaf) / ~0.86 (+2), because the shared content dominates the sum, so the floor does not catch it — that class stays guarded by the existing +2 balloon cap and the structural key-match, NOT the geometry. An honest limit, not a regression. The cut if it ever bites live: a PER-ADDED-LEAF semantic check (each ballooned leaf must itself be close to some original leaf), rather than the whole-zip centroid. Promote only if a real live polish sneaks a small invention past the cap.

**The sentence tag-vector — a per-zip aboutness centroid (2026-07-25, the author's brainstorm)** — a 2925-dim centroid computed AT INGESTION over a zip (and over each KB doc: axioms/definitions/theorems), stored + Mongo-indexed for native `$vectorSearch`. NOT meaning and NOT a duplication of the zip: it is the zip's CLASSIFICATION — an *aboutness TAG* (the author's framing), a first-class derived artifact used only as such (possibly wrong, never authoritative). By construction it discards all logical structure — operators, negation, quantifier, role-order, spacetime — so "a cat is a mammal" and "a mammal is a cat" tag alike, and antonyms (love/hate ≈ 0.86 in this dictionary) don't separate: FENCED to retrieval / association / recall, NEVER grounding or truth (geometry doesn't vote on is_a, nor here). **Consumers it folds:** the anecdote's "by the way, this reminds me…" (today an in-memory centroid scan — this is literally the promotion of its own parked "`$vectorSearch` becomes right when the KB grows" note), semantic recall/search over memory + KB, clustering, a public "what this belief is about" surface. **Reuse map (unify, don't reinvent):** `e_label.evaluator_assignWord` already does centroid→nearest-dictionary-word via `$vectorSearch` (the tag EXTRACTOR — top-N nouns from the centroid); `context.topic_centroid` + the anecdote's per-doc cached centroids; `_semantic_centroid` (normalizer, sound-only); the `vector_index` already exists for senses. **The weighting is the whole game (its own design session):** role weights à la `e_label` (noun-heavy; subject+predicate over indirects), drop operators/negation/quantifier (aboutness, not meaning), how much the predicate verb counts; a bad formula makes every stored tag subtly useless and expensive to recompute KB-wide. **Discipline:** version the formula + recompute on change (the `recompile.py` precedent), the zip stays the source of truth. **Promote when** a concrete consumer needs it OR the KB outgrows the in-memory centroid scan (the laptop-ceiling trigger) — design now, build on first real need.

**LEARNING a voice in the speaker's own language (2026-07-26 — the author's idea; its CURATED half LANDED the same day, see `landed.md`)** — the machinery (`MEMScaffold.lang`, the per-language shelf gate, the fallback chain, the carrier no-op) and 232 curated it/es/fr/de rows are BUILT. What stays parked is the LEARNING half: the convergence with the accommodation (2026-07-24) — tokeniko picking up native phrasings directly from what a person actually says in their own tongue, so his Italian register becomes THEIRS rather than our curation. **The blocking coupling, confirmed from both sides**: `brain/mimicry.py` mints `template = item.original` VERBATIM, and on a translated turn `original` is the SOURCE language while the matched zip is English — so a mint would drop an unlabelled Italian row into the English shelf. The step-2 FENCE (a translated turn mints nothing) holds that shut today. **The honest minimum when the fence is lifted**: stamp the row's language from the item's `source_lang` (the officer's finding — without it, `mimic_observe` seeds unlabelled foreign strings at the `lang="english"` default), and let the existing shelf gate do the rest — it already filters by language and the carrier already skips a native row. **The fuller prize**: per-language mimic shelves consolidated in sleep like any other, so his Italian voice GROWS from Italian conversation instead of being written for him. Promote when the curated voice has lived a while.
