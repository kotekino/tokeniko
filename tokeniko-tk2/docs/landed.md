# tokeniko 2 — LANDED

*What is done. Items move here from `roadmap.md` when they finish — moved, never copied. Phase 1
(conception — the sixteen requirement sets) predates this project root and is recorded in
`README.md` §9's register, not here.*

## E0 — the keel ✅ 2026-08-23 (five commits, one officer, one day)

- [x] **repo scaffold** — package `tk2` beside `docs/`; `db/`+`tools/` deliberately non-importable; closed dependency list in pyproject (python-dotenv admitted by ruling).
- [x] **write-class schema** — kb/param/logic declared by inheritance, undeclared models refuse to import; Provenance (mandatory once mixed) · EpochStamped (layer version) · Timestamped (wall clock) split.
- [x] **datatier core** — the guard refuses tk1 BY NAME ahead of the whitelist (holds even when whitelisted); all 13 ODM writers behind assert_writable, r-class locks underneath; migration writer = the second door (pydantic twin, raw pymongo, no toggle); r-cache with wholesale snapshot, monotonic clock, hot-loop floor.
- [x] **the twelve collections** — params (r) · heart_anatomy + micro_nn_instances (logic — the anatomy is ROWS, a new sphere arrives by migration, proven live) · nine kb tables (each write-class justified in its docstring); the instinct fenced by construction (no Provenance on the micro-nn pair); epoch-layer ruled NO COLUMN.
- [x] **migration runner + THE E0 GATE** — immutable applied-ledger (checksummed, written last); 0001 created the world in `tokeniko_tk2_body` (12 collections · 5 dotted params · 15-row anatomy · the newborn's levels); the gate log: ticks 1–12 read epoch=0, migration 0002 landed on the LIVE body, tick 13 read epoch=1 — no restart. 263 checks.

*Inherited flags: temperament baselines are 0.0 placeholders — who he starts out as is a Captain's
migration before E7 · E4 must confirm the «0 = unset» budget-param convention · `task body` runs
forever by default (`--max-ticks`/SIGTERM to bound).*

---

## E1 — the dictionary at scale ✅ 2026-09-10

*Sixteen commits (`34e43c8 → 0678054`). The base is built, sealed and on the body.*

- [x] closure engine (keys as law, ring boundary visible, policy fingerprinted) — `34e43c8`
- [x] inflection-collision fix (req 21) + stop list yields to membership — `fe73d40`
- [x] proper-noun/abbreviation refusal (`or`=Oregon out of the base) — `1e7cad3`
- [x] policy as rows — the mechanism (collection, bar ledger, manifest, offline snapshot) — `e480ccd`
- [x] policy as rows — the ruling: k=200, rail 25,000, closed classes as typed KB rows — `a6acefb`
- [x] R at scale + curation pipeline (Captain's hand on approve) — `f71baa3`
- [x] lemma scope ruled (v4) + inferred opposition ruled (v5) — `7da676f`
- [x] D at scale + the dual read ruled (min_shared 1 · derivational 0.45 · mix 0.5) — `b8f325e`
- [x] the bar grown 18 → 37 as rows; the closed-class filter and the mix re-ruled against it — `e1dbdd2`
- [x] the seal, the verifier, the map — a base can say «I am complete» — `a4b13f1`
- [x] acceptance floors ruled: NEAR ≥ +0.27 · FAR < 0 · ABSTAIN between — `0678054`
- [x] **THE BASE IS BUILT AND SEALED ON THE BODY** — 4,555 dims · R 51,564 · D 473,262

**What stands, in `tokeniko_tk2`** *(renamed at E1b; the table below already uses the new names)* — one sealed build, `config 9824ef46…`, policy v9, bar v2,
authorized and applied by the Captain 2026-09-10, read back whole by `tools/verify_base.py`:

| collection | class | what it holds |
|---|---|---|
| `dictionary_base_keys` | logic (r) | the **4,555 POS-split dimensions**, contiguous, sealed |
| `dictionary_base_relations` | logic (r) | **51,564 relation cells** — every one naming its relation(s), weight and source |
| `dictionary_base_distribution` | logic (r) | **473,262 gloss-overlap cells**, unsigned and symmetric |
| `dictionary_base_seals` | logic (r) | one row per (build, matrix): rows written, cells, content fingerprint |
| `dictionary_policy` | logic (r) | **nine versions**, a ledger — v1's fingerprint still names what v1 measured |
| `dictionary_bar` | logic (r) | the acceptance bar, **37 pairs across two versions**, append-mostly, epoch-stamped |
| `language_closed_classes` | logic (r) | **383 typed rows** — English's closed classes, replacing tk1's four code lists |
| `dictionary_builds` | logic (ledger) | the manifest: which policy and bar version+fingerprint a build was measured against |

**The reading:** 68,779-word lexicon → 3,172 words → 4,555 dimensions, `stopped=depth`. Dual read
**R + 0.15·D = 276 of 336** NEAR/FAR comparisons ordered correctly, local order 5/8, 6 mute of 37.
Verdicts: **NEAR ≥ +0.27 · FAR < 0 · ABSTAIN between.** *(E1's number, and history: +0.27 → +0.28 at policy v10 → **+0.15 at v14**, each re-fitted to the base that existed. See E1d.)*

**Nine rulings, every one measured first and every one now a row** — v1 seeds/cuts · v2 seeds ruled
+ cap→rail · v3 relation weights + POS alphabet · v4 lemma scope `word` · v5 `antonym_inferred` /
`add_only` · v6 D's walk · v7 the dual read · v8 `structure=compiled` + mix 0.15 · v9 the verdict's
two edges. The two standing LAWS came out of this epic and bind everything after it: *where a closed
set may live* (frame / curation / open) and *content is defined, structure is compiled*.

**What E1 did NOT build — read this before assuming the dictionary is finished.** E1 built the
**BASE**: the frame the geometry is stated over. The resource carries **68,779 words and 120,475
senses**, and those ride ON the base (a sense holds a D-vector over base dimensions and consults R
through its sense key — tkzip req 11). ~~**That layer does not exist yet and has no epic.**~~ It needed
two decisions E1 deliberately left open: how a sense's vector is derived, and sense selection
(`senses="primary"` is kept and its rot is documented — `small` reading as «the slender part of the
back»). **BOTH WERE RULED AND THE LAYER WAS BUILT: it became E1c**, below, the same day.

*Inherited flags: `compass.n~compass.v` (+0.2668) is the POS collapse the NEAR floor is fitted to —
if it is ever resolved, the floor is re-measured and not inherited. **IT WAS, AT E1d**: requirement
16 mined `derivational` at primary-sense resolution, `compass` fell to +0.0948, and the floor was
re-measured and re-ruled to +0.15 rather than inherited — exactly as this flag required · `measure` and `vocabulary` are
unruled BY DEFAULT rather than by decision (they were unobservable behind the old cap and are
observable now) · a transient `OperationFailure: Operation not permitted` appears in long live test
runs against the `tk-atlas` container and passes on retry.*

---

## E1b — the names, and one baseline ✅ 2026-09-10

*Ruled and executed the day E1 closed, for a reason the Captain named himself: «is the dictionary
complete?» is a harder question to answer when the collection holding the answer is called `base_r`.*

**The rename**, by the rule that every collection carries the component that owns it:
`dictionary_base_keys` · `dictionary_base_relations` · `dictionary_base_distribution` ·
`dictionary_base_seals` · `language_closed_classes` · `tkzip_derived_points` ·
`senses_channel_registers` · `heart_forecasts` · `heart_emotional_log` · `body_params`. The db
`tokeniko_tk2_body` became **`tokeniko_tk2`** — the name freed by dropping the 983-dimension
prototype that held it, superseded whole by the base E1 built.

**A rebuild, not a rename, and the reason is worth keeping:** mongo cannot rename a TIMESERIES
collection at all (`heart_emotional_log` is one), and moving a database is a copy in any case. The
cost was measured before it was chosen and it was **nothing** — every heart row read `0.0` with
`created_at == updated_at ==` the migration's own timestamp. He had been created and had never
ticked; there was no biography to lose.

**Thirteen migrations became one baseline**, the originals in `db/archive/`. The ledger did not go
with them, because **the ledger was never the files** — all nine policy versions are written by the
baseline out of `db/data/declared_rows.json`, notes verbatim. What was given up is the SEQUENCE as
replayable steps; it survives in git and in the notes, and the Captain took that price knowingly.

**Proved, not asserted:** config fingerprint `9824ef46…` reproduces exactly; every collection
compared row by row against the old world before it was dropped — **identical, all of them**; the
base rebuilt and read back WHOLE. The matrices' own content fingerprints DID move, and that is
correct: a matrix's name is inside its content hash, and the name changed.

**Also landed:** the **third standing law** — *a name is written for the human who reads it cold*
(`plan.md`, before the epics) — and the guard's special case for the prototype's database retired.

*Inherited flags: `db/archive/` must stay readable and never runnable — `discover()` does not descend
into it, and a test holds that · `db/data/declared_rows.json` is 744 KB of curated rows and its diff
is the audit trail: a changed NOTE shows there as plainly as a changed value.*

---

## E1c — the sense layer ✅ 2026-09-10

*The dictionary's second floor, and the half E1 did not build. Ruled before E2 on the Captain's
word: E3's parser resolves a word to a SENSE, and discovering that mid-station would be expensive.*

**What stands, in `tokeniko_tk2.dictionary_sense_vectors`** — one row per sense, sealed like a
matrix, read back WHOLE:

| | |
|---|---|
| senses | **120,475** |
| placed | **116,725 (96.9%)** |
| cells | **816,309** (693,811 distribution + 122,498 relations) |
| unplaced | 3,750 (3.1%) — no gloss word and no relation reaches the base |
| build | ~4½ minutes; the base itself unchanged at `9824ef46…` |

**The ruling, in one sentence: THE BASE IS THE FRAME, THE SENSES ARE THE CONTENT.** A base dimension
is one word under one part of speech reading WordNet's first synset. `small.n` reads «the slender
part of the back» — called a defect all through E1 — and it stops being one here, because the other
readings finally have somewhere to live. The base's 4,555 dimensions cover 17,257 senses at a mean of
3.79 apiece; 73% of what a dimension means was being discarded until this table.

**Two vectors, mirroring the two floors**, so one law reads both. The `relations` half is the point:
WordNet states relations per SYNSET, and collapsing synsets to POS keys is what lost them —
`bank.n.01` reaches `slope`, `bank.n.02` reaches `financial institution`, `bank.n` is both at once
and reaches neither cleanly. Measured before it was built: the gloss reaches 3.41 base dimensions and
is empty for 5.3% of senses; the relations reach 0.86 and are empty for 54.1%. Neither alone places a
sense.

**Never square, and the row's shape is what enforces it** (tkzip req 11): a sense's cells are BASE
DIMENSIONS. 120,475 × 4,555 is half a billion possible cells; senses×senses would be **14.5 billion**.

**`senses="primary"` stands for the base**, now with a reason. Both alternatives were measured:
`senses="all"` triples the key space and collapses the local order to 1/7; the UNION of a dimension's
senses buys +5 on global order but **buries 15 stated oppositions**, lifts every FAR control and
flips `land.v~leave.v` positive — a thirteen-word vector shares words with everything.

**The distribution vector is an indicator and says so.** Scoring it as an overlap was tried first:
94.8% of cells landed on the cap anyway, the same saturation that halved D's gate at T4, and the 5%
that varied varied by definition LENGTH — a fact about prose, not about meaning. The `weighting` seam
is kept so a later `idf` ruling makes the cells stop being flat.

*Inherited flags: an **unplaced sense** (3.1%) is one the station will ABSTAIN on — the count is in
the manifest so it is predictable rather than surprising · the **acceptance floors are the base's**,
measured over base-to-base cosines, and whether a sense-to-base reading is judged by the same numbers
is E3's question · `dictionary_builds` gained a `build` field: the T5 finding that a manifest could
not name its own rows became real the moment two builds shared one policy, and the two pre-fix rows
are left in the ledger because a ledger records what happened.*

---

## E1d — the audit's repairs ✅ 2026-09-14 *(bar 13 → 19 of 37 decided, 0 wrong)*

*It exists because at E2's close the Captain called in a parked order — «go through ALL the docs of
`docs/<chapter>` and see if we missed something in the old requirements» — and because of how he
framed the audit: **«if we ruled in some direction, it is not relevant. What is relevant is the final
status, how much it differs from all the original requirements, and what we can do to fix.»** The
`docs/E1-dictionary/` audit measured all 21 requirements against the sealed base: **11 clean · 6 partial
· 2 LOST · 1 contradicted by construction · 1 superseded.***

- [x] **the audit itself** — 21 statuses corrected in the chapter (`202609141115_the-e1-audit.md`). What it found: **req 2 «eat stays near food» was marked PROVEN at +0.405 and read +0.048** — their glosses share nothing, because D measures what two definitions SHARE and the real relation is that eat's definition NAMES food · **req 10 said «never blended into one float» and the reader returned `cos(R + 0.15·D)`** · **req 20's two hand-approved curated edges were GONE**, zero curated cells in the base, because a curated edge was an OUTPUT of a build and not an INPUT to one.
- [x] **T2 — SEPARATE READS** (policy v11) — R decides, D proposes, ABSTAIN when R is silent. Measured first: where R is silent, D provably cannot tell a declared NEAR from a declared FAR (`eat~hungry` 0.338 against `bed~cause` 0.326). `space.similarity()` DELETED — a function returning one number is what req 10 forbids. `thick~thin` and `push~pull` recover their FAR.
- [x] **T3 — `gloss_reference` mined into R** (policy v12) — «A's definition NAMES B», weight 0.9, reciprocal 0.54, and **a STATED CELL may decide** (req 19, honoured at last; only UNAMBIGUOUS references decide). **Requirement 2 CLOSED.**
- [x] **T4 — curated edges are INPUTS** — `dictionary_curated_edges`, append-mostly, consumed by the build, and a build **REFUSES** when an approved edge names a dimension the base no longer has. The structural fix for req 20: an output gets regenerated, an input survives.
- [x] **T5 — the two lost edges restored** (`db/0005`).
- [x] **REQUIREMENT 16 — `derivational` at primary-sense resolution** (policy v13) — its own proposed fix was **measured impossible**: a weight is a monotone rescale, so `compass` (FAR) sits above `cause` and `buy` (NEAR) at every scale. The defect was a **resolution mismatch** — a dimension IS its primary sense, but `derivational` was mined across every sense of the word. At the right resolution WordNet already separates all seven declared siblings, no threshold, 0% unanswerable over 1,626 pairs. *The QM's own first hypothesis failed too — D separated the seven by 0.020, which lands on the population median across all pairs; seven pairs were thin evidence and the bench existed to say so.*
- [x] **APPLIED, REBUILT, RE-MEASURED, RULED — on the body** — `0003`–`0006` applied; base rebuilt as **`969766250c02`** with the sense layer and read back WHOLE against all four seals; membership unchanged at 4,555. **`db/0002`'s order was followed this time**: rebuild, then measure, then rule.
- [x] **NEAR floor re-ruled +0.28 → +0.15** (policy v14) — the floor governs ONE gap, `compass.n~compass.v` FAR +0.0948 below and `walk.v~run.v` NEAR +0.2116 above, and 0.15 is the **middle** of it. The floor it replaced sat 0.0079 above a FAR pair and failed the first time the base moved.
- [x] **R PROPOSES, AND THERE IS NO FALLBACK** — brain req 12 said «memory proposes by cosine» and never said WHOSE. Benched: **D 5.9% precision@10 with 36.6% junk · R 28.7% with 9.8%**, and **no variant of D helps** (direct cell 4.2%, `min_shared=2` 4.7%, uncapped 6.3%, idf 6.0%). The cause is measured — D's cosine asks «which common gloss word do you contain», `eat.v` shares 49 of its ~50 columns with `lead.v` on the word **«take»**, and 62% of D's cells sit at the cap. Where R is silent (14 of 4,555, 0.3%) **nothing is proposed**: the fallback removed was offering cosines of +0.000, `argmax` over zeros. *This also confirmed the 2026-08-25 idf rejection at a second and different gate.*
- [x] **A SENSE IS PLACED BY WHAT IT STATES** — R first, D where the sense states none, **and the placement names the half**. Deliberately NOT the proposer's rule: relations reach 56.3% of the out-of-base senses `place()` exists for against the distribution's 94.5%, and D still answers 18.8% hit@5 — so the honest move is to LABEL the weaker answer, not refuse it. And a projected sense is ranked **in the half it came from**: ranking it elsewhere makes its `source` label FALSE, and measured worse (15.6% prec@5 against 13.3%).

**Two bugs found by the work rather than by a test:** `MatrixStore.drop()` never covered the sense
layer, so dropping the superseded build left **120,475 orphaned sense rows** under a build the
verifier could not even list · and the build tool's default report still scored the pre-v11 blended
reading, printing `mental.a~physical.a` — a declared FAR with a stated antonym — at **+0.105**. Both
fixed; the tool now scores through the engine's own reader and `--floors` works under separate reads.

*Four more found en route: `closed_forms(None)` broken since `0002` landed · `db/0004`'s first draft
silently un-declared six rows · `assert_coherent` fired on its own success (R has two miners now) ·
and D's cosine is «do these share NEIGHBOURS», not «does one name the other».*

**Requirements 2, 10, 14, 16, 19 and 20 are closed — in code AND on the body.**

*Open, named rather than left to be discovered: **D's neighbourhood cannot be tuned** and its honest
content is the DIRECT CELL, first-order evidence rather than a neighbourhood
(`202609141853_d-cannot-propose.md`) · **tkzip req 11 is flagged in its own chapter** — it assumes
retrieval is topical cosine over the D-side geometry, and that geometry cannot rank · and **the
acceptance floors are the BASE's**, fitted on base-to-base cosines where p90 is +0.000: applied to
sense-to-base placements the same +0.15 says NEAR to **99.7%** of relations-placed senses and 89.7%
of distribution-placed ones, so it does not discriminate in that population at all. **Carried to E3**,
which is where `plan.md` said that question belonged before it was measurable.*

---

## E2 — the format ✅ 2026-09-14 (tkzip v2.0, FROZEN)

*Limit B dies on paper before any code — and it did, in seventy-eight sentences. Six tasks, all run
in the Captain's Socratic shape; from task 2 onward under his standing instruction: **be as pedantic
with core design as with deploys — bench first, candidates second, no recommendation before the test.***

- [x] **the role inventory — 17 boxes, FRAME** — cut from VerbNet (29 roles / 429 classes), PropBank (112,917 annotated sentences) and FrameNet (1,221 frames), then cross-checked against the Captain's own first draft, which already had `comitative` — a box neither computational inventory carries. Ruled **named and verb-independent**: PropBank's `ARG2` means recipient for *give* and substance for *fill*, which would compare Anna against water. Settles OQ2 — passive normalizes to deep roles, topicality survives as one non-geometric marker. **No catch-all slot, ever**: the Captain refuted the QM's typed `other` as «the db option by the back door».
- [x] **named rows & scope — the collapse** — his rule: *collapse into math everything we can, into fields or variables what remains.* **Nothing survived as a relation.** CAUSE is `IMPLY` read with the theatre's arrow (premise stated, not assumed: *in a deterministic world a cause is what implies its effect*); PURPOSE is POV(want) + IMPLY; RESULT goes with them. «because» and «if» are one IMPLY separated by **assertion status**; «only» converts IMPLY→EQ and is a marker word, a KB row. **The operator set is the ten non-degenerate truth functions — frame, closed by mathematics, never trimmed to what English marks.** Row order = scope order, with a five-element prefix. OQ3, OQ5, OQ6, OQ8 answered.
- [x] **binding states & moods — the largest collapse** — **mood is not a field.** Question = something OPEN (a box, or the row's TRUTH for polar questions) · imperative = POV(want) over an unasserted row · supposition = POV(suppose), which heart 16's imagination gain reads · forecast = a future theatre (heart 17 verbatim) · irony leaves for the figurative layer. A question and an equation are the SAME zip — the Captain's own 2026-08-11 ruling, found by reading the notes. Net addition: binding state (`BOUND · OPEN · EMPTY`), a PRIOR on open slots, and the record's sixth field.
- [x] **confidence & provenance — an audit that added one field** — `parse_confidence`, one scalar per zip and a slot, so it may be EMPTY. Provenance, `derived_by`, `original` and forecast resolution are all document-level and were all built at E0. Two findings handed to `data-modeling` and `datatier` (req 7 each) rather than decided inside E2.
- [x] **storage (OQ9) — decided by measurement** — mean 2.59 roles per row of 18 slots, so **~80% of every row is EMPTY**; sparse, and fixed arity is a property of the schema. **The KEY is the truth, the VECTOR is an epoch-stamped cache** (dictionary req 13) — affordable because E1c's sense vectors average 6.78 cells of 4,555. **~60× smaller than v1 per sentence.** The consequence that matters: a dictionary rebuild invalidates only the cache, so **E9's translation night is for a SCHEMA change and never for a new base.**
- [x] **⚑ THE DRILL — 78 sentences, 97.4% no-abstention, 0 silent-wrong, BAR MET** — bar and scoring rules declared and committed *before* the drill existed (`1a68337`). All 28 sentences drawn from his own stored journeys zipped clean. **Three schema changes forced**, each named with the sentence that forced it: `direction` (the 18th role — «He looked up») · `scopes` on prefix rows («software can be minds and humans must be minds») · `Ref` («the result of perception and learning and reasoning»). The only abstention is **`almost`**, on two witnesses, amending req 23.
- [x] **tkzip FROZEN at v2.0** — `tk2/tkzip/schema.py`. Changes from here are migrations, never edits.

**The world it can now hold:** «my cat is cute» is *cat + cute, no verb* — his first draft verbatim ·
«every man loves a woman» is two zips · de re and de dicto are two zips · «as a doctor I disagree; as
a father I understand» is not a contradiction · a passive and its active differ by one non-geometric
marker · and «the cat sleeps» stores in **130 bytes**.

*Two method rulings came out of this epic and now govern the project: **the chapter docs are the
decision record** (`CLAUDE.md`, after the QM rebuilt the role inventory without reading the Captain's
own draft — «an origin that cannot be read is not documentation»), and **pedantry applies to
direction, not only to operations** (PRIO 1 — bench first, state costs both ways, never let «what the
next layer needs» decide what the frame is).*

*Open, named rather than left to be discovered: **`almost`** has no home and the format says so ·
the derived point's DENSITY follows from a composition operator that is not yet defined for all ten
(req 43) · whether a zip is EMBEDDED in its document is data-modeling's call · and the drill's
«to / toward» cluster left `direction`'s marker semantics (arrival entailment) to E3's closed-class
rows.*
