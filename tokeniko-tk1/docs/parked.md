# tokeniko — parked (the icebox)

> Deliberately deferred — good ideas and known gaps that are **not** the current focus. Moved out of
> `roadmap.md` so the road ahead stays clean. Promote an item back to `roadmap.md` Next when its time
> comes. The active road is `roadmap.md`; history is `landed.md`.
>
> **`→ tk2` tags (2026-08-03).** An item tagged `→ tk2` is parked for a *structural* reason, not a
> scheduling one: the layer it touches is marked **rebuild** in the inheritance ledger
> (`../tokeniko-tk2/docs/README.md` §5), so building it in v1 means building it twice. These do **not** get
> promoted back here when "their time comes" — their time comes inside the blueprint. The status
> lives in this file; the design reasoning lives in **`../tokeniko-tk2/docs/carried-in.md`** (reference, exempt
> from the status invariants — a pointer, never a copy).

---

## → tk2 — carried into the blueprint (moved off `roadmap.md` 2026-08-03)

### The second wave — moved 2026-08-12 by the sharpened filter

*The author's blade: **what makes v1 better and bug-free is welcome; NEW FEATURES go to tk2.** A
repair keeps the empirical instrument fit; a new capability built in v1 is built twice. This emptied
`roadmap.md` §4 to a single item. Per-item reasoning: `../tokeniko-tk2/docs/carried-in.md`.*

**Vocabulary growth** (hunches 1+2) `→ tk2` — OOV → a staging dictionary entry · the typo-ALIAS table
· definitional triangulation (a trusted definition's zip matched against known ones → a graded link
at the definition's trust, never a hard `=`). The DICTIONARY it grows is `inherit untouched`, so
every row would cross the bridge — but the *machinery that mints rows* is new capability, and tk2
should own how its vocabulary expands from the start.

**Ingestion-time differentia** `→ tk2` — differentia extraction wired at definition INGESTION. The
extractor exists and stays; making ingestion enrich automatically is a new capability, and it changes
WHEN the KB grows, which is a blueprint decision.

**KB growing OUTWARD — tier-1 synthetic learning** `→ tk2` — learned axioms vs derived theorems, the
analytic/synthetic cut. Design + open forks: `doc/ref/kb-growing-outward.md`. **The largest item that
was ever on the road**, and an entire new learning mode: exactly what should be designed against
tk2's format rather than retrofitted onto v1's.

**Etiquette — the PROTOCOL half** (hunch 8) `→ tk2` — repair initiation («what?», «huh?» — the
inbound mirror of his own did-you-mean, which he has no channel for) and farewell / channel-close
(«bye»; the exchange window closes only by TIMEOUT today). *Its 2026-08-03 argument for staying was
that the mention-vocative bug proved protocol is structural — but that BUG is fixed (2026-08-11), and
what remains is two new behaviours.* The DISPATCH half and all of REGISTER were already here; the
whole of etiquette now sits in one place.

**Trust-ledger-movement digests** `→ tk2` — «my opinion of X shifted twice today» batching like the
rest. A new digest kind.

**Trust-ledger consumers** `→ tk2` — the trust-gated tkzip lane (format-coupled, was always destined
here) · attitude-report unwrapping (events / facts-as-axioms) · tier-1 teaching by an EARNED-trust
stranger (Hellen is 4 kickers from the bar). All new capability on top of a ledger that works.

**Contrast as default-expectation fuel** `→ tk2` — wondering reads a contrast-flagged «X but Y» as a
hint at a background generic «X normally ¬Y», then corroborates or asks. **The flag is live and
stays; only the CONSUMER moves** — v1 keeps producing the evidence tk2 will read.

**«I picked up a way of speaking from X»** `→ tk2` — a transmission voice for a consolidated learned
scaffold. The scaffold rows are `inherit`; the voice that announces them is new.

**Blog `life:learned` / `life:discussion` triggers** `→ tk2` — new outbound triggers on a channel
that already works.

**The possessive-relation carrier** `→ tk2` — «kotekino is MY creator», the creator-of-ME bond. A new
relation carrier, split out of the complement-family follow-on (whose other half — verify xcomp→THAT
— is a check and stays on the road).


**TKZip binary compaction + the zip-native renderer** `→ tk2` — the zip becomes an actual packed
vector; the JSON is the human projection. **The author's own worked example of the filter**: the
format changes substantially in tk2, so this is optimization of a thing being replaced — partial
reuse at best, significant overhead certainly. **Its dependent, per-conjunct KNOWLEDGE** (the
AND-split's deferred half, 2026-07-24) travels with it: the teach path mints from `item.original`
(the WHOLE sentence), so a conjunct cannot be learned alone until a renderer can produce that
conjunct's own surface text. Splitting speech is safe; splitting knowledge on a guessed string is
not. *(Note for the blueprint: tk2 answers this differently — open question 9, "fixed arity is a
property of the schema, not of the storage".)*

**Restricted-universal residuals** (Brain v1.1 2c) `→ tk2` — relative-clause restriction ("all
machines THAT THINK are minds") + object-side modifiers ("an ARTIFICIAL body"); the basket's trailer
(indirect roles + markers as chainer fuel) travels with it. **This IS the binder problem** —
blueprint open question 6. A restricted universal needs a variable bound across atoms with a
quantifier scoping over both; v1 can only approximate it with hardwired special cases, and tk2
dissolves it structurally.

**Conditional reasoning / premise-in-question (R4b)** `→ tk2` — "given P, is Q?": the
co-submitted-premise discriminator then hypothetical premise USE. The *logic* transfers; the
evaluator implementation does not (evaluator grounding is `rebuild`). Recorded as a **capability
requirement** for the blueprint's capability inventory (hunch 21 step 4) rather than as v1 work.

**Questions follow-ups** `→ tk2` — imperatives (the `imperative` scalar: a mood field on the zip =
format), wh when/how solving (evaluator), multi-clause/embedded questions («Do you know why…» =
format + evaluator). **And "real self-knowledge for how do you feel?" is hunch 20** — situational
awareness — which is already investigation order #3 in the blueprint. The whole entry sits in
rebuilt layers.

**Etiquette — the DISPATCH half, and ALL of REGISTER** (hunch 8) `→ tk2` — (a) the thinking-reaction →
idea → reflex chain that makes «hello John» stop being evaluated as an assertion: **limit A in
miniature**, since hardwiring which reaction follows which trigger is exactly what tk2 turns into
revisable KB. And (b) **register** — warmth, formality, whether he thanks at all — which the author
ruled out of tk1 for a second, independent reason: *register is shaped by the HEART* (hunch 14), so
building it before the heart exists builds something unreusable, and the heart must come first for
obvious reasons. In tk2 both halves converge on behaviour rules anyway. *(The PROTOCOL half — where
getting it wrong CORRUPTS rather than merely offends — stayed on the road: `roadmap.md` tail #5.)*

**D-phase realtime enhancements** `→ tk2` — cross-speaker patterns, inference-implied conflicts, the
full working-memory consumer set on top of the landed context ring (`brain/context.py`). State-layer
work, and the state layer is what limit A is actually waiting on (blueprint §6.3, hunch 20).
*(Ingestion-time differentia was split out and stayed on the road: `roadmap.md` tail #3.)*

**The third memory tier — EVENT vs general knowledge** `→ tk2` — episodic event vs timeless theorem,
the missing middle tier (author-ruled 2026-07-21, all design reasoning deferred until approached).
**A data-model question**, therefore a blueprint question: deciding it inside v1's format would be
deciding it twice. It also converges with hunch 20's event-magnitude work (an event is a delta in
the SA matrix; a fact is a payload), which is where it should be designed. Holding ruling unchanged:
moment-anchored claims stay events — remembered, not believed. Candidate anchors + the live specimen
→ `doc/ref/notes.md`.

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

**Vocative stripping is split across two discriminators (parked 2026-08-11, the author's ruling).**
`lib/core/deixis.py::strip_vocative` cleans a leading vocative off the stored `original` at
materialization (5 call sites in `brain/thinking.py`) and its discriminator is the COMMA — by
deliberate, evidence-based design. The §2 fix taught the PARSER a better one: the part-of-speech of
the token after his name (AUX/finite-verb ⇒ he is the subject, hands off; determiner ⇒ the vocative
is stealing the subject). So the compile is now repaired for plain-text address while `original`
still carries the wart — and `original` is what feeds theorem dedup keys and the blog polish. Two
discriminators for one question, the weaker one on the user-visible path. Unifying them is a design
question, not a patch; promote when the dedup key or a published digest actually shows the wart.

**Performance (optimize-later)** — *(the theorem-invalidates-the-vocabulary half is DONE, 2026-08-09:
the two-tier fingerprint — see `landed.md` §0 addendum. What stays parked is the residue.)* A true
**delta reload of the definitions themselves** — when the vocabulary really does grow, the whole
1.2 GB is still re-read — and **trimming the load to what the evaluator actually reads**, paired with
watermark-gating `kb_wonder`'s re-saturation (the noted future optimization in `thinking.py`). Both
are now genuinely optimize-later: definitions change rarely, so the pressure that made this urgent is
gone. Dual `en_core_web_lg` load (`parser.nlp` + `c_state.nlp`) → consolidate. *(TKZip binary
compaction left here for the roadmap 2026-07-14 and RETURNED 2026-08-03 under the tk2 filter — it now
lives in the `→ tk2` section at the top of this file.)*

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
over-asserts — penguins don't fly). *(2026-08-03: the **geometry-coupled** half of this list is
effectively `→ tk2` — `evaluator comparison/grounding` is `rebuild` in the ledger, so refining how
today's role tensors compare is refining a thing being replaced. The **logic-level** items —
tautology guard, trust-weighted arbitration, defeasible universals — are engine questions that
survive any format and stay honestly parked here.)*

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

**The sentence tag-vector — a per-zip aboutness centroid (2026-07-25, the author's brainstorm)** `→ tk2 (design)` *(2026-08-03: the weighting formula reads OFF the zip's roles, so it must be designed against tk2's fixed-arity schema — where it gets easier, not harder: uniform slots make a role-weighted centroid a matrix operation rather than a traversal. Design it in the blueprint; the consumers listed below are unaffected.)* — a 2925-dim centroid computed AT INGESTION over a zip (and over each KB doc: axioms/definitions/theorems), stored + Mongo-indexed for native `$vectorSearch`. NOT meaning and NOT a duplication of the zip: it is the zip's CLASSIFICATION — an *aboutness TAG* (the author's framing), a first-class derived artifact used only as such (possibly wrong, never authoritative). By construction it discards all logical structure — operators, negation, quantifier, role-order, spacetime — so "a cat is a mammal" and "a mammal is a cat" tag alike, and antonyms (love/hate ≈ 0.86 in this dictionary) don't separate: FENCED to retrieval / association / recall, NEVER grounding or truth (geometry doesn't vote on is_a, nor here). **Consumers it folds:** the anecdote's "by the way, this reminds me…" (today an in-memory centroid scan — this is literally the promotion of its own parked "`$vectorSearch` becomes right when the KB grows" note), semantic recall/search over memory + KB, clustering, a public "what this belief is about" surface. **Reuse map (unify, don't reinvent):** `e_label.evaluator_assignWord` already does centroid→nearest-dictionary-word via `$vectorSearch` (the tag EXTRACTOR — top-N nouns from the centroid); `context.topic_centroid` + the anecdote's per-doc cached centroids; `_semantic_centroid` (normalizer, sound-only); the `vector_index` already exists for senses. **The weighting is the whole game (its own design session):** role weights à la `e_label` (noun-heavy; subject+predicate over indirects), drop operators/negation/quantifier (aboutness, not meaning), how much the predicate verb counts; a bad formula makes every stored tag subtly useless and expensive to recompute KB-wide. **Discipline:** version the formula + recompute on change (the `recompile.py` precedent), the zip stays the source of truth. **Promote when** a concrete consumer needs it OR the KB outgrows the in-memory centroid scan (the laptop-ceiling trigger) — design now, build on first real need.

**LEARNING a voice in the speaker's own language (2026-07-26 — the author's idea; its CURATED half LANDED the same day, see `landed.md`)** — the machinery (`MEMScaffold.lang`, the per-language shelf gate, the fallback chain, the carrier no-op) and 232 curated it/es/fr/de rows are BUILT. What stays parked is the LEARNING half: the convergence with the accommodation (2026-07-24) — tokeniko picking up native phrasings directly from what a person actually says in their own tongue, so his Italian register becomes THEIRS rather than our curation. **The blocking coupling, confirmed from both sides**: `brain/mimicry.py` mints `template = item.original` VERBATIM, and on a translated turn `original` is the SOURCE language while the matched zip is English — so a mint would drop an unlabelled Italian row into the English shelf. The step-2 FENCE (a translated turn mints nothing) holds that shut today. **The honest minimum when the fence is lifted**: stamp the row's language from the item's `source_lang` (the officer's finding — without it, `mimic_observe` seeds unlabelled foreign strings at the `lang="english"` default), and let the existing shelf gate do the rest — it already filters by language and the carrier already skips a native row. **The fuller prize**: per-language mimic shelves consolidated in sleep like any other, so his Italian voice GROWS from Italian conversation instead of being written for him. Promote when the curated voice has lived a while.

**The mention-vocative refinement — a POS-aware comma (2026-08-03, the fix's own residual)** — the
landed fix inserts a comma after a leading mention of tokeniko unconditionally, which restores the
vocative reading («@tokeniko the cat is a mammal») and **breaks the SUBJECT reading** («@tokeniko is
a machine that thinks» → `(be [a] machine) AND (machine think)`, subject lost). The trade was taken
DELIBERATELY and ruled by the author: a mention *pings*, and people ping when addressing rather than
when discussing, so the vocative population is far larger — and the two failures are not equally
bad. The old one was a **confident false claim about himself, silently stored**; the new one is a
**subjectless clause that grades honestly as unknown**. Trading silent corruption for honest
confusion is the right direction. **The refinement**: insert the comma only when the body opens with
a NOUN PHRASE, not with a finite verb — which fixes both readings. It is parked rather than built
because it needs a POS check, and the adapter is **deliberately dumb about language** (it owns the
wire, not the grammar); doing it there would break that contract. Promote when the subject-mention
reading is seen failing live, and home it at a layer that already has the parser.

**The `talker` default mints an ungated placeholder speaker (2026-08-03, the officer's finding)** —
`api/main.py` `GET /api/v1/input` declares `talker: str = "unknown"`, so a hand-made call with no
talker files its words under a placeholder stakeholder (`uid: "unknown"`, channel `api`) that no one
consented for. Live count is 2 items of 743 — both the author's own probes — so **the shape is the
finding, not the count**: a default parameter is a route for words to enter ungated. The honest fix
is to make `talker` REQUIRED (or mint a per-caller uid); both are one-line changes with a blast
radius on every manual probe, which is why it is parked rather than slipped into an unrelated build.
*(The microscope now treats such items as UNJUDGEABLE rather than denied-pending-consent — a
placeholder is not someone who can be asked. See `landed.md`.)*

**rag1/rag4 rejection rows hide their items from the microscope (2026-08-03, pre-existing)** —
`_log_ears_rejection` / `_log_translation_rejection` write `TKZipDebugDoc` rows keyed by `item_id`,
and the microscope's dedup counts ANY row for an item as already-judged. So an item that had an ears
or translation rejection is **never examined by rag3**. Possibly intended (a rejected reading is
arguably not a specimen of the compile path) — but if it is not, the microscope is blind to exactly
the items most likely to be interesting, which is the opposite of the instrument's purpose. Decide
the intent before changing anything; the cure is a discriminated row type, not a dedup tweak.

**Etiquette protocol — the three parked candidates (2026-08-03, scoped with the author)** — the
protocol half of hunch 8 was scoped to TWO items (repair initiation + farewell → `roadmap.md` tail
#5). Parked with the author, in the order I would promote them:
- **«I wasn't talking to you» — the directedness correction.** Real in a multi-person channel where
  he listens to everything: a human currently has no way to say *you misread the address*. One
  utterance, direct effect on the directedness ladder he already has.
- **Acknowledgment — «ok», «I see», «got it».** The most frequent utterances in human conversation and
  entirely CONTENTLESS: they must not compile as assertions, and an ack after his answer is a
  RECEIPT — evidence the answer landed, a stronger signal than today's silence=consent.
- **The unprompted greeting — he never speaks first.** Every channel he is in is opened by a human,
  but the consent click is now a JOIN EVENT (2026-08-03), and a person who has just entered is
  exactly whom a host would greet. Protocol in the purest sense — opening a channel rather than
  answering in one — and his first genuinely unprompted social act, which makes it a small step
  toward the volitional layer. The greeting scaffolds already exist in five languages.
