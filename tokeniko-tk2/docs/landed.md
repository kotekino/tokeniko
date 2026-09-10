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

**What stands, in `tokeniko_tk2_body`** — one sealed build, `config 9824ef46…`, policy v9, bar v2,
authorized and applied by the Captain 2026-09-10, read back whole by `tools/verify_base.py`:

| collection | class | what it holds |
|---|---|---|
| `base_keys` | logic (r) | the **4,555 POS-split dimensions**, contiguous, sealed |
| `base_r` | logic (r) | **51,564 relation cells** — every one naming its relation(s), weight and source |
| `base_d` | logic (r) | **473,262 gloss-overlap cells**, unsigned and symmetric |
| `base_seals` | logic (r) | one row per (build, matrix): rows written, cells, content fingerprint |
| `dictionary_policy` | logic (r) | **nine versions**, a ledger — v1's fingerprint still names what v1 measured |
| `dictionary_bar` | logic (r) | the acceptance bar, **37 pairs across two versions**, append-mostly, epoch-stamped |
| `closed_classes` | logic (r) | **383 typed rows** — English's closed classes, replacing tk1's four code lists |
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
