"""THE KEY CONVENTION — one module, one truth about what names a dimension.

Two levels, and the whole architecture rests on the difference:

  - the BASE KEY `eat.v` — a DIMENSION. The square matrices R and D exist over these and only
    these: the POS-split base lexicon, thousands of keys. Requirement 9, PROVEN: a collapsed
    dimension merges two different relation sets, because `cause` the noun and `cause` the verb do
    not have the same neighbours (measured cost of the split: x1.70).
  - the SENSE KEY `eat.v.01` — a SENSE, which is not a dimension. The full dictionary (~197k senses)
    rides ON the base: a sense carries a D-vector over base dims and consults R through its base key
    (tkzip req. 11). There is never a senses x senses matrix; the sense key exists so a sense stays
    distinguishable in the dictionary layer (tkzip req. 9 — a wrong verb sense is a wrong action).

The sense key is deliberately WORD-ANCHORED rather than WordNet's own synset name: `left.a.01`
truncates to the base key `left.a`, which is the operation the whole ride-on-the-base design
performs constantly, while WordNet's synset name is anchored on whichever lemma happens to head the
synset (`devour`'s sense is `devour.v.01`, whose prefix is not `devour`... but for many words it is
another word entirely). Truncation must be sound; therefore the convention owns the numbering, and
the resource's own name is kept BESIDE the key as provenance, never as the key.

The POS split is not a switch. The prototype carried a `SPLIT_BY_POS` flag because it was measuring
whether the split was worth its cost; requirement 9 answered that, so here the split is the law and
there is no un-split key to construct.

One hazard, recorded where the convention lives: KEYS CONTAIN DOTS. A key must therefore never be
used as a Mongo field path — `{"$set": {f"edges.{key}": ...}}` silently writes a NESTED document
(`edges.sleep.v`) instead of the cell you meant. The review caught this live; store cells in a way
that treats the key as a VALUE (a subdocument list, or the whole map replaced at once).
"""

# ------------------------------------------------------------------------------------------------
# the alphabet
# ------------------------------------------------------------------------------------------------

# In WordNet's own order, which is also the order a multi-POS word's keys are listed in — so the
# dimension order is a function of the word set alone and a rebuild lands the indices in the same
# places.
POS_ORDER = ("n", "v", "a", "r")
VALID_POS = frozenset(POS_ORDER)

POS_NAMES = {"n": "noun", "v": "verb", "a": "adjective", "r": "adverb"}

SEPARATOR = "."

# WordNet's satellite adjective. It is an adjective — a separate `s` dimension would split `hungry`
# from `famished` on a distinction the lexicographer made about the synset, not about the word.
SATELLITE_POS = "s"


class InvalidKey(ValueError):
    """A key that does not obey the convention. Raised, never returned: the tk1 trap this project
    keeps refusing to repeat is the silent no-op, and a bad key that quietly becomes a new dimension
    is exactly that failure wearing a lexicographer's hat."""


# ------------------------------------------------------------------------------------------------
# base keys — the dimensions
# ------------------------------------------------------------------------------------------------


def normalize_pos(pos: str) -> str:
    """The one place `s` becomes `a`. Every reader of a resource's POS goes through here."""
    if not pos:
        raise InvalidKey("empty part of speech")
    p = pos.lower()
    if p == SATELLITE_POS:
        p = "a"
    if p not in VALID_POS:
        raise InvalidKey(f"unknown part of speech {pos!r} — the alphabet is {POS_ORDER}")
    return p


def normalize_word(word: str) -> str:
    """Lower-cased, stripped, spaces as underscores — WordNet's own multiword form (`take_in`).

    A word may itself contain a dot (`u.s.`), which is why `split_key` validates the SUFFIX against
    the POS alphabet instead of trusting the first separator it finds.
    """
    if word is None:
        raise InvalidKey("no word")
    w = word.strip().lower().replace(" ", "_")
    if not w:
        raise InvalidKey("empty word")
    return w


def key_of(word: str, pos: str) -> str:
    """`eat`, `v` -> `eat.v`."""
    return f"{normalize_word(word)}{SEPARATOR}{normalize_pos(pos)}"


def split_key(key: str) -> tuple[str, str]:
    """`eat.v` -> (`eat`, `v`). Raises on anything that is not a base key — including a sense key,
    which is a different kind of thing and has its own splitter."""
    word, pos = _rsplit_pos(key)
    if pos is None:
        raise InvalidKey(f"not a base key: {key!r} (expected word{SEPARATOR}pos)")
    return word, pos


def word_of(key: str) -> str:
    return split_key(key)[0]


def pos_of(key: str) -> str:
    return split_key(key)[1]


def is_base_key(key: str) -> bool:
    """A predicate, for the places that must sort keys from words without an exception flying."""
    try:
        split_key(key)
        return True
    except InvalidKey:
        return False


def keys_for_word(word: str, parts_of_speech) -> list[str]:
    """Every dimension one word occupies, in POS order.

    The POS list is DATA — it comes from the lexical resource, so a single-POS word costs exactly
    one dimension, as the x1.70 measurement promised. Duplicates (a resource that reports `a` and
    `s` separately) collapse here rather than in each caller.
    """
    seen: list[str] = []
    for pos in parts_of_speech:
        p = normalize_pos(pos)
        if p not in seen:
            seen.append(p)
    return [key_of(word, p) for p in sorted(seen, key=POS_ORDER.index)]


def key_space(words, parts_of_speech_of) -> list[str]:
    """THE dimension order, from a word set alone: words sorted, then POS in WordNet order.

    Deterministic by construction — rebuild it tomorrow from the same words and every index lands
    where it was. Nothing about a dimension's position may encode where its word came from (the
    prototype interleaved its repaired words alphabetically for exactly this reason).
    """
    return [k for w in sorted({normalize_word(w) for w in words}) for k in keys_for_word(w, parts_of_speech_of(w))]


# ------------------------------------------------------------------------------------------------
# sense keys — the dictionary layer, riding on the base
# ------------------------------------------------------------------------------------------------

# The width of the sense number. Two digits is WordNet's own convention (`eat.v.01`) and it keeps a
# sense key sorting in sense order as a string.
SENSE_DIGITS = 2


def sense_key(word: str, pos: str, number: int) -> str:
    """`eat`, `v`, 1 -> `eat.v.01`. The number is the sense's rank among THIS word's senses of THIS
    POS, 1-based — the resource's frequency order, which is the order a reader means by "the first
    sense of eat"."""
    if number < 1:
        raise InvalidKey(f"sense numbers are 1-based, got {number}")
    return f"{key_of(word, pos)}{SEPARATOR}{number:0{SENSE_DIGITS}d}"


def split_sense_key(key: str) -> tuple[str, str, int]:
    """`eat.v.01` -> (`eat`, `v`, 1)."""
    head, _, tail = key.rpartition(SEPARATOR)
    if not head or not tail.isdigit():
        raise InvalidKey(f"not a sense key: {key!r} (expected word{SEPARATOR}pos{SEPARATOR}NN)")
    word, pos = split_key(head)
    number = int(tail)
    if number < 1:
        raise InvalidKey(f"sense numbers are 1-based, got {number} in {key!r}")
    return word, pos, number


def base_of(key: str) -> str:
    """The dimension a key consults. A base key is its own base; a sense key truncates to one.

    This is THE operation the ride-on-the-base architecture performs: a sense has no row of its own
    in R, it reads the row of its base key.
    """
    if is_base_key(key):
        return key
    word, pos, _number = split_sense_key(key)
    return key_of(word, pos)


def is_sense_key(key: str) -> bool:
    try:
        split_sense_key(key)
        return True
    except InvalidKey:
        return False


# ------------------------------------------------------------------------------------------------


def _rsplit_pos(key: str) -> tuple[str, str | None]:
    """Split on the LAST separator and accept it only if what follows is a POS. `u.s.a.` has no POS
    suffix and comes back whole; `u.s.a..n` splits where it should."""
    if not key:
        raise InvalidKey("empty key")
    word, sep, tail = key.rpartition(SEPARATOR)
    if not sep or tail not in VALID_POS:
        return key, None
    return word, tail
