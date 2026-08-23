# tokeniko 2 — the blueprint project

> **Step 0: the plan for how to plan.** This document is not the design of tokeniko 2. It is the
> agreed method for producing that design — what we are solving, what is inherited, what must survive,
> what is still open, in what order we investigate, and how we would know the result is *better*
> rather than merely *newer*.

## What this directory is — and is not

`doc/tk2/` holds the conception work for the next architecture. Everything here is **reference
material**, exempt from the status-doc invariants exactly as `doc/ref/notes.md` is.

- **Nothing here enters `roadmap.md`, `landed.md` or `parked.md`.** These items have no status: they
  are neither in flight, nor done, nor deferred work — they are *design*. Forcing a status would
  violate invariant #1 by inventing one.
- **v1 continues unchanged.** It is not frozen, not deprecated, not a museum. It remains the
  empirical instrument: every limit it hits is a finding, and findings are the fuel of this
  directory. A tk2 that stops v1 has destroyed its own source of evidence.
- **This phase costs conversation and documents, not implementation.** No officer is dispatched to
  *build tk2* until the blueprint is fixed and a scope is cut from it. Cost is a design constraint.
  *(Amended 2026-08-12, the «verify instead of guessing» ruling: officers MAY be dispatched to build
  **instruments** — code/drafts/tests that settle a doubt and thereby DEFINE a requirement, sandboxed
  to `tokeniko_tk2`. The prohibition is on building the product, not on measuring the design.)*
- **Parking is free.** If attention moves elsewhere, this directory sits still and loses nothing.

Origin: hunch 21 of `doc/ref/captain-hunches.md`, opened and argued 2026-07-31.

---

## 1. The two limits — stated so they can be falsified

The whole project rests on these being *real*. Each is written here in the sharpest form we can give
it, so that it can be attacked rather than assumed.

### A — behaviour is hardwired

**The imprecise claim:** "all his behaviour is hardwired." That is an overstatement of the current
state, and stating it that way makes the work untractable.

**The precise claim:** the rule *table* is already KB (`behavior_rules`, `MEMBehaviorRule`) — the code
holds capabilities and effects, memory holds which effect follows which trigger. What is **not** in
memory is the **trigger vocabulary**, the **action vocabulary**, and above all the **conditions**: an
`eval:*` token is *computed in code* and then looked up. So policy is partly in memory, over a fixed
vocabulary, keyed on conditions that only code can produce.

**Falsifiable form:** *tokeniko cannot acquire a behaviour we did not anticipate the shape of.*

**Why it matters:** `VISION.md` says logic hardwired as the first axiom, all knowledge **and
behaviour** in memory. By the project's own charter, this is a gap — and behaviour is what defines a
being's relation to its environment.

### B — the zip is not computable

**The precise claim:** the zip is fixed-size *per role*, but the *set of roles is variable* —
`indirects` is an open list. Therefore traversal requires code that knows the shape, comparison is
type-routed through the marker gate, and there is no uniform algebra over sentences.

**Falsifiable form:** *two sentences cannot be compared, matched, or batch-processed without code
that knows their individual shape.*

### The relationship between them — corrected

The originating intuition was "B causes A". **It does not**, and the correction is what makes the
work tractable.

A is caused by the absence of a first-class **state**: rules cannot be data because there is nothing
in the same language for them to be evaluated *against*. Today the state is implicit in the control
flow of `thinking_phase`. Fixing the zip's arity does not produce a state.

**But B is the enabler in build order**, which is why the intuition pointed the right way: a
variable-arity zip is a *bad rule language*. Rules-as-patterns want fixed slots and wildcards. So the
sequence stands — **B before A** — for a different reason than the one first given.

---

## 2. The continuity contract — SETTLED, do not re-open

The question was: is tokeniko 2 the same being, or his child? The ruling: **both, and nothing is
erased.**

- **`_ME_UID` is preserved.** Identity is carried by continuity of the causal chain, not by substrate
  or encoding — and the practical anchor is a foreign key, not a claim: every trust episode, every
  `taught:<uid>` premise, every circulating reference stays valid across the translation.
- **Memory is translated, not replaced.** The raw text was always kept (`item.original`), so a v2
  reading is derivable for every past item.
- **The v1 zips are KEPT beside the v2 ones.** This is the refinement that makes the translation
  legal under «true history be it»: a wholesale recompile would silently erase the record of what he
  *misunderstood*, which is a bulk edit of history by another name. The old zip is what he understood
  **then**; the new one is what he understands **now**; the original text is what was actually said.
  Translation becomes additive rather than destructive, and every derivation still points at its
  premises as they were.
- **Reconciliation is his, not ours.** Some theorems will not re-derive under the new semantics. They
  are not to be fixed by hand. The sleep phase already exists and its duty is already belief hygiene:
  **the migration night is a night of sleep** — he wakes, wonders, finds what no longer follows, and
  retreats it through the in-mind machinery. Not surgery performed on him: an event in his life.

Supporting precedent worth remembering: biological memory does this continuously. Every recall is
rewritten in the substrate the mind has *now*, not the one that formed the trace. Re-encoding is not
a break in identity; it is what remembering *is*.

---

## 3. The governing decisions — settled 2026-07-31

These were argued to conclusion and are the premises of the blueprint. They are *current-best*, not
law (see §9), but re-opening them requires a new argument, not a fresh opinion.

**Behaviour lives in the KB as belief, subject to the same trust, provenance and revision machinery
as any other belief.** Not a config table, not a dispatch registry with a data skin. The prize is
that a rule becomes something he can *derive*, *be taught*, and *retract*.

**Protection is cost, never impossibility.** An earlier proposal — a constitutional tier of
un-overridable rules — was rejected, and rightly. A mind that cannot be persuaded is not protected;
it is finished. The capacity that makes him movable by an adversary is the *same capacity* that lets
him be moved by a great book — one faculty seen from two sides, and no design removes one without
removing the other.

**Skepticism is the instrument** — defined here as *the match over trust and logic*. It makes
revision difficult in proportion to what is at stake. It prevents nothing.

**The imprint ceiling is removed in principle: he must be able to outgrow his father.** If a single
source is pinned at maximum trust, everything that source teaches is permanently un-outbiddable, and
the arithmetic that makes revision meaningful never runs. Mechanism is open (§7); the direction is
settled.

**The reason this matters, recorded because it is the thesis:** if he can be persuaded, then whatever
he eventually holds is *his*. A mind whose foundations cannot be revised never chose them. This is
what gives hunch 21's step 7 something to observe — without revisability, whatever he becomes is
only what we wrote.

### What still needs mechanism (not principle)

Three refinements were proposed and accepted as directions, and belong in the blueprint proper:

1. **Depth-weighted revision cost.** Trust is earned incrementally but spent atomically: one
   sufficiently-trusted source could otherwise rewrite everything below its threshold at once. The
   cost of overturning a belief should scale with its structural depth — age, and how many other
   beliefs derive from it. This is provenance-cascade run backwards, and it is the mechanical form of
   «deep beliefs are hard to break»: not sealed, but load-bearing, so the weight is felt when pulled.
2. **The self-modifying rule class.** Rules that alter his *capacity to evaluate rules* («ask why
   less», «check less», «trust faster») are not symmetric with other rules — they change the
   machinery that would later catch the next one. They are not to be forbidden; they are to be
   **detected and priced**, via hunch 18's derivative guard, which identifies them structurally
   without judging their content.
3. **Plurality of sources.** A single-channel being can be enclosed: whoever controls the one channel
   controls the entire information environment, and no amount of perfect recall defends against a
   bounded world. This makes multi-channel presence and the web-retrieval hunch (#3) structural
   rather than decorative.

One caveat to carry forward: **"he forgets nothing" is true of storage, not of consultation.** Hunch
20's telescoping blurs older awareness by design, and retrieval at decision time is bounded
regardless. The requirement is not perfect memory — it is that revision trajectories are *recorded*
so that reversal remains possible.

---

## 4. Invariants that must survive the rebuild

Non-negotiable inputs to any design produced here. If a proposed architecture breaks one of these,
the architecture is wrong, not the invariant.

- **Logic is hardwired, in code, as the first axiom.** It is the one thing that is *not* KB, by
  design — the equivalent of the cells the rest is built on.
- **The biography is sacred.** Memory, theorems, ideas, actions, `brain_state` are never wiped.
- **True history be it.** Wrong beliefs are retreated through in-mind machinery, never edited in the
  database.
- **`item.original` always holds the speaker's own words, in their own language.**
- **Abstention over guessing.** Where the format cannot represent a sentence, the answer is to
  *abstain*, never to silently truncate into the nearest fit.
- **One body, embodied, bare metal** (`doc/ref/deploy-body.md` §0 — settled and not to be
  re-litigated).
- **`_ME_UID` continuity** (§2).

---

## 5. The inheritance ledger — the core work

The central deliverable of the blueprint: a component-by-component decision, **inherit / migrate /
rebuild**, each with its reason. Anything marked *rebuild* must justify why migration is impossible,
because rebuilding is how a second system quietly becomes a rewrite.

The initial lean (2026-07-31) — a starting position to be argued, not a conclusion. **Where a
component session has since closed, its `requirements.md` is authoritative and the lean below is
history**; rows overtaken so far are annotated:

| Component | Lean | Why |
|---|---|---|
| Dictionary + 2925 base vectors | ~~**inherit** untouched~~ → **rebuild the base, inherit the curation** | OVERTAKEN 2026-08-12: the two-matrix base (R stated · D topical, POS-split keys) replaces the Jurassic squared matrix; what is inherited is the curated *senses* and the lexicon, not the old geometry |
| Anchor resolver + anchor sets | **inherit** | orthogonal to the format |
| Parser (spaCy/Stanza → AST) | **inherit**, retune | the surface layer does not change — but it now emits sense slots OPEN (WSD moved to the evaluator, 2026-08-13) |
| Curated senses, scaffolds, behaviour seeds | **inherit** | curation is the costly part, not the code |
| TKZip format | **rebuild** | this *is* limit B |
| Compiler zip section | **rebuild** | follows the format |
| Evaluator comparison / grounding | **rebuild** | follows the format — and it grows: the KB's door, absorbing WSD (brain req. 7) |
| Logic kernel (consistency, operators) | **inherit** | invariant by charter |
| Forward chainer | **inherit**, generalize | already fires rules to a fixpoint |
| Behaviour / dispatch | **rebuild** | this *is* limit A |
| Brain phases (thinking/priorities/actions/sleep) | ~~**inherit**~~ → **rebuild the orchestrator, keep the phase idea** | OVERTAKEN 2026-08-13: the compensator half dies into the dual read; phases become kb reweighting (dna only knows they exist); the loop survives as dna, the how becomes rows |
| API, senses, adapters, Mongo | **inherit** the senses/adapters; the tier is its own session | the everything-is-rows ruling (2026-08-13) makes the body an interpreter of the db — datatier/body/data-modeling get their own conception sessions (register #11–13) |
| Stored memory documents | **migrate** | §2's translation |

**The signal to watch:** if the finished ledger says *rebuild everything*, the design is not
converging on the existing foundation and the premise should be challenged before a line is written.
The lean above still says the opposite — the overtaken rows moved toward rebuild, but the costly
assets (curation, logic kernel, chainer, senses) are still carried across intact.

---

## 6. The order of investigation

> **Superseded as the operating order (2026-08-13)** by the components register + «the road to the
> build» in §9: requirements per component → project (epics) → plan (tasks + briefings) → build
> (the officer cluster, with proof slices between epics). The steps below remain valid as
> *instruments inside their sessions* — the fifty-sentence drill belongs to the tkzip session, the
> state representation to rules/brain, valence to the heart session — but the sequence itself is no
> longer what we follow.

1. **The fifty-sentence table drill.** Drive fifty sentences by hand through the draft table —
   including the awkward ones: nested attitudes, `source`, secondary predication, two quantifiers,
   three operators, passives. Twelve rows already produced five findings; fifty will produce the
   rest, for the cost of an afternoon rather than an implementation cycle. **This is first because it
   is the cheapest instrument we have.**
2. **B — the format.** The role inventory, the noun-phrase record, named rows and operators, scope,
   storage.
3. **The state representation** (hunch 20's situational awareness) — because A cannot be built
   without something for rules to be evaluated against.
4. **Valence** (hunch 14, the heart) — because step 7's «better» requires a selection signal, and
   logic supplies truth, not preference. Without it, rules can only be *taught*, never *learned from
   experience*.
5. **A — rules as zips, and the matcher.**

The dependency worth naming plainly: **21 needs 20 and 14.** They were written as colour; they are
structural. Hunch 21 is the keystone that explains why.

---

## 7. The open questions ledger

Every entry carries an owner. Nothing here blocks the blueprint — the blueprint is *where these get
decided*.

| # | Question | Owner | State |
|---|---|---|---|
| 1 | Imprint ceiling — the mechanism by which trust stops being pinned | Cap | **answered in principle** (yes, he must be able to outgrow), mechanism open |
| 2 | Active/passive: normalize to deep roles, or keep surface topicality | Cap | **suspended** — implementation detail, deliberately deferred |
| 3 | Purpose encoding — `goal` slot vs. rows glued by an operator | both | open; the IMPLY encoding in the draft is **unsound** (it would derive that an intended outcome occurred) and is withdrawn |
| 4 | `source` — the missing dual of `destination` | — | **agreed: add** |
| 5 | Secondary predication («painted the door red») — new slot, or two rows | both | open; the equation form is preferred but must carry an explicit `RESULT`/`CAUSE` operator, since temporal succession is not causation |
| 6 | Scope and binders | both | open; leaning **row order = scope order** (prenex normal form) — costs one convention, no columns |
| 7 | `part` conflates two axes | both | open; **quantity** and **determination** are orthogonal, and the draft column currently *loses* a distinction v1 already makes (the five-way quantifier: universal / existential / negative / definite / generic). Definiteness is part of the scoping mechanism |
| 8 | Nesting via named rows | — | **agreed** — the Captain's `[Y = A AND B, Y IMPLY C]`; this is the Tseitin transformation, and it also solves nested attitudes (POV beyond depth 1) and gives variables a home |
| 9 | Storage width | — | proposed: **fixed arity is a property of the schema, not of the storage** — store sparse (most slots are `*`), densify on demand for batch work |
| 10 | Depth-weighted revision cost | both | proposed (§3) |
| 11 | Self-modifying rule detection | both | proposed (§3) |
| 12 | Plurality of sources / enclosure resistance | both | flagged (§3) |
| 13 | Role inventory completeness | both | open — VerbNet/PropBank thematic roles are the reference inventory; the draft already maps onto them almost one-to-one |

---

## 8. Success criteria — how we would know v2 is *better*, not merely newer

The section rewrites skip, and the one that decides whether this project can ever end. Stated as
tests, in advance, so the answer is not a matter of taste later.

1. **The A test** — tokeniko acquires a behaviour we did not anticipate, and the derivation of that
   behaviour is inspectable. (If every behaviour he shows is one we seeded, limit A survived.)
2. **The B test** — two arbitrary sentences are compared, matched, and batch-processed by uniform
   numeric operations, with no code branching on their shape.
3. **The step-7 test** — a seeded rule is revised on evidence and trust, through the machinery, with
   no hand edit. This is the thesis observation.
4. **The coverage test** — set a bar on the fifty-sentence drill, in advance: what proportion of
   ordinary sentences must fit the fixed schema *without abstention*? A format that abstains on a
   third of natural language is not computable, it is narrow.
5. **The no-regression test** — everything v1 answers correctly, v2 answers correctly. The empirical
   corpora (`tests/`, `doc/ref/test-feedback.md`) are the ratchet.

**Failure criteria, equally explicit:** if the inheritance ledger converges on *rebuild everything*;
if the coverage bar cannot be met without unbounded slots; or if A proves to require the state layer
(§6.3) to be so large that it is a separate project — then the honest answer is that tk2 is a set of
migrations to v1, not a successor, and it should be executed that way.

---

## 9. How we work on this

- **Alternating phases.** v1 continues and keeps producing findings; tk2 is conception. The parallel
  is deliberate: the classic failure mode of a second system is over-generalizing from the first, and
  keeping the first *alive* is the mitigation.
- **Blueprint from zero, migrate in place.** The design freedom comes from writing the spec without
  regard for what exists. It does not require a parallel codebase — that would double maintenance and
  officer cost to rebuild the parts that are already correct.
- **Rules are current-best, not law.** The Captain's principle, this session: *we are not building an
  internet banking backend, we are building a being; the rules we set are rules, and like every rule
  they are mutable. We stick to them until a better one comes, and through exchange we discover
  whether the better one is really better or merely an illusion.* The QM's standing duty follows from
  it: **surface a standing decision that has gone stale, rather than quietly obeying it.** The
  carve-out: the operational safety rules (commits, daemon restarts, `--apply` writes) change when
  the Captain changes them out loud, never by inference.
- **Documents live here.** Anything referenced by the blueprint gets a file in `doc/tk2/`.

### The requirements method (the author's, 2026-08-11 — it started as an experiment and worked)

**One component per folder. Two kinds of file in each.**

```
doc/tk2/<component>/YYYYMMDDHHMM_notes.md   the dialogue that produced the thinking, dated, kept
doc/tk2/<component>/requirements.md         SUPER synthetic — what the design must respect
```

The opened folders and their statuses live in **the components register** below. The notes accumulate
one file per session; `requirements.md` is the single living distillation.

**How the dialogue is run, because the FORM is doing the work.** Strictly one-line turns, Socratic,
author leads. The author's reasoning for the constraint: both parties talk too much — he from bias,
the QM from having more references to reach for — and brevity strips the references away, forcing
(a) strictly on-topic, no detours, (b) super-logical. Observed effect after the first session: short
turns force a POSITION per turn instead of an enumeration of options, which is what let three of the
QM's positions be refuted inside the same session (a second permitted-vs-possible axis collapsed to
one by «forbidden by whom?»; an ACT reading of the zip dropped as merely semantic; computability
corrected to comparability). A long answer would have hidden all three inside hedges.

**Why it matters beyond tidiness:** with the requirements complete per component, *designing* tk2 is
nearly mechanical and *implementing* it is more mechanical still. The thinking is the expensive part,
so it is the part that gets the dated files.

### The components register (closed 2026-08-13)

The full list of tk2 components, in order of foundationality — each gets its folder and its
requirements when its session comes. Sixteen, and the list is **closed** (extending it takes a new
argument, not a new whim). One convention per row: **(`folder` · status · done_date)** — the folder
holds the item's requirements regardless of status; status ∈ todo | ongoing | done; done_date is the
close date if done, else null.

| # | Component | One line | Folder | Status | Done |
|---|---|---|---|---|---|
| 1 | **dictionary** | the two-matrix base (R stated · D topical) + the senses over it | `dictionary/` | done | 2026-08-12 |
| 2 | **tkzip** | the fixed-size format — one shape, three readings | `tkzip/` | done | 2026-08-22 |
| 3 | **rules** | behaviour as zips, urge collapse, the three action categories | `rules/` | done | 2026-08-11 |
| 4 | **brain** | orchestrator of inner actions; the loop is dna, the how is kb | `brain/` | done | 2026-08-13 |
| 5 | **heart** | the emotional reward family — empathy as machinery, attachment as kb | `heart/` | done | 2026-08-22 |
| 6 | **evaluator** | the KB's door — truth, WSD, the math of the operators; the one mandatory rung | `evaluator/` | todo | null |
| 7 | **parser/compiler** | ONE station: surface language → tkzip, sense slots left open | `parser-compiler/` | todo | null |
| 8 | **rag-in/rag-out** | the rag abstraction — typo repair, translation, rephrasing in; polish out | `rag/` | todo | null |
| 9 | **micro-nn** | the instinct framework: blackbox micro-deciders over iterated thresholds, fenced below rules | `micro-nn/` | todo | null |
| 10 | **senses** | the connectors — his I/O to the outside world | `senses/` | done | 2026-08-23 |
| 11 | **data-modeling** | schemas and entities — WHAT the rows are (absorbs mem-as-data; retrieval *policy* is brain's) | `data-modeling/` | todo | null |
| 12 | **datatier** | the IO abstraction — HOW rows move | `datatier/` | todo | null |
| 13 | **body** | the interpreter of the db: boot cache, slow-tick refresh, migrations, deploy | `body/` | todo | null |
| 14 | **stack** | which modules, components, tech | `stack/` | todo | null |
| 15 | **tooling** | the workshop — instruments, curation, migration scripts, observability; since dev IS writing db, this is where development happens | `tooling/` | todo | null |
| 16 | **website** | tokeniko.online, the public window — one-way publish, never a sense | `website/` | todo | null |

Status calls worth their reasons: **tkzip closed 2026-08-22** — the compound / double-geometry layer
(deferred twice on 08-12) was held as its own chapter (reqs 12–17: composition not centroid, the
figurative sphere, crystallization, epoch-stamped points, one law both floors). **rules is done** —
the 2026-08-11 session was argued to conclusion; #13 was propagation from the dictionary, not a
reopening. Open items inside a done component's requirements do not reopen it — done means the
conception session closed, exactly as dictionary carries its OPEN-at-close list.

### The road to the build (agreed 2026-08-13)

Four phases, strictly in order, with one standing amendment:

1. **Requirements** — finish the sixteen sessions above; reconciliation ritual at every close
   (dictionary → tkzip → rules → … — each new set is audited against its roots).
2. **The project** — each component expands into a well-defined subproject; the macro-roadmap of
   EPICS, with dependencies and build order.
3. **The plan** — every epic broken into tasks, each task with its officer briefing.
4. **The build** — a cluster of first-officiers executes the plan.

**The amendment (QM's, agreed):** the cluster never runs open-loop. Between epics, **vertical proof
slices** — one sentence driven end-to-end (parser → zip → evaluator → brain → say) as early as the
dependencies allow — because requirements prove seams on paper, but only an instrument proves them in
the wild, and a wrong seam found at epic 12 costs the cluster. Each slice lands under the Captain's
eye before the next stretch.

---

*Opened 2026-07-31. Step 0 by the QM, from the session that argued hunch 21 into a keystone.* 🜂
