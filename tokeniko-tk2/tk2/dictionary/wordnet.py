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

# The order morphy is tried in. Verbs first: a gloss is written in verbs and the inflected forms that
# need lemmatising are overwhelmingly verbal («takes in solid food»). The prototype's order, kept —
# it decides which lemma wins for an ambiguous surface form, so changing it changes the base.
MORPHY_ORDER = ("v", "n", "a", "r")


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
        self._lemma_cache: dict[str, tuple[str, ...]] = {}
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
        cached = self._pos_cache.get(word)
        if cached is None:
            found: list[str] = []
            for synset in wn.synsets(word):
                pos = keys.normalize_pos(synset.pos())
                if pos not in found:
                    found.append(pos)
            cached = tuple(sorted(found, key=keys.POS_ORDER.index))
            self._pos_cache[word] = cached
        return cached

    def lemmas(self, token: str) -> tuple[str, ...]:
        """The base forms morphy can reach, in `MORPHY_ORDER`, deduplicated.

        This is the surface of requirement 21. Today it answers per-token and the caller takes the
        first hit that is a lexicon word — which is how «something *left* over» reached `left` the
        direction instead of `leave`. The POS-aware repair lands here.
        """
        cached = self._lemma_cache.get(token)
        if cached is None:
            found: list[str] = []
            for pos in MORPHY_ORDER:
                lemma = wn.morphy(token, pos)
                if lemma and lemma not in found:
                    found.append(lemma)
            cached = tuple(found)
            self._lemma_cache[token] = cached
        return cached

    def stopwords(self) -> frozenset[str]:
        return self._stopwords

    # -- beyond the protocol: what the dictionary layer will need --------------------------------

    def synsets(self, word: str, senses: str = "primary"):
        """The senses that speak for a word. `primary` = the first synset per POS, which is exactly
        what the Jurassic build used; `all` = the full sense list, denser and noisier."""
        found = wn.synsets(word)
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
        found = [s for s in wn.synsets(word) if keys.normalize_pos(s.pos()) == pos]
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
        for synset in wn.synsets(word):
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
