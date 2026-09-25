# tooling — REQUIREMENTS

*Serves: `E1e` — the ids of `roadmap.md` / `plan.md`*

*The workshop. Distillation session 2026-08-23 (author's ruling: matches tk1, more or less). One line
each.*

1. **Since dev IS writing db, tooling is where development happens** — seeding, curation, migration scripts are the primary build artifacts, not side utilities.
2. **The generation split is inherited** — `scripts/tk1/` · `docs/E1-dictionary/origin-prototype/` · `body/tools/`; a tool names its generation and its db.
3. **Instruments are sandboxed by the guard** (datatier req. 4) — read-only on the body, rw only on their sandbox; the guard is never weakened.
4. **Policy before results** — an instrument's config (seeds, weights, bars) is declared before the run and never edited after seeing the outcome (the PAIRS law, made general). **[THE TEST GATE, RULED 2026-09-22.** The Captain: *«tests must be minimal for the portion of code the coding is doing»*. **A** the gate per commit is the broad-short test (`pytest -m spine`, one minute, a spine through every module) plus the full tests of the SECTION being committed; **B** the full suite runs ONLY on deploy and ONLY on the body, as tk1 does it — the machinery does not exist yet and the clause is written ahead of it deliberately, while its effect now is total: we do not run the full suite; **C** a test that answers a QUESTION is always welcome and is never a gate. *The full suite had reached two hours, almost all of it one defect — `Migration.load` re-executed the module every call, so the closed-class chain 0008→0031 re-ran everything beneath each level and `standing_closed_classes()` cost 186s. Memoised: 0.2s. Every migration we wrote had been making every station test slower.* The rule lives in the root `CLAUDE.md`; `tokeniko-tk2/CLAUDE.md` carries only the commands and the section map. Record `202609220900_the-test-inventory.md`.]**
5. **Gated writes are the Captain's hand** — `--apply`-class flags run only in the main session with his recorded yes; officers propose, never approve.
6. **Observability lives here** — probes, bars, maps (ship him things to look at); the mind-monitor's engine-side feeds are tooling, their public face is the website's.
