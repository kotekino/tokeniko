"""The compile core — a skeleton in, a zip out.

What is held here is not «it produced a zip» but that it produced the RIGHT SHAPE: the two halves of
the 37 → 18 mapping stay apart, a quantifier binds the phrase it restricts, a possessor lands inside
the record, and every word the station could not place is visible rather than gone.
"""

import pytest

from tests.fixtures.ud import CASES
from tk2.language import standing_closed_classes
from tk2.language.compile import RELATION_FILLS_ROLE, Compiler, compile_sentence
from tk2.language.skeleton import skeleton_from_conllu
from tk2.tkzip.schema import Determination, Open, Operator, Quantity, Role, Var


@pytest.fixture(scope="module")
def compiler():
    return Compiler(standing_closed_classes())


def case(text):
    return next(c for c in CASES if c.text == text)


def compiled(compiler, text):
    return compiler.compile(case(text).skeleton)


# ------------------------------------------------------------------------------------------------
# the two halves of the mapping
# ------------------------------------------------------------------------------------------------


def test_a_core_argument_is_filled_by_the_RELATION(compiler):
    """No marker exists for agent or patient — English marks them by position, and the closed-class
    table proves it by holding no row for either."""
    out = compiled(compiler, "the cat chased the dog")
    boxes = out.zip.rows[-1].boxes

    assert boxes[Role.AGENT].head == "cat.n"
    assert boxes[Role.PATIENT].head == "dog.n"
    assert out.coverage == 1.0


def test_the_passive_subject_IS_the_patient(compiler):
    """«the cat was chased by the dog» — nsubj:pass is the patient and obl:agent is the agent, so
    the passive and the active compile to the SAME roles. That is what «roles normalize» means."""
    out = compiled(compiler, "the cat was chased by the dog")
    boxes = out.zip.rows[-1].boxes

    assert boxes[Role.PATIENT].head == "cat.n"
    assert boxes[Role.AGENT].head == "dog.n"
    assert boxes[Role.AGENT].marker == "by", "and the marker is kept (req 65)"
    assert out.coverage == 1.0


def test_a_circumstance_is_filled_by_the_MARKER(compiler):
    """«Sue left after the rehearsal» — `obl` says «a nominal dependent», which is not a role. The
    marker is what says TIME."""
    out = compiled(compiler, "Sue left after the rehearsal")
    boxes = out.zip.rows[-1].boxes

    assert out.zip.rows[-1].predicate == "leave.v"
    assert boxes[Role.TIME].head == "rehearsal.n"
    assert boxes[Role.TIME].marker == "after"


def test_the_relation_half_names_only_roles_tkzip_has():
    allowed = set(Role)
    assert set(RELATION_FILLS_ROLE.values()) <= allowed
    assert RELATION_FILLS_ROLE["nsubj:pass"] is Role.PATIENT


# ------------------------------------------------------------------------------------------------
# the shapes the schema asked for
# ------------------------------------------------------------------------------------------------


def test_a_quantifier_BINDS_a_variable_restricted_to_its_phrase(compiler):
    """The schema's own docstring: «All cats are mammals» becomes a binder for X restricted to cats,
    then a content row saying X is a mammal. The binder cannot be emitted on meeting «every» — the
    restriction is a Box, and the phrase has not been read yet."""
    out = compiled(compiler, "every cat sleeps")
    binder, content = out.zip.rows

    assert binder.kind == "quantifier"
    assert binder.quantity is Quantity.UNIVERSAL
    assert binder.restriction.head == "cat.n", "restricted to CATS"
    assert binder.scopes == content.name
    assert content.boxes[Role.AGENT].head == Var(name=binder.binds), "the box holds the VARIABLE"


def test_an_article_sets_determination_and_raises_no_binder(compiler):
    """db/0008's re-typing, reaching the zip: the same `det` relation, and only the ROW tells an
    article from a quantifier."""
    out = compiled(compiler, "the cat sleeps")

    assert len(out.zip.rows) == 1, "no binder"
    box = out.zip.rows[0].boxes[Role.AGENT]
    assert box.determination is Determination.DEFINITE
    assert box.head == "cat.n"


def test_both_spellings_of_a_possessor_reach_the_SAME_place(compiler):
    """UD's `case` page pairs «the Chair 's office» with «the office of the Chair» explicitly. tkzip
    keeps the possessor INSIDE the record as Box.relation (req 26), so the two must agree — and
    before db/0009 the clitic spelling threw the possessor away entirely."""
    clitic = compiled(compiler, "the Chair 's office").zip.rows[0].boxes[Role.COMPLEMENT]
    preposition = compiled(compiler, "the office of the Chair").zip.rows[0].boxes[Role.COMPLEMENT]

    assert clitic.head == preposition.head == "office.n"
    assert clitic.relation == preposition.relation == "chair.n"


def test_plain_copular_be_earns_no_predicate(compiler):
    """Req 31 and the Captain's first draft verbatim: «the cat is cute» is cat + cute, NO VERB. And
    the subject of a copula is the TOPIC — nobody is acting."""
    out = compiled(compiler, "Sue is a teacher")
    row = out.zip.rows[-1]

    assert row.predicate is None
    assert row.boxes[Role.COMPLEMENT].head == "teacher.n"
    assert row.boxes[Role.TOPIC].head == "sue.n"


def test_a_pronoun_fills_its_box_with_an_OPEN_head(compiler):
    """Content is defined, structure is compiled (the second standing law). A pronoun is INDEXICAL —
    resolved to an entity from context before the dictionary is consulted — so it fills its role and
    never earns a dimension."""
    out = compiled(compiler, "I sleep")
    box = out.zip.rows[-1].boxes[Role.AGENT]

    assert isinstance(box.head, Open), "not `i.n`"
    assert out.coverage == 1.0


def test_the_sense_slot_is_always_OPEN(compiler):
    """The station never picks a sense — binding is the evaluator's one algorithm, and it has a KB
    to check itself against (evaluator req 5)."""
    out = compiled(compiler, "Sue left after the rehearsal")
    row = out.zip.rows[-1]

    assert isinstance(row.predicate_sense, Open)
    assert all(isinstance(box.sense, Open) for box in row.boxes.values())


# ------------------------------------------------------------------------------------------------
# half-understood is legal; wrongly-understood is the sin
# ------------------------------------------------------------------------------------------------


def test_a_word_the_station_cannot_place_is_VISIBLE(compiler):
    """Req 21: material no box fits is RECORDED, never given a position it did not earn — and never
    silently dropped either.

    The example moved when relative clauses started compiling: this test used to use «the cat that
    sleeps», and the honest thing on that day was to point it at something still unhandled rather
    than to keep asserting a limitation that had been lifted. «who» in an embedded question has no
    rule yet, and that is what the zip reports."""
    out = compiled(compiler, "if you know who did it , tell me")

    assert out.unplaced, "the embedded question is not compiled yet, and the zip says so"
    assert set(out.unplaced) <= set(case("if you know who did it , tell me").skeleton.tokens)
    assert out.zip.unplaced == list(out.unplaced)
    assert 0.0 < out.coverage < 1.0, "partial, and honestly so"


def test_an_ambiguous_marker_abstains_rather_than_guessing(compiler):
    """«I swam IN the pool» reads location|time|instrument|manner and nothing chooses between them.
    Picking the first candidate would be the silently-complete nearest fit req 8 forbids."""
    out = compiled(compiler, "Last night , I swam in the pool")

    assert any("in:" in note for note in out.abstained)
    assert Role.LOCATION not in out.zip.rows[-1].boxes, "it did not guess"
    assert out.zip.rows[-1].boxes[Role.TIME].head == "night.n", "what it DID know is bound"


def test_a_multiword_marker_covers_every_token_it_spans(compiler):
    """«out OF the box» is one form, and `of` hangs off `out` as UD's `fixed`. Marking only the
    first token left `of` looking unplaced in a sentence that was fully understood."""
    out = compiled(compiler, "out of the box")

    assert out.coverage == 1.0 and out.unplaced == ()
    assert out.zip.rows[0].boxes[Role.COMPLEMENT].marker == "out of"


def test_every_case_produces_a_valid_zip(compiler):
    """The schema is FRAME and validates on construction: a zip that exists is a zip that is legal.
    What this adds is that NONE of the corpus crashes the compiler."""
    for ud_case in CASES:
        out = compiler.compile(ud_case.skeleton)
        assert out.zip.rows, f"{ud_case.text!r} produced no rows"
        assert out.zip.schema_version == 2


def test_the_compiler_is_pure(compiler):
    """Context is an argument, never state (req 7). The same skeleton twice is the same zip."""
    first = compiled(compiler, "Sue left after the rehearsal")
    second = compiled(compiler, "Sue left after the rehearsal")

    assert first.zip == second.zip


def test_one_call_needs_no_compiler_object():
    out = compile_sentence(case("the cat sleeps").skeleton, standing_closed_classes())

    assert out.zip.rows[0].predicate == "sleep.v"


# ------------------------------------------------------------------------------------------------
# MANY ROWS — one content row per clause, related by joins, attitudes and shared variables
# ------------------------------------------------------------------------------------------------

from tk2.language.skeleton import skeleton_from_conllu  # noqa: E402

#: «If it rains I stay home.» as stanza reads it.
IF = skeleton_from_conllu("If it rains I stay home.", [
    ("1", "If", "if", "SCONJ", "3", "mark"),
    ("2", "it", "it", "PRON", "3", "nsubj"),
    ("3", "rains", "rain", "VERB", "5", "advcl"),
    ("4", "I", "i", "PRON", "5", "nsubj"),
    ("5", "stay", "stay", "VERB", "0", "root"),
    ("6", "home", "home", "ADV", "5", "advmod"),
    ("7", ".", ".", "PUNCT", "5", "punct"),
])

#: «I stayed home because it rained.» — the same operator, the other assertion status.
BECAUSE = skeleton_from_conllu("I stayed home because it rained.", [
    ("1", "I", "i", "PRON", "2", "nsubj"),
    ("2", "stayed", "stay", "VERB", "0", "root"),
    ("3", "home", "home", "ADV", "2", "advmod"),
    ("4", "because", "because", "SCONJ", "6", "mark"),
    ("5", "it", "it", "PRON", "6", "nsubj"),
    ("6", "rained", "rain", "VERB", "2", "advcl"),
    ("7", ".", ".", "PUNCT", "2", "punct"),
])

#: «It rained and I stayed home.» — the third of the three.
AND = skeleton_from_conllu("It rained and I stayed home.", [
    ("1", "It", "it", "PRON", "2", "nsubj"),
    ("2", "rained", "rain", "VERB", "0", "root"),
    ("3", "and", "and", "CCONJ", "5", "cc"),
    ("4", "I", "i", "PRON", "5", "nsubj"),
    ("5", "stayed", "stay", "VERB", "2", "conj"),
    ("6", "home", "home", "ADV", "5", "advmod"),
    ("7", ".", ".", "PUNCT", "2", "punct"),
])

#: «He says that you swim.» — a POV, not a join.
SAYS = skeleton_from_conllu("He says that you swim.", [
    ("1", "He", "he", "PRON", "2", "nsubj"),
    ("2", "says", "say", "VERB", "0", "root"),
    ("3", "that", "that", "SCONJ", "5", "mark"),
    ("4", "you", "you", "PRON", "5", "nsubj"),
    ("5", "swim", "swim", "VERB", "2", "ccomp"),
    ("6", ".", ".", "PUNCT", "2", "punct"),
])

#: «The cat that sleeps is mine.» — one cat, described twice.
RELATIVE = skeleton_from_conllu("The cat that sleeps is mine.", [
    ("1", "The", "the", "DET", "2", "det"),
    ("2", "cat", "cat", "NOUN", "6", "nsubj"),
    ("3", "that", "that", "PRON", "4", "nsubj"),
    ("4", "sleeps", "sleep", "VERB", "2", "acl:relcl"),
    ("5", "is", "be", "AUX", "6", "cop"),
    ("6", "mine", "mine", "PRON", "0", "root"),
    ("7", ".", ".", "PUNCT", "6", "punct"),
])


def rows_of(out, kind):
    return [r for r in out.zip.rows if r.kind == kind]


def test_IF_asserts_NEITHER_half_and_claims_only_the_join(compiler):
    """THE DISTINCTION E2 SPENT A SESSION ON (req 38). «If it rains I stay home» claims neither the
    rain NOR the staying — only the conditional. The main clause being the ROOT is not a reason to
    claim it, which is what the first draft got backwards."""
    out = compiler.compile(IF)
    content, join = rows_of(out, "content"), rows_of(out, "join")[0]

    assert [r.truth for r in content] == [None, None], "both halves EMPTY — stated, not claimed"
    assert join.operator is Operator.IMPLY
    assert join.truth == 1.0, "the JOIN is what is asserted"


def test_BECAUSE_is_the_same_operator_with_both_halves_CLAIMED(compiler):
    """«I stayed home because it rained» — same IMPLY, and the speaker claims the rain. One operator
    set, no relation field, and the two sentences still distinguishable."""
    out = compiler.compile(BECAUSE)
    content, join = rows_of(out, "content"), rows_of(out, "join")[0]

    assert all(r.truth == 1.0 for r in content), "both halves CLAIMED"
    assert join.operator is Operator.IMPLY
    assert join.operands[0] == next(r.name for r in content if r.predicate == "rain.v"), \
        "the antecedent is the subordinate clause, whichever order it was said in"


def test_AND_is_the_third_and_all_three_are_distinguishable(compiler):
    """«it rained and I stayed home» — the shape the other two are contrasted against."""
    if_out, because_out, and_out = (compiler.compile(s) for s in (IF, BECAUSE, AND))

    shape = lambda o: (rows_of(o, "join")[0].operator,
                       tuple(r.truth for r in rows_of(o, "content")))
    assert shape(if_out) == (Operator.IMPLY, (None, None))
    assert shape(because_out) == (Operator.IMPLY, (1.0, 1.0))
    assert shape(and_out) == (Operator.AND, (1.0, 1.0))
    assert len({shape(if_out), shape(because_out), shape(and_out)}) == 3


def test_a_reporting_verb_opens_an_ATTITUDE_and_claims_only_the_saying(compiler):
    """«He says that you swim» — E2 made the attitude a prefix element with its own holder, not a
    join. The saying is claimed; the swimming is not, and nothing in the zip says it is."""
    out = compiler.compile(SAYS)
    attitude = rows_of(out, "attitude")[0]
    saying = next(r for r in rows_of(out, "content") if r.predicate == "say.v")
    swimming = next(r for r in rows_of(out, "content") if r.predicate == "swim.v")

    assert attitude.verb == "say.v"
    assert attitude.scopes == swimming.name
    assert saying.truth == 1.0
    assert swimming.truth is None, "the content of a report is not claimed by reporting it"
    assert not rows_of(out, "join"), "an attitude is not a join"


def test_a_relative_clause_SHARES_A_VARIABLE_rather_than_joining(compiler):
    """«The cat that sleeps is mine» is ONE cat described twice — req 36's single binding mechanism
    doing the work a second box would fake."""
    out = compiler.compile(RELATIVE)
    sleeping = next(r for r in rows_of(out, "content") if r.predicate == "sleep.v")
    main = next(r for r in rows_of(out, "content") if r.predicate is None)

    shared = sleeping.boxes[Role.AGENT].head
    assert isinstance(shared, Var)
    assert any(box.head == shared for box in main.boxes.values()), "the same variable, both rows"
    assert out.coverage == 1.0, "the relative pronoun IS the variable, not a third participant"


def test_an_xcomp_stays_inside_its_clause(compiler):
    """«you like TO SWIM» is one predication with a controlled subject, not two claims: nobody
    asserts that you swim. A second row would put an unasserted proposition in the zip with nothing
    marking it unasserted — the one thing the truth slot exists to prevent."""
    from tk2.language.compile import CLAUSE_DEPS

    assert "xcomp" not in CLAUSE_DEPS


def test_many_rows_raised_the_floor(compiler):
    """20 of 25 whole and 95.8% mean, up from 18 and 89.5% before joins existed."""
    scored = [compiler.compile(c.skeleton) for c in CASES]
    full = sum(1 for s in scored if s.coverage == 1.0)
    mean = sum(s.coverage for s in scored) / len(scored)

    assert full >= 20, f"{full} of {len(CASES)} whole; 20 were on 2026-09-15"
    assert mean >= 0.95, f"mean {mean:.1%}; it was 95.8% on 2026-09-15"
