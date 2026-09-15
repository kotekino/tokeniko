"""The skeleton — tokens, universal POS, dependencies, and the boundary that keeps them swappable.

Almost everything here is written against HAND-BUILT skeletons, which is the point of the dataclass:
the station must be testable without loading a 400 MB model, and a test that needs one is a test
that will eventually be skipped. The few that call stanza carry `@pytest.mark.skeleton`.
"""

import pytest

from tk2.language import (
    EMBEDDING_DEPS,
    UD_DEPS,
    UD_POS,
    Skeleton,
    Word,
    bare,
    skeleton_from_conllu,
    standing_closed_classes,
)

#: «The cat sat on the mat because of the rain.» exactly as stanza reads it — captured from a live
#: parse on 2026-09-15 so the shape under test is a real one and not one I found convenient.
CAT = skeleton_from_conllu("The cat sat on the mat because of the rain.", [
    ("1", "The", "the", "DET", "2", "det"),
    ("2", "cat", "cat", "NOUN", "3", "nsubj"),
    ("3", "sat", "sit", "VERB", "0", "root"),
    ("4", "on", "on", "ADP", "6", "case"),
    ("5", "the", "the", "DET", "6", "det"),
    ("6", "mat", "mat", "NOUN", "3", "obl"),
    ("7", "because", "because", "ADP", "10", "case"),
    ("8", "of", "of", "ADP", "7", "fixed"),
    ("9", "the", "the", "DET", "10", "det"),
    ("10", "rain", "rain", "NOUN", "3", "obl"),
    ("11", ".", ".", "PUNCT", "3", "punct"),
])

#: «I am happy when I talk.» — tk1's R5 specimen: the `when` is NOT a question.
HAPPY = skeleton_from_conllu("I am happy when I talk.", [
    ("1", "I", "i", "PRON", "3", "nsubj"),
    ("2", "am", "be", "AUX", "3", "cop"),
    ("3", "happy", "happy", "ADJ", "0", "root"),
    ("4", "when", "when", "ADV", "6", "advmod"),
    ("5", "I", "i", "PRON", "6", "nsubj"),
    ("6", "talk", "talk", "VERB", "3", "advcl"),
    ("7", ".", ".", "PUNCT", "3", "punct"),
])

#: «When do you sleep?» — the same word, attaching to the root. A question.
WHEN = skeleton_from_conllu("When do you sleep?", [
    ("1", "When", "when", "ADV", "4", "advmod"),
    ("2", "do", "do", "AUX", "4", "aux"),
    ("3", "you", "you", "PRON", "4", "nsubj"),
    ("4", "sleep", "sleep", "VERB", "0", "root"),
    ("5", "?", "?", "PUNCT", "4", "punct"),
])


# ------------------------------------------------------------------------------------------------
# the shape
# ------------------------------------------------------------------------------------------------


def test_the_root_heads_itself(): 
    """CoNLL-U writes the root's head as 0 and is 1-indexed; we are 0-indexed and the root points at
    ITSELF — so a walk terminates on identity of INDEX, never on a sentinel nobody checked for."""
    assert CAT.root.text == "sat"
    assert CAT.root.head == CAT.root.index
    assert sum(1 for w in CAT if w.is_root) == 1


def test_heads_are_indices_and_never_objects():
    """THE 43-MINUTE GREMLIN, inherited from tk1: spaCy mints a fresh Token wrapper on every `.head`
    access, so `token.head is token` is never true and a walk to the root never terminates."""
    assert all(isinstance(w.head, int) for w in CAT)
    node = CAT[9]
    for _ in range(len(CAT)):
        if node.is_root:
            break
        node = CAT[node.head]
    assert node.is_root, "the walk terminated"


def test_subtypes_are_bared_but_the_full_label_survives():
    """`acl:relcl` is a refinement OF `acl`. A consumer matching the full string would silently stop
    handling a relation the moment a model got more specific."""
    assert bare("acl:relcl") == "acl" and bare("nsubj") == "nsubj"
    w = Word(index=0, text="x", lemma="x", upos="VERB", dep="acl:relcl", head=0)
    assert w.dep == "acl:relcl" and w.bare_dep == "acl"


def test_children_and_tags_are_what_the_table_reads():
    assert [w.text for w in CAT.children(5)] == ["on", "the"]
    assert CAT.tags[3] == ("ADP", "case")
    assert CAT.tokens[:3] == ("The", "cat", "sat")


# ------------------------------------------------------------------------------------------------
# R5 — the wh-position test, inherited with its bound intact
# ------------------------------------------------------------------------------------------------


def test_a_wh_attaching_to_the_root_is_a_question_and_one_under_advcl_is_not():
    """tk1's R5, earned on live specimens 2026-07-12/13: «WHEN do you sleep» is a question,
    «I am happy WHEN I talk» is subordination — and a taught rule, not a question about time."""
    assert WHEN.attaches_to_root(0) is True
    assert HAPPY.attaches_to_root(3) is False
    assert "advcl" in EMBEDDING_DEPS


def test_the_walk_is_bounded_so_a_head_cycle_cannot_hang_the_station():
    """Not defensive programming: a malformed skeleton would otherwise spin forever, and the station
    must fail rather than stop responding."""
    cycle = Skeleton(text="broken", words=(
        Word(index=0, text="a", lemma="a", upos="X", dep="dep", head=1),
        Word(index=1, text="b", lemma="b", upos="X", dep="dep", head=0),
    ))

    assert cycle.attaches_to_root(0) in (True, False), "it returned rather than hanging"


# ------------------------------------------------------------------------------------------------
# the UD gate's own instrument
# ------------------------------------------------------------------------------------------------


def test_the_declared_vocabularies_are_ud_s(): 
    assert len(UD_POS) == 17, "UD publishes seventeen universal POS tags"
    assert len(UD_DEPS) == 37, "and thirty-seven main dependency relations"
    assert "case" in UD_DEPS and "ADP" in UD_POS


def test_a_skeleton_reports_what_is_NOT_ud():
    """«Take stanza as close enough and CHECK against UD2» (the Captain) — this is the checking."""
    assert CAT.non_ud() == ()

    creative = skeleton_from_conllu("x", [("1", "x", "x", "PARTICLE", "0", "prepmod")])
    assert creative.non_ud() == ("PARTICLE", "prepmod")


# ------------------------------------------------------------------------------------------------
# the skeleton and the table together — which is the whole point of both
# ------------------------------------------------------------------------------------------------


def test_a_multiword_marker_is_read_across_two_tokens_of_a_real_parse():
    """stanza reads «because of» as two tokens, `case` + `fixed`. The table holds it as ONE form,
    and it compiles to a JOIN — so the sentence has a cause, not a location."""
    table = standing_closed_classes()
    found = {i: m for i, m in table.walk(CAT.tokens, CAT.tags)}

    assert found[6].form == "because of"
    assert found[6].kind == "join" and found[6].compiled["operator"] == "imply"
    assert 7 not in found, "the second token was consumed by the form"


def test_the_dependency_outranks_the_pos_when_they_disagree():
    """FOUND ON A LIVE PARSE, 2026-09-15. stanza reads «He looked UP» as `upos=ADP, dep=compound:prt`
    — the tag says «adposition», the relation says «the verb's particle». Narrowing by POS first
    returned a DIRECTION marker for a phrasal verb. A POS tag labels a token in isolation; a
    dependency states its relation to the sentence, and the job this table records is relational."""
    table = standing_closed_classes()

    assert table.select("up", "ADP", "compound:prt")["role"] == "verb_particle"
    assert table.select("up", "ADP", "case")["role"] == "role_marker"


# ------------------------------------------------------------------------------------------------
# the provider itself — the only tests that need the model
# ------------------------------------------------------------------------------------------------


@pytest.mark.skeleton
def test_stanza_produces_a_ud_skeleton():
    from tk2.language import StanzaSkeletons

    sentences = StanzaSkeletons()("The cat sat on the mat because of the rain.")

    assert len(sentences) == 1
    got = sentences[0]
    assert got.tokens == CAT.tokens
    assert [w.dep for w in got] == [w.dep for w in CAT], "the captured shape is still what it emits"
    assert got.non_ud() == ()


@pytest.mark.skeleton
def test_a_second_sentence_indexes_within_ITSELF():
    """spaCy's `token.i` is an offset into the whole DOCUMENT, so a second sentence would carry heads
    pointing past its own end. A skeleton IS one sentence and indexes within one."""
    from tk2.language import StanzaSkeletons

    first, second = StanzaSkeletons()("The cat sleeps. The dog barks.")

    for sentence in (first, second):
        assert all(0 <= w.head < len(sentence) for w in sentence)
        assert sentence.root is not None
