"""Reading the closed classes — the matcher and the job selector (`tk2/language/`).

Two problems the table alone cannot solve: a form can be several WORDS, and a form can be several
JOBS. This holds both, and holds that UD is what decides the second.
"""

import pytest

from tk2.language import UD_DEP_TO_ROLE, UD_POS_TO_WORD_CLASS, ClosedClasses, standing_closed_classes


@pytest.fixture(scope="module")
def table():
    return standing_closed_classes()


def rows(*specs):
    """A tiny table: (form, word_class, role, compiled)."""
    return ClosedClasses([
        {"form": f, "word_class": w, "role": r, "compiled": c, "features": {}, "version": 2}
        for f, w, r, c in specs
    ], source="(fixture)")


# ------------------------------------------------------------------------------------------------
# a form can be several WORDS
# ------------------------------------------------------------------------------------------------


def test_the_longest_form_wins(table):
    """«in front of the station» is ONE role marker. A matcher walking token by token would see
    `in` and hand the compiler a LOCATION marker for a phrase that means something else."""
    tokens = "the cat sat in front of the station".split()

    assert table.match(tokens, 3) == "in front of"
    assert table.match(tokens, 0) == "the"


def test_a_multiword_form_is_consumed_WHOLE(table):
    """The walk must not re-read `front` and `of` as forms in their own right."""
    tokens = "I walked in front of him".split()
    found = dict((i, m.form) for i, m in table.walk(tokens))

    assert found[2] == "in front of"
    assert 3 not in found and 4 not in found, "the inner tokens were consumed"
    assert found[5] == "him"


def test_matching_is_case_folded(table):
    assert table.match(["The", "cat"], 0) == "the"


def test_the_table_knows_its_own_shape(table):
    """The reader always holds ONE version — the newest it was given — because a table carrying two
    would answer the same form twice with different jobs. Not pinned to a number here: the versions
    are a ledger and will keep growing, and a test that pinned one would fail on every correction
    while proving nothing about the reader."""
    assert table.version >= 2
    assert table.longest == 3, "English's complex prepositions reach three tokens here"
    assert len(table.multiword_forms()) > 40
    assert "in front of" in table.multiword_forms()


# ------------------------------------------------------------------------------------------------
# a form can be several JOBS — and UD is the selector
# ------------------------------------------------------------------------------------------------


def test_that_is_three_forms_and_the_dependency_decides(table):
    """`that` is a subordinator, a demonstrative and a relative. The row cannot say which; the
    sentence does, and stanza reports it as a UD dependency label."""
    assert len(table.jobs("that")) == 3

    assert table.select("that", "SCONJ", "mark")["role"] == "subordinator"
    assert table.select("that", "DET", "det")["role"] == "demonstrative"
    assert table.select("that", "PRON", "nsubj")["role"] == "relative"


def test_no_is_a_quantifier_or_a_negation(table):
    assert table.select("no", "DET", "det")["role"] == "quantificational"
    assert table.select("no", "PART", "advmod")["role"] == "negation"


def test_there_is_referential_or_existential(table):
    assert table.select("there", "PRON", "expl")["role"] == "existential"
    assert table.select("there", "ADV", "advmod")["role"] == "referential"


def test_a_filter_that_would_empty_the_set_is_NOT_applied(table):
    """UD and this table were built by different people for different purposes. A token UD calls
    something this table does not hold is a disagreement about LABELS — dropping the match there
    would lose a form the station can see perfectly well."""
    kept = table.select("through", "VERB", "root")

    assert kept is not None, "a nonsense tag must not delete the form"
    assert kept["form"] == "through"


def test_an_unnarrowed_match_says_it_is_uncertain(table):
    """`Match.certain` is what the confidence scalar is entitled to know: the form is right, the
    job was picked without evidence."""
    blind = table.read(["that"], 0)
    told = table.read(["that"], 0, "SCONJ", "mark")

    assert blind.certain is False and told.certain is True
    assert told.role == "subordinator"


def test_an_unambiguous_form_is_certain_even_with_no_tags(table):
    only = table.read(["because", "of", "you"], 0)

    assert only.form == "because of" and only.certain is True


# ------------------------------------------------------------------------------------------------
# what a match carries into the zip
# ------------------------------------------------------------------------------------------------


def test_a_match_carries_the_compiled_meaning(table):
    to = table.read(["to", "Anna"], 0, "ADP", "case")

    assert to.kind == "box"
    assert to.roles == ("destination", "recipient"), "best-first, both kept"


def test_a_causal_marker_reads_as_a_JOIN_not_a_box(table):
    because = table.read(["because", "of", "the", "rain"], 0, "ADP", "case")

    assert because.kind == "join"
    assert because.compiled["operator"] == "imply"
    assert because.roles == (), "it marks no box at all"


def test_the_walk_finds_every_closed_form_in_a_sentence(table):
    tokens = "the cat sat on the mat because of the rain".split()
    found = [(i, m.form, m.kind) for i, m in table.walk(tokens)]
    forms = [f for _, f, _ in found]

    assert forms == ["the", "on", "the", "because of", "the"]
    assert found[-2][2] == "join", "«because of» joins rows; it is not a location"


# ------------------------------------------------------------------------------------------------
# the frame maps relate two published vocabularies, and only that
# ------------------------------------------------------------------------------------------------


def test_the_ud_maps_name_only_word_classes_and_roles_the_table_has(table):
    classes = {r["word_class"] for r in table._rows}
    roles = {r["role"] for r in table._rows}

    named_classes = {c for group in UD_POS_TO_WORD_CLASS.values() for c in group}
    named_roles = {r for group in UD_DEP_TO_ROLE.values() for r in group}

    assert not named_classes - classes, f"UD map names a word_class the table lacks: {named_classes - classes}"
    unknown = named_roles - roles
    assert unknown <= {"complementizer"}, f"UD map names a role the table lacks: {unknown}"


def test_a_tiny_table_behaves_like_the_real_one():
    """The reader holds no knowledge of its own — hand it three rows and it reads three rows."""
    t = rows(
        ("up to", "preposition", "role_marker", {"kind": "box", "roles": ["destination"]}),
        ("up", "preposition", "role_marker", {"kind": "box", "roles": ["direction"]}),
        ("up", "particle", "verb_particle", {"kind": "structure"}),
    )

    assert t.match(["up", "to", "here"], 0) == "up to"
    assert t.select("up", "ADP", "case")["role"] == "role_marker"
    assert t.select("up", "PART", "compound:prt")["role"] == "verb_particle"
