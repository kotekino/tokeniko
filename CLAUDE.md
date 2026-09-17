# CLAUDE.md — the repository root

Guidance for Claude Code across **the whole repository**. Everything here applies everywhere.
Each subproject has its own `CLAUDE.md` carrying **only what differs** — never a copy of this.

---

## ⮕ THE VISION IS THE TIE-BREAKER, AND IT IS READ BEFORE THE FACT

**`docs/vision.md` is the polar star.** One persistent, logic-first entity; a digital twin of its
author; logic hardwired as the first axiom and everything else in memory; one body, one continuous
self; expression, not exposure.

**Every decision, and every micro-steering, is taken with the vision in view.** Not consulted when a
question looks big enough — consulted as a matter of course, so that nothing is ever *discovered
late* to be something the vision prohibits, implies, or already settled. A design that has to be
undone because the north star said so was a design taken without looking up.

When a decision is unclear, the vision decides. When the vision and a tactical convenience disagree,
the vision wins and the convenience is written down as a cost.

## WHAT IS IN THIS ROOT

```
docs/          the FOUNDATIONAL documents — the vision, the source-corpus provenance,
               and the author's original notebook (notes.xlsx, where the idea started)
tokeniko-tk1/  v1 — the LIVE engine, embodied. Development FROZEN; it keeps running and
               keeps witnessing. Its corpora are the no-regression ratchet tk2 must clear
tokeniko-tk2/  v2 — the blueprint and the build. This is where active work happens
tokeniko-public/ the public window (Node/React) at tokeniko.online — a one-way surface:
               the mind publishes outward, the public never reaches into the body
body/          the embodiment: deploy machinery, service definitions, hardware baselines.
               NOT under a generation folder, because the body outlives the engine in it
bi/            business-intelligence workspace
data/          the raw source corpora (gitignored — see docs/provenance.md for the ledger)
```

**One git repository, at this root.** Every subproject is a folder in it, so a move is a `git mv` and
a change spanning two of them is one commit.

## THE HIERARCHY RULE — FOR DOCS AND FOR INSTRUCTIONS

**A folder's documents describe what belongs to that folder. A subfolder's documents carry ONLY the
difference.** A child that restates its parent is a child that will drift from it.

So: this file and `README.md` hold the common ground; `tokeniko-tk1/CLAUDE.md`,
`tokeniko-tk2/CLAUDE.md` and the public project's docs hold what is true of *that* project alone and
point here for the rest. The same rule governs `docs/` at every level.

The one thing that is *not* inherited is a rule scoped to its own folder — the tk2 sandbox guard
lives in tk2's file because it is a fact about tk2, not about the repository. Placing a rule by its
real scope is what makes the hierarchy safe; nothing needs duplicating.

## THE DOCUMENT COMES FIRST, THEN THE REFERENCE TO IT *(the Captain, 2026-09-17)*

> *«Any addition we do — because the coding discovered something — should FIRST and foremost start
> with the update in the documents, whether it affects plan, roadmap or all. First reconcile, then
> you can refer to a point listed there as if I know what you are talking about. Otherwise if you say
> "next is e34a.122" and I don't find it there, I push back saying "wut?".»*

**A task identifier that exists only in my head, or in only one of the documents, is not vocabulary —
it is a private note.** Before naming a point in conversation, it must already be written where he
reads it. This costs one edit and saves him the work of reconstructing what I meant.

**It applies to the conversation, not only to the commit.** The failure it was written for was a task
called `2d` that lived in `plan.md`, indented so markdown never even numbered it, and was then used
in chat as though it were shared.

## SYNTHESIS IS NOT A COURTESY — IT IS HOW STEERING SURVIVES *(the Captain, 2026-09-17)*

> *«As a human I spend time reading a lot of tokens: I don't have an upper limit like a model, but I
> have degradation in my capabilities the more tokens I consume. So synthesis and order are a crucial
> game changer, to let me steer better.»*

Reports are **synthetic and hierarchical**: verdict first, then numbers, then what needs him, then
what is parked. Status documents keep to their declared density — **a roadmap line is one line**, and
the reasoning that justifies it goes to the chapter note where it belongs. Prose that grows a status
document is prose that costs him the ability to steer it.

Artifacts stay verbose. Summaries do not.

## PEDANTRY APPLIES TO DIRECTION, NOT ONLY TO OPERATIONS *(the Captain, 2026-09-11, PRIO 1)*

> *«You should be as pedantic with the CORE project as you are with deploys and db operations. No
> easy solutions, no result-oriented mindset — accuracy and deepness is the polar star. We are not in
> a hurry, we don't have a product or a company to please. We are doing science and accuracy takes
> time.»*

A wrong deploy is revertible; a wrong schema decision is not. So on any core-design question:

- **establish the criteria and the test bench BEFORE proposing an answer** — enumerate the cases a
  mechanism must handle, then measure candidates against them; never pick the tidy one and defend it
- **state costs in both directions**, including for the option being recommended
- **never let «what does the next layer need» decide what the FRAME is**
- re-steering costs him real time; being right the second time is not the goal

## FRAME OR KNOWLEDGE? — ASK BEFORE YOU PUT A SET IN CODE *(the Captain, 2026-09-16, PRIO 1)*

> *«Whenever you think to stick something in the code, always ask me to discuss: frame or knowledge?
> 99% of the times it will be knowledge and we will discover together. It applies everywhere — except
> logic.»*

**Choosing our own set and hard-coding it does not remove the rigidity, it relocates it.** That is
the failure this rule catches, and it is invisible from inside the decision — which is why it is a
conversation and not a checklist.

Before any list, map, enum, threshold or roster is written into a `.py` file, **stop and ask**. Not
«is this convenient in code» — *is this LAW, or a revisable fact about a language, a resource or the
world?* The default answer is KNOWLEDGE. The one exception is the **logic kernel**, invariant by
charter.

**And the failure mode is not only hard-coding a set — it is NEEDING one** *(2026-09-17)*. Asked
which characters count as quotation marks, the right answer was not «put them in a table»: it was
that the parser had already isolated the quote structurally and no such list was needed. *Before
asking where a list should live, ask why there is a list.*

**At the end of every epic, audit what was built** and ask which things called frame belong in the
knowledge kingdom.

## AND A THIRD KINGDOM: EVIDENCE *(the Captain, 2026-09-17)*

Frame and knowledge govern the **application's business logic**. Tests are neither:

| | what it is | where it lives |
|---|---|---|
| **frame** | law the app obeys | code — and kept small |
| **knowledge** | revisable facts the app reasons with | db, by migration |
| **evidence** | curated circumstances that JUDGE the app | isolated; never read at runtime |

> *«A test is by its nature a curated set of circumstances: it can't be knowledge, it is curated, and
> it should be isolated by the app itself.»*

Evidence still wants the ledger properties — versioned, append-mostly, its justification kept
verbatim — but those are separable from *which* database it sits in.

## STATUS DOCUMENTS — THE INVARIANTS, EVERYWHERE

Each project keeps its own status documents. Whatever they are called, these hold:

1. **One item, one status, one document.** Never the same task under two statuses.
2. **No cross-doc duplication.** When an item moves status, **MOVE it** — never copy. A one-line
   pointer is allowed; it references, it does not carry status detail of its own.
3. **Reconcile BEFORE proposing the commit**, not after — so the document changes are in the diff
   he approves. A commit that lands code and leaves the status describing the world before it is a
   commit that made the status wrong.

Reference material (design notes, empirical logs, chapter records) is **exempt**: an item may be
discussed there *and* have a status entry elsewhere.

## HOW WE WORK

- **Commits, pushes and `--apply`-class writes happen only on the Captain's explicit yes.** Surface
  the diff and the proposed message, then wait.
- **Small tasks go straight to `main`**; no feature branches for now. Never check out a branch in the
  shared working tree.
- **Never `git add -A`.** Stage explicit paths and read `git status` for foreign files.
- **Tests run at the commit gate, not between edits** *(2026-09-17)*. While developing, run only the
  subset that STEERS the next decision; the full suite runs once, before proposing the commit, and
  its result is reported there. Foundational work must stay fast-paced, and much of the suite talks
  to a remote body.
- **His rulings are current-best, not law.** Surface a stale decision with an argument rather than
  quietly obeying — safety rules excepted.
- **`tokeniko-tk1/docs/ref/captain-hunches.md`** is his private future strategy: awareness only,
  never propagated into roadmaps or docs.

## WHERE TO GO NEXT

| working on | read |
|---|---|
| the live engine | `tokeniko-tk1/CLAUDE.md` |
| the next architecture | `tokeniko-tk2/CLAUDE.md` |
| the public window | `tokeniko-public/README.md` |
| the body itself | `body/tools/README.md` |
| anything at all | `docs/vision.md` — first, and again when it gets hard |
