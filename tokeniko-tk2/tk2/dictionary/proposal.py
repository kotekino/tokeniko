"""THE SEED PROPOSAL — candidates measured, never typed.

«It grows generated-then-curated (propose → simulate → the Captain approves), never typed by hand
until it looks long enough» (the standing law, 2026-08-25). This module is the PROPOSE half, and it
is pure: a graph, a provider and a set of forms to exclude go in, a labelled ranking comes out.
`tools/propose_seeds.py` runs it and simulates what each cut would close to; approving is the
Captain's hand and lives in neither.

TWO SOURCES, LABELLED, because they are approved under different eyes:

  - PURPOSE — the declared families (requirement 8: in scope BY CONSTRUCTION). An argument about
    what this being must be able to think about, which no measurement can make and none can refute.
  - STRUCTURE — the definitional core, by IN-DEGREE over the whole definition digraph. An argument
    about the resource: the words WordNet writes its definitions with are the words the base cannot
    do without, because everything else is defined in terms of them.

TWO EXCLUSIONS STAND BETWEEN THE RANKING AND A SEED, and they are different in kind.

  1. THE CLOSED CLASSES, by PRINCIPLE (the second standing law: content is defined, structure is
     compiled). `in` heads the ranking with 14,408 in-edges and WordNet's `in` means *inch*; `at` is
     #19 and means the Lao kip. A function word never asks the dictionary a question, so it is not
     a candidate — not filtered late, not down-weighted, simply never in the running. The forms
     arrive as an argument (`closed_forms`) because they are ROWS (`closed_classes`), and nothing in
     this package reads a database.

  2. THE DE-INFLECTION GUARD, by CRITERION. `used`, `are`, `made`, `lacking`, `marked` and `being`
     rank in the hundreds because glosses are written in English and English inflects: a gloss
     saying «used to cut» names `use`, and the mining layer honestly records that it might also
     name the adjective `used` (requirement 21 — nothing picks a winner among a token's readings).
     The frequency is the LEMMA's, earned as grammar; the word may still be a fine dimension and it
     may not be seeded on somebody else's in-degree.

     The criterion is `inflection_of` below, and it is a criterion rather than the six-word list the
     measurement turned up, for the reason the standing law gives lists in code. It is also
     DELIBERATELY BLUNT, and the bluntness is measurable: `left` is `leave`'s participle, `number`
     is morphy's comparative of `numb`, `saw` is `see`'s past — all three are real words the guard
     removes from the RANKING. That is a cost paid in seeds only: a word the guard removes can and
     usually does still enter the base through the closure. `inflection_share` is reported beside
     each removal so the cost is visible rather than argued about — see its docstring.
"""

from collections import Counter
from dataclasses import dataclass

from tk2.dictionary import glosses
from tk2.dictionary.closure import Digraph
from tk2.dictionary.glosses import GlossProvider

#: Why a candidate is not a candidate. Recorded per row rather than filtered away, because the
#: Captain approves the ranking and a ranking that silently dropped its head would be a ranking
#: nobody can audit.
CLOSED_CLASS = "closed-class"
INFLECTION = "inflection"


@dataclass(frozen=True, slots=True)
class Candidate:
    """One word of the structural ranking, with everything the Captain needs to rule on it."""

    word: str
    #: How many of the lexicon's definitions name this word. THE ranking number.
    in_degree: int
    #: The parts of speech it would mint dimensions for — `()` when it would mint none at all.
    dimensions: tuple[str, ...]
    #: The first line of what the resource thinks it means. This is the column that exposed `in` =
    #: *inch* and `are` = a unit of area, so it is part of the proposal and not a debug print.
    gloss: str
    #: `None` when the word is a candidate; `CLOSED_CLASS` or `INFLECTION` when it is not.
    excluded: str | None = None
    #: For an inflection: the lexicon words this one is a form OF, and how much of the in-degree is
    #: shared with them (see `inflection_share`).
    inflection_of: tuple[str, ...] = ()
    inflection_share: float | None = None

    @property
    def is_candidate(self) -> bool:
        return self.excluded is None


# ------------------------------------------------------------------------------------------------
# the ranking number
# ------------------------------------------------------------------------------------------------


def in_degrees(graph: Digraph) -> Counter:
    """How many definitions name each word. Every node is present, zeros included: a word nothing
    defines is a fact about the resource, and a Counter that omits it would answer the same as one
    that never heard of the word."""
    counts = Counter({word: 0 for word in graph})
    for targets in graph.values():
        counts.update(targets)
    return counts


# ------------------------------------------------------------------------------------------------
# the de-inflection guard
# ------------------------------------------------------------------------------------------------


def inflection_of(word: str, lexicon: frozenset[str], provider: GlossProvider) -> tuple[str, ...]:
    """The lexicon words `word` is an inflected form OF — empty when it is nobody's inflection.

    Asked of the resource's morphology, one part of speech at a time, which is the same question
    `analyses_of` asks when it mines a gloss: if a token spelled like this word names some OTHER
    lexicon word, then every gloss containing this token gave that other word an in-edge too, and
    this word's in-degree is not evidence about this word.

    Note what it does NOT test: whether the word is a base form of something. `used` IS a base-form
    adjective, `being` IS a noun, `are` IS a unit of area — all three have honest dimensions and all
    three rank on grammar. Basing the guard on «is it a base form of anything» would therefore have
    caught none of the six words the measurement found.
    """
    return tuple(
        lemma
        for lemma in provider.lemmas(word)
        if lemma != word and lemma in lexicon
    )


def inflection_share(word: str, lemmas, counts: Counter) -> float | None:
    """How much of the LEMMA's in-degree this form accounts for, at most 1.0 — the number that says
    which of the two spellings is the real word.

    Every gloss whose token is `word` gives an in-edge to `word` AND to its lemma, so the lemma's
    count is always the larger. The RATIO is what separates the two cases the guard cannot:

      - `used` -> `use`: `use` is written in glosses constantly in its own right, so `used`'s share
        of it is small. Grammar riding on a word — the guard is right.
      - `number` -> `numb` (morphy reads it as the comparative): almost every in-edge `numb` has
        came from the token `number`, so the share is near 1.0. The rare word is the passenger and
        the guard has the pair backwards.

    Reported, never thresholded here. Where the line falls is a ruling, and this module measures.
    """
    if not lemmas:
        return None
    best = max(counts.get(lemma, 0) for lemma in lemmas)
    return None if best == 0 else min(1.0, counts[word] / best)


# ------------------------------------------------------------------------------------------------
# the ranking
# ------------------------------------------------------------------------------------------------


def structural_ranking(
    graph: Digraph,
    provider: GlossProvider,
    closed_forms=(),
    gloss_length: int = 90,
) -> list[Candidate]:
    """Every word in the digraph, by in-degree, each labelled with why it is or is not a candidate.

    The whole ranking is returned rather than the survivors. What was excluded and at what rank is
    the most argued-about part of a proposal — `in` at #1 is the second standing law's own example —
    and a function that returned only the clean list would be asking to be trusted.
    """
    lexicon = frozenset(graph)
    closed = frozenset(closed_forms)
    counts = in_degrees(graph)

    out: list[Candidate] = []
    for word, count in counts.most_common():
        lemmas = inflection_of(word, lexicon, provider)
        excluded = None
        if word in closed:
            excluded = CLOSED_CLASS
        elif lemmas:
            excluded = INFLECTION
        gloss = provider.gloss(word).split(" ; ")[0]
        out.append(
            Candidate(
                word=word,
                in_degree=count,
                dimensions=glosses.dimension_parts_of_speech(word, provider),
                gloss=gloss[:gloss_length],
                excluded=excluded,
                inflection_of=lemmas,
                inflection_share=inflection_share(word, lemmas, counts),
            )
        )
    return out


def structural_seeds(ranking, k: int) -> tuple[str, ...]:
    """The top `k` CANDIDATES — the excluded rows are skipped, not counted.

    `k` counts what would be seeded, so «top 100» means a hundred seeds and never «a hundred rows of
    which sixty were function words». That is the number the Captain is ruling on.
    """
    out: list[str] = []
    for candidate in ranking:
        if len(out) >= k:
            break
        if candidate.is_candidate:
            out.append(candidate.word)
    return tuple(out)


def excluded_head(ranking, reason: str, limit: int = 25) -> list[Candidate]:
    """The highest-ranked words one exclusion removed — the price of that exclusion, in order.

    Read beside the clean ranking, always: an exclusion is only as good as what it costs, and this
    is where a form that has a real content reading (`like`, `save`, `bar`) shows up as a number
    rather than as a worry.
    """
    return [c for c in ranking if c.excluded == reason][:limit]
