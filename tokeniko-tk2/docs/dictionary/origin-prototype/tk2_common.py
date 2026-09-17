# tk2 / dictionary review — shared plumbing. No policy here; policy lives in tk2_config.py.

import os
import re
import sys
from functools import lru_cache

from pymongo import MongoClient

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import tk2_config as CFG

import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords

for pkg in ("stopwords", "wordnet", "omw-1.4"):
    nltk.download(pkg, quiet=True)

STOP = set(stopwords.words("english"))

# ------------------------------------------------------------------------------------------------
# mongo — the body is READ-ONLY here; every write is fenced into the tk2 sandbox
# ------------------------------------------------------------------------------------------------

_client = None


def client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(CFG.MONGO_URI, serverSelectionTimeoutMS=8000)
    return _client


def src_db():
    """The body's knowledge base. NEVER written to by anything in this directory."""
    return client()[CFG.SRC_DB]


def tk2_db():
    """The sandbox. The guard is deliberate: a typo in a config must not reach the biography."""
    name = CFG.TK2_DB
    if name in (CFG.SRC_DB, "tokeniko", "tokeniko_mem", "tokeniko_memory", "admin", "local", "config"):
        raise SystemExit(f"REFUSING to write: TK2_DB is set to '{name}', which is not a sandbox.")
    return client()[name]


# ------------------------------------------------------------------------------------------------
# the base
# ------------------------------------------------------------------------------------------------


@lru_cache(maxsize=1)
def base_words() -> list[str]:
    """The 2925, in index order."""
    rows = list(src_db().base.find({}, {"word": 1, "index": 1}).sort("index", 1))
    return [r["word"] for r in rows]


@lru_cache(maxsize=1)
def base_set() -> frozenset[str]:
    return frozenset(base_words())


@lru_cache(maxsize=1)
def base_index() -> dict[str, int]:
    rows = src_db().base.find({}, {"word": 1, "index": 1})
    return {r["word"]: r["index"] for r in rows}


def base_vector(word: str) -> list[float] | None:
    """The Jurassic row, for side-by-side comparison in stage 3."""
    row = src_db().base.find_one({"word": word}, {"vector": 1})
    return row["vector"] if row else None


# ------------------------------------------------------------------------------------------------
# definitions reduced to base words — stage 1's raw material
# ------------------------------------------------------------------------------------------------

_TOKEN = re.compile(r"\b[a-z][a-z-]*\b")


def _lemmas_in_base(text: str) -> set[str]:
    """Every base word named in a gloss. Tries the surface form, then WordNet morphy per POS —
    a gloss says «takes in solid food», and `takes` must land on `take`."""
    out: set[str] = set()
    bset = base_set()
    for tok in _TOKEN.findall(text.lower()):
        if len(tok) < 2 or tok in STOP:
            continue
        if tok in bset:
            out.add(tok)
            continue
        for pos in ("v", "n", "a", "r"):
            lem = wn.morphy(tok, pos)
            if lem and lem in bset:
                out.add(lem)
                break
    return out


def gloss_names_word(text: str, word: str) -> str | None:
    """`_lemmas_in_base`'s matching, aimed at ONE target word instead of the whole base set — returns
    the surface token that named it, or None. Needed by stage 4 because a curation target may be a
    dimension without being a Jurassic base word (`swallow`, `runway`), which `_lemmas_in_base`
    filters out by construction."""
    word = word.lower()
    for tok in _TOKEN.findall(text.lower()):
        if len(tok) < 2 or tok in STOP:
            continue
        if tok == word:
            return tok
        for pos in ("v", "n", "a", "r"):
            lem = wn.morphy(tok, pos)
            if lem == word:
                return tok
    return None


def synsets_for(word: str, mode: str | None = None):
    """The senses that speak for a base word. `primary` = first synset per POS, which is exactly
    what the Jurassic build used; `all` = the full sense list."""
    mode = mode or CFG.DEFINITION_SENSES
    all_syn = wn.synsets(word)
    if mode == "all":
        return all_syn
    seen, keep = set(), []
    for s in all_syn:
        if s.pos() not in seen:
            keep.append(s)
            seen.add(s.pos())
    return keep


def definition_of(word: str, mode: str | None = None) -> str:
    """The gloss text (definitions only — examples are NOT definition, they are usage)."""
    return " ; ".join(s.definition() for s in synsets_for(word, mode))


def definition_in_base(word: str, mode: str | None = None) -> set[str]:
    """The Captain's reduction: a definition rewritten using only base words. Self-reference dropped."""
    return _lemmas_in_base(definition_of(word, mode)) - {word}


# ------------------------------------------------------------------------------------------------
# POS-qualified keys — `eat.v`, `food.n`
# ------------------------------------------------------------------------------------------------

POS_ORDER = ("n", "v", "a", "r")


def normalize_pos(pos: str) -> str:
    """WordNet's satellite adjective `s` is an adjective."""
    return "a" if pos == "s" else pos


def key_of(word: str, pos: str) -> str:
    return f"{word}.{normalize_pos(pos)}" if CFG.SPLIT_BY_POS else word


def split_key(key: str) -> tuple[str, str | None]:
    if "." in key:
        w, p = key.rsplit(".", 1)
        if p in POS_ORDER:
            return w, p
    return key, None


def keys_for_word(word: str) -> list[str]:
    """Every POS this base word actually has in WordNet — the POS split is data-driven, so a
    single-POS word costs exactly one dimension, as promised."""
    if not CFG.SPLIT_BY_POS:
        return [word]
    poss = []
    for s in wn.synsets(word):
        p = normalize_pos(s.pos())
        if p not in poss:
            poss.append(p)
    return [f"{word}.{p}" for p in sorted(poss, key=POS_ORDER.index)]


def synsets_of_key(key: str, mode: str | None = None):
    word, pos = split_key(key)
    syns = synsets_for(word, mode) if pos is None else [
        s for s in wn.synsets(word) if normalize_pos(s.pos()) == pos
    ]
    if pos is not None and (mode or CFG.DEFINITION_SENSES) == "primary" and syns:
        syns = syns[:1]
    return syns


# ------------------------------------------------------------------------------------------------
# small helpers
# ------------------------------------------------------------------------------------------------


def cosine(a, b) -> float:
    import numpy as np

    va, vb = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    na, nb = np.linalg.norm(va), np.linalg.norm(vb)
    if na == 0 or nb == 0:
        return 0.0
    return float(va.dot(vb) / (na * nb))
