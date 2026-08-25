"""THE WORDNET ADAPTER — the real gloss provider, and the only file in tk2 that imports nltk.

Everything else in `tk2.dictionary` is pure: policy, graph algorithms, key convention. This is where
a resource with opinions gets wrapped so those opinions arrive through one door — WordNet's satellite
adjectives, its morphological exceptions, its stop list, its sense order.

THE LEXICON IS INJECTED. It is not WordNet's business which words the base is made of: the Jurassic
2925 is data that crosses into tk2 by migration (the inheritance ledger), a full-lexicon build is a
declared derivation, and either way the word set is an argument the caller must be able to state.
`wordnet_lexicon()` below produces the at-scale one, and it is a helper, not a default — a provider
that silently defaulted to «all of WordNet» would be a provider that decides the base by omission.

nltk is imported at module scope on purpose: importing this module IS the declaration that you want
the real resource. `tk2.dictionary.__init__` does not import it, so the engine keeps running (and
keeps being tested) on a fixture with no nltk installed at all.
"""

from functools import lru_cache

import nltk
from nltk.corpus import stopwords as nltk_stopwords
from nltk.corpus import wordnet as wn

from tk2.dictionary import keys

# The corpora this adapter reads. Named so a missing one produces a sentence an operator can act on
# rather than nltk's own LookupError, which is forty lines of ASCII art.
REQUIRED_CORPORA = ("wordnet", "omw-1.4", "stopwords")

# No morphy ORDER lives here any more, and it is worth saying why rather than leaving the absence to
# be re-filled. The prototype had one (verbs first) because the miner took the first lemma that was
# a lexicon word and stopped, so the order decided which reading became the base. Since requirement
# 21's repair nothing picks a winner among a token's readings: the reduction walks the whole POS
# alphabet (`keys.POS_ORDER`) and keeps them all.

# A cache sentinel: `lemma()` answers None for «not that part of speech at all», which is a real
# answer and has to be cacheable as one.
_UNCACHED = object()


class CorpusMissing(RuntimeError):
    """A corpus nltk does not have locally. Raised loudly instead of downloading: a build that
    reaches the network mid-run is a build whose inputs nobody pinned."""


def ensure_corpora(download: bool = False) -> None:
    """Check the corpora are USABLE. `download=True` is the operator's explicit hand, never the
    library's own initiative — the prototype downloaded at import, which is convenient exactly once
    and unreproducible every time after.

    The check reads the corpus rather than looking for its directory. `nltk.data.find` reports
    `corpora/wordnet` missing on a machine where WordNet answers perfectly well, because nltk ships
    it as a zip and resolves it elsewhere — a control that does not contain the thing at risk.
    """
    probes = (
        ("wordnet", lambda: wn.morphy("dogs", "n")),
        ("stopwords", lambda: nltk_stopwords.words("english")),
    )
    for corpus, probe in probes:
        try:
            probe()
        except LookupError:
            if download:
                nltk.download(corpus, quiet=True)
                probe()
                continue
            raise CorpusMissing(
                f"nltk cannot read the {corpus!r} corpus. "
                f"Install the set with: python -m nltk.downloader {' '.join(REQUIRED_CORPORA)}"
            ) from None


# ------------------------------------------------------------------------------------------------
# the provider
# ------------------------------------------------------------------------------------------------


class WordNetProvider:
    """WordNet, wearing the `GlossProvider` shape.

    Memoised per instance because the closure walks every gloss at least once and the matrix
    builders will walk them again; WordNet's own lookups are not free at lexicon scale.
    """

    def __init__(self, lexicon, download: bool = False):
        ensure_corpora(download=download)
        self._lexicon = tuple(dict.fromkeys(keys.normalize_word(w) for w in lexicon))
        self._gloss_cache: dict[tuple[str, str], str] = {}
        self._pos_cache: dict[str, tuple[str, ...]] = {}
        self._lemma_cache: dict[tuple[str, str], str | None] = {}
        self._synset_cache: dict[str, tuple] = {}
        self._stopwords = frozenset(nltk_stopwords.words("english"))

    # -- the protocol ----------------------------------------------------------------------------

    def lexicon(self) -> tuple[str, ...]:
        return self._lexicon

    def gloss(self, word: str, senses: str = "primary") -> str:
        cached = self._gloss_cache.get((word, senses))
        if cached is None:
            # Definitions only. An example sentence is usage, and usage is co-occurrence wearing a
            # definition's clothes — D's job, never the definition digraph's.
            cached = " ; ".join(s.definition() for s in self.synsets(word, senses))
            self._gloss_cache[(word, senses)] = cached
        return cached

    def parts_of_speech(self, word: str) -> tuple[str, ...]:
        """The POS the word is a BASE FORM of — read off `lemma_synsets`, so it can never disagree
        with the senses this provider is willing to speak about."""
        cached = self._pos_cache.get(word)
        if cached is None:
            found: list[str] = []
            for synset in self.lemma_synsets(word):
                pos = keys.normalize_pos(synset.pos())
                if pos not in found:
                    found.append(pos)
            cached = tuple(sorted(found, key=keys.POS_ORDER.index))
            self._pos_cache[word] = cached
        return cached

    def lemma(self, token: str, pos: str) -> str | None:
        """morphy, one part of speech at a time — `left` read as a verb is `leave`, read as a noun
        it is `left`, and requirement 21 is about the difference."""
        pos = keys.normalize_pos(pos)
        cached = self._lemma_cache.get((token, pos), _UNCACHED)
        if cached is _UNCACHED:
            cached = wn.morphy(token, pos)
            self._lemma_cache[(token, pos)] = cached
        return cached

    def lemmas(self, token: str) -> tuple[str, ...]:
        """Every base form morphy reaches, over the POS alphabet, deduplicated. Not a ranking: the
        reduction takes them all."""
        found: list[str] = []
        for pos in keys.POS_ORDER:
            lemma = self.lemma(token, pos)
            if lemma and lemma not in found:
                found.append(lemma)
        return tuple(found)

    def stopwords(self) -> frozenset[str]:
        return self._stopwords

    # -- beyond the protocol: what the dictionary layer will need --------------------------------

    def lemma_synsets(self, word: str) -> tuple:
        """The synsets the word is a LEMMA of — never the ones it only reaches by inflection.

        `wn.synsets` runs morphy for you, so it answers `used` with all six of `use`'s verb senses
        and `left` with all nineteen of `leave`'s. Convenient for a search box, ruinous for a
        dimension: those senses are another word's key, and mining them here is exactly how `used.v`
        and `left.v` were minted — duplicate dimensions of `use.v` and `leave.v` (requirement 21).

        The test is lemma membership rather than `morphy(word, pos) == word` because it asks the
        resource the question directly: does this synset actually contain this word? It also keeps
        `left`'s honest adjective sense — WordNet's `leftover.s.01` lists `left` among its lemmas,
        which is «something left over» being an adjective all along.
        """
        cached = self._synset_cache.get(word)
        if cached is None:
            cached = tuple(s for s in wn.synsets(word) if word in _lemma_names(s))
            self._synset_cache[word] = cached
        return cached

    def synsets(self, word: str, senses: str = "primary"):
        """The senses that speak for a word. `primary` = the first synset per POS, which is exactly
        what the Jurassic build used; `all` = the full sense list, denser and noisier."""
        found = self.lemma_synsets(word)
        if senses == "all":
            return found
        seen, keep = set(), []
        for synset in found:
            pos = keys.normalize_pos(synset.pos())
            if pos not in seen:
                keep.append(synset)
                seen.add(pos)
        return keep

    def synsets_of_key(self, key: str, senses: str = "primary"):
        """The senses behind ONE dimension — `land.v` asks WordNet only about the verb."""
        word, pos = keys.split_key(key)
        found = [s for s in self.lemma_synsets(word) if keys.normalize_pos(s.pos()) == pos]
        return found[:1] if senses == "primary" and found else found

    def sense_keys(self, word: str) -> list[dict]:
        """Every sense of a word under the tk2 sense-key convention, with WordNet's own name kept
        beside it as PROVENANCE.

        The key is word-anchored (`left.a.01`) so it truncates to its base key; WordNet's synset name
        is anchored on whichever lemma heads the synset and does not truncate soundly. Both are
        recorded: the key is what the geometry uses, the synset name is what makes a build auditable
        against the resource it was built from — and what a WordNet version bump would be diffed on.
        """
        out: list[dict] = []
        counters: dict[str, int] = {}
        for synset in self.lemma_synsets(word):
            pos = keys.normalize_pos(synset.pos())
            counters[pos] = counters.get(pos, 0) + 1
            out.append(
                {
                    "key": keys.sense_key(word, pos, counters[pos]),
                    "base": keys.key_of(word, pos),
                    "synset": synset.name(),
                    "definition": synset.definition(),
                }
            )
        return out


def _lemma_names(synset) -> frozenset[str]:
    """A synset's lemmas as the key convention spells them — lower case, underscores for spaces,
    which is WordNet's own multiword form."""
    return frozenset(lemma.name().lower() for lemma in synset.lemmas())


# ------------------------------------------------------------------------------------------------
# the at-scale lexicon
# ------------------------------------------------------------------------------------------------


@lru_cache(maxsize=4)
def wordnet_lexicon(min_length: int = 2, multiword: bool = False) -> tuple[str, ...]:
    """Every lemma WordNet knows, sorted — the candidate lexicon for a full-base build.

    Multiword lemmas (`take_in`, `united_states`) are OUT by default: a compound is the atom of the
    DERIVED space (requirement 6, layer two), and admitting them here would put layer two's atoms
    into layer one's dimensions before the layer exists to hold them.
    """
    ensure_corpora()
    found = set()
    for lemma in wn.all_lemma_names():
        if len(lemma) < min_length:
            continue
        if "_" in lemma and not multiword:
            continue
        found.add(lemma.lower())
    return tuple(sorted(found))
