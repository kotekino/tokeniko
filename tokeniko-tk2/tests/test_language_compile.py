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
from tk2.tkzip.schema import Determination, Open, Quantity, Role, Var


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
    silently dropped either."""
    out = compiled(compiler, "the cat that sleeps")

    assert out.unplaced, "the relative clause is not compiled yet, and the zip says so"
    assert set(out.unplaced) <= set(case("the cat that sleeps").skeleton.tokens)
    assert out.zip.unplaced == list(out.unplaced)


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


def test_coverage_is_measured_and_held(compiler):
    """A floor for the confidence scalar to be built on later (req 4). It may only go up — and if a
    change lowers it, that is the change saying something about itself."""
    scored = [compiler.compile(c.skeleton) for c in CASES]
    full = sum(1 for s in scored if s.coverage == 1.0)
    mean = sum(s.coverage for s in scored) / len(scored)

    assert full >= 18, f"{full} of {len(CASES)} compiled whole; 18 did on 2026-09-15"
    assert mean >= 0.89, f"mean coverage {mean:.1%}; it was 89.5% on 2026-09-15"


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
