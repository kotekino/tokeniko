"""THE SENSE LAYER — the dictionary's second floor, and the half E1 did not build.

E1 built the BASE: 4,555 POS-split keys, the frame the geometry is stated over. The resource carries
68,779 words and 120,475 senses, and this is where those live. The division is E1c's ruling and it
is worth stating in one line, because it answers a question that ran the whole of E1: **the base is
the frame, the senses are the content.**

WHY THAT SETTLES THE `senses="primary"` ROT. A base dimension reads its definition from WordNet's
FIRST synset, so `small.n` reads «the slender part of the back» and `state.n` reads «the territory
occupied by…». That was called a defect all through E1, and the alternatives were measured: reading
EVERY sense into the dimension (`senses="all"`) triples the key space and collapses the bar to 1 of
7, and taking the UNION of a dimension's senses into its gloss vector costs 15 stated oppositions and
lifts every FAR control, because a thirteen-word vector shares words with everything. The rot was
never in `primary`. It was in having nowhere else to put the other senses. Here is the nowhere else:
the base's 4,555 dimensions cover 17,257 senses at a mean of 3.79 apiece, and 73% of what a
dimension means was being discarded until this file.

IT RIDES ON THE BASE AND IT IS NEVER SQUARE — the architecture guard, tkzip req 11. A sense's cells
are BASE DIMENSIONS. 120,475 senses against 4,555 dimensions is half a billion possible cells and
about half a million real ones; senses against senses would be 14.5 BILLION, and the shape of this
module is what makes that impossible to write by accident.

TWO VECTORS, MIRRORING THE TWO FLOORS, so that one law reads both:

  - `distribution` is the sense's own definition, reduced through THE SAME SEAM D uses. Not a
    similar one: `glosses.lexicon_words_in` carries requirement 21's repair, the Captain's stop-list
    ruling, the name refusal and the structure filter, and a second reduction here would re-open
    every one of them quietly — two builds would differ and no fingerprint could say why.
  - `relations` is what WordNet states about THIS SYNSET, mapped onto base dimensions. It is
    evidence the base structurally cannot hold: relations are stated per synset, and collapsing
    synsets to POS keys is what lost them. `bank.n.01` reaches `slope`; `bank.n.02` reaches
    `financial institution`; `bank.n` is both at once and so reaches neither cleanly.

MEASURED BEFORE IT WAS BUILT, and both numbers matter to a reader deciding what to trust: the gloss
reaches 3.41 base dimensions on average and is EMPTY for 5.3% of senses; the synset's relations reach
0.86 and are EMPTY for 54.1%, because most of a synset's relatives are not base words. Relations
alone cannot place a sense. Together they can, and a row whose `relations` is empty while its
`distribution` is not is the normal case rather than a fault.

PURE, like the rest of this package: the provider is injected, the policy arrives as a value, and
nothing here knows what a database is.
"""

from dataclasses import dataclass

from tk2.dictionary import glosses, keys
from tk2.dictionary.config import DictionaryConfig
from tk2.dictionary.distribution import GLOSS_OVERLAP, vocabulary_of
from tk2.dictionary.matrix import Cell, Provenance, SOURCE_MINED, dimension_index
from tk2.dictionary.relations import known_relations


@dataclass(frozen=True, slots=True)
class SenseVector:
    """One sense, placed. `distribution` and `relations` are cells over BASE dimensions."""

    key: str
    base: str
    ordinal: int
    synset: str
    definition: str
    distribution: tuple[Cell, ...] = ()
    relations: tuple[Cell, ...] = ()

    @property
    def is_placed(self) -> bool:
        """Whether anything at all places this sense. False is a legitimate answer — 5.3% of senses
        name no base word and 54.1% reach none by relation — and it is reported rather than hidden,
        because a sense the geometry cannot see is a sense the station will have to ABSTAIN on."""
        return bool(self.distribution or self.relations)


def senses_of(word: str, provider) -> list[dict]:
    """Every sense of one word, as the provider states them. A thin pass-through, named so the
    walk below reads as what it is."""
    return provider.sense_keys(word)


def distribution_cells(definition, own_word, vocabulary, provider, policy, index, mass_of=None):
    """A sense's own definition, against the base's dimensions.

    THE VECTOR IS AN INDICATOR, and the reason is structural rather than a shortcut: D's cells score
    how much TWO DEFINITIONS overlap, but a sense is being placed against a DIMENSION, which is one
    word and not a definition. «This definition names `slope`» has no magnitude of its own — and
    within one sense's own definition there is nothing that makes one named dimension weigh more
    than another. So every cell of a sense's distribution vector carries the same weight, the walk's
    declared `cap`, and the module says so instead of computing a number that would look like
    evidence and be none.

    It was measured the other way first, scoring 1-shared-word against the definition's length
    through `value_of`: 94.8% of the cells landed exactly on the cap anyway, which is the same
    saturation finding that halved D's own gate at T4 — and the 5.2% that varied were varying by
    definition LENGTH, which is a fact about prose and not about meaning.

    `mass_of` is the seam that keeps this honest under a later ruling: `weighting` is a policy row,
    and under `idf` a rare named word IS worth more than a common one. Passed, the cells stop being
    flat and start carrying the vocabulary's own answer. Under `uniform` — the standing reading — it
    degenerates to the indicator above, which is what `uniform` means.

    The word's OWN name is dropped for `gloss_vectors`' reason: «land: the land on which real estate
    is located» states nothing about two concepts, and counting it would give every sense of a word
    a free cell on its own base key. A named word may be several dimensions (`land` is `land.n` and
    `land.v`) and states a cell on each: the base's digraph fans out the same way, and it is why a
    sense reaching 3.41 dimensions names rather fewer words.
    """
    named = glosses.lexicon_words_in(definition, vocabulary, provider) - {own_word}
    if not named:
        return ()

    masses = {word: (mass_of(word) if mass_of else 1.0) for word in named}
    heaviest = max(masses.values()) or 1.0

    cells = []
    for word in sorted(named):
        weight = policy.cap * (masses[word] / heaviest)
        if weight < policy.floor:
            continue
        for column in sorted(k for k in index if keys.word_of(k) == word):
            cells.append(
                Cell(
                    column=column,
                    weight=weight,
                    relation=GLOSS_OVERLAP,
                    source=SOURCE_MINED,
                    via=(Provenance(relation=GLOSS_OVERLAP, weight=weight),),
                    evidence=word,
                )
            )
    return tuple(cells)


def relation_cells(sense: str, provider, policy, index):
    """What WordNet states about this synset, on the base's dimensions.

    Every target is a SENSE (`slope.n.01`); it lands on the base dimension it truncates to
    (`slope.n`), and only if that dimension exists. Most do not — the base is 4,555 keys out of
    68,779 words — which is why 54.1% of senses reach nothing this way.
    """
    weights = dict(policy.weights)
    found: dict[str, list[Provenance]] = {}
    for relation, targets in provider.relations_of_sense(sense).items():
        weight = weights.get(relation)
        if weight is None:
            continue
        for target in targets:
            column = keys.base_of(target) if keys.is_sense_key(target) else target
            if column in index:
                found.setdefault(column, []).append(
                    Provenance(relation=relation, weight=weight)
                )

    cells = []
    for column in sorted(found):
        # The strongest claim wins the cell and the rest ride along as provenance — R's own
        # precedence, so a reader comparing a sense to its base key is comparing like with like.
        stated = sorted(found[column], key=lambda p: (-abs(p.weight), p.relation))
        winner = stated[0]
        cells.append(
            Cell(
                column=column,
                weight=winner.weight,
                relation=winner.relation,
                source=SOURCE_MINED,
                via=tuple(stated),
                evidence=sense,
            )
        )
    return tuple(cells)


def build(dimensions, words, provider, config: DictionaryConfig, closed=None, progress=None):
    """Place every sense of every word in `words` against `dimensions`.

    `words` is an argument rather than «the lexicon» because the two callers want different
    populations and neither should have to hope: the build tool passes the whole lexicon (120,475
    senses), a test passes six. What it must NOT be handed is the dimensions' own words only — the
    point of the layer is that a sense of a word the base does not contain still has a place in the
    base's space.
    """
    if config.distribution is None:
        raise PolicyIncomplete(
            "the policy declares no gloss walk, so a sense has no way to be placed by its "
            "definition. Policy v6 (the baseline's `distribution` rows) is what declares one."
        )
    if config.relations is None:
        raise PolicyIncomplete(
            "the policy declares no relation weights, so a sense's synset has nothing to state "
            "with. Policy v3 is what declares them."
        )

    index = dimension_index(dimensions)
    vocabulary = vocabulary_of(tuple(index), provider, config.distribution, closed)

    placed: list[SenseVector] = []
    for position, word in enumerate(words, 1):
        for entry in senses_of(word, provider):
            key = entry["key"]
            placed.append(
                SenseVector(
                    key=key,
                    base=entry["base"],
                    ordinal=keys.split_sense_key(key)[2],
                    synset=entry["synset"],
                    definition=entry["definition"],
                    distribution=distribution_cells(
                        entry["definition"], keys.word_of(entry["base"]),
                        vocabulary, provider, config.distribution, index,
                    ),
                    relations=relation_cells(key, provider, config.relations, index),
                )
            )
        if progress is not None and position % 5000 == 0:
            progress(position, len(words))
    return placed


def stats(placed) -> dict:
    """What a build has to report about a layer nobody can eyeball: how much of it is actually
    placed, and by which floor. An unplaced sense is not an error and is not silence either — it is
    a sense the station will have to ABSTAIN on, and the count is what makes that predictable."""
    n = len(placed)
    if not n:
        return {"senses": 0, "placed": 0, "distribution_cells": 0, "relation_cells": 0}
    d = sum(len(s.distribution) for s in placed)
    r = sum(len(s.relations) for s in placed)
    return {
        "senses": n,
        "placed": sum(1 for s in placed if s.is_placed),
        "unplaced": sum(1 for s in placed if not s.is_placed),
        "no_distribution": sum(1 for s in placed if not s.distribution),
        "no_relations": sum(1 for s in placed if not s.relations),
        "distribution_cells": d,
        "relation_cells": r,
        "mean_distribution": round(d / n, 2),
        "mean_relations": round(r / n, 2),
    }


class PolicyIncomplete(ValueError):
    """A policy version that cannot place a sense — see `build`."""


#: The layer's name where a matrix would carry its own — the seal, the manifest and the verifier all
#: key on it, and it is not a matrix name because the layer is not a matrix.
SENSE_LAYER = "dictionary_sense_vectors"


def fingerprint(placed) -> str:
    """A content hash over the whole layer, for the seal to vouch for.

    THE SAME PROPERTY `matrix.fingerprint` has and for the same reason: what a build wrote and what
    a database gives back are two different things, and only a hash recomputed from the READ can
    tell them apart. Order-independent by construction — the layer has no canonical row order and a
    hash that depended on one would fail on a re-read that sorted differently.
    """
    import hashlib

    digest = hashlib.sha256()
    for sense in sorted(placed, key=lambda s: s.key):
        digest.update(sense.key.encode())
        digest.update(sense.synset.encode())
        for label, cells in (("d", sense.distribution), ("r", sense.relations)):
            digest.update(label.encode())
            for cell in sorted(cells, key=lambda c: c.column):
                digest.update(f"{cell.column}:{cell.weight:.6f}:{cell.relation}".encode())
    return digest.hexdigest()
