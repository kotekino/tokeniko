"""THE VERB FRAMES — whether a verb takes an object, as the resource itself states it.

**THE QUESTION THIS ANSWERS.** «the fish the cat ate» and «the day I slept» are the same tree — a
zero relative, its subject said, no object — and the antecedent is the OBJECT in one and an
ADVERBIAL in the other. Only the verb's VALENCY separates them (G5, the fixpoints note of
2026-09-24), and WordNet publishes it: every verb sense carries the numbered sentence frames it is
used in — «Somebody ----s something», «Somebody ----s», «Something ----s to somebody».

**AN OBJECT FRAME IS READ OFF THE RESOURCE'S OWN STRINGS, NOT LISTED.** A frame takes an object when
the token after the verb slot in its published string is `something` or `somebody`. That is decoding
WordNet's notation, which is frame; which verbs have which frames is the resource's, and nothing
here chooses it.

**READ ON THE LEMMA, NOT THE SYNSET.** A synset's own `frame_ids` omit the frames WordNet attaches
to one lemma of it and not the others, so the lemma's are read where the verb is one.

**THE PRIMARY SENSE**, `db/0006`'s rule, as `supersense` reads it — and with the cost that rule
always carries: WordNet splits valency across senses (`cook.v.01` is intransitive, `cook.v.02`
transitive), so any primary-sense reading inherits the resource's sense order. Measured, not
assumed: `tools/relative_gap_bench.py` (2026-09-25), which is also where the alternatives — any
sense, strict — were measured and refused.

**THE PROVENANCE DEBT is `supersense`'s own, and named there**: this reads WordNet live.
"""

from __future__ import annotations

from functools import cache

from tk2.dictionary import wordnet as wn

#: WordNet's frame strings number 35. FRAME: the resource publishes them, and a corpus with a
#: different count is not the one this was written against.
FRAME_COUNT = 35

#: The tokens WordNet's frame strings use for a participant — `Somebody ---- SOMETHING`. The
#: notation's own vocabulary, read to decode it; not a judgement about English.
PARTICIPANTS = ("something", "somebody")


@cache
def canonical_frames() -> dict[int, str]:
    """WordNet's 35 frame strings with the verb slot as `----`, read off single-word lemmas.

    NLTK prints a frame with the lemma already substituted («Somebody sleeps»), so the slot is found
    by where the lemma stands — which is why a multi-word lemma, whose substitution spans tokens, is
    skipped.
    """
    found: dict[int, str] = {}
    for synset in wn.all_synsets("v"):
        for lemma in synset.lemmas():
            name = lemma.name()
            if "_" in name:
                continue
            for number, text in zip(lemma.frame_ids(), lemma.frame_strings()):
                if number not in found:
                    found[number] = " ".join("----" + t[len(name):] if t.startswith(name) else t
                                             for t in text.split())
        if len(found) >= FRAME_COUNT:
            break
    return found


def takes_object(frame: str) -> bool:
    """Does this frame string put a participant straight after the verb?"""
    words = frame.split()
    slot = next(i for i, w in enumerate(words) if w.startswith("----"))
    return slot + 1 < len(words) and words[slot + 1] in PARTICIPANTS


@cache
def object_frames() -> frozenset[int]:
    """The numbers of the frames that take an object, derived from the strings."""
    return frozenset(n for n, s in canonical_frames().items() if takes_object(s))


def _lemma_frames(synset, verb: str) -> set[int]:
    for lemma in synset.lemmas():
        if lemma.name().lower() == verb:
            return set(lemma.frame_ids())
    return set(synset.frame_ids())


def verb_senses(verb: str) -> list[set[int]]:
    """The frame numbers of every verb sense of this lemma, in WordNet's own sense order."""
    verb = (verb or "").lower()
    return [_lemma_frames(s, verb) for s in wn.synsets(verb, "v")] if verb else []


def primary_takes_object(verb: str) -> bool | None:
    """Does the PRIMARY sense of this verb have an object frame? None when WordNet holds no verb.

    «Has one», not «has only such»: the bench's permissive reading, which is the one the Captain's
    agreement rule was measured with (`tools/relative_gap_bench.py`, candidate a1 inside c1).
    """
    senses = verb_senses(verb)
    if not senses:
        return None
    return bool(senses[0] & object_frames())
