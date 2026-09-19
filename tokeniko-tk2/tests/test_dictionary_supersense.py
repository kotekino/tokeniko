"""THE SUPERSENSE — what kind of thing a word names, as WordNet's own lexicographer files state it.

The published inventory is the claim under test: 26 noun classes and 15 verb classes. If an nltk
upgrade moved either set, every rule in `db/0012` would be quantifying over a vocabulary that no
longer exists — and it would do so silently, because a rule that matches nothing simply falls
through to its default. So the inventory is checked against the corpus rather than trusted.
"""

import pytest

from nltk.corpus import wordnet as wn

from tk2.dictionary.supersense import (
    NOUN_SUPERSENSES,
    SUPERSENSES,
    VERB_SUPERSENSES,
    derived_supersense,
    supersense_for,
    supersense_of,
)


def test_the_published_inventory_is_the_one_the_corpus_has():
    assert sorted(NOUN_SUPERSENSES) == sorted({s.lexname() for s in wn.all_synsets("n")})
    assert sorted(VERB_SUPERSENSES) == sorted({s.lexname() for s in wn.all_synsets("v")})
    assert len(SUPERSENSES) == 41


@pytest.mark.parametrize("lemma, pos, expected", [
    ("noon", "n", "noun.time"), ("may", "n", "noun.time"), ("monday", "n", "noun.time"),
    ("friend", "n", "noun.person"), ("paris", "n", "noun.location"),
    ("knife", "n", "noun.artifact"), ("ink", "n", "noun.substance"),
    ("talk", "v", "verb.communication"), ("go", "v", "verb.motion"),
    ("give", "v", "verb.possession"),
])
def test_the_readings_the_marker_rules_depend_on(lemma, pos, expected):
    """These ten are not examples — they are the evidence `db/0012`'s rules fire on. A resource that
    stopped saying `noun.time` about noon would change what the station compiles."""
    assert supersense_of(lemma, pos) == expected


def test_it_reads_the_PRIMARY_sense_and_not_the_best_of_them_all():
    """`db/0006`'s rule, and here it is not a preference: taking the strongest of every sense was
    measured first and returns `pool` as a TIME (via `pool.n.08`) and `dog` as an INSTRUMENT. A
    word's eighth reading is a different word."""
    assert supersense_of("pool", "n") == "noun.artifact" == wn.synsets("pool", "n")[0].lexname()
    assert supersense_of("dog", "n") == "noun.animal"


def test_a_word_the_resource_does_not_hold_gets_None_and_not_a_guess():
    assert supersense_of("zzzqx", "n") is None
    assert supersense_of("", "n") is None


def test_a_ud_tag_reaches_the_right_half_of_the_resource():
    assert supersense_for("talk", "VERB") == "verb.communication"
    assert supersense_for("talk", "NOUN") == "noun.communication"
    assert supersense_for("paris", "PROPN") == "noun.location", "a PROPN is still asked as a noun"
    assert supersense_for("the", "DET") is None, "a function word is nobody's noun"


# ------------------------------------------------------------------------------------------------
# the NOUN an adjective is about — parser-compiler req 22, and the hash-order defect of 2026-09-19
# ------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("adjective, expected", [
    ("hungry", "noun.state"), ("tired", "noun.state"), ("ready", "noun.state"),
    ("green", "noun.attribute"), ("late", "noun.attribute"), ("cute", "noun.attribute"),
])
def test_the_adjectives_the_subject_rule_depends_on(adjective, expected):
    """These are not examples, they are the evidence `db/0018`'s copular rule fires on: WordNet files
    almost every adjective under `adj.all`, so the noun it measures is what speaks."""
    assert derived_supersense(adjective) == expected


@pytest.mark.parametrize("adjective", ["dead", "alive", "happy"])
def test_an_adjective_the_resource_files_TWO_WAYS_gets_no_answer(adjective):
    """**THE DEFECT THAT MADE ONE SENTENCE TWO THOUGHTS** (2026-09-19, found by the drill gate's
    fourth widening). NLTK keeps a synset's pointers in a `set`, so `attributes()` comes back in the
    process's own string-hash order — and *dead* has TWO attribute nouns, `animation.n.01`
    (`noun.state`) and `animation.n.02` (`noun.attribute`). Taking `[0]` made «the cat is dead» an
    experiencer under one `PYTHONHASHSEED` and a patient under the next.

    Sorting the set would have hidden the question: **WordNet publishes no priority among a synset's
    attributes**, so an order imposed by us would be our invention in the resource's clothes. Where
    the resource does not say, we do not decide — and `db/0019` answers for *happy*, on E2's ruling.
    """
    first = (wn.synsets(adjective, "a") + wn.synsets(adjective, "s"))[0]
    assert len({a.lexname() for a in first.attributes()}) > 1, (
        f"{adjective!r} no longer has disagreeing attributes — this test's premise moved")
    assert derived_supersense(adjective) is None


def test_it_reads_the_WHOLE_relation_and_not_whichever_came_first():
    """The repair, stated as a property rather than as a case: the answer depends on the SET of
    lexnames the resource states, so it cannot depend on the order they arrive in."""
    assert derived_supersense("hungry") == "noun.state", "one reading, and it answers"
    assert derived_supersense("zzzqx") is None
    assert derived_supersense("") is None
