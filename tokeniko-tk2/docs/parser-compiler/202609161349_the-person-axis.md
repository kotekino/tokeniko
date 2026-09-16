# parser/compiler — THE PERSON AXIS: NO, THERE IS NO PLAN, 2026-09-16 13:49

> *«I wonder: did we take in consideration also the quotes? "John said to Marie «You are a clever
> girl»". The "you" should rotate to take for tokeniko the meaning of Marie, not himself. In tk1 I
> managed all of this: in tk2, is there a plan to do it or a note?»*
>
> *«And in general the pronouns to rotate the meaning depending on the point of view.»*
> — the Captain, 2026-09-16

**THE HONEST ANSWER IS NO.** Not a note, not a requirement, not a task. The blueprint contains
exactly one sentence on the subject, in `plan.md`'s statement of the second standing law:

> *«A pronoun is indexical (`me` means whoever is speaking), so it is resolved to an ENTITY at parse
> time and the dictionary is never asked.»*

That says WHAT to do and never says that **the context it resolves against CHANGES inside a point of
view** — which is the whole of the Captain's question. This note is written so the gap is on the
record before anything is built on top of it.

---

## WHAT tk2 HAS, AND WHY IT LOOKS LIKE MORE THAN IT IS

Three pieces exist and each one makes the hole easier to miss:

- **Requirement 7** — *«the station is pure: context is an argument, never state — anaphora,
  ellipsis, fragments resolve against caller-provided recent zips»*. It names the mechanism, and
  the three things it lists are all ANAPHORA — *which earlier thing does «it» point at*. Deixis is a
  different question: «you» points at a PARTICIPANT of the speech act, and the speech act it belongs
  to is not always the outer one.
- **`Pov(holder, verb, strength)`** — the attitude machinery, from the Captain's own first draft.
  It can already say «John / say». **It is a field on a row and nothing reads it as a scope for
  resolution.**
- **The compiler emits `Open()` for every pronoun** and the comment says «resolved to an entity from
  context before the dictionary is consulted». Correct, and it means the question has been deferred
  rather than answered — which is exactly what the plan's own line admits: *«Context-as-argument is
  untouched; nothing has needed it yet.»* **Something needs it now.**

## THE GAP HAS FOUR PARTS, AND THEY ARE NOT ONE TASK

**1 — THERE IS NO PERSON AXIS AT ALL.** tk1 had `_TALKER_ID` and `_LISTENER_ID` and a `meta` entity
that carried the stakeholder's uid across the LLC boundary; a first-person pronoun resolved to the
talker, a second-person one to the listener. **tk2 has none of it.** `compile(skeleton)` takes no
context argument, so there is nowhere for «who is speaking» to enter. Req 7 is WRITTEN and NOT BUILT.

**2 — AND THE AXIS ROTATES UNDER A POV, WHICH IS THE PART THE CAPTAIN IS ASKING ABOUT.** The rule is
not «first person = the talker». It is:

    a first-person pronoun names the HOLDER of the innermost POV it is under
    a second-person pronoun names that POV's ADDRESSEE
    with no POV, the outer speech act supplies both

    «John said to Marie: YOU are a clever girl»   ->  you = Marie
    «John thinks I am wrong»                      ->  I   = the speaker  (a THINKING POV addresses
                                                                          nobody; only `say` does)
    «John said «I am wrong»»                      ->  I   = John

**The addressee is a slot tkzip does not have.** `Pov` holds `holder`, `verb` and `strength`. «Said
TO MARIE» is a `recipient` box on the saying row, so the information is present in the zip — but
nothing connects the recipient of a `say` row to the resolution of a `you` inside it. That
connection is the ruling this note is asking for, and it is a FORMAT question as much as a station
one.

**3 — STANZA SPLITS A QUOTE INTO A SEPARATE SENTENCE, AND `compile()` TAKES ONE SKELETON.** Measured
2026-09-16:

    «John said to Marie " You are a clever girl "»
      sentence 1:  John said to Marie "        root = said
      sentence 2:  You are a clever girl "      root = girl

**The rotation information and the pronouns it governs are in different skeletons.** There is no
multi-sentence path in the station at all — `compile` is one skeleton in, one zip out — so today the
quote is not merely unrotated, it is a second unrelated utterance with nothing marking it as quoted.
*This is a structural gap and it is the cheapest of the four to close.*

**4 — NOTHING IN EITHER GATE TESTS IT.** The drill has no quoted speech: 78 hand-compiled sentences
and not one direct quotation. And the UD corpus does not either — `ccomp` was transcribed as «He
said that he knew the muffin man», which is INDIRECT speech and does not rotate. **UD's own `ccomp`
page prints the direct-quote cases** — `I asked : " Do you know the muffin man ? "` and `" Do you
know the muffin man ? " I asked .` — **and this QM passed over them when transcribing.** That is the
omission that let the hole stay invisible: a corpus that only holds the indirect form cannot report
that the direct form is unhandled.

## WHY IT IS NOT MERELY A PARSER DETAIL

**A wrong rotation is a wrong BELIEF, not a wrong parse.** «John said to Marie: you are a clever
girl» resolved with the outer listener puts *«tokeniko is a clever girl, according to John»* into a
being whose whole architecture is built so that a landed misreading is retreatable but a landed
BELIEF is his. The evaluator cannot catch it — the zip is perfectly well-formed and internally
coherent, and it is about the wrong person.

That places it with the shields (req 3) rather than with the features: `original` stays verbatim so
even this is retreatable, but nothing downstream would flag it.

**And it is the second time this week that a name turned out to be load-bearing.** «John» and
«Marie» have to become individuals before a rotation can name them — which is **E3b**, already open.
The ROTATION mechanism and the NAME mechanism are separable (a «you» can rotate to «the person
addressed» without knowing who that is), but a rotation that cannot name its target is half an
answer.

## WHAT IS OWED, IN THE ORDER THE DEPENDENCIES FALL

1. **A context argument on `compile()`** — req 7, finally built: the speech act's participants
   (speaker, addressee) and the recent zips, passed in and never held. Small, and everything else
   waits on it.
2. **Multi-sentence input**, so a quote and its frame reach the station as one utterance.
3. **THE RULING, which is the Captain's and not the QM's:** where does the addressee live? A fourth
   field on `Pov`, or read off the `recipient` box of a `say` row? The second adds nothing to the
   format and asks the resolver to know that `say`-like verbs are special; the first is a schema
   change and tkzip is FROZEN at v2, so it is a migration under his hand (req 73).
4. **The rotation itself**, which is small once 1–3 exist.
5. **Cases in BOTH gates** — UD's direct-quote examples in the corpus, and hand-compiled quotation
   in the drill. *Requirement 18 again: the two gates have never met, and this is the second hole
   that would have been visible if they had.*

**Nothing above is scheduled.** It is written here so the next session does not rediscover it, and so
the Captain can place it — E3, E3b, or a piece of its own.
