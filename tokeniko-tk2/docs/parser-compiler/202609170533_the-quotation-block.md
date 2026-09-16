# parser/compiler — THE QUOTATION BLOCK, AND THE ROTATION FOUND INVERTED, 2026-09-17 05:33

*Nine hand-compiled sentences with quotation marks in them, added to the drill because schema v3 had
gained a field nothing held it to account for. They found three things, and the first one is that
**we had the rule backwards**.*

**Drill 87 sentences** (from 78). **Drill gate: 47 agreed · 15 DISAGREED · 25 no common ground**,
roles **98 of 129** (from 71 of 138 — the gate was measuring blind, see below).

---

## WHAT WAS ASKED, AND WHY IT WAS NOT DECORATION

> *«For the drill, you can create few random sentences with quotes.»* — the Captain, 2026-09-16

Schema v3 added `addressee` to `Pov` and `AttitudeRow` **the same day**, under req 73, to carry his
own sentence. Twenty-four hours later the field had a station that wrote it, a test that read it, and
**no hand-compiled truth to be wrong against**. A field the drill never exercises is a field nobody
has checked — so the nine cases are the format's witnesses for req 20, not more attitude examples.

The bar and the scoring rules are untouched. The size is amended in the bar doc, dated, with the
reason, per that doc's own rule.

## FINDING 1 — QUOTATION ROTATES, REPORTING DOES NOT, AND WE HAD IT EXACTLY THE OTHER WAY ROUND

    «John said to Marie that you are late.»     the LISTENER is late      station says: Marie
    «John said to Marie "You are late".»        MARIE is late             station says: the listener

**Both are wrong, and they are wrong in opposite directions.** The rule in English is not about
attitudes at all: inside quotation marks the original speaker's deictic centre is preserved, so «I»
is the holder and «you» is the addressee. In reported speech **the reporter has already done that
work** — that is what reporting IS — and rotating a second time moves the sentence onto the wrong
person while looking entirely confident. A silent-wrong, in the drill's own vocabulary.

**HOW THE INVERSION HAPPENED IS INSTRUCTIVE.** `_contexts` rotates a clause when its joiner says
`asserts: matrix`. That flag lives on the word «that» — so it is present in exactly the indirect
case, where rotation is wrong, and absent from a bare quoted `ccomp`, where it is right. *We keyed
the rotation on the one signal that is anti-correlated with it.*

And the note that recorded the rule the day before states it wrongly in its own worked example
(`202609161544_the-rotation.md`, «John said to Marie that YOU swim → marie.n»), as does the test that
guards it (`test_the_rotation_inside_ONE_sentence`). **This was not the Captain's ruling** — his was
(a) versus (b), where the addressee LIVES, and it stands. The English was mine and it was wrong. Both
are corrected. **The test is not deleted and not fixed**: it is renamed to say what it is —
`test_the_rotation_inside_one_sentence_IS_INVERTED_and_this_pins_it` — so it pins the wrong behaviour
and goes RED the day somebody makes it right, which is the only way a known defect stays loud in a
green suite.

**IT ALSO EXPLAINS A THING WE THOUGHT WE KNEW.** 2b.2 measured that «stanza splits a quote», and the
whole frame-across-a-sentence-boundary machinery was built on it. Measured again on these nine:
**stanza splits a quote only when the quotation marks are spaced away from their words**. All nine
arrive as ONE skeleton with the quote as a `ccomp`. The cross-boundary path is the exception, not the
rule — so the fix belongs in `_contexts`, where the rotation is actually decided, and the two paths
need the same test.

## THE FIX — AND THE CAPTAIN REFUSED THE QUESTION, CORRECTLY

The QM brought him one: the correct signal is the quotation marks, which characters count is a SET,
and the rule of 2026-09-16 says a set does not go into a `.py` file without asking — **frame or
knowledge?** The recommendation was knowledge, on the grounds that `«»` is Italian, `„“` German and
`「」` Japanese.

**He refused the premise, and he was right on three counts:**

> *«Do we parse directly the input sentence? Not through spacy-stanza, which already has the tooling
> to isolate the quote? Also: do we parse anything else than English — the input on the parser is
> always English, the translation layer stays on the senses. Basically: I find it weak to care about
> what a quotation symbol is. We shouldn't have this problem in the first place: meaning if we have
> it, something went in the wrong direction.»*

1. **We do go through stanza**, and the QM never asked what it was already saying.
2. **The station parses English only.** Translation is the senses layer, via RAG. The multilingual
   argument was imported from a layer that is not this one.
3. **Needing the set at all was the smell.**

**MEASURED, AND THE SIGNAL IS STRUCTURAL:**

    John said to Marie "You are late".      late/ccomp    punct  "  before the span,  "  after
    He replied “I am late” quickly.         late/ccomp    punct  “  before,            ”  after
    She said 'I am here' loudly.            here/ccomp    punct  '  before,            '  after
    John said to Marie that you are late.   late/ccomp    NO punct anywhere on the clause

Stanza has already isolated the quote. **So `_is_quoted` asks whether the clause's SPAN is bracketed
by punctuation, and never reads a character.** Curly quotes, straight quotes and apostrophes all work
because none of them is looked at. The test is on the span rather than on the head's own children
because the two marks do not reliably share a parent — in «Bob told me "I trust you"» the opening
mark hangs off the root and only the closing one off the complement.

**THE LESSON IS A SHARPENING OF HIS OWN RULE.** *Its failure mode is not only hard-coding a set. It
is NEEDING one.* A question of the form «where should this list live» is worth one more question
first: **why is there a list?**

## AND TWO MORE THINGS THE FIX NEEDED, BOTH FOUND BY MEASURING

**The rotation must NEST.** «Marie said "John told me 'you are late'"» rotates three times and each
level reads the one above it: the «me» inside Marie's quotation is MARIE, which makes her the
addressee of John's telling, which makes the «you» inside THAT quotation her again. Walking the
clauses in sentence order and resolving every one against the OUTERMOST context got the innermost
pronoun wrong by exactly one level — it named the narrator. The clauses are now walked outermost
first, and each reads its enclosing clause's already-rotated context.

**A rotation must name the same somebody the ROWS do.** Taking the holder's key straight off the word
gave `i.n` for «me» while the box for that same token held `me.n` — so the quoted «you» resolved to
an identifier appearing nowhere else in the zip. A pronoun carrying a `person` feature is now
resolved through the outer context exactly as `_compile_word` resolves it.

## FINDING 2 — THE GATE COULD NOT SEE ANY OF THIS, TWICE OVER

The drill gate was built on 2026-09-16 and the quotation block walked straight past it. Two separate
blindnesses, both closed:

**It passed no context.** The station resolves a first- or second-person pronoun against the context
it is handed and returns the bare closed-class key when handed none — so every pronoun in the drill
compiled to itself and the person axis was invisible by construction. The gate now passes
`DRILL_CONTEXT = Context(speaker="me.n", addressee="you.n")`, which is not a choice: it is **the
drill's own convention**, which hand-compiles «I» as `me.n` and «you» as `you.n` throughout. Every
unrotated sentence therefore compiles to exactly what it compiled to before, and only the rotation
moves. *Roles agreed went from 71 of 138 to 98 of 129 — the missing 27 were pronouns that had never
been compared to anything.*

**It could only see half a disagreement.** The gate paired boxes by their FILLER and asked whether
the two zips gave it the same ROLE — the shape of the `topic`/`patient` defect it was built for. The
person axis fails in the mirror shape: the right role holding **the wrong somebody**. «that you are
late» compiled about Marie is an ordinary `patient` on an ordinary row. Both tests now run, and
neither implies the other.

That second one is worth saying plainly: **an instrument built to catch one defect caught exactly
that defect and was shaped by it.** The gate is a day old and has already needed widening twice.

## FINDING 3 — THE TRUTH SLOT UNDER AN ATTITUDE. **RULED: THE ROWS KEEP THEIR TRUTH**

The station emptied the truth slot of anything under an attitude (`quoted_under`, and the `ccomp`
path). **The drill never has**: `dere-1` carries a cat at truth 1.0 under «he thinks», `dere-3` a
marriage under «he wants», `aw-11` a hungry cat under two nested attitudes. The prefix is what keeps
the row out of the world; the truth slot says what the HOLDER does with it.

Emptying it lost a distinction the format otherwise has for free:

    John said "The sky is green."      the holder ASSERTS it        truth = 1.0   (q-8)
    I asked Anna "Where do you live?"  the holder ASKS it           an OPEN box   (q-7)
    John said "Close the door!"        the holder WANTS it          truth = None  (aw-21)

And it matters downstream rather than only formally: **«John told me X»** (I may believe it, if I
trust John), **«John asked me X»** (I should answer) and **«John told me to do X»** (I may act) are
three different things to the brain, and one blanked slot made them the same row.

**The Captain ruled the drill's side**, and the station moved — the `unasserted.add` in both attitude
branches is gone, and `quoted_under` no longer rewrites. *A lone deviation in code, against the
format's own gate, is the deviation that moves* — the same ruling as `topic`/`patient`, on the same
grounds, eight days apart.

**AND IT IMMEDIATELY EXPOSED SOMETHING THE BLANKING HAD HIDDEN.** «Is the cat hungry?» compiles with
**truth = 1.0**, where the schema's own docstring says *«Is the cat hungry?» has every box bound and
its truth OPEN*. The station never opens the truth of a POLAR question — wh-questions open a box and
are fine, `whether` opens the truth from its marker row, and the bare AUX-fronted polar has nothing
that fires. It was invisible while everything under an attitude was blanked anyway. **Named, not
fixed here**: it is a mood question, not a truth-slot question, and it is now a task with a witness.

*Making a slot mean something is how you find out who was not filling it.*

## WHAT ELSE THE CONTEXT TURNED UP, FREE

Giving the gate a context took the subject-role question from **three witnesses to nine**
(`exist-3` `t-ws-1` `t-ws-8` `t-dc-4` `t-of-1` `t-mo-1` `aw-11` `aw-16` `aw-20`) — every one of them
a pronoun subject the gate had never been able to compare. *«I go to sleep because I'm tired»,
«You learn only from minds you trust», «As a doctor I disagree».* The question has not changed and
it is still the geometry's: **what the subject's role is depends on what is predicated of it.** But
it is now the largest single family in the ratchet, and that is an argument about when it gets built.

And `aw-15` appeared: «In Italy, you may drive in France with a foreign licence» puts Italy in
`location` and displaces the France that belongs there. The station builds no `DomainRow` yet — E3
unfinished — but it shows as a CONFLICT rather than as a missing row, because the wrong filler
reached a real box. Worth knowing: an unbuilt feature is not always a silent gap.

## ONE CASE THE FIX DOES NOT REACH, AND WHY IT IS NOT THE SAME BUG

`q-5` — «John said to Marie "You are late".» — still produces only the saying, with the quote's
content missing entirely. **Stanza parses the quoted `late` as `appos` on Marie**, not as a `ccomp`
on `said`, so there is no complement clause for the rotation or the attitude to find. Nothing in the
person axis can help: the reading never reaches it.

It is worth keeping visible rather than filing under «stanza is imperfect», because it is the same
family as the three relations stanza never produces (`goeswith`, `orphan`, `reparandum`) and it sets
the shape of the answer: **where the provider gives us a structure we know to be wrong, the station
abstains rather than compensates.** `q-5` reads as MISSING in the gate, which is exactly right.

## THE LEDGER

    drill            78 -> 87 sentences (amended in the bar doc, dated)
    drill gate       44 agreed ·  4 DISAGREED   before the context and the mirror test
                     47 agreed · 15 DISAGREED   after — 11 of the 15 were always there
                     50 agreed · 12 DISAGREED   after the two fixes, same morning
    roles agreed     71/138 -> 98/129 -> 101/128
    fixed            the rotation (q-4 q-7 q-9 resolved; q-2's rotation is right and what remains
                     of it is the subject-role question) · the truth slot under an attitude
    opened           the POLAR question never opens its truth — found by fixing the truth slot
    refused          «which characters are quotation marks» — the wrong question, and the right
                     answer was that stanza had already parsed it
