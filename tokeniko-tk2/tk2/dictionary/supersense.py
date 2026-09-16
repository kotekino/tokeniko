"""THE SUPERSENSE — what KIND of thing a word names, as the resource itself states it.

**THE QUESTION THIS ANSWERS, AND WHY THE COSINE COULD NOT.** «I swam in the pool» is a LOCATION and
«I left in May» is a TIME, and the only difference between them is what kind of thing `pool` and
`May` are. That is a question about the TAXONOMY — *is this a place? is this a stretch of time?* —
and the standing ruling of the dictionary chapter is that geometry does not answer taxonomy:
*«dictionary cosine = co-occurrence, not hypernymy; true cross-abstraction edges read FAR»*. It was
benched here anyway, because `db/0008` predicted geometry would be the instrument, and it measured
worse than the resource's own label on every bucket. The record is in
`docs/parser-compiler/202609161010_the-ambiguous-markers.md`.

**WHAT A SUPERSENSE IS.** WordNet files every synset in one of 45 *lexicographer files* — 26 for
nouns, 15 for verbs, plus the adjective and adverb files — and the name of that file is a broad
semantic class the lexicographer assigned: `noun.time`, `noun.person`, `noun.location`,
`verb.motion`, `verb.communication`. It is PUBLISHED and it is CLOSED, which is the same property
that made Universal Dependencies the station's gate: **both ends of the mapping are finite, so the
table from a supersense to a tkzip role can be complete rather than merely large.**

**THE PRIMARY SENSE, AND NOT THE BEST OF ALL OF THEM.** `db/0006` ruled that a dimension IS its
primary sense; the same rule holds here and for a sharper reason. Reading every sense and taking the
strongest was measured first and it is *garbage*: `pool` comes back as a TIME through `pool.n.08`,
`table` as a TIME, `dog` as an INSTRUMENT. A word's eighth reading is a different word for every
practical purpose, and a max over senses is a machine for finding it.

**THE PROVENANCE DEBT, NAMED.** This reads WordNet LIVE. It is therefore not covered by the base's
build fingerprint, and a station that answered differently after an nltk upgrade would have no
record saying so. The honest home is the sense layer — `SenseVectorDoc` already stores each sense's
`synset` as provenance, and a `lexname` beside it would be sealed like everything else. That is a
rebuild, and it is named here rather than done quietly.
"""

from __future__ import annotations

from nltk.corpus import wordnet as wn

#: WordNet's 26 noun lexicographer files, published. FRAME: the resource defines the set, and a name
#: outside it means the corpus is not the one this was written against.
NOUN_SUPERSENSES = (
    "noun.Tops", "noun.act", "noun.animal", "noun.artifact", "noun.attribute", "noun.body",
    "noun.cognition", "noun.communication", "noun.event", "noun.feeling", "noun.food", "noun.group",
    "noun.location", "noun.motive", "noun.object", "noun.person", "noun.phenomenon", "noun.plant",
    "noun.possession", "noun.process", "noun.quantity", "noun.relation", "noun.shape", "noun.state",
    "noun.substance", "noun.time",
)

#: WordNet's 15 verb lexicographer files, published.
VERB_SUPERSENSES = (
    "verb.body", "verb.change", "verb.cognition", "verb.communication", "verb.competition",
    "verb.consumption", "verb.contact", "verb.creation", "verb.emotion", "verb.motion",
    "verb.perception", "verb.possession", "verb.social", "verb.stative", "verb.weather",
)

SUPERSENSES = NOUN_SUPERSENSES + VERB_SUPERSENSES

#: UD's universal POS tags -> the WordNet part of speech to ask about. Only the two the selector
#: needs: a marker's role is settled by what the NOMINAL is and what the VERB does.
UD_POS_TO_WORDNET = {"NOUN": "n", "PROPN": "n", "PRON": "n", "VERB": "v", "AUX": "v"}


def supersense_of(lemma: str, pos: str) -> str | None:
    """The class WordNet files this word's PRIMARY reading under, or None if it holds no reading.

    `pos` is WordNet's own letter (`n`, `v`), not UD's tag — use `supersense_for` for a UD token.

    **None is an answer and not a failure.** A word the resource does not hold gets no supersense,
    the marker's rules find nothing to fire on, and the curation's default stands — named as a
    default, so the confidence scalar (req 4) can tell it from a settled read.
    """
    if not lemma:
        return None
    readings = wn.synsets(lemma.lower().replace(" ", "_"), pos)
    return readings[0].lexname() if readings else None


def supersense_for(lemma: str, upos: str) -> str | None:
    """The same, for a token described the way a skeleton describes it."""
    letter = UD_POS_TO_WORDNET.get((upos or "").upper())
    return None if letter is None else supersense_of(lemma, letter)
