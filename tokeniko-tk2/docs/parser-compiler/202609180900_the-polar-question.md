# parser/compiler — THE POLAR QUESTION, AND WHERE A QUESTION LIVES, 2026-09-18 09:00

*E3 task 2c. «Is the cat hungry?» compiled at truth 1.0 — **a question stored as a belief**, the
worst direction a mood can fail in. Found the day before by fixing the truth slot under an attitude
(`202609170533_the-quotation-block.md`, finding 3).*

---

## THE BENCH, BEFORE ANY ANSWER

31 sentences, through stanza's dependency parser and — to be sure nothing was being missed — its
constituency parser too.

**Word order carries most of it.** In a polar question the auxiliary precedes the subject with
nothing fronted before it but material UD sets apart (`punct` `cc` `discourse` `vocative`). That
separated «Is the cat hungry?» · «Is there a cat?» · «John, are you coming?» from «Never have I seen
such a thing» · «So do I» · «Only then did I understand», and left «Had I known, …» alone because it
is an `advcl`. The constituency parser's `SQ` agreed with it on every case, and would have been a
second reader of the same sentence (req 2) for no gain.

**And word order is blind to exactly one family — the declarative question.** «The cat is hungry?»,
«You know the muffin man?». **Stanza is not wrong there**: the syntax IS declarative. English marks
that question with intonation, and writing keeps the intonation only as the `?` token — which
stanza has already isolated as `PUNCT`. UD has no interrogative feature for English verbs; nothing
is missing from the parse.

## THE RULING — THE `?` DECIDES *(the Captain)*

> *«Declarative questions: surely the question mark at the end is the safest option. If it is there,
> it IS a question out of any doubt. The same logic covers "now the cat is hungry?". "Is he tall!"
> has the exclamation mark and not the question mark: this should be enough not to mark it.»*

So word order is **not read at all**. The `?` is the whole signal, and a missing one means a
statement: a dropped `?` is untidy input, and restoring it belongs to the pre-input layer, not to a
station guessing at intonation.

## AND A QUESTION BELONGS TO A STATEMENT, NOT TO A SENTENCE *(the Captain)*

The QM had raised that a sentence can end in `?` and not ask: «I know you are tired, but is the cat
hungry?» asserts the tiredness. His answer placed it:

> *«As it is in tk1: a sentence like that is two statements. The first is a simple statement, the
> second is a question, so the property of being a question is not in the full sentence but in the
> single statement. And the same is applicable to the quotes: they should break and be different
> statements, bound through operators.»*

The station already compiles that way — a coordinate becomes a JOIN, a quote the content of an
attitude. What was missing is only **which statement the `?` belongs to**, because stanza hangs it
on the ROOT: on *know* in the sentence above, on *asked* in «I asked: "Do you know the muffin man?"».

**The rule: the `?` belongs to the last statement it closes.** Statements are the main clause, a
coordinate, and a quote. A subordinate clause is part of its statement and asks only through its
own word — `whether` (req 14), a wh-word.

| sentence | the `?` goes to | reading |
|---|---|---|
| The cat is hungry? · Now is the cat hungry? | the main | truth OPEN |
| I know you are tired, **but is the cat hungry?** | the coordinate | «tired» stays asserted |
| I asked: **"Do you know the muffin man?"** | the quote | the asking is claimed, the knowing OPEN |
| **Will you stay** if it rains? | the main — not «if it rains» | truth OPEN |
| Do you know who did it? | the main | truth OPEN; `who` opens its own slot |
| Where is the cat? · I asked Anna "Where do you live?" | already asks | the box opens; truth untouched |
| Is he tall! · Never have I seen such a thing. | — | statements |
| The cat is hungry, **isn't it?** | the tag | the claim asserted, the tag asks |

**The tag question was on the QM's parked list and this rule resolved it**: a tag question is
exactly a claim followed by a request to confirm it.

## FRAME — AND WHERE THE LINE FALLS

The `?` is one token read by its spelling, so the frame-or-knowledge rule was put to him. His answer
drew the line for the whole station (now in the root `CLAUDE.md`):

> *«tokeniko starts being a mind AFTER the parsing. An input string before being parsed is
> gibberish, so the knowledge concept isn't even applicable.»*

**Decoding is frame** — the string into a tree, and the tree's shape: relations, order, punctuation.
**What is checked against the decoded is knowledge** — the dictionary, the closed classes, the
marker rules, the adverb table. So `db/0008`–`0015` stand, and the `?` is frame.

---

## BUILT, AND WHAT IT FOUND

`_statements` finds each statement; `_question` gives each `?` to the last statement it closes and
opens that statement's **claim, wherever it sits**: its row's truth, or the IMPLY in «Will you stay if
it rains?» (neither half was claimed, the join was), or the OR in «Is the cat hungry or tired?». A
claimed join binding the asking statement to another opens too — «A, but B?» does not claim A-and-B.
Only what was CLAIMED opens. 22 bench sentences read as intended; 7 tests.

**THE DRILL GATE'S THIRD BLINDNESS.** It compared roles and never truth, so it saw neither the bug nor
the fix. It now compares the truth slot's **state** — a value · OPEN · unstated — never the value,
because the drill writes negation as `truth=0.0` and a forecast as a confidence where the station
does otherwise, and neither is a disagreement about whether anything was asked. Run against the OLD
station it flags `t-mo-1` «Do you exist?»; against the new one, not.

**AND IT FOUND THE IMPERATIVE AT ONCE** — `aw-21`, «Close the door!», stated where the drill leaves it
unstated under a want (tkzip req 48). **E3 task 2d.** Stanza carries it as `Mood=Imp` — in a quote,
under a conditional, coordinated, negated — so this one is structural from the start.

**TWO CURATION DEFECTS, FOUND ON THE BENCH AND NOT FIXED HERE:**

    «I wonder whether the cat is hungry»   whether/mark → a JOIN (imply, asserts neither)
    «The cat is hungry or tired»           or/cc → asserts BOTH — two claims

`whether` was req 14's subordinate polar, and the plan's statement of 2c took it as working. It
never fired: the row read in `mark` position is the join. `if` has the same double life, and the
tree separates the two readings (`ccomp` asks, `advcl` supposes).

    drill gate       50 agreed · 12 DISAGREED   before
                     49 agreed · 13 DISAGREED   after — the one new entry is aw-21, a real defect
                                                 the gate could not see until it compared truth

## `WHETHER` AND `IF` — FIXED THE SAME DAY *(the Captain: «whether/if first, then 2d»)*

Split along the frame line he drew that morning. **What a word can do is knowledge**: `whether` held
an asking row and a supposing row, `if` only the supposing one, and `db/0016` gives `if` the asking
reading — English uses the two interchangeably there («I don't know if he's coming»). **Which one a
sentence uses is the tree's shape, so frame**: a `mark` on a complement (`ccomp`, `csubj`) asks, on
an `advcl` supposes. An asking clause then relates to its matrix as the complementizer `that` does —
an attitude: the wondering claimed, the content OPEN.

    «I wonder whether the cat is hungry»    POV(wonder) · wondering claimed · hunger OPEN
    «I asked if the cat is hungry»           POV(ask)    · asking claimed    · hunger OPEN
    «Whether he comes is unclear»            the `csubj` asks
    «If it rains, I stay home»               IMPLY — unchanged
    «Whether it rains or not, I go»          IMPLY — unchanged (the concessive; not reworked here)

**And the test suite had been pinning the gap.** Two utterance tests asserted truth 1.0 on «I asked:
"Do you know the muffin man?"» — one with a message saying it *should* read OPEN and naming the
missing polar question as the reason. Both now assert OPEN, one of them across the sentence boundary
stanza draws at the quote.

## AND THE IMPERATIVE — TASK 2d, THE SAME AFTERNOON

The widened gate's first catch. **Stanza states the mood**: `Mood=Imp` on the verb or its copula or
auxiliary — the one place in this whole note where UD English does carry a mood. The station builds
the drill's shape (`aw-21`): POV(speaker · want) over an UNSTATED row, and the understood subject —
the addressee — in the box a subject would have taken.

    «Close the door!»                       want(me) · close.v, agent you — AGREES with aw-21
    «Be quiet!»                             the addressee is the copular PATIENT
    «He said to Marie: "Close the door!"»   HIS want; Marie closes it
    «Go and see»                            two wants, and the AND between them claims nothing
    «You close the door!»                   `Mood=Ind` — English leaves it ambiguous; a claim

**It found a rotation defect on the way.** A quoted holder the station cannot name — «He said "I am
late"», where `he` is anaphora — fell back to the OUTER speaker, so the narrator was late. Inside a
quotation «I» is never the narrator unless the narrator is the one quoted; an unknown holder is now
OPEN.

**Asked, not decided:** the drill's `strength = 0.9` for a bare imperative (the tree states no
number), and «Suppose the cat is hungry» (`aw-20`), which E2 collapses into the speaker's own
supposition while the station reads it compositionally as a want. Which imperatives collapse is
per-verb, so it is knowledge — the attitude-verb question req 55 already holds.

    drill gate       50 agreed · 12 DISAGREED   roles 102 of 128   (aw-21 agrees)
