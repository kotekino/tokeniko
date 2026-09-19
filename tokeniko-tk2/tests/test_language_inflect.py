"""THE SPELLING RULE AND ITS ROSTER — requirement 9's smallest piece, and a measured one.

The rule is frame and the exceptions are rows, and the test that matters is the one that keeps that
split honest: every row in the roster must be a word the rule ACTUALLY gets wrong, checked against
the rule as the code states it. A roster that drifts from its rule is two sources of truth.
"""

import pytest

from tk2.language.inflect import PRESENT, Inflections, present_tense_rule, standing_inflections


@pytest.mark.parametrize("lemma, expected", [
    ("think", "thinks"), ("walk", "walks"), ("exist", "exists"),    # the plain case
    ("watch", "watches"), ("push", "pushes"), ("fix", "fixes"),     # a sibilant takes -es
    ("kiss", "kisses"), ("buzz", "buzzes"),
    ("marry", "marries"), ("carry", "carries"),                     # consonant + y -> -ies
    ("play", "plays"), ("buy", "buys"),                             # vowel + y keeps the y
    ("demo", "demos"), ("solo", "solos"),                           # -o takes the MAJORITY side
])
def test_the_rule_is_orthography_and_needs_no_table(lemma, expected):
    assert present_tense_rule(lemma) == expected


def test_the_rule_says_nothing_about_an_empty_word():
    assert present_tense_rule("") == "" and present_tense_rule(None) == ""


@pytest.mark.parametrize("lemma, expected", [
    ("be", "is"), ("have", "has"),                  # the two true irregulars
    ("go", "goes"), ("do", "does"), ("echo", "echoes"), ("veto", "vetoes"),
    ("quiz", "quizzes"), ("whir", "whirrs"),        # a doubled consonant
    ("stomach", "stomachs"),                        # the `ch` is a /k/
])
def test_the_roster_carries_what_the_rule_gets_wrong(lemma, expected):
    """`db/0022`, measured over all 20,364 verb lemmas WordNet holds: the rule is right for every one
    but 21, and those 21 are here. A 0.1% exception roster is what makes it a rule rather than a
    lookup table wearing a rule's clothes."""
    standing = standing_inflections()
    assert standing.of(lemma, PRESENT) == expected
    assert present_tense_rule(lemma) != expected, "a row that agrees with the rule is not an exception"


def test_a_verb_nobody_listed_is_REGULAR_and_not_unknown():
    """There is no abstention here and there should not be. The measurement is what licenses that:
    a verb the roster never heard of is not an unknown word, it is a regular one. The place that
    abstains is the decompiler, and it abstains about MEANINGS, not about spellings."""
    standing = standing_inflections()
    assert standing.of("zzzqm") == "zzzqms"
    assert standing.of("defenestrate") == "defenestrates"


def test_a_tag_the_roster_does_not_hold_yet_leaves_the_word_alone():
    """`VBD` and `VBN` arrive when the theatre is read. Until then the decompiler renders the
    present, and a past tense it cannot place is a tense it must not speak."""
    standing = standing_inflections()
    assert standing.of("walk", "VBD") == "walk", "no past is invented"


def test_the_roster_is_read_from_the_newest_version_only():
    rows = [
        {"version": 1, "lemma": "go", "tag": PRESENT, "form": "goeth"},
        {"version": 2, "lemma": "go", "tag": PRESENT, "form": "goes"},
    ]
    assert Inflections.from_rows(rows).of("go") == "goes"
