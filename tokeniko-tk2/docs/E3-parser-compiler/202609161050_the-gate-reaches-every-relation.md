# parser/compiler — THE GATE SCORES THE ZIP, AND REACHES ALL 37, 2026-09-16 10:50

*Roadmap: `E3.5.1.3`*

*The gate was measuring half a station. Its own docstring said so — «roles that come from a relation
rather than from a marker are not its job yet» — and that was honest in September when the
closed-class table was all that existed. **It stopped being honest the day the compile core landed**,
and it was blocking: the twenty-one relations still unreached are almost all COMPILER questions, and
a gate that only asks the table cannot ask them.*

**43 cases · every one of UD's 37 relations · 30 answered · 0 WRONG · 13 abstained.**

---

## WHAT CHANGED: IT COMPILES THE SENTENCE NOW

The old gate asked `ClosedClasses.read` what a token was. The new one **compiles the skeleton and
looks the token up in `Compiled.placement`** — the compiler's own record of where each word went.

That record is the piece that had to be built first. A `set` of covered indices answers *how much of
this sentence was understood* and nothing else; it cannot tell a role from a prefix from a row, so
«what does `amod` become» had no way of being asked. `Placements` carries a LABEL beside each index
— `box:location`, `prefix`, `join`, `predicate:r1`, `field:relation`, `marker`, `structure` — and
behaves as the set it replaces, so no existing call site moved.

**It is also what requirement 4 wants.** «Which word became which part of this zip» is the question
the confidence scalar asks, and the question requirement 3 means by a reading that can be handed
back. It was going to be built either way; the gate is what made it urgent.

**The `expect` vocabulary did not move**, and deliberately: a case still marks the MARKER and still
expects a ROLE. Re-pointing twenty-five transcribed cases at their nominals would have been editing
the corpus to suit the instrument.

## THE TRACE FOUND FOUR DEFECTS BEFORE A SINGLE NEW CASE WAS ADDED

**1. THREE WORDS «REACHED NO PART OF THE ZIP» IN SENTENCES THAT COMPILED AT 100%.** `of`, `'s` and
`beside` were being covered by `covered.add(index)` with nothing said about where they went — *counted
as understood without saying what they became*. The coverage number was not lying, but nothing behind
it could be checked. **A trace that records nothing is a trace that cannot be wrong**, and that is
the whole reason to label.

**2. «The cafe up beside the lookout» SAID THE CAFE BELONGED TO THE LOOKOUT.** `nmod` under a noun
was read as a possessor unconditionally. It is not enough: «the office OF the Chair» is a possessor,
«the cafe UP BESIDE the lookout» is a LOCATION, and **the marker decides — exactly as it does under
`obl`**.

*And the marker is ASKED, not listed.* A `{"of", "'s"}` in Python would have been a hand list in the
one file whose purpose is to end them — **the Captain's rule of the same morning**: *before a set
goes in code, frame or knowledge?* The rows already say it. `'s` compiles to `field: relation`;
`db/0012` gives `of` the rule «head is a NOUN → relation». So the test is *what does this marker
produce here*, and a new possessive spelling is a migration. **The rule earned its keep on its first
day.**

**3. «out of the box» THREW THE MARKER'S MEANING AWAY AND KEPT ITS SPELLING.** A non-verb root
defaulted to `complement`; the marker `out of` says SOURCE. `_role_of` gates on `NOMINAL_DEPS` and
`root` is in none of them, so a root could never reach its own marker. **The copula is the exception
and by construction**: in «Sue is a teacher» the root IS the complement (req 31), so there the marker
does not get to override.

**4. A VOCATIVE WAS MERELY UNPLACED.** E2 ruled it in the drill — *«the vocative is addressing, not
content»* — so it must compile to NOTHING on purpose. A word left out and a word that compiles to
nothing are different answers, and `Zip.unplaced` is for the first.

## ALL 37, AND THREE STATES INSTEAD OF TWO

Eighteen cases added, one per relation, each transcribed from that relation's own page and then
parsed by stanza and **checked against the published edge**.

    covered by a case        34
    do not arise in English   2   clf · dislocated — UD's own pages print no English example
    UD's own abstention       1   dep — «we could not decide which relation this is»
    not yet reached           0

*«We have not got to it» and «it does not arise in English» are different states, and folding the
second into the first makes the coverage number a lie in the flattering direction — while folding it
the other way makes the gate look permanently incomplete for a reason nobody can fix.*

## THE PROVIDER MEASUREMENT REQUIREMENT 2 ASKED FOR, AT A SECOND GATE

**Stanza produces 15 of the 18 relations UD publishes on these sentences.** The three it does not are
one family:

    goeswith    UD: goeswith(with-4, out-5) for the typo «with out»  ->  stanza reads a second `case`
    orphan      UD: orphan(Peter, bronze) for the gapped «and Peter bronze»  ->  stanza reads `compound`
    reparandum  UD: reparandum(left-7, righ--4) for a self-correction  ->  stanza reads `nmod`

**A typo, a gapping and a self-correction.** So the station will never meet these three labelled from
this provider, and building handling for them would be building against a label that never arrives.
That is worth knowing before it is built, and it is the second time req 2's *«close enough is a
measurement E3 owes»* has produced a number rather than a hope.

## WHAT THE GATE NOW NAMES, WHICH IS THE POINT

The corpus splits into a **ratchet** (the 25 cases that existed before: **22 whole, 98.4%**, and they
may never get worse) and a **frontier** (the 18 added today: **6 whole, 76.6%**, and it is meant to
climb). One averaged figure would let a real regression on the old cases be paid for by a lucky gain
on the new ones.

The frontier's gaps, by size:

- **`amod` — attributive adjectives, five cases.** Requirement 70 already rules them: *«attributive
  adjectives are SECOND ROWS, not a field — «a human body» is ∃B(body(B) ∧ human(B)), the same
  machinery as the depictive»*. The station does not build them, and «Last night» leaving `Last`
  unplaced is the same hole from the other side. **This is the next piece.**
- **`flat` and `list` — one name across several tokens.** «Hillary Rodham Clinton» is one individual,
  and the station must not mint three. That is E3b arriving by another route.
- **`xcomp` — the named gap.** It is deliberately not a clause («nobody asserts that you swim») and
  what it IS instead has never been ruled. The zip says so by leaving the verb unplaced.
- **`nummod` — the box's own `count` field** (req 26). A numeral is not a quantifier and not a
  determination.
- **`appos`** — one individual under two descriptions; unruled, and it leans on E3b.

## ON THE FRAME/KNOWLEDGE AUDIT

This piece added one set to code — `DEPS_THAT_COMPILE_TO_NOTHING`, currently `{"vocative"}` — and it
is **on E3's audit list before it was written**, beside `CLAUSE_DEPS`, which it resembles exactly.
The reading «a vocative is not content» is a ruling, and a ruling is a row. Named here rather than
discovered at the end.
