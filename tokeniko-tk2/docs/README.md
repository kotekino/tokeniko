# tk2 — the docs

*The status trio is `plan.md` · `roadmap.md` · `landed.md`; everything else is a CHAPTER — the
decision record for one part of the build, read in full before working on any item in it.*

**Every item has a nested, immutable id** (root `CLAUDE.md`): `E3.3.2.5` is the fifth thing found
under `E3.3.2`. The same id appears in `plan.md`, in `roadmap.md`, and at the head of every chapter
note that elaborates it (`*Roadmap: …*`). **A chapter folder is prefixed with the epic that owns it**;
its `requirements.md` opens with `*Serves: …*`, which lists every id it elaborates.

| folder | owned by | serves | renamed from *(2026-09-25)* |
|---|---|---|---|
| `E0-data-modeling/` | E0 — the keel | E0 | `data-modeling/` |
| `E0-datatier/` | E0 | E0 | `datatier/` |
| `E0-stack/` | E0 | E0 | `stack/` |
| `E1-dictionary/` | E1 — the dictionary at scale | E1 · E1b · E1c · E1d | `dictionary/` |
| `E1e-tooling/` | E1e — the tests, isolated | E1e | `tooling/` |
| `E2-tkzip/` | E2 — the format | E2 | `tkzip/` |
| `E3-parser-compiler/` | E3 — the station | E3 · E3b | `parser-compiler/` |
| `E4-evaluator/` | E4 | E4 | `evaluator/` |
| `E5-micro-nn/` | E5 — the instinct middleware | E5 · E3b.5.1 | `micro-nn/` |
| `E6-brain/` | E6 — the mind | E6 | `brain/` |
| `E6-rules/` | E6 | E6.1 | `rules/` |
| `E7-heart/` | E7 | E7 | `heart/` |
| `E8-senses/` | E8 — the voice and the ears | E8 | `senses/` |
| `E8-rag/` | E8 | E8.4 | `rag/` |
| `E10-body/` | E10 — the embodiment | E10 | `body/` |
| `E10-website/` | E10 | E10.3 | `website/` |

**The old names survive in two places, deliberately:** the applied migrations under `db/` (immutable
— their checksums are the ledger) and the past work orders in `.claude/briefs/`. Read `tkzip/…` there
as `E2-tkzip/…`, and so on down this table.

Also here: `charter.md` (the phase-1 record) · `carried-in.md` (what the tk2 filter moved off the v1
road) · `ideas.md`.
