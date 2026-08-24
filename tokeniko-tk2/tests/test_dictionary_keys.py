"""The key convention: dimensions are base keys, senses ride on them, and truncation is sound."""

import pytest

from tests.lexicon_fixture import PARTS_OF_SPEECH, LEXICON
from tk2.dictionary import keys


# ------------------------------------------------------------------------------------------------
# base keys — the dimensions
# ------------------------------------------------------------------------------------------------


def test_the_pos_alphabet_is_closed():
    """Four parts of speech and no fifth. A new one would be a new kind of dimension, and the base
    only stays comparable across builds because the alphabet does not grow quietly."""
    assert keys.POS_ORDER == ("n", "v", "a", "r")
    assert keys.VALID_POS == {"n", "v", "a", "r"}


def test_the_satellite_adjective_is_an_adjective():
    """WordNet's `s`. A separate dimension for it would split `hungry` from `famished` on a
    distinction the lexicographer made about the synset, not about the word."""
    assert keys.normalize_pos("s") == "a"
    assert keys.key_of("hungry", "s") == "hungry.a"


def test_key_of_and_split_key_are_inverses():
    assert keys.key_of("eat", "v") == "eat.v"
    assert keys.split_key("eat.v") == ("eat", "v")


def test_a_word_may_contain_a_dot():
    """`u.s.` is a lemma. The splitter validates the SUFFIX against the POS alphabet rather than
    trusting the first separator it meets, so a dotted word survives the round trip."""
    assert keys.split_key(keys.key_of("u.s.", "n")) == ("u.s.", "n")
    assert keys.is_base_key("u.s.") is False


def test_multiword_lemmas_take_wordnets_underscore():
    assert keys.key_of("take in", "v") == "take_in.v"


@pytest.mark.parametrize("bad", ["eat", "", "eat.", "eat.x", "eat.v.01"])
def test_split_key_refuses_what_is_not_a_base_key(bad):
    """A sense key is refused too, and on purpose: it is a different kind of thing, and a splitter
    that quietly accepted both would let a sense become a dimension."""
    with pytest.raises(keys.InvalidKey):
        keys.split_key(bad)


def test_an_unknown_pos_is_refused_loudly():
    """Raised, never returned. A bad POS that quietly minted a new dimension is the silent no-op
    this project keeps refusing to repeat."""
    with pytest.raises(keys.InvalidKey):
        keys.key_of("eat", "x")


# ------------------------------------------------------------------------------------------------
# the dimension list
# ------------------------------------------------------------------------------------------------


def test_keys_for_word_follows_the_pos_order():
    """`left` occupies four dimensions, in WordNet's order — not the order the resource listed them."""
    assert keys.keys_for_word("left", ("a", "r", "n", "v")) == ["left.n", "left.v", "left.a", "left.r"]


def test_a_single_pos_word_costs_exactly_one_dimension():
    """The x1.70 measurement's promise: the split is data-driven, so a word with one POS pays once."""
    assert keys.keys_for_word("furniture", ("n",)) == ["furniture.n"]


def test_the_satellite_collapses_instead_of_doubling():
    assert keys.keys_for_word("hungry", ("a", "s")) == ["hungry.a"]


def test_key_space_is_a_function_of_the_word_set_alone():
    """Rebuild it tomorrow from the same words in another order and every index lands where it was.
    Nothing about a position may encode where its word came from."""
    pos_of = lambda w: PARTS_OF_SPEECH[w]  # noqa: E731
    forward = keys.key_space(LEXICON, pos_of)
    backward = keys.key_space(tuple(reversed(LEXICON)), pos_of)
    assert forward == backward
    assert forward[:3] == ["bed.n", "direction.n", "furniture.n"]
    assert len(forward) == sum(len(PARTS_OF_SPEECH[w]) for w in LEXICON)


def test_key_space_deduplicates_words():
    pos_of = lambda w: ("n", "v")  # noqa: E731
    assert keys.key_space(["land", "land", "LAND"], pos_of) == ["land.n", "land.v"]


# ------------------------------------------------------------------------------------------------
# sense keys — the dictionary layer riding on the base
# ------------------------------------------------------------------------------------------------


def test_sense_keys_are_word_anchored_and_numbered_from_one():
    assert keys.sense_key("eat", "v", 1) == "eat.v.01"
    assert keys.split_sense_key("eat.v.01") == ("eat", "v", 1)


def test_a_sense_key_truncates_to_its_dimension():
    """THE operation the ride-on-the-base architecture performs: a sense has no row of its own in R,
    it reads the row of its base key. Word-anchoring exists so that this is sound."""
    assert keys.base_of("left.a.01") == "left.a"
    assert keys.base_of("left.a") == "left.a"


def test_sense_numbers_are_not_zero_based():
    with pytest.raises(keys.InvalidKey):
        keys.sense_key("eat", "v", 0)


def test_the_two_kinds_of_key_never_answer_for_each_other():
    assert keys.is_base_key("eat.v") and not keys.is_sense_key("eat.v")
    assert keys.is_sense_key("eat.v.01") and not keys.is_base_key("eat.v.01")
