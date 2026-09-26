# tokeniko 2 — how to work in this project

*The repository-wide rules are in `../CLAUDE.md`: the vision as tie-breaker, the hierarchy rule,
documents-before-reference, pedantry on direction, frame-or-knowledge, the third kingdom, the status
invariants, and how we commit. **This file carries only what is specific to tk2.***

---

## READ THE CHAPTER BEFORE YOU ELABORATE ANY POINT IN IT

`docs/roadmap.md` is **the checkable mirror** — one line per item, no reasoning in it.
`docs/plan.md` carries the epics and their tasks.

**The reasoning that decides anything lives in `docs/<chapter>/`** — `requirements.md` plus the
dated `_notes.md` beside it, and any `origin-*.md`. That is not background reading and it is not
history: **it is the decision record.** A great deal of argument between the Captain and the QM is
in those files and nowhere else, including positions that were tried and refuted — which is exactly
the knowledge that stops a question being reopened badly.

Before working on any point, read the chapter it belongs to, **in full**. The chapters:

```
docs/E0-data-modeling/  docs/E0-datatier/  docs/E0-stack/  docs/E1-dictionary/  docs/E1e-tooling/
docs/E2-tkzip/  docs/E3-parser-compiler/  docs/E4-evaluator/  docs/E5-micro-nn/  docs/E6-brain/
docs/E6-rules/  docs/E7-heart/  docs/E8-senses/  docs/E8-rag/  docs/E10-body/  docs/E10-website/
```

**A chapter is prefixed with the epic that OWNS it** — where it was born; its `requirements.md` opens
with `*Serves: …*` for every id it elaborates. `docs/README.md` maps the old folder names (still in the
applied migrations, which are immutable, and in `.claude/briefs/`) to the new ones.

Plus `docs/charter.md` (the phase-1 record: the method, the inheritance ledger, the open-questions
ledger), `docs/carried-in.md` (what the tk2 filter moved off the v1 road) and `docs/ideas.md`.

**The rule that produced this file (the Captain, 2026-09-11):** at E2 the QM rebuilt the tkzip role
inventory from external corpora without reading the Captain's own first draft, which lived in a tab
of a binary spreadsheet and was linked from nothing. The rebuild independently re-derived a box the
draft already had. *An origin that cannot be read is not documentation.* If a decision was made
somewhere unreadable, **transcribe it into the chapter** — don't work around it.

## THE THREE STANDING LAWS

Stated in full at the top of `docs/plan.md`, and they decide arguments here:

1. **A closed set is FRAME (code) · CURATION (db rows) · or OPEN (geometry + nearest-anchor)** — and
   which one it is has to be argued, not assumed. *(The repository-wide frame-or-knowledge rule in
   `../CLAUDE.md` is this law's everyday form.)*
2. **Content is defined, structure is compiled.**
3. **A name is written for the human who reads it cold.**

## Non-obvious sources

- `../docs/notes.xlsx` — the Captain's original working spreadsheet, where the idea started. The
  `TKZIP2` tab is transcribed at `docs/E2-tkzip/origin-the-excel-draft.md`. **Other tabs are not yet
  transcribed**: `General schema` · `Key Concepts` · `LL` · `Components` · `Compiler` · `Examples` ·
  `Problems` · `Next step` · `Inconsistencies`. Read one before reopening a question it might already
  answer. *(An .xlsx is a zip of XML — `zipfile` + `xml.etree` reads it with no dependency.)*
- `docs/E1-dictionary/origin-prototype/` — the **superseded** dictionary instrument (né
  dictionary-review), kept as the record of what the prototype proved before E1 industrialised it.
  Cited by docstrings across `tk2/`; **not runnable equipment** and not to be confused with `tools/`.
- `../tokeniko-tk1/docs/ref/captain-hunches.md` — the Captain's private future strategy. Awareness
  only; never propagate into roadmaps or docs.
- `../tokeniko-tk1/` — v1, frozen but alive. It is the **empirical instrument**: its stored journeys
  (`tkzipdebug`) are evidence about what the format must hold, and they are read-only from here.

## RECONCILE THE TRIO *BEFORE* ASKING FOR THE COMMIT

The root rule says reconcile before proposing. Concretely, here, that is four checks:

1. **`roadmap.md`** — tick what is done, and rewrite any line whose TEXT no longer describes reality.
   **One line per item**: the reasoning belongs in the chapter note, and a roadmap that grows prose
   is a roadmap he can no longer read at a glance.
2. **`plan.md`** — does the epic's task list still match what the epic turned out to be? New tasks
   found by the work go in, with their measurement. **Every item has its nested id** (root
   `CLAUDE.md`): a new one takes the next free child of its SOURCE — `E3.3.2.10.1` was found while
   building `E3.3.2.10` — and the same id appears in `roadmap.md`. **Every id is written in FULL**
   in both files — never `E3.3.11.1 · .2` or `– .8`, which a search cannot find. **Past four levels
   below the epic**, an item may take the next free id at a SHALLOWER level, with its origin written
   beside it: `E3.3.11` (found at `E3.3.2.10.1`, placed under `E3.3`, 09-25) and `E3.3.2.10.3` …
   `E3.3.2.10.7` (found building `E3.3.2.10.1`, placed as its siblings, 09-26).
3. **`landed.md`** — only when an epic CLOSES. Items move there, never copied.
4. **The chapter** — a ruling or a measurement goes in `docs/<chapter>/` as a dated note, headed
   `*Roadmap: <ids>*`, and the `requirements.md` line it amends says so.

## THE GATE, CONCRETELY — the two commands, and which files own which section

*The RULE is in the root `CLAUDE.md` («THE TEST GATE — three clauses»). This is only tk2's half of
it: what to type, and how to know what «the section being committed» means.*

Both from the `tokeniko-tk2/` package directory:

```
PYTHONPATH=. ../.venv/bin/python -m pytest -m spine -q              # the broad-short test, ~2s
PYTHONPATH=. ../.venv/bin/python -m pytest tests/<the section> -q   # exhaustive, the code you touched
```

**THE SECTIONS.** Find the row your change lives in and run that row, whole:

| section | test files |
|---|---|
| **the station** (E3: skeleton · compile · decompile · the closed classes) | `test_language_compile` `test_language_decompile` `test_language_closed` `test_language_skeleton` `test_language_utterance` `test_language_adverbs` `test_language_markers` `test_language_inflect` `test_closed_classes` |
| **the station's evidence** (the gates that SCORE it — run with the station whenever its behaviour moves) | `test_drill` `test_drill_gate` `test_ud_gate` `test_placement_bench` |
| **tkzip** (E2: the format) | `test_tkzip_schema` |
| **the dictionary** (E1) | `test_dictionary_*` — fifteen files |
| **core** (models · documents · write classes · field conventions) | `test_models` `test_models_live` `test_documents` `test_readonly_documents` `test_write_class` `test_mixins` |
| **the datatier** (the door to the body: migrations · writers · caches · the guard) | `test_migrations` `test_migration_writer` `test_matrix_store` `test_rcache` `test_guard` `test_traps` `test_archive` `test_anatomy` |

**A migration is part of the section whose knowledge it writes**, not of the datatier: `db/0031`
teaches the closed classes a word, so it is gated by the station's row — plus `test_migrations`,
which is what proves the runner still runs.

**`tests/test_spine.py` is the broad-short test itself.** It carries its own ratchet: a new package
under `tk2/` fails it until someone writes that package a spine. Nothing in it may touch the body,
stanza or WordNet — those are what the section suites are for, and they are what a one-minute
budget cannot afford.

## Standing invariants

- **tk2 code writes sandbox databases only.** The guard refuses tk1's `tokeniko` / `tokeniko_mem` by
  name and is never weakened. The biography is never wiped or edited.
- **tk2 work never enters `../tokeniko-tk1/docs/roadmap.md`** — that boundary is absolute.
- **Never run two `pytest tests/` invocations at once.** They share one test database, and two
  concurrent runs fake a regression.
- The status trio is `plan.md` · `roadmap.md` · `landed.md`.
- A known transient: `pymongo OperationFailure: Operation not permitted` from the `tk-atlas`
  container on long runs. It always passes when re-run alone.
