# parser/compiler — THE THIRTEEN AMBIGUOUS MARKERS, 2026-09-16 09:29

*The last big piece of the 37 → 18 mapping, and the instrument turned out not to be the one
`db/0008` predicted. **`db/0008` said geometry. It was benched and it lost.** What settles «at noon»
against «at the door» is a fact the resource STATES — WordNet's own supersense — and the cosine
could not have answered it, for a reason the dictionary chapter ruled a month ago.*

**19 of 25 UD cases answered, 0 wrong** (from 16). **22 of 25 compile whole, mean 98.4%** (from 21
and 96.8%).

---

## THE QUESTION, STATED SO THE ANSWER IS FORCED

«I swam IN the pool» is a LOCATION. «I left IN May» is a TIME. «It was written IN ink» is an
INSTRUMENT. Same marker, same dependency — `case` on an `obl` — and the only difference in the whole
sentence is **what kind of thing the nominal is.**

That is a question about the TAXONOMY. And the dictionary chapter has a standing ruling about
taxonomy, made on 2026-08-19 and never disturbed:

> *«dictionary cosine is co-occurrence, not hypernymy; true cross-abstraction edges read FAR;
> disambiguate taxonomy with the is_a GRAPH, not geometry.»*

**«Is a pool a place?» is a hypernymy question**, and the geometry is structurally the wrong
instrument for it. That argument was available before any measurement — but `db/0008` had predicted
geometry in writing, so it was benched rather than dismissed.

## THE BENCH, AND WHAT IT SAID

52 cases, each a marker with its nominal, its head verb and its gold role
(`tests/fixtures/markers.py`, `tools/marker_bench.py`). **Three buckets, never averaged:**

| selector | independent | the curation's own | named individuals |
|---|---|---|---|
| take the first candidate | 7 ok · 4 wrong | 10 ok · 20 wrong | 7 ok · 4 wrong |
| **nearest-anchor geometry** | 6 ok · 3 wrong | 14 ok · 2 wrong · **14 mute** | 4 ok · 0 wrong · 7 mute |
| **the supersense** | **11 ok · 0 wrong** | **29 ok · 1 wrong** | 9 ok · 2 wrong |

**The `independent` bucket is the only one a claim may rest on** — E2's hand-compiled drill and the
UD gate's own examples, written by people who had never heard of a selector. `the curation's own` is
`db/0008`'s worked examples: a selector that reproduces them has agreed with the curation and
discovered nothing, and is here only because one that could NOT hold them would be refuted.

**THE GEOMETRY IS MUTE ON NEARLY HALF.** Most everyday nouns are not among the base's 4,555
dimensions — `pool`, `park`, `friend`, `dog`, `table`, `knife`, `door` are all absent, because the
base is the abstract core. The sense projection that reaches them then shares no column with any
role anchor, and `nearest_anchor_of_vector` correctly refuses rather than `argmax`ing over zeros.
Where it does speak it is no better than a coin toss on this question.

**AND PUTTING IT BEHIND THE SUPERSENSE MADE THINGS WORSE**, which is the sharpest result here: as a
fallback it scored 9 on the independent bucket against the supersense's 11, because it kept
overriding a DEFAULT that was right. «I build my contraption with my hammer» became comitative;
«I swam in the pool» became an instrument. A fallback that fires where the leading rule is already
correct is not a fallback, it is noise with an opinion.

## WHAT THE ANSWER IS: THE RESOURCE'S OWN SUPERSENSE

WordNet files every synset in a *lexicographer file* whose name is a broad semantic class —
**26 for nouns, 15 for verbs**, published and closed:

    noun.time  noun.person  noun.location  noun.artifact  noun.substance  noun.cognition  …
    verb.motion  verb.communication  verb.possession  verb.contact  …

**That is the UD gate's own argument arriving a second time.** Both ends of the mapping are finite —
41 supersenses in, 18 roles out — so the table from one to the other can be **complete** rather than
merely large. It is the property that made UD the station's gate, and it is why this is a table and
not a heuristic.

    at    noun.time -> time                                    else location
    in    noun.time -> time · noun.substance -> instrument     else location
    on    noun.time -> time · noun.cognition -> topic          else location
    by    noun.time -> time · noun.person -> agent · noun.object -> path   else instrument
    to    noun.person -> recipient · verb.motion -> destination · verb.communication -> recipient
    with  noun.person -> comitative                            else instrument
    for   noun.time -> duration · noun.person -> beneficiary · noun.location -> destination
    over  noun.time -> duration · verb.motion -> path          else location
    of    head is a VERB -> source · head is a NOUN -> the possessor FIELD   else complement

**`of` NEEDS NO DICTIONARY AT ALL**, and finding that out was worth the detour. «made OF titanium»
hangs off a verb and is the material; «the office OF the Chair» hangs off a noun and is the
possessor — which req 26 keeps INSIDE the record as a field and not as a box of the clause. UD
already says which, so a supersense here would be a lookup bought for nothing. *The gate caught
this: the first rule set produced `complement` for the Chair's office and the gate went WRONG for
the first time since it opened.*

**AND THE VERB'S SUPERSENSE IS THE CASE `db/0008` NAMED.** «give-like → recipient, go-like →
destination» was its own words, and `verb.motion` against `verb.communication` is exactly that
distinction, published. The prediction about WHICH evidence was right; only the instrument was
wrong.

## A DEFAULT IS AN ANSWER, AND IT IS COUNTED

The compile core abstained on these markers, on this reading of req 8:

> *«Picking the first candidate would be exactly the silently-complete nearest fit the requirement
> forbids.»*

**The operative word was SILENTLY.** A default that the zip's bookkeeping records as a default is
not silent — and unlike `roles[0]` it is now measured. So the marker fills its box, `Compiled`
gained a `defaulted` list beside `abstained`, and req 4's confidence scalar is entitled to the
difference between «a person, therefore a recipient» and «nothing chose, so location».

*The alternative was to keep abstaining on «in the pool», which loses a location any reader would
call obvious, in a sentence otherwise understood completely.*

## THE PRIMARY SENSE, AND WHY THAT IS NOT A PREFERENCE HERE

`db/0006` ruled that a dimension IS its primary sense. The same rule holds here and the reason is
sharper: reading every sense and taking the strongest was tried FIRST, and it is garbage.

    pool  -> TIME        (pool.n.08)
    table -> TIME        (table.n.05)
    dog   -> INSTRUMENT  (dog.n.07)

A word's eighth reading is a different word for every practical purpose, and a max over senses is a
machine for finding it.

## THREE ERRORS SURVIVE, AND TWO OF THEM ARE THE SAME PARKED HOLE

**«at speed» reads TIME.** WordNet files `speed.n.01` under `noun.time` — a distance per unit time —
so the resource is right and the rule is coarse. Left standing rather than special-cased: a rule that
named `speed` would be the hand list this table exists to end.

**«I ate with Anna» and «went with Anna» read INSTRUMENT.** WordNet holds `anna` only as an Indian
coin. **This is the named-individual hole**, which already has its answer waiting — a type-centroid
semantic vector plus a context-scoped identity — and is not something a better marker rule should
paper over. It is also why the bench scores names in their own bucket: averaging them in would hide
a known gap behind a selector's number.

*The geometry rescued both Anna cases, and that is not a reason to keep it: `anna.n.01` is a coin,
and a coin reading near `person.n` is luck rather than signal.*

## THE PROVENANCE DEBT, NAMED

`tk2/dictionary/supersense.py` reads WordNet **live**. It is therefore not covered by the base's
build fingerprint, and a station that answered differently after an nltk upgrade would leave no
record saying so. The honest home is the sense layer: `SenseVectorDoc` already stores each sense's
`synset` as provenance, and a `lexname` beside it would be sealed like everything else. **That is a
rebuild, and it is named here rather than done quietly.** The inventory is meanwhile checked against
the corpus on every run (`tests/test_dictionary_supersense.py`), so a resource that moved would fail
loudly instead of falling through to defaults.

## WHAT REMAINS

    « Last night , I swam in the pool »    86%   `Last` — an `amod`, one of the 21 unreached relations
    « he says that you like to swim »      86%   the xcomp's own verb, correctly not a row
    « if you know who did it , tell me »   88%   an embedded question

The thirteen are done. The ambiguous markers were the last piece of the mapping that needed anything
outside the tree; what is left in E3 is the other 21 UD relations, the embedded question, and then
the renderer and the confidence scalar the `defaulted` count now feeds.
