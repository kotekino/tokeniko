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
