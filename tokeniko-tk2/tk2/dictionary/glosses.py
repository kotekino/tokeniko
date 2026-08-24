"""THE GLOSS SEAM — what a lexical resource must answer, and how a definition becomes edges.

The Captain's method, 2026-08-12: take the DEFINITIONS of the lexicon's words, shorten each to use
only lexicon words, and the subset is where the intersections are smallest. His trivial example —

    me -> not you | you -> not me | not -> negation | negation -> not
    => {me, not, you, negation} defines itself and never leaves

This module owns the reduction — tokenise, drop the stop words, land each token on a lexicon word,
drop the self-reference — and declares the PROVIDER protocol the reduction reads through. The split
is deliberate: the reduction is POLICY and stays pure and testable on a handcrafted fixture; the
provider is the RESOURCE (WordNet, today) and is injected, so nothing in this package imports nltk.

The known defect lives here and gets fixed here: requirement 21 — «something *left* over» minted
`left`, the direction, because `left` was matched as a bare surface form instead of as a lemma of
`leave`. The lemma path below is the place that fix lands; the fixture that reproduces the pull is
already in the tests.
"""

import re
from typing import Protocol, runtime_checkable

# A definition's words. Hyphens stay inside a token (`well-being` is one word to a lexicographer);
# digits and punctuation are not lexicon words and never were.
TOKEN = re.compile(r"\b[a-z][a-z-]*\b")

# Below this a token carries no lexical weight and matching it produces noise, never an edge.
MIN_TOKEN_LENGTH = 2


@runtime_checkable
class GlossProvider(Protocol):
    """What the closure engine needs from a lexical resource — and nothing more.

    Kept this small on purpose: everything the engine could compute itself, it computes itself, so
    two providers (the real WordNet and a twenty-word fixture) cannot drift into two different
    reductions of the same gloss.
    """

    def lexicon(self) -> tuple[str, ...]:
        """The words the definition digraph is built over, in the resource's own order."""
        ...

    def gloss(self, word: str, senses: str = "primary") -> str:
        """The definition text. Definitions only — an example sentence is usage, not definition."""
        ...

    def parts_of_speech(self, word: str) -> tuple[str, ...]:
        """Every POS the word actually has, so the POS split costs one dimension per real POS."""
        ...

    def lemmas(self, token: str) -> tuple[str, ...]:
        """The base forms a surface token could be, best first. `takes` -> `take`."""
        ...

    def stopwords(self) -> frozenset[str]:
        """The resource's stop list. A property of the language, so the resource owns it — but the
        reduction reads it through here so a fixture can declare its own twenty."""
        ...


# ------------------------------------------------------------------------------------------------
# the reduction — a definition rewritten using only lexicon words
# ------------------------------------------------------------------------------------------------


def tokens_of(text: str) -> list[str]:
    """Lower-cased words, in the order the gloss says them. Order is kept even though the caller
    takes a set: a later reader (the miner, the curator) needs to quote the token that spoke."""
    return [t for t in TOKEN.findall(text.lower()) if len(t) >= MIN_TOKEN_LENGTH]


def lexicon_words_in(
    text: str,
    lexicon: frozenset[str],
    provider: GlossProvider,
    stopwords: frozenset[str] | None = None,
) -> set[str]:
    """Every lexicon word a gloss names, surface form first, then the token's lemmas.

    A gloss says «takes in solid food» and `takes` must land on `take`. The surface form is tried
    first because a word that IS in the lexicon means itself — lemmatising it first would send
    `left` (the direction, a lexicon word in its own right) to `leave` on the strength of a
    coincidence, and the review's finding is that the coincidence goes the other way just as often.
    """
    stops = provider.stopwords() if stopwords is None else stopwords
    out: set[str] = set()
    for token in tokens_of(text):
        if token in stops:
            continue
        if token in lexicon:
            out.add(token)
            continue
        for lemma in provider.lemmas(token):
            if lemma in lexicon:
                out.add(lemma)
                break
    return out


def definition_in_lexicon(
    word: str,
    lexicon: frozenset[str],
    provider: GlossProvider,
    senses: str = "primary",
    stopwords: frozenset[str] | None = None,
) -> set[str]:
    """One node's out-edges: the lexicon words its definition is written with, minus itself.

    The self-reference is dropped because «land: the land on which real estate is located» states
    nothing about two concepts — it is a tautology, and mining it is how a POS-split base gets
    re-merged by an edge that says only that a word is itself.
    """
    text = provider.gloss(word, senses)
    return lexicon_words_in(text, lexicon, provider, stopwords) - {word}


def names_word(text: str, target: str, provider: GlossProvider) -> str | None:
    """`lexicon_words_in`'s matching aimed at ONE word instead of the whole lexicon — returns the
    surface token that named it, or None.

    Needed because a curation target may be a dimension without being a lexicon word (`swallow`,
    `runway` arrived by membership repair), which the set-based reduction filters out by
    construction. The token is returned rather than a boolean because the Captain's approval reads
    the evidence verbatim.
    """
    target = target.lower()
    stops = provider.stopwords()
    for token in tokens_of(text):
        if token in stops:
            continue
        if token == target:
            return token
        if target in provider.lemmas(token):
            return token
    return None
