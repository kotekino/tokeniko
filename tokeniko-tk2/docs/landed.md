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
