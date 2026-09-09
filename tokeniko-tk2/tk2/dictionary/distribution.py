"""D — THE DISTRIBUTIONAL MATRIX. What two definitions have in common, and nothing else.

Finding 4 of the 2026-08-12 review is why this file exists at all: `eat` and `food` have NO WordNet
relation between them, so R scores them 0.000 and requirement 2 («eat stays near food») and
requirement 10 («density from relations, never co-occurrence») cannot both hold in one matrix. The
prototype's answer — and the architecture since — is to stop blending them into a single float:
R states what the resource STATES, D states what two definitions SHARE, and a query consults the
one that can honestly answer it. Neither is folded into the other, here or anywhere downstream.

D IS SQUARE OVER THE SAME BASE KEYS AS R, in the same order, which is the whole reason
`build.build_base` computes the key space once and hands it to both. What differs is what fills the
cells; how they are shaped, stored and read is `matrix.py`'s, for both.

THE MINING SEAM IS THE ONE THE CLOSURE ALREADY USES, and that is a decision rather than a
convenience: `glosses.lexicon_words_in` carries requirement 21's repair (a token names every word it
could be, no winner picked), the Captain's stop-list ruling (membership outranks the stop list) and
the name refusal (option C — a spelling the resource knows only as a name names nothing). A D with
its own tokeniser would re-open every one of those defects, and quietly: two builds would differ and
no fingerprint could say why. What D adds is only the aim — a DIMENSION's gloss (`land.v` reads the
verb's definitions) where the closure reads a WORD's.

SYMMETRIC, AND R IS NOT. «These two definitions share these words» is one statement about a pair, so
row X column Y and row Y column X carry the same number; R's asymmetry exists because `entails` and
`entailed_by` are two different claims, and overlap has no such direction. It is computed per row
rather than per pair anyway — see `build` — so the symmetry is a property of the measure and not a
mirroring step that could be forgotten.

UNSIGNED. There is no negative overlap: two definitions share words or they do not. The sign is R's
alone, and it is the antonym column-read primitive (`row[X][index(W)] < 0`); a D cell can never be
mistaken for one because D never writes a negative number.

THE SHAPE OF A CELL'S VALUE, in one line, because the policy names four numbers and their order
matters: `floor <= min(cap, scale * measure(shared, a, b)) `, written only when the two share at
least `min_shared` words. The measure is over MASSES rather than counts, so a weighting (`idf`) is a
property of the vocabulary and not a fifth measure — under `uniform` every word weighs one and the
Jaccard is the plain set Jaccard the prototype computed.
"""

import math
from collections import defaultdict
from typing import Mapping, Protocol, runtime_checkable

from tk2.dictionary import glosses, keys
from tk2.dictionary.config import DistributionPolicy
from tk2.dictionary.matrix import (
    SOURCE_AXIS,
    SOURCE_MINED,
    Cell,
    Matrix,
    MatrixRow,
    Provenance,
    assert_square,
    dimension_index,
)

#: The diagonal. Declared by D's own policy rather than borrowed from R's `identity` weight: they
#: are two geometries, and a shared row would tie one matrix's axis to the other's weight table.
IDENTITY = "identity"

#: The one relation a D cell can carry. It is NOT one of R's — «their definitions share words» is
#: co-occurrence, which is precisely the claim R refuses to make (`relations.py`, head) — and it
#: keeps the prototype's name so a reader of either collection meets the same word.
GLOSS_OVERLAP = "gloss_overlap"


class DistributionIncoherent(ValueError):
    """The walk cannot be run as declared. Loud, for `RelationsIncoherent`'s reason: a D built
    around a parameter nobody could satisfy is a matrix the manifest describes and nobody has."""


@runtime_checkable
class DefinitionProvider(Protocol):
    """What D needs from a lexical resource beyond the gloss seam: one DIMENSION's definition.

    `GlossProvider.gloss` answers about a WORD, joining the readings of every part of speech, which
    is right for membership (a word is admitted for what it is defined as) and wrong for a geometry
    whose rows are POS-split: `land.n` and `land.v` would then have identical definitions and D
    would report them as the same point. So the resource is asked about the key.
    """

    def gloss_of_key(self, key: str, senses: str = "primary") -> str:
        """The definitions of the senses this dimension speaks for, under the declared sense cut."""
        ...


# ------------------------------------------------------------------------------------------------
# the vocabulary a gloss is read in
# ------------------------------------------------------------------------------------------------


def vocabulary_of(dimensions, provider, policy: DistributionPolicy) -> frozenset[str]:
    """The words a definition may be counted as naming.

    `base` derives it from the dimensions themselves rather than taking it as an argument, which is
    what keeps the two readings honestly comparable: under `base` D's intermediate vocabulary IS the
    base's own words (the prototype's reading — the subset was chosen for defining itself), and
    under `lexicon` it is everything the resource knows, so a definition may share a word the base
    does not contain.
    """
    if policy.vocabulary == "base":
        return frozenset(keys.word_of(key) for key in dimensions)
    return frozenset(keys.normalize_word(word) for word in provider.lexicon())


def gloss_vectors(dimensions, provider, policy: DistributionPolicy) -> dict[str, frozenset[str]]:
    """Each dimension's definition, reduced to the vocabulary words it names.

    The dimension's own word is dropped for `definition_in_lexicon`'s reason: «land: the land on
    which real estate is located» states nothing about two concepts, and counting it would give
    every POS-sibling pair a free shared word — which is exactly the pair (`land.n ~ land.v`) the
    Captain is ruling on.
    """
    vocabulary = vocabulary_of(dimensions, provider, policy)
    vectors: dict[str, frozenset[str]] = {}
    for key in dimensions:
        text = provider.gloss_of_key(key, policy.senses)
        named = glosses.lexicon_words_in(text, vocabulary, provider)
        vectors[key] = frozenset(named - {keys.word_of(key)})
    return vectors


def document_frequency(vectors: Mapping[str, frozenset[str]]) -> dict[str, int]:
    """How many dimensions' definitions name each word — D's own answer about its vocabulary.

    Reported as well as used: after the name refusal the loudest words left are real function words
    (`in`, `be`, `by`, `as`), and «what does the base's gloss vocabulary actually look like» is the
    question the weighting is ruled on.
    """
    counts: dict[str, int] = defaultdict(int)
    for words in vectors.values():
        for word in words:
            counts[word] += 1
    return dict(counts)


def word_weights(
    vectors: Mapping[str, frozenset[str]], policy: DistributionPolicy
) -> dict[str, float]:
    """What each vocabulary word is worth in an overlap.

    `uniform` — one word, one vote — is the prototype's reading and makes the measures the plain set
    measures. `idf` is log(N / df): a word that half the base uses carries almost nothing, a word
    two rows share carries nearly everything. It weights rather than excludes, which is the whole
    argument for it — a stop list here would be the third filter over the same tokens, and `in` is
    a real English word that the base admits on purpose.

    The smoothing is `log(1 + N/df)` rather than `log(N/df)` for one reason worth stating: the bare
    form gives a word every dimension names a weight of exactly zero, which would delete it from the
    union as well as the intersection and let two definitions that share NOTHING BUT it score a
    perfect 0/0. A word nobody can avoid is worth little; it is never worth nothing.
    """
    if policy.weighting == "uniform":
        return {}
    total = max(1, len(vectors))
    return {
        word: math.log(1.0 + total / count)
        for word, count in document_frequency(vectors).items()
    }


# ------------------------------------------------------------------------------------------------
# the measure
# ------------------------------------------------------------------------------------------------


def overlap(shared: float, left: float, right: float, measure: str) -> float:
    """How much of two definitions is the same, over masses (a count under `uniform` weighting).

    The three differ only in what they divide by, and the difference is a real one at this base:
    Jaccard punishes a long definition against a short one, `dice` splits the difference, `cosine`
    is the gentlest of the three. Which one is right is the Captain's; that they are the same
    statement measured three ways is why they live in one function.
    """
    if shared <= 0 or left <= 0 or right <= 0:
        return 0.0
    if measure == "jaccard":
        union = left + right - shared
        return shared / union if union > 0 else 0.0
    if measure == "dice":
        return 2.0 * shared / (left + right)
    if measure == "cosine":
        return shared / math.sqrt(left * right)
    raise DistributionIncoherent(f"unknown overlap measure {measure!r}")


def value_of(shared: float, left: float, right: float, policy: DistributionPolicy) -> float:
    """One cell's weight, or 0.0 for «D says nothing about these two».

    The order is the prototype's and it is load-bearing: measure, then scale, then cap, then the
    floor. A floor applied before the scale would be a floor on a different number.
    """
    raw = overlap(shared, left, right, policy.measure)
    if raw <= 0:
        return 0.0
    scaled = min(policy.scale * raw, policy.cap)
    return scaled if scaled >= policy.floor else 0.0


# ------------------------------------------------------------------------------------------------
# the walk
# ------------------------------------------------------------------------------------------------


def build(
    dimensions,
    provider,
    policy: DistributionPolicy,
    name: str = "base_d",
    progress=None,
) -> Matrix:
    """Fill D over `dimensions` — the call the build tool makes, beside R's.

    THE WALK IS INVERTED, exactly as R's is and for the same arithmetic: comparing every ordered
    pair of keys is 19.8 million comparisons at the full base, almost all of them to discover that
    two definitions share nothing. Here each dimension meets only the dimensions its own gloss words
    reach, through a posting list built once — which produces the same cells (a cell exists iff two
    definitions share at least `min_shared` words) in time proportional to the overlaps.

    Row by row rather than pair by pair, and that is a memory decision with a measured reason: under
    `senses="all"` there are 3.8 million pairs sharing a word, and a dictionary of them is a
    gigabyte of tuples. A row's neighbours are a few thousand entries and are emitted before the
    next row is walked.
    """
    index = dimension_index(dimensions)
    order = tuple(index)

    vectors = gloss_vectors(order, provider, policy)
    weights = word_weights(vectors, policy)

    def mass_of(word: str) -> float:
        # Empty under `uniform` — one word, one vote — so the default IS the uniform reading.
        return weights.get(word, 1.0)

    posting: dict[str, list[str]] = defaultdict(list)
    for key in order:
        for word in vectors[key]:
            posting[word].append(key)

    mass: dict[str, float] = {key: sum(mass_of(w) for w in vectors[key]) for key in order}

    rows = []
    for position, key in enumerate(order, 1):
        cells = []
        if policy.identity:
            cells.append(
                Cell(
                    column=key,
                    weight=policy.identity,
                    relation=IDENTITY,
                    source=SOURCE_AXIS,
                    via=(Provenance(IDENTITY, policy.identity),),
                )
            )
        shared_mass: dict[str, float] = defaultdict(float)
        shared_count: dict[str, int] = defaultdict(int)
        for word in vectors[key]:
            weight = mass_of(word)
            for column in posting[word]:
                if column == key:
                    continue
                shared_mass[column] += weight
                shared_count[column] += 1

        for column in sorted(shared_mass, key=lambda k: index[k]):
            if shared_count[column] < policy.min_shared:
                continue
            weight = value_of(shared_mass[column], mass[key], mass[column], policy)
            if not weight:
                continue
            cells.append(
                Cell(
                    column=column,
                    weight=round(weight, 6),
                    relation=GLOSS_OVERLAP,
                    source=SOURCE_MINED,
                    via=(Provenance(GLOSS_OVERLAP, round(weight, 6)),),
                )
            )
        rows.append(MatrixRow(key=key, index=index[key], cells=tuple(cells)))
        if progress is not None:
            progress(position, len(order))

    matrix = Matrix(name=name, keys=order, rows=tuple(rows))
    assert_square(matrix)
    return matrix


# ------------------------------------------------------------------------------------------------
# reading D back — what the vocabulary is doing
# ------------------------------------------------------------------------------------------------


def shared_words(vectors: Mapping[str, frozenset[str]], a: str, b: str) -> tuple[str, ...]:
    """The words two dimensions' definitions have in common — D's `via`, at the vocabulary level.

    A cell can name the relation that made it (`gloss_overlap`) and that is not much of an answer,
    because D has only one relation; what a reader actually wants to argue with is WHICH words were
    shared. It is not stored per cell — a hundred and fifty thousand cells carrying their word lists
    is a different order of collection — so it is recomputed from the vectors when asked.
    """
    return tuple(sorted(vectors.get(a, frozenset()) & vectors.get(b, frozenset())))


def junk_pollution(
    vectors: Mapping[str, frozenset[str]],
    junk: frozenset[str],
    min_shared: int = 1,
    weights: Mapping[str, float] | None = None,
) -> dict:
    """How much of D's evidence is nothing but the words everybody uses.

    THE T2b FIGURE, generalised. Before the name refusal, 84.8% of the base's overlapping pairs
    shared nothing but `or` (Oregon) and its kind; after it, 59.1% shared nothing but real function
    words. Two numbers rather than one, because a WEIGHTING moves only the second:

      - `pairs_only_junk` — of the pairs that overlap at all, the share whose every shared word is
        junk. A fact about membership; `idf` cannot change it, only a filter could.
      - `mass_from_junk` — of all the shared-word mass in D, the share those words carry. This is
        what a down-weight actually moves, and therefore the honest figure to rule on. Pass the
        weighting's own `weights` to measure it AS WEIGHTED: without them every word counts one, and
        the figure would report the uniform reading under an idf run's name.
    """
    posting: dict[str, list[str]] = defaultdict(list)
    for key, words in vectors.items():
        for word in words:
            posting[word].append(key)

    def mass_of(word: str) -> float:
        return weights.get(word, 1.0) if weights else 1.0

    overlapping = 0
    only_junk = 0
    total_mass = 0.0
    junk_mass = 0.0
    for key in vectors:
        counts: dict[str, int] = defaultdict(int)
        junk_counts: dict[str, int] = defaultdict(int)
        mass: dict[str, float] = defaultdict(float)
        junk_share: dict[str, float] = defaultdict(float)
        for word in vectors[key]:
            weight = mass_of(word)
            for column in posting[word]:
                if column == key:
                    continue
                counts[column] += 1
                mass[column] += weight
                if word in junk:
                    junk_counts[column] += 1
                    junk_share[column] += weight
        for column, count in counts.items():
            if count < min_shared:
                continue
            overlapping += 1
            total_mass += mass[column]
            junk_mass += junk_share[column]
            if junk_counts[column] == count:
                only_junk += 1

    return {
        "overlapping_pairs": overlapping // 2,
        "pairs_only_junk": only_junk // 2,
        "pairs_only_junk_pct": round(100 * only_junk / overlapping, 2) if overlapping else 0.0,
        "shared_mass": round(total_mass / 2, 2),
        "mass_from_junk": round(junk_mass / 2, 2),
        "mass_from_junk_pct": round(100 * junk_mass / total_mass, 2) if total_mass else 0.0,
    }
