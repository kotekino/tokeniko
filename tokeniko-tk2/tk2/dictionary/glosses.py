"""THE GLOSS SEAM — what a lexical resource must answer, and how a definition becomes edges.

The Captain's method, 2026-08-12: take the DEFINITIONS of the lexicon's words, shorten each to use
only lexicon words, and the subset is where the intersections are smallest. His trivial example —

    me -> not you | you -> not me | not -> negation | negation -> not
    => {me, not, you, negation} defines itself and never leaves

This module owns the reduction — tokenise, land each token on the lexicon words it could be naming,
drop the stop words that are not lexicon words, drop the self-reference — and declares the PROVIDER
protocol the reduction reads through. The split is deliberate: the reduction is POLICY and stays
pure and testable on a handcrafted fixture; the provider is the RESOURCE (WordNet, today) and is
injected, so nothing in this package imports nltk.

REQUIREMENT 21 LANDED HERE (2026-08-25). «something *left* over» minted `left`, the direction,
because the surface form was tried first and the match stopped there. The repair is not to try the
lemma first — that only moves the blindness («turn left» would become `leave`) — it is to stop
picking a winner at all: a token names every lexicon word it could be, and the POS a word only
reaches by INFLECTION stops being a POS it can mint a dimension for. Two levels, both needed:

  - here, in the reduction: `left` in a gloss names `leave` AND `left`; the ambiguity is real and
    the layer that can settle it is the geometry this mining feeds, not a regex.
  - one level up, at the key: `left.v` and `used.v` cease to exist, because `parts_of_speech` may
    only report the POS a word is a BASE FORM of. That is where the duplicate dimensions died.

THE STOP LIST YIELDS TO MEMBERSHIP (the Captain's ruling, 2026-08-25). A word that is in the lexicon
is never dropped as a stop word: the stop list is a statement about function words in text, and once
a word is a dimension, what its gloss names is the geometry's business and not a filter's. The list
still applies to every token that is not a lexicon word — which is what keeps «was» from quietly
naming `be`.

The ruling was made so his closure example above could form at all: `me`, `you`, `not` and `be` are
all nltk stop words and the old order deleted them before the lexicon was ever consulted. Measured
afterwards (2026-08-25), it still cannot form on WordNet, for a reason no filter owns: `you` is not
a WordNet lemma at all and WordNet's `me` is the state of Maine. That is a MEMBERSHIP finding — the
method is sound, the resource cannot supply the vocabulary the method was stated in.

A NAME IS NOT A WORD (the Captain's option C, 2026-08-25). The ruling above bought real function
words — `not`, `no`, `some`, `other`, `own`, `will`, `very` — and admitted, in the same motion,
WordNet's case-folded names of the same spellings: `or` = Oregon, `me` = Maine, `an` = Associate in
Nursing. Measured before the repair, `or` sat on 57.8% of the base's rows, and of every pair of base
words that shared a gloss word at all, 84.8% shared nothing but these; D is gloss overlap, so its
loudest signal would have been «both definitions used the word *or*». Measured after, on the same
six hundred words: 77,242 overlapping pairs became 27,942 and the share fell to 59.1%, the rest of
it being `in`, `be`, `by` and `as` — real English function words that the ruling admitted on
purpose, and a separate question. The refusal is a fact about the
resource and therefore a provider question (`is_name_only`), asked here on every reading a token
produces. It is NOT the stop list returning through a side door: the stop list is about function
words, this is about whether a spelling is vocabulary at all, and `not` — a function word and a real
adverb — survives both.
"""

import re
from typing import Protocol, runtime_checkable

from tk2.dictionary import keys

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
        """The definition text. Definitions only — an example sentence is usage, not definition.

        The word's OWN senses. A resource that answers `used` with `use`'s definitions is answering
        about another word (see `parts_of_speech`).
        """
        ...

    def parts_of_speech(self, word: str) -> tuple[str, ...]:
        """Every POS the word is a BASE FORM of — never one it only reaches by inflection.

        This is requirement 21 at the dimension level, and it is a contract on the provider because
        `keys.keys_for_word` takes the POS list as DATA. Asked «what is `used`?», a resource happily
        answers «an adjective, and a verb», having walked back from `used` to `use`; reporting that
        verb mints `used.v`, which is a second name for `use.v` — a duplicate dimension. `left.v` is
        the same defect wearing `leave`'s participle.
        """
        ...

    def lemma(self, token: str, pos: str) -> str | None:
        """The base form of `token` READ AS `pos`, or None if it is not that part of speech at all.

        Per-POS on purpose: `left` read as a verb is `leave`, read as a noun it is `left`, and both
        answers are correct. A call that collapses them has already discarded the one fact
        requirement 21 needs.
        """
        ...

    def lemmas(self, token: str) -> tuple[str, ...]:
        """Every base form the token could be, over every POS, deduplicated.

        A convenience over `lemma` for the callers that do not care which POS spoke. The order is
        NOT a ranking — since the repair, nothing picks a winner among a token's readings.
        """
        ...

    def stopwords(self) -> frozenset[str]:
        """The resource's stop list. A property of the language, so the resource owns it — but the
        reduction reads it through here so a fixture can declare its own twenty. Subordinate to
        lexicon membership: see the module head."""
        ...

    def is_name_only(self, word: str) -> bool:
        """True when every reading the resource has for this spelling is a NAME — a proper noun, a
        named instance, an acronym, a chemical symbol — and none of them is a word of the language.

        On the provider and not in here because it is a fact about the RESOURCE, not a rule the
        reduction could compute: only the lexical source knows that its `or` is Oregon's `OR` and
        its `me` is Maine's `ME`. What the reduction does with the answer is refuse the reading (see
        `analyses_of`); a fixture with no names in it answers False to everything and nothing about
        its behaviour changes.
        """
        ...


# ------------------------------------------------------------------------------------------------
# the reduction — a definition rewritten using only lexicon words
# ------------------------------------------------------------------------------------------------


def tokens_of(text: str) -> list[str]:
    """Lower-cased words, in the order the gloss says them. Order is kept even though the caller
    takes a set: a later reader (the miner, the curator) needs to quote the token that spoke."""
    return [t for t in TOKEN.findall(text.lower()) if len(t) >= MIN_TOKEN_LENGTH]


def analyses_of(token: str, provider: GlossProvider) -> tuple[str, ...]:
    """Every word a surface token could be naming: itself, then its base form under each POS —
    minus the readings that are not words at all.

    The token itself is included because a word that IS in the lexicon means itself — and because a
    lexicon may hold words the resource has no morphology for at all. It is included, not preferred:
    the whole of requirement 21's repair is that this function returns a SET of readings and no
    caller is allowed to stop at the first one.

    THE NAME REFUSAL (the Captain's option C, 2026-08-25) is applied here, on the readings, and not
    only at membership. Membership is the caller's — the lexicon is an argument, and a caller may
    hand in `or` or `me` from somewhere other than `wordnet_lexicon()` (the Jurassic 2925 holds both
    as function words). If the refusal lived only in the word list, a lemma path would walk `ate`
    back to Ate the Greek goddess and put her on a row. So the reading is refused where the reading
    is produced, and a token whose every reading is a name names nothing.

    Morphology itself is untouched: `provider.lemma` still answers `ate -> eat`, and `eat` is a word
    and survives. The refusal is about what a spelling MEANS, never about how it inflects.
    """
    out = [token]
    for pos in keys.POS_ORDER:
        lemma = provider.lemma(token, pos)
        if lemma and lemma not in out:
            out.append(lemma)
    return tuple(word for word in out if not provider.is_name_only(word))


def lexicon_words_in(
    text: str,
    lexicon: frozenset[str],
    provider: GlossProvider,
    stopwords: frozenset[str] | None = None,
) -> set[str]:
    """Every lexicon word a gloss names — the token itself if it is one, and every base form it
    could be under any part of speech.

    Nothing is tried FIRST. «as when one has left» names `leave` (the gloss is about leaving) and
    `left` (a lexicon word in its own right, and WordNet's own «leftover» adjective is spelled
    exactly so). Both readings are honest, no tagger lives at this layer, and the layer that CAN
    settle which one a gloss meant is the geometry that this mining feeds.

    The stop list is consulted only for tokens the lexicon does not contain (the Captain's ruling,
    2026-08-25 — see the module head).
    """
    stops = provider.stopwords() if stopwords is None else stopwords
    out: set[str] = set()
    for token in tokens_of(text):
        if token not in lexicon and token in stops:
            continue
        out |= {word for word in analyses_of(token, provider) if word in lexicon}
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

    The target IS a dimension, so it plays the part membership plays in `lexicon_words_in`: a token
    spelled like the target is never dropped as a stop word, and every other token still is.
    """
    target = keys.normalize_word(target)
    stops = provider.stopwords()
    for token in tokens_of(text):
        if token != target and token in stops:
            continue
        if target in analyses_of(token, provider):
            return token
    return None


def dimension_parts_of_speech(word: str, provider: GlossProvider) -> tuple[str, ...]:
    """The parts of speech that may mint a DIMENSION for a word: the ones it is a base form of.

    Requirement 21 enforced where keys are minted, through the protocol alone. `parts_of_speech` is
    a contract on the provider (read its docstring), and a contract nothing checks is a comment — so
    this asks the resource the same question a second way, per POS: read as this part of speech, is
    the word its own lemma? `used` read as a verb is `use`, so `used.v` is never built; `left` read
    as a verb is `leave`, so `left.v` is never built. Both were duplicate dimensions of a word that
    already had one.
    """
    return tuple(p for p in provider.parts_of_speech(word) if provider.lemma(word, p) == word)


def dimensions_of(words, provider: GlossProvider) -> list[str]:
    """THE dimension order for a word set — `keys.key_space` fed through the base-form rule.

    The call site the build tool wants: membership arrives as words (the closure decided them), and
    this is the one place they become the axes of R and D.
    """
    return keys.key_space(words, lambda word: dimension_parts_of_speech(word, provider))
