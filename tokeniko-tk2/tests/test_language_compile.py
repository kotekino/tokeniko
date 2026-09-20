"""The compile core — a skeleton in, a zip out.

What is held here is not «it produced a zip» but that it produced the RIGHT SHAPE: the two halves of
the 37 → 18 mapping stay apart, a quantifier binds the phrase it restricts, a possessor lands inside
the record, and every word the station could not place is visible rather than gone.
"""

import inspect

import pytest

from tests.fixtures.ud import CASES, frontier, ratchet
from tk2.language import standing_closed_classes
from tk2.language.compile import RELATION_FILLS_ROLE, Compiler, compile_sentence
from tk2.language.skeleton import skeleton_from_conllu
from tk2.tkzip.schema import (
    SCHEMA_VERSION, Determination, Open, Operator, Quantity, Role, Var,
)


@pytest.fixture(scope="module")
def compiler():
    return Compiler(standing_closed_classes())


def case(text):
    return next(c for c in CASES if c.text == text)


def compiled(compiler, text):
    return compiler.compile(case(text).skeleton)


def main_row(out):
    """The last CLAUSE row — which is neither `rows[-1]` nor «the last content row», and stopped
    being both the day attributive adjectives started raising rows and joins of their own.

    A zip is a FLAT LIST whose order carries scope (req 35), not a list whose last element is the
    point. Clause rows are named `r0, r1, …`; a modifier's row is `mN` and an antecedent's is
    `rN_why`, and neither is what a test about the predication means.
    """
    import re
    return [r for r in out.zip.rows
            if r.kind == "content" and re.fullmatch(r"r\d+", r.name)][-1]


# ------------------------------------------------------------------------------------------------
# the two halves of the mapping
# ------------------------------------------------------------------------------------------------


def test_a_core_argument_is_filled_by_the_RELATION(compiler):
    """No marker exists for agent or patient — English marks them by position, and the closed-class
    table proves it by holding no row for either."""
    out = compiled(compiler, "the cat chased the dog")
    boxes = main_row(out).boxes

    assert boxes[Role.AGENT].head == "cat.n"
    assert boxes[Role.PATIENT].head == "dog.n"
    assert out.coverage == 1.0


def test_the_passive_subject_IS_the_patient(compiler):
    """«the cat was chased by the dog» — nsubj:pass is the patient and obl:agent is the agent, so
    the passive and the active compile to the SAME roles. That is what «roles normalize» means."""
    out = compiled(compiler, "the cat was chased by the dog")
    boxes = main_row(out).boxes

    assert boxes[Role.PATIENT].head == "cat.n"
    assert boxes[Role.AGENT].head == "dog.n"
    assert boxes[Role.AGENT].marker == "by", "and the marker is kept (req 65)"
    assert out.coverage == 1.0


def test_a_circumstance_is_filled_by_the_MARKER(compiler):
    """«Sue left after the rehearsal» — `obl` says «a nominal dependent», which is not a role. The
    marker is what says TIME."""
    out = compiled(compiler, "Sue left after the rehearsal")
    boxes = main_row(out).boxes

    assert main_row(out).predicate == "leave.v"
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
    """Req 31 and the Captain's first draft verbatim: «the cat is cute» is cat + cute, NO VERB.

    **And the subject is the PATIENT, which the drill settles.** The compile core wrote `topic` here,
    reasoning from «what the complement is said of» — sound English, wrong role name. In this
    inventory `topic` is SUBJECT MATTER, the thing «about» and «on» mark, and the drill uses it for
    that and nothing else (three times) while hand-compiling the copular row as patient + complement
    **43 times**. E2 ruled the shape outright: *row · POV · patient · complement*.
    """
    out = compiled(compiler, "Sue is a teacher")
    row = main_row(out)

    assert row.predicate is None
    assert row.boxes[Role.COMPLEMENT].head == "teacher.n"
    assert row.boxes[Role.PATIENT].head == "sue.n"


def test_the_compiler_uses_topic_for_SUBJECT_MATTER_and_nothing_else(compiler):
    """The control that would have caught the copular slip, stated as the invariant rather than as
    the one case: `topic` is what «about» and «on» mark. A copular subject is not subject matter."""
    copular = compiled(compiler, "Sue is a teacher")
    assert Role.TOPIC not in copular.zip.rows[-1].boxes

    marked = compiler.table.jobs("about")[0]["compiled"]
    assert marked["roles"][0] == "topic", "the marker table is where topic comes from"


def test_a_pronoun_fills_its_box_with_an_OPEN_head(compiler):
    """Content is defined, structure is compiled (the second standing law). A pronoun is INDEXICAL —
    resolved to an entity from context before the dictionary is consulted — so it fills its role and
    never earns a dimension."""
    out = compiled(compiler, "I sleep")
    box = main_row(out).boxes[Role.AGENT]

    assert isinstance(box.head, Open), "not `i.n`"
    assert out.coverage == 1.0


def test_the_sense_slot_is_always_OPEN(compiler):
    """The station never picks a sense — binding is the evaluator's one algorithm, and it has a KB
    to check itself against (evaluator req 5)."""
    out = compiled(compiler, "Sue left after the rehearsal")
    row = main_row(out)

    assert isinstance(row.predicate_sense, Open)
    assert all(isinstance(box.sense, Open) for box in row.boxes.values())


# ------------------------------------------------------------------------------------------------
# half-understood is legal; wrongly-understood is the sin
# ------------------------------------------------------------------------------------------------


def test_an_EMBEDDED_QUESTION_opens_its_slot(compiler):
    """«if you know WHO did it, tell me» — the wh-word opens a participant in its own row, and the
    utterance is still not a question.

    **A WH-WORD HAS THREE READINGS AND R5's BINARY TEST CONFLATED THE LAST PAIR.** R5 asks «is this
    the root clause» and answers the MOOD question rightly — «I am happy WHEN I talk» is not an
    interrogative. It was then read as «therefore RELATIVE», which is the conflation: an embedded
    question opens its slot exactly as a root one does. **UD marks the difference**: a relative
    clause modifies a NOUN (`acl:relcl`); an embedded question is a clausal COMPLEMENT.
    """
    out = compiled(compiler, "if you know who did it , tell me")
    did = next(r for r in out.zip.rows if getattr(r, "predicate", None) == "do.v")

    assert isinstance(did.boxes[Role.AGENT].head, Open), "`who` opens the agent slot"
    assert out.coverage == 1.0 and out.unplaced == ()


def test_the_three_readings_of_a_wh_word_stay_apart(compiler):
    """Root asks · a noun-modifying clause describes · a complement clause asks without the
    utterance being a question. All three, in one test, because the risk is a fix that collapses
    them the other way."""
    asking = compiled(compiler, "when do you sleep ?")
    describing = compiled(compiler, "the cat that sleeps")
    embedded = compiled(compiler, "if you know who did it , tell me")

    assert Role.TIME in main_row(asking).boxes, "the root clause ASKS: a box is opened"
    assert isinstance(main_row(asking).boxes[Role.TIME].head, Open)

    sleeps = next(r for r in describing.zip.rows if getattr(r, "predicate", None) == "sleep.v")
    assert isinstance(sleeps.boxes[Role.AGENT].head, Var), "the relative BINDS, it does not open"

    did = next(r for r in embedded.zip.rows if getattr(r, "predicate", None) == "do.v")
    assert isinstance(did.boxes[Role.AGENT].head, Open), "the embedded one asks"
    assert all(c == 1.0 for c in (asking.coverage, describing.coverage, embedded.coverage))


def test_UNASSERTION_PROPAGATES_into_an_enclosed_clause(compiler):
    """**«if you know WHO DID IT, tell me» does not assert that anybody did it.** The whole antecedent
    is supposed, and a clause inside it is inside the supposition.

    It was a TRUTH error and therefore the worst kind: the `ccomp` was joined by an AND that claimed
    its operand while the other half of the same conditional was explicitly not claimed.

    **THE SHAPE MOVED ON 2026-09-20 AND THE PROPERTY DID NOT.** A bare `ccomp` is now an ATTITUDE
    whatever its verb — `that` is optional and cannot change what is asserted — so «who did it» sits
    under «you know» instead of beside it. Its truth is 1.0, and that is the 2026-09-17 ruling
    working: under an attitude the truth slot says what the HOLDER does with the row, and the prefix
    is what keeps it out of the world. What must still hold is the thing this test was written for —
    **nothing reaches the world** — so the row that carries the attitude is unasserted, and every
    content row outside one is too.
    """
    out = compiled(compiler, "if you know who did it , tell me")
    content = [r for r in out.zip.rows if r.kind == "content"]
    under_attitude = {r.scopes for r in out.zip.rows if r.kind == "attitude"}
    holders = {r.name for r in content if r.predicate in {"know.v"}}

    loose = [r for r in content if r.name not in under_attitude]
    assert all(r.truth is None for r in loose), f"claimed: {[r.name for r in loose if r.truth]}"
    assert holders and all(out_row.truth is None for out_row in content
                           if out_row.name in holders), (
        "the KNOWING is supposed, so nothing under it reaches the world either")
    assert [r.truth for r in out.zip.rows if r.kind == "join"] == [1.0], "the JOIN is claimed"


def test_a_compiled_form_does_not_ALSO_abstain(compiler):
    """A report that cries wolf is worse than no report. `if` was in the abstention list of a
    sentence whose IMPLY it had built, because the per-clause walk met it before `_relate` ran."""
    out = compiled(compiler, "if you know who did it , tell me")

    assert out.abstained == (), f"spurious: {out.abstained}"
    assert any(r.kind == "join" and r.operator is Operator.IMPLY for r in out.zip.rows)
    assert compiled(compiler, "the cat that sleeps").abstained == ()


def test_a_word_the_station_cannot_place_is_VISIBLE(compiler):
    """Req 21: material no box fits is RECORDED, never given a position it did not earn — and never
    silently dropped either.

    The example has moved TWICE, and each move is the same honesty: point it at something still
    unhandled rather than keep asserting a limitation that has been lifted. It was «the cat that
    sleeps» until relative clauses compiled, then «if you know who did it» until embedded questions
    did. It is now `xcomp`, which is not a gap but a RULING — «you like TO SWIM» is one predication
    and nobody asserts that you swim — so what the zip reports is that the ruling has no compiled
    consequence yet."""
    out = compiled(compiler, "he says that you like to swim")

    assert out.unplaced, "the xcomp's own verb is not a row, and the zip says so"
    assert set(out.unplaced) <= set(case("he says that you like to swim").skeleton.tokens)
    assert out.zip.unplaced == list(out.unplaced)
    assert 0.0 < out.coverage < 1.0, "partial, and honestly so"


def test_an_ambiguous_marker_is_settled_and_says_how(compiler):
    """«I swam IN the pool» reads location|time|instrument|manner, and `db/0012` says what chooses.

    It was an ABSTENTION until 2026-09-16, on the reading that picking a candidate would be the
    silently-complete nearest fit req 8 forbids — and the operative word was SILENTLY. Nothing
    fires here, so the curation's best-first default stands, and the zip RECORDS that it was a
    default. A counted default is not a silent one.
    """
    out = compiled(compiler, "Last night , I swam in the pool")

    row = main_row(out)
    assert row.boxes[Role.LOCATION].head == "pool.n"
    assert row.boxes[Role.LOCATION].marker == "in", "req 65: the marker the speaker chose is kept"
    assert any("in pool" in note for note in out.defaulted), "and it says nothing chose"
    # «LAST night» — the adjective raises a binder (req 70), so the TIME box holds the VARIABLE and
    # the noun moves into the binder's restriction. That indirection is the point of req 36.
    binder = next(r for r in out.zip.rows if r.kind == "quantifier")
    assert row.boxes[Role.TIME].head == Var(name=binder.binds), "what it DID know is still bound"
    assert binder.restriction.head == "night.n"


def test_a_supersense_settles_a_marker_and_that_is_not_a_default(compiler):
    """«I talked TO my friend» is a RECIPIENT and «I walk TO the station» a destination, and the two
    differ only in what kind of thing the nominal is. A rule fired, so nothing is defaulted."""
    out = compiled(compiler, "I talked to my friend in the park")

    row = main_row(out)
    assert row.boxes[Role.RECIPIENT].head == "friend.n"
    assert not any("to friend" in note for note in out.defaulted), "a person is not a guess"
    assert out.coverage == 1.0


def test_a_multiword_marker_covers_every_token_it_spans(compiler):
    """«out OF the box» is one form, and `of` hangs off `out` as UD's `fixed`. Marking only the
    first token left `of` looking unplaced in a sentence that was fully understood."""
    out = compiled(compiler, "out of the box")

    assert out.coverage == 1.0 and out.unplaced == ()
    assert out.zip.rows[0].boxes[Role.SOURCE].marker == "out of"


def test_a_marked_ROOT_takes_its_markers_role_and_not_the_default(compiler):
    """«out of the box» is a SOURCE the speaker said out loud. A non-verb root defaulted to
    `complement`, which kept the marker's SPELLING and threw its MEANING into the default — a zip
    that reads as understood and is not. The gate caught it the day it started scoring the zip.

    **The copula is the exception, and by construction**: in «Sue is a teacher» the root IS the
    complement (req 31), so there the marker does not get to override.
    """
    out = compiled(compiler, "out of the box")
    assert Role.SOURCE in out.zip.rows[0].boxes
    assert Role.COMPLEMENT not in out.zip.rows[0].boxes

    copular = compiled(compiler, "Sue is a teacher")
    assert Role.COMPLEMENT in copular.zip.rows[0].boxes


def test_an_nmod_under_a_noun_is_a_possessor_ONLY_IF_ITS_MARKER_SAYS_SO(compiler):
    """«the office OF the Chair» is a possessor; «the cafe UP BESIDE the lookout» is a LOCATION, and
    reading the second as a possessor said the cafe belonged to the lookout.

    **And the marker is ASKED, never listed**: `'s` compiles to `field: relation` and `db/0012` gives
    `of` the rule «head is a NOUN → relation», so a `{"of", "'s"}` in Python would be a hand list in
    the one file whose purpose is to end them — the Captain's frame-or-knowledge rule, 2026-09-16.
    """
    possessor = compiled(compiler, "the office of the Chair")
    assert possessor.zip.rows[0].boxes[Role.COMPLEMENT].relation == "chair.n"

    located = compiled(compiler, "The cafe up beside the lookout")
    assert located.zip.rows[0].boxes[Role.LOCATION].head == "lookout.n"
    assert located.zip.rows[0].boxes[Role.COMPLEMENT].relation is None, "the cafe owns no lookout"


def test_every_covered_token_says_WHERE_it_went(compiler):
    """`Compiled.placement` — the trace the zip-level gate needed and req 4's confidence will read.

    A covered token with no label is "counted as understood without saying what it became", and that
    is what the trace exists to make impossible: three UD cases reported `of`, `'s` and `beside` as
    never reaching the zip, in sentences that compiled at 100% coverage.
    """
    out = compiled(compiler, "the office of the Chair")

    assert set(out.placement) == set(out.covered)
    assert all(out.placement.values()), f"unlabelled: {[k for k, v in out.placement.items() if not v]}"
    assert out.placement[2] == "field:relation", "`of` marked the possessor FIELD, not a box"


def test_every_case_produces_a_valid_zip(compiler):
    """The schema is FRAME and validates on construction: a zip that exists is a zip that is legal.
    What this adds is that NONE of the corpus crashes the compiler."""
    for ud_case in CASES:
        out = compiler.compile(ud_case.skeleton)
        assert out.zip.rows, f"{ud_case.text!r} produced no rows"
        assert out.zip.schema_version == SCHEMA_VERSION


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
    join. The saying is claimed; the swimming is not, and nothing in the zip says it is.

    **AND THE SAYING'S OWN CLAUSE DISSOLVES INTO THE ATTITUDE ROW** *(2026-09-20)*. The verb, its
    holder and its addressee are all on the prefix row, so a content row beside it saying the same
    thing is one thinking written down twice — which the decompiler duly spoke twice: «He says. He
    says that you swim.» Found by the fixpoint, `tools/roundtrip.py --fixpoint`.
    """
    out = compiler.compile(SAYS)
    attitude = rows_of(out, "attitude")[0]
    swimming = next(r for r in rows_of(out, "content") if r.predicate == "swim.v")

    assert attitude.verb == "say.v"
    assert attitude.scopes == swimming.name
    assert not [r for r in rows_of(out, "content") if r.predicate == "say.v"], (
        "the saying is the attitude row, and it is not also a claim beside it")
    assert swimming.truth == 1.0, (
        "the HOLDER claims it; the attitude row is what keeps it out of the world (2026-09-17)")
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




# ------------------------------------------------------------------------------------------------
# WH-WORDS — «a question is something OPEN», and five kinds of open
# ------------------------------------------------------------------------------------------------

WHEN = skeleton_from_conllu("When do you sleep ?", [
    ("1", "When", "when", "ADV", "4", "advmod"),
    ("2", "do", "do", "AUX", "4", "aux"),
    ("3", "you", "you", "PRON", "4", "nsubj"),
    ("4", "sleep", "sleep", "VERB", "0", "root"),
    ("5", "?", "?", "PUNCT", "4", "punct"),
])

WHO = skeleton_from_conllu("Who sleeps ?", [
    ("1", "Who", "who", "PRON", "2", "nsubj"),
    ("2", "sleeps", "sleep", "VERB", "0", "root"),
    ("3", "?", "?", "PUNCT", "2", "punct"),
])

WHAT = skeleton_from_conllu("What did you eat ?", [
    ("1", "What", "what", "PRON", "4", "obj"),
    ("2", "did", "do", "AUX", "4", "aux"),
    ("3", "you", "you", "PRON", "4", "nsubj"),
    ("4", "eat", "eat", "VERB", "0", "root"),
    ("5", "?", "?", "PUNCT", "4", "punct"),
])

WHY = skeleton_from_conllu("Why do you sleep ?", [
    ("1", "Why", "why", "ADV", "4", "advmod"),
    ("2", "do", "do", "AUX", "4", "aux"),
    ("3", "you", "you", "PRON", "4", "nsubj"),
    ("4", "sleep", "sleep", "VERB", "0", "root"),
    ("5", "?", "?", "PUNCT", "4", "punct"),
])

WHOSE = skeleton_from_conllu("Whose cat sleeps ?", [
    ("1", "Whose", "whose", "PRON", "2", "nmod:poss"),
    ("2", "cat", "cat", "NOUN", "3", "nsubj"),
    ("3", "sleeps", "sleep", "VERB", "0", "root"),
    ("4", "?", "?", "PUNCT", "3", "punct"),
])

#: «The cat who sleeps is mine» — the SAME `who`, describing rather than asking.
WHO_RELATIVE = skeleton_from_conllu("The cat who sleeps is mine .", [
    ("1", "The", "the", "DET", "2", "det"),
    ("2", "cat", "cat", "NOUN", "6", "nsubj"),
    ("3", "who", "who", "PRON", "4", "nsubj"),
    ("4", "sleeps", "sleep", "VERB", "2", "acl:relcl"),
    ("5", "is", "be", "AUX", "6", "cop"),
    ("6", "mine", "mine", "PRON", "0", "root"),
    ("7", ".", ".", "PUNCT", "6", "punct"),
])


def test_a_wh_word_OPENS_the_box_it_asks_about(compiler):
    """«There is no mood field» (E2): a question IS something open. «When do you sleep?» is the same
    row as «you sleep», with the TIME box open instead of absent."""
    out = compiler.compile(WHEN)
    row = main_row(out)

    assert isinstance(row.boxes[Role.TIME].head, Open)
    assert row.predicate == "sleep.v"
    assert out.coverage == 1.0


def test_a_participant_question_takes_its_role_from_the_RELATION(compiler):
    """`who` and `what` name no role — the dependency does, exactly as it does for every other
    nominal (req 12). A role written in the row would be a third place the same fact lives."""
    who, what = compiler.compile(WHO), compiler.compile(WHAT)

    assert isinstance(who.zip.rows[-1].boxes[Role.AGENT].head, Open), "nsubj -> agent"
    assert isinstance(what.zip.rows[-1].boxes[Role.PATIENT].head, Open), "obj -> patient"
    assert who.coverage == what.coverage == 1.0


def test_WHY_asks_for_an_ANTECEDENT_because_there_is_no_cause_box(compiler):
    """REQ 37, PAYING FOR ITSELF. There is no CAUSE relation — a cause is IMPLY read with the
    theatre's arrow — so «why do you sleep?» cannot open a cause box. It asks for an unknown ROW
    implying the one that was asserted, and the format already had that shape."""
    out = compiler.compile(WHY)
    asked = next(r for r in rows_of(out, "content") if r.predicate == "sleep.v")
    unknown = next(r for r in rows_of(out, "content") if r is not asked)
    join = rows_of(out, "join")[0]

    assert isinstance(unknown.predicate, Open) and not unknown.boxes, "wholly open"
    assert join.operator is Operator.IMPLY
    assert join.operands == [unknown.name, asked.name], "the unknown implies the claim"
    assert asked.truth == 1.0, "the sleeping is asserted; only its antecedent is asked"


def test_WHOSE_opens_the_possessor_FIELD_and_adds_no_box(compiler):
    """The possessor lives inside the record (req 26), so asking about it opens a field."""
    out = compiler.compile(WHOSE)
    box = main_row(out).boxes[Role.AGENT]

    assert box.head == "cat.n"
    assert isinstance(box.relation, Open)
    assert out.coverage == 1.0


def test_the_SAME_word_asks_in_a_root_clause_and_describes_in_a_relative_one(compiler):
    """tk1's R5, deciding a question the dependency cannot: «WHO sleeps» and «the cat WHO sleeps»
    are both `nsubj` of their own clause, and only the clause's own attachment separates them."""
    asking = compiler.compile(WHO).zip.rows[-1]
    describing = compiler.compile(WHO_RELATIVE)

    assert isinstance(asking.boxes[Role.AGENT].head, Open), "a question: the agent is asked"

    sleeping = next(r for r in rows_of(describing, "content") if r.predicate == "sleep.v")
    assert isinstance(sleeping.boxes[Role.AGENT].head, Var), "a description: the agent is the cat"
    assert describing.coverage == 1.0


def test_copular_be_as_ROOT_still_earns_no_predicate(compiler):
    """«Where is the cat?» has `be` as its root because there is no other verb, and it is still glue
    (req 31): the question is a LOCATION box on a row about the cat."""
    out = compiler.compile(skeleton_from_conllu("Where is the cat ?", [
        ("1", "Where", "where", "ADV", "2", "advmod"),
        ("2", "is", "be", "AUX", "0", "root"),
        ("3", "the", "the", "DET", "4", "det"),
        ("4", "cat", "cat", "NOUN", "2", "nsubj"),
        ("5", "?", "?", "PUNCT", "2", "punct"),
    ]))
    row = main_row(out)

    assert row.predicate is None, "no `be.v`, and certainly no `be.n`"
    assert isinstance(row.boxes[Role.LOCATION].head, Open)
    assert row.boxes[Role.PATIENT].head == "cat.n", "patient, not topic — the drill settles it"


def test_existential_be_IS_content_and_keeps_its_predicate(compiler):
    """Req 31 names the exception: «there is a cat» is content, not glue. The expletive is what
    separates it from the copular reading."""
    out = compiler.compile(skeleton_from_conllu("There is a cat .", [
        ("1", "There", "there", "PRON", "2", "expl"),
        ("2", "is", "be", "AUX", "0", "root"),
        ("3", "a", "a", "DET", "4", "det"),
        ("4", "cat", "cat", "NOUN", "2", "nsubj"),
        ("5", ".", ".", "PUNCT", "2", "punct"),
    ]))

    assert main_row(out).predicate == "be.v", "content, and a VERB key"


def test_the_RATCHET_half_of_the_corpus_never_gets_worse(compiler):
    """The 25 cases that existed before the corpus reached all 37 relations: **24 whole, 99.4%.**

    **The floor is stated in TWO HALVES on purpose.** On 2026-09-16 the corpus grew from 16 relations
    to 37, and the eighteen new cases are the hard ones by construction — everything easy had already
    been transcribed. One averaged figure over the whole corpus would let a real regression on these
    twenty-five be paid for by a lucky gain on the frontier, which is the shape of a number that
    stops measuring.
    """
    scored = [compiler.compile(c.skeleton) for c in ratchet()]
    full = sum(1 for s in scored if s.coverage == 1.0)
    mean = sum(s.coverage for s in scored) / len(scored)

    assert len(scored) == 25
    assert full >= 23, f"{full} of {len(scored)} whole; 23 were on 2026-09-16"
    assert mean >= 0.98, f"mean {mean:.1%}; it was 98.9% on 2026-09-16"


def test_the_FRONTIER_half_is_where_the_work_is(compiler):
    """The relations the corpus reached on 2026-09-16: **11 of 20 whole, 84.6% mean.**

    Low, and honestly so. What is missing is NAMED rather than averaged away — `flat`/`list` (one
    name across several tokens — E3b), `xcomp` (deliberately not a clause, and what it IS instead is
    unruled), `nummod` (the box's own `count` field), `appos`, and the gapped `orphan`, which stanza
    does not label at all.
    """
    scored = [compiler.compile(c.skeleton) for c in frontier()]
    full = sum(1 for s in scored if s.coverage == 1.0)
    mean = sum(s.coverage for s in scored) / len(scored)

    assert len(scored) >= 20, "a relation may gain a case; the frontier grows and the ratchet does not"
    assert full >= 11, f"{full} of {len(scored)} whole; 11 were on 2026-09-16"
    assert mean >= 0.84, f"mean {mean:.1%}; it was 84.6% on 2026-09-16"


# ------------------------------------------------------------------------------------------------
# attributive adjectives — tkzip req 70
# ------------------------------------------------------------------------------------------------


def test_an_attributive_adjective_is_a_SECOND_ROW(compiler):
    """Req 70: «a human body» is ∃B(body(B) ∧ human(B)) — the same machinery as the depictive, and
    NOT a field on the box. The shape is the drill's own, hand-compiled at E2.

    The adjective row has **no predicate** (req 31: cat + cute, no verb) and its subject is the
    **patient** (the copular row's shape). The binder scopes the **JOIN**, not either row, because
    the variable lives in both and a binder over one would leave the other's variable unbound.
    """
    out = compiled(compiler, "Sam eats large hot dogs")
    binder = out.zip.rows[0]
    content = next(r for r in out.zip.rows if getattr(r, "predicate", None) == "eat.v")
    adjectives = [r for r in out.zip.rows if r.kind == "content" and r.name.startswith("m")]
    joins = [r for r in out.zip.rows if r.kind == "join"]

    assert binder.kind == "quantifier"
    assert binder.restriction.head == "dog.n", "the variable is restricted to the NOUN"
    assert content.boxes[Role.PATIENT].head == Var(name=binder.binds), "the box holds the VARIABLE"

    assert [r.boxes[Role.COMPLEMENT].head for r in adjectives] == ["large.a", "hot.a"]
    assert all(r.predicate is None for r in adjectives), "cat + cute, no verb"
    assert all(r.boxes[Role.PATIENT].head == Var(name=binder.binds) for r in adjectives)

    assert [j.operator for j in joins] == [Operator.AND, Operator.AND]
    assert binder.scopes == joins[-1].name, "the binder scopes the JOIN, not either row"
    assert out.coverage == 1.0


def test_two_adjectives_CHAIN_their_joins(compiler):
    """«large hot dogs» is AND(large, AND(hot, eats)) — one join apiece, exactly as the drill chains
    j1, j2, j3. A single join with three operands would not be a binary operator."""
    out = compiled(compiler, "Sam eats large hot dogs")
    joins = [r for r in out.zip.rows if r.kind == "join"]

    assert joins[0].operands == ["m0", "r0"]
    assert joins[1].operands == ["m1", "j0"], "the second adjective joins the growing conjunction"
    assert all(len(j.operands) == 2 for j in joins)


# ------------------------------------------------------------------------------------------------
# adverbs — requirement 23's four scopes
# ------------------------------------------------------------------------------------------------


def test_a_circumstantial_adverb_fills_its_own_box(compiler):
    """«left EARLY in the morning» — `early` is a TIME, and it is its own filler: there is no nominal
    under it, so the head is the adverb's own key."""
    out = compiled(compiler, "The guy , John said , left early in the morning")
    row = next(r for r in out.zip.rows if getattr(r, "predicate", None) == "leave.v")

    assert row.boxes[Role.TIME].head in ("early.r", "morning.n")
    assert out.coverage == 1.0


def test_a_MARKED_nominal_outranks_a_bare_adverb_for_the_same_box(compiler):
    """«left EARLY in the MORNING» has two time expressions and one time box. The speaker CHOSE the
    marker on «in the morning», so it is the stronger evidence — and placing adverbs in token order
    let `early` take the box and pushed `morning` out, which is the same coverage and the worse
    reading. Adverbs are therefore placed after the nominals of their clause."""
    out = compiled(compiler, "The guy , John said , left early in the morning")
    row = next(r for r in out.zip.rows if getattr(r, "predicate", None) == "leave.v")

    assert row.boxes[Role.TIME].head == "morning.n", "the marked one won"
    assert out.unplaced == (), "and the adverb is still accounted for"


def test_a_referential_adverb_fills_a_box_with_an_OPEN_head(compiler):
    """«They come HERE» — closed classes v7 gave the row its box. The head stays OPEN because the
    form is INDEXICAL and context resolves it (req 7), exactly as a pronoun's does."""
    out = compiled(compiler, "They come here with out legal permission")
    row = main_row(out)

    assert isinstance(row.boxes[Role.LOCATION].head, Open), "not `here.r`"
    assert out.coverage == 1.0


# ------------------------------------------------------------------------------------------------
# numerals — the box's own `count` field
# ------------------------------------------------------------------------------------------------


def test_a_numeral_fills_COUNT_and_raises_no_binder(compiler):
    """Req 26: `quantity`, `count` and `determination` are three ORTHOGONAL fields — «the three cats»
    is definite AND counted. A numeral is not a quantifier: it does not bind, so it changes no scope
    and adds no row. It is a field of the record, exactly as the possessor is."""
    out = compiled(compiler, "Sam ate 3 sheep")
    box = main_row(out).boxes[Role.PATIENT]

    assert box.head == "sheep.n" and box.count == 3
    assert box.quantity is None, "a numeral is not a quantifier"
    assert not [r for r in out.zip.rows if r.kind == "quantifier"], "and it raises no binder"
    assert out.coverage == 1.0


def test_a_number_WORD_is_read_too(compiler):
    """«Sam spent forty dollars» — UD's own second nummod example, which arrived in the corpus
    ABSTAINING and got its dependency admitted the same day (`word2number`, on `nltk`'s terms: one
    door, and `numeral_value` is the door)."""
    out = compiled(compiler, "Sam spent forty dollars")
    box = main_row(out).boxes[Role.PATIENT]

    assert box.head == "dollar.n" and box.count == 40
    assert out.coverage == 1.0


def test_what_the_numeral_reader_REFUSES(compiler):
    """The refusals are the interesting half, and two of them are about not trusting the library.

    A comma or a space inside a digit string is a thousands separator in most of the world and a
    decimal point in some of it, so neither is stripped — `1,5` is not read at all rather than read
    as fifteen. And `word_to_num` returns **0** for some strings that are not numerals: a zero no
    word in the phrase asked for is the library shrugging, and a shrug is not a count.
    """
    from tk2.language.compile import numeral_value

    assert numeral_value("3") == 3
    assert numeral_value("", "17") == 17
    assert numeral_value("twenty-one") == 21, "a hyphen is spelling, not a separator"
    assert numeral_value("three hundred and four") == 304
    assert numeral_value("zero") == 0, "and a real zero survives the shrug guard"

    assert numeral_value("1,5") is None
    assert numeral_value("dollars") is None, "the library answers 0 here; the guard refuses it"
    assert numeral_value("sheep") is None
    assert numeral_value("") is None


def test_the_numeral_reader_never_stops_a_parse(compiler):
    """**ONE DOOR, AND ITS FAILURE IS AN ABSTENTION.** `word2number` is imported inside
    `numeral_value` and nowhere else, so a machine without the package still parses — only the count
    abstains. The import error is caught with the library's own raises, because all of them mean the
    same thing here and none may reach the caller."""
    import tk2.language.compile as mod

    assert "word2number" not in [n for n in dir(mod)], "not imported at module scope"
    assert "from word2number import w2n" in inspect.getsource(mod.numeral_value)
    assert "ImportError" in inspect.getsource(mod.numeral_value)


# ------------------------------------------------------------------------------------------------
# the polar question — req 21 (E3 task 2c). Skeletons are stanza's own parses, measured 2026-09-18.
# ------------------------------------------------------------------------------------------------

def _row(out, name):
    return next(r for r in out.zip.rows if r.name == name)


POLAR = skeleton_from_conllu("Is the cat hungry ?", [
    ("1", "Is", "be", "AUX", "4", "cop"),
    ("2", "the", "the", "DET", "3", "det"),
    ("3", "cat", "cat", "NOUN", "4", "nsubj"),
    ("4", "hungry", "hungry", "ADJ", "0", "root"),
    ("5", "?", "?", "PUNCT", "4", "punct"),
])

DECLARATIVE_QUESTION = skeleton_from_conllu("The cat is hungry ?", [
    ("1", "The", "the", "DET", "2", "det"),
    ("2", "cat", "cat", "NOUN", "4", "nsubj"),
    ("3", "is", "be", "AUX", "4", "cop"),
    ("4", "hungry", "hungry", "ADJ", "0", "root"),
    ("5", "?", "?", "PUNCT", "4", "punct"),
])

EXCLAMATION = skeleton_from_conllu("Is he tall !", [
    ("1", "Is", "be", "AUX", "3", "cop"),
    ("2", "he", "he", "PRON", "3", "nsubj"),
    ("3", "tall", "tall", "ADJ", "0", "root"),
    ("4", "!", "!", "PUNCT", "3", "punct"),
])

CLAIM_THEN_QUESTION = skeleton_from_conllu("I know you are tired , but is the cat hungry ?", [
    ("1", "I", "I", "PRON", "2", "nsubj"),
    ("2", "know", "know", "VERB", "0", "root"),
    ("3", "you", "you", "PRON", "5", "nsubj"),
    ("4", "are", "be", "AUX", "5", "cop"),
    ("5", "tired", "tired", "ADJ", "2", "ccomp"),
    ("6", ",", ",", "PUNCT", "11", "punct"),
    ("7", "but", "but", "CCONJ", "11", "cc"),
    ("8", "is", "be", "AUX", "11", "cop"),
    ("9", "the", "the", "DET", "10", "det"),
    ("10", "cat", "cat", "NOUN", "11", "nsubj"),
    ("11", "hungry", "hungry", "ADJ", "2", "conj"),
    ("12", "?", "?", "PUNCT", "2", "punct"),
])

QUOTED_QUESTION = skeleton_from_conllu('I asked : " Do you know the muffin man ? "', [
    ("1", "I", "I", "PRON", "2", "nsubj"),
    ("2", "asked", "ask", "VERB", "0", "root"),
    ("3", ":", ":", "PUNCT", "2", "punct"),
    ("4", '"', '"', "PUNCT", "2", "punct"),
    ("5", "Do", "do", "AUX", "7", "aux"),
    ("6", "you", "you", "PRON", "7", "nsubj"),
    ("7", "know", "know", "VERB", "2", "ccomp"),
    ("8", "the", "the", "DET", "10", "det"),
    ("9", "muffin", "muffin", "NOUN", "10", "compound"),
    ("10", "man", "man", "NOUN", "7", "obj"),
    ("11", "?", "?", "PUNCT", "2", "punct"),
    ("12", '"', '"', "PUNCT", "2", "punct"),
])

CONDITIONAL_QUESTION = skeleton_from_conllu("Will you stay if it rains ?", [
    ("1", "Will", "will", "AUX", "3", "aux"),
    ("2", "you", "you", "PRON", "3", "nsubj"),
    ("3", "stay", "stay", "VERB", "0", "root"),
    ("4", "if", "if", "SCONJ", "6", "mark"),
    ("5", "it", "it", "PRON", "6", "nsubj"),
    ("6", "rains", "rain", "VERB", "3", "advcl"),
    ("7", "?", "?", "PUNCT", "3", "punct"),
])

TAG_QUESTION = skeleton_from_conllu("The cat is hungry , is n't it ?", [
    ("1", "The", "the", "DET", "2", "det"),
    ("2", "cat", "cat", "NOUN", "4", "nsubj"),
    ("3", "is", "be", "AUX", "4", "cop"),
    ("4", "hungry", "hungry", "ADJ", "0", "root"),
    ("5", ",", ",", "PUNCT", "6", "punct"),
    ("6", "is", "be", "AUX", "4", "parataxis"),
    ("7", "n't", "not", "PART", "6", "advmod"),
    ("8", "it", "it", "PRON", "6", "nsubj"),
    ("9", "?", "?", "PUNCT", "4", "punct"),
])


def test_a_POLAR_question_opens_its_truth(compiler):
    """«Is the cat hungry?» — every box bound, and the TRUTH is what is asked (E2, tkzip req 48). It
    compiled at 1.0 until 2026-09-18: a question stored as a belief."""
    assert isinstance(main_row(compiler.compile(POLAR)).truth, Open)


def test_the_QUESTION_MARK_decides_and_the_word_order_does_not(compiler):
    """Req 21. «The cat is hungry?» has declarative syntax — stanza reads it correctly — and asks
    anyway; «Is he tall!» is inverted and asks nothing. `!` is not `?`."""
    assert isinstance(main_row(compiler.compile(DECLARATIVE_QUESTION)).truth, Open)
    assert main_row(compiler.compile(EXCLAMATION)).truth == 1.0


def test_a_question_belongs_to_the_STATEMENT_it_closes(compiler):
    """Stanza hangs the `?` on the ROOT, *know*. The question is the coordinate: the tiredness stays
    claimed, the hunger is asked, and the AND binding them is not claimed either."""
    out = compiler.compile(CLAIM_THEN_QUESTION)
    assert _row(out, "r0").truth == 1.0
    assert _row(out, "r1").truth == 1.0, "«you are tired» is still asserted"
    assert isinstance(_row(out, "r2").truth, Open)
    between = next(j for j in out.zip.rows if j.kind == "join" and "r2" in j.operands)
    assert isinstance(between.truth, Open), "«A, but B?» does not claim A-and-B"


def test_a_QUOTED_question_asks_while_the_saying_stays_claimed(compiler):
    """«I asked: "Do you know the muffin man?"» — the asking happened; the knowing is what was
    asked. A quote is a statement of its own (req 21).

    *The asking is the ATTITUDE ROW since 2026-09-20 — its clause dissolved into it — so what is
    claimed is read off the attitude, and what is asked off the row it scopes.*
    """
    out = compiler.compile(QUOTED_QUESTION)
    attitude = rows_of(out, "attitude")[0]
    assert attitude.verb == "ask.v"
    assert isinstance(_row(out, attitude.scopes).truth, Open)


def test_a_conditional_question_opens_the_JOIN_that_carries_the_claim(compiler):
    """«Will you stay if it rains?» claims neither half — the IMPLY carries the claim, so that is
    what the question opens. The halves stay unasserted rather than becoming questions."""
    out = compiler.compile(CONDITIONAL_QUESTION)
    imply = next(j for j in out.zip.rows if j.kind == "join")
    assert isinstance(imply.truth, Open)
    assert _row(out, "r0").truth is None and _row(out, "r1").truth is None


def test_a_WH_question_keeps_its_truth(compiler):
    """«When do you sleep?» asks WHEN. That you sleep stays claimed: a `?` closing a statement that
    already asks through its wh-word opens nothing more."""
    out = compiler.compile(WHEN)
    assert isinstance(main_row(out).boxes[Role.TIME].head, Open)
    assert main_row(out).truth == 1.0


def test_a_TAG_question_claims_and_then_asks(compiler):
    """«The cat is hungry, isn't it?» — the claim stands and the tag asks for its confirmation."""
    out = compiler.compile(TAG_QUESTION)
    assert _row(out, "r0").truth == 1.0
    assert isinstance(_row(out, "r1").truth, Open)


WONDER_WHETHER = skeleton_from_conllu("I wonder whether the cat is hungry .", [
    ("1", "I", "I", "PRON", "2", "nsubj"),
    ("2", "wonder", "wonder", "VERB", "0", "root"),
    ("3", "whether", "whether", "SCONJ", "7", "mark"),
    ("4", "the", "the", "DET", "5", "det"),
    ("5", "cat", "cat", "NOUN", "7", "nsubj"),
    ("6", "is", "be", "AUX", "7", "cop"),
    ("7", "hungry", "hungry", "ADJ", "2", "ccomp"),
    ("8", ".", ".", "PUNCT", "2", "punct"),
])

ASKED_IF = skeleton_from_conllu("I asked if the cat is hungry .", [
    ("1", "I", "I", "PRON", "2", "nsubj"),
    ("2", "asked", "ask", "VERB", "0", "root"),
    ("3", "if", "if", "SCONJ", "7", "mark"),
    ("4", "the", "the", "DET", "5", "det"),
    ("5", "cat", "cat", "NOUN", "7", "nsubj"),
    ("6", "is", "be", "AUX", "7", "cop"),
    ("7", "hungry", "hungry", "ADJ", "2", "ccomp"),
    ("8", ".", ".", "PUNCT", "2", "punct"),
])


@pytest.mark.parametrize("skeleton, verb", [(WONDER_WHETHER, "wonder.v"), (ASKED_IF, "ask.v")])
def test_WHETHER_and_IF_on_a_complement_ASK(compiler, skeleton, verb):
    """Req 21, and req 14 finally true. The word is `mark` whether it asks or supposes; the CLAUSE
    decides — a complement is asked, an `advcl` supposed. Until 2026-09-18 `mark` always read the
    subordinator row, and «I wonder whether the cat is hungry» was a CONDITIONAL."""
    out = compiler.compile(skeleton)
    attitude = next(r for r in out.zip.rows if r.kind == "attitude")
    assert attitude.verb == verb and attitude.scopes == "r1"
    assert not [r for r in rows_of(out, "content") if r.predicate == verb], (
        "the wondering IS the attitude row, and not also a claim beside it (2026-09-20)")
    assert isinstance(_row(out, "r1").truth, Open), "the hunger is what is asked"
    assert not [r for r in out.zip.rows if r.kind == "join"], "and it is not a conditional"


def test_IF_on_an_ADVERBIAL_clause_still_supposes(compiler):
    """The other reading of the same word, chosen by the same tree: «If it rains I stay home»."""
    out = compiler.compile(IF)
    assert next(r for r in out.zip.rows if r.kind == "join").operator == Operator.IMPLY
    assert not [r for r in out.zip.rows if r.kind == "content" and isinstance(r.truth, Open)]


# ------------------------------------------------------------------------------------------------
# the imperative — E3 task 2d. Stanza's `Mood=Imp` is added by hand: CoNLL-U here carries no FEATS.
# ------------------------------------------------------------------------------------------------

def _with_mood(skeleton, *indices):
    from dataclasses import replace as _replace
    words = tuple(_replace(w, feats={**w.feats, "Mood": "Imp"}) if w.index in indices else w
                  for w in skeleton.words)
    return _replace(skeleton, words=words)


CLOSE_THE_DOOR = _with_mood(skeleton_from_conllu("Close the door !", [
    ("1", "Close", "close", "VERB", "0", "root"),
    ("2", "the", "the", "DET", "3", "det"),
    ("3", "door", "door", "NOUN", "1", "obj"),
    ("4", "!", "!", "PUNCT", "1", "punct"),
]), 0)

BE_QUIET = _with_mood(skeleton_from_conllu("Be quiet !", [
    ("1", "Be", "be", "AUX", "2", "cop"),
    ("2", "quiet", "quiet", "ADJ", "0", "root"),
    ("3", "!", "!", "PUNCT", "2", "punct"),
]), 0)

GO_AND_SEE = _with_mood(skeleton_from_conllu("Go and see .", [
    ("1", "Go", "go", "VERB", "0", "root"),
    ("2", "and", "and", "CCONJ", "3", "cc"),
    ("3", "see", "see", "VERB", "1", "conj"),
    ("4", ".", ".", "PUNCT", "1", "punct"),
]), 0, 2)

HE_SAID_I_AM_LATE = skeleton_from_conllu('He said " I am late "', [
    ("1", "He", "he", "PRON", "2", "nsubj"),
    ("2", "said", "say", "VERB", "0", "root"),
    ("3", '"', '"', "PUNCT", "6", "punct"),
    ("4", "I", "I", "PRON", "6", "nsubj"),
    ("5", "am", "be", "AUX", "6", "cop"),
    ("6", "late", "late", "ADJ", "2", "ccomp"),
    ("7", '"', '"', "PUNCT", "6", "punct"),
])


def _speech():
    from tk2.language.utterance import Context
    return Context(speaker="me.n", addressee="you.n")


def test_the_IMPERATIVE_is_a_WANT_over_an_unstated_row(compiler):
    """«Close the door!» — the drill's `aw-21`, exactly: POV(me · want) over «close.v», agent = the
    addressee, and NOTHING CLAIMED. It compiled as «you close the door», stated, until 2026-09-18."""
    out = compiler.compile(CLOSE_THE_DOOR, _speech())
    want = next(r for r in out.zip.rows if r.kind == "attitude")
    row = _row(out, "r0")
    assert (want.verb, want.holder.head, want.scopes) == ("want.v", "me.n", "r0")
    assert row.truth is None, "wanted, not claimed"
    assert row.boxes[Role.AGENT].head == "you.n", "the understood subject is the addressee"
    assert want.strength == 0.9, "the drill's own number, and it comes from `db/0020`"


def test_how_strongly_an_imperative_wants_comes_from_THE_ROWS(compiler):
    """**Requirement 23, and the seam is the point.** The tree states no number; the Captain ruled
    the gradation «close the door» → «would you mind closing the door» KNOWLEDGE, so the compiler
    asks the table. Handed a table with no row it says NOTHING rather than a number of its own —
    half-understood is legal, wrongly-understood is not (req 8)."""
    from tk2.language.compile import Compiler
    from tk2.language.strength import AttitudeStrengths

    empty = Compiler(compiler.table, strengths=AttitudeStrengths({}, "a table with no rows"))
    silent = next(r for r in empty.compile(CLOSE_THE_DOOR, _speech()).zip.rows
                  if r.kind == "attitude")
    assert silent.strength is None

    louder = Compiler(compiler.table,
                      strengths=AttitudeStrengths({"imperative": {"strength": 0.4}}, "a curation"))
    softened = next(r for r in louder.compile(CLOSE_THE_DOOR, _speech()).zip.rows
                    if r.kind == "attitude")
    assert softened.strength == 0.4, "re-curating the number is a migration, not a code change"


def test_the_understood_subject_takes_the_box_a_subject_WOULD_have(compiler):
    """«Be quiet!» is copular, and a copular subject is `patient` (E2) — so the addressee is too.
    The mood is on the copula, not on the head."""
    row = _row(compiler.compile(BE_QUIET, _speech()), "r0")
    assert row.boxes[Role.PATIENT].head == "you.n"
    assert row.truth is None


def test_a_JOIN_of_wants_claims_nothing(compiler):
    """«Go and see» — two wants; the AND between them, left claimed, asserted that you go and see."""
    out = compiler.compile(GO_AND_SEE, _speech())
    assert len([r for r in out.zip.rows if r.kind == "attitude"]) == 2
    assert next(r for r in out.zip.rows if r.kind == "join").truth is None


def test_a_holder_the_station_cannot_name_is_SOMEBODY_not_the_narrator(compiler):
    """«He said "I am late"» — `he` is anaphora and cannot be named from the speech act, so the
    quoted «I» is somebody OPEN. Falling back to the outer speaker made the NARRATOR late. Found
    2026-09-18 by the imperative, on «He said: "Close the door!"»."""
    out = compiler.compile(HE_SAID_I_AM_LATE, _speech())
    late = next(r for r in out.zip.rows if r.kind == "content" and r.name != "r0")
    assert isinstance(late.boxes[Role.PATIENT].head, Open), "somebody — never `me.n`"


# ------------------------------------------------------------------------------------------------
# a disjunction claims the disjunction — `db/0017`, the Captain's ruling (b), 2026-09-18
# ------------------------------------------------------------------------------------------------

HUNGRY_OR_TIRED = skeleton_from_conllu("The cat is hungry or tired .", [
    ("1", "The", "the", "DET", "2", "det"),
    ("2", "cat", "cat", "NOUN", "4", "nsubj"),
    ("3", "is", "be", "AUX", "4", "cop"),
    ("4", "hungry", "hungry", "ADJ", "0", "root"),
    ("5", "or", "or", "CCONJ", "6", "cc"),
    ("6", "tired", "tired", "ADJ", "4", "conj"),
    ("7", ".", ".", "PUNCT", "4", "punct"),
])

HUNGRY_NOR_TIRED = skeleton_from_conllu("The cat is hungry nor tired .", [
    ("1", "The", "the", "DET", "2", "det"),
    ("2", "cat", "cat", "NOUN", "4", "nsubj"),
    ("3", "is", "be", "AUX", "4", "cop"),
    ("4", "hungry", "hungry", "ADJ", "0", "root"),
    ("5", "nor", "nor", "CCONJ", "6", "cc"),
    ("6", "tired", "tired", "ADJ", "4", "conj"),
    ("7", ".", ".", "PUNCT", "4", "punct"),
])


@pytest.mark.parametrize("skeleton, operator", [(HUNGRY_OR_TIRED, Operator.OR),
                                                (HUNGRY_NOR_TIRED, Operator.NOR)])
def test_a_DISJUNCTION_claims_the_join_and_neither_half(compiler, skeleton, operator):
    """«hungry or tired» does not tell you it is hungry; «neither hungry nor tired» claimed both
    halves AND that neither holds — a zip that contradicted itself. The halves are stated, the join
    is the claim: the shape `if` has had since `db/0010`."""
    out = compiler.compile(skeleton)
    join = next(r for r in out.zip.rows if r.kind == "join")
    assert join.operator == operator and join.truth == 1.0
    assert _row(out, "r0").truth is None and _row(out, "r1").truth is None


def _tea_or_coffee(text, question=False):
    """«You can have tea or you can have coffee» — stanza's parse, measured 2026-09-18."""
    rows = [
        ("1", "You", "you", "PRON", "3", "nsubj"),
        ("2", "can", "can", "AUX", "3", "aux"),
        ("3", "have", "have", "VERB", "0", "root"),
        ("4", "tea", "tea", "NOUN", "3", "obj"),
        ("5", "or", "or", "CCONJ", "8", "cc"),
        ("6", "you", "you", "PRON", "8", "nsubj"),
        ("7", "can", "can", "AUX", "8", "aux"),
        ("8", "have", "have", "VERB", "3", "conj"),
        ("9", "coffee", "coffee", "NOUN", "8", "obj"),
        ("10", "?" if question else ".", "?" if question else ".", "PUNCT", "3", "punct"),
    ]
    return skeleton_from_conllu(text, rows)


def test_FREE_CHOICE_under_a_modal_claims_both_halves(compiler):
    """The Captain's ruling (b), 2026-09-18: «you CAN have tea or you CAN have coffee» means both
    are possible. `or` alone claims only the join (`db/0017`); under a possibility modal on both
    halves, the halves are claimed too."""
    out = compiler.compile(_tea_or_coffee("You can have tea or you can have coffee ."))
    assert _row(out, "r0").truth == 1.0 and _row(out, "r1").truth == 1.0
    assert next(r for r in out.zip.rows if r.kind == "join").truth == 1.0


def test_an_ASKED_free_choice_claims_neither_half(compiler):
    """«Can you have tea or can you have coffee?» — the halves were claimed only through the
    disjunction, so asking the disjunction asks them too."""
    out = compiler.compile(_tea_or_coffee("You can have tea or you can have coffee ?", question=True))
    assert isinstance(_row(out, "r0").truth, Open) and isinstance(_row(out, "r1").truth, Open)


# ------------------------------------------------------------------------------------------------
# the subject's role — req 22, `db/0018`. Skeletons are stanza's parses, measured 2026-09-18.
# ------------------------------------------------------------------------------------------------

def _svo(text, subject, verb, lemma, obj=None):
    rows = [("1", subject, subject.lower(), "PRON" if subject in ("I", "You") else "PROPN", "2", "nsubj"),
            ("2", verb, lemma, "VERB", "0", "root")]
    if obj:
        rows.append(("3", obj[0], obj[1], "NOUN", "2", "obj"))
    return skeleton_from_conllu(text, rows)


@pytest.mark.parametrize("text, verb, lemma, role", [
    ("God exists", "exists", "exist", Role.PATIENT),            # verb.stative — one shape with «there is»
    ("I love", "love", "love", Role.EXPERIENCER),                # verb.emotion
    ("I understand", "understand", "understand", Role.EXPERIENCER),   # verb.cognition
    ("I disagree", "disagree", "disagree", Role.EXPERIENCER),    # the exception row: a held position
    ("I walk", "walk", "walk", Role.AGENT),                      # the default
])
def test_the_SUBJECT_is_what_its_predicate_makes_it(compiler, text, verb, lemma, role):
    subject = text.split()[0]
    out = compiler.compile(_svo(text, subject, verb, lemma), _speech())
    assert role in main_row(out).boxes, f"{text!r}: the subject should be {role.value}"


def test_a_TRANSITIVE_clause_keeps_its_patient_for_the_object(compiler):
    """«Sam spent forty dollars» — `spend`'s primary sense is stative («pass time»), which would make
    Sam the patient and push the dollars out. The relation outranks the rule (req 12)."""
    out = compiler.compile(_svo("Sam spent money", "Sam", "spent", "spend", obj=("money", "money")))
    row = main_row(out)
    assert row.boxes[Role.AGENT].head == "sam.n"
    assert row.boxes[Role.PATIENT].head == "money.n"


@pytest.mark.parametrize("adjective, role", [
    ("hungry", Role.EXPERIENCER), ("green", Role.PATIENT),
    # **THE RESOURCE IS OF TWO MINDS ABOUT THESE THREE** (2026-09-19, `db/0019`). `dead` and `alive`
    # are filed under noun.state AND noun.attribute, so the reader abstains and the copular default
    # stands — which is what the drill hand-compiled anyway. `happy` is noun.state AND noun.feeling,
    # and `noun.feeling` cannot enter the rule («Be QUIET!»), so a LEMMA ROW settles it.
    ("dead", Role.PATIENT), ("alive", Role.PATIENT), ("happy", Role.EXPERIENCER),
])
def test_a_copular_ADJECTIVE_is_read_through_its_noun(compiler, adjective, role):
    """WordNet files almost every adjective under `adj.all`; the noun it measures is what speaks —
    *hunger* is `noun.state`, *greenness* `noun.attribute`."""
    out = compiler.compile(skeleton_from_conllu(f"The cat is {adjective} .", [
        ("1", "The", "the", "DET", "2", "det"),
        ("2", "cat", "cat", "NOUN", "4", "nsubj"),
        ("3", "is", "be", "AUX", "4", "cop"),
        ("4", adjective, adjective, "ADJ", "0", "root"),
        ("5", ".", ".", "PUNCT", "4", "punct"),
    ]))
    assert main_row(out).boxes[role].head == "cat.n"
