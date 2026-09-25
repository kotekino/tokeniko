# parser/compiler — THE UD GATE OPENS, 2026-09-15 12:59

*Roadmap: `E3.5.1.1`*

*The first scoring run. 25 cases over 16 of UD's 37 relations: **16 answered · 0 wrong · 9
abstained**, and stanza agrees with UD's own published parse on 9 of the 12 sentences UD annotated
in full.*

---

## WHAT THE GATE IS, AND WHY THE DRILL IS NOT IT

E2's drill is the **format's** gate: 78 hand-compiled sentences proving tkzip can HOLD the world,
with no parser anywhere in it. It says nothing about whether a skeleton was read correctly. This is
the **station's** gate, and the Captain ruled it on 2026-09-15: *«take all the examples from
`universaldependencies.org/u/dep/` and `/u/pos/` and make our combo work good and consistently.»*

Both ends are CLOSED — **37 relations in**, 18 tkzip roles and 10 operators and the five-element
prefix out — which is what makes the 37 → 18 table completable rather than merely large, and what
makes «not yet reached» a list of names rather than a shrug.

**IT REPORTS THREE NUMBERS AND THE THIRD IS THE POINT.** Answered · **WRONG** · abstained. Only the
middle one is a defect: *«half understood is legal, wrongly understood is the sin»* (req 8). An
abstention is a diagnosis and is never averaged into a score that would hide it.

**AND COVERAGE IS REPORTED APART**, every run, by name. A gate scoring 100% on the sixteen relations
someone happened to transcribe would be measuring its own corpus. Not yet reached (21): `amod appos
ccomp clf conj csubj dep discourse dislocated expl flat goeswith list nmod nummod orphan parataxis
reparandum root vocative xcomp`.

## THE CORPUS IS TRANSCRIBED, NOT INVENTED

Every sentence is from `universaldependencies.org/u/dep/<rel>`; where the page prints the parse
(`case(Chair-2, 's-3)`) the heads and labels are the page's, converted from its 1-indexed
head-0-is-root convention. **12 of 25 carry UD's own annotation** and the rest say `annotated=False`
where the missing columns are stanza's. *An origin that cannot be read is not documentation* — the
rule that produced `CLAUDE.md`, applied to someone else's document.

## WHAT THE GATE FOUND — four defects, none of which reading the code would have shown

**1. `obl:agent` SETTLES `by`, AND THE LABEL IS ON THE HEAD.** UD: *«obl:agent — used for agents in
passive constructions»*. `by` is instrument/agent/path/time in the table and unanswerable from the
row alone; «the cat was chased BY the dog» is `case(dog, by)` **+ `obl:agent(chased, dog)`**. The
marker's own dep is `case` in every such sentence and says nothing — **the head's dep is what
speaks.** `read()` gained `head_dep`, and `UD_DEP_SETTLES_ROLE` is the narrow frame map for it:
every entry is a relation whose UD definition NAMES the role, so it is a reading of UD's
documentation and not a judgement about English. **One of the thirteen ambiguous markers, solved by
the standard rather than by us.** Guarded: a subtype naming a role the form cannot fill is a
disagreement to report, never a role to invent.

**2. THE POSSESSIVE CLITIC WAS TYPED AS GLUE.** UD analyses «the Chair **'s** office» as `case('s)`
+ `nmod(office, Chair)` **and pairs it explicitly with «the office OF the Chair»** — the same
relation, two spellings. `db/0008` had `'s` compiling to `structure`, which threw the possessor
away. tkzip keeps the possessor INSIDE the record as `Box.relation` (req 26), so it compiles to a
**FIELD**, not a box and not nothing. *The pairing is what makes this a defect rather than a
preference: UD says the two spellings mean the same thing, and the table made one of them vanish.*

**3. PLAIN COPULAR `be` WAS MOVING THE THEATRE.** Requirement 31 and the Captain's own first draft:
«the cat is cute» is *cat + cute, **no verb***. The rows had every form of `be` typed `tense_aspect`
→ theatre. It now compiles conditionally — **`structure` under `cop`, theatre otherwise** — because
one row cannot tell copular `be` from auxiliary `be` («she is running», `aux`) or from existential
`be` («there is a cat», which IS content). **The dependency is what tells them apart**, so the row
states both readings and NAMES the relation that chooses.

**4. TWO OF MY OWN TRANSCRIPTIONS WERE ASKING THE TABLE THE WRONG QUESTION**, and correcting the
corpus was the right fix rather than bending the code:

- «when do you sleep?» — I expected `time`. A wh-word OPENS a slot; **which** box it opens is the
  compile core's answer. The row can only say «this leaves something open», which is what it says.
- «she gave me a raise» — I expected `recipient` of the marker table. There IS no marker: the role
  comes from `iobj`, exactly as agent and patient come from `nsubj`/`obj`. What the table owes is
  «this pronoun resolves to an entity».

**Both are the same error**, and naming it is worth more than the two fixes: **the 37 → 18 mapping
has two halves.** Roles that arrive with a MARKER (location, time, instrument, …) are the closed
classes' business; roles that arrive by RELATION (agent, patient, recipient) are the compile core's.
The table proves the split by holding no marker for `patient` or `experiencer` — and the relation
half is now transcribed beside the cases as `RELATION_FILLS_ROLE`, so the mapping is one document
even though it will be two implementations.

## «TAKE STANZA AS CLOSE ENOUGH AND CHECK» — the checking, with a number

    agrees with UD's published parse   9 of 12
    differs                           3
    not comparable (tokenization)     0

None of the three is nonsense, and two are stanza being MORE specific than the page:

    the Chair 's office        stanza nmod:poss   UD published nmod       (a subtype, not a conflict)
    if you know … tell me      stanza iobj        UD published obj        (defensible either way)
    The cafe up beside …       stanza advmod      UD published case       ← a real disagreement

The third is the one to keep: UD prints that sentence precisely to show **two `case` markers on one
nominal**, and stanza reads the first as an adverb. *«Close enough» is now a measurement rather than
an assumption, which is what the ruling asked for.*

## STILL OPEN, NAMED

- **21 of 37 relations have no case yet.** The list is printed every run.
- **The thirteen ambiguous markers** are still ambiguous where no UD subtype settles them: «I talked
  **to** my friend» (destination|recipient) and «I swam **in** the pool»
  (location|time|instrument|manner) both abstain. That is the head-verb geometry, and it needs the
  dictionary in the loop.
- **`mark` under a reporting verb** («he says **that** you like to swim») opens a POV, not a join —
  E2 made attitude a prefix element with its own holder, and the station has no rule that emits one.
- **stanza splits «Every cat except Tom sleeps.»** into two sentences at the exceptive marker. A
  provider defect, logged rather than worked around.

*Run it: `PYTHONPATH=. ../.venv/bin/python tools/ud_gate.py [--db tokeniko_tk2] [--live]`. Offline by
default, because the corpus and the table both ship with the code and a measurement that needed a
body would not run before an apply. `--live` adds the stanza comparison and needs the models.*
