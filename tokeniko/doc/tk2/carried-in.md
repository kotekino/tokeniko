# Carried in — what the tk2 filter moved off the v1 road

> **The filter, in one line: work that builds an ASSET migrates; work that builds MACHINERY gets
> rebuilt.** This document holds the *reasoning* for each item the filter moved. Their **status** is
> `doc/parked.md` (tagged `→ tk2`) — one item, one status, one doc; this file references, it never
> duplicates.

Established 2026-08-03, on the author's question: *should we review the roadmap so we don't do tasks
that will surely be rebuilt with tk2?*

## The criterion, and why it is not "will it be rebuilt"

The author's opening formulation — skip what tk2 will discard, skip tuning and tweaking — is right in
its effect and slightly wrong in its handle. "Will it be rebuilt?" invites a guess about the future.
**"Which layer does it touch?"** is answerable *today*, from `README.md` §5, and it gives the same
answers with a reason attached.

- **Assets** — the dictionary and its 2925 base vectors, curated senses, curated scaffolds, the KB
  (axioms/definitions/theorems), the anchor sets, findings, regression corpora. These cross the
  bridge intact. Work that produces them is never wasted.
- **Machinery** — anything coupled to the TKZip format, to the evaluator's geometric comparison, or
  to hardwired behaviour dispatch. These are the two limits themselves (`README.md` §1). Work here
  is done twice.

## Two corrections the filter needed

**1. Findings are assets.** v1's job is now explicitly to be the empirical instrument
(`README.md` §9 — keeping the first system alive is the mitigation against second-system syndrome).
So work that produces *evidence* survives even when it produces no shipped feature. This **promoted**
the microscope analysis pass rather than deferring it: every case where the pipeline mis-reads a real
sentence is a requirement on tk2's schema. It is the fifty-sentence drill's big brother — the drill
uses sentences we choose, the microscope uses every sentence he has actually heard.

**2. Instrument fitness is not tuning.** A naive reading of "skip optimization" would have dropped
the KB-load big-O item. But that load stalls the tick on every materialized theorem, which directly
reduces the findings v1 produces. It stayed on the road, scoped to its cheap half.

**The danger this guards against:** a filter applied too hard turns v1 into a museum, and a blueprint
with no living instrument behind it is just a rewrite with confidence.

## What the partition revealed

Seven of the strengthening tail's eleven entries left. **Everything that survived is asset work** —
anchors, dictionary, KB, curated voice — and nothing that survived is machinery. The filter was
never aimed at that line; it found it. That is the strongest evidence available that the inheritance
ledger's cut is real and not a convenience.

The consequence the author should keep in view: **tk2 becomes the main line sooner than "alternating
phases" suggests.** Two large survivors remain (KB growing outward, vocabulary growth), so v1 is not
finished — but its tail is no longer a year of work.

## The carried items, and what each becomes in the blueprint

Each entry names what it *stops being* (v1 work) and what it *becomes* (a blueprint input).

**TKZip binary compaction + zip-native renderer** — the author's own worked example, and correct.
Becomes: **open question 9** (fixed arity is a property of the schema, not of the storage — store
sparse, densify on demand). tk2 answers the storage question differently and more cheaply than a
packing pass over the current format would. Its dependent, **per-conjunct knowledge**, is blocked on
a renderer that only tk2 will make honest.

**Restricted-universal residuals** — becomes: **open question 6, scope and binders.** "All machines
that think are minds" needs a variable bound across atoms with a quantifier scoping over both. v1 can
only special-case it. This is the single clearest instance of the filter earning its keep: the item
looked like a parser gap and is actually a formalism gap.

**Conditional reasoning (R4b)** — becomes: a **capability requirement** in the capability inventory
(hunch 21 step 4). "Given P, is Q?" is a capability we know he needs; the logic transfers, the
evaluator implementation does not. Recording it as a requirement is worth more than implementing it
twice.

**Questions follow-ups** — splits across three blueprint homes: the `imperative` scalar is a **mood
field on the schema**; wh when/how solving is **evaluator**; and "real self-knowledge for how do you
feel?" is **hunch 20, situational awareness** — already investigation order #3, and a prerequisite
for limit A rather than a question feature.

**Etiquette, the dispatch half** — becomes: a **worked example for the rule layer.** It is limit A in
miniature — hardwiring which reaction follows which trigger — and therefore an excellent first test
of rules-as-KB: greetings are low-stakes, high-frequency, and obviously *conventional* rather than
logical, which is exactly the profile of a rule that should be learnable and revisable. *(The
curation half stayed on the v1 road: scaffold rows are assets.)*

**D-phase realtime enhancements** — becomes: part of the **state layer** (§6.3). The landed context
ring (`brain/context.py`) is already the seed of hunch 20's social column; the full consumer set
should be designed against the SA matrix rather than bolted onto the ring.

**The third memory tier (event vs general knowledge)** — becomes: a **first-class blueprint
question**, converging with hunch 20's event-magnitude design (*an event is a delta in the SA matrix;
a fact is a payload*). Deciding the tier inside v1's format would decide it twice, and the better
frame — magnitude as resistance to consolidation — only exists on the tk2 side.

## How to use this document

When an item's time comes, it does **not** get promoted back to `roadmap.md`. It gets picked up
inside the blueprint, at the point in the investigation order where it belongs. The v1 road and this
list are not two queues into the same build; they are the asset track and the design track.

*Opened 2026-08-03, from the author's roadmap-reconciliation question.* 🜂
