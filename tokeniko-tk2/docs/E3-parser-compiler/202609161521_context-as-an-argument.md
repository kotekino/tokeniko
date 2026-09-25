# parser/compiler — CONTEXT AS AN ARGUMENT, AND THE QUOTE THAT ARRIVES TWICE, 2026-09-16 15:21

*Roadmap: `E3.2.1` (its sub-tasks 1 and 2)*

*E3 task 2b.1 and 2b.2. **Requirement 7 was written when the chapter was conceived and has been
unbuilt ever since** — «nothing has needed it yet» is in the plan in those words. Two things need it
now, and they are different things.*

**The other two sub-tasks are deliberately absent**, and a test asserts the WRONG answer so that the
day they land, it fails and somebody comes and reads this.

---

## 2b.1 — THE STATION TAKES A CONTEXT, AND STILL HOLDS NOTHING

> *«The station is pure — context is an ARGUMENT, never state.»* (req 7)

`Compiler.compile(skeleton, context=NO_CONTEXT)`. The context carries what the caller knows and the
sentence does not: the speech act's **speaker** and **addressee**, and — declared but unused —
`recent`, the zips that anaphora and ellipsis will resolve against.

**THE AXIS HAD ITS DATA SINCE v1 AND NO CALLER TO SUPPLY THE OTHER END.** `i` and `me` carry
`person: 1` in their closed-class rows; `you` carries `person: 2`. Nothing read them, because there
was nowhere for «who is speaking» to enter. Now there is:

    compile(«I sleep»)                              agent = OPEN        — unchanged
    compile(«I sleep», Context(speaker="me.n"))     agent = me.n

**WITHOUT A CONTEXT NOTHING CHANGES**, and that is what makes this additive: every existing
measurement — ratchet 24/25, frontier 11/19, both gates — is untouched.

**THIRD PERSON IS NOT HERE AND IT IS NOT AN OVERSIGHT.** «He» and «they» are ANAPHORA: they point at
something earlier in the discourse, not at a participant in the speech act. `Context.for_person`
answers for 1 and 2 and returns None for everything else, so the day `recent` is read, third person
has somewhere to go that is not the speaker.

**THE STATION NEVER INVENTS AN IDENTIFIER.** The drill hand-compiles «I» as `me.n`; the blueprint
says the self-model is carried by named individuals with uids (E3b). Both are legal, and the station
chooses neither — it copies what it was handed into the box, and puts `Open()` there when it was
handed nothing. *That is what keeps this from pre-empting E3b.*

## 2b.2 — A QUOTE ARRIVES AS A SECOND SENTENCE, AND THE SECOND WAS BEING DROPPED

Measured: stanza splits «John said to Marie " You are a clever girl "» into **two skeletons**.
`Compiler.compile` takes one. So the second half was not merely unrotated — **it was not compiled at
all**, and the drill gate had been reporting exactly that from the other side: *«5 were split by
stanza and only the first half was read»*.

`compile_utterance(compiler, skeletons, context)` compiles each and merges them into ONE zip.

**THE FIRST SENTENCE KEEPS ITS NAMES.** A single-sentence utterance is identical to what
`Compiler.compile` produces alone, which is why nothing had to be re-measured. Later sentences are
prefixed `s1.`, `s2.` — **and every reference moves with them**, which is the part that could have
gone quietly wrong: row names and variable names are two namespaces, and a second sentence's `x0`
binding the first sentence's variable would be a zip that is well-formed and means something nobody
said.

    s1.q0  binds s1.x0, scopes s1.j0
    s1.r0  complement = Var(s1.x0) · patient = …
    s1.j0  AND (s1.m0, s1.r0)

A name that is not one of that zip's own is left alone, so `cat.n` is never mangled — the rename
checks each string against the zip's own row and variable names rather than prefixing whatever it
finds.

**THE SENTENCES ARE NOT RELATED TO ONE ANOTHER, AND THAT IS THE HONEST STATE.** «John said to Marie
"…"» needs the quote to become the CONTENT of the saying, and that is 2b.3 — the Captain's format
ruling on where an addressee lives. What 2b.2 bought is that **the information is now in the zip**:

    r0     say.v    agent = john.n, recipient = marie.n
    s1.r0  (copular) patient = «the outer addressee», complement = Var(s1.x0)
    s1.m0  (copular) patient = Var(s1.x0), complement = clever.a

The saying row carries `recipient = marie.n`. **The rotation now has something to read.**

## THE TEST THAT ASSERTS THE WRONG ANSWER

`test_THE_ROTATION_IS_NOT_BUILT_AND_THIS_TEST_SAYS_SO` checks that `you` inside the quote resolves to
the OUTER addressee — which is wrong, and is req 20's whole point. It is asserted deliberately:

> *The day this test fails, the rotation works — and whoever made it fail should come here, read
> `202609161349_the-person-axis.md`, and delete it.*

*A gap that no test mentions is a gap that gets closed by accident and nobody notices the note it
should have been read against.*

## AND THE FRAME REFUSED SOMETHING, AGAIN

`compile_utterance([])` first returned `Zip(rows=[])`, and the schema refused it: **a zip requires at
least one row.** That is right — a zip is a claim about something, and «nothing» is not something. So
an empty utterance produces the shape the compiler already produces for a skeleton with no root: one
empty content row, saying «I received this and made nothing of it». **One convention for one state**,
rather than a second one invented at the edge.

*Third time this week the frozen schema has caught a design error in the compiler: the quantifier's
restriction at the compile core, two rows named `m0` at the drill gate, and this.*

## WHAT 2b STILL OWES

    2b.3  ⚑ THE CAPTAIN'S RULING — where does the ADDRESSEE live? `Pov` holds holder · verb ·
          strength and has no fourth field, and tkzip is FROZEN at v2 (req 73), so either it gains
          one by migration under his hand, or the resolver reads the `recipient` box of a `say` row
          and learns that saying-verbs are special.
    2b.4  the rotation itself — small once 2b.3 is ruled — plus cases in BOTH gates, including UD's
          own direct-quote examples, which this QM passed over when transcribing `ccomp`.
