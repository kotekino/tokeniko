# parser/compiler — A CONTENT WORD IS NOT A FUNCTION WORD SPELLED THE SAME, 2026-09-22

*Opened as «the subject vanishes from a universal with a predicate nominal». It had nothing to do
with universals, or with predicate nominals.*

    « Every human being is an animal. »  ->  « An animal is. »

The zip held **one row with one box** — `{complement: animal.n}`. No binder, no subject. The
decompiler was saying exactly what it was given; the subject had been destroyed before it arrived.

## THE PARSES ARE IDENTICAL AND THE COMPILES ARE NOT

    Every human being is an animal.      All human beings are animals.
      Every  DET   det   -> being          All   DET   det   -> beings
      human  ADJ   amod  -> being          human ADJ   amod  -> beings
      being  NOUN  nsubj -> animal         beings NOUN nsubj -> animals

Same relations, same shape. The plural compiles correctly. The singular loses the subject and puts
`human` in `unplaced`. **The difference is not grammatical — it is that «being» is spelled like a
word in the closed-class table**, the participle of the copula, and the matcher took it.

## THE MECHANISM IS AN EARLY RETURN

```python
rows = self._by_form.get(form.lower())
if len(rows) == 1:
    return rows[0]          # no POS, no dependency, no narrowing
```

**221 of the 331 distinct forms have exactly one row**, and for every one of them the match was made
on the spelling alone. At least seventeen are ordinary English words:

    back · bar · being · can · dare · like · may · might · must
    need · one · ought · past · round · save · used · will

    « The back of the house is green. »    house  UNPLACED
    « I need a can of soup. »              soup   UNPLACED
    « The will of the people is clear. »   people UNPLACED

Three more sentences silently losing a noun, found by following one sentence that looked like a
quantifier bug.

## THE RULE: THIS TABLE HOLDS NO CONTENT WORDS

`UD_POS_TO_WORD_CLASS` maps UD's function-word tags to ours — `ADP` · `AUX` · `CCONJ` · `DET` ·
`PART` · `PRON` · `SCONJ` · `ADV`. It has **no entry for `NOUN`, `PROPN` or `ADJ`, and that absence
is evidence**: the table holds pronouns, determiners, adpositions, conjunctions, auxiliaries,
modals, particles, clitics and adverbs, and not one noun, adjective or proper noun. So a token UD
tags as one of those is not in this table at all, whatever it is spelled like.

## AND WHY `VERB` IS NOT ON THE LIST — A TEST SAID SO, AND IT WAS RIGHT

The first cut refused all four open classes and broke
`test_a_filter_that_would_empty_the_set_is_NOT_applied`, which pins
`select("through", "VERB", "root")` returning the preposition. **That test is correct and the
distinction it protects is whether the TAG IS CREDIBLE:**

- English HAS a noun «being», so UD tagging it `NOUN` is right and the closed-class row is the
  wrong reading.
- English has NO verb «through», so UD tagging it `VERB` is a parse error, and deleting the
  preposition over it would lose a form the station can see perfectly well.

That is exactly the disagreement `select`'s own docstring forgives — *«UD and this table were built
by different people for different purposes»* — and it is the reason the refusal names three classes
rather than every open class UD has. `ADV` and `INTJ` are excluded for the same reason from the
other direction: the table genuinely holds adverbs, and «no» answering a question as an `INTJ` is a
label disagreement, not a different word.

    drill gate   66 agreed · 4 DISAGREED · 17     unmoved
    fixpoint     69 of 87                          unmoved
    read whole   72 -> 73, FIXED 60 -> 61
    gate         spine 7 · station + evidence 407

**The instruments barely moved and that is the point.** The corpus has one sentence with this
shape; the defect was in a matcher every sentence goes through, and it was found by chasing a
symptom nobody would have attributed to it.
