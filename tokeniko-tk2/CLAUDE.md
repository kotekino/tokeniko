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
docs/tkzip/  docs/dictionary/  docs/parser-compiler/  docs/evaluator/  docs/brain/
docs/rules/  docs/heart/  docs/senses/  docs/micro-nn/  docs/rag/  docs/data-modeling/
docs/datatier/  docs/body/  docs/stack/  docs/tooling/  docs/website/
```

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
  `TKZIP2` tab is transcribed at `docs/tkzip/origin-the-excel-draft.md`. **Other tabs are not yet
  transcribed**: `General schema` · `Key Concepts` · `LL` · `Components` · `Compiler` · `Examples` ·
  `Problems` · `Next step` · `Inconsistencies`. Read one before reopening a question it might already
  answer. *(An .xlsx is a zip of XML — `zipfile` + `xml.etree` reads it with no dependency.)*
- `docs/dictionary/origin-prototype/` — the **superseded** dictionary instrument (né
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
   found by the work go in, with their measurement. A task gets a number only if it is a real
   sibling, and that number must also appear in `roadmap.md`.
3. **`landed.md`** — only when an epic CLOSES. Items move there, never copied.
4. **The chapter** — a ruling or a measurement goes in `docs/<chapter>/` as a dated note, and the
   `requirements.md` line it amends says so.

## Standing invariants

- **tk2 code writes sandbox databases only.** The guard refuses tk1's `tokeniko` / `tokeniko_mem` by
  name and is never weakened. The biography is never wiped or edited.
- **tk2 work never enters `../tokeniko-tk1/docs/roadmap.md`** — that boundary is absolute.
- **Never run two `pytest tests/` invocations at once.** They share one test database, and two
  concurrent runs fake a regression.
- The status trio is `plan.md` · `roadmap.md` · `landed.md`.
- A known transient: `pymongo OperationFailure: Operation not permitted` from the `tk-atlas`
  container on long runs. It always passes when re-run alone.
