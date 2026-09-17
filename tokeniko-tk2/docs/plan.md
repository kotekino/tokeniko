# tokeniko 2 — THE EXECUTION PLAN

*Phases 2+3 of «the road to the build» (README §9), fused deliberately: the epics with their
dependencies AND their task breakdown, in one document. Written 2026-08-23, the day phase 1 closed at
sixteen of sixteen. This file is the context-keeper across sessions — verbose where precision pays.
The concise, checkable mirror is `roadmap.md`; what finishes moves to `landed.md` (same status
invariants as tk1's trio: one item, one status, one doc; reconcile at every commit).*

> ### ⚠ THE ROADMAP IS THE OVERARCHING PLAN ONLY
> **The reasoning that decides anything lives in `docs/<chapter>/`** — `requirements.md`, the dated
> `_notes.md` beside it, and any `origin-*.md`. That is the **decision record**, not background:
> a great deal of argument between the Captain and the QM is there and nowhere else, including
> positions tried and refuted. **Read the chapter, in full, before elaborating any point in it.**
> *(The Captain's ruling, 2026-09-11 — see `CLAUDE.md` for what produced it.)*

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

**A THIRD LAW, ruled 2026-09-10 — a name is written for the human who reads it cold.** Readability
for an LLM and readability for a person are not the same thing, and only one of them is scarce: a
model reconstructs `base_r` from context in an instant, a person coming back in six months does not.
So names are **explicit and a little verbose**, and the cost is paid in typing rather than in
recall.

- **Collections carry the component that owns them as a prefix**, taken from the register: `heart_`,
  `dictionary_`, `senses_`, `tkzip_`, `micro_nn_`, `language_`, `body_`. The register is already the
  project's taxonomy, so naming becomes a RULE rather than a judgement each time. A cross-cutting
  table that no component owns keeps a bare name and has to argue for it.
- **The layer is in the name too when there is one**: `dictionary_base_relations`, not
  `dictionary_relations` — because `dictionary_sense_vectors` is coming and the base is not the
  whole dictionary. A name that leaves room for what is coming is a name that will not have to move.
- **No abbreviations that cost a lookup.** `base_r` and `base_d` were the shortest possible names and
  the least readable in the schema; a reader had to learn an alphabet before reading a row.
- **The same goes for parameters, variables and functions.** `relational` and `distributional`
  rather than `R` and `D` outside a formula; a local whose meaning is not in its name is a comment
  waiting to be written.
- **The db is named for what it IS.** `tokeniko_tk2` is this generation's body; it used to name the
  discarded prototype while the body was called `tokeniko_tk2_body`, which is a name doing the
  opposite of its job.

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
                                              └──► E3b names (beside E4; in before PS1)
                                                     ▲ carries E5's ABSTRACTION (Cap, 09-16)
   └──► E5 micro-nn (the epic stays here; its machinery lands in E3b with the first real case)
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

**Goal:** the PoC (983 dims, `docs/dictionary/origin-prototype/`) becomes the full base: every lexicon word under
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
   **LANDED 2026-09-04/09 (`f71baa3`, `7da676f`)** — R is square over the 4,445 base keys, built by
   walking edges rather than the PoC's 19.8M-pair loop (5s); every cell names the relations that
   produced it and whether it was mined or curated. The weights and the POS alphabet are policy v3
   rows; curation's `approve` is a testable gate, not a CLI branch. **Two rulings came out of it,
   both on measured numbers, both now rows:**
   - **v4 — the lemma scope (`word`).** WordNet states antonymy and derivation lemma-to-lemma; the
     PoC read them across the whole synset, asserting **6,634 edges the resource never wrote**
     (`abstract.v → sugar.n`, lent by `cabbage`) including **257 unaudited negatives** — of which
     `dark.n → day.n` was an antonym lent by `night` sitting on top of a real holonym. *A wrong
     negative is worse than silence; ABSTAIN is first-class.* R: 56,599 → **49,965** cells,
     membership unmoved, and **`land.n~land.v` (FAR) and `cause.n~cause.v` (NEAR) moved in opposite
     directions for the first time** — the POS collapse is separable, which is what the bar was
     declared to test.
   - **v5 — the inferred opposition (`add_only`).** Opposition is symmetric even where the
     lexicographer wrote it once, so the reverse cell is stated **where R is silent and never over a
     stated one**: the overwriting variant destroyed four real relations, including the very
     `dark.n → day.n` cell v4 had just repaired. The inferred half carries **its own relation name
     and its own weight row** (`antonym_inferred`), so a cell can always say whether WordNet stated
     the opposition or we completed it — the same principle that keeps curated distinguishable from
     mined. 143 added, 0 overwritten, seven dimensions stop being silent (all adjectives/adverbs,
     R's quietest ground). **The bar reads identically under all three readings** — this ruling rests
     on the principle, not on a number, and the rows say so.
   - **Neither reading has a code default**: an undeclared scope or mode is a refusal, never a quiet
     fallback, and a build whose provider disagrees with the declared law is refused at assembly.
   - Standing R under v5: **50,108 cells** (0.25% density), 806 negative, 346 silent rows;
     `derivational` **5,870 cells / 11.7%**. Silent rows are not evenly spread — adverbs 46%,
     adjectives 13%, nouns 1.7%, verbs 0.3%: **R is close to mute about adverbs**, and the honest fix
     is D and curation, not borrowed edges.
3. **D at scale** — gloss overlap over POS-split keys; derivational down-weight DECIDED here (the
   land.n~land.v OPEN item); membership repair with POS-aware lemmas.
   **LANDED 2026-09-09 (`b8f325e`).** D is the second floor: unsigned, symmetric, square over the
   same 4,445 keys, mined through the seam T2/T2b/v4 hardened so it cannot re-open a defect R
   already closed. Its walk arrived as **nine policy rows on its first day** (v6, migration 0009)
   rather than a table in `config.py` — and those rows' notes named their own defect in numbers,
   which is what made the ruling possible: at the prototype's gate of two, **87% of D's cells sat at
   the cap**, so D had stopped saying HOW MUCH.
   **v7 (migration 0010) is ONE ruling with THREE values**, all measured:
   - **`min_shared` 2 -> 1.** The gate was suppressing the evidence (swept: 1 -> 1.67M cells, 41% at
     cap, 41 silent rows, D alone 47/80 · 2 -> 153,830, 87%, 809, 26/80 · 3 -> 19,524, 98.7%, 2,285,
     8/80). **At one, D separates what R cannot**: `cause.n~cause.v` +0.050 against `land.n~land.v`
     +0.024 — twice as near, where R states the *identical* derivational cell.
   - **`derivational` 0.90 -> 0.45.** A **peak, not a slope**: 0.90->64 · 0.60->65 · **0.45->67** ·
     0.30->66 with the LOCAL order breaking (5/7 -> 4/7). Halved and not killed — the POS collapse is
     now pulled apart by **evidence** rather than by silence. *It also moves PROVENANCE, not only
     weight:* R's total is unchanged but **101 cells change which relation they claim**
     (`attribute` 302 -> 400), because a derivation no longer outranks a stated `attribute` (0.70).
     The row's note says so — a weight ruling that silently re-labels cells must be told, not found.
   - **`mix` = 0.5, and it becomes a row at all** — in its own **`ReadingPolicy`** with its own
     dated law, because *a parameter must travel with the law it is applied under* (a bare float
     would let the concatenation shape change underneath a fingerprint). At mix 1.0 **D drowns the
     opposition R states** — `enter~leave` goes positive. T5's acceptance floors belong in the same
     object.
   - **The dual read: 58/80 -> 67/80, local order 4/7 -> 5/7, MUTE 7 -> 0**, membership unmoved.
   - **Both parked questions CLOSED, with their numbers in the rows so nobody re-litigates them
     blind:** `senses="all"` **rejected** (key space 4,445 -> 12,925, `enter~leave` reads +0.759,
     local 1/7 — and it moves MEMBERSHIP, a different kind of decision from a weight); `idf` **not
     adopted, measured twice** — once at each gate, because the `min_shared` ruling repealed the
     first measurement's conditions. At the ruled gate it cuts junk's share of shared mass
     62.9% -> 45.7% (a bigger win than before) but the only-junk pairs never move (63.5%, that
     figure is membership) and the reading gets **worse, 67 -> 65**; decisively, `bed.n~cause.n` — a
     declared FAR and D's worst false positive — gets **louder**, +0.338 -> +0.352.
   - **`measure` and `vocabulary` are unruled BY DEFAULT, not by decision**: at the old gate all
     three measures and both vocabularies returned the identical bar (everything saturated). At the
     new gate they are observable for the first time — a real question, now askable.
   - **Carried to T5, measured not guessed:** D is **218.8 MB BSON** (max document 259 KB, the 16 MB
     limit nowhere near), written as ONE `insert_many` that pymongo splits into ~5 wire batches —
     **not atomic**. An interrupted apply leaves a partial base under a build label with no manifest
     row; 218 MB over the network to the body makes that likely rather than theoretical.
   *The two questions as they were parked by the Captain, 2026-08-25:* (a) **the sense mode** — the closure mines `senses="primary"`, so for
   every polysemous word the edges come from whichever sense WordNet ordered first, and that is
   frequently not the sense that made the word frequent (`small` = «the slender part of the back»,
   `large` = «a garment size», `plant` = «buildings for industrial labor», `state` = «the territory
   occupied by…»); measure `senses="all"` against edges, base size and the bar before ruling.
   (b) **high-frequency dimensions** — after the name refusal the residual gloss-overlap floor is
   real function words (`in` 27% of base rows, `be` 14%, `by` 14%, `as` 10%), which is a WEIGHTING
   question (IDF-shaped down-weight), not a membership one.
4. **Inflection-collision fix** — req 21 proper (`left`/leave, `use.v`/`used.v`): lemma-normalize at
   gloss-mining time.
**LANDED 2026-09-10 — THE BASE IS BUILT AND ON THE BODY.** `tokeniko_tk2_body` holds the first
sealed base: **4,555 dimensions · R 51,564 cells · D 473,262 cells**, config fingerprint
`9824ef46…`, policy v9, bar v2, authorized and applied by the Captain's own hand. Read back whole by
`tools/verify_base.py` — every matrix's content fingerprint recomputed from what came back and
matched against its seal.

**THE SCOPE BOUNDARY, stated here because it is the thing most easily misread:** what E1 built is
the **BASE** — the 4,555 POS-split keys the geometry is *stated over*. It is NOT the full dictionary:
the resource carries **68,779 words and 120,475 senses**, and those ride ON the base (a sense holds a
D-vector over base dimensions and consults R through its sense key — the epic brief's architecture
guard, tkzip req 11). **The base is complete; the sense layer is not built and was never E1's.** It
has no home in the plan yet — see «what E1 did not build» below.

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
without finding a new `left`. — **ALL MET 2026-09-10.**

**What E1 did NOT build, and where it goes.** The base is the *frame* of the geometry; the full
dictionary is the 120,475 senses read against it. Building that layer needs two things E1
deliberately did not decide: the **sense vector** (how a sense's D-vector over base dims is derived,
and whether R is consulted per sense or per key — tkzip req 11's «rides on the base») and the
**sense selection** (`senses="primary"` was measured and kept, and its rot is documented in task 3 —
`small` reading as «the slender part of the back» is a *base* problem today and becomes a *sense*
problem the moment senses are first-class). Neither belongs to E2 (the zip's schema) or E3 (the
station): it is **a dictionary task with no epic**, and the plan must gain one rather than let it
arrive by accident inside another epic's scope. ~~Named here as OPEN, for the Captain to place.~~
**PLACED AND BUILT: it became E1c** (2026-09-10), which ruled both questions it names — the sense
vector carries BOTH floors, and `senses="primary"` stands with a reason rather than by default. The
epic the plan had to gain is below.

---

## E1b — The names, and one baseline *(done 2026-09-10)*

**Goal:** every collection says what it holds and who owns it, before E1c doubles the dictionary's
surface. Ruled by the Captain the day E1 closed, on the argument that the naming was itself a source
of confusion — «is the dictionary complete?» is a harder question to answer when the collection
holding the answer is called `base_r`.

**What moved.** `base_r`/`base_d`/`base_keys`/`base_seals` → `dictionary_base_*` (the layer is in the
name because `dictionary_sense_vectors` is coming) · `closed_classes` → `language_closed_classes` ·
`derived_points` → `tkzip_derived_points` · `channel_registers` → `senses_channel_registers` ·
`forecasts`/`emotional_log` → `heart_*` · `params` → `body_params`. The db `tokeniko_tk2_body` became
**`tokeniko_tk2`**, the name having been freed by dropping the 983-dimension PROTOTYPE it used to
hold — superseded whole by the base E1 built.

**Why it was a REBUILD and not a rename.** Mongo cannot rename a timeseries collection at all
(`heart_emotional_log` is one, with its `system.buckets` shadow), and moving a database is a copy in
any case. The cost of a rebuild was measured before it was chosen and it was **nothing**: every heart
row read `0.0` with `created_at == updated_at ==` the migration's own timestamp. He had been created
and had never ticked.

**The thirteen migrations became one baseline** (`db/0001_the_world_and_everything_declared`, the
originals in `db/archive/`), and the ledger did not go with them — **the ledger was never the files**.
All nine policy versions are written by the baseline with their notes verbatim, out of
`db/data/declared_rows.json`: v1 still fingerprints to what v1 measured, v4 still argues its own
lemma scope. What was given up is the SEQUENCE as replayable steps, which survives in git and in the
notes but not as thirteen runnable files — a price the Captain took knowingly.

**Proved rather than asserted:** the config fingerprint `9824ef46…` reproduces exactly from the
baseline, and every collection was compared row by row against the old world before it was dropped —
identical, all of them. The base was rebuilt and read back WHOLE.

**Also landed:** the third standing law (above), and the guard's special case for the prototype's
database retired — `tokeniko_tk2` is now the one name it allows rather than one it singles out.

---

## E1c — The sense layer *(done 2026-09-10)*

**Goal:** the full dictionary. E1 built the BASE — 4,555 POS-split keys, the frame the geometry is
stated over. The resource carries **68,779 words and 120,475 senses**, and those RIDE ON the base: a
sense holds a D-vector over base dimensions and consults R through its sense key (the architecture
guard, tkzip req 11 — **never a senses×senses matrix**).

**Why it comes before E2.** E3's parser resolves a word to a SENSE, not to a POS key, and
discovering that mid-station would be expensive. The Captain ruled it first on 2026-09-10: «we should
take care of it before anything else».

**The two decisions, MEASURED then RULED 2026-09-10:**

1. **The sense vector: BOTH floors, mirroring the base.** A sense carries a `distribution` vector
   (its own definition through the same seam D uses) and a `relations` vector (what WordNet states
   about THIS SYNSET, mapped onto base dimensions). Measured first: the gloss reaches **3.41** base
   dimensions on average and is empty for 5.3% of senses; the synset's relations reach **0.86** and
   are empty for **54.1%**. Relations alone cannot place a sense — which is why both, and why a row
   with empty `relations` is the normal case rather than a fault.
   *The relations are the point of the layer*: WordNet states them per SYNSET, and collapsing
   synsets to POS keys is what lost them. `bank.n.01` reaches `slope`, `bank.n.02` reaches
   `financial institution`, and `bank.n` is both at once and so reaches neither cleanly.
   The distribution vector is an **indicator** and says so: a sense is placed against a DIMENSION,
   which is one word and not a definition, so «this definition names `slope`» has no magnitude.
   Measured the other way first — scoring one shared word against the definition's length — and
   **94.8% of the cells landed on the cap anyway**, the same saturation that halved D's gate at T4.
   The `weighting` seam is kept, so a later `idf` ruling makes the cells stop being flat.
2. **Sense selection: `senses="primary"` STANDS for the base, now with a reason rather than by
   default.** The rot was never in `primary` — it was in having nowhere else to put the other
   readings. Both alternatives were measured and both cost more than they bought: `senses="all"`
   triples the key space and collapses the local order to 1 of 7 (rejected at T4), and the UNION of
   a dimension's senses into its gloss vector buys +5 on global order while **burying 15 stated
   oppositions**, lifting every FAR control and flipping `land.v~leave.v` positive — because a
   thirteen-word vector shares words with everything. **The base is the frame, the senses are the
   content**, and that sentence is the whole ruling.

**Answers to:** dictionary req «sense-split seam» (resolved in part at E1 — dimensions stop at POS;
this is the other half) · tkzip req 9 (a wrong verb sense is a wrong action, so senses must stay
distinguishable in the dictionary layer).

**LANDED.** `dictionary_sense_vectors`: **120,475 senses, 116,725 placed (96.9%), 816,309 cells**,
built in ~4½ minutes and sealed like a matrix — the layer reads back WHOLE or it does not read. The
base is unchanged by it (`9824ef46…`), because the layer rides ON the dimensions and is never
square: 120,475 × 4,555 is half a billion possible cells against 14.5 BILLION for senses×senses,
which is the mistake the row's shape makes impossible to write.

**One defect it surfaced, flagged at T5 as theoretical and now real:** a manifest recorded the
POLICY a build ran and never the LABEL its rows are under, so the only link was that the default
label IS the head of the config fingerprint. The moment two builds shared a policy — E1b's rebuild
and E1c's layer — the verifier printed one build's authorization beside another build's rows.
`DictionaryBuildDoc` gains `build`, and the verifier finds by it.

*Open, and named rather than left to be discovered: **an unplaced sense** (3.1%) is one the station
will have to ABSTAIN on — the count is in the manifest so that is predictable rather than
surprising · the **acceptance floors are the base's**, measured over base-to-base cosines, and
whether a sense-to-base reading is judged by the same numbers is E3's question, not answered here.*

***MEASURED 2026-09-14, and it is now E3's with a number rather than a worry.*** *Base-to-base
cosines are +0.000 at p90 and +0.117 at p99, so the ruled floor of +0.15 is a HIGH bar in the
population it was fitted to. Applied to sense-to-base placements it is not: the top-1 cosine of a
placed sense has a median of **+0.484** when relations placed it and **+0.228** when the distribution
did, so the same +0.15 reads **NEAR for 99.7%** of relations-placed senses and 89.7% of
distribution-placed ones. **A floor that says NEAR to everything is not discriminating** — it is a
threshold calibrated on another population. Nothing is wrong with the base's floor, which is the
point: the sense layer needs its OWN, fitted its own way, and E3 is where a placement first has to
be trusted or refused.*

---

---

## E1d — The audit's repairs *(opened and closed 2026-09-14)*

**Why it exists.** At E2's close the Captain called in a parked order: *«go through all the docs of
`tokeniko-tk2/docs/<chapter>` and see if we missed something in the old requirements.»* The
`docs/dictionary/` audit measured all 21 requirements against the sealed build and found **11 clean ·
6 partial · 2 lost · 1 contradicted by construction · 1 superseded**.

**His framing, and it governs the epic:** *«as you were wrong in not taking into consideration the
full list of reqs, so was I. We are not searching the blame. I would like to not have bias: if we
ruled in some direction, it is not relevant. What is relevant is the final status, how much it differs
from all the original requirements, and what we can do to fix.»* **So E1d is judged against the
chapter as written, never against what was ruled later.**

**Tasks**
1. ~~**The audit, written in**~~ **— DONE 2026-09-14.** `docs/dictionary/202609141115_the-e1-audit.md`;
   21 statuses corrected in place, the original wording left untouched because what a requirement SAID
   is part of the record.
2. **SEPARATE READS (req 10)** — the requirement says R and D are *«consulted separately, every answer
   naming its source, never blended into one float»*, and `distribution.py`'s own docstring repeats it,
   while `space.py` returns `cos(R + 0.15·D)`. **Ruled 2026-09-14: separate.** The verdict shape
   changes; req 19's dual read (cosine AND direct cell) becomes what the verdict actually uses.
3. **MINE `gloss_reference` INTO R (req 2)** — `eat~food` is refuted at scale because their glosses
   share nothing: D measures what two definitions SHARE, and the real relation is that *eat's
   definition NAMES food*. Both edges the Captain curated by hand are instances of that one rule, and
   the signal is already computed by `glosses.lexicon_words_in` and thrown away. Measured caveats:
   roughly doubles R, and carries noise (`bed`'s gloss also names *furniture, ground, plants*).
   **The Captain rules the weight AFTER the measurement, never before.**
4. ~~**THE CURATION GUARD**~~ **— DONE 2026-09-14, and it is a structural repair rather than a
   check.** `curation.py` produced cells that went into R, so a curated edge was an OUTPUT of a
   build and never an INPUT to one; E1b dropped the prototype db and the rebuild regenerated R
   without them. **No check could have saved them** — the decision had nowhere to live. So:
   **`dictionary_curated_edges`**, append-mostly (withdrawn, never deleted), consumed by
   `build_base`, with the manifest finally recording `curated_edges` / `cells` / `withdrawn` /
   `unresolvable`. **A build REFUSES** when an approved edge names a dimension this base does not
   have — a rebuild moves the closure's cut, so an edge can outlive its dimension, and that is
   precisely the silence E1d exists to end. A curated cell OVERRIDES a mined one and the override
   is reported, because «the resource stated otherwise and a person disagreed» is a discovery.
5. ~~**RE-APPROVE THE TWO LOST EDGES**~~ **— WRITTEN AND APPLIED 2026-09-14 (`db/0005`).**
   `bed.n→sleep.v` (`used_for`) and `hungry.a→eat.v` (`state_of`), with the ORIGINAL authorization
   and date carried, because this restores a decision rather than making a new one. **`sleep~bed`
   closes** — the pair the 2026-08-12 review called the one only R gets right.

6. ~~**REQUIREMENT 16**~~ **— CLOSED 2026-09-14 (policy v13, `db/0006`, applied).** Requirement
   16's own proposed fix — down-weighting `derivational` — was measured IMPOSSIBLE: a weight is a
   monotone rescale and `compass.n~compass.v` (FAR) sits above `buy` and `cause` (NEAR) at every
   scale. A D threshold failed on the population (it landed on the median of 1,626 sibling pairs).
   **The defect was a resolution mismatch**: the closure reads `senses = "primary"`, so a dimension IS
   its primary sense, while `derivational` was mined across every sense. Mined at primary-sense
   resolution it separates all seven declared siblings with no threshold. On a real rebuild of R:
   `derivational` 5,964 → 1,719 cells, `compass` +0.273 → +0.095, and the best zero-wrong floor is
   0.10 on a plateau to 0.20 (19 of 37). **The floor is NOT moved** (the Captain's ruling): at the
   standing 0.28 v13 decides 17, one fewer than T5 (`buy.n~buy.v` falls to +0.246), so the re-ruling
   after the rebuild is a real dependency.
   **Decision record: `docs/dictionary/202609141714_requirement-16.md`.**

7. ~~**APPLY, REBUILD, RE-MEASURE, RULE THE FLOOR**~~ **— DONE 2026-09-14, on the Captain's order.**
   `0003`–`0006` applied; the base rebuilt as **`969766250c02`** with the sense layer and read back
   WHOLE against all four seals; membership unchanged at 4,555 dimensions, so the frontier measured on
   the rebuild of R still described the base. Re-measured through the verdict reader on the stored
   build: zero-wrong from 0.10 to 0.20, 19 of 37. **The floor governs one gap** — `compass.n~compass.v`
   FAR +0.0948 below, `walk.v~run.v` NEAR +0.2116 above — and the Captain ruled **+0.15, the middle of
   it** (policy v14, `db/0007`, applied). `db/0002`'s order was followed this time: rebuild, then
   measure, then rule.

**Done when:** ✅ **MET 2026-09-14.** Every requirement the audit marked REFUTED, LOST, CONTRADICTED or
open is closed — 2, 10, 14, 16, 19, 20 — and it is TRUE ON THE BODY, not only in code. **Bar: 13 → 19
of 37 decided, 0 wrong.** Carried forward, named: ~~the old build `9824ef465c86` is still on the body~~
**dropped 2026-09-14, and `MatrixStore.drop()` fixed — it never covered the sense layer and left
120,475 orphaned rows** · ~~the build tool's printed bar report still scores the pre-v11 blended
reading~~ **fixed — it scores through the engine's own reader, and `--floors` works under separate
reads** · **D's neighbourhood cannot be tuned** (benched: no variant helps; R proposes instead) ·
**the placement floor is E3's**, measured and handed over above.

*T2 precedes T3: «did it close?» cannot be answered while the verdict is a blend.*

## E1e — The tests, isolated *(opened 2026-09-17 by the Captain — runs AFTER E3 closes)*

> *«Tests are there to verify that the next development step is not regressing the already working
> requirements. They should be the gate for each dev step, but they should be WELL isolated from the
> BL. We need to look into everything we have done from E0 to E3 and see if tests, somehow, are
> leaking into the BL code (at least from a formal order point of view) and strongly and neatly
> separate them.»*

**IT IS NOT ABOUT `dictionary_bar`, THOUGH THAT IS WHAT FOUND IT.** The bar — 37 declared pairs the
base must satisfy — lives in the BODY database and, worse than that, **in the runtime config**:

    # DictionaryConfig.seeds
    for word in (*self.declared_seeds, *bar_words(self.bar), *self.closure.extra_seeds):

Requirement 8, verbatim: *«the seeds + the bar's own words are forced into every subset»*. So **the
acceptance test injects its own vocabulary into the artifact it judges**, and rides in the config
fingerprint every consumer reads. The original reason is sound — `eat.v NEAR food.n` cannot be
measured if `food.n` is not in the space — but that justifies *a bar-measuring RUN* adding them, not
*the standing policy* declaring them for everybody.

### THE THIRD KINGDOM

The frame/knowledge rule governs the APP'S BUSINESS LOGIC, and the Captain drew the line explicitly:

| | what it is | where it lives |
|---|---|---|
| **frame** | law the app obeys | code — and kept small |
| **knowledge** | revisable facts the app reasons with | db, by migration |
| **evidence** | curated circumstances that JUDGE the app | isolated; never read at runtime |

*«A test is by its nature a curated set of circumstances: it can't be knowledge, it is curated, and
it should be isolated by the app itself.»* Evidence still wants the LEDGER properties that sent the
bar to a database in the first place — versioned, append-mostly, `why` kept verbatim — and those are
separable from WHICH database. `closed_classes` is **not** in this kingdom: the station reads it at
runtime, so it is app knowledge.

### THE TASKS

1. **Sweep E0 → E3 for test material in the BL** — formal order included: what does app code import,
   read or configure that exists to judge it? `dictionary_bar` is the known case; the sweep is for
   the ones nobody has noticed.
2. **`dictionary_bar` out of the body.** To the test database, or to `bar_snapshot.json` alone,
   which already exists, is hash-pinned, and already runs with no body reachable.
3. **The body keeps only PROVENANCE** — `dictionary_builds.bar_version` + `bar_fingerprint`, a claim
   checkable against the snapshot.
4. **Bar words stop being standing seeds** and become `extra_seeds` on a measuring run — a mechanism
   that already exists and whose own docstring is the argument for this: *«what a run argues with the
   standing policy… so a run that added seeds can never be mistaken for the standard one»*.
   **COST, STATED: this moves the config fingerprint**, so builds recorded under the old one stop
   being directly comparable. E9-shaped, not a free edit.
5. **The doctrine line** in `tk2/core/models/__init__.py` calls policy, bar and closed classes one
   thing («CURATION (logic)»). It is three things now, and the comment says two.

### AND THE PACING RULE, WHICH IS THE OTHER HALF

> *«I would like the development of these foundational points (dictionary, tkzip) to be agile and
> fast paced: burdening every single move with a gargantuan suite of tests for each micro step is
> really slow — also considering that many of them work remotely on the body, so there is latency to
> consider. Excluding single cases (where a test subset must be executed to steer the development
> itself), tests are performed at the final commit/push, not during the intermediate steps.»*

**Concretely:** during development, run only the subset that STEERS the next decision — the file
under the hand, the one gate that answers the open question. **The full suite runs once, at the
commit gate**, and that is when its result is reported. A green full suite is a precondition of
asking for the commit, not a checkpoint between edits.

## E2 — The format *(tkzip v2)* — ✅ **COMPLETE 2026-09-14**

**Goal:** the fixed-arity zip — limit B dies on paper before any code. The schema answers every open
question the blueprint carries.

**Answers to:** tkzip reqs 1–17 · README §7 open questions 3–9, 13 · carried-in (OQ9 storage,
mood/imperative field, third-memory-tier framing).

**Tasks**
1. ~~**Role inventory**~~ **— DONE 2026-09-11.** Seventeen boxes plus the predicate, cut from
   VerbNet (29 roles / 429 classes), PropBank (112,917 annotated sentences) and FrameNet (1,221
   frames), and cross-checked against the Captain's own first draft (`docs/tkzip/origin-the-excel-draft.md`).
   The inventory is **FRAME** — code, fixed, exhaustive; a miss is a bug, never a migration. Roles are
   **named and verb-independent**. The noun-phrase record is five fields (quantity · count ·
   determination · relation · noun). OQ2, OQ3, OQ4, OQ5, OQ13 answered; OQ7's quantity/determination
   split answered, its definiteness-as-scoping half carried into task 2.
   **Decision record: `docs/tkzip/202609111051_notes.md`; requirements 18–32.**
2. ~~**Named rows & scope**~~ **— DONE 2026-09-11.** A zip is a FLAT LIST; nesting is naming
   (Tseitin, OQ8). **Row order = scope order** (OQ6), and the prefix carries FIVE scope-bearing
   elements — `quantifier · negation · modality · attitude · domain` — so row order is never free for
   anything else. Quantification uses BINDER ROWS: one binding mechanism for quantification,
   questions, equations and naming. **CAUSE, RESULT and PURPOSE all dissolve** into `IMPLY` + the
   theatre's arrow of time (premise: in a deterministic world a cause is what implies its effect);
   «because» vs «if» is carried by ASSERTION STATUS, «only» converts IMPLY→EQ. **The operator set is
   the TEN non-degenerate binary truth functions — frame, closed by mathematics, never trimmed to
   what English marks.** `domain` satisfies req 6 with no new machinery.
   **Decision record: `docs/tkzip/202609111511_notes.md`; requirements 33–46, req 29 rewritten.**
3. ~~**Binding states & moods**~~ **— DONE 2026-09-11.** The largest collapse of the epic:
   **mood is not a field.** Question = something OPEN (a box, or the row's TRUTH for polar questions)
   · imperative = POV(want) over an unasserted row · supposition = POV(suppose), which is what
   heart 16's imagination gain reads · forecast = a future theatre + confidence in the truth slot
   (heart 17, verbatim) · irony = the figurative layer, not the schema. A question and an equation
   are the SAME zip (the Captain's own 2026-08-11 ruling, found in the notes).
   **Net addition: the binding state (`BOUND` · `OPEN` · `EMPTY`) on any slot, a PRIOR on an open
   slot, and the nominal record's sixth field (`sense`).** Scalar wherever there is a quantity.
   **Decision record: `docs/tkzip/202609111607_notes.md`; requirements 47–57, req 26 extended.**
4. ~~**Confidence + provenance fields**~~ **— DONE 2026-09-12.** Mostly an audit: almost everything
   expected here was already built at E0 or answered by task 3. **Net addition: ONE field,
   `parse_confidence` — one scalar on the whole zip, and a slot, so it may be EMPTY** (self-talk
   invokes no parser; 1.0 would claim perfect understanding of an utterance that never happened).
   One number because its calibration signal («did the speaker correct me?») arrives per UTTERANCE;
   per-part doubt is already carried by binding state + prior — a half-heard word is `OPEN`, never
   `BOUND` to a guess. Provenance, `derived_by`, `original` and forecast resolution are all
   DOCUMENT-level and all four exist since E0. A resolved forecast mints a new belief; the stored zip
   never mutates.
   **Two findings handed to their own chapters rather than decided here** (the Captain's ruling,
   2026-09-12): `docs/data-modeling/` req 7 — what a PARSED belief's parents are; `docs/datatier/`
   req 7 — the retreat cascade has no reverse index on `parents.id`.
   **Decision record: `docs/tkzip/202609121556_notes.md`; requirements 58–60.**
5. ~~**Storage**~~ **— DONE 2026-09-12.** Decided by measurement: PropBank's 112,917 predicate
   instances give **mean 2.59 roles per row of 18 slots — ~80% of every row is EMPTY** — so storage is
   **sparse** and fixed arity is a property of the schema, not of the storage (OQ9). **The KEY is the
   truth, the VECTOR is an epoch-stamped cache** (dictionary req 13), which is affordable because
   E1c's sense vectors average **6.78 cells of 4,555**: roughly **60×** smaller than v1 per sentence.
   **The consequence that matters: a dictionary rebuild invalidates only the cache, so E9's
   translation night is for a SCHEMA change and never for a new base.** The theatre is a cache on the
   same pattern. Row names are zip-local, so a zip is self-contained — whether it is EMBEDDED is
   data-modeling's call. Case 7 added a seventh record field (`marker`).
   **Decision record: `docs/tkzip/202609121807_notes.md`; requirements 61–66, req 26 extended.**
6. ~~**THE DRILL**~~ **— DONE 2026-09-14. ⚑ 78 sentences, 97.4% no-abstention, 0 silent-wrong,
   BAR MET.** Bar and scoring rules declared and committed BEFORE the drill existed (`1a68337`).
   Raised 50 → 75 (drilled 78). **All 28 sentences drawn from his own stored journeys zipped clean.**
   **Three schema changes forced, each named with the sentence that forced it** — `direction` (the
   18th role: «He looked up») · `scopes` on prefix rows («software can be minds and humans must be
   minds») · `Ref` («the result of perception and learning and reasoning»). The only abstention is
   **`almost`**, on two witnesses, which amends req 23. The drill also caught SEVEN QM encoding
   errors, none of them the schema's fault — attributive adjectives are second rows.
   **Deliverables: `tk2/tkzip/schema.py` (frame, frozen v2.0) · `tests/fixtures/drill.py` ·
   `tests/test_tkzip_schema.py` · `tests/test_drill.py`. 796 checks green.**
   **Decision record: `docs/tkzip/202609141009_notes.md`; requirements 67–73.**

**Done when:** the drill passes its pre-set bar on paper and the schema is frozen v2.0 (changes
after freeze are migrations, not edits).

---

## E3 — The station *(parser/compiler, one lib)*

**Scope, stated so it can be defended** *(the Captain, 2026-09-15)*: **natural language → skeleton
(stanza) → tkzip.** Mechanical. What the zip MEANS — senses bound, truth, consequence — is the
evaluator's and the mind's, which is evaluator req 5 already written down. The station consults the
dictionary for **SHAPE, never for MEANING**: the ported content lists become geometry with a
nearest-anchor fallback, and the sense slot is emitted **OPEN**. Record:
`docs/parser-compiler/202609151148_the-ud-gate-and-the-stations-edges.md`.

**Goal:** surface → tkzip → surface, one pure bidirectional library. tk1's AST/LLC die as
interfaces — **and its ~40 hand lists die with them**: the standing law above prices this epic's
first bill, so every ported set arrives as rows (the grammatical classes and the weights alike — they
are knowledge, not frame) or as geometry with a nearest-anchor fallback (the content lists). A list
copied across as written is a rebuild that inherited the defect.

**Answers to:** parser-compiler reqs 1–10 · rag reqs (the in-fence) · senses req 7 (dumb ear feeds
it).

**Tasks**
0. ~~**The closed classes as typed KB rows**~~ **— THE TABLE EXISTS. What is owed is its SEMANTICS.**
   *Rewritten 2026-09-15, on the Captain's ruling, after checking the body rather than the plan.*
   E1 built `language_closed_classes` when it needed to exclude function words from its seed
   ranking — the «born earlier, one table two consumers» clause below came true — and it holds
   **383 typed rows** sourced verbatim as «tk1 `lib/llc/constants.py`, the hand list this table
   retires»: 135 prepositions · 77 pronouns · 47 conjunctions · 41 determiners · 24 particles ·
   17 adverbs · 17 auxiliaries · 13 modals · 7 clitics · 5 postpositions, across 22 roles.

   **But `compiled` is EMPTY on all 383.** The enumeration landed and the MEANING did not, and the
   plan's own words for this task were «each row carrying its type **and its compiled meaning**».
   So E3's task is the second half: referential → entity (resolved from context) · quantificational
   → quantifier · interrogative/relative → unbound variable + question mood · **prepositions → WHICH
   OF TKZIP'S 18 ROLES each marks**, which is exactly the question E2's drill parked when it left
   `direction`'s marker cluster here («does *toward* entail arrival?»). All 135 prepositions are
   typed `role_marker` today and not one says which role it marks.

   **This kind is NOT rebuilt from raw input, and that is the point of naming the kinds.** A closed
   class is closed BY ENUMERATION; a corpus can TEST its completeness and can never generate it.
   Deriving it from text is how the set silently becomes open — «the db option by the back door»,
   refused once already for tkzip's typed `other`.
1. **Skeleton adapter** — stanza behind the lib boundary, swappable (req 2); the torch-load patch
   and model-loading quirks contained in the adapter.
2. **The compile core** — roles filled from the skeleton + anchors (the resolver migrates — it's an
   asset); sense slots left OPEN; context-as-argument for anaphora/ellipsis/fragments (req 7);
   partial zips with open variables (req 8).
   **HALF DONE 2026-09-15** (`tk2/language/compile.py`, record
   `docs/parser-compiler/202609151415_the-compile-core.md`): one content row, both halves of the
   mapping, quantifier binders with their restriction, possessors inside the record, senses OPEN —
   **18 of 25 UD cases whole, mean coverage 89.5%**. The frame caught a design error on the way: a
   `QuantifierRow`'s `restriction` is a Box, so a binder cannot be emitted on meeting «every».
   ~~**WHAT REMAINS IS ONE FEATURE: MANY ROWS.**~~ **DONE 2026-09-15** (record
   `202609151505_many-rows.md`): one content row per clause, related by joins, attitudes and shared
   variables — **20 of 25 whole, mean 95.8%**. The three-way distinction of req 38 is produced from
   a real parse: «if» leaves both halves EMPTY, «because» claims both, «and» is the third, one
   operator set and no relation field. It needed **closed classes v4** (`db/0010`) first, because
   «if» and «because» carried IDENTICAL rows and nothing in the dependency tree separates them
   either — the assertion status is knowledge about the word.
   ~~**WHAT REMAINS:** the wh-word's box~~ **DONE 2026-09-15** (`db/0011`, record
   `202609151555_the-wh-words.md`): five kinds, and three of them are not boxes — `whether` opens
   the TRUTH, `whose` a FIELD, and **`why` an ANTECEDENT**, because req 37 left no cause box to
   open and the shape was already in the format. **21 of 25 whole, mean 96.8%.**
   ~~**WHAT REMAINS:** the thirteen ambiguous markers~~ **DONE 2026-09-16** (`db/0012`, record
   `202609160929_the-ambiguous-markers.md`): **22 of 25 whole, mean 98.4%; the UD gate answers 19
   of 25 with 0 WRONG.** `db/0008` predicted head-verb GEOMETRY and it was benched and lost — «is a
   pool a place?» is a hypernymy question, and the dictionary chapter ruled a month ago that cosine
   does not answer taxonomy. What settles them is a fact the resource STATES: **WordNet's supersense**
   (26 noun classes + 15 verb classes, published and closed — the UD gate's own «both ends closed, so
   the table can be complete» argument, arriving a second time). Measured on 52 cases with their
   gold: supersense 11/11 on the independent bucket, geometry 6 with 3 wrong, first-candidate 7 with
   4. **`of` needs no dictionary at all** — the head's POS settles it, and the gate caught the first
   rule set getting the possessor wrong. **A `default` now fills its box and is COUNTED** in
   `Compiled.defaulted` rather than abstaining: req 8 forbids the SILENTLY complete nearest fit, and
   a counted default is not silent. Residual errors: «at speed» (WordNet files speed under
   `noun.time`) and «with Anna» twice — **the named-individual hole**, parked with its own answer
   waiting. **NAMED DEBT:** the supersense is read LIVE from WordNet and is therefore outside the
   base's build fingerprint; its home is a `lexname` on `SenseVectorDoc`, which is a rebuild.
   **WHAT REMAINS, as the completed gate now names it** *(2026-09-16)*:
   - ~~**`amod`**~~ **DONE 2026-09-16** (record `202609161215_the-attributive-adjective.md`). The
     shape was not designed here — req 70 ruled it and the drill hand-compiled it at E2: the
     adjective is a second row with NO predicate, its subject is the PATIENT, and **the binder
     scopes the JOIN** because the variable lives in both rows. **An adjective forces a binder even
     with no quantifier word**, because a row saying `patient=body.n, complement=human.a` claims
     that BODIES are human. Ratchet **23/25 at 98.9%**, frontier **7/18 at 80.8%**, gate **31
     answered · 0 WRONG**.
     **AND IT FOUND A SLIP**: the copular subject is the **PATIENT**, not the `topic` the compile
     core wrote. `topic` here is SUBJECT MATTER («a lecture ON physics»); the drill uses it for that
     alone, three times, and hand-compiles the copular row as patient + complement 43 times.
   - ~~**⚑ THE TWO GATES HAVE NEVER MET**~~ **BUILT 2026-09-16** — `tools/drill_gate.py`, req 18,
     record `202609161502_the-two-gates-meet.md`. It scores AGREEMENT and not equality, because most
     of the drill needs features E3 has not built and an equality check would fail all 78 and teach
     nothing. **It crashed the compiler before it could score anything** — a `SPACE` token outside
     UD's seventeen (the Captain's «[de dicto]» annotations leave whitespace) and two rows called
     `m0`, which no UD sentence can produce because none carries both a modal and an attributive
     adjective. **Then six disagreements, now four**: two curation errors fixed by `db/0015`, one
     E3b, and **three witnesses of ONE open question**. 38 agreed · 4 DISAGREED · 91 of 126 rows
     paired, held as a ratchet by a `skeleton`-marked test.
     **WIDENED TWICE ON 2026-09-17**, both times because the drill's new quotation block walked past
     it. (i) It passed NO CONTEXT — the station returns the bare closed-class key for a pronoun when
     handed none, so the person axis was invisible by construction; it now passes the DRILL'S OWN
     convention (`speaker="me.n"`, `addressee="you.n"`), under which every unrotated sentence
     compiles exactly as before and only the rotation moves. Roles agreed went 71/138 → 98/129: the
     missing 27 were pronouns never compared to anything. (ii) It paired boxes by FILLER and asked
     about the ROLE — the `topic`/`patient` shape it was built for — and was blind to the MIRROR,
     the right role holding the wrong somebody, which is the only shape the person axis fails in.
     *An instrument built to catch one defect was shaped by it.* **47 agreed · 15 DISAGREED**, and
     11 of the 15 were always there. **50 agreed · 12 DISAGREED · 101 of 128 roles** once the
     rotation and the truth slot were fixed the same morning.
   - **⚑ THE SUBJECT'S ROLE DEPENDS ON WHAT IS PREDICATED OF IT** — TEN of the drill gate's twelve
     disagreements are one question, and it is the one `RELATION_FILLS_ROLE`'s own comment defers:
     «God exists» is a PATIENT · «the cat is hungry» an EXPERIENCER · «Sue is a teacher» a patient.
     *«Which one it is depends on the VERB, that is a head-verb question the geometry answers, and a
     station that guessed here would be doing the compile core's job badly instead of leaving it
     open.»* **Three witnesses on 2026-09-16, NINE on 2026-09-17** — `exist-3` `t-ws-1` `t-ws-8`
     `t-dc-4` `t-mo-1` `t-of-1` `aw-11` `aw-16` `aw-20`, and TEN with `q-2` — because giving the
     gate a context made the pronoun subjects comparable for the first time. It is now the largest family in the ratchet,
     which is an argument about WHEN it gets built, not about what the answer is.
   - ~~**content ADVERBS**~~ **DONE 2026-09-16** (`db/0013` + `db/0014`, record
     `202609161251_the-adverbs.md`). Requirement 23 split adverbs four ways at E2 and nothing said
     WHICH is which. **The resource cannot say**: WordNet has ONE adverb class (`adv.all`) and
     adverbs have NO hypernyms, so the supersense instrument that settled the markers gives nothing
     here. It is curation — **and curatable only because MANNER IS THE DEFAULT**: 79% of English's
     3,767 single-word adverbs are `-ly` and describe the action, so the table holds the 106
     EXCEPTIONS rather than the class. A default is COUNTED, never silent.
     **THE RULE'S FIRST LIVE APPLICATION MOVED THE ANSWER.** By the second standing law these are
     structure and belong in the closed classes; the Captain ruled a separate collection on a cost
     the principle does not see — those forms filter D's vocabulary, and 60 new ones would
     desynchronise the sealed base. The cost he named (two tables) is paid by making only the ROSTER
     second: `compiled` here is the closed classes' own vocabulary.
     **THE CLASH CHECK PAID FOR ITSELF ON THE FIRST RUN** — 11 forms were already in the closed
     classes and **10 were already compiled CORRECTLY** there. The other two became `db/0014`, which
     is FREE because the exclusion set is a set of FORMS: 268 before, 268 after.
     Frontier **9/18 at 82.2%**, ratchet unmoved, gate **31 answered · 0 WRONG**.
   - **`flat` / `list`** — one name across several tokens; E3b by another route.
   - **`xcomp`** — deliberately not a clause, and what it IS instead has never been ruled.
   - ~~**`nummod`**~~ **DONE 2026-09-16.** The box's own `count` field (req 26), and the three
     fields are ORTHOGONAL — «the three cats» is definite AND counted — so a numeral raises no binder
     and changes no scope. Frontier **10/19 at 83.2%**, gate **32 answered · 0 WRONG**.
     **⚑ AND IT NAMED A RULING THE CAPTAIN OWES.** «Sam ate 3 sheep» compiles whole; «Sam spent
     forty dollars» ABSTAINS and says why. `3` is ORTHOGRAPHY — the same mechanical transformation
     `normalize_word` performs, carrying no judgement about English. **`forty` is not**: it needs a
     roster of atoms plus composition rules, and `db/0001` ruled numerals out of the closed classes
     for exactly that reason. tk1 solved it with **`word2number`, which is present in this venv and
     is NOT in `pyproject.toml`** — and every dependency there was admitted by the Captain with a
     stated reason, so admitting a fifth is his and not the compiler's.
     **ADMITTED THE SAME DAY**, on `nltk`'s terms: one door (`compile.numeral_value`), local import,
     failure is an abstention and never a crash. The library is checked rather than trusted — it
     returns **0** for some strings that are not numerals, so a zero no word in the phrase asked for
     is refused. *The corpus case arrived abstaining and answered within the hour, and it is kept:
     a corpus that holds only what already works is a corpus that cannot report a gap.*
     Frontier **11/19 at 84.5%**, gate **33 answered · 0 WRONG**.
   - **`appos`** — one individual under two descriptions; unruled, and it leans on E3b.
   - ~~**embedded questions**~~ **DONE 2026-09-16.** **A wh-word has THREE readings and R5's binary
     test conflated the last pair**: root → interrogative (opens a slot, the utterance asks) · a
     noun-modifying clause → relative (BINDS an antecedent, opens nothing) · a complement clause →
     free relative (opens a slot, and the utterance does NOT ask). R5 answered the MOOD question
     rightly and was then read as «therefore relative». **UD marks the difference and nothing else
     does** — `acl:relcl` modifies a noun; an embedded question is a clausal complement.
     **AND IT FOUND A TRUTH ERROR, which is the worst kind**: «if you know WHO DID IT, tell me»
     CLAIMED that somebody did it. The `ccomp`'s AND asserted its operand while the other half of
     the same conditional was explicitly not claimed — so unassertion now propagates into an
     enclosed clause. The heads are walked in sentence order, so an enclosing clause has always
     spoken first and no second pass is needed.
     **Plus one honesty repair**: `if` was in the abstention list of a sentence whose IMPLY it had
     built, because the per-clause walk meets a joiner before `_relate` runs. A report that cries
     wolf is worse than no report.
     **Ratchet 24/25 at 99.4%** — a new high — gate **33 answered · 0 WRONG**.
   Context-as-argument is untouched; nothing has needed it yet.
2b. **⚑ THE PERSON AXIS — deixis, and the rotation under a point of view** *(the Captain asked
   2026-09-16; the answer was that tk2 had no plan and no note, and he ruled it E3 SCOPE the same
   day)*. Record: `docs/parser-compiler/202609161349_the-person-axis.md`, requirement 20.

   > *«John said to Marie: "You are a clever girl". The "you" should rotate to take for tokeniko the
   > meaning of Marie, not himself… and in general the pronouns to rotate the meaning depending on
   > the point of view.»*

   **The rule**: a first-person pronoun names the HOLDER of the innermost POV it is under; a
   second-person one names that POV's ADDRESSEE; with no POV the outer speech act supplies both.
   «John thinks I am wrong» still means the speaker — a THINKING pov addresses nobody, and only a
   saying does.

   **A wrong rotation is a wrong BELIEF, not a wrong parse**, and the evaluator cannot catch it: the
   zip is well-formed, internally coherent, and about the wrong person. That puts it with the shields
   (req 3), not with the features.

   **Four sub-tasks, in dependency order:**
   1. ~~**CONTEXT AS AN ARGUMENT**~~ **DONE 2026-09-16** (record
      `202609161521_context-as-an-argument.md`). `compile(skeleton, context=NO_CONTEXT)` — the
      speech act's speaker and addressee, plus `recent` declared for the anaphora that is not built.
      **The axis had its data since v1**: `i` carries `person: 1` and `you` `person: 2` in their own
      rows, and nothing read them because there was nowhere for «who is speaking» to enter.
      **Without a context nothing changes**, so no existing measurement moved. Third person is
      deliberately absent — «he» is ANAPHORA, not a speech-act participant — and **the station never
      invents an identifier**: it copies what the caller handed it, which is what keeps this from
      pre-empting E3b.
   2. ~~**MULTI-SENTENCE INPUT**~~ **DONE 2026-09-16.** `compile_utterance` compiles every skeleton
      of one utterance into ONE zip. The first sentence keeps its names (so a single-sentence
      utterance is byte-identical to before and nothing was re-measured); later ones are prefixed
      `s1.` **and every reference moves with them** — row names and variable names are two
      namespaces, and a second sentence's `x0` binding the first's variable would be a zip that is
      well-formed and means something nobody said. **The drill gate reported this gap and now reads
      all five split sentences whole.** The halves are not yet RELATED to one another; that is 2b.3.
   3. ~~**⚑ THE FORMAT RULING**~~ **RULED (a) BY THE CAPTAIN, 2026-09-16 — the format gains the
      field.** `SCHEMA_VERSION = 3`, `addressee: Box | None` on `Pov` and `AttitudeRow`. **The first
      migration of the frozen schema** (req 73). The alternative — read the `recipient` of a `say`
      row — cost nothing in the format and asked the resolver to KNOW THAT SAYING-VERBS ARE SPECIAL,
      a closed set of verbs in code, which is the exact shape his own rule of that morning refuses.
      *The cost was small: the body holds zero zips, so E9 has nothing to translate.* **EMPTY is the
      point, not `Open()`**: «no addressee» and «addressed to somebody unknown» are different facts,
      and only the first stops a rotation.
   4. ~~**THE ROTATION ITSELF**~~ **DONE 2026-09-16** (record `202609161544_the-rotation.md`).
      «John said to Marie that YOU swim» → `marie.n`; «John thinks that I swim» → `john.n` and «you»
      stays the outer listener; a conditional does not rotate at all. **It had to be decided BEFORE
      the clauses were compiled** — a pronoun resolves where it is met and its attitude is built
      later, so the contexts are worked out in a pass of their own from the tree.
      **And the Captain's own sentence crosses a sentence boundary**: stanza splits a quote, so a
      FRAME sentence (a saying with an agent and a recipient) rotates the next one. «John said to
      Marie "You are a clever girl"» → the `you` is **marie.n**.
      **AND THE QUOTE BECOMES THE CONTENT OF THE SAYING** — finished the same afternoon. «John said
      the sky is green» does not assert that the sky is green: the quoted sentence is placed under an
      attitude and its rows go EMPTY, the shape `ccomp` already produced for the indirect form. The
      attitude scopes the outermost JOIN, not a row under it, or «clever» would stay asserted outside
      the quotation.
      **UD's direct-quote case — the one this QM passed over — found a defect on arrival**: `that` is
      OPTIONAL, and without it nothing raised the POV, so «I asked: "Do you know the muffin man?"»
      CLAIMED that you know him. A bare `ccomp` under a saying verb is now reported content, and both
      forms produce the same zip. *It also separated BEING A FRAME from ROTATING: «I asked» addresses
      nobody named, so the `you` rightly stays the outer listener.*
      **2b IS COMPLETE.** *The drill still has no hand-compiled quotation — that is the Captain's to
      write, and the two gates now exist to disagree about it when he does.*

      **AND IT DID, THE NEXT MORNING.** Nine hand-compiled quotations landed 2026-09-17 on his
      green light (`q-1` … `q-9`, drill 78 → 87, amended in the bar doc), and they found the
      ROTATION INVERTED — record `202609170533_the-quotation-block.md`:

          «John said to Marie THAT you are late»    the LISTENER is late     station: Marie
          «John said to Marie "You are late"»       MARIE is late            station: the listener

      **Quotation preserves the original speaker's deictic centre; reporting does not**, because the
      reporter has already moved the pronouns into his own frame. `_contexts` keys the rotation on
      the joiner's `asserts: matrix` — which lives on the word «that», present exactly where
      rotating is wrong and absent from the bare quoted `ccomp` where it is right. *We keyed it on
      the one signal anti-correlated with it.* The correct signal is the QUOTATION MARKS.
      It also corrects 2b.2's premise: **stanza splits a quote only when the marks are SPACED from
      their words**, so all nine arrive as ONE skeleton and the cross-boundary path is the exception.
      The fix belongs in `_contexts`, and both paths need the same test.
      **FIXED THE SAME MORNING, AND THE CAPTAIN REFUSED THE QUESTION THE QM BROUGHT HIM.** It was
      «which characters count as quotation marks — frame or knowledge?», recommended as knowledge on
      multilingual grounds. His answer: *«Do we parse directly the input sentence, not through
      spacy-stanza which already has the tooling to isolate the quote? Do we parse anything else
      than English — the input on the parser is always English, the translation layer stays on the
      senses. I find it weak to care about what a quotation symbol is: we shouldn't have this
      problem in the first place, meaning if we have it something went in the wrong direction.»*
      **Measured, and he was right on all three counts.** A quoted complement's SPAN is bracketed by
      `punct` and a reported one is not:

          John said to Marie "You are late".      late/ccomp   punct  "  before,  "  after
          He replied “I am late” quickly.         late/ccomp   punct  “  before,  ”  after
          John said to Marie that you are late.   late/ccomp   no punct on the clause at all

      So `_is_quoted` never reads a character, and curly quotes work for free. *The rule's failure
      mode is not only HARD-CODING a set — it is NEEDING one. A question of the form «where should
      this list live» deserves one more question first: why is there a list?*
      Two further things the fix needed, both found by measuring: **the rotation must NEST** (depth
      two resolved to the narrator, because every clause was read against the outermost context),
      and **it must name the same somebody the rows do** (the holder's key was `i.n` where the box
      for that very token held `me.n`). `q-4` `q-7` `q-9` resolved; `q-2`'s rotation is right and
      what remains of it is the subject-role question.

      **⚑ AND THE TRUTH SLOT UNDER AN ATTITUDE — RULED 2026-09-17: the rows KEEP their truth.** The
      station emptied the truth slot of anything under an attitude (`quoted_under`, and the `ccomp`
      path). **The drill never has**: `dere-1` carries a cat at truth 1.0 under «he thinks», `dere-3`
      a marriage under «he wants», `aw-11` a hungry cat under two nested attitudes. The PREFIX is
      what keeps a row out of the world; the TRUTH SLOT says what the holder does with it — and
      blanking it flattened three speech acts the format otherwise separates for free:

          John said "The sky is green."      the holder ASSERTS    truth = 1.0   (q-8)
          I asked Anna "Where do you live?"  the holder ASKS       an OPEN box   (q-7)
          John said "Close the door!"        the holder WANTS      truth = None  (aw-21)

      It matters downstream and not only formally: «John told me X» (I may believe it if I trust
      John), «John asked me X» (I should answer) and «John told me to do X» (I may act) are three
      different things to the brain, and one blanked slot made them the same row. *A lone deviation
      in code against the format's own gate is the deviation that moves* — the same ruling as
      `topic`/`patient`, eight days apart.

   *It touches E3b: «John» and «Marie» must become individuals before a rotation can NAME its
   target. The mechanisms are separable — a «you» can rotate to «the person addressed» without
   knowing who that is — but a rotation that cannot name its target is half an answer.*

2c. **⚑ A POLAR QUESTION NEVER OPENS ITS TRUTH** *(found 2026-09-17, by fixing the truth slot in
   2b — and it is NOT a person-axis task, which is why it has a number of its own)*. «Is the cat
   hungry?» compiles at **truth 1.0**, where the schema's own docstring says it *«has every box
   bound and its truth OPEN»*. Wh-questions open a BOX and are fine; `whether` opens the truth from
   its marker row; **the bare AUX-fronted polar has nothing that fires.** It was invisible while
   everything under an attitude was blanked anyway. A MOOD question, and the witness is written.
   *Making a slot mean something is how you find out who was not filling it.*

3. **The renderer** — zip → faithful scaffold, same lib (req 9).
4. **The confidence scalar** — coverage + repairs bookkeeping (free), self-round-trip
   escalation-only (reqs 4, 6); calibration instance stubbed for E5.
5. **The drill, automated** — E2's fifty sentences as the acceptance gate (req 10), run in CI
   fashion by tooling. *The drill is the FORMAT's gate and stays one — it proved tkzip can HOLD the
   world. It is not the STATION's gate: it says nothing about whether stanza's skeleton was read
   correctly.*
5b. **⚑ THE UD GATE — the station's real acceptance test** *(the Captain, 2026-09-15)*. Every one of
   **UD's 37 dependency relations and 17 POS tags**, handled consistently against **UD's own
   published examples** (`universaldependencies.org/u/dep/`, `/u/pos/` — 67 relations have a global
   page with examples). Both ends are CLOSED — 37 relations in, 18 tkzip roles + 10 operators + the
   five-element prefix out — so **the mapping table can be COMPLETE, and it is E3's real
   deliverable.** `case` is the relation that fills task 0's empty `compiled` field.
   *Why UD and not more of our own sentences: our fixtures encode OUR habits. UD's examples are
   strangers'. And stanza is chosen precisely because it TARGETS this standard — «close enough» is
   a measurement owed relation by relation, not an assumption carried.*

   **DONE 2026-09-16** (record `202609161050_the-gate-reaches-every-relation.md`). Two changes, and
   the first had to come before the second:
   - **THE GATE SCORES THE ZIP, NOT THE TABLE.** It was measuring half a station — its own docstring
     said «roles that come from a relation are not its job yet» — and the relations still unreached
     were almost all COMPILER questions. It needed **`Compiled.placement`** first: a per-token record
     of WHERE each word went, which is also exactly what req 4's confidence scalar reads and what
     req 3 means by a reading that can be handed back. **It found four defects before one new case
     was added**: three words «reaching no part of the zip» in sentences that compiled at 100%
     (covered with nothing said about where they went), «the cafe up beside the lookout» compiled as
     a POSSESSOR, «out of the box» defaulting to `complement` and throwing its marker's meaning away
     while keeping its spelling, and a vocative merely UNPLACED rather than deliberately dropped.
   - **EVERY ONE OF THE 37 IS REACHED.** 43 cases · **30 answered · 0 WRONG · 13 abstained**. 34
     relations have a case, **2 do not arise in English** (`clf`, `dislocated`) and **1 is UD's own
     abstention** (`dep`) — three states reported apart, because folding «not in English» into «not
     yet reached» makes the coverage figure a lie in the flattering direction.
   - **AND A SECOND PROVIDER MEASUREMENT, which req 2 asked for**: stanza produces **15 of the 18**
     relations UD publishes on these sentences. The three it does not — `goeswith`, `orphan`,
     `reparandum` — are ONE FAMILY: a typo, a gapping, a self-correction. **The station will never
     meet them labelled from this provider**, so building handling for them would be building
     against a label that never arrives.
   - The corpus now splits into a **ratchet** (the 25 earlier cases: 22 whole, 98.4%, and they may
     never get worse) and a **frontier** (the 18 added: 6 whole, 76.6%, and it is meant to climb).
     One averaged figure would let a regression on the old be paid for by a gain on the new.

6. **THE PLACEMENT FLOOR — inherited from E1c/E1d, and measured before it was handed over.** The
   station is where a placement is first trusted or refused: a word it does not know reaches the
   geometry through `place()`, which returns each reading with a verdict. That verdict currently uses
   **the BASE's floor**, and the base's floor was fitted on base-to-base cosines where p90 is +0.000
   — a population where +0.15 is a high bar. It is not one here: a placed sense's top-1 cosine has a
   median of **+0.484** (relations) / **+0.228** (distribution), so +0.15 reads NEAR for **99.7%** and
   89.7% of them. **A floor that says NEAR to everything is not a floor.** The sense layer needs its
   own, fitted its own way — with the same discipline `db/0002` and `db/0007` were: measure the
   population first, then put the threshold in the MIDDLE of a real gap, never on a wall. *And the
   bar it is fitted against has to be built: the base's 37 pairs are base-to-base and say nothing
   about placements.*
7. **The unplaced sense** — 3.1% of senses are placed by neither half, and the station ABSTAINS on
   them. The count is in the manifest, so it is predictable rather than surprising.
8. **⚑ THE FRAME/KNOWLEDGE AUDIT — the epic's closing act** *(the Captain, 2026-09-16, and the first
   of these)*. *«At the end of E3 we should go through everything we have done and double check if
   something we consider frame should be moved in the knowledge kingdom.»* Walk every set this epic
   put in a `.py` file and re-ask the FRAME test on it: is it LAW, or a revisable fact about a
   language, a resource or the world? **The rule's own lesson is that the answer is not obvious from
   inside the decision** — choosing our own inventory and hard-coding it relocates the rigidity
   instead of removing it — so each one is discussed, not self-marked.

   **The candidates already on the list, named as they were built rather than remembered at the end:**

   | in code today | why it is suspect |
   |---|---|
   | `RELATION_FILLS_ROLE` (`compile.py`) | its own comment says `nsubj → agent` and not «agent or experiencer» is a JUDGEMENT the station declines to make. A judgement is knowledge |
   | `CLAUSE_DEPS` (`compile.py`) | **`xcomp` is deliberately absent**, argued at length — «nobody asserts that you swim». An argued exclusion is a ruling, and a ruling is a row |
   | `UD_DEP_TO_ROLE` (`closed.py`) | the roles are BEST-FIRST, and an ordering is a claim about which reading is commoner in English |
   | `UD_POS_TO_WORD_CLASS` (`closed.py`) | «UD's `AUX` covers our auxiliaries AND our modals» is a statement about English, not about UD |
   | `CLAIMED = 1.0` (`compile.py`) | a threshold in code is the shape `db/0002` and `db/0007` exist to refuse |
   | `UD_DEP_SETTLES_ROLE` (`closed.py`) | *defensible as frame* — every entry is a relation whose UD definition NAMES the role. But the READING is ours, so it is argued, not assumed |
   | `DEPS_THAT_COMPILE_TO_NOTHING` (`compile.py`) | added 2026-09-16 and put on this list in the same commit. `{"vocative"}` — and «a vocative is addressing, not content» is an E2 RULING, which is a row |
   | `ADVERB_DEPS` (`compile.py`) | added 2026-09-16, same day, same list. `{"advmod", "discourse"}` — weaker than the two above (it selects WHERE to look rather than ruling what a thing means) and the same shape |
   | **`SAYING_VERBS`** (`utterance.py`) | added 2026-09-16 and listed here in the SAME COMMIT. Nine verb keys in a frozenset, and **req 55 already rules the replacement**: *«attitude verbs are open, so the classification is nearest-anchor geometry over a small anchor set and never misses the verb nobody thought of»* — E4 owns that geometry. Reached only ACROSS a sentence boundary; the in-sentence path asks the joiner's own `asserts: matrix` row, which is curation doing it properly |
   | `POS_LETTER`, `UD_POS_TO_WORDNET`, `NOUN/VERB_SUPERSENSES` | *defensible as frame* — correspondences between two published closed vocabularies, and the supersense inventory is checked against the corpus every run |

   **Done when** every row of that table has a ruling and a home, and the ones that moved are a
   migration.

**Done when:** the drill bar passes through the real lib (parse AND render), **every UD relation and
POS tag is read consistently against UD's own examples**, clean input costs one parse, confidence
orders the drill's failures sensibly, **a placement is judged by a floor fitted to placements**, and
**a pronoun under a point of view resolves to that POV's participants** (task 2b).

*NOT owed by this epic: named individuals. A proper noun reaching a box with an identity is **E3b**,
opened 2026-09-16 — E3 closes with names unresolved and honestly marked, which is req 8 working.*

---

## E3b — The name *(named individuals: recognition, identification, and the first micro-nn)*

**Opened 2026-09-16 by the Captain, reopening a hole E3 had parked.** The ambiguous markers closed
with two errors and both were «Anna» — WordNet holds the spelling only as an Indian coin. I called it
«the named-individual hole, which already has its answer waiting». **He refused the parking and
widened the scope**: names are a point of their own, and they run from *is this a name at all* to
*which Paris did he mean*. Record: `docs/parser-compiler/202609160959_the-name-question.md`.

**Scope:** everything between a proper noun on the wire and a box whose head is a named individual.
**Not** in scope: what the individual MEANS to him — that is the KB's, and the heart's target table
is already keyed by uid.

**Answers to:** parser-compiler req 16 · micro-nn reqs 1–4, 7, **9** (the admission criterion, which
this epic is the first case of).

**Where it sits:** after E3 closes, and it may run BESIDE E4 — the evaluator does not wait on name
resolution, and a zip with an unresolved name is still a zip. It should be in before **PS1**, because
a proof slice on a real sentence will contain a real name. *(A judgement call, revisable: the
alternative is to let PS1 run with names unresolved and see what actually breaks.)*

> **AND IT CARRIES E5's MACHINERY — the Captain, 2026-09-16** *(open question 15, answered)*:
> *«Bring E5 forward because it is propaedeutic to closing the E3 name hole. So E5 remains where it
> is, but the machinery (micro-nn abstraction) should go in E3b.»* **The epic stays where it is and
> the ABSTRACTION lands here**, as task 5a. That is the better half of the trade in both directions:
> the name hole cannot close without a net, and a framework whose first instance arrives with it is
> a framework that has met a real case before it is declared general — which is the failure mode
> «one abstraction, many instances» is most exposed to.

**THE INHERITANCE IS LARGE AND IT IS TRANSCRIBED, NOT REMEMBERED.** tk1 built most of the curated
half and recorded its failures in code comments that no roadmap points at. The chapter note
transcribes them; the short version is that **the places table is an asset and the stakeholders are
biography**, and those go to different epics — the Captain's own boundary of 2026-09-15.

**Tasks**
1. **IS IT A NAME?** — stanza's NER against spaCy's, measured on the same text, with UD's `PROPN` and
   the casing as separate weak evidence. **Casing is an indicator and not a test**, and tk1 proved it
   from both sides: its gate admitted OOV gibberish that spaCy labelled `GPE` (repaired with a
   `has_vector` guard) and refused «kotekino is my creator», which is lower case and perfectly known
   (repaired with a second, recognition-only path). Those two are the bench's first cases.
   *This does not reopen req 2 — entity recognition is not a UD task and has no UD relation, so a
   second model here is not a second opinion on a dependency parse.*
2. **A NAME OF WHAT? — OUR KINDS, AND THEY ARE ROWS** *(the Captain, 2026-09-16, req 17)*. The
   inventory is ours and it lives in the db, not in code: *«with our inventory as db we can modify it
   keeping the logic — everything is KB. If we rely on a third party we lose this ability.»* So two
   tables and no enum — **the kinds** (person · organization · place · work · event · none, each row
   naming the type-centroid sense it carries and which lookup it triggers) and **the label map**
   (an NER label → a kind, one row each, so a model's new label is a migration and not a release).
   tk1's nine mappings are the map's starting position: `PERSON → person.n.01`,
   `ORG → organization.n.01`, `GPE/LOC/FAC → location.n.01`, `NORP → group.n.01`,
   `PRODUCT`/`WORK_OF_ART → artifact.n.01`, `EVENT → event.n.01`.
   **Prominence is NOT a kind** — it is a scalar on the resolution, and it is what task 5 ranks.
   *A consequence to hold on to: a kind that is a row cannot be an enum the compiler branches on, so
   the box carries it as a string. The precedent is `ClosedClassDoc.word_class`, which is a string
   and not an enum for this exact reason — «a class that needed a code change to exist would put the
   table back in code».*
3. **THE PLACES TABLE, INHERITED** — **measured against the live v1 body, 2026-09-16: 4,674,701
   rows**, two containment chains (`path_admin` political · `path_geo` physical), a **`type` column of
   EXACTLY 21 values** which is an `is_a` statement, a second closed axis `category`
   (administrative · geographical), coordinates on **99.9%** and `physical_features` on **54.9%**.
   Both ends closed again, so the type → sense map can be COMPLETE. **Read lazily and never
   materialized** — `places.py`'s own words, and the cascade-noise ruling applied once already at
   this exact table. It goes on the inheritance ledger beside the curated senses.
3b. **THE NAMES LIST, INHERITED — AND IT CANNOT BE A TEST.** `tokeniko.names`: **21,975 rows, one
   column**, a flat roster of personal-name spellings. It holds `anna` and would fix the marker
   bench's two errors on the spot. Measured the same day: **28.1% of it is also a place name** (6,170
   — `paris` among them) and **15.2% is also a WordNet common noun** (3,333 — `abbey`, `ace`,
   `acacia`). Membership is EVIDENCE with a 28% collision rate, never a test, and that measurement is
   the sharpest argument for task 5. *(It also needs a cleaning pass: the string `TRUE` is in it, a
   spreadsheet boolean that survived ingestion.)*
4. **HAVE I MET IT?** — recognition against a names table, which is a different question from
   identification and is the one that carries identity. tk1's preference order is inherited whole:
   the individual scoped to THIS talker's context, else a participant (a real interlocutor with a
   global identity), else a unique individual from another context, and **genuinely ambiguous → never
   guess**. The MECHANISM is E3b's; the ROWS are biography and E9 migrates them — and there are
   **18 of them** (`tokeniko_mem.stakeholders`, measured 2026-09-16), so this half is small and the
   scale lives entirely in tasks 3 and 3b.
5a. **⚑ THE MICRO-NN ABSTRACTION ITSELF — brought forward from E5 by the Captain's ruling.** The
   lib (features → a ranking or a scalar in [0,1], online updates, weights as epoch-stamped db rows,
   deterministic per epoch — micro-nn reqs 1–4, 8) and the instance registry (declaration rows: input
   schema · output kind · reward source) with **the shared fence enforced STRUCTURALLY** — candidates
   in, ordering out, no candidate creation (req 7). *Reward plumbing is NOT here: the reward families
   arrive with E7 and E8, so this instance learns from the correction signal the station already has
   and the rest is wired later.* **Built to serve task 5 and generalized against it, never before
   it.**
5. **⚑ WHICH ONE? — THE FIRST INSTANCE, and the first admitted by micro-nn req 9.** «Paris» is a city
   in France and a town in Ontario; tk1 logged the problem («name lookup is not disambiguated by
   prominence, so homonyms resolve to whichever the knowledge base returns first») and never solved
   it. **It passes both of the Captain's tests**: curation can cover the places we have seen and never
   the next one, and the answer MOVES — what is prominent this year was not prominent last year.
   An instance declaration (input schema · output kind · reward source) against the framework task 5a
   builds, **ranking candidates the curated tables produced** — the places rows, the names roster, the
   stakeholders he has met — under the shared fence. **The 28.1% collision measured in task 3b is
   this task's brief**: the signals are strong and they contradict each other, which is exactly the
   split decision that cannot be curated.
6. **WHAT A NAME IS IN A ZIP** — a box whose `head` is a named individual: the **type centroid is the
   SEMANTIC content** and the **uid is the IDENTITY**, and the two never merge (the second standing
   law, and `plan.md`'s own «uid + type-centroid» for `kotekino` and `tokeniko`). Identity uids are
   `name@channel:talker_uid` and `docs/ideas.md` already flags the trap: a new channel mints a NEW
   individual unless it is deliberately bound.
7. **THE MARKERS GET THEIR THIRD READING** — `db/0012`'s selector reads a nominal's supersense, and a
   named individual has a type centroid instead. The day this lands, «went with Anna» becomes
   comitative because Anna is a PERSON, with no rule about Anna anywhere. **That is the acceptance
   test**: the two residual errors on the marker bench turn green without the bench being touched.

**Done when:** a name on the wire reaches a box with a type centroid and an identity, the kinds are a
closed set with a complete map, the places table is read lazily and answers containment, an unknown
or ambiguous name ABSTAINS rather than guessing, the first micro-nn instance ranks without ever
minting a candidate — and the marker bench's «with Anna» cases pass.

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
   *Amended 2026-09-14 — «dual read» here predates policy v11 and must not be read as a blend:
   **R DECIDES, D PROPOSES, and where R is silent the answer is ABSTAIN.** A stated cell decides
   before any threshold. «Both floors» remains right (NEAR floor + FAR ceiling) but they are R's
   floors; D has none, because D never issues a verdict. `space.similarity()` no longer exists —
   `read(a, b)` is the door, and it already names its source, which is what «source named in the
   derivation» was asking for.*
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

> **THE MACHINERY MOVED TO E3b — the Captain, 2026-09-16.** *«Bring E5 forward because it is
> propaedeutic to closing the E3 name hole. So E5 remains where it is, but the machinery (micro-nn
> abstraction) should go in E3b.»* **The epic stays here; the ABSTRACTION lands earlier**, because
> name resolution cannot close without it and a framework built for one real case is a framework
> that has met a real case. Tasks 1 and 2 below are therefore E3b's, and are listed here with a
> pointer rather than repeated — one item, one status, one doc.

**Tasks**
1. ~~**The lib**~~ **— BUILT IN E3b (task 5a).** Features → ranking/scalar; online updates; weights
   epoch-stamped in db; deterministic per epoch.
2. ~~**Instance registry**~~ **— BUILT IN E3b (task 5a).** Declaration rows (input schema · output
   kind · reward source); the shared fence enforced structurally (candidates in, ordering out — no
   candidate creation).
3. **Instance breadth** — E3b declares the first (name prominence, and the first admitted by req 9
   rather than at conception). This epic adds the rest: station confidence calibration (E3),
   evaluator search order (E4), and then the sites that need an organ — the heart jump, the
   figurative layer, the channel register, the mouth's coloring.
4. **Reward plumbing** — the intellectual and heart families wired to the instances; arrives with
   E7 (heart) and E8 (dialogue feedback), which is why it could never have landed with the lib.

**Done when:** two live instances demonstrably reorder/calibrate without ever changing a verdict,
**on a framework E3b already proved against one real case.**

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
   **THE LOG IS NAMED, and it is measured** *(2026-09-15)*: `tokeniko_mem.tkzipdebug` — **583
   journeys, 546 distinct, 529 never spent on E2's drill, and v1 read 209 of them WRONG (40%)**.
   Those 209 are the ratchet's hard half: not «everything v1 answered correctly» but everything it
   did not, which is the list v2 must not reproduce. Read them with
   `tools/journey_ledger.html` — grouped by phenomenon, carrying v1's own verdict and its own note
   on every mismatch. **They arrived here by the Captain's own catch**: the QM had proposed them as
   E3's derivation corpus, and they are memory inherited from tk1, which is this epic. They may
   still inform E3 as EVIDENCE; they are never its gate.
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
   cache, slow tick; deploy-by-migration runbook evolved from `body/tools/`.
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
  `tokeniko-tk1/docs/roadmap.md`, never here. tk1 stops growing; it keeps witnessing.
- **The multi-body horizon, open-world growth** (captain-hunches) — awareness only.
- **Anything the register doesn't hold** — the list is closed; extending it takes an argument.
