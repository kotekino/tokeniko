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
Verdicts: **NEAR ≥ +0.27 · FAR < 0 · ABSTAIN between.**

**Nine rulings, every one measured first and every one now a row** — v1 seeds/cuts · v2 seeds ruled
+ cap→rail · v3 relation weights + POS alphabet · v4 lemma scope `word` · v5 `antonym_inferred` /
`add_only` · v6 D's walk · v7 the dual read · v8 `structure=compiled` + mix 0.15 · v9 the verdict's
two edges. The two standing LAWS came out of this epic and bind everything after it: *where a closed
set may live* (frame / curation / open) and *content is defined, structure is compiled*.

**What E1 did NOT build — read this before assuming the dictionary is finished.** E1 built the
**BASE**: the frame the geometry is stated over. The resource carries **68,779 words and 120,475
senses**, and those ride ON the base (a sense holds a D-vector over base dimensions and consults R
through its sense key — tkzip req 11). **That layer does not exist yet and has no epic.** It needs
two decisions E1 deliberately left open: how a sense's vector is derived, and sense selection
(`senses="primary"` is kept and its rot is documented — `small` reading as «the slender part of the
back»). See `plan.md` § E1, «what E1 did not build».

*Inherited flags: `compass.n~compass.v` (+0.2668) is the POS collapse the NEAR floor is fitted to —
if it is ever resolved, the floor is re-measured and not inherited · `measure` and `vocabulary` are
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
