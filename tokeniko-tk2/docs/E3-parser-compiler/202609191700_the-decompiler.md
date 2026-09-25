# parser/compiler — THE DECOMPILER, AND THE TEST THAT CAME WITH ITS NAME, 2026-09-19 17:00

*Roadmap: `E3.3`*

*E3 task 3. The Captain renamed it before a line was written — «I would call it DECOMPILER, mimicking
the compiler/decompiler of computer languages» — and the name settled the acceptance test, the output
contract and one standing confusion in the same sentence.*

**The round trip: 46 of 87 → 79 of 82 read back as the same thought. The failures went 32 → 3.**

---

## THE NAME WAS THE DESIGN

The blueprint called the output a «scaffold», in req 9 and in three other chapters. The word was
wrong twice over: it named the *output* rather than the *operation*, and tk1 already uses
`TKScaffoldDoc` for curated VOICE TEMPLATES — an unrelated thing wearing the same word, which the
third standing law exists to prevent. Renamed in the live documents; the dated notes keep what they
said, because a record that is edited is not a record.

What the analogy brought with it:

- **the acceptance test.** Decompiled source is never the original source; it is *a* source that
  compiles to the same object. So the question is never «does this read like the sentence we started
  from» but **does it compile back to the zip we started from** — `tools/roundtrip.py`, scored by
  the drill gate's own comparator so that the instrument judging the compiler judges the decompiler
  too, and a defect cannot hide in the seam between two graders.
- **the contract.** It is faithful to the ZIP, not to the sentence. Where the parse normalised, the
  decompilation shows what the zip holds, and that gap IS the misparse signal req 3 asks the brain to
  speak back.
- **the bar for the prose.** With rag off, this text is what ships (rag req 5), and rag-out only
  POLISHES it (senses req 4) — which is exactly what stops an LLM inventing content: it is handed a
  sentence that already says what the zip says and nothing more.

## THE SPINE — SYMMETRY, SO THE FRAME/KNOWLEDGE LINE IS DRAWN ONCE

    word order · punctuation · clause structure · orthography   FRAME, as decoding is frame
    WHICH WORD carries a meaning                                 KNOWLEDGE — the rows, read backwards

The module holds no vocabulary. A marker comes from `Box.marker`, which records the preposition
actually used (req 65); every other word is looked up in `language_closed_classes` BY MEANING.

## WHAT THE FIRST SLICE MEASURED, AND THE TWO WALLS IT HIT

    46 same thought · 32 CHANGED · 9 refused

**Wall 1 — a lemma verb is an IMPERATIVE.** «A calculator never thinks» decompiled to «Think.», which
the station reads as a command, correctly, by its own `Mood=Imp` rule. **26 of the 32 failures were
that one artefact.** Inflection is not decoration: it carries mood and voice.

**Wall 2 — the inverse map is not a function.** 385 rows carry 81 distinct meanings and **47 of those
are many-formed**: thirty-two prepositions mean `location`, eighteen subordinators mean an asserted
`imply`, three forms mean sentential negation. Nothing in the rows says which one to SPEAK.

*And the decompiler refused rather than choosing — including refusing whole clauses. A negation it
cannot say would make the sentence claim the opposite of the zip, so the clause is not said at all:
half-said is legal, wrongly-said is the sin (req 8), in this direction as in the other.*

## THE TWO RULINGS, AND ONE OF THEM REVERSED ON EVIDENCE

**The preferred form** (`db/0021`, closed classes v11). A `spoken` flag, one row per meaning, ten
meanings today. The choices are curation and are listed in the migration so they can be argued with:
`not` over «n't» and «no» · `every` (it takes a singular noun, which is what is rendered) · `some` ·
`no` · `and` (the others all add something) · `because` and `if` — `db/0010`'s and `db/0016`'s own
examples — and `when`, which speaks the abstention rather than inventing a stronger word.

**The inflection library — admitted, then withdrawn on a measurement.** The Captain ruled «yes to the
library». Then `lemminflect` turned out to execute a spaCy hook on import, so importing it loads
**spacy and torch** — and those are deliberately NOT on the closed dependency list, because the
provider lives behind the skeleton adapter. The mouth would have loaded torch to say a sentence.

So it was measured instead. Over **all 20,364 verb lemmas WordNet holds**, a plain spelling rule
(`-ies` after consonant-plus-y, `-es` after a sibilant, `-s` otherwise) is right for every one but
43 — and **22 of those 43 are defects in the instrument**, not facts about English:

    ghostwrite -> «ghost-writes»    a hyphen           overshoot -> «over shoots»   a SPACE
    jell       -> «gels»            another word       okay      -> «o.k.'s»        punctuation
    torpedo    -> «torpedo»         no inflection at all, and plainly wrong

**Curated to 21 rows** (`db/0022`): two true irregulars (`be`, `have`), the fourteen `-o` verbs that
take `-es` where the majority take `-s`, three consonant-doublings, and `stomach`, whose *ch* is a
/k/. *The library does not ship. It was used the way WordNet is used to build the base — offline, as
an instrument — and its errors were caught by curation, which is what curation is for.* The closed
dependency list did not grow.

## AFTER BOTH: 79 OF 82, AND THREE LEFT

    aw-19   «I ate with Anna» -> comitative vs instrument     the named-individual hole, E3b
    aw-6    a purpose clause becomes two sentences            the joins, slice 3c
    dir-3   «as far as the bridge»                            A COMPILE DEFECT, FOUND HERE

**`dir-3` is the round trip earning its keep on day one.** «I walked as far as the bridge» compiles
with the bridge DROPPED ENTIRELY — a silent omission the drill gate could only ever see as a missing
role. Decompiled and read again, the same phrase lands in `measure`, which CONFLICTS with the drill's
`destination` and so becomes visible. `db/0015` already ruled that a marked phrase with an endpoint
is a destination, so «as far as» is a curation row; it is named here and not fixed here.

**Also named, not fixed**: `me.n` renders as «me» in subject position — «Me eats with Anna» — because
the person axis has not been read backwards yet. It round-trips correctly, which is why it is a wart
and not a defect, and it is the question the pronoun slice opens.

## WHAT THE SLICE DOES NOT DO

The prefix (attitudes, modality, negation rows, domains), the quantifiers and their variables, the
joins, and the questions. Each is recorded in `unsaid` on every zip that needs it — 60 variables, 41
joins, 10 attitudes, 7 open heads — so the round trip's number never flatters itself about how much
of the format the sentence actually reached.
