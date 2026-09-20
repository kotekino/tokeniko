# parser/compiler — THE STATION AGAINST ITSELF, 2026-09-20

*E3 task 3, second and third slices. The Captain's instruction is the whole of the method:*

> *«What the decompiler can't do, either is because the compiler doesn't encode the missed
> information in the zip OR the decompiler doesn't extract the information encoded in the tkzip.
> Everything that emerged should be fixed … until everything is fixed and the input sentence is
> 100% equivalent to the output one. The decompiler is another CORE feature, so it must be perfect
> from the beginning — at least it should be the reverse operation of what the compiler does.»*

**The fixpoint, which did not exist yesterday: 24 → 62 of 87 zips come back IDENTICAL** (52 of the
69 sentences the compiler reads whole). **The drill gate went 61·3 → 63·5, and the two new reds are
a gain** — see the last section but one.

---

## THE INSTRUCTION NEEDED A DIFFERENT INSTRUMENT, SO IT GOT ONE

`tools/roundtrip.py` measures the decompiler against **the drill's hand-compiled zips**, and those
hold things the station cannot yet produce. A failure there is either a decompiler gap or an E3
backlog item, and the number cannot tell you which.

**`--fixpoint` asks only the Captain's question**: sentence → zip → sentence → zip, and the two zips
must be **IDENTICAL**. Whatever the compiler failed to encode is absent from both sides and cannot
hide a decompiler defect; whatever it encoded and the decompiler drops shows up at once.

Equality, not agreement — the drill gate's comparator is generous by design, and generosity is right
when judging a parse against a hand-compiled truth and wrong when both sides come from one machine.
Three things are normalised first, each because the format says they carry no meaning:

    row names           zip-local and arbitrary (req 64) — `r0` and `s1.r0` are one row
    `and` chains        associative by MATHEMATICS (req 41), so `and(and(a,b),c)` is one thought
    `unplaced`          req 21 makes it a diagnostic, recorded and never compared

And it reports **two populations**: the 69 sentences the compiler read whole, and the rest. A
sentence with a word left unplaced cannot test the decompiler, because the zip never held it.

## THE COMPILER WAS DROPPING THREE THINGS, AND NONE OF THEM WAS A DECOMPILER GAP

| | what was happening | what it is now |
|---|---|---|
| **tense** | `Theatre` was written on **0 of 87** zips. 19 drill sentences are in the past and every one came back present — «I walked to the station» and «I walk to the station» were **the same zip** | read off UD's `Tense`, written as the theatre's time axis: **−1 before the utterance, 0 at it, +1 after**, which is the convention the drill's own forecast already used (`aw-22`) |
| **voice** | `topicality` was written by nothing. Requirement 27 — *«the renderer reads it to speak the sentence back in the voice it was heard in»* — was **dead data**, set by hand on one zip of 87 | read off `nsubj:pass`; the role that phrase filled is already recorded, because `Placements` says where every token went |
| **an unresolved pronoun** | «he» compiled to `Open()`, so **«he thinks» and «she thinks» were the same zip** — and the decompiler could only speak an OPEN box as a question | an OPEN that REMEMBERS what the sentence said about it: *third person, masculine, singular* (**schema v4**, below). The first answer was the pronoun's own key `he.n` — the drill's own spelling — and it was a stand-in, replaced the same day |

**And the third one found two defects that an abstention had been hiding.** The drill gate abstains
on an OPEN filler, so while «he» was OPEN there was nothing to compare: the moment the word was kept,
`look` → experiencer and `die` → agent both appeared. WordNet's supersense says what a verb is ABOUT
and the subject's role turns on whether the subject DOES it — *looking* and *seeing* are both
perception and only one is volitional. Volitionality is not in the resource, so both are lemma rules
(`db/0025`), on `db/0019`'s own precedent for `disagree` and `happy`.

## THE FOUR OTHER COMPILER DEFECTS THE FIXPOINT FOUND

1. **`compile_utterance` dropped the theatre and the voice on the way out.** Both are one field on
   the zip, so a merge has to choose, and it chose nothing at all.
2. **A clause that became an attitude was also left as a claim.** «He thinks a cat is in the garden»
   produced an `AttitudeRow` *and* a content row for the thinking, so the decompiler said it twice —
   «He thinks. He thinks that a cat is in the garden.» The clause now dissolves into the prefix row
   that replaced it, **unless it holds anything else** (a saying with a manner on it keeps its row)
   **or anything still names it** (nested attitudes scope the row they came from).
3. **A bare `ccomp` was read as a conjunction unless the verb was in `SAYING_VERBS`**, so «he THINKS
   a cat is in the garden» claimed the cat. `that` is optional in English and whether the speaker
   typed it cannot change what is asserted, so the rule is the RELATION's. *One fewer reader of
   `SAYING_VERBS`, which E3's frame/knowledge audit wants gone anyway.*
4. **THE ZIP WAS COMING OUT A DAG AND A SENTENCE IS A TREE.** Clauses were joined pairwise by name,
   so a clause in two joins was named by both: «I am happy because I am thinking and I love thinking»
   gave `imply(think, happy)` beside `and(think, love)` — two roots sharing a half, which the
   decompiler duly said twice. **Coordination binds tighter than subordination**, and that is what
   decides where a new join goes: a `conj` REPLACES the clause it extends wherever an earlier join
   named it; anything else attaches to the OUTERMOST join that clause already sits in.

*And a fifth, found by the passive: `Tense=Past` on a participle is the participle's own form, not
when the thing happened. «The hammer IS MADE of titanium» was being read as past, because the finite
auxiliary — which is what carries the tense — was not the word being asked.*

## WHAT THE DECOMPILER LEARNED TO EXTRACT

- **the tense and the voice**, which needed `VBD` and `VBN` (`db/0024`, below);
- **the person axis backwards** — `me.n` is «I» in subject position and «my» before a noun, and
  neither is chosen here: the key's own row carries `person: 1`, and the rows answer;
- **agreement**, including the copula's three present cells;
- **the existential** — «There is a cat», decided *before* the subject is rendered, because
  rendering the phrase and then moving it says a bound variable twice and «There are no cats» came
  back «There is the cat»;
- **the expletive** — «It rains», where the thought has no participant at all;
- **the question**, in three shapes: a subject question word does not move and nothing inverts
  («Who ate the fish?»), a non-subject one fronts and pulls the auxiliary, and an embedded question
  takes no `that` because it already opens with its own word;
- **and the passive**, which is what an OPEN agent in a plain claim means. «The hammer is made of
  titanium» does not ask who made it.

## THE TWO RULES THAT ARE NOT ABOUT TIDINESS

**A negation that cannot be delivered REFUSES THE ROW.** Three renders were claiming the opposite of
their zip: a dropped `¬□` («a calculator does not necessarily think» is an adverb the table does not
carry), a dropped `¬∀`, and — found by the round trip — a supposed half standing alone. «You learn
the thing.» was said for a row the zip only supposes, because its join had collapsed to one half.
A clause standing alone is a declarative, and a declarative asserts by being one.

**A row that claims nothing is sayable exactly when something above it says so.** The antecedent of
«if it rains, I stay home» claims nothing and the JOIN is what is asserted there (req 38).

## THE KNOWLEDGE, AND WHY EACH MIGRATION EXISTS

**`db/0023` — closed classes v12, the features a form is CHOSEN by.** `db/0021`'s `spoken` flag
answers *«this MEANING has several forms — which one do we say?»*. Three of the choices this slice
ran into are not about meaning at all: «my» or «mine» is about WHERE IT STANDS, «I» or «me» about the
SLOT, «am» or «are» about WHO THE SUBJECT IS. A flag keyed on meaning cannot separate any of them —
all seventeen possessives compile to the same three words. So the `features` column finishes the
paradigm: `use: determiner|pronoun`, the copula's cells with `are` as the **default**, `archaic` on
thou·thee·ye·thy·thine (which is why «you» had three nominative candidates), `selective` on the
interrogative `which`.

**And «although» loses its `spoken` flag.** Its meaning is `and` asserting both halves — exactly
«and»'s meaning — and both carried the flag, which v11's check allowed because it keyed on *(role,
meaning)* and those are two roles. The decompiler asks by OPERATOR and got two answers, so **the
commonest join in the corpus could not be spoken at all**. The v12 check is widened to the key the
decompiler actually uses. `can`, `must` and `will` gain the flag.

**`db/0024` — inflections v2, the tense the sentence was heard in.** 862 rows, and **two resources,
not one**: `db/0022` measured 22 of lemminflect's 43 answers to be its own defects, so every row here
is cross-checked against **WordNet's `verb.exc`**, Princeton's hand-curated irregulars, read from the
corpus this project already builds its base on. A row enters on one of four witnesses — *both* ·
*unchanging* (the instrument says the past IS the lemma and WordNet records only an `-ing` form,
which is the silence of a verb with nothing else to record) · *stress* (the answer differs from the
rule by exactly a doubled consonant, which is the one fact the rule declared out of reach) · *hand*
(the two disagreed and the QM ruled it, each listed in the migration). The bench is
`tools/inflection_bench.py` and the classification is its output, not a description of it.

*The rule grew too, and each change is measured: `-c` → `-cked` after a vowel («panic», but «sync»
takes a plain `-ed`), and `y` counts as a vowel for syllables after a consonant («cypher») and as a
CONSONANT between them, which is what splits «cray|on» and «kay|ak».*

**`db/0025` — subject roles v3**, the two verbs above.

## AND THE ONE THING THAT WAS NOT MINE TO DECIDE — RULED, AND THE RULE ABOVE IT REWRITTEN

**Three symptoms, one missing field.** `Open` carried a `prior` and nothing else, so «who» and
«what», «he» and «she», «its» and «his» compiled to one zip each. I brought it to the Captain as a
schema question under tkzip req 73's freeze, **and he rewrote the requirement instead of answering
under it:**

> *«Not sure why you talk about "frozen" schemas: we are building from scratch, nothing is running,
> no retro-compatibility problems are bothering us: there are no frozen schemas :) … When schema
> improvements are the best solution (and I may have overlooked), schema must be changed. … We are
> in a blueprint, so when you propose a solution consider that a shortcut will force us to
> reconsider the choice. **The ideal solution is always the FIRST solution.**»*

What survives of req 73 is the GATE — a change here reaches him as a DECISION rather than being
settled by whoever is editing the file. What does not survive is treating the version integer as a
cost to be routed around. *Recorded in the requirement itself, and as the memory
`no-frozen-schemas-in-a-blueprint`.*

**SCHEMA v4**: `Open` gains `sort` · `person` · `number` · `gender`, carrying exactly what the
closed-class row it matched already records — same names, same values — so the compiler copies and
the decompiler matches back. Strings and an integer rather than enums, for `BaseKey`'s reason: the
table owns the vocabulary and the schema only carries it.

**And it came out cleaner than the stand-in it replaced.** The decompiler now separates THREE kinds
of unknown with no heuristic anywhere:

    Open(sort="person")              the sentence ASKED           -> a question word
    Open(person=3, gender="f", …)    the sentence DESCRIBED it    -> «she»
    Open()                           nobody described it          -> the passive leaves it out

The rule I had written — *an agent, in a claimed clause, not under an attitude, is probably a
passive* — is deleted. The zip says which.

**The shortcut was fixed in the same direction, as he asked.** The drill held `he.n` in **thirteen
boxes** — a pronoun's dictionary key standing in for a referent, which contradicts the drill's own
doctrine that *«a pronoun that survives into a row is an unresolved reference and not a reading»*.
It was written that way because the format could not say «a male singular person nobody has
identified». Sentences and verdicts untouched; only the spelling of the unknown moved.

## THE GATE WENT 65·3 → 63·5, AND THAT IS THE HONEST NUMBER

The comparator flattened every open slot to the word «open», so **«he» compared EQUAL to «she»**,
and a box the drill described compared equal to one the station left blank. It reads the features
now; an OPEN nobody described still abstains, because «I do not know» contradicts nothing.

The two new reds are `q-6` and `t-dc-5`, and they are one thing: *the station says an unidentified
feminine singular person, the drill says `marie.n`.* **That is ANAPHORA**, req 7, never built — and
it had been invisible twice over. **The second time in one day that an abstention turned out to be
hiding a defect**, after `look` and `die`.

**Parked, and the Captain ruled the parking a DEPENDENCY rather than a deferral**: the blocker is
not the search, it is that nothing knows *Marie is feminine and John is not* — WordNet has no gender
for a name, stanza's NER says `PERSON` for both, the supersense says `noun.person` for both. That is
an attribute of a NAMED INDIVIDUAL, which is **E3b**'s whole subject, and the plan now records it
there with its three steps. *Written without it, the resolver would guess on exactly the two cases
we have, and an OPEN carrying its features is a better zip than a coin-flipped `marie.n`.*

## AND A REGRESSION THE FIXPOINT CAUGHT WITHIN THE HOUR

«It will rain tomorrow» stopped round-tripping. v4 let the decompiler ask for *the third-person
neuter singular nominative* — and **two rows answered**, `it` and `one`. Two answers is no answer,
so it said nothing. They are not the same word: `one` is the IMPERSONAL pronoun, and its person,
number and gender are the grammar it agrees by rather than what it points at. One feature on one
row (`db/0026`, `generic: true`).

## AND THE SECOND SCHEMA CHANGE OF THE DAY, RULED IN ONE LINE

I named a limitation at the end of the commit report — *the theatre is one field on the zip, so «I
went to Rome and I will go to Genoa» cannot record both tenses* — and said that under yesterday's
freeze I would have called it a limitation, but by today's rule it is a question with a first
solution. **The Captain: «let's do it right away: theatre must obviously be a field per row.»**

**SCHEMA v5.** The field had been documented as *«the CLAUSE's spacetime»* from the day it was
written, and had been sitting on the Zip the whole time. It now rides on:

    ContentRow    a predication happens in spacetime
    AttitudeRow   so does a saying — «John SAID that the sky IS green» is a past saying about a
                  present sky, and the saying's own clause dissolves into this row
    Pov           because req 45 makes it the same mechanism in a second spelling, and a field on
                  one and not the other would make the shorthand say less

and **nowhere else**. A JOIN is a logical relation between things that have a time, not a thing with
one — req 37 reads its arrow by comparing its halves'. A quantifier, a negation, a modality and a
domain have none, and a slot that can only ever be empty is a slot this schema does not add.

*The compiler computes it per clause head instead of once for the root; `compile_utterance` needs no
merge rule for it any more, because every clause of every sentence keeps its own. Every number held:
gate 63·5, fixpoint 62 of 87.*

    « I went to Rome and I will go to Genoa. »  ->  « I went to rome and I will go to genoa. »
    « John said that the sky is green. »        ->  « John said that the sky is green. »

*Also named and not fixed: a proper noun is spoken lower-case, because the zip holds `john.n` and
nothing says it is a name — **E3b** again, and E3 closes with names unresolved by design.*
