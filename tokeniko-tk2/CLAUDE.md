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

## FRAME OR KNOWLEDGE? — ASK BEFORE YOU PUT A SET IN CODE (the Captain, 2026-09-16, PRIO 1)

> *«Whenever you think to stick something in the code, always ask me to discuss: frame or knowledge?
> 99% of the times it will be knowledge and we will discover together. This must be a rule. It
> applies everywhere — except logic.»*

**The rule was earned the same day.** Asked whether the KINDS OF NAME should be OntoNotes' label set
or our own, the QM argued for our own on four engineering grounds — and still left the inventory as
an enum **in code**. The Captain's answer went a layer deeper:

> *«With our inventory as db (not code!), we can modify it keeping the logic: everything is KB. If
> we rely on a third party we lose this ability.»*

**Choosing our own set and hard-coding it does not remove the rigidity, it relocates it.** That is
the failure this rule exists to catch, and it is not obvious from inside the decision — which is why
it is a conversation and not a checklist.

**So: before any list, map, enum, threshold or roster is written into a `.py` file, STOP and ask.**
Not «is this convenient in code» — *is this LAW, or is it a revisable fact about a language, a
resource or the world?* The default answer is KNOWLEDGE.

- **The one exception is LOGIC.** The logic kernel is invariant by charter and is not up for
  discussion — everything else is.
- **The FRAME test** (2026-08-25): a set feels like law and is not, when it is a contingent fact,
  dialect-varying and revisable. `ClosedClassDoc.word_class` is a **string and not an enum** for
  exactly this reason — *«a class that needed a code change to exist would put the table back in
  code»*. That sentence is the test, already written down, a month before the rule.
- **What frame legitimately holds**: the MECHANISM that reads the rows, and the relations between two
  published, closed vocabularies where no evidence revises the correspondence. Everything else is a
  migration.
- **AT THE END OF EVERY EPIC, AUDIT WHAT WAS BUILT** — walk back through it and ask which of the
  things called frame belong in the knowledge kingdom. E3 carries the first such audit as a task.

## RECONCILE THE TRIO *BEFORE* ASKING FOR THE COMMIT (the Captain, 2026-09-15)

> *«Keep the rule to reconcile always before asking me to commit.»*

Not after, and not «at» the commit: **the reconciliation is part of the work being proposed**, so it
is in the diff he is approving. A commit that lands code and leaves `roadmap.md` describing the
state before it is a commit that made the trio wrong — and the trio is how he sees the project.

Concretely, before every «ready to commit?»:

1. **`roadmap.md`** — tick what is done, and rewrite any line whose TEXT no longer describes reality
   (a task-0 line still saying «`compiled` is empty on all of them» is worse than an unticked box).
2. **`plan.md`** — does the epic's task list still match what the epic turned out to be? New tasks
   found by the work go in, with their measurement.
3. **`landed.md`** — only when an epic CLOSES. Items move there, never copied.
4. **The chapter** — a ruling or a measurement goes in `docs/<chapter>/` as a dated note, and the
   `requirements.md` line it amends says so.

Then propose the commit, with the doc changes in the same diff as the code.

## Standing invariants

- tk2 work never enters `../tokeniko-tk1/doc/roadmap.md` — that boundary is absolute.
- The status trio is `plan.md` · `roadmap.md` · `landed.md`. One item, one status, one doc;
  **reconcile BEFORE proposing the commit** — see the section above.
- Commits, pushes and `--apply`-class writes happen **only** on the Captain's explicit yes.
- tk2 code writes sandbox databases only. The guard is never weakened.
- The three standing laws (where a closed set may live · content is defined, structure is compiled ·
  a name is written for the human who reads it cold) are stated in full at the top of `plan.md`.
