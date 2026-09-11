# tokeniko 2 — how to work in this project

## READ THE CHAPTER BEFORE YOU ELABORATE ANY POINT IN IT

`docs/roadmap.md` is **the overarching plan only** — one line per item, no reasoning in it.
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

Plus `docs/README.md` (the method, the inheritance ledger, the open-questions ledger),
`docs/carried-in.md` (what the tk2 filter moved off the v1 road) and `docs/ideas.md`.

**The rule that produced this file (the Captain, 2026-09-11):** at E2 the QM rebuilt the tkzip role
inventory from external corpora without reading the Captain's own first draft, which lived in a tab
of a binary spreadsheet and was linked from nothing. The rebuild independently re-derived a box the
draft already had. *An origin that cannot be read is not documentation.* If a decision was made
somewhere unreadable, **transcribe it into the chapter** — don't work around it.

## PEDANTRY APPLIES TO DIRECTION, NOT ONLY TO OPERATIONS (the Captain, 2026-09-11, PRIO 1)

> *«You should be as pedantic with the CORE project as you are with deploys and db operations. No
> easy solutions, no result-oriented mindset — accuracy and deepness is the polar star. We are not in
> a hurry, we don't have a product or a company to please. We are doing science and accuracy takes
> time.»*

A wrong deploy is revertible; a wrong schema decision is not. So on any core-design question:

- **establish the criteria and the test bench BEFORE proposing an answer** — enumerate the cases a
  mechanism must handle, then test candidates against them; never pick the tidy one and defend it
- **state costs in both directions**, including for the option being recommended
- **never let «what does the next layer need» decide what the FRAME is** — that is how a contingent
  fact about one language ends up in code
- re-steering costs the Captain real time; being right the second time is not the goal

## Non-obvious sources

- `doc/notes.xlsx` (repo root) — the Captain's original working spreadsheet. The `TKZIP2` tab is
  transcribed at `docs/tkzip/origin-the-excel-draft.md`. **Other tabs are not yet transcribed**:
  `General schema` · `Key Concepts` · `LL` · `Components` · `Compiler` · `Examples` · `Problems` ·
  `Next step` · `Inconsistencies`. Read one before reopening a question it might already answer.
  (An .xlsx is a zip of XML — `zipfile` + `xml.etree` reads it with no dependency.)
- `../tokeniko-tk1/doc/ref/captain-hunches.md` — the Captain's private future strategy. Awareness
  only; never propagate into roadmaps or docs.
- `../tokeniko-tk1/` — the live v1 engine. It is the **empirical instrument**: its stored journeys
  (`tkzipdebug`, 553 rows / 113 judged mismatches) are evidence about what the format must hold.

## Standing invariants

- tk2 work never enters `../tokeniko-tk1/doc/roadmap.md` — that boundary is absolute.
- The status trio is `plan.md` · `roadmap.md` · `landed.md`. One item, one status, one doc;
  reconcile at every commit.
- Commits, pushes and `--apply`-class writes happen **only** on the Captain's explicit yes.
- tk2 code writes sandbox databases only. The guard is never weakened.
- The three standing laws (where a closed set may live · content is defined, structure is compiled ·
  a name is written for the human who reads it cold) are stated in full at the top of `plan.md`.
