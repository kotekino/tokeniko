# parser/compiler — THE ATTRIBUTIVE ADJECTIVE, AND A SLIP THE DRILL WOULD HAVE CAUGHT, 2026-09-16 12:15

*The frontier's biggest gap, and the least design work of anything in E3 — because **tkzip already
ruled it and the drill already hand-compiled the shape.** The whole job was reading what was there.
On the way, comparing the two turned up a role the compile core had got wrong since the day it was
written.*

**Ratchet 23 of 25, 98.9%** (from 22 and 98.4%). **Frontier 7 of 18, 80.8%** (from 6 and 76.6%).
**Gate: 31 answered · 0 WRONG.**

---

## THE SHAPE WAS NOT DESIGNED HERE

Requirement 70, written at E2's self-audit:

> *«Attributive adjectives are SECOND ROWS, not a field — «a human body» is ∃B(body(B) ∧ human(B)),
> the same machinery as the depictive «he ate the fish raw». `degree` is for «very big», an
> intensifier on a property, and conflating the two was a QM error the drill's self-audit caught.»*

And the drill hand-compiles it, for «I live in a human body in Japan»:

    ∃B restricted to body.n, scoping the JOIN
    hu:  patient = B, complement = human.a
    me:  live.v, agent = me.n, location = (B, marker «in»)
    j1:  AND (hu, me)

**Three things in that are not obvious and all three are load-bearing.**

1. **The adjective row has NO PREDICATE** — req 31, «the cat is cute» is cat + cute and no verb.
2. **Its subject is the PATIENT**, which is the copular row's shape.
3. **The binder scopes the JOIN, not either row.** The variable lives in both, and a binder over one
   of them would leave the other's `B` unbound. `_box_for` raises the binder scoping the content row
   because that is all that exists when it runs; `_modify` moves it once the join is built.

**An adjective FORCES a binder even where no quantifier word appears**, and that is the part worth
saying out loud. A row reading `patient = body.n, complement = human.a` would claim that BODIES are
human — a statement about the kind, not about this one. There is no way to say «this particular body,
which is human» without a variable, so the adjective raises the binder req 36 already provides.
EXISTENTIAL, with the phrase's own determination riding beside it — which is exactly what req 26
split determination from quantity for. *(A bare plural — «large dogs» — is genericity, which E2
parked. It reads existential here, and that is an honest approximation rather than a silent
universal.)*

## ONE TREE PER CLAUSE, WHICH THE FIRST DRAFT DID NOT DO

«Large hot dogs» chains correctly on its own — AND(hot, AND(large, eats)) — because both adjectives
share one binder. **Two MODIFIED NOUNS did not.** «The big cat chased the small dog» produced two
joins that both named the content row:

    j0  AND (m0, r0)        j1  AND (m1, r0)

Logically sound — both are claimed, and each binder's scope covers its own variable — and **not what
the drill does**, which chains j1, j2, j3 into a single conjunction. A zip with two unrelated
top-level assertions says the same thing in a shape nothing else in the format uses, and an evaluator
walking it would have to learn a second convention for no gain. So the modifier joins chain per
clause, and every binder raised in that clause scopes the outermost join:

    q0 binds x0 (cat.n)  scopes j1        j0  AND (m0, r0)
    q1 binds x1 (dog.n)  scopes j1        j1  AND (m1, j0)

Their ORDER is untouched, and row order is scope order (req 35) — so the prefix still reads left to
right as the speaker said it.

## THE SLIP: `topic` WAS NEVER THE COPULAR SUBJECT

Building this meant reading the drill's copular row, and the drill does not agree with the compiler.

The compile core reasoned its way to `topic` on 2026-09-15: *«nobody is acting — the subject is what
the complement is said OF. That is topicality, not agency.»* **The English is right and the role name
is wrong.** In THIS inventory `topic` is SUBJECT MATTER — the thing «about» and «on» mark, «a lecture
ON physics» — and that is the only way the drill uses it, three times: «I love thinking», «I know X»,
«to see the Ligurian sea».

E2 ruled the copular row outright (`202609111511_notes.md`):

    | row | POV | patient | complement |

and the drill hand-compiles **43 rows** in that shape. A lone deviation in code, against the format's
own gate, is the deviation that moves. It is `patient`.

**AND NOTHING WOULD HAVE CAUGHT IT.** The drill validates hand-written zips with no parser involved;
the UD gate compiles UD's sentences and never looks at the drill. **The two gates have never met**,
and a role the station puts in every copular sentence was wrong for a day without a single test
going red. That is a missing control, and it is now a task rather than a lesson.

## WHAT MOVED, AND WHAT DID NOT

    ratchet   22 -> 23 of 25   98.4% -> 98.9%
    frontier   6 ->  7 of 18   76.6% -> 80.8%
    gate      30 -> 31 answered, 0 WRONG throughout

«Last night, I swam in the pool» is whole for the first time: `Last` is an `amod`, so the TIME box
now holds a VARIABLE restricted to `night.n` with «last» asserted of it in a row of its own. The same
mechanism, the same day, on a sentence that had been 86% since the compile core landed.

**What is still unplaced is no longer adjectives — it is ADVERBS.** `early` in «left early in the
morning» and `here` in «they come here» are content words with no home, and they are the adjectives'
problem one part of speech over. That is the next small piece, and it is not the same piece: an
adverb modifies the PREDICATION, not a nominal, so it does not raise a binder and its row (if it is
a row) says something about the event rather than about a participant.

## ON THE FRAME/KNOWLEDGE AUDIT

This piece put one default in code — an adjective-raised binder is EXISTENTIAL — and one POS test
(`amod` on `ADJ` or `VERB`, the participial «the sleeping cat»). Neither is a SET, so neither is the
shape the rule was written against; both are named here so the end-of-epic audit has them.
