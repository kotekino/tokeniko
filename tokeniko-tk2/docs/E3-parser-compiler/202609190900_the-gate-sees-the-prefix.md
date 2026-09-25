# parser/compiler — THE GATE SEES THE PREFIX, AND CATCHES A COIN TOSS, 2026-09-19 09:00

*Roadmap: `E3.5.2.1`*

*The fourth widening of the drill gate, and the first one asked for BEFORE the thing it was to
measure was built. The Captain's ruling: «widen the gate now, then docs first». It found the defect
it was widened for, and a second one nobody was looking for — the station reading one sentence as two
different thoughts depending on the process it ran in.*

**Drill gate: 59 agreed · 3 DISAGREED → 59 agreed · 5 DISAGREED, and 89 prefix rows + 50 joins are
now inside the instrument. Content unmoved: 99/136 rows, 114/140 roles.**

---

## WHY IT WAS WIDENED BEFORE THE BUILD, AND NOT AFTER

The day's first task was the imperative's `strength` — ruled KNOWLEDGE by the Captain, so a row and a
reader. Before writing it, one check: **where would it be measured?** The answer was nowhere.
`rows_of()` filtered `kind="content"` and nothing else, so the whole PREFIX was invisible:

    every attitude's holder · verb · addressee · STRENGTH       aw-21, aw-20, q-4…q-9, t-md-4
    every negation, modality and domain row                     aw-13…aw-16, t-ws-6
    every quantifier's quantity and restriction                 the whole universal family
    every JOIN's truth slot                                     db/0017 and free choice turned on it

So `aw-21`'s POV(me · want) — built the day before, and the drill's own reason for the case — was
measured by an instrument that could not see it. The same was true of the quotation holders the
person axis exists for: yesterday's rotation defect was caught in a CONTENT row, by luck of where it
landed, not because the gate was looking at the attitude.

*Writing the number first would have shipped a value no instrument could contradict.*

## HOW A PREFIX ROW PAIRS — THE DOCTRINE, APPLIED A THIRD TIME

A prefix element scopes a row BY NAME, and the two zips name their rows independently: `aw-21`'s want
scopes `cl`, the station's scopes `r0`. So the target is resolved to something both sides can say —
a content row's signature, or, for a join, its operator over its operands' keys, recursively
(`target_keys`).

Then the gate's standing split: **pair on what the row IS, compare what it SAYS.**

    a content row   pairs on its PREDICATE     compared on its boxes
    a box           pairs on its FILLER        compared on its role
    an attitude     pairs on its VERB          compared on holder · addressee · strength
    a quantifier    pairs on its RESTRICTION   compared on its quantity
    a modality      pairs on its target        compared on ◇ / □
    a negation      pairs on its target        being there IS the agreement

**AND THE LEFTOVERS ARE READ, because absence and substitution are different facts.** A drill row
nothing paired with is MISSING — E3 unfinished, never a defect — *unless* the station has an unpaired
row of the same kind over the same target. Then it is a SUBSTITUTION, and it is a defect: the station
said something else about the same row.

**The first half was forced by a case, the second is a guard and is recorded as one.** Pairing by
document order to begin with, «Marie said "John told me 'you are late'"» reported three conflicts —
and the station had in fact got John's telling exactly right, holder and addressee and all, and
merely missed the outer saying: **a MISSING dressed as a defect.** Pairing on the verb fixed it. The
substitution rule was then added because identity pairing alone can hide the opposite error, and
**it fires nowhere in the drill today** — the case it is written for, `aw-20`, does not reach it
(below). A guard with no witness is worth keeping only when it is named as a guard.

**No magnitude is compared, ever.** `strength` is reported `stated` / `unstated`, exactly as
`truth_state` reports the truth slot. «The station says nothing about how strongly this wants» is a
defect; «the station says 0.85 where the table says 0.9» is a migration, and the gate is not the
curator.

## WHAT IT FOUND — ONE EXPECTED, ONE NOT

### 1. `aw-21` — the imperative wants at no strength *(expected, and the point)*

    attitude over close.v: strength — the station says unstated, the drill says stated

The case the widening was built for, now red, and `db/0020` is what closes it.

### 2. `t-qu-1` — THE SAME SENTENCE READ AS TWO DIFFERENT THOUGHTS *(not expected)*

«Tokeniko, the cat is dead and alive» disagreed on one run and agreed on the next, with no code
between them touching a content role. It was not the provider: stanza's parse is bit-stable over six
runs. It was **ours**.

**NLTK stores a synset's pointers in a `set`** (`Synset._pointers`, a `defaultdict(set)`), so every
`_related`-based accessor — `attributes()`, `derivationally_related_forms()`, `hypernyms()` — comes
back in the process's own string-hash order. `derived_supersense` took `[0]`. And *dead* has TWO
attribute nouns:

    animation.n.01   noun.state       -> experiencer
    animation.n.02   noun.attribute   -> patient

so «the cat is dead» compiled an experiencer under `PYTHONHASHSEED=3` and a patient under 0, 1, 2, 4
and 5. **This is also the ghost of 2026-09-18** — the ratchet test that reported a different list
once and never again, recorded honestly as non-reproducing. It has a cause and a name now.

*A mind that reads one sentence as two different thoughts is worse than a mind that reads it wrongly
twice: the second can be corrected, the first cannot even be discussed.*

**THE FIX IS AT THE RESOURCE'S END, AND IT ABSTAINS.** `derived_supersense` now reads the WHOLE
relation and answers only when it is of one mind. Sorting the set would have been the easy repair and
the wrong one: **WordNet publishes no priority among a synset's attributes**, so any order we imposed
would be our invention wearing the resource's clothes — the same error the `q-5` and lone-`iobj`
rulings refused at the provider's end. Where the resource does not say, we do not decide; the
caller's default stands and is COUNTED as a default (reqs 8, 15).

Verified across hash seeds: identical for every adjective on the bench.

### The cost, and the one row it needs

    dead     {noun.state, noun.attribute}   abstains -> default patient        agrees with the drill
    alive    {noun.state, noun.attribute}   abstains -> default patient        agrees with the drill
    happy    {noun.state, noun.feeling}     abstains -> default patient        THE DRILL SAYS EXPERIENCER

`happy` is the price, and `t-of-1` («I am happy because I am thinking…») went red for it.
**`noun.feeling` cannot enter the rule** — that was refused on 2026-09-18 with a witness, «Be
QUIET!», which WordNet relates to a feeling. So `happy` becomes a LEMMA EXCEPTION ROW, the shape
already ruled for `disagree`: where the resource is of two minds, E2's ruling settles it and the
settlement is curation. `db/0019`.

*Note what the two cases have in common and where they part: `dead` is a word WordNet cannot classify
and the Captain hand-compiled as a patient — so abstaining is right twice over. `happy` is a word
WordNet cannot classify and the ruling names explicitly («verbs of feeling and thinking»). The
instrument abstains in both; the table answers in one.*

## THE STATE OF THE RATCHET — FIVE, TWO OF THEM CLOSING TODAY

    t-ws-7   «an animal or A MIND» read as one noun phrase        provider defect, abstained
    aw-15    no DomainRow yet                                      E3 unfinished
    aw-19    «I ate with Anna» — the named-individual hole         E3b
    aw-21    the imperative's strength                             db/0020 closes it
    t-of-1   «happy» — the resource is of two minds                db/0019 closes it

## AND THE SECOND PARKED QUESTION, MEASURED RATHER THAN ASSUMED — `aw-20`

The Captain's ruling: the station does NOT collapse «Suppose the cat is hungry» into the speaker's
own supposition; which imperatives collapse is per-verb, hence knowledge, hence req 55's (req 24).
The divergence sounded like a contradiction. **What the gate actually reports is smaller and more
honest**: the station builds no attitude for «suppose» at all.

    the station   want.v over suppose.v · content suppose.v (agent: you) AND the cat's row
    the drill     suppose.v over the cat's row

Different targets, so nothing is substituted and nothing conflicts — the drill's attitude is reported
MISSING. *The collapse question cannot even be asked of the station until req 55 gives an attitude
verb its own row.* Recorded so that a later reader does not mistake a silence for agreement.

## WHAT THE PREFIX NUMBERS SAY, READ HONESTLY

    PREFIX PAIRED   23 of 89, and 51 of their slots agree     17 of the 87 sentences reach it
    JOINS PAIRED    12 of 50, on the truth slot

    MISSING, by kind    quantifier 42 · attitude 14 · negation 5 · domain 5 · modality 0

Two thirds of the prefix the Captain hand-compiled is not produced at all, and the breakdown says
where the epic's remaining weight sits: **every modality row the drill holds is produced**, while the
quantifiers are barely begun and there is no domain row anywhere. That is E3 unfinished and it is now
VISIBLE — the other half of what a widening buys. The gate could not previously say how much of the
format the station does not reach; it can now, and the figure is meant to climb.
