"""GLOSS REFERENCES — «A's definition NAMES B», mined as a STATED relation of R.

--------------------------------------------------------------------------------------------------
WHY THIS MODULE EXISTS: requirement 2 was refuted at scale, and this is the repair
--------------------------------------------------------------------------------------------------
Requirement 2 says `eat` stays near `food`, and was marked PROVEN at +0.405 on the 975-dimension
prototype. The E1 audit of 2026-09-14 measured it on the base that was actually built: **D cosine
+0.0484, D DIRECT CELL 0.0000.** Their definitions share no words at all.

D measures *«what two definitions SHARE»*. The relation between `eat` and `food` is *«eat's
definition NAMES food»* — a different question, and one D was never going to answer:

    eat.v.01     take in solid FOOD
    bed.n.01     a piece of furniture that provides a place to SLEEP
    hungry.a.01  feeling a need or desire to EAT food

**Both edges the Captain curated by hand in August are instances of that single rule**, and the
signal was already being computed — `distribution.gloss_vectors` reduces every dimension's gloss to
the words it names, and R never asked for it.

--------------------------------------------------------------------------------------------------
WHY IT BELONGS TO R AND NOT TO D
--------------------------------------------------------------------------------------------------
It is **stated** by the resource, it is **directional** (`eat` names `food`; `food` does not name
`eat`), it is accountable per cell, and its evidence is a quotable string. That is requirement 18's
contract, and requirement 20 already ruled the shape of such an edge: analytic only, cross-referenced
from either side, reciprocal at 0.60.

--------------------------------------------------------------------------------------------------
TWO RULINGS THAT CAME OUT OF THE MEASUREMENT, AND NEITHER IS A PREFERENCE
--------------------------------------------------------------------------------------------------
**1. Only an UNAMBIGUOUS reference may decide a verdict.** `lexicon_words_in` deliberately keeps no
tagger, so a gloss word names every dimension it could be: `state.v`'s gloss «express in words»
names `express.n`, `express.v`, `express.a` and `express.r`, of which one is meant. **69% of mined
references are ambiguous that way.** Harmless for D, where overlap is symmetric and the noise
averages; not harmless for a cell that DECIDES. So a reference is minted whenever it is found, and
only the unambiguous ones carry `gloss_reference` — the rest carry `gloss_reference_ambiguous`,
which the reading policy does not admit as a decider.

Measured against the alternative (splitting an ambiguous reference's weight across its readings and
fitting a floor): both score 0 wrong, the split scores one pair better, and it costs THREE fitted
numbers governing 31,086 edges on the evidence of 37 bar pairs. The Captain ruled the rule with one
number over the rule with three.

**2. Reference cells do NOT enter the relational cosine.** Measured: with them in the cosine and the
reciprocal on, `land.n~land.v`, `state.n~state.v` and `play.n~play.v` all flip to a wrong NEAR —
reciprocal references inflate POS-sibling profiles. A reference is a claim about a PAIR, not a
statement about a key's relational profile, and the measurement agrees with the reading.

--------------------------------------------------------------------------------------------------
WHAT IS DELIBERATELY NOT HERE
--------------------------------------------------------------------------------------------------
No tokeniser and no gloss reading of its own: the vectors arrive from `distribution.gloss_vectors`,
which carries requirement 21's POS-aware repair, the Captain's stop-list ruling, the name refusal and
the closed-class filter. A second reading of the same glosses would re-open every one of those
defects, quietly, and no fingerprint could say why.
"""

from collections.abc import Mapping

from tk2.dictionary import keys
from tk2.dictionary.matrix import Cell, Provenance

#: An unambiguous reference: the named word occupies exactly ONE dimension, so the claim names a
#: dimension rather than guessing among several. These are the cells allowed to decide a verdict.
GLOSS_REFERENCE = "gloss_reference"

#: The reciprocal of one, written at the lower weight — requirement 20's `entailed_by` convention,
#: so a mined reference is shaped like the curated edges it sits beside.
GLOSS_REFERENCE_RECIPROCAL = "gloss_reference_reciprocal"

#: A reference to a word that occupies SEVERAL dimensions. Recorded, never a decider: «express in
#: words» is a claim about one of `express.n/v/a/r` and the gloss does not say which.
GLOSS_REFERENCE_AMBIGUOUS = "gloss_reference_ambiguous"


#: Every relation THIS module produces. `relations.assert_coherent` refuses a weight nothing
#: produces — a good check that cannot see a miner it does not call — so the build tells it.
#:
#: A FRAME fact (which miners exist), not curation (how their cells are read). The first draft took
#: this set from the reading policy's `reference_relations`, which conflated the two: the reading
#: policy says these cells stay out of the cosine, and that is a different statement from «a
#: different miner writes them».
RELATIONS = (GLOSS_REFERENCE, GLOSS_REFERENCE_RECIPROCAL, GLOSS_REFERENCE_AMBIGUOUS)


def dimensions_by_word(dimensions) -> dict[str, list[str]]:
    """Word -> the dimensions it occupies. `land` is `land.n` and `land.v`; `food` is `food.n` only."""
    out: dict[str, list[str]] = {}
    for key in dimensions:
        out.setdefault(keys.word_of(key), []).append(key)
    return out


def reference_cells(
    gloss_vectors: Mapping[str, frozenset[str]],
    dimensions,
    weight: float,
    reciprocal_weight: float,
) -> dict[str, list[Cell]]:
    """Every «A's definition names B» in the base, as R cells, keyed by row.

    The forward cell is A -> B at `weight`; the reciprocal B -> A is written at
    `reciprocal_weight`, and it is what carries `sleep.v ~ bed.n`, where only *bed*'s gloss speaks.

    A cell is NOT written where one already exists from the WordNet walk: a mined relation is a
    stronger statement than a definitional mention, and overwriting it would lose the relation that
    made it. The caller merges, so this returns only what references add.
    """
    by_word = dimensions_by_word(dimensions)
    known = set(dimensions)
    forward: dict[tuple[str, str], tuple[str, float]] = {}

    for key, named in gloss_vectors.items():
        if key not in known:
            continue
        own = keys.word_of(key)
        for word in named:
            if word == own:
                # «land: the land on which real estate is located» states nothing about two
                # concepts, and mining it is how a POS-split base gets re-merged by a tautology.
                continue
            targets = by_word.get(word, ())
            if not targets:
                continue
            unambiguous = len(targets) == 1
            relation = GLOSS_REFERENCE if unambiguous else GLOSS_REFERENCE_AMBIGUOUS
            # AN AMBIGUOUS REFERENCE IS RECORDED, NOT DISCARDED. It cannot decide — the reading
            # policy does not admit its relation — but it is evidence, and it is precisely what the
            # curator's hand promotes: `sleep.v ~ bed.n` is a two-way ambiguity («sleep» is both
            # `sleep.n` and `sleep.v`), it is the pair the chapter singled out as the one only R
            # gets right, and it is visible here rather than absent.
            #
            # Written at its HONEST SHARE (`weight / n`) rather than at the full weight: a claim
            # spread over four readings is a quarter of a claim, and a number that said otherwise
            # would be the ambiguity hidden inside an accurate-looking cell.
            value = weight if unambiguous else weight / len(targets)
            for target in targets:
                forward[(key, target)] = (relation, float(value))

    rows: dict[str, list[Cell]] = {}
    for (row_key, column), (relation, value) in forward.items():
        rows.setdefault(row_key, []).append(
            Cell(column=column, weight=value, relation=relation,
                 via=(Provenance(relation, value),))
        )
        if relation is not GLOSS_REFERENCE:
            continue
        # The reciprocal, unless the other direction states it outright — a mutual reference is one
        # claim from both sides and must not be written twice at two weights.
        if (column, row_key) in forward:
            continue
        rows.setdefault(column, []).append(
            Cell(column=row_key, weight=float(reciprocal_weight),
                 relation=GLOSS_REFERENCE_RECIPROCAL,
                 via=(Provenance(GLOSS_REFERENCE_RECIPROCAL, float(reciprocal_weight)),))
        )
    return rows


def merged_into(matrix, additions: Mapping[str, list[Cell]]):
    """R with the reference cells added — and a MINED RELATION ALWAYS WINS.

    A WordNet edge is a stronger statement than a definitional mention: `eat entails swallow` says
    what eating IS, «take in solid food» says what the dictionary happened to write. Where both
    speak about a pair, the relation stands and the reference is dropped rather than layered — a
    cell that could not say which claim set it is a cell whose provenance lies.

    Returns a new `Matrix`; nothing here mutates what it was handed.
    """
    from dataclasses import replace

    rows = []
    for row in matrix.rows:
        extra = additions.get(row.key, ())
        if not extra:
            rows.append(row)
            continue
        stated = {cell.column for cell in row.cells}
        rows.append(replace(row, cells=(*row.cells,
                                        *(c for c in extra if c.column not in stated))))
    return replace(matrix, rows=tuple(rows))
