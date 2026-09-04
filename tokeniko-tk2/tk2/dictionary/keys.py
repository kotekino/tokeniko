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

WHAT LEFT THIS MODULE AT T3, and what did not. The GRAMMAR stays — a key is a word plus a part of
speech, sense keys are word-anchored, the numbering is ours. WHICH parts of speech exist is
WordNet's answer rather than the grammar (the Captain's ruling of 2026-08-25, test 2 of the standing
law), so it is declared in `dictionary_policy` from policy v3 and read back into the `Alphabet`
below. The constant that remains is what this code was COMPILED against, and `assert_compiled` is
what keeps the two from disagreeing in silence.
"""

from dataclasses import dataclass

# ------------------------------------------------------------------------------------------------
# the alphabet — WHICH parts of speech exist, which is not the same statement as the key grammar
# ------------------------------------------------------------------------------------------------

SEPARATOR = "."


class InvalidKey(ValueError):
    """A key that does not obey the convention. Raised, never returned: the tk1 trap this project
    keeps refusing to repeat is the silent no-op, and a bad key that quietly becomes a new dimension
    is exactly that failure wearing a lexicographer's hat."""


class AlphabetMismatch(InvalidKey):
    """The declared alphabet and the one this module was compiled against disagree.

    Not recoverable at run time and not meant to be: the fix is a code change under the Captain's
    hand, landing in the same breath as the migration that moved the rows. Raised at the seam where
    a policy becomes a config, so the refusal happens before a build measures anything.
    """


@dataclass(frozen=True, slots=True)
class Alphabet:
    """The parts of speech a key may name, in the order a multi-POS word's keys are listed.

    A SEPARATE THING FROM THE GRAMMAR, and the standing law of 2026-08-25 is what separates them:
    that a key IS a word plus a part of speech is FRAME (change it and every row, key and operation
    changes shape); WHICH parts of speech exist is WordNet's answer about English, and evidence
    could revise it — a resource that split adjectives from participles, or a language with a
    class English has not got. So the alphabet is CURATION and its declaration is rows
    (`dictionary_policy`, kind `pos`, since policy v3); this is the shape those rows are read into.

    `aliases` is the resource's own spelling variance mapped onto the alphabet — WordNet's satellite
    adjective `s` is an adjective, and a separate `s` dimension would split `hungry` from `famished`
    on a distinction the lexicographer made about the SYNSET rather than about the word.
    """

    #: The letters, in the order dimensions are listed in. The dimension order is a function of the
    #: word set alone, so a rebuild lands every index where it was.
    order: tuple[str, ...]
    #: `(letter, long name)`, for the probes that print a POS to a reader.
    names: tuple[tuple[str, str], ...] = ()
    #: `(spelling, letter)` — a reading the resource writes differently and the alphabet folds in.
    aliases: tuple[tuple[str, str], ...] = ()

    def __post_init__(self):
        if not self.order:
            raise InvalidKey("an alphabet with no parts of speech can name no dimension")
        if len(set(self.order)) != len(self.order):
            raise InvalidKey(f"the alphabet repeats a part of speech: {self.order}")
        for spelling, letter in self.aliases:
            if letter not in self.order:
                raise InvalidKey(f"alias {spelling!r} points at {letter!r}, which is not in {self.order}")
            if spelling in self.order:
                raise InvalidKey(f"{spelling!r} is both a part of speech and an alias for one")

    def __contains__(self, pos: str) -> bool:
        return pos in self.order

    def index(self, pos: str) -> int:
        """Where this part of speech sorts. Raises rather than answering -1: an unknown POS is a
        defect, and a sort that quietly put it first would hide it in a dimension order."""
        try:
            return self.order.index(pos)
        except ValueError:
            raise InvalidKey(f"unknown part of speech {pos!r} — the alphabet is {self.order}") from None

    def normalize(self, pos: str) -> str:
        """The one place an alias becomes its letter. Every reader of a resource's POS goes here."""
        if not pos:
            raise InvalidKey("empty part of speech")
        p = pos.lower()
        p = dict(self.aliases).get(p, p)
        if p not in self.order:
            raise InvalidKey(f"unknown part of speech {pos!r} — the alphabet is {self.order}")
        return p

    def as_dict(self) -> dict:
        """The canonical form the policy fingerprint takes the alphabet over."""
        return {
            "order": list(self.order),
            "names": [list(pair) for pair in self.names],
            "aliases": [list(pair) for pair in self.aliases],
        }


#: THE ALPHABET THE KEY GRAMMAR IS COMPILED AGAINST — and deliberately not a second declaration of
#: it. The declaration is the rows; this is what the code in this module was written to handle, and
#: `assert_compiled` below is what makes the two agree out loud instead of by assumption.
#:
#: Why a constant survives the move at all: `db/0003` and `db/0005` construct a `DictionaryConfig`
#: and a `WordNetProvider` with no alphabet in sight, and an applied migration is IMMUTABLE — the
#: database already holds what that file did. Threading the alphabet through every key function
#: would therefore have needed a default here anyway, and a default is the quieter declaration of
#: the two. So the rows are made load-bearing by a REFUSAL rather than by a parameter: a policy that
#: declares a different alphabet does not silently build a base under this one, it stops.
GRAMMAR_ALPHABET = Alphabet(
    order=("n", "v", "a", "r"),
    names=(("n", "noun"), ("v", "verb"), ("a", "adjective"), ("r", "adverb")),
    aliases=(("s", "a"),),
)

POS_ORDER = GRAMMAR_ALPHABET.order
VALID_POS = frozenset(POS_ORDER)
POS_NAMES = dict(GRAMMAR_ALPHABET.names)

# WordNet's satellite adjective, named because the adapter and the tests both speak about it.
SATELLITE_POS = "s"


def assert_compiled(alphabet: Alphabet) -> None:
    """Refuse an alphabet the key grammar was not built for. See `GRAMMAR_ALPHABET`."""
    if alphabet != GRAMMAR_ALPHABET:
        raise AlphabetMismatch(
            f"the policy declares the alphabet {alphabet.as_dict()}, and the key convention was "
            f"compiled against {GRAMMAR_ALPHABET.as_dict()}. A build under rows this module cannot "
            f"honour would mint keys nobody declared: move `keys.GRAMMAR_ALPHABET` in the same "
            f"breath as the migration that moved the rows."
        )


# ------------------------------------------------------------------------------------------------
# base keys — the dimensions
# ------------------------------------------------------------------------------------------------


def normalize_pos(pos: str) -> str:
    """The one place `s` becomes `a`. Every reader of a resource's POS goes through here."""
    return GRAMMAR_ALPHABET.normalize(pos)


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
