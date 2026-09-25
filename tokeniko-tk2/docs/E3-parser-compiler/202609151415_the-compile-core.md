# parser/compiler — THE COMPILE CORE, 2026-09-15 14:15

*Roadmap: `E3.2` · `E3.2.4`*

*A skeleton in, a zip out. **18 of 25 UD cases compile at 100% coverage, mean 89.5%** — and the
seven partials are all one known gap: a sentence needing more than one content row.*

---

## WHAT IT DOES, AND THE TWO THINGS IT REFUSES TO DO

Fills boxes from the dependency tree; compiles the function words into structure. It does **not**
resolve senses — every `sense` slot is emitted OPEN, because binding is the evaluator's one
algorithm and the evaluator has a KB to check itself against (evaluator req 5). It does not decide
truth. *«The station consults the dictionary for SHAPE, never for MEANING.»*

## THE MAPPING'S TWO HALVES, KEPT APART IN ONE FILE

**BY RELATION** — `nsubj → agent`, `obj → patient`, `iobj → recipient`, `nsubj:pass → patient`. No
marker exists for these; English marks them by position, and the closed-class table proves it by
holding **no row for `patient` or `experiencer`**.

**BY MARKER** — `case` plus the closed-class row: «after the rehearsal» is a TIME box because the
table says `after` marks time.

*`nsubj` maps to `agent` and NOT to «agent or experiencer», deliberately: which one it is depends on
the VERB («the cat chased» against «the cat saw»), that is a head-verb question the geometry
answers, and a station guessing here would be doing the compile core's job badly instead of leaving
it open.*

## WHAT THE FIRST RUNS FOUND

**1. THE PASSIVE AND THE ACTIVE COMPILE TO THE SAME ROLES.** «the cat was chased by the dog» →
patient `cat.n`, agent `dog.n` via `obl:agent`, marker `by` kept (req 65). That is what *«roles
normalize»* means, working: the two sentences compare as one thought, and `topicality` is what keeps
the difference the speaker chose.

**2. BOTH SPELLINGS OF A POSSESSOR REACH THE SAME PLACE.** «the Chair 's office» and «the office of
the Chair» now produce the same zip — `head=office.n, relation=chair.n`. UD's `case` page pairs them
explicitly, and before `db/0009` the clitic spelling threw the possessor away entirely.

**3. A QUANTIFIER MUST BE BUILT WITH THE PHRASE IT RESTRICTS.** The first draft emitted a
`QuantifierRow` on meeting «every» — and the schema refused it: `restriction` is a **Box**, and the
phrase had not been read yet. The schema's own docstring says the shape: *«All cats are mammals»
becomes a binder for X restricted to cats, then a content row saying X is a mammal.* So the binder
is raised by `_box_for`, and the content row's box holds a **`Var`**. The frame caught a design
error in the compiler, which is what freezing it bought.

**4. THE COPULAR SUBJECT IS THE TOPIC, NOT AN AGENT.** «Sue is a teacher» has no predicate at all
(req 31 — *cat + cute, no verb*) and nobody is acting: the subject is what the complement is said
OF.

**5. A MULTI-WORD MARKER MUST COVER EVERY TOKEN IT SPANS.** «out OF the box» is one form and `of`
hangs off `out` as UD's `fixed`; marking only the first token left `of` looking unplaced in a
sentence that was completely understood. *A coverage number is only worth having if it is not
lying.*

## HALF-UNDERSTOOD IS LEGAL; WRONGLY-UNDERSTOOD IS THE SIN (req 8)

Three refusals, all normal output rather than error paths:

- a word that reaches no box lands in **`Zip.unplaced`** (req 21: recorded, never given a position
  it did not earn);
- a slot nobody can fill is **OPEN**;
- **an ambiguous marker abstains.** «I swam IN the pool» reads location|time|instrument|manner and
  nothing chooses, so no box is filled and the abstention is named. Picking the first candidate
  would be exactly the silently-complete nearest fit the requirement forbids — and «Last night» in
  the same sentence still binds, which is what «the caught parts stay bound» means.

## THE SEVEN PARTIALS ARE ONE GAP

    « he says that you like to swim »      57%    a POV and a second row
    « if you know who did it , tell me »   50%    a JOIN and two more rows
    « she was reading or writing »         60%    a JOIN
    « the cat that sleeps »                50%    a relative: a Var shared between rows
    « when do you sleep ? »                75%    the wh OPENS a box; which box is unsettled
    « I talked to my friend in the park »  75%    two ambiguous markers
    « Last night , I swam in the pool »    71%    one ambiguous marker

**Everything except the ambiguous markers is the same missing feature: the compiler emits ONE
content row.** A join, a relative clause and a reported speech all need two or more, plus a
`JoinRow` or an `AttitudeRow` to relate them. That is the next task, and it is named rather than
worked around.

*`tk2/language/compile.py`. Coverage is held by a test as a floor — 18 whole, 89.5% mean — so a
change that lowers it has to say why.*
