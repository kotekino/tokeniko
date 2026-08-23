# tooling — REQUIREMENTS

*The workshop. Distillation session 2026-08-23 (author's ruling: matches tk1, more or less). One line
each.*

1. **Since dev IS writing db, tooling is where development happens** — seeding, curation, migration scripts are the primary build artifacts, not side utilities.
2. **The generation split is inherited** — `scripts/tk1/` · `scripts/tk2/` · `scripts/body/`; a tool names its generation and its db.
3. **Instruments are sandboxed by the guard** (datatier req. 4) — read-only on the body, rw only on their sandbox; the guard is never weakened.
4. **Policy before results** — an instrument's config (seeds, weights, bars) is declared before the run and never edited after seeing the outcome (the PAIRS law, made general).
5. **Gated writes are the Captain's hand** — `--apply`-class flags run only in the main session with his recorded yes; officers propose, never approve.
6. **Observability lives here** — probes, bars, maps (ship him things to look at); the mind-monitor's engine-side feeds are tooling, their public face is the website's.
