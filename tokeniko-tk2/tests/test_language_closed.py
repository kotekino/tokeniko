"""Reading the closed classes — the matcher and the job selector (`tk2/language/`).

Two problems the table alone cannot solve: a form can be several WORDS, and a form can be several
JOBS. This holds both, and holds that UD is what decides the second.
"""

import pytest

from tk2.language import UD_POS_TO_WORD_CLASS, ClosedClasses, standing_closed_classes
from tk2.language.ud_readings import UdReadings


@pytest.fixture(scope="module")
def table():
    return standing_closed_classes()


def rows(*specs, readings=None):
    """A tiny table: (form, word_class, role, compiled)."""
    return ClosedClasses([
        {"form": f, "word_class": w, "role": r, "compiled": c, "features": {}, "version": 2}
        for f, w, r, c in specs
    ], source="(fixture)", readings=readings)


def readings(**admits):
    """Tiny UD readings: relation -> the roles it admits (`db/0034`'s shape)."""
    return UdReadings([
        {"version": 2, "inventory": "relation", "label": label.replace("__", ":"),
         "reads": {"admits_roles": sorted(roles)}, "source": "(fixture)", "position": n}
        for n, (label, roles) in enumerate(admits.items())
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
    would lose a form the station can see perfectly well.

    `case` leaves `through` ONE reading — the path marker, before its noun or after it — and the
    `VERB` tag empties the POS filter. The tolerance keeps what the relation settled."""
    kept = table.select("through", "VERB", "case")

    assert kept is not None, "a nonsense tag must not delete the form"
    assert kept["form"] == "through" and kept["role"] == "role_marker"


def test_an_unnarrowed_match_says_it_is_uncertain(table):
    """`Match.certain` is what the confidence scalar is entitled to know: the form is right, the
    word class was picked without evidence. «his» is one READING in two rows — the determiner and
    the pronoun — so the meaning is settled and only which row carried it is a guess."""
    blind = table.read(["his"], 0)
    told = table.read(["his"], 0, "DET", "det:poss")

    assert blind.certain is False and told.certain is True
    assert blind.role == told.role == "possessive"
    assert told.word_class == "determiner"


def test_an_unnarrowed_match_of_SEVERAL_readings_is_not_made_at_all(table):
    """«that» with no tags is a subordinator, a demonstrative or a relative, and nothing says which.
    The guess this used to return is exactly what the tie rule refuses (the Captain, 2026-09-24)."""
    assert table.read(["that"], 0) is None
    assert table.read(["that"], 0, "SCONJ", "mark").role == "subordinator"


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
    tags = [("DET", "det"), (None, None), (None, None), ("ADP", "case"), ("DET", "det"),
            (None, None), ("ADP", "case"), ("ADP", "fixed"), ("DET", "det"), (None, None)]
    found = [(i, m.form, m.kind) for i, m in table.walk(tokens, tags)]
    forms = [f for _, f, _ in found]

    assert forms == ["the", "on", "the", "because of", "the"]
    assert found[-2][2] == "join", "«because of» joins rows; it is not a location"


# ------------------------------------------------------------------------------------------------
# the frame maps relate two published vocabularies, and only that
# ------------------------------------------------------------------------------------------------


def test_the_ud_maps_name_only_word_classes_and_roles_the_table_has(table):
    """The POS map is frame and the admissible roles are UD readings (`db/0034`) — and both must
    name only what the closed classes hold, or they filter against a vocabulary that is not there."""
    classes = {r["word_class"] for r in table._rows}
    roles = {r["role"] for r in table._rows}

    named_classes = {c for group in UD_POS_TO_WORD_CLASS.values() for c in group}
    named_roles = {role for row in table.readings._rows
                   for role in (row.get("reads") or {}).get("admits_roles") or ()}

    assert named_roles, "the readings admit no role at all — `db/0034` is not what the table read"
    assert not named_classes - classes, f"UD map names a word_class the table lacks: {named_classes - classes}"
    unknown = named_roles - roles
    assert unknown <= {"complementizer"}, f"the readings admit a role the table lacks: {unknown}"


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


def test_a_CONTENT_word_is_not_a_function_word_spelled_the_same(table):
    """**«Every human BEING is an animal» compiled to «An animal is.»** The noun matched the row for
    `being` — the copula's participle — was read as STRUCTURE, compiled to nothing, and took the
    whole subject with it; its adjective «human» went `unplaced`.

    **221 of the 331 forms here have exactly ONE row**, and the shortcut for those returned it
    without ever consulting the POS. At least seventeen are ordinary English words — `back` · `can`
    · `will` · `need` · `like` · `one` · `past` · `round` — so «the BACK of the house», «a CAN of
    soup» and «the WILL of the people» each silently lost a noun.

    This table holds pronouns, determiners, adpositions, conjunctions, auxiliaries, modals,
    particles, clitics and adverbs. **Not one noun, adjective or proper noun** — so a token UD tags
    as one of those is not in here at all.
    """
    assert table.select("being", "NOUN", "nsubj") is None
    assert table.select("back", "NOUN", "nsubj") is None
    assert table.select("will", "NOUN", "nsubj") is None

    # and the same spellings still answer where they ARE function words
    assert table.select("being", "AUX", "cop") is not None
    assert table.select("will", "AUX", "aux")["role"] == "tense_aspect"


def test_the_refusal_does_NOT_extend_to_an_INCREDIBLE_tag(table):
    """The other half, and the reason `VERB` is not on the list: the difference is whether the tag
    is CREDIBLE. English has a noun «being», so UD tagging it `NOUN` is right. There is no verb
    «through», so UD tagging it `VERB` is a parse error — and deleting the preposition over it
    would lose a form the station can see perfectly well.

    That is the disagreement `select`'s own note forgives, and it is why the refusal names the
    three classes whose tag can be trusted rather than every open class UD has.
    """
    assert table.select("through", "VERB", "case") is not None
    assert table.select("because", "VERB", "mark") is not None, "one row: the tag deletes nothing"


# ------------------------------------------------------------------------------------------------
# which roles a relation admits is a READING (`db/0034`) — and a tie nobody settles abstains
# ------------------------------------------------------------------------------------------------


def test_admits_roles_is_read_from_the_rows_with_the_subtype_falling_back():
    """The full label first, then the bare one — and a relation nobody wrote about admits anything,
    because a miss is an answer: UD has 37 relations and most never meet a closed-class form."""
    r = readings(det={"determination", "possessive"}, det__poss={"possessive"},
                 compound__prt={"verb_particle"})

    assert r.admits_roles("det") == frozenset({"determination", "possessive"})
    assert r.admits_roles("det:poss") == frozenset({"possessive"}), "the subtype's own row"
    assert r.admits_roles("det:predet") == r.admits_roles("det"), "no row: the bare label's"
    assert r.admits_roles("compound:prt") == frozenset({"verb_particle"})
    assert r.admits_roles("compound") is None, "`compound:prt` is never read as `compound`"
    assert r.admits_roles("nsubj") is None, "a miss is NO CONSTRAINT"


def test_a_subtype_row_that_answers_ANOTHER_question_does_not_hide_the_bare_labels_set():
    r = UdReadings([
        {"version": 2, "inventory": "relation", "label": "obl", "reads": {"admits_roles": ["x"]},
         "source": "(fixture)", "position": 0},
        {"version": 2, "inventory": "relation", "label": "obl:tmod",
         "reads": {"opens_clause": False}, "source": "(fixture)", "position": 1},
    ])

    assert r.admits_roles("obl:tmod") == frozenset({"x"})


def test_the_standing_table_reads_the_standing_admissible_sets(table):
    """`db/0034` is what the station filters by — no map in code stands behind it."""
    assert table.readings.admits_roles("compound:prt") == frozenset({"verb_particle"})
    assert "fused_quantifier" in table.readings.admits_roles("nsubj")
    assert table.readings.admits_roles("discourse") is None


TWO_READINGS = (
    ("no", "determiner", "quantificational", {"kind": "quantifier", "quantity": "negative"}),
    ("no", "particle", "negation", {"kind": "prefix", "element": "negation"}),
)


def test_a_tie_of_two_READINGS_is_not_picked():
    """Both rows admitted by the relation and no tag to narrow them: nothing says which, and the
    table's own order is not evidence (the Captain, 2026-09-24)."""
    t = rows(*TWO_READINGS, readings=readings(advmod={"quantificational", "negation"}))

    assert t.select("no", None, "advmod") is None
    assert {r["role"] for r in t.candidates("no", None, "advmod")} == {"quantificational",
                                                                       "negation"}
    assert t.read(["no"], 0, None, "advmod") is None, "unplaced — the honest answer"
    assert t.select("no", "PART", "advmod")["role"] == "negation", "the tag settles it"


def test_an_EMPTIED_filter_with_two_readings_does_not_fall_back_to_the_first():
    """«NO, some software…»: `discourse` admits nothing the rows hold and `INTJ` names no word class
    here. Both filters empty, both are forgiven — and what they leave is still a tie."""
    t = rows(*TWO_READINGS, readings=readings(det={"quantificational"}))

    assert t.select("no", "INTJ", "discourse") is None
    assert t.select("no", "INTJ", "obj") is None, "a dep filter that emptied chose nothing either"


def test_an_emptied_filter_with_ONE_reading_still_keeps_it():
    """The tolerance survives the tie rule: two rows that SAY the same thing are one reading, and a
    tag that fits neither is a disagreement about labels, not a tie."""
    t = rows(("aside", "preposition", "role_marker", {"kind": "box", "roles": ["location"]}),
             ("aside", "postposition", "role_marker", {"kind": "box", "roles": ["location"]}),
             readings=readings(case={"role_marker"}))

    assert t.select("aside", "INTJ", "discourse")["role"] == "role_marker"
    assert t.select("aside", "INTJ", "case")["word_class"] == "preposition"


def test_the_standing_no_under_discourse_is_not_compiled_as_anything(table):
    """t-ng-4's «No» as stanza parses it: `INTJ`, `discourse`. It used to fall back to the table's
    first row and compile as a negative QUANTIFIER."""
    assert table.select("no", "INTJ", "discourse") is None
    assert table.read(["No", ",", "some"], 0, "INTJ", "discourse", head_dep="root",
                      in_root_clause=True) is None


def test_the_clause_settles_a_wh_tie_the_relation_leaves_open(table):
    """«who» under `nsubj` is interrogative or relative, and the relation admits both. The CLAUSE
    says which — and a tree-less caller, which cannot, gets no pick."""
    asked = dict(upos="PRON", dep="nsubj")

    assert table.select("who", **asked) is None, "the relation alone is a tie"
    assert table.read(["who"], 0, **asked, head_dep="root", in_root_clause=True).role == \
        "interrogative"
    assert table.read(["who"], 0, **asked, head_dep="acl:relcl", in_root_clause=False).role == \
        "relative"
    assert table.read(["who"], 0, **asked, head_dep="ccomp", in_root_clause=False).role == \
        "interrogative", "an embedded question asks — `who` has no free-relative row"
    assert table.read(["who"], 0, **asked) is None, "no tree, and nothing else can say"


def test_the_clause_does_not_settle_a_tie_OUTSIDE_the_wh_readings():
    """`what` the exclamative quantifier beside `what` the question: the clause separates the three
    wh-readings and has no evidence about anything else."""
    t = rows(("what", "determiner", "quantificational", {"kind": "quantifier"}),
             ("what", "pronoun", "interrogative", {"kind": "open", "opens": "participant"}),
             readings=readings(det={"quantificational", "interrogative"}))

    assert t.read(["what"], 0, None, "det", head_dep="root", in_root_clause=True) is None


# ------------------------------------------------------------------------------------------------
# a row may name the clause it is the reading for — `features.introduces`, `db/0037`
# ------------------------------------------------------------------------------------------------


def test_TO_is_a_purpose_under_an_advcl_and_structure_anywhere_else(table):
    """«I go TO sleep» and «I want TO sleep» are one token, one tag, one relation; the clause it
    introduces is what differs (the Captain, 2026-09-25: *«recognised by SHAPE»*)."""
    mark = dict(upos="PART", dep="mark")

    purpose = table.read(["to"], 0, **mark, head_dep="advcl", in_root_clause=False)
    assert purpose.compiled == {"kind": "join", "operator": "imply", "asserts": "antecedent",
                                "antecedent": "matrix"}
    assert table.read(["to"], 0, **mark, head_dep="xcomp", in_root_clause=False).compiled == \
        {"kind": "structure"}
    assert table.read(["to"], 0, **mark, head_dep="csubj", in_root_clause=False).compiled == \
        {"kind": "structure"}, "«To err is human» is no purpose"


def test_a_reader_with_NO_TREE_never_sees_a_row_that_names_a_clause(table):
    """`select` and a token walk hold no clause, so the clause-bound reading cannot be theirs — and
    the old `to` answers exactly as it did."""
    assert table.select("to", "PART", "mark")["compiled"] == {"kind": "structure"}
    assert all((r.get("features") or {}).get("introduces") is None
               for r in table.candidates("to", "PART", "mark"))


# ------------------------------------------------------------------------------------------------
# a wh-word at the front of an ADVERBIAL clause is its joiner — `E3.12.5.9.5`
# ------------------------------------------------------------------------------------------------


def test_WHEN_under_an_advcl_is_the_subordinator_and_a_question_everywhere_else(table):
    """stanza tags «when» `advmod` in «I stay home WHEN it rains», never `mark`, and the walk read it
    as a question word. Under an `advcl` it can be neither a question nor a relative — the clause
    is a circumstance and modifies no noun — so the tree picks the conjunction row."""
    adverb = dict(upos="ADV", dep="advmod")

    joining = table.read(["when"], 0, **adverb, head_dep="advcl", in_root_clause=False)
    assert joining.role == "subordinator" and joining.kind == "join"
    assert table.read(["when"], 0, **adverb, head_dep="root", in_root_clause=True).role == \
        "interrogative", "«When do you sleep?» still asks"
    assert table.read(["when"], 0, **adverb, head_dep="acl:relcl",
                      in_root_clause=False).role == "relative"


def test_a_wh_word_whose_subordinator_row_opens_a_POINT_OF_VIEW_is_not_made_a_joiner(table):
    """«where»'s subordinator row asserts its `matrix`, which the compiler routes to an ATTITUDE
    (`db/0037`) — and a wh-word at the front of an adverbial clause opens no point of view."""
    read = table.read(["where"], 0, "ADV", "advmod", head_dep="advcl", in_root_clause=False)

    assert read is None or read.role != "subordinator"
