# parser/compiler — THE CHECK AND THE LOOKUP MUST ASK THE SAME QUESTION, 2026-09-21

*E3 task 3, resumed. One defect, measured, root-caused and fixed — and the wrong attribution I
carried into it corrected first, because that mattered more than the fix.*

**The fixpoint's 65 → 60 was `db/0028`, written by me eighteen minutes before the run that showed
it.** I had recorded it as having «appeared when the officer's `compile.py` met my `decompile.py`».
That reading was wrong. Measured against today's code with `db/0028` set aside, the officer's work
costs nothing and **gains two** — `aw-13` and `aw-14` moved into FIXED.

| table | code | FIXED of 87 |
|---|---|---|
| v13 | before the officer landed (16:14) | 65 |
| v13 | today's — officer's `compile.py` · schema v6 · my `decompile.py` | **65** |
| v14 | today's | **60** |

---

## THE DEFECT: FIVE FLAGS LANDED ON THREE OCCUPIED SLOTS

`Decompiler._voices()` builds MEANING → *the one form curation says speaks it*, keyed on
`(role, compiled)`. And `no` and `nobody` have **identical** `compiled`:

    no       quantificational   {'kind': 'quantifier', 'quantity': 'negative'}   word_class: determiner
    nobody   quantificational   {'kind': 'quantifier', 'quantity': 'negative'}   word_class: pronoun

So the fused forms `db/0028` flagged overwrote the determiners already in those slots, last row
wins, in a dict, without a word:

    universal     ['every', 'everyone']                          ->  said 'everyone'
    existential   ['some', 'someone', 'something', 'somewhere']  ->  said 'somewhere'
    negative      ['no', 'nobody']                               ->  said 'nobody'

Five sentences, all the same wound, and they read like it:

    « There are no cats. »                     ->  « There is nobody cat. »
    « I work every day. »                      ->  « I work everyone day. »
    « not every cloud produces rain »          ->  « not everyone cloud produces rain »
    « Every teacher gave some student a book » ->  « Everyone teacher gave somewhere student a book »
    « Some software is mind… »                 ->  « Somewhere software is mind… »

## WHY THE MIGRATION'S OWN CHECK WAVED IT THROUGH

`db/0028` carried a one-voice check — *no two flagged rows may claim the same meaning* — and the
first version of it **widened `_meaning()` to include `features.sort`**, on the correct reasoning
that a quantifier's meaning is its quantity *and* the sort it ranges over. It then left
`Decompiler._voices()` keyed on `(role, compiled)`.

**So `no` and `nobody` were two meanings to the check and one slot to the index.** I changed the
check and not the lookup, and a check that keys on something the lookup does not is not checking
the lookup — it is describing a table that does not exist.

**And the arithmetic was the tell, sitting in plain sight and read by nobody**: seventeen rows
carried the flag and the index held **twelve** keys, before the migration and after. Five flags
were absorbed in silence and the count never moved.

## THE FIX IS THAT THEY ARE NOT THE SAME KIND OF WORD

The lean I first drew was a choice between teaching the index to tolerate two words in one slot and
giving the fused forms a role of their own. **That framing was wrong and the Captain's ruling — «go
with B» — is the half that fixes the live defect; the other half was needed too**, because inside
the new role `someone` · `something` · `somewhere` still share a `compiled`. Both landed:

1. **`role: fused_quantifier`** for every quantificational row whose `word_class` is not
   `determiner` — 26 rows. `no` takes a noun; `nobody` IS one; that is a difference of JOB and
   `role` is the column for the job. **The table always knew** — `word_class` has said `determiner`
   against `pronoun` since `db/0008` — and only `role` failed to say so. The split is exact and the
   table drew it: all 25 rows carrying a `sort` are pronouns or adverbs, every determiner is
   sortless, and the one sortless pronoun (`none`, «none of the cats») is fused too, which is why
   the criterion is the word class and not the sort.
2. **`_key()` gained the sort**, so the index and `db/0028`'s `_meaning()` now key on the same
   three things, and each of the two places names the other in its docstring. A lookup that wants a
   plain quantifier passes no sort and **cannot reach a fused form**.

*`compiled` was deliberately NOT widened to carry the sort, though it would have made the key
unique on its own: `_unknown()` already reads the sort out of `features` into the zip, and a second
home for one fact is a fact that will drift.*

**The compiler needed no change at all**, and that is the evidence that the split is the real seam:
`_bare_quantifier` routes on `compiled.kind`, which is what the word MEANS, while `role` is what
kind of word it is. One reader each, and they never wanted the same column.

`UD_DEP_TO_ROLE` gained the new role on `nsubj` · `obj` · `obl` · `advmod`, and deliberately not on
`det` / `det:predet` — a fused quantifier fills an argument slot and never marks a noun. Only
`once` has a competing row (`subordinator`), and it was surviving on the POS filter by accident;
now it survives by intent.

## THE RATCHET

`tests/test_language_decompile.py` gained the test the defect would have failed, and it is a count:

> **every form curation gave a voice can be REACHED** — `len(_spoken) == len(flagged rows)`.
> It was 12 for 17. It is 17 for 17.

A dict does not raise when two keys collide, so there is no place for an assertion inside the
module; the only honest test of a silent overwrite is the arithmetic. The same guard now also sits
in `db/0028`'s own `_check()`, so the migration cannot be re-flagged into a collision either.

Plus the behavioural pair in one test, because the defect was the PAIR and not either half:
«Every cat sleeps» and «Everyone sleeps» must both come out, from the same table.

## WHERE IT LEAVES THE NUMBERS

    fixpoint      65 of 87 — db/0028 now costs nothing, and all six fused forms render
    drill gate    65 agreed · 5 DISAGREED · 17 — unmoved, and the five are the pinned set
                  aw-15 · aw-19 · q-6 · t-dc-5 · t-ws-7

## AND THE RESIDUAL, DIAGNOSED THE SAME DAY — IT WAS THE INSTRUMENT

Two things moved in the same window that `db/0028` is innocent of, and they looked like a
compiler regression: **SILENT went 1 → 3** and **the sentences the compiler reads whole went
69 → 67**. Measured by putting the committed `compile.py` back under today's everything else, they
are **one fact and it is not a regression at all**:

    officer's compile.py   FIXED 65 · MOVED 19 · SILENT 3     read whole 55 of 67
    committed compile.py   FIXED 65 · MOVED 21 · SILENT 1     read whole 55 of 69

`aw-13` and `aw-14` went **MOVED → SILENT**. Nothing stopped being read whole; the fixpoint was
**subtracting a silent case from the read-whole population**, because the `continue` that handles
silence came before either counter. And it printed a SILENT line **only under `--all`**.

**So the worst outcome the instrument can report was also its quietest**, and a change that turned
two wrong sentences into two refusals read as *two fewer failures and a smaller denominator*. That
is how a regression looks like an improvement, and it is the second measuring instrument today that
was asking a different question from the one it answered.

Fixed: SILENT prints always, with its own `*` marker; it counts in the read-whole population; and
it makes the tool exit non-zero. **The honest denominator is 70** — it was never 69 or 67.

    65 of 87 come back identical · 19 MOVED · 3 SILENT
    of the 70 the compiler reads whole: 55 FIXED · 12 MOVED · 3 SILENT

## WHAT THIS LEAVES OPEN

**`aw-13`/`aw-14` are a DECOMPILER gap, newly exposed, and the officer's work is what exposed it.**
His half is right and the gate agrees with both cases now; the zip he produces says «all» with a
bare OPEN restriction and puts the narrowing in a row that SHARES the variable, and the decompiler
has no inverse for that — so the phrase comes out empty and the clause is refused:

    ⚑ r1: its subject is a variable whose binder cannot be said

That is exactly the Captain's framing — the compiler encodes it, the decompiler does not extract it
— and it is `_share_variable` needing its other direction. On the roadmap, not started.

*I had recorded these two as having moved into FIXED. They had left the MOVED list, which is not
the same thing, and the list they had joined was not being printed.*

---

# AND THE SAME DAY: SCHEMA v6's COMPILER HALF, AND WHAT IT UNCOVERED

*Built by the 1st Officier against a written work order; measured and reviewed by the QM.*

**`Box.number` existed and nothing filled it.** It does now, from UD's own `Number` feature, and
the case the v6 epoch note was written for round-trips at last:

    t-md-1   « Software can be minds and humans must be minds. »   MOVED -> FIXED

## A PROPER NOUN TAKES NO NUMBER, AND THAT WAS MEASURED

The officer's first cut read `Number` off `NOUN` and `PROPN` alike, and reported honestly that it
cost `q-9`. His diagnosis was exact: the same referent reaches a box by two routes — «John told ME»
and «John told MARIE» — and only the name carried a number, so the round trip could never close.

**The field's own docstring settles it**: *«the grammatical number the speaker used»*. «cats» is
plural because the speaker chose that word — a fact about the UTTERANCE. «Marie» is singular
because Marie is one person — a fact about the REFERENT. UD tags `Number=Sing` on every proper noun
by default morphology rather than on evidence, so taking it recorded something nobody said.

    NOUN + PROPN    fixpoint 65 of 87    q-9 MOVED
    NOUN only       fixpoint 66 of 87    q-9 FIXED, and nothing else moved

*«The Alps are beautiful» loses its agreement, and that is the honest place for it to sit. UD marks
that one `Plur` and it is real evidence — but recording it makes the decompiler spell the name
«alpses», because nothing in the zip says a head is a NAME. Names are E3b and E3 closes first
(`202609160959_the-name-question.md`); a referent's number arrives when the referent does.*

## THE EXISTENTIAL COPULA NEVER AGREED, AND NOTHING COULD SEE IT

«There are no cats» came back **«There is no cats»** — and once the agreement was taken from the
displaced box rather than hard-coded third-singular, **«There be no cats»**. Two defects stacked:

1. The expletive is not what the verb agrees with. English agrees the existential copula with the
   thing said to exist; `there` is only holding the subject position for it.
2. `be` was reaching the REGULAR verb path, where everything but the third singular is spoken as
   the bare lemma. That rule is true of every English verb except this one, and **an existential row
   is not flagged copular** — existential `be` is content (req 31) — so nothing routed it to the
   paradigm that has three cells. The guard now lives in `_agreeing` itself, where no caller can
   forget it.

Both were invisible until v6 let a zip carry a plural at all.

## THE INSTRUMENT IS BLIND TO BAD ENGLISH THAT ROUND-TRIPS

**Not one of these four renderings was a fixpoint failure**, because each recompiles to the zip it
came from:

    « There is no cats. »              « Every human beings are animals. »
    « The alpses are beautiful. »      « An animal is. »

That is not a bug in the fixpoint — it asks *«does the decompiler say back what the compiler wrote
down»* and the answer was yes. But it means **a green fixpoint is not a claim that the station
speaks English**, and req 9's acceptance test has to be read that way. The drill gate does not catch
them either; a human reading the output did. Worth remembering before the number is ever trusted
alone.

## WHAT IS OPEN, WITH ITS DIAGNOSIS

- **«Every human beings are animals»** — the zip is RIGHT (universal · plural) and English picks the
  determiner by the noun's number: «every cat», «all cats». `db/0021`'s one-voice-per-meaning is
  too coarse, exactly as it was for the fused quantifiers this morning — `spoken` needs the number
  the way it needed the sort. **This wants a ruling, not a patch.**
- **«Every human being is an animal» → «An animal is.»** — the subject vanishes from a universal
  with a predicate nominal. **Predates `Box.number`**; measured against the earlier `compile.py`.
- **`_share_variable`'s else branch mints a variable nothing binds** *(the officer, finding 5)* —
  for a REFERRING phrase «the cat that sleeps» the outer box becomes a `Var` and no `QuantifierRow`
  ever binds it, so the decompiler reports *«nothing in the zip binds it»*. Pre-existing, unrelated
  to number, not investigated.

---

# AND A THIRD TIME: `db/0029`, A QUANTIFIER'S VOICE DEPENDS ON ITS NOUN

*The Captain: «agree with your lean on the spoken flag, go for the migration».*

«All human beings are animals» came back **«Every human beings are animals»**. The zip was right —
universal over a plural restriction, which schema v6's compiler half had just made possible — and
`db/0021`'s flag answers *«this meaning has several forms, which do we say?»* with **one** form.
English has two, and the noun picks:

    every cat  ·  every human being        the universal over a SINGULAR noun
    all cats   ·  all human beings         the universal over a PLURAL noun

**Third time in two days that the key was coarser than the meaning** — after the described unknown
(schema v4) and the fused quantifier (`db/0028`, the same morning). Same fix: the distinguishing
thing goes into the key, on both sides.

## MEASURED, NOT ASSERTED

The standing law says a fact about a language is curation, so the witness is tk1's own stored
journeys — 547 distinct sentences of the Captain's real writing, parsed, counting the number of the
noun each determiner modifies:

    all      0 Sing   24 Plur      «all minds»
    some     9 Sing   10 Plur      «some software» · «some softwares»
    no      10 Sing    0 Plur      «no value»
    every    7 Sing    0 Plur      «every cat»
    each     0 Sing    3 Plur      «each others»      <- «each other». DISCARDED, not believed
    both     0 Sing    3 Plur      «both minds»

Three rows earn a number and the rest earn none. `some` is attested both ways, which is the evidence
that it does not distinguish; `no` is 10–0 here and «no cats» is plainly English, so the corpus
**under-witnesses** it rather than restricting it; `each`'s only three hits are a parse artefact.
**An absent `takes_number` is a meaning** — *this word does not distinguish* — and such a row
answers whichever number it is asked for.

## THE DRILL GATE EARNED ITS KEEP, AND THE FIXPOINT DID NOT SEE IT

The first cut wrote the feature into `features["number"]`, and the gate went **65·5 → 63·7** with
`aw-13` and `aw-14` newly DISAGREED — **while the fixpoint stayed flat at 66**.

`Compiler._unknown()` reads `features["number"]` as *the number of the unknown this word describes*
(schema v4, how «she» becomes an `Open` that remembers it is feminine singular). A determiner's
number is **the number of the noun it takes** — a different fact about a different word — so a bare
«all» started compiling to `Open(number='pl')`, a restriction «All that glitters is not gold» never
stated. One column, two facts, for the third time today; the column is now `takes_number` and the
ratchet asks the migration directly that no row's own `number` moved.

*`both` · `neither` · `either` keep `number: dual` from an older migration, and should: «neither of
the two» is a fact about the WORD, which is what that column has always been for.*

## AND THE DETERMINER AGREES WITH THE WORD ABOUT TO BE WRITTEN

A box with no `number` is not a third case to choose in. `_dress` spells the head singular unless
the box says `pl`, so the determiner in front of it is asked for with the same rule — otherwise a
numberless box reached the slot no measured row occupies and came back **«Each cat sleeps»**, where
`each` was the default only because nobody had measured it.

    fixpoint    66 of 87 · 18 MOVED · 3 SILENT      56 of the 70 read whole
    drill gate  65 agreed · 5 DISAGREED · 17        the same pinned five
