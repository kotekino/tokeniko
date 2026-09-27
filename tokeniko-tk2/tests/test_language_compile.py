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

    *Amended 2026-09-26 (`E3.3.11.1` · `E3.3.11.2`, the Captain's `E3.3.11.2.16` (2))*: «if you
    know who did it» SUPPOSES the knowing, and an attitude row has no truth slot to suppose it in —
    so that sentence is withheld whole, and the property is pinned on `dere-4`'s claimed knowing.
    """
    out = compiler.compile(I_DO_NOT_KNOW_WHO)
    ate = next(r for r in out.zip.rows if getattr(r, "predicate", None) == "eat.v")

    assert isinstance(ate.boxes[Role.AGENT].head, Open), "`who` opens the agent slot"
    assert out.coverage == 1.0 and out.unplaced == ()
    assert not [r for r in out.zip.rows if isinstance(getattr(r, "truth", None), Open)], (
        "and the utterance is not a question")

    supposed = compiled(compiler, "if you know who did it , tell me")
    assert _claims(supposed) == [] and any("SUPPOSED" in why for why in supposed.abstained)


def test_the_three_readings_of_a_wh_word_stay_apart(compiler):
    """Root asks · a noun-modifying clause describes · a complement clause asks without the
    utterance being a question. All three, in one test, because the risk is a fix that collapses
    them the other way."""
    asking = compiled(compiler, "when do you sleep ?")
    describing = compiled(compiler, "the cat that sleeps")
    # Amended 2026-09-26 (E3.3.11.2.16 (2)): the supposed «if you know who did it» is withheld; the
    # complement clause that asks is `dere-4`'s, under a claimed knowing.
    embedded = compiler.compile(I_DO_NOT_KNOW_WHO)

    assert Role.TIME in main_row(asking).boxes, "the root clause ASKS: a box is opened"
    assert isinstance(main_row(asking).boxes[Role.TIME].head, Open)

    sleeps = next(r for r in describing.zip.rows if getattr(r, "predicate", None) == "sleep.v")
    assert isinstance(sleeps.boxes[Role.AGENT].head, Var), "the relative BINDS, it does not open"

    ate = next(r for r in embedded.zip.rows if getattr(r, "predicate", None) == "eat.v")
    assert isinstance(ate.boxes[Role.AGENT].head, Open), "the embedded one asks"
    assert all(c == 1.0 for c in (asking.coverage, describing.coverage, embedded.coverage))


#: dere-4 as stanza parses it: `who` is `nsubj` of a `ccomp` — an EMBEDDED question.
I_DO_NOT_KNOW_WHO = skeleton_from_conllu("I do n't know who ate the fish .", [
    ("1", "I", "i", "PRON", "4", "nsubj"),
    ("2", "do", "do", "AUX", "4", "aux"),
    ("3", "n't", "not", "PART", "4", "advmod"),
    ("4", "know", "know", "VERB", "0", "root"),
    ("5", "who", "who", "PRON", "6", "nsubj"),
    ("6", "ate", "eat", "VERB", "4", "ccomp"),
    ("7", "the", "the", "DET", "8", "det"),
    ("8", "fish", "fish", "NOUN", "6", "obj"),
    ("9", ".", ".", "PUNCT", "4", "punct"),
])

#: t-ng-4 as stanza parses it: the answering «No» is `INTJ` under `discourse`.
NO_SOME_SOFTWARE = skeleton_from_conllu("No , some software is a mind and some is not .", [
    ("1", "No", "no", "INTJ", "7", "discourse"),
    ("2", ",", ",", "PUNCT", "7", "punct"),
    ("3", "some", "some", "DET", "4", "det"),
    ("4", "software", "software", "NOUN", "7", "nsubj"),
    ("5", "is", "be", "AUX", "7", "cop"),
    ("6", "a", "a", "DET", "7", "det"),
    ("7", "mind", "mind", "NOUN", "0", "root"),
    ("8", "and", "and", "CCONJ", "10", "cc"),
    ("9", "some", "some", "DET", "10", "nsubj"),
    ("10", "is", "be", "AUX", "7", "conj"),
    ("11", "not", "not", "PART", "10", "advmod"),
    ("12", ".", ".", "PUNCT", "7", "punct"),
])


def test_an_embedded_WHO_is_settled_by_its_clause_when_the_relation_cannot(compiler):
    """dere-4, «I do not know WHO ate the fishes». `nsubj` admits the interrogative AND the relative,
    and since 2026-09-24 nothing picks between them by order — the CLAUSE does, and a complement
    clause asks. Refusing the tie without letting the clause choose left `who` unplaced and the
    decompiler wrote «…know that who ate…»."""
    from tk2.language.decompile import Decompiler

    out = compiler.compile(I_DO_NOT_KNOW_WHO)
    ate = next(r for r in out.zip.rows if getattr(r, "predicate", None) == "eat.v")

    assert isinstance(ate.boxes[Role.AGENT].head, Open), "`who` opens the agent slot"
    assert out.coverage == 1.0 and out.unplaced == ()
    text = Decompiler(compiler.table).decompile(out.zip).text
    assert "know who" in text and "that who" not in text, text


def test_a_discourse_NO_is_unplaced_and_not_compiled_as_a_quantifier(compiler):
    """t-ng-4, «NO, some software is a mind and some is not». `discourse` admits no closed-class
    role and `INTJ` names no word class, so both filters empty — and the fallback used to take the
    table's FIRST row, the negative quantifier. Nothing settles which `no` this is, so it is
    unplaced: the honest answer (the Captain, 2026-09-24)."""
    out = compiler.compile(NO_SOME_SOFTWARE)

    assert "No" in out.unplaced
    quantities = [getattr(r, "quantity", None) for r in out.zip.rows
                  if type(r).__name__ == "QuantifierRow"]
    assert Quantity.NEGATIVE not in quantities, "«no» is not «no software»"


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

    **AND SINCE 2026-09-26 NOTHING IS CLAIMED AT ALL** (`E3.3.11.2.16` (2)). The knowing is
    SUPPOSED, and an attitude row has no truth slot to suppose it in: the attitude cannot take its
    clause's place, so what it holds is withheld, the antecedent with it (a cut there widens the
    claim), and the conditional goes. The property holds more strongly than before: nothing, not
    even the conditional, reaches the world — and the zip says why.
    """
    out = compiled(compiler, "if you know who did it , tell me")
    content = [r for r in out.zip.rows if r.kind == "content"]
    under_attitude = {r.scopes for r in out.zip.rows if r.kind == "attitude"}

    loose = [r for r in content if r.name not in under_attitude]
    assert all(r.truth is None for r in loose), f"claimed: {[r.name for r in loose if r.truth]}"
    assert _claims(out) == [] and not [r for r in out.zip.rows if r.kind == "join"]
    assert any("SUPPOSED" in why for why in out.abstained)


def test_a_compiled_form_does_not_ALSO_abstain(compiler):
    """A report that cries wolf is worse than no report. `if` was in the abstention list of a
    sentence whose IMPLY it had built, because the per-clause walk met it before `_relate` ran."""
    # Amended 2026-09-26 (E3.3.11.2.16 (2)): «if you know who did it» is withheld now — its
    # supposed knowing has no attitude row to go in — and says why. A conditional with no attitude
    # in it carries the property.
    out = compiler.compile(IF)

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
    consequence yet.

    *And it moved a third time, 2026-09-26, off «he says that you like to swim»: E3.12.5 (1) withholds
    its content — a word cut from under «says» changes what was said — so its xcomp no longer shows
    in a partial reading. «We expect them to change their minds» is the same `xcomp` in a claimed
    clause, where the cut only weakens the claim and the partial reading stands.*"""
    out = compiled(compiler, "We expect them to change their minds")

    assert out.unplaced, "the xcomp's own verb is not a row, and the zip says so"
    assert set(out.unplaced) <= set(case("We expect them to change their minds").skeleton.tokens)
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

#: «All that glitters is not gold.» — the quantifier IS the phrase, and the noun it ranges over is a
#: whole CLAUSE. Note where stanza hangs `All`: off `gold`, as the subject, not off anything as a
#: determiner.
GLITTERS = skeleton_from_conllu("All that glitters is not gold.", [
    ("1", "All", "all", "DET", "6", "nsubj"),
    ("2", "that", "that", "PRON", "3", "nsubj"),
    ("3", "glitters", "glitter", "VERB", "1", "acl:relcl"),
    ("4", "is", "be", "AUX", "6", "cop"),
    ("5", "not", "not", "PART", "6", "advmod"),
    ("6", "gold", "gold", "NOUN", "0", "root"),
    ("7", ".", ".", "PUNCT", "6", "punct"),
])

#: The same phrase with the negation FIRST — the order that settles ¬∀ (E3.12.5 (5)): «All … is
#: NOT gold» is withheld as ambiguous, so the structure below is pinned on the reading that is not.
NOT_ALL_GLITTERS = skeleton_from_conllu("Not all that glitters is gold.", [
    ("1", "Not", "not", "PART", "2", "advmod"),
    ("2", "all", "all", "DET", "6", "nsubj"),
    ("3", "that", "that", "PRON", "4", "nsubj"),
    ("4", "glitters", "glitter", "VERB", "2", "acl:relcl"),
    ("5", "is", "be", "AUX", "6", "cop"),
    ("6", "gold", "gold", "NOUN", "0", "root"),
    ("7", ".", ".", "PUNCT", "6", "punct"),
])

#: «Nobody knows the answer.» — a quantifier that is its own phrase LEXICALLY.
NOBODY = skeleton_from_conllu("Nobody knows the answer.", [
    ("1", "Nobody", "nobody", "PRON", "2", "nsubj"),
    ("2", "knows", "know", "VERB", "0", "root"),
    ("3", "the", "the", "DET", "4", "det"),
    ("4", "answer", "answer", "NOUN", "2", "obj"),
    ("5", ".", ".", "PUNCT", "2", "punct"),
])

#: «Every cat that sleeps is happy.» — a QUANTIFIED phrase described twice.
EVERY_CAT = skeleton_from_conllu("Every cat that sleeps is happy.", [
    ("1", "Every", "every", "DET", "2", "det"),
    ("2", "cat", "cat", "NOUN", "6", "nsubj"),
    ("3", "that", "that", "PRON", "4", "nsubj"),
    ("4", "sleeps", "sleep", "VERB", "2", "acl:relcl"),
    ("5", "is", "be", "AUX", "6", "cop"),
    ("6", "happy", "happy", "ADJ", "0", "root"),
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


def test_a_bare_quantifier_binds_ITSELF_and_the_relative_clause_restricts_it(compiler):
    """«All that glitters is not gold» — THREE wrong things that were one cause *(2026-09-20)*.

    A quantifier reached the zip only as a DETERMINER, by being scooped up from the children of the
    noun whose box was being built — and stanza hangs this `All` off `gold`, as the SUBJECT. So the
    binder came out ranging over **gold**, the complement box held the variable instead of the
    metal, and the phrase the sentence is actually about reached no box at all. The relative clause
    then looked for a box holding `all.n`, found none, and minted a second variable nobody bound: a
    row that says nothing, about nobody.

    **The relation is what separates the two readings of one word**, and nothing else can: «ALL
    cats are mammals» is a `det`, «ALL that glitters» is an `nsubj`.

    What is pinned here is the STRUCTURE, not the drill's `glitterer.n` — this station has no
    nominaliser and needs none. The universal binds the glitterer, the negation and the binder both
    scope the predication, and the clause that says what the variable ranges over SHARES that
    variable (req 36) rather than joining it or being dropped.

    *Pinned on «NOT all that glitters is gold» since 2026-09-26: the proverb's own order is withheld
    as ambiguous (E3.12.5 (5), `test_a_universal_BEFORE_a_negation_is_withheld_like_may_not`), and
    the structure is the same one with the negation where it settles the scope.*
    """
    out = compiler.compile(NOT_ALL_GLITTERS)
    binder = rows_of(out, "quantifier")[0]
    negation = rows_of(out, "negation")[0]
    glittering = next(r for r in rows_of(out, "content") if r.predicate == "glitter.v")
    gold = next(r for r in rows_of(out, "content") if r.predicate is None)
    bound = Var(name=binder.binds)

    assert binder.quantity is Quantity.UNIVERSAL
    assert binder.restriction.head != "gold.n", "the metal is what is DENIED, never what is ranged"
    assert gold.boxes[Role.COMPLEMENT].head == "gold.n", "and it stays in the complement"
    assert gold.boxes[Role.PATIENT].head == bound, "the universal binds the SUBJECT of the claim"
    # **THE GAP IS WHAT A SUBJECT OF «glitter» IS** *(G5, 2026-09-24)*. This read `AGENT` while the
    # gap took «the first open box, else the agent» — a default no subject anywhere else obeys. It
    # is now `db/0018`'s answer, the one «gold glitters» gets, whatever that row says.
    alone = compiler.compile(skeleton_from_conllu("Gold glitters.", [
        ("1", "Gold", "gold", "NOUN", "2", "nsubj"),
        ("2", "glitters", "glitter", "VERB", "0", "root"),
        ("3", ".", ".", "PUNCT", "2", "punct"),
    ]))
    gap = next(role for role, box in main_row(alone).boxes.items() if box.head == "gold.n")
    assert glittering.boxes[gap].head == bound, "one variable in two rows — no orphan"
    # **A RESTRICTION IS JOINED TO WHAT THE UNIVERSAL SCOPES, BY IMPLY** (`E3.3.14`, 2026-09-27):
    # ∀x (glitter(x) → gold(x)) — held only by the variable, the glittering stood outside the ¬.
    join = rows_of(out, "join")[0]
    assert join.operator is Operator.IMPLY and join.operands == [glittering.name, gold.name]
    assert binder.scopes == join.name and negation.scopes == join.name, (
        "both prefix elements scope the restricted quantification; their ORDER is the two "
        "readings (req 35)")
    assert out.zip.rows.index(negation) < out.zip.rows.index(binder), "¬∀, the order said"
    assert glittering.truth is None and gold.truth is None and join.truth == 1.0, (
        "the halves are STATED, the implication is the claim — the sentence says neither that "
        "anything glitters nor that anything is gold")
    assert out.coverage == 1.0


def test_a_quantifier_PRONOUN_fills_its_own_box_rather_than_vanishing(compiler):
    """«Nobody knows the answer» compiled to «the answer is known» *(2026-09-20)*.

    `nobody` · `everyone` · `nothing` are quantifiers that are their own phrase — the table's own
    `word_class: pronoun` — and the compile core had one path for a quantifier: be a determiner, and
    move the noun under you into a binder's restriction. With no noun under it the word was
    accounted for as covered and then dropped, so `unplaced` stayed EMPTY and the zip claimed, in
    confidence, the opposite of what was said. Wrongly-understood is the sin (req 8), and this one
    made no sound at all.

    The restriction is the row's own `sort`, as a described OPEN (schema v4, tkzip req 2): «nobody»
    states that what it ranges over is a PERSON, and a restriction is content.
    """
    out = compiler.compile(NOBODY)
    binder = rows_of(out, "quantifier")[0]
    row = main_row(out)

    assert binder.quantity is Quantity.NEGATIVE
    assert isinstance(binder.restriction.head, Open)
    assert binder.restriction.head.sort == "person", "«nobody» ranges over PEOPLE"
    assert binder.scopes == row.name
    assert [role for role, box in row.boxes.items() if box.head == Var(name=binder.binds)], \
        "the quantifier reached a box of its own"
    assert row.boxes[Role.PATIENT].head == "answer.n"
    assert out.coverage == 1.0


def test_a_relative_clause_on_a_QUANTIFIED_phrase_reuses_the_binders_variable(compiler):
    """«Every cat that sleeps is happy» — one cat, one variable, and the sleeping not claimed.

    The clause found the phrase it describes by looking for the box holding `cat.n`, and a
    quantified phrase's box holds a VARIABLE — so the search failed on every quantified phrase
    there is, and the sleeping got a fresh name nobody bound. The placement trace answers what the
    boxes' contents cannot: which box that noun BECAME, which is a record that survives the box
    being rewritten.

    **And reading the variable back in is what makes the truth slot load-bearing here.** Bound to
    the universal, a CLAIMED row says that every cat sleeps. A restriction says which cats are
    meant and claims nothing — while «the cat that sleeps», which binds nothing, stays claimed.

    *Since `E3.3.14` (2026-09-27)* the restriction is JOINED to what the universal scopes, by
    IMPLY: the happy row this pinned CLAIMED said, under ∀, that every cat is happy.
    """
    out = compiler.compile(EVERY_CAT)
    binder = rows_of(out, "quantifier")[0]
    sleeping = next(r for r in rows_of(out, "content") if r.predicate == "sleep.v")
    happy = next(r for r in rows_of(out, "content") if r.predicate is None)
    join = rows_of(out, "join")[0]
    bound = Var(name=binder.binds)

    assert binder.restriction.head == "cat.n"
    assert sleeping.boxes[Role.AGENT].head == bound, "the binder's variable, not a second name"
    assert any(box.head == bound for box in happy.boxes.values()), "the same cat, twice"
    assert binder.scopes == join.name and join.operator is Operator.IMPLY
    assert join.operands == [sleeping.name, happy.name]
    assert sleeping.truth is None and happy.truth is None and join.truth == 1.0
    # **BY KIND, NOT BY POSITION.** Schema v8 gave the referring phrase a binder of its own — «the
    # cat that sleeps» is one cat described twice and the variable is how the zip says so — and a
    # prefix row sorts ahead of the content, so `rows[0]` stopped being the clause this asks about.
    # The claim it makes is unchanged, and it is the one the compiler pins deliberately.
    referring = rows_of(compiler.compile(RELATIVE), "content")
    assert all(row.truth == 1.0 for row in referring), (
        "a relative clause on a REFERRING phrase is presupposed content, and stays claimed")


# ------------------------------------------------------------------------------------------------
# the relative gap takes the role its POSITION gives it (G5, 2026-09-24)
# ------------------------------------------------------------------------------------------------

#: stanza's own parse of each, transcribed so the test needs no model.
FISH_THAT = skeleton_from_conllu("I like the fish that the cat ate.", [
    ("1", "I", "I", "PRON", "2", "nsubj"),
    ("2", "like", "like", "VERB", "0", "root"),
    ("3", "the", "the", "DET", "4", "det"),
    ("4", "fish", "fish", "NOUN", "2", "obj"),
    ("5", "that", "that", "PRON", "8", "obj"),
    ("6", "the", "the", "DET", "7", "det"),
    ("7", "cat", "cat", "NOUN", "8", "nsubj"),
    ("8", "ate", "eat", "VERB", "4", "acl:relcl"),
    ("9", ".", ".", "PUNCT", "2", "punct"),
])

FISH_ZERO = skeleton_from_conllu("I like the fish the cat ate.", [
    ("1", "I", "I", "PRON", "2", "nsubj"),
    ("2", "like", "like", "VERB", "0", "root"),
    ("3", "the", "the", "DET", "4", "det"),
    ("4", "fish", "fish", "NOUN", "2", "obj"),
    ("5", "the", "the", "DET", "6", "det"),
    ("6", "cat", "cat", "NOUN", "7", "nsubj"),
    ("7", "ate", "eat", "VERB", "4", "acl:relcl"),
    ("8", ".", ".", "PUNCT", "2", "punct"),
])

MIND_TRUST = skeleton_from_conllu("You learn from every mind that you trust.", [
    ("1", "You", "you", "PRON", "2", "nsubj"),
    ("2", "learn", "learn", "VERB", "0", "root"),
    ("3", "from", "from", "ADP", "5", "case"),
    ("4", "every", "every", "DET", "5", "det"),
    ("5", "mind", "mind", "NOUN", "2", "obl"),
    ("6", "that", "that", "PRON", "8", "obj"),
    ("7", "you", "you", "PRON", "8", "nsubj"),
    ("8", "trust", "trust", "VERB", "5", "acl:relcl"),
    ("9", ".", ".", "PUNCT", "2", "punct"),
])

HOUSE_IN_WHICH = skeleton_from_conllu("I like the house in which I live.", [
    ("1", "I", "I", "PRON", "2", "nsubj"),
    ("2", "like", "like", "VERB", "0", "root"),
    ("3", "the", "the", "DET", "4", "det"),
    ("4", "house", "house", "NOUN", "2", "obj"),
    ("5", "in", "in", "ADP", "6", "case"),
    ("6", "which", "which", "PRON", "8", "obl"),
    ("7", "I", "I", "PRON", "8", "nsubj"),
    ("8", "live", "live", "VERB", "4", "acl:relcl"),
    ("9", ".", ".", "PUNCT", "2", "punct"),
])

HOUSE_STRANDED = skeleton_from_conllu("I like the house I live in.", [
    ("1", "I", "I", "PRON", "2", "nsubj"),
    ("2", "like", "like", "VERB", "0", "root"),
    ("3", "the", "the", "DET", "4", "det"),
    ("4", "house", "house", "NOUN", "2", "obj"),
    ("5", "I", "I", "PRON", "6", "nsubj"),
    ("6", "live", "live", "VERB", "4", "acl:relcl"),
    ("7", "in", "in", "ADP", "6", "obl"),
    ("8", ".", ".", "PUNCT", "2", "punct"),
])

#: Not English — a tree whose gap is ALREADY FILLED: the pronoun is the object and so is the mouse.
#: A provider can hand the station this, and the question is only what it does with it.
FISH_FILLED = skeleton_from_conllu("I like the fish that the cat ate the mouse.", [
    ("1", "I", "I", "PRON", "2", "nsubj"),
    ("2", "like", "like", "VERB", "0", "root"),
    ("3", "the", "the", "DET", "4", "det"),
    ("4", "fish", "fish", "NOUN", "2", "obj"),
    ("5", "that", "that", "PRON", "8", "obj"),
    ("6", "the", "the", "DET", "7", "det"),
    ("7", "cat", "cat", "NOUN", "8", "nsubj"),
    ("8", "ate", "eat", "VERB", "4", "acl:relcl"),
    ("9", "the", "the", "DET", "10", "det"),
    ("10", "mouse", "mouse", "NOUN", "8", "obj"),
    ("11", ".", ".", "PUNCT", "2", "punct"),
])


def _bound(out, row):
    """The variable `row` shares with a binder — and that binder, so a test can say which noun."""
    binders = {b.binds: b for b in rows_of(out, "quantifier")}
    shared = [(role, box) for role, box in row.boxes.items()
              if isinstance(box.head, Var) and box.head.name in binders]
    assert len(shared) == 1, f"{row.name} shares {len(shared)} variables with a binder"
    role, box = shared[0]
    return role, box, binders[box.head.name]


def test_an_OBJECT_relative_puts_the_antecedent_in_the_OBJECT_box(compiler):
    """«I like the fish that the cat ate» compiled to `eat(agent = the fish)`, **the cat gone and
    `unplaced` empty** (G5). The gap took the first OPEN box, else the agent; there was no open box,
    so the fish was written OVER the cat's agent box — and the cat had been placed, so nothing said
    it was lost. A box replaced in silence is req 8's worst case.

    `that` is `obj`, and `obj` is the patient in every sentence: the pronoun's own relation decides,
    exactly as if the fish stood there.
    """
    out = compiler.compile(FISH_THAT)
    eating = next(r for r in rows_of(out, "content") if r.predicate == "eat.v")
    role, _box, binder = _bound(out, eating)

    assert role is Role.PATIENT and binder.restriction.head == "fish.n", "the fish is what was eaten"
    assert eating.boxes[Role.AGENT].head == "cat.n", "and the cat, which ate it, is still there"
    assert out.coverage == 1.0 and out.zip.unplaced == []


def test_a_ZERO_relative_whose_verb_takes_an_object_and_whose_head_names_nothing_is_the_OBJECT(
        compiler):
    """«I like the fish the cat ate» — no pronoun, so no relation names the gap, and the TREE is the
    same as «the day I slept». G5 withheld it; the Captain's ruling of 2026-09-25 reads it when two
    signals AGREE: `eat` has an object frame in its primary sense, and «fish» names no
    circumstance (`db/0038`). The fish is what was eaten, and the cat is still the eater."""
    out = compiler.compile(FISH_ZERO)
    eating = next(r for r in rows_of(out, "content") if r.predicate == "eat.v")
    role, _box, binder = _bound(out, eating)

    assert role is Role.PATIENT and binder.restriction.head == "fish.n"
    assert eating.boxes[Role.AGENT].head == "cat.n"
    assert out.coverage == 1.0 and out.zip.unplaced == []


DAY_SLEPT = skeleton_from_conllu("The day I slept was cold.", [
    ("1", "The", "the", "DET", "2", "det"),
    ("2", "day", "day", "NOUN", "6", "nsubj"),
    ("3", "I", "I", "PRON", "4", "nsubj"),
    ("4", "slept", "sleep", "VERB", "2", "acl:relcl"),
    ("5", "was", "be", "AUX", "6", "cop"),
    ("6", "cold", "cold", "ADJ", "0", "root"),
    ("7", ".", ".", "PUNCT", "6", "punct"),
])

DAY_BORN = skeleton_from_conllu("The day she was born was sunny.", [
    ("1", "The", "the", "DET", "2", "det"),
    ("2", "day", "day", "NOUN", "7", "nsubj"),
    ("3", "she", "she", "PRON", "5", "nsubj:pass"),
    ("4", "was", "be", "AUX", "5", "aux:pass"),
    ("5", "born", "bear", "VERB", "2", "acl:relcl"),
    ("6", "was", "be", "AUX", "7", "cop"),
    ("7", "sunny", "sunny", "ADJ", "0", "root"),
    ("8", ".", ".", "PUNCT", "7", "punct"),
])

TIME_ATE = skeleton_from_conllu("I miss the time we ate together.", [
    ("1", "I", "I", "PRON", "2", "nsubj"),
    ("2", "miss", "miss", "VERB", "0", "root"),
    ("3", "the", "the", "DET", "4", "det"),
    ("4", "time", "time", "NOUN", "2", "obj"),
    ("5", "we", "we", "PRON", "6", "nsubj"),
    ("6", "ate", "eat", "VERB", "4", "acl:relcl"),
    ("7", "together", "together", "ADV", "6", "advmod"),
    ("8", ".", ".", "PUNCT", "2", "punct"),
])

REASON_LEFT = skeleton_from_conllu("The reason he left is clear.", [
    ("1", "The", "the", "DET", "2", "det"),
    ("2", "reason", "reason", "NOUN", "6", "nsubj"),
    ("3", "he", "he", "PRON", "4", "nsubj"),
    ("4", "left", "leave", "VERB", "2", "acl:relcl"),
    ("5", "is", "be", "AUX", "6", "cop"),
    ("6", "clear", "clear", "ADJ", "0", "root"),
    ("7", ".", ".", "PUNCT", "6", "punct"),
])

MAN_THINK = skeleton_from_conllu("The man I think you met is here.", [
    ("1", "The", "the", "DET", "2", "det"),
    ("2", "man", "man", "NOUN", "8", "nsubj"),
    ("3", "I", "I", "PRON", "4", "nsubj"),
    ("4", "think", "think", "VERB", "2", "acl:relcl"),
    ("5", "you", "you", "PRON", "6", "nsubj"),
    ("6", "met", "meet", "VERB", "4", "ccomp"),
    ("7", "is", "be", "AUX", "8", "cop"),
    ("8", "here", "here", "ADV", "0", "root"),
    ("9", ".", ".", "PUNCT", "8", "punct"),
])


def test_a_ZERO_relative_whose_verb_takes_none_and_whose_head_names_a_time_is_the_TIME(compiler):
    """«The day I slept» — `sleep` has no object frame, «day» is `noun.time`: the two agree, and the
    day is WHEN I slept, in the box a time phrase fills. Never `sleep(patient = day)`."""
    out = compiler.compile(DAY_SLEPT)
    sleeping = next(r for r in rows_of(out, "content") if r.predicate == "sleep.v")
    role, box, binder = _bound(out, sleeping)

    assert role is Role.TIME and box.marker is None and binder.restriction.head == "day.n"
    assert Role.PATIENT not in sleeping.boxes
    assert out.zip.unplaced == []


def test_a_PASSIVE_relative_has_no_object_gap_whatever_the_verb_frames_say(compiler):
    """«The day she was born» — `bear` takes an object, so the frames alone would say object and
    disagree with «day». But the object was promoted to the subject: a passive relative's gap is an
    adverbial or nothing. The tree's shape outranks a frame that describes the active verb."""
    out = compiler.compile(DAY_BORN)
    bearing = next(r for r in rows_of(out, "content") if r.predicate == "bear.v")
    role, _box, _binder = _bound(out, bearing)

    assert role is Role.TIME
    assert not isinstance(bearing.boxes[Role.PATIENT].head, Var), "she is the one born, not the day"


def test_a_ZERO_relative_the_two_signals_DISAGREE_on_is_withheld_as_before(compiler):
    """Any disagreement withholds, exactly as G5 did — «I miss the time we ate together»: `eat`
    takes an object and «time» names a time (the `db/0038` row: WordNet files it `noun.event`).
    And a kind that names no box — «the reason he left»: tkzip says a reason with a join — is
    heard, and withheld."""
    for skeleton, words, why in (
            (TIME_ATE, {"we", "ate", "together"}, "disagree"),
            (REASON_LEFT, {"he", "left"}, "no box")):
        out = compiler.compile(skeleton)
        assert not [r for r in rows_of(out, "content") if r.predicate in ("eat.v", "leave.v")]
        assert not rows_of(out, "quantifier"), "no binder minted for nothing"
        assert set(out.zip.unplaced) == words
        assert any(why in reason for reason in out.abstained), out.abstained


def test_a_ZERO_relative_over_a_CLAUSAL_complement_is_withheld(compiler):
    """«The man I think you met» — the man is the object of the MEETING, and `think` already has its
    object, the clause. Read as `think`'s object he went into a row the attitude dissolved, and a
    zip that had lost him called itself whole. The tree does not say at which level the gap is."""
    out = compiler.compile(MAN_THINK)

    assert not [r for r in rows_of(out, "content") if r.predicate == "meet.v"]
    assert {"I", "think", "you", "met"} <= set(out.zip.unplaced)
    assert any("clausal complement" in why for why in out.abstained)


def test_the_two_curation_rows_answer_what_the_RESOURCE_misfiles():
    """`db/0038`'s check asks its question with WordNet's answers as recorded when the rows were
    written, so the migration never loads the resource. This is the other half: the record is
    still what WordNet says — or the rows are answering a question nobody asks any more."""
    from tk2.dictionary.supersense import supersense_for
    from tk2.migrations import discover

    rows = next(m for m in discover() if m.number == 38).load().CURATED
    for row in rows:
        assert supersense_for(row["lemma"], "NOUN") == row["resource_says"], row["lemma"]


def test_a_relative_on_a_QUANTIFIED_phrase_puts_the_variable_where_the_pronoun_stands(compiler):
    """«You learn from every mind that you trust» compiled `trust(experiencer = you, AGENT = mind)` —
    the minds doing the trusting. `that` is the object, so the mind is what is trusted."""
    out = compiler.compile(MIND_TRUST)
    trusting = next(r for r in rows_of(out, "content") if r.predicate == "trust.v")
    role, box, binder = _bound(out, trusting)

    assert role is Role.PATIENT and binder.restriction.head == "mind.n"
    assert Role.AGENT not in trusting.boxes
    assert box.marker is None, "«from» marks the mind in the LEARNING, not in the trusting"
    assert trusting.truth is None, "a quantifier's restriction is stated, not claimed"
    assert out.coverage == 1.0


def test_an_OBLIQUE_relative_takes_its_marker_s_role_and_keeps_the_marker(compiler):
    """«the house IN WHICH I live» — `which` is `obl` with «in», and the marker's rule settles the
    role with the HOUSE as its nominal: «which» has no supersense and «house» does. The marker rides
    on the gap's box, as every marker rides on the box it marks (req 65)."""
    out = compiler.compile(HOUSE_IN_WHICH)
    living = next(r for r in rows_of(out, "content") if r.predicate == "live.v")
    role, box, binder = _bound(out, living)

    assert role is Role.LOCATION and box.marker == "in"
    assert binder.restriction.head == "house.n"
    assert out.coverage == 1.0


def test_a_STRANDED_marker_is_the_gap_s_marker(compiler):
    """«the house I live IN» — a zero relative, and the tree DOES say where the gap is: a marker with
    no nominal of its own. It is settled by the same rule, with the antecedent where its nominal
    would be, and the two spellings compile to one zip."""
    stranded = compiler.compile(HOUSE_STRANDED)
    living = next(r for r in rows_of(stranded, "content") if r.predicate == "live.v")
    role, box, _binder = _bound(stranded, living)

    assert role is Role.LOCATION and box.marker == "in"
    assert stranded.coverage == 1.0
    overt = compiler.compile(HOUSE_IN_WHICH)
    assert [r.model_dump() for r in stranded.zip.rows] == [r.model_dump() for r in overt.zip.rows]


def test_a_gap_whose_box_is_already_FILLED_withholds_the_clause(compiler):
    """Never overwrite. The pronoun says `obj` and the clause already has an object; the fish cannot
    take the mouse's box, and neither can the station pick one of them. The clause goes to
    `unplaced` whole, and nothing is bound."""
    out = compiler.compile(FISH_FILLED)

    assert not [r for r in rows_of(out, "content") if r.predicate == "eat.v"]
    assert not rows_of(out, "quantifier")
    assert {"cat", "mouse", "ate", "that"} <= set(out.zip.unplaced)
    assert any("already filled" in why for why in out.abstained)


LIKE_TO_SWIM = skeleton_from_conllu("You like to swim.", [
    ("1", "You", "you", "PRON", "2", "nsubj"),
    ("2", "like", "like", "VERB", "0", "root"),
    ("3", "to", "to", "PART", "4", "mark"),
    ("4", "swim", "swim", "VERB", "2", "xcomp"),
    ("5", ".", ".", "PUNCT", "2", "punct"),
])


def test_an_xcomp_stays_inside_its_clause(compiler):
    """«you like TO SWIM» is one predication with a controlled subject, not two claims: nobody
    asserts that you swim. A second row would put an unasserted proposition in the zip with nothing
    marking it unasserted — the one thing the truth slot exists to prevent.

    **THIS ASKS THE BEHAVIOUR, NOT THE SET** *(rewritten 2026-09-22)*. It used to assert
    `"xcomp" not in CLAUSE_DEPS`, and E3's frame/knowledge audit moved that judgement to `db/0032`:
    `CLAUSE_DEPS` now holds every relation UD NAMES as a clause, `xcomp` among them, and the table
    says which of them earns a row. A test that pins the implementation cannot survive the
    implementation moving — and the thing worth protecting was never the set, it was the zip.
    """
    rows = [r for r in compiler.compile(LIKE_TO_SWIM).zip.rows if r.kind == "content"]

    assert len(rows) == 1, f"the xcomp earned a row of its own: {[r.name for r in rows]}"
    assert rows[0].predicate == "like.v"


def test_the_TABLE_is_what_keeps_an_xcomp_out_and_it_can_be_asked():
    """The other half of the move: the ruling is now readable, which is the whole point of a row.

    `xcomp` is IN the set UD's own definitions give — UD calls it an «open clausal complement» and
    is right to — so nothing in code says it is not a clause. What says it earns no row is a row.
    """
    from tk2.language.compile import CLAUSE_DEPS
    from tk2.language.ud_readings import standing_ud_readings

    readings = standing_ud_readings()

    assert "xcomp" in CLAUSE_DEPS, "the set is UD's, and UD calls an xcomp a clause"
    assert readings.opens_clause("xcomp") is False
    assert readings.opens_clause("ccomp") is True, "a miss is the ordinary reading"




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
    *Today (2026-09-26, night) 23 whole, 93.1% — the `full` floor has no slack left; the mean's
    re-base below is the Captain's (2026-09-27).*

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
    # Re-based 2026-09-26, 0.98 → 0.97, E3.12.5 — the Captain re-based the exit's ratchets: «he says
    # that you like to swim» claimed a false content and is now withheld but for «he says».
    # Re-based 2026-09-26 (night), 0.97 → 0.93, E3.3.11.2.16 (2) — built by the 1st Officier on the
    # ruling, CONFIRMED by the Captain 2026-09-27 («all your ruling, go», the build's re-base of
    # E3.3.11.2.16 taken whole): «if you know who did it, tell me» SUPPOSES the knowing, an
    # attitude row has no truth slot to suppose it in, and the sentence is withheld whole (it
    # claimed a conditional whose antecedent was a knowing held outside any supposition).
    assert mean >= 0.93, f"mean {mean:.1%}; it was 93.1% on 2026-09-26, night (98.9% on 2026-09-16)"


def test_the_FRONTIER_half_is_where_the_work_is(compiler):
    """The relations the corpus reached on 2026-09-16: **11 of 20 whole, 84.6% mean.** *Today
    (2026-09-26, night) 9 whole, 74.8% — re-based by the Captain, 2026-09-27.*

    Low, and honestly so. What is missing is NAMED rather than averaged away — `flat`/`list` (one
    name across several tokens — E3b), `xcomp` (deliberately not a clause, and what it IS instead is
    unruled), `nummod` (the box's own `count` field), `appos`, and the gapped `orphan`, which stanza
    does not label at all.
    """
    scored = [compiler.compile(c.skeleton) for c in frontier()]
    full = sum(1 for s in scored if s.coverage == 1.0)
    mean = sum(s.coverage for s in scored) / len(scored)

    assert len(scored) >= 20, "a relation may gain a case; the frontier grows and the ratchet does not"
    # Re-based 2026-09-26, 11 → 10 and 0.78 → 0.77, E3.12.5.9.7 (the Captain's re-base): «left
    # early in the morning» — «early» was counted placed with the time box taken; it is unplaced now.
    # Re-based 2026-09-26 (night), 10 → 9 and 0.77 → 0.74, E3.3.11.2.10 / E3.3.11.2.16 (2) — built
    # by the 1st Officier on the ruling, CONFIRMED by the Captain 2026-09-27 («all your ruling, go»,
    # the build's re-base of E3.3.11.2.16 taken whole): «That he lied surprised me» made ME
    # the holder of a surprising — the holder was read off the patient box. A clausal subject is not
    # a holder, the matrix keeps its place, and «[it] surprised me» stands with «that he lied» cut.
    assert full >= 9, f"{full} of {len(scored)} whole; 9 were on 2026-09-26, night (11 on 09-16)"
    # Re-based 2026-09-26, 0.84 → 0.78, E3.12.5 — the Captain re-based the exit's ratchets: the two
    # «muffin man» sentences claimed a content never said and are withheld but for the saying.
    assert mean >= 0.74, f"mean {mean:.1%}; it was 74.8% on 2026-09-26, night (84.6% on 2026-09-16)"


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


#: «Cognition is the psychological result of perception and I love learning.» as stanza reads it —
#: an attributive adjective inside a clause that a `conj` has already joined.
FOLD_IN_A_JOIN = skeleton_from_conllu(
    "Cognition is the psychological result of perception and I love learning.", [
        ("1", "Cognition", "cognition", "NOUN", "5", "nsubj"),
        ("2", "is", "be", "AUX", "5", "cop"),
        ("3", "the", "the", "DET", "5", "det"),
        ("4", "psychological", "psychological", "ADJ", "5", "amod"),
        ("5", "result", "result", "NOUN", "0", "root"),
        ("6", "of", "of", "ADP", "7", "case"),
        ("7", "perception", "perception", "NOUN", "5", "nmod"),
        ("8", "and", "and", "CCONJ", "10", "cc"),
        ("9", "I", "i", "PRON", "10", "nsubj"),
        ("10", "love", "love", "VERB", "5", "conj"),
        ("11", "learning", "learning", "NOUN", "10", "obj"),
        ("12", ".", ".", "PUNCT", "5", "punct"),
    ])


def test_the_adjective_conjunction_TAKES_THE_ROW_S_PLACE_in_the_clause_join(compiler):
    """**A SENTENCE IS A TREE** (G2, 2026-09-24). The clause join named the copular row, and req 70's
    fold join named it again — two parents, and the decompiler said the second one as a sentence of
    its own: «Cognition is the result.» The fold join replaces the row where the clause join named
    it, as a `conj` replaces the clause it extends, and the binder scoping it goes with it.
    """
    out = compiler.compile(FOLD_IN_A_JOIN)
    joins = {r.name: r for r in out.zip.rows if r.kind == "join"}
    copular = next(r for r in out.zip.rows if r.kind == "content"
                   and Role.COMPLEMENT in r.boxes and isinstance(r.boxes[Role.COMPLEMENT].head, Var))
    fold = next(j for j in joins.values() if copular.name in j.operands)
    binder = next(r for r in out.zip.rows if r.kind == "quantifier")

    named = [operand for join in joins.values() for operand in join.operands]
    assert named.count(copular.name) == 1, f"the copular row has two parents: {joins}"
    assert any(fold.name in j.operands for j in joins.values()), "the fold sits INSIDE the clause"
    assert binder.scopes == fold.name, "the binder scopes the fold, which carries every use of it"
    assert len(named) == len(set(named)), "no row is an operand twice"


# ------------------------------------------------------------------------------------------------
# `E3.3.14` — ONE SPELLING FOR A RESTRICTIVE MODIFIER: the binder scopes a join of the restriction
# with what it scopes, by the binder's own operator (2026-09-27)
# ------------------------------------------------------------------------------------------------


def _restricted(det: str, subject: list) -> object:
    """«<det> tired man sleeps .» and its relative twin — the subject phrase's rows, then the verb."""
    noun = next(i for i, _t, _l, upos, _h, _d in subject if upos == "NOUN")
    rows = [("1", det, det.lower(), "DET", noun, "det"), *subject]
    verb = str(len(rows) + 1)
    rows = [(i, t, lemma, upos, verb if head == "V" else head, dep)
            for i, t, lemma, upos, head, dep in rows]
    rows += [(verb, "sleeps", "sleep", "VERB", "0", "root"),
             (str(len(rows) + 2), ".", ".", "PUNCT", verb, "punct")]
    return _tree(" ".join(r[1] for r in rows), rows)


TIRED = [("2", "tired", "tired", "ADJ", "3", "amod"), ("3", "man", "man", "NOUN", "V", "nsubj")]


@pytest.mark.parametrize("det, operator, halves", [
    ("Every", Operator.IMPLY, None),     # ∀x (tired(x) → sleep(x)): the halves are stated
    ("No", Operator.AND, None),          # ¬∃x (tired(x) ∧ sleep(x)): neither half on its own
    ("A", Operator.AND, 1.0),            # ∃x (tired(x) ∧ sleep(x)): both entailed, both claimed
])
def test_a_restriction_is_joined_by_its_BINDER_S_operator_and_claims_what_the_binder_allows(
        compiler, det, operator, halves):
    """«Every tired man sleeps» was ∀x (tired(x) ∧ sleep(x)) — every man is tired, a WRONG CLAIM
    (`E3.3.14`). Restricted quantification is logic: ∀ joins its restriction by IMPLY, every other
    binder by AND; and a half is claimed on its own only where the binder distributes over the
    conjunction (`restriction_truths`). The join takes the clause's claim."""
    out = compiler.compile(_restricted(det, TIRED))
    binder, join = rows_of(out, "quantifier")[0], rows_of(out, "join")[0]
    tired, sleeping = (_row(out, name) for name in join.operands)

    assert binder.scopes == join.name and join.operator is operator and join.truth == 1.0
    assert tired.boxes[Role.COMPLEMENT].head == "tired.a" and sleeping.predicate == "sleep.v"
    assert tired.truth == halves and sleeping.truth == halves


def test_a_RELATIVE_clause_is_spelled_as_the_adjective_is(compiler):
    """«A man who is tired sleeps» and «A tired man sleeps» — one reading, and the relative clause
    was a row held by the variable alone: nothing joined it, so nothing that scoped the clause
    scoped it (`E3.3.11.2.5.1`). It is the first operand of its binder's join now, as the adjective
    is. *The binder's force still differs — ∃ for the adjective, none for the relative — and that is
    `E3.3.14.1`, for the Captain.*"""
    out = compiler.compile(_restricted("A", [
        ("2", "man", "man", "NOUN", "V", "nsubj"), ("3", "who", "who", "PRON", "5", "nsubj"),
        ("4", "is", "be", "AUX", "5", "cop"), ("5", "tired", "tired", "ADJ", "2", "acl:relcl")]))
    binder, join = rows_of(out, "quantifier")[0], rows_of(out, "join")[0]
    tired, sleeping = (_row(out, name) for name in join.operands)

    assert binder.scopes == join.name and join.operator is Operator.AND
    assert tired.boxes[Role.COMPLEMENT].head == "tired.a" and sleeping.predicate == "sleep.v"
    assert out.coverage == 1.0


def test_the_restriction_join_stands_WHERE_ITS_BINDER_STANDS(compiler):
    """Row order is scope order (req 35), and the join goes in at the binder's place: what came
    before the binder scopes the join, what came after stays on the clause. The binder used to move
    out past everything — «NOT every tired man sleeps» came out ∀¬, «He does NOT see a tired man»
    claimed the man — and the relative clause's binder was minted late, after the clause's own
    «not»: «The man who left was not happy» said «not the man» (`E3.3.11.2.1.1`)."""
    not_every = compiler.compile(_tree("Not every tired man sleeps .", [
        ("1", "Not", "not", "PART", "5", "advmod"), ("2", "every", "every", "DET", "4", "det"),
        ("3", "tired", "tired", "ADJ", "4", "amod"), ("4", "man", "man", "NOUN", "5", "nsubj"),
        ("5", "sleeps", "sleep", "VERB", "0", "root"), ("6", ".", ".", "PUNCT", "5", "punct")]))
    does_not_see = compiler.compile(_tree("He does not see a tired man .", [
        ("1", "He", "he", "PRON", "4", "nsubj"), ("2", "does", "do", "AUX", "4", "aux"),
        ("3", "not", "not", "PART", "4", "advmod"), ("4", "see", "see", "VERB", "0", "root"),
        ("5", "a", "a", "DET", "7", "det"), ("6", "tired", "tired", "ADJ", "7", "amod"),
        ("7", "man", "man", "NOUN", "4", "obj"), ("8", ".", ".", "PUNCT", "4", "punct")]))
    the_man = compiler.compile(_tree("The man who left was not happy .", [
        ("1", "The", "the", "DET", "2", "det"), ("2", "man", "man", "NOUN", "7", "nsubj"),
        ("3", "who", "who", "PRON", "4", "nsubj"), ("4", "left", "leave", "VERB", "2", "acl:relcl"),
        ("5", "was", "be", "AUX", "7", "cop"), ("6", "not", "not", "PART", "7", "advmod"),
        ("7", "happy", "happy", "ADJ", "0", "root"), ("8", ".", ".", "PUNCT", "7", "punct")]))

    for out in (not_every, does_not_see):
        join = rows_of(out, "join")[0]
        assert [r.kind for r in out.zip.rows if getattr(r, "scopes", None) == join.name] \
            == ["negation", "quantifier"], "¬ over the binder, both over the restricted clause"
    join = rows_of(the_man, "join")[0]
    happy = _row(the_man, join.operands[1])
    assert _stack(the_man, join.name) == [("quantifier", None)]
    assert [r.kind for r in the_man.zip.rows if getattr(r, "scopes", None) == happy.name] \
        == ["negation"], "the definite, then the «not» — the words' order"


def test_an_ATTITUDE_holds_the_restriction_of_what_it_holds(compiler):
    """`E3.3.11.2.5.1` — «I think that a man who sleeps is tired» claimed that a man sleeps: the
    attitude scoped the matrix row, and the relative clause was held by the variable alone. Joined,
    the restriction is inside the complement's place, and the attitude seats over it."""
    out = compiler.compile(_tree("I think that a man who sleeps is tired .", [
        ("1", "I", "I", "PRON", "2", "nsubj"), ("2", "think", "think", "VERB", "0", "root"),
        ("3", "that", "that", "SCONJ", "9", "mark"), ("4", "a", "a", "DET", "5", "det"),
        ("5", "man", "man", "NOUN", "9", "nsubj"), ("6", "who", "who", "PRON", "7", "nsubj"),
        ("7", "sleeps", "sleep", "VERB", "5", "acl:relcl"), ("8", "is", "be", "AUX", "9", "cop"),
        ("9", "tired", "tired", "ADJ", "2", "ccomp"), ("10", ".", ".", "PUNCT", "2", "punct")]),
        _speech())
    join = rows_of(out, "join")[0]

    assert _stack(out, join.name) == [("attitude", "think.v"), ("quantifier", None)]
    assert _content(out, "sleep.v").name == join.operands[0]
    assert not [r for r in out.zip.rows if getattr(r, "scopes", None) not in (join.name, None)]


def test_a_SENTENCE_whose_root_is_a_noun_phrase_with_a_clause_has_lost_its_predicate(compiler):
    """`E3.3.14.3` (the QM's judgement, 2026-09-27) — stanza makes the NOUN the root of «The man who
    knew that she lied left.», hangs «left» inside the relative clause, and the station claimed «the
    man knew that she lied left(ward)» beside «[] is the man». A sentence closed as one, whose root
    is a noun phrase with a clause and no copula and no subject, has lost its predicate: withheld.
    UD's citation fragment «the cat that sleeps», closed by nothing, keeps its reading."""
    out = compiler.compile(_tree("The man who knew that she lied left .", [
        ("1", "The", "the", "DET", "2", "det"), ("2", "man", "man", "NOUN", "0", "root"),
        ("3", "who", "who", "PRON", "4", "nsubj"), ("4", "knew", "know", "VERB", "2", "acl:relcl"),
        ("5", "that", "that", "SCONJ", "7", "mark"), ("6", "she", "she", "PRON", "7", "nsubj"),
        ("7", "lied", "lie", "VERB", "4", "ccomp"), ("8", "left", "left", "ADV", "7", "advmod"),
        ("9", ".", ".", "PUNCT", "2", "punct")]))

    assert _claims(out) == [] and not [r for r in out.zip.rows if r.kind == "attitude"]
    assert any("lost its predicate" in why for why in out.abstained)
    assert compiled(compiler, "the cat that sleeps").coverage == 1.0


def test_a_restriction_inside_a_SUPPOSITION_is_supposed_with_it(compiler):
    """G9 read on the restriction join: «If I see a tired man, I leave» claimed that a man is tired —
    the adjective's row stood CLAIMED inside a supposed conjunction. A half claims only as much as
    the clause it restricts, and a supposed clause claims nothing."""
    out = compiler.compile(_tree("If I see a tired man , I leave .", [
        ("1", "If", "if", "SCONJ", "3", "mark"), ("2", "I", "I", "PRON", "3", "nsubj"),
        ("3", "see", "see", "VERB", "9", "advcl"), ("4", "a", "a", "DET", "6", "det"),
        ("5", "tired", "tired", "ADJ", "6", "amod"), ("6", "man", "man", "NOUN", "3", "obj"),
        ("7", ",", ",", "PUNCT", "9", "punct"), ("8", "I", "I", "PRON", "9", "nsubj"),
        ("9", "leave", "leave", "VERB", "0", "root"), ("10", ".", ".", "PUNCT", "9", "punct")]),
        _speech())

    assert [r.operator for r in rows_of(out, "join")] == [Operator.IMPLY, Operator.AND]
    assert _claims(out) == [rows_of(out, "join")[0]], "only the conditional is claimed"


# ------------------------------------------------------------------------------------------------
# adverbs — requirement 23's four scopes
# ------------------------------------------------------------------------------------------------


def test_a_circumstantial_adverb_fills_its_own_box(compiler):
    """«She left EARLY» — `early` is a TIME, and it is its own filler: there is no nominal under
    it, so the head is the adverb's own key.

    *It was pinned on «…left early in the morning» until `E3.12.5.9.7`, where the box is TAKEN —
    and «early» was counted as placed while nothing in the zip held it.*"""
    out = compiler.compile(skeleton_from_conllu("She left early.", [
        ("1", "She", "she", "PRON", "2", "nsubj"),
        ("2", "left", "leave", "VERB", "0", "root"),
        ("3", "early", "early", "ADV", "2", "advmod"),
        ("4", ".", ".", "PUNCT", "2", "punct"),
    ]))
    row = main_row(out)

    assert row.boxes[Role.TIME].head == "early.r"
    assert out.coverage == 1.0


def test_a_MARKED_nominal_outranks_a_bare_adverb_for_the_same_box(compiler):
    """«left EARLY in the MORNING» has two time expressions and one time box. The speaker CHOSE the
    marker on «in the morning», so it is the stronger evidence — and placing adverbs in token order
    let `early` take the box and pushed `morning` out, which is the same coverage and the worse
    reading. Adverbs are therefore placed after the nominals of their clause.

    **AND THE LOSER IS UNPLACED, NOT COUNTED** (`E3.12.5.9.7`, 2026-09-26). One box holds one
    phrase: `early` reached no part of the zip, and until then `placement` said it had — a silent
    loss. It is in `unplaced` now, and `abstained` says why."""
    out = compiled(compiler, "The guy , John said , left early in the morning")
    row = next(r for r in out.zip.rows if getattr(r, "predicate", None) == "leave.v")

    assert row.boxes[Role.TIME].head == "morning.n", "the marked one won"
    assert out.unplaced == ("early",), "and the adverb it displaced is visible, not counted"
    assert any(line.startswith("early: a second time") for line in out.abstained)


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

#: The same question with the one word the station cannot place taken out — the `compound`.
QUOTED_QUESTION_WHOLE = skeleton_from_conllu('I asked : " Do you know the man ? "', [
    ("1", "I", "I", "PRON", "2", "nsubj"),
    ("2", "asked", "ask", "VERB", "0", "root"),
    ("3", ":", ":", "PUNCT", "2", "punct"),
    ("4", '"', '"', "PUNCT", "2", "punct"),
    ("5", "Do", "do", "AUX", "7", "aux"),
    ("6", "you", "you", "PRON", "7", "nsubj"),
    ("7", "know", "know", "VERB", "2", "ccomp"),
    ("8", "the", "the", "DET", "9", "det"),
    ("9", "man", "man", "NOUN", "7", "obj"),
    ("10", "?", "?", "PUNCT", "2", "punct"),
    ("11", '"', '"', "PUNCT", "2", "punct"),
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
    claimed, the hunger is asked, and the AND binding them is not claimed either.

    *Amended 2026-09-26 (`E3.3.11.2`)*: the knowing is the attitude over the tiredness, and it
    takes its clause's place in the «but» — so the join names the tiredness, and no know.v row is
    left beside the attitude to claim the knowing a second time."""
    out = compiler.compile(CLAIM_THEN_QUESTION)
    knowing = next(r for r in out.zip.rows if r.kind == "attitude")
    assert (knowing.verb, knowing.scopes) == ("know.v", "r1")
    assert not [r for r in out.zip.rows if getattr(r, "predicate", None) == "know.v"]
    assert _row(out, "r1").truth == 1.0, "«you are tired» is still asserted"
    assert isinstance(_row(out, "r2").truth, Open)
    between = next(j for j in out.zip.rows if j.kind == "join" and "r2" in j.operands)
    assert between.operands == ["r1", "r2"], "the complement took the knowing's place in the join"
    assert isinstance(between.truth, Open), "«A, but B?» does not claim A-and-B"


def test_a_QUOTED_question_asks_while_the_saying_stays_claimed(compiler):
    """«I asked: "Do you know the muffin man?"» — the asking happened; the knowing is what was
    asked. A quote is a statement of its own (req 21).

    *The asking is the ATTITUDE ROW since 2026-09-20 — its clause dissolved into it — so what is
    claimed is read off the attitude, and what is asked off the row it scopes.*

    *And the muffin man is WITHHELD since 2026-09-26* (E3.12.5 (1)): «muffin» is a `compound` the
    station does not build, and asking whether you know «the man» is not what was asked. The shape
    is pinned on the question without it.
    """
    out = compiler.compile(QUOTED_QUESTION_WHOLE)
    attitude = rows_of(out, "attitude")[0]
    assert attitude.verb == "ask.v"
    assert isinstance(_row(out, attitude.scopes).truth, Open)

    withheld = compiler.compile(QUOTED_QUESTION)
    assert not rows_of(withheld, "attitude") and "muffin" in withheld.unplaced
    assert any("«muffin»" in why and "attitude" in why for why in withheld.abstained)


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


def test_a_TAG_question_asks_its_host_with_a_PRIOR(compiler):
    """«The cat is hungry, isn't it?» — tkzip req 50: the host OPEN with a high prior, and the tag no
    row of its own.

    *Amended 2026-09-27 (`E3.3.11.2.21`, the Captain: «a tag question is req 50's: the host OPEN
    with a high prior»)* — this was `test_a_TAG_question_claims_and_then_asks`, pinning the 09-18
    note's «a claim followed by a request to confirm it»: the hunger claimed at 1.0 beside an asked
    copula with no complement — a claim and a question of one content. Superseded, and renamed so
    the name says what is pinned. The copula tag is the one the elision never saw (`be` heading its
    clause is no elided verb); the tag's SHAPE sees it.

    And «it» says the cat is neuter, which no box of a noun holds: unplaced, and said so."""
    out = compiler.compile(TAG_QUESTION)
    (host,) = [r for r in out.zip.rows if r.kind == "content"]

    assert isinstance(host.truth, Open) and host.truth.prior == compiler.priors.of("reversed_tag")
    assert [r.kind for r in out.zip.rows] == ["content"], "no tag row, no join, no ¬ of the tag's"
    assert out.unplaced == ("it",)
    assert any("«it»" in why and "gender" in why for why in out.abstained)


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
    asks the table — and a table with no row for the bare imperative is refused, because every
    imperative's want carries its strength (`E3.3.11.2.24`)."""
    from tk2.language.compile import Compiler
    from tk2.language.strength import AttitudeStrengths

    # *Amended 2026-09-27 (`E3.3.11.2.24`, the Captain: every imperative's want carries a strength,
    # an invariant the station asserts)* — a table with no row for the bare imperative used to
    # leave the slot EMPTY, and the want was then read back as one the speaker STATES. It is refused
    # where the compiler is built now, never in the middle of a sentence.
    with pytest.raises(ValueError, match="bare imperative"):
        Compiler(compiler.table, strengths=AttitudeStrengths({}, "a table with no rows"))

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


# **A QUOTE ROTATES WHATEVER VERB FRAMES IT** (E3.2.1.4): the rotation reads the same test `_relate`
# raises the attitude by — a bare quoted `ccomp` of a readable verb — and no list of saying verbs.

JOHN_EXCLAIMED_TO_MARIE = skeleton_from_conllu('John exclaimed to Marie " You are late "', [
    ("1", "John", "john", "PROPN", "2", "nsubj"),
    ("2", "exclaimed", "exclaim", "VERB", "0", "root"),
    ("3", "to", "to", "ADP", "4", "case"),
    ("4", "Marie", "marie", "PROPN", "2", "obl"),
    ("5", '"', '"', "PUNCT", "8", "punct"),
    ("6", "You", "you", "PRON", "8", "nsubj"),
    ("7", "are", "be", "AUX", "8", "cop"),
    ("8", "late", "late", "ADJ", "2", "ccomp"),
    ("9", '"', '"', "PUNCT", "8", "punct"),
])

JOHN_SCREAMED = skeleton_from_conllu('John screamed " I am late "', [
    ("1", "John", "john", "PROPN", "2", "nsubj"),
    ("2", "screamed", "scream", "VERB", "0", "root"),
    ("3", '"', '"', "PUNCT", "6", "punct"),
    ("4", "I", "I", "PRON", "6", "nsubj"),
    ("5", "am", "be", "AUX", "6", "cop"),
    ("6", "late", "late", "ADJ", "2", "ccomp"),
    ("7", '"', '"', "PUNCT", "6", "punct"),
])


JOHN_THOUGHT = skeleton_from_conllu('John thought " I am late "', [
    ("1", "John", "john", "PROPN", "2", "nsubj"),
    ("2", "thought", "think", "VERB", "0", "root"),
    ("3", '"', '"', "PUNCT", "6", "punct"),
    ("4", "I", "I", "PRON", "6", "nsubj"),
    ("5", "am", "be", "AUX", "6", "cop"),
    ("6", "late", "late", "ADJ", "2", "ccomp"),
    ("7", '"', '"', "PUNCT", "6", "punct"),
])


@pytest.mark.parametrize("skeleton, who", [(JOHN_EXCLAIMED_TO_MARIE, "marie.n"),
                                           (JOHN_SCREAMED, "john.n"),
                                           (JOHN_THOUGHT, "john.n")])
def test_a_QUOTE_rotates_under_ANY_verb_not_only_a_saying_one(compiler, skeleton, who):
    """«John exclaimed to Marie "You are late"» — the «you» is Marie; «John screamed "I am late"» —
    the «I» is John. Neither verb was on the saying list, and both clauses were already attitudes.
    **A quoted THOUGHT rotates too** — «John thought "I am late"» is John's «I»: the marks are the
    signal, and thinking is not saying."""
    out = compiler.compile(skeleton, _speech())
    late = next(r for r in out.zip.rows if r.kind == "content"
                and getattr(r.boxes.get(Role.COMPLEMENT), "head", None) == "late.a")
    assert late.boxes[Role.PATIENT].head == who


# **A DEICTIC ADVERB IS AN OPEN THAT REMEMBERS WHICH ONE IT WAS** (E3.2.1.5, schema v10): «She
# lives here» compiled to the same undescribed OPEN as «Where does she live?», and came back as it.


def _she_lives(adverb):
    return skeleton_from_conllu(f"She lives {adverb} .", [
        ("1", "She", "she", "PRON", "2", "nsubj"),
        ("2", "lives", "live", "VERB", "0", "root"),
        ("3", adverb, adverb, "ADV", "2", "advmod"),
        ("4", ".", ".", "PUNCT", "2", "punct"),
    ])


@pytest.mark.parametrize("adverb, role, deixis, distance", [
    ("here", Role.LOCATION, "place", "proximal"),
    ("there", Role.LOCATION, "place", "distal"),
    ("now", Role.TIME, "time", "proximal"),
    ("then", Role.TIME, "time", "distal"),
])
def test_a_DEICTIC_adverb_is_an_open_that_remembers_it_and_is_said_back(compiler, adverb, role,
                                                                        deixis, distance):
    from tk2.language.decompile import Decompiler

    out = compiler.compile(_she_lives(adverb))
    lives = next(r for r in out.zip.rows if getattr(r, "predicate", None) == "live.v")
    assert lives.boxes[role].head == Open(deixis=deixis, distance=distance)

    said = Decompiler().decompile(out.zip)
    assert said.text == f"She lives {adverb}.", "a statement — never «Where/When does she live?»"


# **A DEMONSTRATIVE IS POINTED AT TOO** (E3.2.1.6): its row carries `distance` and `number` and no
# `deixis`, so the v10 guard — keyed on `deixis` alone — let «This is good» come back as «Who is
# good?». A slot the speaker pointed at is said back from the rows, whichever row it was.


def _pointed_subject(word, lemma, copula):
    return skeleton_from_conllu(f"{word} {copula} good .", [
        ("1", word, lemma, "PRON", "3", "nsubj"),
        ("2", copula, "be", "AUX", "3", "cop"),
        ("3", "good", "good", "ADJ", "0", "root"),
        ("4", ".", ".", "PUNCT", "3", "punct"),
    ])


def _pointed_object(word, lemma):
    return skeleton_from_conllu(f"She saw {word} .", [
        ("1", "She", "she", "PRON", "2", "nsubj"),
        ("2", "saw", "see", "VERB", "0", "root"),
        ("3", word, lemma, "PRON", "2", "obj"),
        ("4", ".", ".", "PUNCT", "2", "punct"),
    ])


# «That» is not here, and not by choice: as a PRONOUN it reads as the RELATIVE today and is lost in
# silence — «That is good» compiles with no subject and nothing unplaced. Reported with E3.2.1.6;
# the decompiling half of «that» is held by the pure-zip test in `test_language_decompile.py`.
@pytest.mark.parametrize("word, lemma, copula, distance, number", [
    ("This", "this", "is", "proximal", "sg"),
    ("These", "this", "are", "proximal", "pl"),
    ("Those", "that", "are", "distal", "pl"),
])
def test_a_DEMONSTRATIVE_is_an_open_that_remembers_it_and_is_said_back(compiler, word, lemma,
                                                                       copula, distance, number):
    from tk2.language.decompile import Decompiler

    pointed = Open(distance=distance, number=number)

    subject = compiler.compile(_pointed_subject(word, lemma, copula))
    good = next(r for r in subject.zip.rows if r.kind == "content")
    assert good.boxes[Role.PATIENT].head == pointed
    said = Decompiler().decompile(subject.zip)
    assert said.text == f"{word} {copula} good.", "a statement, agreeing — never «Who is good?»"

    obj = compiler.compile(_pointed_object(word.lower(), lemma))
    saw = next(r for r in obj.zip.rows if getattr(r, "predicate", None) == "see.v")
    assert saw.boxes[Role.PATIENT].head == pointed
    said = Decompiler().decompile(obj.zip)
    # a hand-written skeleton carries no tense, so the clause comes back in the present
    assert said.text == f"She sees {word.lower()}.", "a statement — never «What does she see?»"


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
# where «not» scopes over a modal — word order for an adverb (frame), the row for an auxiliary
# (`db/0036`). Skeletons are stanza's parses, measured 2026-09-24.
# ------------------------------------------------------------------------------------------------

def _thinks(*words):
    """«A calculator <words> think .» — every word before the verb hangs off it, as stanza hangs
    an auxiliary (`aux`), a «not» (`advmod`, PART) and an epistemic adverb (`advmod`, ADV)."""
    tags = {"not": ("PART", "advmod"), "does": ("AUX", "aux")}
    rows = [("1", "A", "a", "DET", "2", "det"),
            ("2", "calculator", "calculator", "NOUN", str(len(words) + 3), "nsubj")]
    for at, word in enumerate(words, start=3):
        upos, dep = tags.get(word, ("ADV", "advmod") if word.endswith("ly") else ("AUX", "aux"))
        rows.append((str(at), word, "do" if word == "does" else word, upos,
                     str(len(words) + 3), dep))
    rows += [(str(len(words) + 3), "think", "think", "VERB", "0", "root"),
             (str(len(words) + 4), ".", ".", "PUNCT", str(len(words) + 3), "punct")]
    return skeleton_from_conllu(" ".join(("A calculator", *words, "think.")), rows)


def _scope_of(out) -> list[str]:
    return [r.modality.value if r.kind == "modality" else r.kind
            for r in out.zip.rows if r.kind in ("negation", "modality")]


@pytest.mark.parametrize("words, scope", [
    (("must", "not"), ["necessity", "negation"]),             # □¬ — a prohibition
    (("need", "not"), ["negation", "necessity"]),             # ¬□ — an exemption
    (("can", "not"), ["negation", "possibility"]),            # ¬◇ — it read ◇¬ until `db/0036`
    (("cannot",), ["negation", "possibility"]),               # ¬◇ — it read a bare `think`
    (("might", "not"), ["possibility", "negation"]),          # ◇¬
    (("necessarily", "does", "not"), ["necessity", "negation"]),   # □¬ — it read ¬□
    (("does", "not", "necessarily"), ["negation", "necessity"]),   # ¬□ — `t-md-2`'s order
    (("possibly", "does", "not"), ["possibility", "negation"]),    # ◇¬ — it read ¬◇
])
def test_the_SCOPE_of_a_negation_and_a_modality_is_the_one_the_sentence_says(compiler, words,
                                                                             scope):
    """An ADVERB scopes by WORD ORDER — the one before the other outscopes it (the tree's shape,
    frame). An AUXILIARY always stands before its «not», so position cannot say it: the row does,
    `following_negation` (`db/0036`, knowledge). Every word is placed and nothing abstains."""
    out = compiler.compile(_thinks(*words))

    assert _scope_of(out) == scope
    assert out.unplaced == () and out.abstained == ()
    assert main_row(out).truth == 1.0


def test_an_AMBIGUOUS_may_not_withholds_the_clause_rather_than_toss_a_coin(compiler):
    """«may not» is ¬◇ as permission and ◇¬ as a guess, and neither half is true under both: «may»
    alone claims what the permission denies, «not» alone what the guess only allows. The clause is
    withheld — its words back in `unplaced`, the reason in `abstained`, and nothing claimed."""
    out = compiler.compile(_thinks("may", "not"))

    assert _scope_of(out) == []
    assert {"may", "not", "think"} <= set(out.unplaced)
    assert any("«may not»" in why and "withheld" in why for why in out.abstained)
    assert not any(getattr(r, "truth", None) == 1.0 for r in out.zip.rows)


def test_a_withheld_ANTECEDENT_takes_its_conditional_with_it(compiler):
    """Why withheld and not merely unclaimed: «if you may not go, I stay» with the clause kept and
    its modal dropped would still claim IMPLY(go, stay) — a conditional the speaker never said.

    **AND THE CONSEQUENT GOES TOO** (`E3.12.5.9.13`, the Captain 2026-09-26). «I stay» was left
    stated, unclaimed and joined to nothing — a row that claims nothing and that no form can say.
    This test pinned that residue until the ruling; it is withheld with its antecedent now."""
    out = compiler.compile(skeleton_from_conllu("If you may not go , I stay .", [
        ("1", "If", "if", "SCONJ", "5", "mark"),
        ("2", "you", "you", "PRON", "5", "nsubj"),
        ("3", "may", "may", "AUX", "5", "aux"),
        ("4", "not", "not", "PART", "5", "advmod"),
        ("5", "go", "go", "VERB", "8", "advcl"),
        ("6", ",", ",", "PUNCT", "8", "punct"),
        ("7", "I", "I", "PRON", "8", "nsubj"),
        ("8", "stay", "stay", "VERB", "0", "root"),
        ("9", ".", ".", "PUNCT", "8", "punct"),
    ]))

    assert not [r for r in out.zip.rows if r.kind == "join"]
    assert not [r for r in out.zip.rows if getattr(r, "predicate", None)], "nothing stranded"
    assert {"If", "may", "not", "go", "I", "stay"} <= set(out.unplaced)
    assert any("stated and unclaimed" in why for why in out.abstained)


def test_a_modal_row_with_NO_scope_withholds_rather_than_defaults(compiler):
    """No default hidden in code: a table from before `db/0036` says nothing about «must», and the
    station withholds the clause instead of assuming the negation sits inside."""
    from tk2.language.closed import ClosedClasses
    from tk2.migrations import discover

    v18 = next(m for m in discover() if m.number == 33).load().CLOSED_CLASS_ROWS
    out = Compiler(ClosedClasses(v18, "db/0033 (test)")).compile(_thinks("must", "not"))

    assert _scope_of(out) == []
    assert any("following_negation" in why for why in out.abstained)


def test_a_disjunction_of_CANNOTs_is_not_free_choice(compiler):
    """«you cannot have tea or you cannot have coffee» — ¬◇ twice, and free choice is a fact about
    ◇: the disjunction claims only itself (`db/0017`), not both halves."""
    rows = [("1", "You", "you", "PRON", "3", "nsubj"), ("2", "cannot", "cannot", "AUX", "3", "aux"),
            ("3", "have", "have", "VERB", "0", "root"), ("4", "tea", "tea", "NOUN", "3", "obj"),
            ("5", "or", "or", "CCONJ", "8", "cc"), ("6", "you", "you", "PRON", "8", "nsubj"),
            ("7", "cannot", "cannot", "AUX", "8", "aux"), ("8", "have", "have", "VERB", "3", "conj"),
            ("9", "coffee", "coffee", "NOUN", "8", "obj"), ("10", ".", ".", "PUNCT", "3", "punct")]
    out = compiler.compile(skeleton_from_conllu("You cannot have tea or you cannot have coffee .",
                                                rows))

    assert _row(out, "r0").truth is None and _row(out, "r1").truth is None
    assert next(r for r in out.zip.rows if r.kind == "join").truth == 1.0


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


# ------------------------------------------------------------------------------------------------
# the number the speaker stated — schema v6. The CoNLL-U here carries no FEATS, so a test ABOUT the
# feature states it by hand, exactly as the imperative block does for `Mood`.
# ------------------------------------------------------------------------------------------------

def _with_number(skeleton, marked: dict):
    """`{index: "Plur"}` — stanza puts UD's `Number` on the token and these fixtures do not."""
    from dataclasses import replace as _replace
    words = tuple(_replace(w, feats={**w.feats, "Number": marked[w.index]})
                  if w.index in marked else w
                  for w in skeleton.words)
    return _replace(skeleton, words=words)


def _eats(marked: dict):
    return _with_number(skeleton_from_conllu("Cats eat fish .", [
        ("1", "Cats", "cat", "NOUN", "2", "nsubj"),
        ("2", "eat", "eat", "VERB", "0", "root"),
        ("3", "fish", "fish", "NOUN", "2", "obj"),
        ("4", ".", ".", "PUNCT", "2", "punct"),
    ]), marked)


def test_the_NUMBER_the_noun_carries_reaches_the_box(compiler):
    """«Software can be MINDS» and «software can be A MIND» compiled to ONE box until 2026-09-20,
    so the decompiler had two renderings of it and both were wrong. UD had said which all along."""
    out = compiler.compile(_eats({0: "Plur", 2: "Sing"}))
    boxes = main_row(out).boxes

    assert boxes[Role.AGENT].number == "pl"
    assert boxes[Role.PATIENT].number == "sg", "and the singular is STATED, not the absence of pl"


def test_a_noun_the_parse_does_not_MARK_gets_no_number(compiler):
    """**NOTHING SAID IS AN ANSWER, NOT A GAP** — a mass noun, and a box the brain builds for
    itself. A number nobody stated is a number the decompiler must not speak, so the field stays
    empty rather than defaulting to the singular that happens to render."""
    box = main_row(compiler.compile(_eats({0: "Plur"}))).boxes[Role.PATIENT]

    assert box.number is None, "`fish` was left unmarked and the station invented nothing"


def test_a_value_UD_does_not_use_here_reads_as_NOTHING(compiler):
    """`Ptan`, `Coll`, `Dual` — the transcription answers for the two English marks and abstains on
    the rest, because a value it cannot spell is not a value it may guess at (req 8)."""
    box = main_row(compiler.compile(_eats({0: "Ptan"}))).boxes[Role.AGENT]

    assert box.number is None


def test_a_PRONOUN_keeps_its_number_in_its_ROW_and_not_in_the_box(compiler):
    """**ONE FACT, ONE HOME.** A pronoun's number is a column of its `language_closed_classes` row
    and the decompiler reads it from there — writing it into the box as well would give one fact two
    homes, and a fact with two homes drifts."""
    out = compiler.compile(_with_number(skeleton_from_conllu("They eat fish .", [
        ("1", "They", "they", "PRON", "2", "nsubj"),
        ("2", "eat", "eat", "VERB", "0", "root"),
        ("3", "fish", "fish", "NOUN", "2", "obj"),
        ("4", ".", ".", "PUNCT", "2", "punct"),
    ]), {0: "Plur", 2: "Sing"}))

    assert main_row(out).boxes[Role.AGENT].number is None


def test_an_ADJECTIVE_heading_a_box_is_not_a_noun_and_takes_no_number(compiler):
    """«The cat is cute» — the complement's head is `cute.a`. Only an OPEN-CLASS NOUN carries the
    mark, so the gate is on the part of speech and not on the presence of the feature."""
    out = compiler.compile(_with_number(skeleton_from_conllu("The cats are cute .", [
        ("1", "The", "the", "DET", "2", "det"),
        ("2", "cats", "cat", "NOUN", "4", "nsubj"),
        ("3", "are", "be", "AUX", "4", "cop"),
        ("4", "cute", "cute", "ADJ", "0", "root"),
        ("5", ".", ".", "PUNCT", "4", "punct"),
    ]), {1: "Plur", 3: "Plur"}))
    boxes = main_row(out).boxes

    assert boxes[Role.COMPLEMENT].number is None, "an adjective has no grammatical number"
    assert boxes[Role.PATIENT].number == "pl", "and the noun beside it still has its own"


def test_NUMBER_is_orthogonal_to_COUNT_and_to_DETERMINATION(compiler):
    """Req 26 keeps the three apart and this is the sentence that needs all of them: «the three
    cats» is DEFINITE and COUNTED and PLURAL, and v1's single field could say one at a time."""
    out = compiler.compile(_with_number(skeleton_from_conllu("The three cats eat .", [
        ("1", "The", "the", "DET", "3", "det"),
        ("2", "three", "three", "NUM", "3", "nummod"),
        ("3", "cats", "cat", "NOUN", "4", "nsubj"),
        ("4", "eat", "eat", "VERB", "0", "root"),
        ("5", ".", ".", "PUNCT", "4", "punct"),
    ]), {2: "Plur"}))
    box = main_row(out).boxes[Role.AGENT]

    assert (box.determination, box.count, box.number) == (Determination.DEFINITE, 3, "pl")


def test_a_QUANTIFIED_phrase_carries_its_number_on_the_RESTRICTION(compiler):
    """The binder takes the noun and the box keeps only the variable (req 36), so the number goes
    where the noun went. A variable has no grammatical number — it is not a word anybody said."""
    out = compiler.compile(_with_number(skeleton_from_conllu("All cats eat .", [
        ("1", "All", "all", "DET", "2", "det"),
        ("2", "cats", "cat", "NOUN", "3", "nsubj"),
        ("3", "eat", "eat", "VERB", "0", "root"),
        ("4", ".", ".", "PUNCT", "3", "punct"),
    ]), {1: "Plur"}))
    box = main_row(out).boxes[Role.AGENT]
    binder = next(r for r in out.zip.rows if r.kind == "quantifier")

    assert isinstance(box.head, Var) and box.number is None
    assert binder.restriction.head == "cat.n" and binder.restriction.number == "pl"


@pytest.mark.skeleton
def test_a_RELATIVE_clause_on_a_referring_phrase_BINDS_its_variable():
    """«The cat that sleeps is happy» is ONE cat described twice, and req 36 says a shared variable
    is how a zip says «the same one». There was no binder to share, so this branch minted a variable
    and bound it with nothing — and **threw the noun away**, because a binder's `restriction` is the
    only place a shared noun can live:

        r0  sleep.v     agent       = Var(y2)
        r1  happy.a     experiencer = {definite, sg, head: Var(y2)}      <- cat.n is GONE

    The zip said «the definite singular thing that sleeps is happy». Schema v8 lets a binder
    introduce a variable **without quantifying it**, which is what this phrase does: it quantified
    nothing, and inventing a force from the determination would say more than the sentence did.
    """
    from tk2.language import StanzaSkeletons
    from tk2.language.utterance import compile_utterance
    from tk2.tkzip.schema import QuantifierRow
    from tools.drill_gate import DRILL_CONTEXT

    provider = StanzaSkeletons()
    compiler = Compiler(standing_closed_classes())
    zip_ = compile_utterance(compiler, provider("The cat that sleeps is happy."),
                             DRILL_CONTEXT).zip

    binders = [row for row in zip_.rows if isinstance(row, QuantifierRow)]
    assert len(binders) == 1, "the shared variable has no binder"
    binder = binders[0]

    assert binder.quantity is None, "the phrase quantified nothing and the zip must not say it did"
    assert binder.restriction.head == "cat.n", "the noun must survive, in the restriction"
    assert binder.restriction.determination is Determination.DEFINITE

    used = {box.head.name for row in zip_.rows if getattr(row, "boxes", None)
            for box in row.boxes.values() if isinstance(box.head, Var)}
    assert used == {binder.binds}, f"{used - {binder.binds}} are bound by nothing"


@pytest.mark.skeleton
def test_no_drill_sentence_compiles_to_a_FREE_VARIABLE():
    """A variable nothing binds is not a rendering problem — it is a MALFORMED ZIP, and the
    decompiler is right to refuse it. This walks the whole corpus because the defect above reached
    only one drill sentence (`t-dc-4`) while breaking a whole construction: «the cat that sleeps»,
    «the man who ate the fish», «minds you trust».
    """
    from tests.fixtures.drill import CASES as DRILL
    from tk2.language import StanzaSkeletons
    from tk2.language.utterance import compile_utterance
    from tk2.tkzip.schema import QuantifierRow
    from tools.drill_gate import DRILL_CONTEXT

    provider = StanzaSkeletons()
    compiler = Compiler(standing_closed_classes())
    loose = []
    for drill_case in DRILL:
        skeletons = provider(drill_case.sentence)
        if not skeletons:
            continue
        zip_ = compile_utterance(compiler, skeletons, DRILL_CONTEXT).zip
        bound = {row.binds for row in zip_.rows if isinstance(row, QuantifierRow)}
        used = {box.head.name for row in zip_.rows if getattr(row, "boxes", None)
                for box in row.boxes.values() if isinstance(box.head, Var)}
        used |= {row.restriction.head.name for row in zip_.rows
                 if isinstance(row, QuantifierRow) and isinstance(row.restriction.head, Var)}
        if used - bound:
            loose.append((drill_case.id, sorted(used - bound)))

    assert not loose, f"{loose} name variables no row binds"


IN_ITALY = skeleton_from_conllu("In Italy, you may drive in France.", [
    ("1", "In", "in", "ADP", "2", "case"),
    ("2", "Italy", "italy", "PROPN", "6", "obl"),
    ("3", ",", ",", "PUNCT", "6", "punct"),
    ("4", "you", "you", "PRON", "6", "nsubj"),
    ("5", "may", "may", "AUX", "6", "aux"),
    ("6", "drive", "drive", "VERB", "0", "root"),
    ("7", "in", "in", "ADP", "8", "case"),
    ("8", "France", "france", "PROPN", "6", "obl"),
])

AS_A_DOCTOR = skeleton_from_conllu("As a doctor I disagree.", [
    ("1", "As", "as", "ADP", "3", "case"),
    ("2", "a", "a", "DET", "3", "det"),
    ("3", "doctor", "doctor", "NOUN", "5", "obl"),
    ("4", "I", "i", "PRON", "5", "nsubj"),
    ("5", "disagree", "disagree", "VERB", "0", "root"),
])

IN_THE_MORNING = skeleton_from_conllu("In the morning, I go to work.", [
    ("1", "In", "in", "ADP", "3", "case"),
    ("2", "the", "the", "DET", "3", "det"),
    ("3", "morning", "morning", "NOUN", "6", "obl"),
    ("4", ",", ",", "PUNCT", "6", "punct"),
    ("5", "I", "i", "PRON", "6", "nsubj"),
    ("6", "go", "go", "VERB", "0", "root"),
    ("7", "to", "to", "ADP", "8", "case"),
    ("8", "work", "work", "NOUN", "6", "obl"),
])


def test_a_CONTESTED_fronted_phrase_is_the_DOMAIN_and_the_other_keeps_its_box(compiler):
    """«In Italy, you may drive IN FRANCE» — the drill calls this «the sentence that proved `domain`
    is not `location`», and the station used to lose it: Italy took the one `location` box and
    **France went to `unplaced`**. A word dropped, not merely misfiled.

    Two phrases wanting one box is the only evidence in the tree that one of them is not about the
    event at all, and the fronted one is the frame (req 6, rules reqs 6-7).
    """
    out = compiler.compile(IN_ITALY)

    domains = [r for r in out.zip.rows if r.kind == "domain"]
    assert len(domains) == 1 and domains[0].domain.head == "italy.n"
    assert not out.zip.unplaced, f"{out.zip.unplaced} was dropped"

    clause = next(r for r in out.zip.rows if r.kind == "content")
    assert clause.boxes[Role.LOCATION].head == "france.n", "France must keep the box it earned"


def test_a_fronted_AS_phrase_is_a_capacity_and_therefore_a_DOMAIN(compiler):
    """«AS A DOCTOR I disagree; as a father I understand» must be two positions honestly held, not
    a KB contradiction — which is the whole of rules reqs 6-7 and why the fifth prefix element
    exists. `as` is the one marker English keeps for the frame itself."""
    out = compiler.compile(AS_A_DOCTOR)

    domains = [r for r in out.zip.rows if r.kind == "domain"]
    assert len(domains) == 1 and domains[0].domain.head == "doctor.n"
    assert domains[0].domain.marker == "as"


def test_a_fronted_phrase_whose_box_NOBODY_CONTESTS_is_not_a_domain(compiler):
    """**THE HALF THAT MATTERS.** «A marked nominal before the subject is a domain» fits every
    drill case and swallows this one too — `tools/domain_bench.py` measured it at FIVE false
    positives out of six. «In the morning» is a TIME and «to work» a destination: two `obl`s, two
    different boxes, no contest, no frame.

    A domain nobody stated indexes a claim to a context it was never held in, and the evaluator
    would then never contradict it. A miss only leaves the station where it was.
    """
    out = compiler.compile(IN_THE_MORNING)

    assert not [r for r in out.zip.rows if r.kind == "domain"]
    clause = next(r for r in out.zip.rows if r.kind == "content")
    assert clause.boxes[Role.TIME].head == "morning.n"


AS_FAR_AS_PAST = skeleton_from_conllu("I walked as far as the bridge.", [
    ("1", "I", "i", "PRON", "2", "nsubj"),
    ("2", "walked", "walk", "VERB", "0", "root"),
    ("3", "as", "as", "ADV", "4", "advmod"),
    ("4", "far", "far", "ADV", "2", "advmod"),
    ("5", "as", "as", "ADP", "3", "fixed"),      # stanza's PAST-tense reading: a fixed expression
    ("6", "the", "the", "DET", "7", "det"),
    ("7", "bridge", "bridge", "NOUN", "4", "obl"),
])

AS_FAR_AS_PRESENT = skeleton_from_conllu("I walk as far as the station.", [
    ("1", "I", "i", "PRON", "2", "nsubj"),
    ("2", "walk", "walk", "VERB", "0", "root"),
    ("3", "as", "as", "ADV", "4", "advmod"),
    ("4", "far", "far", "ADV", "2", "advmod"),
    ("5", "as", "as", "ADP", "7", "case"),       # the SAME phrase, read as a case marker
    ("6", "the", "the", "DET", "7", "det"),
    ("7", "station", "station", "NOUN", "4", "obl"),
])


@pytest.mark.parametrize("skeleton,noun", [(AS_FAR_AS_PAST, "bridge.n"),
                                           (AS_FAR_AS_PRESENT, "station.n")])
def test_a_MULTI_WORD_marker_that_swallowed_the_nominals_head_is_still_its_marker(
        compiler, skeleton, noun):
    """«I walked AS FAR AS the bridge» came back «I walked.» — the bridge simply gone.

    **AND BOTH INSTRUMENTS CALLED IT FINE.** The fixpoint reported `dir-3` FIXED, because a
    truncated sentence recompiles to the same truncated zip; the drill gate reported «no common
    ground», because a row that is MISSING is not a row that CONFLICTS.

    Two defects, one sentence. `db/0033` supplies the marker the table never had — `db/0015` named
    it in the ruling that created `destination`, and the family `to` · `toward` · `up to` was
    otherwise complete. And the nominal could not SEE it: stanza reads this phrase two ways, and in
    the past tense the second `as` is `fixed` to the first, so the bridge hangs off `far` — a token
    INSIDE the marker — with no `case` child at all.

    Reading the marker's SPAN holds under either analysis, which is what makes it a rule about the
    tree's shape rather than a patch for one tense.
    """
    out = compiler.compile(skeleton)
    clause = next(r for r in out.zip.rows if r.kind == "content")

    assert not out.zip.unplaced, f"{out.zip.unplaced} was dropped"
    assert clause.boxes[Role.DESTINATION].head == noun
    assert clause.boxes[Role.DESTINATION].marker == "as far as", (
        "req 65 puts «no arrival entailed» in the MARKER, so the box must carry which one it was")


# ------------------------------------------------------------------------------------------------
# G1 — a purpose is an implication, and its subject is controlled (the Captain, 2026-09-25;
# `db/0037`). Skeletons are stanza's parses, measured 2026-09-25; FEATS added by hand as above.
# ------------------------------------------------------------------------------------------------

def _with_feats(skeleton, **by_index):
    from dataclasses import replace as _replace
    words = tuple(_replace(w, feats={**w.feats, **by_index[f"w{w.index}"]})
                  if f"w{w.index}" in by_index else w for w in skeleton.words)
    return _replace(skeleton, words=words)


_INF, _FIN = {"VerbForm": "Inf"}, {"VerbForm": "Fin", "Tense": "Pres"}

GO_TO_SLEEP = _with_feats(skeleton_from_conllu("I go to sleep .", [
    ("1", "I", "I", "PRON", "2", "nsubj"),
    ("2", "go", "go", "VERB", "0", "root"),
    ("3", "to", "to", "PART", "4", "mark"),
    ("4", "sleep", "sleep", "VERB", "2", "advcl"),
    ("5", ".", ".", "PUNCT", "2", "punct"),
]), w1=_FIN, w3=_INF)

GO_TO_SLEEP_BECAUSE = _with_feats(skeleton_from_conllu("I go to sleep because I 'm tired .", [
    ("1", "I", "I", "PRON", "2", "nsubj"),
    ("2", "go", "go", "VERB", "0", "root"),
    ("3", "to", "to", "PART", "4", "mark"),
    ("4", "sleep", "sleep", "VERB", "2", "advcl"),
    ("5", "because", "because", "SCONJ", "8", "mark"),
    ("6", "I", "I", "PRON", "8", "nsubj"),
    ("7", "'m", "be", "AUX", "8", "cop"),
    ("8", "tired", "tired", "ADJ", "2", "advcl"),
    ("9", ".", ".", "PUNCT", "2", "punct"),
]), w1=_FIN, w3=_INF, w6=_FIN)

BECAUSE_GO_TO_SLEEP = _with_feats(skeleton_from_conllu("Because I 'm tired , I go to sleep .", [
    ("1", "Because", "because", "SCONJ", "4", "mark"),
    ("2", "I", "I", "PRON", "4", "nsubj"),
    ("3", "'m", "be", "AUX", "4", "cop"),
    ("4", "tired", "tired", "ADJ", "7", "advcl"),
    ("5", ",", ",", "PUNCT", "7", "punct"),
    ("6", "I", "I", "PRON", "7", "nsubj"),
    ("7", "go", "go", "VERB", "0", "root"),
    ("8", "to", "to", "PART", "9", "mark"),
    ("9", "sleep", "sleep", "VERB", "7", "advcl"),
    ("10", ".", ".", "PUNCT", "7", "punct"),
]), w2=_FIN, w6=_FIN, w8=_INF)

IN_ORDER_TO_SLEEP = _with_feats(skeleton_from_conllu("I go in order to sleep .", [
    ("1", "I", "I", "PRON", "2", "nsubj"),
    ("2", "go", "go", "VERB", "0", "root"),
    ("3", "in", "in", "ADP", "6", "mark"),
    ("4", "order", "order", "NOUN", "3", "fixed"),
    ("5", "to", "to", "PART", "6", "mark"),
    ("6", "sleep", "sleep", "VERB", "2", "advcl"),
    ("7", ".", ".", "PUNCT", "2", "punct"),
]), w1=_FIN, w5=_INF)

BROUGHT_HIM_TO_HELP = _with_feats(skeleton_from_conllu("I brought him to help .", [
    ("1", "I", "I", "PRON", "2", "nsubj"),
    ("2", "brought", "bring", "VERB", "0", "root"),
    ("3", "him", "he", "PRON", "2", "obj"),
    ("4", "to", "to", "PART", "5", "mark"),
    ("5", "help", "help", "VERB", "2", "advcl"),
    ("6", ".", ".", "PUNCT", "2", "punct"),
]), w1={"VerbForm": "Fin", "Tense": "Past"}, w4=_INF)

GAVE_HER_MONEY_TO_BUY = _with_feats(skeleton_from_conllu("I gave her money to buy food .", [
    ("1", "I", "I", "PRON", "2", "nsubj"),
    ("2", "gave", "give", "VERB", "0", "root"),
    ("3", "her", "she", "PRON", "2", "iobj"),
    ("4", "money", "money", "NOUN", "2", "obj"),
    ("5", "to", "to", "PART", "6", "mark"),
    ("6", "buy", "buy", "VERB", "2", "advcl"),
    ("7", "food", "food", "NOUN", "6", "obj"),
    ("8", ".", ".", "PUNCT", "2", "punct"),
]), w1={"VerbForm": "Fin", "Tense": "Past"}, w5=_INF)

WANT_TO_SLEEP = _with_feats(skeleton_from_conllu("I want to sleep .", [
    ("1", "I", "I", "PRON", "2", "nsubj"),
    ("2", "want", "want", "VERB", "0", "root"),
    ("3", "to", "to", "PART", "4", "mark"),
    ("4", "sleep", "sleep", "VERB", "2", "xcomp"),
    ("5", ".", ".", "PUNCT", "2", "punct"),
]), w1=_FIN, w3=_INF)

TO_SEE_THE_LIGURIAN_SEA = _with_feats(skeleton_from_conllu("I went to Genoa to see the Ligurian sea .", [
    ("1", "I", "I", "PRON", "2", "nsubj"),
    ("2", "went", "go", "VERB", "0", "root"),
    ("3", "to", "to", "ADP", "4", "case"),
    ("4", "Genoa", "Genoa", "PROPN", "2", "obl"),
    ("5", "to", "to", "PART", "6", "mark"),
    ("6", "see", "see", "VERB", "2", "advcl"),
    ("7", "the", "the", "DET", "9", "det"),
    ("8", "Ligurian", "Ligurian", "ADJ", "9", "amod"),
    ("9", "sea", "sea", "NOUN", "6", "obj"),
    ("10", ".", ".", "PUNCT", "2", "punct"),
]), w1={"VerbForm": "Fin", "Tense": "Past"}, w5=_INF)

EVERYONE_WORKS_TO_EARN = _with_feats(skeleton_from_conllu("Everyone works to earn money .", [
    ("1", "Everyone", "everyone", "PRON", "2", "nsubj"),
    ("2", "works", "work", "VERB", "0", "root"),
    ("3", "to", "to", "PART", "4", "mark"),
    ("4", "earn", "earn", "VERB", "2", "advcl"),
    ("5", "money", "money", "NOUN", "4", "obj"),
    ("6", ".", ".", "PUNCT", "2", "punct"),
]), w1=_FIN, w3=_INF)


def _joins(out):
    return {r.name: r for r in out.zip.rows if r.kind == "join"}


def _clause_of(out, predicate):
    return next(r for r in out.zip.rows if r.kind == "content" and r.predicate == predicate)


def test_a_PURPOSE_is_an_implication_that_claims_the_act_and_not_the_end(compiler):
    """«I go to sleep» — the speaker says he goes; that the going leads to the sleep is the join's
    claim, and the sleep itself is not claimed at all (the Captain: *«maybe there is a dog barking
    and I can't sleep»*). It was an AND, and the sleep was claimed."""
    out = compiler.compile(GO_TO_SLEEP)
    go, sleep = _clause_of(out, "go.v"), _clause_of(out, "sleep.v")
    (join,) = _joins(out).values()

    assert join.operator is Operator.IMPLY
    assert join.operands == [go.name, sleep.name], "the ACT is the antecedent, the end follows"
    assert (join.truth, go.truth, sleep.truth) == (1.0, 1.0, None)
    assert not out.zip.unplaced


def test_the_END_of_a_purpose_keeps_no_theatre_because_the_format_cannot_say_after_ITS_PARTNER(
        compiler):
    """The act at t-1, the end at t — relative to each other. `Theatre` is relative to the
    UTTERANCE and the infinitive carries no tense, so nothing is written: the order lives in the
    IMPLY's operands, antecedent first (tkzip req 37). A partner-relative time axis is what is
    missing, and it is not invented here."""
    out = compiler.compile(GO_TO_SLEEP)

    assert _clause_of(out, "go.v").theatre is not None
    assert _clause_of(out, "sleep.v").theatre is None


def test_IN_ORDER_TO_is_the_same_purpose_as_TO(compiler):
    """`db/0037` corrected the row: it compiled imply/both with the introduced clause FIRST —
    «Because money earns, I work» — the end claimed and the arrow reversed."""
    from tools.roundtrip import canonical

    assert canonical(compiler.compile(IN_ORDER_TO_SLEEP).zip) == \
        canonical(compiler.compile(GO_TO_SLEEP).zip)


def test_a_COMPLEMENT_is_not_a_purpose_and_still_opens_no_row(compiler):
    """«I want to sleep» — the same `to`, the same `mark`, and an `xcomp`: `db/0032` rules it opens
    no row, and the purpose row names `advcl` and only `advcl`."""
    out = compiler.compile(WANT_TO_SLEEP)

    assert not _joins(out)
    assert [r.predicate for r in out.zip.rows if r.kind == "content"] == ["want.v"]
    assert out.placement[2] == "structure", "the infinitive marker, as it always was"


def test_the_CONTROLLED_subject_is_the_matrix_subject_when_the_matrix_has_no_complement(compiler):
    """«I go to sleep» — I sleep. The subject a non-finite clause does not say is the one its
    matrix does, in the box the end's own predicate gives a subject (`db/0018`)."""
    out = compiler.compile(GO_TO_SLEEP)

    assert _clause_of(out, "sleep.v").boxes[Role.AGENT] == _clause_of(out, "go.v").boxes[Role.AGENT]


def test_the_CONTROLLED_subject_is_the_OBJECT_when_the_matrix_has_one(compiler):
    """«I brought HIM to help» — he helps. The ruling's `obj` half; `iobj` is read the same way."""
    out = compiler.compile(BROUGHT_HIM_TO_HELP)
    helper = _clause_of(out, "help.v").boxes[Role.AGENT].head

    assert helper == _clause_of(out, "bring.v").boxes[Role.PATIENT].head
    assert isinstance(helper, Open) and helper.gender == "m"


def test_TWO_complements_name_no_controller_and_the_subject_is_left_unsaid(compiler):
    """«I gave her money to buy food» — the rule names ONE complement, and this matrix has two. The
    subject is left empty and the abstention says why; picking one would be a guess in the zip."""
    out = compiler.compile(GAVE_HER_MONEY_TO_BUY)
    buy = _clause_of(out, "buy.v")

    assert set(buy.boxes) == {Role.PATIENT}, "the food, and no buyer"
    assert any("two complements" in why for why in out.abstained)


def test_a_QUANTIFIED_controller_s_binder_comes_to_scope_the_purpose(compiler):
    """«Everyone works to earn money» — the earner is the same everyone, so the variable appears in
    both rows, and a binder scoping only the act would leave it free in the end."""
    out = compiler.compile(EVERYONE_WORKS_TO_EARN)
    binder = next(r for r in out.zip.rows if r.kind == "quantifier")
    (join,) = _joins(out).values()

    assert _clause_of(out, "earn.v").boxes[Role.AGENT].head == Var(name=binder.binds)
    assert binder.scopes == join.name


def test_a_purpose_BRACKETS_the_same_whichever_side_the_because_stands(compiler):
    """«I go to sleep because I'm tired» and «Because I'm tired, I go to sleep» are one thought —
    what the tiredness explains is the going-to-sleep. The purpose extends its act the way a `conj`
    extends its clause; attached to the outermost join instead, the two orders were two trees."""
    from tools.roundtrip import canonical

    after = compiler.compile(GO_TO_SLEEP_BECAUSE)
    before = compiler.compile(BECAUSE_GO_TO_SLEEP)
    assert canonical(after.zip) == canonical(before.zip)

    joins = _joins(after)
    purpose = next(j for j in joins.values() if _clause_of(after, "go.v").name in j.operands)
    because = next(j for j in joins.values() if j is not purpose)
    assert because.operands == [_clause_of(after, None).name, purpose.name], (
        "the tiredness implies the WHOLE purpose, in that order")


def test_an_ADJECTIVE_in_the_end_of_a_purpose_does_not_claim_the_end_again(compiler):
    """«…to see the LIGURIAN sea» — the adjective's conjunction takes the seeing row's place, so it
    takes its truth: held CLAIMED, it asserted the seeing all over again. The adjective's own row
    stays claimed — the sea is Ligurian whether or not I saw it."""
    out = compiler.compile(TO_SEE_THE_LIGURIAN_SEA)
    see = _clause_of(out, "see.v")
    wrapper = next(j for j in _joins(out).values() if see.name in j.operands)
    ligurian = next(r for r in out.zip.rows if r.name in wrapper.operands and r is not see)

    assert (see.truth, wrapper.truth, ligurian.truth) == (None, None, 1.0)
    assert see.boxes[Role.EXPERIENCER] == _clause_of(out, "go.v").boxes[Role.AGENT], (
        "and the seer is the goer")


# ------------------------------------------------------------------------------------------------
# G7 — the understood marker is stored (schema v9, the Captain 2026-09-25)
# ------------------------------------------------------------------------------------------------

GAVE_ANNA_A_BOOK = skeleton_from_conllu("I gave Anna a book .", [
    ("1", "I", "I", "PRON", "2", "nsubj"),
    ("2", "gave", "give", "VERB", "0", "root"),
    ("3", "Anna", "Anna", "PROPN", "2", "iobj"),
    ("4", "a", "a", "DET", "5", "det"),
    ("5", "book", "book", "NOUN", "2", "obj"),
    ("6", ".", ".", "PUNCT", "2", "punct"),
])

GAVE_A_BOOK_TO_ANNA = skeleton_from_conllu("I gave a book to Anna .", [
    ("1", "I", "I", "PRON", "2", "nsubj"),
    ("2", "gave", "give", "VERB", "0", "root"),
    ("3", "a", "a", "DET", "4", "det"),
    ("4", "book", "book", "NOUN", "2", "obj"),
    ("5", "to", "to", "ADP", "6", "case"),
    ("6", "Anna", "Anna", "PROPN", "2", "obl"),
    ("7", ".", ".", "PUNCT", "2", "punct"),
])

TOLD_HER_THE_TRUTH = skeleton_from_conllu("I told her the truth .", [
    ("1", "I", "I", "PRON", "2", "nsubj"),
    ("2", "told", "tell", "VERB", "0", "root"),
    ("3", "her", "she", "PRON", "2", "iobj"),
    ("4", "the", "the", "DET", "5", "det"),
    ("5", "truth", "truth", "NOUN", "2", "obj"),
    ("6", ".", ".", "PUNCT", "2", "punct"),
])


def test_a_BARE_indirect_object_carries_the_recipient_s_marker_understood(compiler):
    """«I gave Anna a book» is «to Anna» — the meaning — said bare — the surface. The marker is the
    table's one recipient marker, never a word of the compiler's."""
    bare = main_row(compiler.compile(GAVE_ANNA_A_BOOK)).boxes[Role.RECIPIENT]
    said = main_row(compiler.compile(GAVE_A_BOOK_TO_ANNA)).boxes[Role.RECIPIENT]

    assert bare.marker == compiler.table.marker_for("recipient") == said.marker == "to"
    assert (bare.marker_implicit, said.marker_implicit) == (True, None)


def test_a_bare_PRONOUN_recipient_is_understood_the_same_way(compiler):
    box = main_row(compiler.compile(TOLD_HER_THE_TRUTH)).boxes[Role.RECIPIENT]
    assert (box.marker, box.marker_implicit) == ("to", True)


# ------------------------------------------------------------------------------------------------
# G9 — an AND under a supposition is supposed, like its halves (the Captain, 2026-09-25)
# ------------------------------------------------------------------------------------------------

IF_I_GO_AND_YOU_STAY = skeleton_from_conllu("If I go and you stay , I am happy .", [
    ("1", "If", "if", "SCONJ", "3", "mark"),
    ("2", "I", "I", "PRON", "3", "nsubj"),
    ("3", "go", "go", "VERB", "10", "advcl"),
    ("4", "and", "and", "CCONJ", "6", "cc"),
    ("5", "you", "you", "PRON", "6", "nsubj"),
    ("6", "stay", "stay", "VERB", "3", "conj"),
    ("7", ",", ",", "PUNCT", "10", "punct"),
    ("8", "I", "I", "PRON", "10", "nsubj"),
    ("9", "am", "be", "AUX", "10", "cop"),
    ("10", "happy", "happy", "ADJ", "0", "root"),
    ("11", ".", ".", "PUNCT", "10", "punct"),
])


def test_an_AND_inside_a_supposition_is_SUPPOSED_like_its_halves(compiler):
    """Both conditions must hold — a boolean AND, which is the zip's reading. The defect was only
    its truth: CLAIMED over two supposed halves, it asserted the going and the staying."""
    out = compiler.compile(IF_I_GO_AND_YOU_STAY)
    joins = _joins(out)
    conditional = next(j for j in joins.values() if j.operator is Operator.IMPLY)
    both = joins[conditional.operands[0]]

    assert both.operator is Operator.AND
    assert (conditional.truth, both.truth) == (1.0, None)
    assert all(out.zip.row(name).truth is None for name in both.operands)


# ------------------------------------------------------------------------------------------------
# t-dc-5 — «and» + a CAUSAL discourse adverb is the adverb's join (the Captain, 2026-09-25)
# ------------------------------------------------------------------------------------------------

def _and_then(adverb):
    return skeleton_from_conllu(f"It rained and {adverb} the river flooded .", [
        ("1", "It", "it", "PRON", "2", "expl"),
        ("2", "rained", "rain", "VERB", "0", "root"),
        ("3", "and", "and", "CCONJ", "7", "cc"),
        ("4", adverb, adverb, "ADV", "7", "advmod"),
        ("5", "the", "the", "DET", "6", "det"),
        ("6", "river", "river", "NOUN", "7", "nsubj"),
        ("7", "flooded", "flood", "VERB", "2", "conj"),
        ("8", ".", ".", "PUNCT", "2", "punct"),
    ])


@pytest.mark.parametrize("adverb", ["therefore", "consequently", "thus"])
def test_AND_plus_a_CAUSAL_adverb_is_the_adverb_s_implication_replacing_the_and(compiler, adverb):
    """«A and therefore B» claims A, B and A → B — ONE join, the implication, over halves that stay
    claimed. The adverb's row says IMPLY (`db/0013`); the class is read off it, not off the word."""
    out = compiler.compile(_and_then(adverb))
    (join,) = _joins(out).values()
    rain, flood = _clause_of(out, "rain.v"), _clause_of(out, "flood.v")

    assert join.operator is Operator.IMPLY
    assert join.operands == [rain.name, flood.name], "the marked clause is the consequent"
    assert (join.truth, rain.truth, flood.truth) == (1.0, 1.0, 1.0)


@pytest.mark.parametrize("adverb", ["also", "nevertheless"])
def test_a_NON_causal_adverb_does_not_replace_the_and_and_builds_no_second_join(compiler, adverb):
    """«and ALSO» is the coordination's own AND said again — nothing to add, so nothing is built, and
    the zip stays a tree. A parked reading («nevertheless» is concessive) is still named."""
    out = compiler.compile(_and_then(adverb))
    (join,) = _joins(out).values()

    assert join.operator is Operator.AND
    if adverb == "nevertheless":
        assert any("concessive" in why for why in out.abstained)


# ------------------------------------------------------------------------------------------------
# E3.12.5 (1) — what remains must be ENTAILED (the Captain, 2026-09-26). A partial zip is quality
# only where what it still claims follows from the sentence; under a negation or an attitude a cut
# widens the claim, and the clause is withheld. Skeletons are stanza's parses, measured 2026-09-26.
# ------------------------------------------------------------------------------------------------

def _claims(out) -> list:
    return [r for r in out.zip.rows if getattr(r, "truth", None) == 1.0]


YOU_NEED_NOT_DRIVE = skeleton_from_conllu("You need not drive .", [
    ("1", "You", "you", "PRON", "2", "nsubj"),
    ("2", "need", "need", "VERB", "0", "root"),
    ("3", "not", "not", "PART", "4", "advmod"),
    ("4", "drive", "drive", "VERB", "2", "xcomp"),
    ("5", ".", ".", "PUNCT", "2", "punct"),
])


def _want(*negation):
    """«I (don't) want to go .» — `go` is an `xcomp`, which opens no row (`db/0032`)."""
    words = [("I", "I", "PRON", "nsubj"), *negation, ("want", "want", "VERB", "root"),
             ("to", "to", "PART", "mark"), ("go", "go", "VERB", "xcomp"),
             (".", ".", "PUNCT", "punct")]
    want = next(at for at, w in enumerate(words, start=1) if w[0] == "want")
    rows = [(str(at), form, lemma, upos,
             "0" if dep == "root" else str(at + 1) if form == "to" else str(want), dep)
            for at, (form, lemma, upos, dep) in enumerate(words, start=1)]
    return skeleton_from_conllu(" ".join(w[0] for w in words), rows)


def test_a_word_cut_from_under_a_NEGATION_withholds_the_clause(compiler):
    """`E3.3.11.6` «You need not drive» compiled ¬need(you), «drive» unplaced — and ¬need(you) is
    STRONGER than what was said: «you need nothing». Recording the word does not help; what remains
    is a claim the sentence does not entail, so the clause goes, its reason with it."""
    out = compiler.compile(YOU_NEED_NOT_DRIVE)

    assert _claims(out) == [] and not [r for r in out.zip.rows if r.kind == "negation"]
    assert {"You", "need", "not", "drive"} <= set(out.unplaced)
    assert any("«drive»" in why and "negation" in why and "withheld" in why
               for why in out.abstained)


def test_the_same_cut_from_a_CLAIMED_clause_only_weakens_it_and_stays(compiler):
    """`E3.12.1.3` «I don't want to go» is withheld on the same ground — and «I want to go» is not:
    want(me) with «go» unplaced says less than the sentence, and says nothing it did not."""
    negated = compiler.compile(_want(("do", "do", "AUX", "aux"), ("n't", "not", "PART", "advmod")))
    plain = compiler.compile(_want())

    assert _claims(negated) == [] and "go" in negated.unplaced
    assert [r.predicate for r in _claims(plain)] == ["want.v"] and plain.unplaced == ("go",)
    assert not any("withheld" in why for why in plain.abstained)


I_M_NOT_SOFTWARE_BUT_A_MIND = skeleton_from_conllu("I'm not a software but I am a mind .", [
    ("1", "I'm", "be", "AUX", "4", "cop"),
    ("2", "not", "not", "PART", "4", "advmod"),
    ("3", "a", "a", "DET", "4", "det"),
    ("4", "software", "software", "NOUN", "0", "root"),
    ("5", "but", "but", "CCONJ", "9", "cc"),
    ("6", "I", "I", "PRON", "9", "nsubj"),
    ("7", "am", "be", "AUX", "9", "cop"),
    ("8", "a", "a", "DET", "9", "det"),
    ("9", "mind", "mind", "NOUN", "4", "conj"),
    ("10", ".", ".", "PUNCT", "4", "punct"),
])


def test_a_withheld_negated_clause_takes_its_JOIN_and_the_JOINING_WORD_with_it(compiler):
    """`t-ws-6`: stanza fuses «I'm», the subject goes with it, and ¬[_ is a software] was claimed.
    The negated clause is withheld; the clause joined to it stands on its own truth — and «but»,
    whose relation went with the clause, is unplaced rather than counted as understood."""
    out = compiler.compile(I_M_NOT_SOFTWARE_BUT_A_MIND)

    assert not _joins(out) and not [r for r in out.zip.rows if r.kind == "negation"]
    (mind,) = _claims(out)
    assert mind.boxes[Role.COMPLEMENT].head == "mind.n"
    assert {"I'm", "not", "software", "but"} <= set(out.unplaced)


I_WOULD_LIKE_TO_KNOW = skeleton_from_conllu(
    "I would like to know what you think about yourself .", [
        ("1", "I", "I", "PRON", "3", "nsubj"),
        ("2", "would", "would", "AUX", "3", "aux"),
        ("3", "like", "like", "VERB", "0", "root"),
        ("4", "to", "to", "PART", "5", "mark"),
        ("5", "know", "know", "VERB", "3", "xcomp"),
        ("6", "what", "what", "PRON", "8", "obj"),
        ("7", "you", "you", "PRON", "8", "nsubj"),
        ("8", "think", "think", "VERB", "5", "ccomp"),
        ("9", "about", "about", "ADP", "10", "case"),
        ("10", "yourself", "yourself", "PRON", "8", "obl"),
        ("11", ".", ".", "PUNCT", "3", "punct"),
    ])


def test_an_attitude_whose_LINK_is_unplaced_is_withheld_and_its_matrix_with_it(compiler):
    """`E3.12.1.4` `t-mo-4` claimed att(like, me) over think(you, what) — «I like what you think»:
    «know», the link between the verb and what it holds, was unplaced. The attitude goes; the matrix
    comes back as a clause of its own (`E3.12.5.1`) and is judged like one — and «would», which set
    no time, is an OPERATOR cut from it (`E3.12.5.2`), so it does not come back as «I like»."""
    out = compiler.compile(I_WOULD_LIKE_TO_KNOW)

    assert _claims(out) == [] and not [r for r in out.zip.rows if r.kind == "attitude"]
    assert {"I", "would", "like", "know", "think", "yourself"} <= set(out.unplaced)
    assert any("«know»" in why and "link" in why for why in out.abstained)
    assert any("operator" in why for why in out.abstained)


def test_a_matrix_whose_attitude_was_withheld_is_judged_ON_ITS_OWN(compiler):
    """`E3.12.5.1` — «He said that he knew the muffin man»: the content loses «muffin» under the
    saying and is withheld; the saying lost nothing of its own, and «he said» is entailed — so it
    stays, claimed, as the clause it would have been had there been no attitude to dissolve into."""
    out = compiled(compiler, "He said that he knew the muffin man .")

    (said,) = _claims(out)
    assert said.predicate == "say.v" and not [r for r in out.zip.rows if r.kind == "attitude"]
    assert {"knew", "muffin", "man"} <= set(out.unplaced) and "said" not in out.unplaced


def test_an_OPERATOR_cut_from_a_claimed_clause_withholds_it_and_a_time_set_is_placed(compiler):
    """`E3.12.5.2` — «would» is a `theatre` row that compiles to a tense `_tense` never reads: it is
    unplaced, and an operator gone is not a weakening — «I would go» is not «I go». «will» sets the
    future and is placed."""
    def go(aux):
        return compiler.compile(skeleton_from_conllu(f"I {aux} go .", [
            ("1", "I", "I", "PRON", "3", "nsubj"), ("2", aux, aux, "AUX", "3", "aux"),
            ("3", "go", "go", "VERB", "0", "root"), ("4", ".", ".", "PUNCT", "3", "punct")]))

    would, will = go("would"), go("will")
    assert _claims(would) == [] and set(would.unplaced) == {"I", "would", "go"}
    assert any("«would»" in why and "operator" in why for why in would.abstained)
    assert will.unplaced == () and main_row(will).theatre is not None


IF_HE_KNEW_THE_MUFFIN_MAN = skeleton_from_conllu("If he knew the muffin man , I stay .", [
    ("1", "If", "if", "SCONJ", "3", "mark"),
    ("2", "he", "he", "PRON", "3", "nsubj"),
    ("3", "knew", "know", "VERB", "9", "advcl"),
    ("4", "the", "the", "DET", "6", "det"),
    ("5", "muffin", "muffin", "NOUN", "6", "compound"),
    ("6", "man", "man", "NOUN", "3", "obj"),
    ("7", ",", ",", "PUNCT", "9", "punct"),
    ("8", "I", "I", "PRON", "9", "nsubj"),
    ("9", "stay", "stay", "VERB", "0", "root"),
    ("10", ".", ".", "PUNCT", "9", "punct"),
])


def test_a_cut_from_an_ANTECEDENT_withholds_it_and_the_implication_with_it(compiler):
    """`E3.12.5.3` — «if he knew the man, I stay» is STRONGER than «if he knew the muffin man, I
    stay»: the antecedent is downward-entailing. The antecedent goes, the implication with it, and
    «I stay» — only ever supposed — claims nothing."""
    out = compiler.compile(IF_HE_KNEW_THE_MUFFIN_MAN)

    assert not _joins(out) and _claims(out) == []
    assert {"If", "knew", "muffin", "man"} <= set(out.unplaced)
    assert any("antecedent" in why for why in out.abstained)


def _muffin_man_sleeps(quantifier):
    return skeleton_from_conllu(f"{quantifier} muffin man sleeps .", [
        ("1", quantifier, quantifier.lower(), "DET", "3", "det"),
        ("2", "muffin", "muffin", "NOUN", "3", "compound"),
        ("3", "man", "man", "NOUN", "4", "nsubj"),
        ("4", "sleeps", "sleep", "VERB", "0", "root"),
        ("5", ".", ".", "PUNCT", "4", "punct"),
    ])


def test_a_cut_from_a_UNIVERSAL_s_restriction_withholds_and_from_an_EXISTENTIAL_s_does_not(compiler):
    """`E3.12.5.3` — «every man sleeps» does not follow from «every muffin man sleeps»; «some man
    sleeps» does follow from «some muffin man sleeps». The force of the binder decides, which is
    logic (`UPWARD_RESTRICTION`)."""
    every = compiler.compile(_muffin_man_sleeps("Every"))
    some = compiler.compile(_muffin_man_sleeps("Some"))

    assert _claims(every) == [] and not [r for r in every.zip.rows if r.kind == "quantifier"]
    assert any("restriction of a universal" in why for why in every.abstained)
    assert [r.predicate for r in _claims(some)] == ["sleep.v"] and some.unplaced == ("muffin",)


I_ASKED_ANNA_WHERE_SHE_LIVES = skeleton_from_conllu("I asked Anna where she lives .", [
    ("1", "I", "I", "PRON", "2", "nsubj"),
    ("2", "asked", "ask", "VERB", "0", "root"),
    ("3", "Anna", "Anna", "PROPN", "2", "iobj"),
    ("4", "where", "where", "ADV", "6", "advmod"),
    ("5", "she", "she", "PRON", "6", "nsubj"),
    ("6", "lives", "live", "VERB", "2", "advcl"),
    ("7", ".", ".", "PUNCT", "2", "punct"),
])


def test_a_clause_beside_a_LONE_iobj_is_withheld_rather_than_joined_by_an_unsaid_and(compiler):
    """`E3.3.2.7.1` — stanza reads the reported question as `advcl` beside an `iobj` with no object,
    and the station joined it with the «and» nobody said: the question became the SPEAKER's own.
    The clause may be the object the `iobj` presupposes, so it is withheld; «I asked» stays."""
    out = compiler.compile(I_ASKED_ANNA_WHERE_SHE_LIVES)

    assert [r.predicate for r in out.zip.rows if r.kind == "content"] == ["ask.v"]
    assert not _joins(out) and main_row(out).truth == 1.0
    assert {"Anna", "where", "she", "lives"} <= set(out.unplaced)


def _glitters(*negation):
    """«(Not) all that glitters is (not) gold .» as stanza parses both."""
    rows, at = [], 1
    if negation == ("before",):
        rows.append((str(at), "Not", "not", "PART", "2", "advmod"))
        at += 1
    quantifier = at
    rows += [(str(at), "all", "all", "DET", "HEAD", "nsubj"),
             (str(at + 1), "that", "that", "PRON", str(at + 2), "nsubj"),
             (str(at + 2), "glitters", "glitter", "VERB", str(quantifier), "acl:relcl"),
             (str(at + 3), "is", "be", "AUX", "HEAD", "cop")]
    at += 4
    if negation == ("after",):
        rows.append((str(at), "not", "not", "PART", "HEAD", "advmod"))
        at += 1
    gold = at
    rows += [(str(at), "gold", "gold", "NOUN", "0", "root"),
             (str(at + 1), ".", ".", "PUNCT", str(gold), "punct")]
    rows = [tuple(str(gold) if v == "HEAD" else v for v in row) for row in rows]
    return skeleton_from_conllu(" ".join(r[1] for r in rows), rows)


def test_a_universal_BEFORE_a_negation_is_withheld_like_may_not(compiler):
    """`E3.12.1.2` `aw-13` — «All that glitters is not gold» is ¬∀ and ∀¬, and the surface says
    both: E3.12.5 (5) withholds it on «may not»'s precedent. «NOT all that glitters is gold» puts
    the negation first, the order the speaker used is the scope, and nothing is withheld."""
    ambiguous = compiler.compile(_glitters("after"))
    settled = compiler.compile(_glitters("before"))

    assert _claims(ambiguous) == [] and not [r for r in ambiguous.zip.rows if r.kind != "content"]
    assert {"all", "that", "glitters", "not", "gold"} <= set(ambiguous.unplaced)
    assert any("«all … not»" in why for why in ambiguous.abstained)

    assert [r.kind for r in settled.zip.rows if r.kind in ("negation", "quantifier")] == \
        ["negation", "quantifier"]
    assert settled.unplaced == ()


# ------------------------------------------------------------------------------------------------
# `E3.12.5.9` — «only» and the conditionals (the Captain's rulings `E3.12.5.9.12`, 2026-09-26)
#
# The trees are stanza's own, copied from the bench (`202609261500_only-and-the-conditionals.md`).
# ------------------------------------------------------------------------------------------------


def _tree(text, rows):
    return skeleton_from_conllu(text, rows)


def _named(out, predicate):
    return next(r for r in out.zip.rows if getattr(r, "predicate", None) == predicate)


def _the_join(out):
    joins = [r for r in out.zip.rows if r.kind == "join"]
    assert len(joins) == 1, joins
    return joins[0]


def _only_if(particle="only"):
    """«I stay home ONLY if it rains.» — the particle hangs off the conditional clause's head."""
    return _tree(f"I stay home {particle} if it rains.", [
        ("1", "I", "i", "PRON", "2", "nsubj"), ("2", "stay", "stay", "VERB", "0", "root"),
        ("3", "home", "home", "ADV", "2", "advmod"), ("4", particle, particle, "ADV", "7", "advmod"),
        ("5", "if", "if", "SCONJ", "7", "mark"), ("6", "it", "it", "PRON", "7", "nsubj"),
        ("7", "rains", "rain", "VERB", "2", "advcl"), ("8", ".", ".", "PUNCT", "2", "punct"),
    ])


def test_UNLESS_negates_the_clause_it_introduces(compiler):
    """`E3.12.5.9.4` — «Unless it rains, I go out» is ¬R → G. The row has said `polarity: negative`
    since v1, and nothing read it: the station compiled «if it rains, I go»."""
    out = compiler.compile(_tree("Unless it rains, I go out.", [
        ("1", "Unless", "unless", "SCONJ", "3", "mark"), ("2", "it", "it", "PRON", "3", "nsubj"),
        ("3", "rains", "rain", "VERB", "6", "advcl"), ("4", ",", ",", "PUNCT", "6", "punct"),
        ("5", "I", "i", "PRON", "6", "nsubj"), ("6", "go", "go", "VERB", "0", "root"),
        ("7", "out", "out", "ADV", "6", "advmod"), ("8", ".", ".", "PUNCT", "6", "punct"),
    ]))
    rain, go, join = _named(out, "rain.v"), _named(out, "go.v"), _the_join(out)

    assert join.operator is Operator.IMPLY and join.operands == [rain.name, go.name]
    assert [r.scopes for r in out.zip.rows if r.kind == "negation"] == [rain.name], \
        "the negation is on the rain, and on nothing else"
    assert (rain.truth, go.truth) == (None, None), "a condition claims neither half"


def test_NOR_carries_its_negation_in_its_operator_and_gets_no_second_one(compiler):
    """«nor» also says `polarity: negative` — and its operator is already ¬(a ∨ b). Reading the
    polarity again would negate the second clause twice (`NEGATED_OPERATORS`)."""
    out = compiler.compile(_tree("I did not swim, nor did I run.", [
        ("1", "I", "i", "PRON", "4", "nsubj"), ("2", "did", "do", "AUX", "4", "aux"),
        ("3", "not", "not", "PART", "4", "advmod"), ("4", "swim", "swim", "VERB", "0", "root"),
        ("5", ",", ",", "PUNCT", "9", "punct"), ("6", "nor", "nor", "CCONJ", "9", "cc"),
        ("7", "did", "do", "AUX", "9", "aux"), ("8", "I", "i", "PRON", "9", "nsubj"),
        ("9", "run", "run", "VERB", "4", "conj"), ("10", ".", ".", "PUNCT", "4", "punct"),
    ]))
    run = _named(out, "run.v")

    assert _the_join(out).operator is Operator.NOR
    assert not [r for r in out.zip.rows if r.kind == "negation" and r.scopes == run.name]


def test_WHEN_heading_an_adverbial_clause_is_its_JOINER_and_claims_what_both_readings_entail(
        compiler):
    """`E3.12.5.9.5` — stanza tags «when» `advmod`, never `mark`, so its conjunction row was never
    reached: the clause was ANDed on, both halves claimed, and a time box opened nobody asked about.
    Under an `advcl` the tree says it is the subordinator (`ClosedClasses._by_adverbial`). The row
    says it is `ambiguous` — generic ∀t or episodic — and only the implication BOTH readings entail
    is claimed; the rest is recorded, not dropped (`E3.12.5.9.12` (2))."""
    out = compiler.compile(_tree("I stay home when it rains.", [
        ("1", "I", "i", "PRON", "2", "nsubj"), ("2", "stay", "stay", "VERB", "0", "root"),
        ("3", "home", "home", "ADV", "2", "advmod"), ("4", "when", "when", "ADV", "6", "advmod"),
        ("5", "it", "it", "PRON", "6", "nsubj"), ("6", "rains", "rain", "VERB", "2", "advcl"),
        ("7", ".", ".", "PUNCT", "2", "punct"),
    ]))
    rain, stay, join = _named(out, "rain.v"), _named(out, "stay.v"), _the_join(out)

    assert join.operator is Operator.IMPLY and join.operands == [rain.name, stay.name]
    assert (rain.truth, stay.truth) == (None, None)
    assert Role.TIME not in rain.boxes, "nobody asked when"
    assert out.placement[3] == "join" and out.unplaced == ()
    assert any(line.startswith("«when»: generic") for line in out.abstained)


def test_ONLY_IF_replaces_the_direction_and_keeps_the_row_order(compiler):
    """`E3.12.5.9.2` — «I stay home only if it rains» is S → R: CONV over the operands «if» would
    have had (row order carries scope — the Captain's normal form, (3)), and neither half claimed:
    «only if» does not claim «if» (1). It compiled IMPLY(R, S), the reverse claim, with «only» in a
    manner box."""
    out = compiler.compile(_only_if())
    rain, stay, join = _named(out, "rain.v"), _named(out, "stay.v"), _the_join(out)

    assert join.operator is Operator.CONV and join.operands == [rain.name, stay.name]
    assert (rain.truth, stay.truth) == (None, None)
    assert Role.MANNER not in rain.boxes, "«only» is not a manner of raining"
    assert out.placement[3] == "focus" and out.unplaced == ()


def test_JUST_IF_is_the_same_exclusive_meaning_as_ONLY_IF(compiler):
    """One meaning, four words (`db/0039`) — the station reads the row, never the word."""
    assert _the_join(compiler.compile(_only_if("just"))).operator is Operator.CONV


def test_the_associate_is_the_clause_the_particle_hangs_off_whichever_it_is(compiler):
    """«It rains only if I STAY HOME» — the condition is the staying: CONV(stay, rain), rain → stay.
    And «home» is placed: the manner box it shared with «only» (`E3.12.5.9.7`) is its own again."""
    out = compiler.compile(_tree("It rains only if I stay home.", [
        ("1", "It", "it", "PRON", "2", "nsubj"), ("2", "rains", "rain", "VERB", "0", "root"),
        ("3", "only", "only", "ADV", "6", "advmod"), ("4", "if", "if", "SCONJ", "6", "mark"),
        ("5", "I", "i", "PRON", "6", "nsubj"), ("6", "stay", "stay", "VERB", "2", "advcl"),
        ("7", "home", "home", "ADV", "6", "advmod"), ("8", ".", ".", "PUNCT", "2", "punct"),
    ]))
    rain, stay, join = _named(out, "rain.v"), _named(out, "stay.v"), _the_join(out)

    assert join.operator is Operator.CONV and join.operands == [stay.name, rain.name]
    assert stay.boxes[Role.MANNER].head == "home.r" and out.unplaced == ()


def test_IF_AND_ONLY_IF_is_EQ_in_both_of_stanzas_trees(compiler):
    """`E3.12.5.9.8` — without commas «only» is `conj` of the first «if»; with them, `advmod` of the
    second, and the clause itself is misread as a `conj`. The four words between the two markers
    are the same in both, and «if» ∧ «only if» over one pair is EQ (ruling 3) — no row for the
    phrase. It was over-withheld (`E3.12.5.10`) and misread as a lone IMPLY."""
    plain = compiler.compile(_tree("If and only if it rains, I stay home.", [
        ("1", "If", "if", "SCONJ", "6", "mark"), ("2", "and", "and", "CCONJ", "3", "cc"),
        ("3", "only", "only", "ADV", "1", "conj"), ("4", "if", "if", "SCONJ", "6", "mark"),
        ("5", "it", "it", "PRON", "6", "nsubj"), ("6", "rains", "rain", "VERB", "9", "advcl"),
        ("7", ",", ",", "PUNCT", "9", "punct"), ("8", "I", "i", "PRON", "9", "nsubj"),
        ("9", "stay", "stay", "VERB", "0", "root"), ("10", "home", "home", "ADV", "9", "advmod"),
        ("11", ".", ".", "PUNCT", "9", "punct"),
    ]))
    commas = compiler.compile(_tree("I stay home if, and only if, it rains.", [
        ("1", "I", "i", "PRON", "2", "nsubj"), ("2", "stay", "stay", "VERB", "0", "root"),
        ("3", "home", "home", "ADV", "2", "advmod"), ("4", "if", "if", "SCONJ", "11", "mark"),
        ("5", ",", ",", "PUNCT", "4", "punct"), ("6", "and", "and", "CCONJ", "11", "cc"),
        ("7", "only", "only", "ADV", "8", "advmod"), ("8", "if", "if", "SCONJ", "11", "mark"),
        ("9", ",", ",", "PUNCT", "8", "punct"), ("10", "it", "it", "PRON", "11", "nsubj"),
        ("11", "rains", "rain", "VERB", "2", "conj"), ("12", ".", ".", "PUNCT", "2", "punct"),
    ]))
    for out in (plain, commas):
        rain, stay, join = _named(out, "rain.v"), _named(out, "stay.v"), _the_join(out)
        assert join.operator is Operator.EQ and join.operands == [rain.name, stay.name]
        assert (rain.truth, stay.truth) == (None, None) and join.truth == 1.0
        assert out.unplaced == () and not out.abstained


def test_EXACTLY_WHEN_is_identifying_necessary_and_sufficient(compiler):
    """«exactly» is the identifying meaning (`db/0039`): the condition necessary AND sufficient."""
    out = compiler.compile(_tree("I stay home exactly when it rains.", [
        ("1", "I", "i", "PRON", "2", "nsubj"), ("2", "stay", "stay", "VERB", "0", "root"),
        ("3", "home", "home", "ADV", "2", "advmod"), ("4", "exactly", "exactly", "ADV", "7", "advmod"),
        ("5", "when", "when", "ADV", "7", "advmod"), ("6", "it", "it", "PRON", "7", "nsubj"),
        ("7", "rains", "rain", "VERB", "2", "advcl"), ("8", ".", ".", "PUNCT", "2", "punct"),
    ]))
    assert _the_join(out).operator is Operator.EQ and out.unplaced == ()


def _only_cats():
    return _tree("Only cats eat fish.", [
        ("1", "Only", "only", "ADV", "2", "advmod"), ("2", "cats", "cat", "NOUN", "3", "nsubj"),
        ("3", "eat", "eat", "VERB", "0", "root"), ("4", "fish", "fish", "NOUN", "3", "obj"),
        ("5", ".", ".", "PUNCT", "3", "punct"),
    ])


def test_ONLY_on_a_NOUN_keeps_the_claim_and_adds_that_nothing_else_does(compiler):
    """`E3.12.5.9.3` — «Only cats eat fish»: the drill's `only-6` shape, ∀x (eat(x, fish) → x is a
    cat), with the frame the antecedent and «is the associate» the consequent — AND the prejacent
    kept claimed (ruling 1: on a noun it is a presupposition). It compiled «cats eat fish» with
    «only» as a manner of eating."""
    out = compiler.compile(_only_cats())
    rows = {r.name: r for r in out.zip.rows}
    claim = next(r for r in out.zip.rows if r.kind == "content" and r.truth == 1.0)
    whole = next(r for r in out.zip.rows if r.kind == "join" and r.operator is Operator.AND)
    rule = rows[whole.operands[1]]
    frame, member = (rows[name] for name in rule.operands)
    binder = next(r for r in out.zip.rows if r.kind == "quantifier")

    assert claim.predicate == "eat.v" and claim.boxes[Role.AGENT].head == "cat.n", "the prejacent"
    assert whole.operands[0] == claim.name and whole.truth == 1.0
    assert rule.operator is Operator.IMPLY and rule.truth == 1.0
    assert binder.quantity is Quantity.UNIVERSAL and binder.scopes == rule.name
    var = Var(name=binder.binds)
    assert frame.predicate == "eat.v" and frame.boxes[Role.AGENT].head == var
    assert frame.boxes[Role.PATIENT] == claim.boxes[Role.PATIENT], "the frame, the associate out"
    assert member.boxes[Role.PATIENT].head == var
    assert member.boxes[Role.COMPLEMENT].head == "cat.n", "…is the associate"
    assert (frame.truth, member.truth) == (None, None)
    assert Role.MANNER not in claim.boxes and out.unplaced == ()


def test_a_PRE_VERBAL_only_is_unplaced_and_the_claim_it_presupposes_stays(compiler):
    """`E3.12.5.9.9` — «Cats only eat fish»: the tree hangs «only» off the verb whatever the focus,
    so the associate is not given. Left unplaced; «cats eat fish» is entailed by every reading."""
    out = compiler.compile(_tree("Cats only eat fish.", [
        ("1", "Cats", "cat", "NOUN", "3", "nsubj"), ("2", "only", "only", "ADV", "3", "advmod"),
        ("3", "eat", "eat", "VERB", "0", "root"), ("4", "fish", "fish", "NOUN", "3", "obj"),
        ("5", ".", ".", "PUNCT", "3", "punct"),
    ]))
    assert out.unplaced == ("only",)
    assert main_row(out).truth == 1.0 and Role.MANNER not in main_row(out).boxes
    assert any("E3.12.5.9.9" in line for line in out.abstained)


def test_a_PRE_VERBAL_only_with_a_CONDITIONAL_in_its_reach_withholds_the_clause(compiler):
    """«I only stay home if it rains» — «only if» (S → R) or «only stay home» (R → S): neither
    direction is entailed, and «if it rains, I stay home» claimed alone would be one of them."""
    out = compiler.compile(_tree("I only stay home if it rains.", [
        ("1", "I", "i", "PRON", "3", "nsubj"), ("2", "only", "only", "ADV", "3", "advmod"),
        ("3", "stay", "stay", "VERB", "0", "root"), ("4", "home", "home", "ADV", "3", "advmod"),
        ("5", "if", "if", "SCONJ", "7", "mark"), ("6", "it", "it", "PRON", "7", "nsubj"),
        ("7", "rains", "rain", "VERB", "3", "advcl"), ("8", ".", ".", "PUNCT", "3", "punct"),
    ]))
    assert not [r for r in out.zip.rows if r.kind == "join" or getattr(r, "predicate", None)]
    assert {"only", "stay", "if", "rains"} <= set(out.unplaced)


def test_ONLY_BECAUSE_is_recorded_lost_never_silent(compiler):
    """`E3.12.5.9.11` — with both halves claimed, «only because» is not a truth function (ruling 2):
    «only» is left UNPLACED, where the zip says so, and never placed as a manner."""
    out = compiler.compile(_tree("I stayed home only because it rained.", [
        ("1", "I", "i", "PRON", "2", "nsubj"), ("2", "stayed", "stay", "VERB", "0", "root"),
        ("3", "home", "home", "ADV", "2", "advmod"), ("4", "only", "only", "ADV", "7", "advmod"),
        ("5", "because", "because", "SCONJ", "7", "mark"), ("6", "it", "it", "PRON", "7", "nsubj"),
        ("7", "rained", "rain", "VERB", "2", "advcl"), ("8", ".", ".", "PUNCT", "2", "punct"),
    ]))
    assert "only" in out.unplaced
    assert any("E3.12.5.9.11" in line for line in out.abstained)
    assert all(Role.MANNER not in r.boxes or r.boxes[Role.MANNER].head != "only.r"
               for r in out.zip.rows if r.kind == "content")


def test_PROVIDED_THAT_is_a_joining_word_and_not_a_verb_of_providing(compiler):
    """`E3.12.5.9.6` — stanza reads «provided» as a VERB heading an `advcl` with the condition as
    its `ccomp`, and the station built «I provide that it rains», all claimed. The table reads it
    as a subordinator, and the tree agrees: it governs the clause it introduces."""
    out = compiler.compile(_tree("I stay home provided that it rains.", [
        ("1", "I", "i", "PRON", "2", "nsubj"), ("2", "stay", "stay", "VERB", "0", "root"),
        ("3", "home", "home", "ADV", "2", "advmod"), ("4", "provided", "provide", "VERB", "2", "advcl"),
        ("5", "that", "that", "SCONJ", "7", "mark"), ("6", "it", "it", "PRON", "7", "nsubj"),
        ("7", "rains", "rain", "VERB", "4", "ccomp"), ("8", ".", ".", "PUNCT", "2", "punct"),
    ]))
    rain, stay, join = _named(out, "rain.v"), _named(out, "stay.v"), _the_join(out)

    assert join.operator is Operator.IMPLY and join.operands == [rain.name, stay.name]
    assert (rain.truth, stay.truth) == (None, None)
    assert not [r for r in out.zip.rows if r.kind == "attitude"], "nobody provides anything"
    assert out.placement[3] == out.placement[4] == "join" and out.unplaced == ()


def test_AS_LONG_AS_is_found_by_its_span_and_claims_neither_half(compiler):
    """`E3.12.5.9.6` + `E3.12.5.9.10` — the clause's `mark` is the LAST «as» and the table's match
    starts at the first, so the joiner was never found and the clause was ANDed on, both claimed.
    Found by the span now; and `db/0039` makes it claim neither half, as «if» does (ruling 6)."""
    out = compiler.compile(_tree("I stay home as long as it rains.", [
        ("1", "I", "i", "PRON", "2", "nsubj"), ("2", "stay", "stay", "VERB", "0", "root"),
        ("3", "home", "home", "ADV", "2", "advmod"), ("4", "as", "as", "ADV", "5", "advmod"),
        ("5", "long", "long", "ADV", "2", "advmod"), ("6", "as", "as", "SCONJ", "8", "mark"),
        ("7", "it", "it", "PRON", "8", "nsubj"), ("8", "rains", "rain", "VERB", "5", "advcl"),
        ("9", ".", ".", "PUNCT", "2", "punct"),
    ]))
    rain, stay, join = _named(out, "rain.v"), _named(out, "stay.v"), _the_join(out)

    assert join.operator is Operator.IMPLY and join.operands == [rain.name, stay.name]
    assert (rain.truth, stay.truth) == (None, None)
    assert out.unplaced == ()


def test_a_SECOND_manner_adverb_is_unplaced_not_counted(compiler):
    """`E3.12.5.9.7` — one manner box, two adverbs: the second was counted as placed and was
    nowhere in the zip. It is unplaced now, and the zip says so."""
    out = compiler.compile(_tree("I stay home quietly.", [
        ("1", "I", "i", "PRON", "2", "nsubj"), ("2", "stay", "stay", "VERB", "0", "root"),
        ("3", "home", "home", "ADV", "2", "advmod"), ("4", "quietly", "quietly", "ADV", "2", "advmod"),
        ("5", ".", ".", "PUNCT", "2", "punct"),
    ]))
    assert main_row(out).boxes[Role.MANNER].head == "home.r"
    assert out.unplaced == ("quietly",) and 3 not in out.placement



# ------------------------------------------------------------------------------------------------
# `E3.12.5.9.13` — the orphan · `E3.12.5.9.3.1` — a focus word whose meaning is not settled
# ------------------------------------------------------------------------------------------------


def test_a_row_a_withholding_leaves_STRANDED_is_withheld_too(compiler):
    """«A person is wrong when he says false» — the antecedent is withheld (the cut «false» widens
    it), and the consequent was left supposed by a conditional that no longer existed: SILENT at
    the fixpoint. Withheld with it, the sentence is WITHHELD and says why."""
    out = compiler.compile(_tree("A person is wrong when he says false.", [
        ("1", "A", "a", "DET", "2", "det"), ("2", "person", "person", "NOUN", "4", "nsubj"),
        ("3", "is", "be", "AUX", "4", "cop"), ("4", "wrong", "wrong", "ADJ", "0", "root"),
        ("5", "when", "when", "ADV", "7", "advmod"), ("6", "he", "he", "PRON", "7", "nsubj"),
        ("7", "says", "say", "VERB", "4", "advcl"), ("8", "false", "false", "ADJ", "7", "xcomp"),
        ("9", ".", ".", "PUNCT", "4", "punct"),
    ]))
    assert all(r.kind == "content" and not r.boxes and not r.predicate for r in out.zip.rows)
    assert {"person", "wrong", "says"} <= set(out.unplaced)


def test_a_RELATIVE_clause_is_held_by_its_variable_and_is_not_stranded(compiler):
    """An unclaimed row with no name pointing at it is not always stranded: a quantifier's
    restriction is held by the variable it shares — «every cat THAT SLEEPS is happy»."""
    out = compiler.compile(EVERY_CAT)
    assert [r.predicate for r in out.zip.rows if r.kind == "content"][0] == "sleep.v"
    assert out.unplaced == ()


def _strictly_if():
    return _tree("I stay home strictly if it rains.", [
        ("1", "I", "i", "PRON", "2", "nsubj"), ("2", "stay", "stay", "VERB", "0", "root"),
        ("3", "home", "home", "ADV", "2", "advmod"), ("4", "strictly", "strictly", "ADV", "2", "advmod"),
        ("5", "if", "if", "SCONJ", "7", "mark"), ("6", "it", "it", "PRON", "7", "nsubj"),
        ("7", "rains", "rain", "VERB", "2", "advcl"), ("8", ".", ".", "PUNCT", "2", "punct"),
    ])


def test_STRICTLY_IF_is_no_longer_claimed_forward(compiler):
    """`E3.12.5.9.3.1` — «strictly» has a row that says ABSTAIN (`db/0040`): it may be «only if».
    Stanza hangs it off the matrix, with the condition in its reach, so the forward implication is
    not entailed and nothing is claimed — it was «if it rains, I stay home», a wrong claim."""
    out = compiler.compile(_strictly_if())
    assert not [r for r in out.zip.rows if r.kind == "join"]
    assert {"strictly", "if", "rains", "stay"} <= set(out.unplaced)


def test_an_ABSTAINING_particle_over_its_CONDITION_withholds_the_conditional(compiler):
    """The same word hung off the condition itself — the shape «only if» has — is withheld too: the
    row gives no direction to compose."""
    out = compiler.compile(_only_if("strictly"))
    assert not [r for r in out.zip.rows if r.kind == "join"]
    assert "strictly" in out.unplaced


def test_EVEN_on_a_noun_is_unplaced_and_the_claim_stays(compiler):
    """«Even cats eat fish» claims that cats do; the rest is not a truth function. «even» is left
    unplaced, never a manner of eating."""
    out = compiler.compile(_tree("Even cats eat fish.", [
        ("1", "Even", "even", "ADV", "2", "advmod"), ("2", "cats", "cat", "NOUN", "3", "nsubj"),
        ("3", "eat", "eat", "VERB", "0", "root"), ("4", "fish", "fish", "NOUN", "3", "obj"),
        ("5", ".", ".", "PUNCT", "3", "punct"),
    ]))
    assert out.unplaced == ("Even",) and main_row(out).truth == 1.0
    assert Role.MANNER not in main_row(out).boxes
    assert any("not settled" in why for why in out.abstained)


# ------------------------------------------------------------------------------------------------
# `E3.3.11.1` · `E3.3.11.2` — THE ATTITUDE TAKES ITS MATRIX CLAUSE'S PLACE (the Captain's
# `E3.3.11.2.16`, 2026-09-26: [what stood over the matrix] · ATTITUDE · [what the complement raised])
# ------------------------------------------------------------------------------------------------

def _stack(out, name):
    """The prefix over one row, outermost first, as (kind, what) — an attitude's verb, a modality's
    value, a binder's force."""
    def what(row):
        return {"attitude": getattr(row, "verb", None),
                "modality": getattr(getattr(row, "modality", None), "value", None),
                "quantifier": getattr(getattr(row, "quantity", None), "value", None)}.get(row.kind)
    return [(r.kind, what(r)) for r in out.zip.rows if getattr(r, "scopes", None) == name]


def _content(out, predicate):
    return next(r for r in out.zip.rows if getattr(r, "predicate", None) == predicate)


def _none_of(out, *predicates):
    return not [r for r in out.zip.rows if getattr(r, "predicate", None) in predicates]


I_THINK_HE_DOES_NOT_SLEEP = _tree("I think that he does not sleep .", [
    ("1", "I", "I", "PRON", "2", "nsubj"), ("2", "think", "think", "VERB", "0", "root"),
    ("3", "that", "that", "SCONJ", "7", "mark"), ("4", "he", "he", "PRON", "7", "nsubj"),
    ("5", "does", "do", "AUX", "7", "aux"), ("6", "not", "not", "PART", "7", "advmod"),
    ("7", "sleep", "sleep", "VERB", "2", "ccomp"), ("8", ".", ".", "PUNCT", "2", "punct"),
])
I_DO_NOT_THINK_HE_SLEEPS = _tree("I do not think that he sleeps .", [
    ("1", "I", "I", "PRON", "4", "nsubj"), ("2", "do", "do", "AUX", "4", "aux"),
    ("3", "not", "not", "PART", "4", "advmod"), ("4", "think", "think", "VERB", "0", "root"),
    ("5", "that", "that", "SCONJ", "7", "mark"), ("6", "he", "he", "PRON", "7", "nsubj"),
    ("7", "sleeps", "sleep", "VERB", "4", "ccomp"), ("8", ".", ".", "PUNCT", "4", "punct"),
])
I_DONT_THINK_HE_SLEEPS = _tree("I do n't think he sleeps .", [
    ("1", "I", "I", "PRON", "4", "nsubj"), ("2", "do", "do", "AUX", "4", "aux"),
    ("3", "n't", "not", "PART", "4", "advmod"), ("4", "think", "think", "VERB", "0", "root"),
    ("5", "he", "he", "PRON", "6", "nsubj"), ("6", "sleeps", "sleep", "VERB", "4", "ccomp"),
    ("7", ".", ".", "PUNCT", "4", "punct"),
])
ANNA_BOB_DOES_NOT_BELIEVE = _tree("Anna thinks that Bob does not believe that he sleeps .", [
    ("1", "Anna", "Anna", "PROPN", "2", "nsubj"), ("2", "thinks", "think", "VERB", "0", "root"),
    ("3", "that", "that", "SCONJ", "7", "mark"), ("4", "Bob", "Bob", "PROPN", "7", "nsubj"),
    ("5", "does", "do", "AUX", "7", "aux"), ("6", "not", "not", "PART", "7", "advmod"),
    ("7", "believe", "believe", "VERB", "2", "ccomp"), ("8", "that", "that", "SCONJ", "10", "mark"),
    ("9", "he", "he", "PRON", "10", "nsubj"), ("10", "sleeps", "sleep", "VERB", "7", "ccomp"),
    ("11", ".", ".", "PUNCT", "2", "punct"),
])


def test_an_embedded_negation_stays_INSIDE_its_attitude(compiler):
    """`E3.3.11.1` — «I think that he does not sleep» compiled ¬ · ATT: «it is not so that I think
    he sleeps», the reverse scope. The attitude was appended last and so landed innermost."""
    out = compiler.compile(I_THINK_HE_DOES_NOT_SLEEP, _speech())
    assert _stack(out, _content(out, "sleep.v").name) == [("attitude", "think.v"), ("negation", None)]
    assert _none_of(out, "think.v")


@pytest.mark.parametrize("skeleton", [I_DO_NOT_THINK_HE_SLEEPS, I_DONT_THINK_HE_SLEEPS])
def test_a_matrix_negation_goes_OUTSIDE_and_no_matrix_row_is_left(compiler, skeleton):
    """`E3.3.11.2` — «I do not think that he sleeps» claimed ¬think(me) AND «I think that he
    sleeps». Literally ¬think(p), neg-raising not built (`E3.12.5` (6)): the «not» stands over the
    attitude, on the complement, and the matrix row is gone — with a «that» or without one."""
    out = compiler.compile(skeleton, _speech())
    sleeping = _content(out, "sleep.v")

    assert _stack(out, sleeping.name) == [("negation", None), ("attitude", "think.v")]
    assert _none_of(out, "think.v")
    assert all(getattr(r, "scopes", sleeping.name) == sleeping.name for r in out.zip.rows
               if r.kind not in ("content", "join"))
    assert out.unplaced == ()


def test_both_negations_keep_their_sides(compiler):
    out = compiler.compile(_tree("I do n't think that he does n't sleep .", [
        ("1", "I", "I", "PRON", "4", "nsubj"), ("2", "do", "do", "AUX", "4", "aux"),
        ("3", "n't", "not", "PART", "4", "advmod"), ("4", "think", "think", "VERB", "0", "root"),
        ("5", "that", "that", "SCONJ", "9", "mark"), ("6", "he", "he", "PRON", "9", "nsubj"),
        ("7", "does", "do", "AUX", "9", "aux"), ("8", "n't", "not", "PART", "9", "advmod"),
        ("9", "sleep", "sleep", "VERB", "4", "ccomp"), ("10", ".", ".", "PUNCT", "4", "punct"),
    ]), _speech())
    assert _stack(out, _content(out, "sleep.v").name) == [
        ("negation", None), ("attitude", "think.v"), ("negation", None)]


def test_nested_attitudes_stack_on_the_innermost_row_in_order(compiler):
    """`E3.3.11.2.3` — «Anna thinks that Bob does not believe that he sleeps»: Bob's clause stayed
    as a row because Anna's attitude scoped it, and so claimed that Bob does not believe. Seated,
    both attitudes and Bob's «not» stand over the sleeping, in the words' own order."""
    out = compiler.compile(ANNA_BOB_DOES_NOT_BELIEVE)
    assert _stack(out, _content(out, "sleep.v").name) == [
        ("attitude", "think.v"), ("negation", None), ("attitude", "believe.v")]
    assert _none_of(out, "think.v", "believe.v")
    assert [r.holder.head for r in out.zip.rows if r.kind == "attitude"] == ["anna.n", "bob.n"]


def test_the_seating_is_ORDER_INDEPENDENT(compiler):
    """`_seat` reads where each attitude came from, never the order the rows were raised in: the
    same RAW rows handed over with the two attitudes swapped — a fronted quote nests the other way
    round — seat to the same stack."""
    from tk2.language.compile import _Seating
    from tk2.tkzip.schema import AttitudeRow, Box, ContentRow, NegationRow

    def raw(order):
        rows = {"anna": ContentRow(name="r0", predicate="think.v", truth=1.0,
                                   boxes={Role.EXPERIENCER: Box(head="anna.n")}),
                "bob": ContentRow(name="r1", predicate="believe.v", truth=1.0,
                                  boxes={Role.EXPERIENCER: Box(head="bob.n")}),
                "sleep": ContentRow(name="r2", predicate="sleep.v", truth=1.0)}
        prefix = {"neg": NegationRow(name="p0", scopes="r1"),
                  "a0": AttitudeRow(name="p1", scopes="r1", holder=Box(head="anna.n"),
                                    verb="think.v"),
                  "a1": AttitudeRow(name="p2", scopes="r2", holder=Box(head="bob.n"),
                                    verb="believe.v")}
        seating = _Seating(matrix={"p1": "r0", "p2": "r1"},
                           holder={"p1": Role.EXPERIENCER, "p2": Role.EXPERIENCER},
                           inside={"p1": {"r1", "r2"}, "p2": {"r2"}})
        content = {0: rows["anna"], 3: rows["bob"], 7: rows["sleep"]}
        seated, _joins = compiler._seat(content, [prefix[k] for k in order], [], {"r0", "r1"},
                                        seating)
        return [(r.kind, getattr(r, "verb", None)) for r in seated if r.scopes == "r2"]

    assert raw(["neg", "a0", "a1"]) == raw(["a1", "neg", "a0"]) == [
        ("attitude", "think.v"), ("negation", None), ("attitude", "believe.v")]


def test_a_matrix_binder_binds_the_holder_OUTSIDE_the_attitude(compiler):
    """«Everyone thinks that I sleep» — the binder is the matrix's, and it binds the holder: ∀x ·
    ATT(x, think) over the sleeping, no think row."""
    out = compiler.compile(_tree("Everyone thinks that I sleep .", [
        ("1", "Everyone", "everyone", "PRON", "2", "nsubj"), ("2", "thinks", "think", "VERB", "0", "root"),
        ("3", "that", "that", "SCONJ", "5", "mark"), ("4", "I", "I", "PRON", "5", "nsubj"),
        ("5", "sleep", "sleep", "VERB", "2", "ccomp"), ("6", ".", ".", "PUNCT", "2", "punct"),
    ]), _speech())
    sleeping = _content(out, "sleep.v")
    binder, attitude = [r for r in out.zip.rows if getattr(r, "scopes", None) == sleeping.name]

    assert binder.kind == "quantifier" and binder.quantity is Quantity.UNIVERSAL
    assert attitude.kind == "attitude" and attitude.holder.head == Var(name=binder.binds)
    assert _none_of(out, "think.v")


def test_a_pronoun_under_a_QUANTIFIED_holder_is_withheld(compiler):
    """Ruling 8 (`E3.3.11.2.14`, on `E3.12.5` (5)'s precedent): «Nobody thinks that he sleeps» —
    «he» is bound by the holder or free, and the tree does not say which. Withheld, not decided."""
    out = compiler.compile(_tree("Nobody thinks that he sleeps .", [
        ("1", "Nobody", "nobody", "PRON", "2", "nsubj"), ("2", "thinks", "think", "VERB", "0", "root"),
        ("3", "that", "that", "SCONJ", "5", "mark"), ("4", "he", "he", "PRON", "5", "nsubj"),
        ("5", "sleeps", "sleep", "VERB", "2", "ccomp"), ("6", ".", ".", "PUNCT", "2", "punct"),
    ]))
    assert _claims(out) == [] and not [r for r in out.zip.rows if r.kind == "attitude"]
    assert any("bound by it or not" in why for why in out.abstained)


@pytest.mark.parametrize("modal, stack", [
    ("cannot", [("negation", None), ("modality", "possibility"), ("attitude", "think.v")]),
    ("can", [("modality", "possibility"), ("attitude", "think.v")]),
])
def test_a_matrix_modality_keeps_its_side(compiler, modal, stack):
    """«I cannot think that he sleeps» compiled ¬◇ over the SLEEPING — «I think that he cannot
    sleep» — and «I can think…» ◇ likewise. The matrix's modality stands over the attitude."""
    out = compiler.compile(_tree(f"I {modal} think that he sleeps .", [
        ("1", "I", "I", "PRON", "3", "nsubj"), ("2", modal, modal, "AUX", "3", "aux"),
        ("3", "think", "think", "VERB", "0", "root"), ("4", "that", "that", "SCONJ", "6", "mark"),
        ("5", "he", "he", "PRON", "6", "nsubj"), ("6", "sleeps", "sleep", "VERB", "3", "ccomp"),
        ("7", ".", ".", "PUNCT", "3", "punct"),
    ]), _speech())
    assert _stack(out, _content(out, "sleep.v").name) == stack


def test_a_complement_modality_and_binder_stay_INSIDE(compiler):
    """«I think that he can sleep» · «I think that some cat sleeps» — the complement's own prefix is
    the holder's: ATT · ◇, and ATT · ∃ read literally de dicto (ruling 1, the drill's `dere-1`) —
    no cat is asserted to exist."""
    can = compiler.compile(_tree("I think that he can sleep .", [
        ("1", "I", "I", "PRON", "2", "nsubj"), ("2", "think", "think", "VERB", "0", "root"),
        ("3", "that", "that", "SCONJ", "6", "mark"), ("4", "he", "he", "PRON", "6", "nsubj"),
        ("5", "can", "can", "AUX", "6", "aux"), ("6", "sleep", "sleep", "VERB", "2", "ccomp"),
        ("7", ".", ".", "PUNCT", "2", "punct"),
    ]), _speech())
    some = compiler.compile(_tree("I think that some cat sleeps .", [
        ("1", "I", "I", "PRON", "2", "nsubj"), ("2", "think", "think", "VERB", "0", "root"),
        ("3", "that", "that", "SCONJ", "6", "mark"), ("4", "some", "some", "DET", "5", "det"),
        ("5", "cat", "cat", "NOUN", "6", "nsubj"), ("6", "sleeps", "sleep", "VERB", "2", "ccomp"),
        ("7", ".", ".", "PUNCT", "2", "punct"),
    ]), _speech())

    assert _stack(can, _content(can, "sleep.v").name) == [
        ("attitude", "think.v"), ("modality", "possibility")]
    assert _stack(some, _content(some, "sleep.v").name) == [
        ("attitude", "think.v"), ("quantifier", "existential")]


def test_the_attitude_sits_on_its_complement_s_PLACE_not_its_row(compiler):
    """The skeptic's first amendment: «I don't think that an old man sleeps» is ∃x (old(x) ∧
    sleep(x)) under the thinking — seated on the sleeping row, the matrix's «not» would land UNDER
    the complement's ∃ and assert the man. So the stack stands on the conjunction the complement
    is: ¬ · ATT · ∃."""
    out = compiler.compile(_tree("I do n't think that an old man sleeps .", [
        ("1", "I", "I", "PRON", "4", "nsubj"), ("2", "do", "do", "AUX", "4", "aux"),
        ("3", "n't", "not", "PART", "4", "advmod"), ("4", "think", "think", "VERB", "0", "root"),
        ("5", "that", "that", "SCONJ", "9", "mark"), ("6", "an", "a", "DET", "8", "det"),
        ("7", "old", "old", "ADJ", "8", "amod"), ("8", "man", "man", "NOUN", "9", "nsubj"),
        ("9", "sleeps", "sleep", "VERB", "4", "ccomp"), ("10", ".", ".", "PUNCT", "4", "punct"),
    ]), _speech())
    (join,) = [r for r in out.zip.rows if r.kind == "join"]

    assert _content(out, "sleep.v").name in join.operands
    assert _stack(out, join.name) == [
        ("negation", None), ("attitude", "think.v"), ("quantifier", "existential")]
    assert _stack(out, _content(out, "sleep.v").name) == []


def test_a_complement_joined_to_its_own_matrix_is_withheld_and_no_join_names_itself(compiler):
    """«I think, therefore I am» — the connective joins the thinking to the being, and the being is
    the thinking's complement: the place it would take contains its own matrix. Renamed, the join
    named itself. The complement is withheld; the thinking stands, claimed."""
    out = compiler.compile(_tree("I think , therefore I am .", [
        ("1", "I", "I", "PRON", "2", "nsubj"), ("2", "think", "think", "VERB", "0", "root"),
        ("3", ",", ",", "PUNCT", "6", "punct"), ("4", "therefore", "therefore", "ADV", "6", "advmod"),
        ("5", "I", "I", "PRON", "6", "nsubj"), ("6", "am", "be", "AUX", "2", "ccomp"),
        ("7", ".", ".", "PUNCT", "2", "punct"),
    ]), _speech())
    assert [r.predicate for r in _claims(out)] == ["think.v"]
    assert not [r for r in out.zip.rows if r.kind in ("attitude", "join")]


def test_the_imperative_want_is_OUTERMOST(compiler):
    """`E3.3.11.2.7` — «Don't touch it!» was ¬WANT: «I do not want you to touch it». The want is
    the speech act and goes before every row already over the clause. And «Suppose the cat is
    hungry» composes two existing rules — the imperative's subject is the addressee, the attitude's
    holder its verb's subject — into WANT(me) · ATT(you, suppose) over the cat (`aw-20`)."""
    touch = compiler.compile(_with_mood(_tree("Do n't touch it !", [
        ("1", "Do", "do", "AUX", "3", "aux"), ("2", "n't", "not", "PART", "3", "advmod"),
        ("3", "touch", "touch", "VERB", "0", "root"), ("4", "it", "it", "PRON", "3", "obj"),
        ("5", "!", "!", "PUNCT", "3", "punct"),
    ]), 0), _speech())
    suppose = compiler.compile(_with_mood(_tree("Suppose the cat is hungry .", [
        ("1", "Suppose", "suppose", "VERB", "0", "root"), ("2", "the", "the", "DET", "3", "det"),
        ("3", "cat", "cat", "NOUN", "5", "nsubj"), ("4", "is", "be", "AUX", "5", "cop"),
        ("5", "hungry", "hungry", "ADJ", "1", "ccomp"), ("6", ".", ".", "PUNCT", "1", "punct"),
    ]), 0), _speech())

    assert _stack(touch, _content(touch, "touch.v").name) == [("attitude", "want.v"),
                                                             ("negation", None)]
    hungry = next(r for r in suppose.zip.rows if r.kind == "content")
    want, supposing = [r for r in suppose.zip.rows if r.kind == "attitude"]
    assert (want.verb, want.holder.head, want.scopes) == ("want.v", "me.n", hungry.name)
    assert (supposing.verb, supposing.holder.head, supposing.scopes) == (
        "suppose.v", "you.n", hungry.name)
    assert _none_of(suppose, "suppose.v") and hungry.truth == 1.0


def test_a_withheld_complement_brings_its_matrix_back_WITH_its_negation(compiler):
    """Trap 1: «I do not think that he knew the muffin man» — the complement is withheld under the
    attitude, the thinking comes back as its own clause with its «not» still over it (RAW), and a
    cut under a negation widens the claim: never «I think» claimed."""
    out = compiler.compile(_tree("I do not think that he knew the muffin man .", [
        ("1", "I", "I", "PRON", "4", "nsubj"), ("2", "do", "do", "AUX", "4", "aux"),
        ("3", "not", "not", "PART", "4", "advmod"), ("4", "think", "think", "VERB", "0", "root"),
        ("5", "that", "that", "SCONJ", "7", "mark"), ("6", "he", "he", "PRON", "7", "nsubj"),
        ("7", "knew", "know", "VERB", "4", "ccomp"), ("8", "the", "the", "DET", "10", "det"),
        ("9", "muffin", "muffin", "NOUN", "10", "compound"), ("10", "man", "man", "NOUN", "7", "obj"),
        ("11", ".", ".", "PUNCT", "4", "punct"),
    ]), _speech())
    assert _claims(out) == [] and _none_of(out, "think.v")
    assert {"not", "think", "muffin"} <= set(out.unplaced)


def test_an_operator_lost_from_a_dissolved_matrix_takes_the_attitude_with_it(compiler):
    """Trap 2, live before this build: «I would think that he sleeps» claimed «I think that he
    sleeps» — the matrix had dissolved, nothing named it, and its lost «would» was judged nowhere."""
    out = compiler.compile(_tree("I would think that he sleeps .", [
        ("1", "I", "I", "PRON", "3", "nsubj"), ("2", "would", "would", "AUX", "3", "aux"),
        ("3", "think", "think", "VERB", "0", "root"), ("4", "that", "that", "SCONJ", "6", "mark"),
        ("5", "he", "he", "PRON", "6", "nsubj"), ("6", "sleeps", "sleep", "VERB", "3", "ccomp"),
        ("7", ".", ".", "PUNCT", "3", "punct"),
    ]), _speech())
    assert _claims(out) == [] and not [r for r in out.zip.rows if r.kind == "attitude"]
    assert "would" in out.unplaced


def test_an_attitude_whose_matrix_is_WITHHELD_goes_with_it(compiler):
    """«He may not think that she sleeps» came back «He thinks that she sleeps»: «may not» withheld
    the thinking (`E3.12.5` (5)) and the attitude stayed. It stands or falls with its matrix."""
    out = compiler.compile(_tree("He may not think that she sleeps .", [
        ("1", "He", "he", "PRON", "4", "nsubj"), ("2", "may", "may", "AUX", "4", "aux"),
        ("3", "not", "not", "PART", "4", "advmod"), ("4", "think", "think", "VERB", "0", "root"),
        ("5", "that", "that", "SCONJ", "7", "mark"), ("6", "she", "she", "PRON", "7", "nsubj"),
        ("7", "sleeps", "sleep", "VERB", "4", "ccomp"), ("8", ".", ".", "PUNCT", "4", "punct"),
    ]))
    assert _claims(out) == [] and not [r for r in out.zip.rows if r.kind == "attitude"]


DO_YOU_THINK = _tree("Do you think that he sleeps ?", [
    ("1", "Do", "do", "AUX", "3", "aux"), ("2", "you", "you", "PRON", "3", "nsubj"),
    ("3", "think", "think", "VERB", "0", "root"), ("4", "that", "that", "SCONJ", "6", "mark"),
    ("5", "he", "he", "PRON", "6", "nsubj"), ("6", "sleeps", "sleep", "VERB", "3", "ccomp"),
    ("7", "?", "?", "PUNCT", "3", "punct"),
])


def test_an_ASKED_attitude_is_never_stored_as_a_statement(compiler):
    """`E3.3.11.2.6` — «Do you think that he sleeps?» claimed ATT(you, think) · sleep: a statement.
    An attitude row has no truth slot to ask in, so what it holds is withheld (ruling 2).

    *Amended 2026-09-27 (`E3.3.16`)*: and the narrower question does not stand. «Do you think?» is
    ANOTHER question, and an answer to it answers nothing that was asked — a cut from a clause that
    asks is never a weakening, so the question is withheld whole."""
    out = compiler.compile(DO_YOU_THINK, _speech())

    assert _claims(out) == [] and _none_of(out, "think.v", "sleep.v")
    assert not [r for r in out.zip.rows if r.kind == "attitude"]
    assert {"Do", "you", "think", "that", "he", "sleeps"} <= set(out.unplaced)
    assert any("ASKED" in why for why in out.abstained)
    assert any("in a question" in why for why in out.abstained)


def test_a_wh_word_FRONTED_out_of_its_complement_asks_through_the_attitude(compiler):
    """The skeptic's amendment: «What do you think he ate?» asks WHAT, through the thinking — the
    wh-word stands before the thinking's own head — so the thinking is not asked and takes its
    place as before. «Do you know what he ate?» asks the knowing: the question is embedded — and
    asked, the knowing cannot hold it, and «Do you know?» is another question (`E3.3.16`)."""
    fronted = compiler.compile(_tree("What do you think he ate ?", [
        ("1", "What", "what", "PRON", "6", "obj"), ("2", "do", "do", "AUX", "4", "aux"),
        ("3", "you", "you", "PRON", "4", "nsubj"), ("4", "think", "think", "VERB", "0", "root"),
        ("5", "he", "he", "PRON", "6", "nsubj"), ("6", "ate", "eat", "VERB", "4", "ccomp"),
        ("7", "?", "?", "PUNCT", "4", "punct"),
    ]), _speech())
    embedded = compiler.compile(_tree("Do you know what he ate ?", [
        ("1", "Do", "do", "AUX", "3", "aux"), ("2", "you", "you", "PRON", "3", "nsubj"),
        ("3", "know", "know", "VERB", "0", "root"), ("4", "what", "what", "PRON", "6", "obj"),
        ("5", "he", "he", "PRON", "6", "nsubj"), ("6", "ate", "eat", "VERB", "3", "ccomp"),
        ("7", "?", "?", "PUNCT", "3", "punct"),
    ]), _speech())

    eating = _content(fronted, "eat.v")
    assert _stack(fronted, eating.name) == [("attitude", "think.v")] and eating.truth == 1.0
    assert isinstance(eating.boxes[Role.PATIENT].head, Open) and _none_of(fronted, "think.v")
    assert _none_of(embedded, "know.v", "eat.v") and _claims(embedded) == []
    assert any("in a question" in why for why in embedded.abstained)


def test_a_question_mark_AFTER_a_quotation_asks_the_frame(compiler):
    """`E3.3.11.2.12` — «Did John say to Marie: "You are late"?» stored that JOHN asked Marie
    whether she is late. The `?` stands after the quotation's closing mark, so it closes the
    saying — asked, and withheld as every asked attitude is. Inside the marks it is the quote's own
    (`test_a_QUOTED_question_asks_while_the_saying_stays_claimed`). *And the saying goes with it
    since `E3.3.16`: «Did John say to Marie?» asks another question.*"""
    out = compiler.compile(_tree('Did John say to Marie : " You are late " ?', [
        ("1", "Did", "do", "AUX", "3", "aux"), ("2", "John", "John", "PROPN", "3", "nsubj"),
        ("3", "say", "say", "VERB", "0", "root"), ("4", "to", "to", "ADP", "5", "case"),
        ("5", "Marie", "Marie", "PROPN", "3", "obl"), ("6", ":", ":", "PUNCT", "3", "punct"),
        ("7", '"', '"', "PUNCT", "10", "punct"), ("8", "You", "you", "PRON", "10", "nsubj"),
        ("9", "are", "be", "AUX", "10", "cop"), ("10", "late", "late", "ADJ", "3", "ccomp"),
        ("11", '"', '"', "PUNCT", "10", "punct"), ("12", "?", "?", "PUNCT", "3", "punct"),
    ]), _speech())
    assert _claims(out) == [] and _none_of(out, "say.v")
    assert not [r for r in out.zip.rows if r.kind == "attitude"] and "late" in out.unplaced


def test_a_SUPPOSED_attitude_is_withheld(compiler):
    """`E3.3.11.2.4` — «If Anna thinks that he sleeps, I leave» claimed that Anna thinks it. A
    supposed thinking has no truth slot to go in: withheld, then the antecedent, the conditional and
    what it left stranded (`E3.12.5.9.13`)."""
    out = compiler.compile(_tree("If Anna thinks that he sleeps , I leave .", [
        ("1", "If", "if", "SCONJ", "3", "mark"), ("2", "Anna", "Anna", "PROPN", "3", "nsubj"),
        ("3", "thinks", "think", "VERB", "9", "advcl"), ("4", "that", "that", "SCONJ", "6", "mark"),
        ("5", "he", "he", "PRON", "6", "nsubj"), ("6", "sleeps", "sleep", "VERB", "3", "ccomp"),
        ("7", ",", ",", "PUNCT", "3", "punct"), ("8", "I", "I", "PRON", "9", "nsubj"),
        ("9", "leave", "leave", "VERB", "0", "root"), ("10", ".", ".", "PUNCT", "9", "punct"),
    ]), _speech())
    assert _claims(out) == [] and not [r for r in out.zip.rows if r.kind in ("attitude", "join")]


SAID_QUIETLY = [("1", "I", "I", "PRON", "2", "nsubj"), ("2", "said", "say", "VERB", "0", "root"),
                ("3", "quietly", "quietly", "ADV", "2", "advmod"),
                ("4", "that", "that", "SCONJ", "7", "mark"), ("5", "he", "he", "PRON", "7", "nsubj"),
                ("6", "did", "do", "AUX", "7", "aux"), ("7", "sleep", "sleep", "VERB", "2", "ccomp"),
                ("8", ".", ".", "PUNCT", "2", "punct")]


def test_a_matrix_with_a_BOX_of_its_own_withholds_what_its_attitude_holds(compiler):
    """Ruling 2: an attitude row has no boxes, so «I said quietly that he slept» cannot put the
    saying's manner anywhere — what was said is withheld and the saying stands, claimed (a cut from
    a claimed clause weakens it). Under its own «not» the saying goes too."""
    kept = compiler.compile(_tree("I said quietly that he did sleep .", SAID_QUIETLY), _speech())
    negated = compiler.compile(_tree("I did not say quietly that he slept .", [
        ("1", "I", "I", "PRON", "4", "nsubj"), ("2", "did", "do", "AUX", "4", "aux"),
        ("3", "not", "not", "PART", "4", "advmod"), ("4", "say", "say", "VERB", "0", "root"),
        ("5", "quietly", "quietly", "ADV", "4", "advmod"), ("6", "that", "that", "SCONJ", "8", "mark"),
        ("7", "he", "he", "PRON", "8", "nsubj"), ("8", "slept", "sleep", "VERB", "4", "ccomp"),
        ("9", ".", ".", "PUNCT", "4", "punct"),
    ]), _speech())

    (said,) = _claims(kept)
    assert said.predicate == "say.v" and Role.MANNER in said.boxes
    assert not [r for r in kept.zip.rows if r.kind == "attitude"] and "sleep" in kept.unplaced
    assert any("manner box of its own" in why for why in kept.abstained)
    assert _claims(negated) == []


def test_the_complement_takes_the_matrix_s_place_in_a_join(compiler):
    """«I leave because Anna thinks that he does not sleep» — the because-join named Anna's clause;
    seated, it names the sleeping, with ATT(anna) · ¬ over it."""
    out = compiler.compile(_tree("I leave because Anna thinks that he does not sleep .", [
        ("1", "I", "I", "PRON", "2", "nsubj"), ("2", "leave", "leave", "VERB", "0", "root"),
        ("3", "because", "because", "SCONJ", "5", "mark"), ("4", "Anna", "Anna", "PROPN", "5", "nsubj"),
        ("5", "thinks", "think", "VERB", "2", "advcl"), ("6", "that", "that", "SCONJ", "10", "mark"),
        ("7", "he", "he", "PRON", "10", "nsubj"), ("8", "does", "do", "AUX", "10", "aux"),
        ("9", "not", "not", "PART", "10", "advmod"), ("10", "sleep", "sleep", "VERB", "5", "ccomp"),
        ("11", ".", ".", "PUNCT", "2", "punct"),
    ]), _speech())
    sleeping, leaving = _content(out, "sleep.v"), _content(out, "leave.v")
    (join,) = [r for r in out.zip.rows if r.kind == "join"]

    assert join.operator is Operator.IMPLY and join.operands == [sleeping.name, leaving.name]
    assert join.truth == 1.0
    assert _stack(out, sleeping.name) == [("attitude", "think.v"), ("negation", None)]
    assert _none_of(out, "think.v")


def test_a_relative_clause_holding_an_attitude_is_withheld(compiler):
    """«Every man who thinks that he sleeps is happy» claimed ∀x happy(x) with the restriction gone
    and a thinking held by a free x.

    *Amended 2026-09-27 (`E3.3.14`)*: a restriction is a join operand now, and an attitude CAN take
    its place inside one («The man who thinks that she sleeps is happy» compiles whole). Here it
    cannot: under ∀ the restriction is STATED, and an attitude row has no truth slot to state it in
    — and cut, the universal's restriction widens the claim."""
    out = compiler.compile(_tree("Every man who thinks that he sleeps is happy .", [
        ("1", "Every", "every", "DET", "2", "det"), ("2", "man", "man", "NOUN", "9", "nsubj"),
        ("3", "who", "who", "PRON", "4", "nsubj"), ("4", "thinks", "think", "VERB", "2", "acl:relcl"),
        ("5", "that", "that", "SCONJ", "7", "mark"), ("6", "he", "he", "PRON", "7", "nsubj"),
        ("7", "sleeps", "sleep", "VERB", "4", "ccomp"), ("8", "is", "be", "AUX", "9", "cop"),
        ("9", "happy", "happy", "ADJ", "0", "root"), ("10", ".", ".", "PUNCT", "9", "punct"),
    ]))
    assert _claims(out) == [] and not [r for r in out.zip.rows if r.kind == "attitude"]
    assert any("SUPPOSED" in why for why in out.abstained)
    assert any("restriction of a universal" in why for why in out.abstained)


def test_a_PASSIVE_subject_is_not_the_attitude_s_holder(compiler):
    """`E3.3.11.2.10` — «He was not told that she sleeps» said HE did not tell: the holder was read
    off the patient box. A passive subject holds nothing; the matrix keeps its place, what it holds
    is withheld, and under its «not» the telling goes too."""
    out = compiler.compile(_tree("He was not told that she sleeps .", [
        ("1", "He", "he", "PRON", "4", "nsubj:pass"), ("2", "was", "be", "AUX", "4", "aux:pass"),
        ("3", "not", "not", "PART", "4", "advmod"), ("4", "told", "tell", "VERB", "0", "root"),
        ("5", "that", "that", "SCONJ", "7", "mark"), ("6", "she", "she", "PRON", "7", "nsubj"),
        ("7", "sleeps", "sleep", "VERB", "4", "ccomp"), ("8", ".", ".", "PUNCT", "4", "punct"),
    ]))
    assert _claims(out) == [] and not [r for r in out.zip.rows if r.kind == "attitude"]
    assert any("passive" in why for why in out.abstained)


def test_a_SECOND_PARTICIPANT_keeps_the_matrix_and_is_never_lost(compiler):
    """`E3.3.11.2.11` — «He did not persuade Anna that she sleeps»: Anna is a box no attitude row
    has, and dissolving the persuading lost her in silence."""
    out = compiler.compile(_tree("He did not persuade Anna that she sleeps .", [
        ("1", "He", "he", "PRON", "4", "nsubj"), ("2", "did", "do", "AUX", "4", "aux"),
        ("3", "not", "not", "PART", "4", "advmod"), ("4", "persuade", "persuade", "VERB", "0", "root"),
        ("5", "Anna", "Anna", "PROPN", "4", "obj"), ("6", "that", "that", "SCONJ", "8", "mark"),
        ("7", "she", "she", "PRON", "8", "nsubj"), ("8", "sleeps", "sleep", "VERB", "4", "ccomp"),
        ("9", ".", ".", "PUNCT", "4", "punct"),
    ]))
    assert _claims(out) == [] and "Anna" in out.unplaced


def test_a_cut_LINK_takes_the_boxes_its_own_dependents_filled(compiler):
    """«I tried to tell him that she sleeps» came back «I tried him»: «tell» opens no row, so «him»
    had landed on the trying. With the link cut, its phrases go with it."""
    out = compiler.compile(_tree("I tried to tell him that she sleeps .", [
        ("1", "I", "I", "PRON", "2", "nsubj"), ("2", "tried", "try", "VERB", "0", "root"),
        ("3", "to", "to", "PART", "4", "mark"), ("4", "tell", "tell", "VERB", "2", "xcomp"),
        ("5", "him", "he", "PRON", "4", "iobj"), ("6", "that", "that", "SCONJ", "8", "mark"),
        ("7", "she", "she", "PRON", "8", "nsubj"), ("8", "sleeps", "sleep", "VERB", "4", "ccomp"),
        ("9", ".", ".", "PUNCT", "2", "punct"),
    ]), _speech())
    (tried,) = _claims(out)
    assert tried.predicate == "try.v" and set(tried.boxes) == {Role.AGENT}
    assert {"tell", "him"} <= set(out.unplaced)


def test_the_ELIDED_conjunct_and_the_post_verbal_NOT_are_withheld(compiler):
    """Ruling 9 (`E3.3.11.2.15`): «…and she DOES not» is an auxiliary heading its clause — the verb it
    carries is elided — and «I hope NOT» negates the elided complement, never the hoping. Neither
    is decided; both are withheld, and the proforms wait for their rows."""
    elided = compiler.compile(_tree("I think that he sleeps and she does not .", [
        ("1", "I", "I", "PRON", "2", "nsubj"), ("2", "think", "think", "VERB", "0", "root"),
        ("3", "that", "that", "SCONJ", "5", "mark"), ("4", "he", "he", "PRON", "5", "nsubj"),
        ("5", "sleeps", "sleep", "VERB", "2", "ccomp"), ("6", "and", "and", "CCONJ", "8", "cc"),
        ("7", "she", "she", "PRON", "8", "nsubj"), ("8", "does", "do", "AUX", "5", "conj"),
        ("9", "not", "not", "PART", "8", "advmod"), ("10", ".", ".", "PUNCT", "2", "punct"),
    ]), _speech())
    hope_not = compiler.compile(_tree("I hope not .", [
        ("1", "I", "I", "PRON", "2", "nsubj"), ("2", "hope", "hope", "VERB", "0", "root"),
        ("3", "not", "not", "PART", "2", "advmod"), ("4", ".", ".", "PUNCT", "2", "punct"),
    ]), _speech())

    assert _none_of(elided, "do.v") and not [r for r in elided.zip.rows if r.kind == "attitude"]
    assert any("elided" in why for why in elided.abstained)
    assert _claims(hope_not) == [] and "not" in hope_not.unplaced


def test_a_joining_word_after_its_verb_joins_nothing_and_is_not_placed(compiler):
    """«I think SO» · «I don't think SO» — «so» is the elided complement, a proform its row does not
    describe yet (ruling 9: later). Counted as a join no pass would build, it vanished: «I think»
    claimed in silence, and under the «not» the reverse. Unplaced, the first keeps «I think» and says
    so; the second is withheld."""
    plain = compiler.compile(_tree("I think so .", [
        ("1", "I", "I", "PRON", "2", "nsubj"), ("2", "think", "think", "VERB", "0", "root"),
        ("3", "so", "so", "ADV", "2", "advmod"), ("4", ".", ".", "PUNCT", "2", "punct"),
    ]), _speech())
    negated = compiler.compile(_tree("I do n't think so .", [
        ("1", "I", "I", "PRON", "4", "nsubj"), ("2", "do", "do", "AUX", "4", "aux"),
        ("3", "n't", "not", "PART", "4", "advmod"), ("4", "think", "think", "VERB", "0", "root"),
        ("5", "so", "so", "ADV", "4", "advmod"), ("6", ".", ".", "PUNCT", "4", "punct"),
    ]), _speech())
    assert [r.predicate for r in _claims(plain)] == ["think.v"] and plain.unplaced == ("so",)
    assert _claims(negated) == [] and "so" in negated.unplaced


def test_a_complement_is_OPAQUE_WHOLE_and_a_cut_in_its_conjunct_withholds_it(compiler):
    """«I think that he sleeps and he knew the muffin man» — the conjunct is inside the thinking
    (seated, the attitude stands over their join), so «muffin» cut from it is cut under an
    attitude: the conjunct goes, then the complement it was joined in, then the attitude; the
    thinking stands on its own. Judged as a free clause, the conjunct would have claimed that he
    knew «the man» OUTSIDE anybody's thinking."""
    out = compiler.compile(_tree("I think that he sleeps and he knew the muffin man .", [
        ("1", "I", "I", "PRON", "2", "nsubj"), ("2", "think", "think", "VERB", "0", "root"),
        ("3", "that", "that", "SCONJ", "5", "mark"), ("4", "he", "he", "PRON", "5", "nsubj"),
        ("5", "sleeps", "sleep", "VERB", "2", "ccomp"), ("6", "and", "and", "CCONJ", "8", "cc"),
        ("7", "he", "he", "PRON", "8", "nsubj"), ("8", "knew", "know", "VERB", "5", "conj"),
        ("9", "the", "the", "DET", "11", "det"), ("10", "muffin", "muffin", "NOUN", "11", "compound"),
        ("11", "man", "man", "NOUN", "8", "obj"), ("12", ".", ".", "PUNCT", "2", "punct"),
    ]), _speech())
    assert [r.predicate for r in _claims(out)] == ["think.v"]
    assert not [r for r in out.zip.rows if r.kind in ("attitude", "join")]
    assert {"sleeps", "knew", "muffin"} <= set(out.unplaced)


# ------------------------------------------------------------------------------------------------
# `E3.3.11.1` · `E3.3.11.2` — the verification round (2026-09-26): what the seating newly exposed
# ------------------------------------------------------------------------------------------------

THE_MAN_WHO_THINKS = _tree("The man who thinks that he sleeps is happy .", [
    ("1", "The", "the", "DET", "2", "det"), ("2", "man", "man", "NOUN", "9", "nsubj"),
    ("3", "who", "who", "PRON", "4", "nsubj"), ("4", "thinks", "think", "VERB", "2", "acl:relcl"),
    ("5", "that", "that", "SCONJ", "7", "mark"), ("6", "he", "he", "PRON", "7", "nsubj"),
    ("7", "sleeps", "sleep", "VERB", "4", "ccomp"), ("8", "is", "be", "AUX", "9", "cop"),
    ("9", "happy", "happy", "ADJ", "0", "root"), ("10", ".", ".", "PUNCT", "9", "punct"),
])


def _told(det: str) -> object:
    """«<det> man who was told that she sleeps is happy» — a restriction whose attitude has no
    holder (a passive subject, `E3.3.11.2.10`), so what it holds must be cut."""
    return _tree(f"{det} man who was told that she sleeps is happy .", [
        ("1", det, det.lower(), "DET", "2", "det"), ("2", "man", "man", "NOUN", "10", "nsubj"),
        ("3", "who", "who", "PRON", "5", "nsubj:pass"), ("4", "was", "be", "AUX", "5", "aux:pass"),
        ("5", "told", "tell", "VERB", "2", "acl:relcl"),
        ("6", "that", "that", "SCONJ", "8", "mark"), ("7", "she", "she", "PRON", "8", "nsubj"),
        ("8", "sleeps", "sleep", "VERB", "5", "ccomp"), ("9", "is", "be", "AUX", "10", "cop"),
        ("10", "happy", "happy", "ADJ", "0", "root"), ("11", ".", ".", "PUNCT", "10", "punct"),
    ])


def test_an_attitude_takes_its_place_INSIDE_a_restriction(compiler):
    """`E3.3.14` — a relative clause is the first operand of its binder's join, so the attitude it
    holds is seated there like any other: «the x such that x thinks that he sleeps» is happy. Held
    by the variable alone it had no place, and what was thought was withheld."""
    out = compiler.compile(THE_MAN_WHO_THINKS)
    thinking = next(r for r in out.zip.rows if r.kind == "attitude")
    binder = rows_of(out, "quantifier")[0]
    join = next(r for r in rows_of(out, "join") if r.name == binder.scopes)

    assert out.zip.unplaced == [] and thinking.holder.head == Var(name=binder.binds)
    assert join.operator is Operator.AND and join.operands[0] == thinking.scopes
    assert _none_of(out, "think.v"), "the thinking lives in the attitude row"


def test_a_DEFINITE_description_that_loses_its_restriction_s_content_is_withheld(compiler):
    """«The man who was told that she sleeps is happy» keeps «the man who was told is happy» once
    what he was told has to go (a passive subject holds nothing): a weaker description under a
    definite may pick out another man, so what remains is not entailed (E3.12.5 (1)). Under an
    INDEFINITE it is — «a man who was told is happy» is weaker and true — and is kept, honestly
    partial. *(The attitude of «The man who THINKS…» takes its place since `E3.3.14`.)*"""
    definite = compiler.compile(_told("The"))
    indefinite = compiler.compile(_told("A"))

    assert _claims(definite) == [] and not [r for r in definite.zip.rows if r.kind == "attitude"]
    assert any("DEFINITE" in why for why in definite.abstained)
    assert sorted(r.predicate or "(be)" for r in rows_of(indefinite, "content")) == ["(be)", "tell.v"]
    assert {"that", "she", "sleeps"} == set(indefinite.unplaced)
    # **AND WHATEVER FORCE ITS BINDER CARRIES** (`E3.3.14.1`): «the TIRED man» mints ∃ where «the
    # man who…» mints none, and the description is definite in both.
    tired = compiler.compile(_tree("The tired man who was told that she sleeps is happy .", [
        ("1", "The", "the", "DET", "3", "det"), ("2", "tired", "tired", "ADJ", "3", "amod"),
        ("3", "man", "man", "NOUN", "11", "nsubj"),
        ("4", "who", "who", "PRON", "6", "nsubj:pass"), ("5", "was", "be", "AUX", "6", "aux:pass"),
        ("6", "told", "tell", "VERB", "3", "acl:relcl"),
        ("7", "that", "that", "SCONJ", "9", "mark"), ("8", "she", "she", "PRON", "9", "nsubj"),
        ("9", "sleeps", "sleep", "VERB", "6", "ccomp"), ("10", "is", "be", "AUX", "11", "cop"),
        ("11", "happy", "happy", "ADJ", "0", "root"), ("12", ".", ".", "PUNCT", "11", "punct")]))
    assert _claims(tired) == [] and any("DEFINITE" in why for why in tired.abstained)


def test_an_interrogative_DETERMINER_that_opens_nothing_withholds_its_question(compiler):
    """`E3.3.15` · `E3.3.11.2.6.1` — «Which man sleeps?» came back «Man sleeps.»: «which» opens a
    participant by its RELATION, and as a determiner it has none, so it went unplaced and the clause
    stood claimed. An interrogative binds (tkzip req 36) and cut it turns a question into a claim —
    an OPERATOR (`E3.12.5.2`). *How «which X» is held is `E3.3.15.1`, for the Captain.*"""
    out = compiler.compile(_tree("Which man sleeps ?", [
        ("1", "Which", "which", "DET", "2", "det"), ("2", "man", "man", "NOUN", "3", "nsubj"),
        ("3", "sleeps", "sleep", "VERB", "0", "root"), ("4", "?", "?", "PUNCT", "3", "punct")]),
        _speech())

    assert _claims(out) == [] and _none_of(out, "sleep.v")
    assert {"Which", "man", "sleeps"} == set(out.unplaced)


def test_a_question_that_lost_a_word_asks_ANOTHER_question_and_is_withheld(compiler):
    """`E3.3.16` — «Who thinks that he sleeps?» came back «Who thinks?»: the complement withheld
    (ruling 8, a pronoun under a questioned holder) and the narrower question left standing. An
    answer to it answers nothing the speaker asked: a question is neither upward nor downward."""
    out = compiler.compile(_tree("Who thinks that he sleeps ?", [
        ("1", "Who", "who", "PRON", "2", "nsubj"), ("2", "thinks", "think", "VERB", "0", "root"),
        ("3", "that", "that", "SCONJ", "5", "mark"), ("4", "he", "he", "PRON", "5", "nsubj"),
        ("5", "sleeps", "sleep", "VERB", "2", "ccomp"), ("6", "?", "?", "PUNCT", "2", "punct")]),
        _speech())

    assert _claims(out) == [] and _none_of(out, "think.v", "sleep.v")
    assert any("in a question" in why for why in out.abstained)


def test_a_clause_ADJECTIVE_whose_subject_is_the_clause_is_withheld_with_it(compiler):
    """`E3.3.11.2.8.1` — «It is true that he sleeps» came back «True is.»: the clause withheld (no
    holder), and the copula left saying «true» of nothing. The expletive stands for the clause, and
    the adjective is said OF it — withheld with it, as ruling 10 of `E3.3.11.2.16` holds «It is (not)
    true that…» until the clause adjectives are rows. A VERB keeps its row: «[it] surprised me»."""
    out = compiler.compile(_tree("It is true that he sleeps .", [
        ("1", "It", "it", "PRON", "3", "expl"), ("2", "is", "be", "AUX", "3", "cop"),
        ("3", "true", "true", "ADJ", "0", "root"), ("4", "that", "that", "SCONJ", "6", "mark"),
        ("5", "he", "he", "PRON", "6", "nsubj"), ("6", "sleeps", "sleep", "VERB", "3", "csubj"),
        ("7", ".", ".", "PUNCT", "3", "punct")]), _speech())

    assert _claims(out) == [] and set(out.unplaced) == {"It", "is", "true", "that", "he", "sleeps"}
    assert any("said of that clause" in why for why in out.abstained)


def test_a_TAG_on_an_attitude_is_withheld_whole_until_the_format_holds_an_asked_attitude(compiler):
    """«He says that he sleeps, doesn't he?» — the tag's verb is elided (ruling 9), and it was the
    sentence's only question: the host stood as a plain claim, a question stored as a statement.

    *Amended 2026-09-27 (`E3.3.11.2.21`)* — this was `test_a_TAG_takes_the_clause_it_asks_about_
    with_it`, when req 50's prior was not built and the host went with its tag. Now the host is
    asked with the prior, exactly as «Does he say that he sleeps?» asks it — and an ASKED attitude
    has no truth slot in an attitude row (`E3.3.11.2.16` (2)), so what it holds is withheld. One
    rule for a `?` and a tag — *and since `E3.3.16` the saying goes too: asked alone, «Does he
    say?» is another question* (it was `…_asks_the_attitude_and_its_complement_waits_…`)."""
    out = compiler.compile(_tree("He says that he sleeps , does n't he ?", [
        ("1", "He", "he", "PRON", "2", "nsubj"), ("2", "says", "say", "VERB", "0", "root"),
        ("3", "that", "that", "SCONJ", "5", "mark"), ("4", "he", "he", "PRON", "5", "nsubj"),
        ("5", "sleeps", "sleep", "VERB", "2", "ccomp"), ("6", ",", ",", "PUNCT", "7", "punct"),
        ("7", "does", "do", "AUX", "2", "parataxis"), ("8", "n't", "not", "PART", "7", "advmod"),
        ("9", "he", "he", "PRON", "7", "nsubj"), ("10", "?", "?", "PUNCT", "2", "punct"),
    ]), _speech())
    assert _claims(out) == [] and not [r for r in out.zip.rows if r.kind == "attitude"]
    assert _none_of(out, "say.v", "sleep.v")
    assert any("ASKED" in why for why in out.abstained)
    assert any("in a question" in why for why in out.abstained)
    assert {"He", "says", "that", "he", "sleeps"} == set(out.unplaced)


def test_a_TAG_whose_auxiliary_the_parser_calls_a_VERB_is_read_as_a_tag(compiler):
    """«She said that he left, didn't she?» with «did» tagged VERB, as stanza tags it — round 2 of
    the verification. Then only the second cue of an elision saw the tag, and the host stood
    CLAIMED, a question stored as a statement.

    *Amended 2026-09-27 (`E3.3.11.2.21`)* — this was `…_takes_its_host_with_it`. A tag is found by
    its SHAPE (`_is_tag`), and a form the table reads as a function word heads one whatever label
    the parser gave it; so the host is asked with the prior, and the tag's words are placed.

    *Its host has no complement since 2026-09-27*: «She said that he left, didn't she?» asks a
    saying, which is withheld whole now (`E3.3.16`), and this test is about the tag."""
    out = compiler.compile(_tree("She left , did n't she ?", [
        ("1", "She", "she", "PRON", "2", "nsubj"), ("2", "left", "leave", "VERB", "0", "root"),
        ("3", ",", ",", "PUNCT", "4", "punct"),
        ("4", "did", "do", "VERB", "2", "parataxis"), ("5", "n't", "not", "PART", "4", "advmod"),
        ("6", "she", "she", "PRON", "4", "nsubj"), ("7", "?", "?", "PUNCT", "2", "punct"),
    ]), _speech())

    assert _claims(out) == []
    assert isinstance(_content(out, "leave.v").truth, Open)
    assert _content(out, "leave.v").truth.prior is not None
    assert {i for i, where in out.placement.items() if where == "tag"} == {3, 4, 5}


@pytest.mark.skeleton
def test_a_TAG_question_claims_nothing_whichever_tag_the_parser_gives_its_auxiliary():
    """The tree is the point, so the real parser reads them: stanza tags the «did» of the first three
    VERB and of the last AUX (measured 2026-09-27), and all four were one question each — none may
    come out a claim. Round 2 found the first three stored as plain claims."""
    from tk2.language import StanzaSkeletons
    from tk2.language.utterance import compile_utterance
    from tools.drill_gate import DRILL_CONTEXT

    provider, station = StanzaSkeletons(), Compiler(standing_closed_classes())
    for sentence in ("She said that he left, didn't she?",
                     "Anna knew that the cat slept, didn't she?",
                     "She slept, didn't she?",
                     "He slept, didn't he?"):
        zip_ = compile_utterance(station, provider(sentence), DRILL_CONTEXT).zip
        assert not [r for r in zip_.rows if getattr(r, "truth", None) == 1.0], sentence


# ------------------------------------------------------------------------------------------------
# `E3.3.11.2.21` — a tag question is req 50's: the host OPEN with a prior (the Captain, 2026-09-27)
# ------------------------------------------------------------------------------------------------


def _slept(tag_auxiliary, *tag, host_subject=("She", "she"), upos="AUX"):
    """«She slept, <tag> ?» — the tag's words after its auxiliary, each (text, lemma, upos, dep)."""
    text, lemma = host_subject
    rows = [("1", text, lemma, "PRON", "2", "nsubj"), ("2", "slept", "sleep", "VERB", "0", "root"),
            ("3", ",", ",", "PUNCT", "4", "punct"),
            ("4", tag_auxiliary, "do", upos, "2", "parataxis")]
    for at, (word, word_lemma, word_upos, dep) in enumerate(tag, start=5):
        rows.append((str(at), word, word_lemma, word_upos, "4", dep))
    rows.append((str(len(rows) + 1), "?", "?", "PUNCT", "2", "punct"))
    return _tree(" ".join(r[1] for r in rows), rows)


def test_a_TAG_on_a_lexical_verb_asks_its_host_whichever_label_its_auxiliary_has(compiler):
    """«She slept, didn't she?» — the do-support tag, with «did» as stanza tags it (VERB) and as UD
    would (AUX): one shape, one reading. The host is asked with the reversed tag's prior, and every
    word of the tag is placed — «she» says nothing its host's «She» did not."""
    for upos in ("VERB", "AUX"):
        out = compiler.compile(_slept("did", ("n't", "not", "PART", "advmod"),
                                      ("she", "she", "PRON", "nsubj"), upos=upos))
        (host,) = [r for r in out.zip.rows]
        assert host.predicate == "sleep.v" and host.truth.prior == compiler.priors.of("reversed_tag")
        assert out.unplaced == () and out.abstained == (), upos


def test_a_NEGATIVE_host_with_a_POSITIVE_tag_is_the_same_shape(compiler):
    """«She did not sleep, did she?» — the polarity REVERSED the other way round: the ¬ stays over
    the host, and the host is asked with the same prior. Polarity is read off the rows each clause
    raised, never off a word."""
    out = compiler.compile(_tree("She did not sleep , did she ?", [
        ("1", "She", "she", "PRON", "4", "nsubj"), ("2", "did", "do", "AUX", "4", "aux"),
        ("3", "not", "not", "PART", "4", "advmod"), ("4", "sleep", "sleep", "VERB", "0", "root"),
        ("5", ",", ",", "PUNCT", "6", "punct"), ("6", "did", "do", "AUX", "4", "parataxis"),
        ("7", "she", "she", "PRON", "6", "nsubj"), ("8", "?", "?", "PUNCT", "4", "punct"),
    ]))
    sleeping = _content(out, "sleep.v")

    assert _stack(out, sleeping.name) == [("negation", None)]
    assert sleeping.truth.prior == compiler.priors.of("reversed_tag")


def test_a_tag_of_its_host_s_OWN_polarity_has_no_row_and_is_withheld(compiler):
    """«She slept, did she?» — the constant tag infers, doubts or mocks, and nothing witnesses how
    much it expects (`db/0042`: a class enters on a witness). Opened without a prior it would be
    «Did she sleep?», which the sentence did not ask; claimed, a question stored as a statement."""
    out = compiler.compile(_slept("did", ("she", "she", "PRON", "nsubj")))

    assert [r for r in out.zip.rows if getattr(r, "predicate", None)] == []
    assert any("constant_tag" in why for why in out.abstained)
    assert {"She", "slept", "did", "she"} == set(out.unplaced)


def test_the_PRIOR_comes_from_THE_ROWS(compiler):
    """Req 50's number is knowledge (`db/0042`): re-curated, it moves by migration; with no row for
    the shape, the tag is withheld with its host rather than opened without it."""
    from tk2.language.prior import OpenPriors

    tag = _slept("did", ("n't", "not", "PART", "advmod"), ("she", "she", "PRON", "nsubj"))
    curated = Compiler(compiler.table, priors=OpenPriors({"reversed_tag": {"prior": 0.6}}, "test"))
    empty = Compiler(compiler.table, priors=OpenPriors({}, "a table with no rows"))

    assert _content(curated.compile(tag), "sleep.v").truth.prior == 0.6
    assert [r for r in empty.compile(tag).zip.rows if getattr(r, "predicate", None)] == []


def test_a_TAG_on_a_CONDITIONAL_asks_the_conditional(compiler):
    """«If it rains, she stays, doesn't she?» — the conditional is the one claim there, so it is
    what is asked, exactly as «Will you stay if it rains?» asks its IMPLY. `_relate` supposes the
    tag with the consequent it extends; the `?` closes it all the same. It claimed the conditional."""
    out = compiler.compile(_tree("If it rains , she stays , does n't she ?", [
        ("1", "If", "if", "SCONJ", "3", "mark"), ("2", "it", "it", "PRON", "3", "nsubj"),
        ("3", "rains", "rain", "VERB", "6", "advcl"), ("4", ",", ",", "PUNCT", "6", "punct"),
        ("5", "she", "she", "PRON", "6", "nsubj"), ("6", "stays", "stay", "VERB", "0", "root"),
        ("7", ",", ",", "PUNCT", "8", "punct"), ("8", "does", "do", "AUX", "6", "parataxis"),
        ("9", "n't", "not", "PART", "8", "advmod"), ("10", "she", "she", "PRON", "8", "nsubj"),
        ("11", "?", "?", "PUNCT", "6", "punct"),
    ]))
    (imply,) = _joins(out).values()

    assert imply.operator is Operator.IMPLY and imply.truth.prior is not None
    assert _content(out, "rain.v").truth is None and _content(out, "stay.v").truth is None
    assert out.unplaced == ()


def test_a_TAG_on_a_COORDINATION_is_withheld_with_it(compiler):
    """«He slept and she left, didn't she?» — UD hangs what a whole coordination shares on its first
    conjunct, so a tag there asks «he slept» or both, and the tree cannot say which. It claimed
    «she left» and dropped the rest."""
    out = compiler.compile(_tree("He slept and she left , did n't she ?", [
        ("1", "He", "he", "PRON", "2", "nsubj"), ("2", "slept", "sleep", "VERB", "0", "root"),
        ("3", "and", "and", "CCONJ", "5", "cc"), ("4", "she", "she", "PRON", "5", "nsubj"),
        ("5", "left", "leave", "VERB", "2", "conj"), ("6", ",", ",", "PUNCT", "7", "punct"),
        ("7", "did", "do", "VERB", "2", "parataxis"), ("8", "n't", "not", "PART", "7", "advmod"),
        ("9", "she", "she", "PRON", "7", "nsubj"), ("10", "?", "?", "PUNCT", "2", "punct"),
    ]))

    assert [r for r in out.zip.rows if getattr(r, "predicate", None)] == []
    assert any("coordination" in why for why in out.abstained)


def test_a_TAG_whose_pronoun_or_carrier_is_not_its_host_s_asks_another_clause(compiler):
    """«He said that she was late, wasn't SHE?» asks the lateness and hangs off the saying; «He
    said that he was late, WASN'T he?» likewise — «said» takes «did». The tree hangs the tag on a
    clause it does not ask, so the host goes with it rather than a question for the wrong clause."""
    def said(pronoun, gender_lemma):
        return _tree(f"He said that {pronoun} was late , was n't {pronoun} ?", [
            ("1", "He", "he", "PRON", "2", "nsubj"), ("2", "said", "say", "VERB", "0", "root"),
            ("3", "that", "that", "SCONJ", "6", "mark"),
            ("4", pronoun, gender_lemma, "PRON", "6", "nsubj"),
            ("5", "was", "be", "AUX", "6", "cop"), ("6", "late", "late", "ADJ", "2", "ccomp"),
            ("7", ",", ",", "PUNCT", "8", "punct"), ("8", "was", "be", "AUX", "2", "parataxis"),
            ("9", "n't", "not", "PART", "8", "advmod"),
            ("10", pronoun, gender_lemma, "PRON", "8", "nsubj"), ("11", "?", "?", "PUNCT", "2", "punct"),
        ])
    she, he = compiler.compile(said("she", "she")), compiler.compile(said("he", "he"))

    assert _claims(she) == [] and any("does not agree" in why for why in she.abstained)
    assert _claims(he) == [] and any("no carrier" in why for why in he.abstained)
    assert not [r for r in [*she.zip.rows, *he.zip.rows] if isinstance(getattr(r, "truth", None),
                                                                      Open)]


def test_a_TAG_on_an_IMPERATIVE_keeps_the_want_and_places_nothing_of_itself(compiler):
    """«Close the door, will you?» — the host is wanted, not claimed; the tag presses or softens the
    want (req 51's gradation of its strength) and no row says by how much. The want stands at the
    bare imperative's strength, the tag is unplaced and said why — and not read as a cut from what
    is wanted, which withheld the whole sentence."""
    out = compiler.compile(_with_mood(_tree("Close the door , will you ?", [
        ("1", "Close", "close", "VERB", "0", "root"), ("2", "the", "the", "DET", "3", "det"),
        ("3", "door", "door", "NOUN", "1", "obj"), ("4", ",", ",", "PUNCT", "5", "punct"),
        ("5", "will", "will", "AUX", "1", "parataxis"), ("6", "you", "you", "PRON", "5", "nsubj"),
        ("7", "?", "?", "PUNCT", "1", "punct"),
    ]), 0), _speech())
    (want,) = [r for r in out.zip.rows if r.kind == "attitude"]

    assert want.verb == "want.v" and want.strength == compiler.strengths.of("imperative")
    assert _content(out, "close.v").truth is None
    assert set(out.unplaced) == {"will", "you"}
    assert any("imperative" in why and "strength" in why for why in out.abstained)


def test_an_elided_question_that_is_NO_tag_still_takes_its_host(compiler):
    """«Anna sleeps, but does Bob?» — a coordinator and a name: an elided question of its own, not a
    tag (`_is_tag`). Ruling 9 withholds it, and what it asks is elided, so its host goes with it as
    before — never asked with a tag's prior."""
    out = compiler.compile(_tree("Anna sleeps , but does Bob ?", [
        ("1", "Anna", "anna", "PROPN", "2", "nsubj"), ("2", "sleeps", "sleep", "VERB", "0", "root"),
        ("3", ",", ",", "PUNCT", "5", "punct"), ("4", "but", "but", "CCONJ", "5", "cc"),
        ("5", "does", "do", "AUX", "2", "conj"), ("6", "Bob", "bob", "PROPN", "5", "nsubj"),
        ("7", "?", "?", "PUNCT", "2", "punct"),
    ]))

    assert [r for r in out.zip.rows if getattr(r, "predicate", None)] == []
    assert not [r for r in out.zip.rows if getattr(getattr(r, "truth", None), "prior", None)]


def test_the_0042_check_REFUSES_what_the_ruling_does_not_say(monkeypatch):
    """`db/0042`'s check travels with its rows: one row per shape, a shape the reader asks for, no
    row for the unwitnessed constant tag, and a prior that is HIGH (req 50)."""
    from tk2.migrations import discover

    found = next(m for m in discover() if m.number == 42)
    module = found.load()
    row = module.OPEN_PRIOR_ROWS[0]
    assert [r["shape"] for r in module.OPEN_PRIOR_ROWS] == ["reversed_tag"]
    for broken in ([row, row],
                   [dict(row, shape="tag")],
                   [row, dict(row, shape="constant_tag")],
                   [dict(row, compiled={"prior": 0.5})],
                   [dict(row, compiled={"prior": 1.5})]):
        monkeypatch.setattr(module, "OPEN_PRIOR_ROWS", broken)
        with pytest.raises(ValueError):
            module._check()                                                 # noqa: SLF001


@pytest.mark.skeleton
def test_every_TAG_the_parser_gives_is_one_rule():
    """The tree is the point, so the real parser reads them (measured 2026-09-27): «did» tagged VERB
    and AUX, the copula tag, the modal tags — «won't» split by stanza into a «wo» no row reads — a
    tag on a conditional, and the cases the tree cannot settle. None may come out a claim; each is
    asked with a prior or withheld whole."""
    from tk2.language import StanzaSkeletons
    from tk2.language.utterance import compile_utterance
    from tools.drill_gate import DRILL_CONTEXT

    provider, station = StanzaSkeletons(), Compiler(standing_closed_classes())

    def read(sentence):
        return compile_utterance(station, provider(sentence), DRILL_CONTEXT)

    asked = {"She slept, didn't she?": "r0", "He left, did he not?": "r0",
             "He is tired, isn't he?": "r0", "It's cold, isn't it?": "r0",
             "He will come, won't he?": "r0", "You can swim, can't you?": "r0",
             "If it rains, she stays, doesn't she?": "j0"}
    for sentence, name in asked.items():
        out = read(sentence)
        rows = {r.name: r for r in out.zip.rows}
        assert rows[name].truth.prior is not None, sentence
        assert not [r for r in out.zip.rows if getattr(r, "truth", None) == 1.0], sentence
        assert out.unplaced == (), sentence
    for sentence in ("He slept and she left, didn't she?", "He said that she was late, wasn't she?",
                     "She slept, did she?"):
        out = read(sentence)
        assert not [r for r in out.zip.rows if getattr(r, "truth", None) is not None
                    and getattr(r, "kind", "") in ("content", "join")], sentence


WHO_THINKS_SHE_SLEEPS = _tree("Who thinks that she sleeps ?", [
    ("1", "Who", "who", "PRON", "2", "nsubj"), ("2", "thinks", "think", "VERB", "0", "root"),
    ("3", "that", "that", "SCONJ", "5", "mark"), ("4", "she", "she", "PRON", "5", "nsubj"),
    ("5", "sleeps", "sleep", "VERB", "2", "ccomp"), ("6", "?", "?", "PUNCT", "2", "punct"),
])
WHO_THINKS_THE_CAT_SLEEPS = _tree("Who thinks that the cat sleeps ?", [
    ("1", "Who", "who", "PRON", "2", "nsubj"), ("2", "thinks", "think", "VERB", "0", "root"),
    ("3", "that", "that", "SCONJ", "6", "mark"), ("4", "the", "the", "DET", "5", "det"),
    ("5", "cat", "cat", "NOUN", "6", "nsubj"), ("6", "sleeps", "sleep", "VERB", "2", "ccomp"),
    ("7", "?", "?", "PUNCT", "2", "punct"),
])


def test_a_QUESTIONED_holder_holds_its_attitude(compiler):
    """«Who thinks that the cat sleeps?» — the wh-word's box is the one it OPENED, which the
    placement trace does not label as a box, so no holder was found and the record said «a passive
    or an expletive subject» of a sentence with neither. The holder is the asked box, and the
    thinking takes its clause's place."""
    out = compiler.compile(WHO_THINKS_THE_CAT_SLEEPS)
    (att,) = [r for r in out.zip.rows if r.kind == "attitude"]

    assert att.verb == "think.v" and isinstance(att.holder.head, Open) and att.holder.head.sort
    assert att.scopes == _content(out, "sleep.v").name and _none_of(out, "think.v")
    assert out.unplaced == ()


def test_a_pronoun_under_a_QUESTIONED_holder_is_withheld_like_a_quantified_one(compiler):
    """«Who thinks that SHE sleeps?» asks for the x who thinks x sleeps as readily as for whoever
    thinks that she does — questions and quantifiers are one binding mechanism (tkzip req 36), so
    ruling 8's ambiguity is withheld here too. And the record names that, not a passive."""
    out = compiler.compile(WHO_THINKS_SHE_SLEEPS)

    assert not [r for r in out.zip.rows if r.kind == "attitude"]
    assert any("questioned holder" in why for why in out.abstained)
    assert not any("passive" in why or "expletive" in why for why in out.abstained)


def test_WHETHER_or_NOT_asks_whether(compiler):
    """«I don't know whether he sleeps or not» — «or not» is the other alternative an open truth
    already holds (p-or-not-p is what «whether p» asks). Read as the clause's own «not» it claimed
    «I do not know that he does not sleep»; read as an elided verb, it withheld the sentence."""
    out = compiler.compile(_tree("I do n't know whether he sleeps or not", [
        ("1", "I", "I", "PRON", "4", "nsubj"), ("2", "do", "do", "AUX", "4", "aux"),
        ("3", "n't", "not", "PART", "4", "advmod"), ("4", "know", "know", "VERB", "0", "root"),
        ("5", "whether", "whether", "SCONJ", "7", "mark"), ("6", "he", "he", "PRON", "7", "nsubj"),
        ("7", "sleeps", "sleep", "VERB", "4", "ccomp"), ("8", "or", "or", "CCONJ", "9", "cc"),
        ("9", "not", "not", "PART", "7", "conj"),
    ]), _speech())
    sleeping = _content(out, "sleep.v")

    assert _stack(out, sleeping.name) == [("negation", None), ("attitude", "know.v")]
    assert isinstance(sleeping.truth, Open) and out.unplaced == ()


def test_a_claimed_OR_NOT_is_still_withheld(compiler):
    """Only under a truth the clause's own word opens: «He sleeps or not» claims nothing it would be
    honest to keep — «he sleeps» is not entailed by a tautology."""
    out = compiler.compile(_tree("He sleeps or not .", [
        ("1", "He", "he", "PRON", "2", "nsubj"), ("2", "sleeps", "sleep", "VERB", "0", "root"),
        ("3", "or", "or", "CCONJ", "4", "cc"), ("4", "not", "not", "PART", "2", "conj"),
        ("5", ".", ".", "PUNCT", "2", "punct"),
    ]))
    assert _claims(out) == []


def _copular(text, subject, subject_lemma, adjective, negated=False):
    words = [("1", subject, subject_lemma, "PRON", "3" if not negated else "4", "nsubj"),
             ("2", "is" if subject == "It" else "am", "be", "AUX", "3" if not negated else "4",
              "cop")]
    at = 3
    if negated:
        words.append(("3", "not", "not", "PART", "4", "advmod"))
        at = 4
    words += [(str(at), adjective, adjective, "ADJ", "0", "root"),
              (str(at + 1), "that", "that", "SCONJ", str(at + 3), "mark"),
              (str(at + 2), "he", "he", "PRON", str(at + 3), "nsubj"),
              (str(at + 3), "sleeps", "sleep", "VERB", str(at), "ccomp")]
    return _tree(text, words)


def test_IT_IS_TRUE_THAT_is_withheld_explicitly_not_by_a_side_effect(compiler):
    """Ruling 10 (`E3.3.11.2.8`): «It is (not) true that…» made the adjective an attitude verb held
    by the expletive. It is withheld meanwhile — and by its own rule, the copula's complement being
    the attitude's word, so that no change to how a holder is read can reopen it."""
    true = compiler.compile(_copular("It is true that he sleeps", "It", "it", "true"), _speech())
    not_true = compiler.compile(_copular("It is not true that he sleeps", "It", "it", "true",
                                         negated=True), _speech())

    for out in (true, not_true):
        assert not [r for r in out.zip.rows if r.kind == "attitude"]
        assert _none_of(out, "sleep.v")
        assert any("E3.3.11.2.16 (10)" in why for why in out.abstained)
    assert _claims(not_true) == [], "cut from under its «not», the rest is withheld too"


def test_I_AM_SURE_THAT_keeps_I_am_sure_and_says_why_the_rest_waits(compiler):
    """«I am sure that he sleeps» has the same tree as «It is true that…», and which adjective its
    subject HOLDS is a fact about the word — knowledge no row holds yet (ruling 10's rows). So the
    complement waits, and the record names that, not «a complement box of its own»: the complement
    box IS the attitude's word."""
    out = compiler.compile(_copular("I am sure that he sleeps", "I", "I", "sure"), _speech())
    (sure,) = _claims(out)

    assert sure.predicate is None and sure.boxes[Role.COMPLEMENT].head == "sure.a"
    assert any("copula's complement" in why for why in out.abstained)
    assert not any("box of its own" in why for why in out.abstained)


@pytest.mark.parametrize("skeleton, cause", [
    (_tree("That he lied surprised me .", [
        ("1", "That", "that", "SCONJ", "3", "mark"), ("2", "he", "he", "PRON", "3", "nsubj"),
        ("3", "lied", "lie", "VERB", "4", "csubj"), ("4", "surprised", "surprise", "VERB", "0", "root"),
        ("5", "me", "I", "PRON", "4", "obj"), ("6", ".", ".", "PUNCT", "4", "punct"),
    ]), "CLAUSE"),
    (_tree("It seems that he sleeps .", [
        ("1", "It", "it", "PRON", "2", "expl"), ("2", "seems", "seem", "VERB", "0", "root"),
        ("3", "that", "that", "SCONJ", "5", "mark"), ("4", "he", "he", "PRON", "5", "nsubj"),
        ("5", "sleeps", "sleep", "VERB", "2", "ccomp"), ("6", ".", ".", "PUNCT", "2", "punct"),
    ]), "expletive"),
])
def test_a_matrix_with_NO_HOLDER_keeps_its_place_and_the_record_names_its_subject(compiler,
                                                                                  skeleton, cause):
    """A clausal subject («That he lied surprised me») and an expletive («It seems that…») hold
    nothing the tree can name. The first was recorded as «a passive or an expletive subject»; the
    second handed its place to an attitude held by a bare `?`. Both keep their place now, and the
    record says which subject the sentence has."""
    out = compiler.compile(skeleton, _speech())

    assert not [r for r in out.zip.rows if r.kind == "attitude"]
    assert any(cause in why for why in out.abstained)
    assert not any("passive" in why for why in out.abstained)


# ------------------------------------------------------------------------------------------------
# `E3.3.11.2.9` — the adverbial quantifiers: «never», «always», «nowhere» bind a circumstance
# ------------------------------------------------------------------------------------------------


def _adverbial(text, rows):
    """A hand-written parse, in the shape stanza gives these sentences (probed 2026-09-27)."""
    return skeleton_from_conllu(text, rows)


HE_NEVER_SLEEPS = _adverbial("He never sleeps .", [
    ("1", "He", "he", "PRON", "3", "nsubj"), ("2", "never", "never", "ADV", "3", "advmod"),
    ("3", "sleeps", "sleep", "VERB", "0", "root"), ("4", ".", ".", "PUNCT", "3", "punct"),
])


def test_an_ADVERBIAL_quantifier_binds_the_box_its_row_names(compiler):
    """«He never sleeps» compiled to «He sleeps» — the REVERSE, with `unplaced` empty: «never» was
    matched, counted as placed, and compiled to nothing (`E3.3.11.2.9`). It is ¬∃t — the binder
    «nobody» raises, its variable in the TIME box, which the row names (`db/0043`) because no
    relation does: `advmod` is not a nominal one."""
    out = compiler.compile(HE_NEVER_SLEEPS)
    (binder,) = rows_of(out, "quantifier")
    row = main_row(out)

    assert binder.quantity is Quantity.NEGATIVE
    assert binder.restriction.head == Open(sort="time"), "what the word said, and nothing else"
    assert row.boxes[Role.TIME].head == Var(name=binder.binds)
    assert binder.scopes == row.name and row.truth == 1.0
    assert out.coverage == 1.0 and out.abstained == ()


def test_a_quantified_PLACE_fills_the_location_box():
    """«He sleeps nowhere» — the same repair, the other circumstance the rows name."""
    out = Compiler(standing_closed_classes()).compile(_adverbial("He sleeps nowhere .", [
        ("1", "He", "he", "PRON", "2", "nsubj"), ("2", "sleeps", "sleep", "VERB", "0", "root"),
        ("3", "nowhere", "nowhere", "ADV", "2", "advmod"), ("4", ".", ".", "PUNCT", "2", "punct"),
    ]))
    (binder,) = rows_of(out, "quantifier")

    assert binder.quantity is Quantity.NEGATIVE
    assert main_row(out).boxes[Role.LOCATION].head == Var(name=binder.binds)


@pytest.mark.parametrize("text, rows, order", [
    ("He does not always sleep .", [
        ("1", "He", "he", "PRON", "4", "nsubj"), ("2", "does", "do", "AUX", "4", "aux"),
        ("3", "not", "not", "PART", "4", "advmod"), ("4", "always", "always", "ADV", "5", "advmod"),
        ("5", "sleep", "sleep", "VERB", "0", "root"), ("6", ".", ".", "PUNCT", "5", "punct"),
    ], ["negation", "universal"]),
    ("He never does not sleep .", [
        ("1", "He", "he", "PRON", "5", "nsubj"), ("2", "never", "never", "ADV", "5", "advmod"),
        ("3", "does", "do", "AUX", "5", "aux"), ("4", "not", "not", "PART", "5", "advmod"),
        ("5", "sleep", "sleep", "VERB", "0", "root"), ("6", ".", ".", "PUNCT", "5", "punct"),
    ], ["negative", "negation"]),
])
def test_the_binder_and_the_negation_scope_in_the_order_the_words_stand(compiler, text, rows,
                                                                          order):
    """The literal reading (`E3.12.5` (6)): «does not ALWAYS sleep» is ¬∀t, «NEVER does not sleep»
    ¬∃t¬ — the prefix is the order the speaker used, which is req 35's whole point."""
    out = compiler.compile(_adverbial(text, rows))
    said = [r.quantity.value if r.kind == "quantifier" else r.kind
            for r in out.zip.rows if r.kind in ("quantifier", "negation")]

    assert said == order
    assert out.coverage == 1.0


def test_a_FUSED_quantifier_is_never_a_determiner_of_what_it_hangs_off(compiler):
    """«He was never late» hangs «never» off «late», and `_box_for` read it as that phrase's
    determiner: the binder bound the ADJECTIVE — «he was no late». A fused quantifier is its own
    phrase (`db/0028`), so the complement stays «late» and the time is quantified."""
    out = compiler.compile(_adverbial("He was never late .", [
        ("1", "He", "he", "PRON", "4", "nsubj"), ("2", "was", "be", "AUX", "4", "cop"),
        ("3", "never", "never", "ADV", "4", "advmod"), ("4", "late", "late", "ADJ", "0", "root"),
        ("5", ".", ".", "PUNCT", "4", "punct"),
    ]))
    (binder,) = rows_of(out, "quantifier")
    row = main_row(out)

    assert row.boxes[Role.COMPLEMENT].head == "late.a"
    assert binder.restriction.head == Open(sort="time")
    assert row.boxes[Role.TIME].head == Var(name=binder.binds)


@pytest.mark.parametrize("word, says", [
    ("seldom", "seldom: says few"), ("often", "often: says many"),
    ("once", "once: ambiguous"),
    ("rarely", "rarely: a quantifier over the time"), ("usually", "usually: a quantifier over the time"),
])
def test_a_word_that_says_MORE_than_a_quantity_holds_is_withheld_never_bound(compiler, word, says):
    """«seldom» is few and «often» many — proportions, withheld (the Captain's `E3.3.11.2.9.2`);
    «seldom»'s row no longer says `negative`, which bound would have read «he never sleeps». «once»
    has two readings, one time or formerly (`E3.3.11.2.9.4`). «rarely» and «usually» are adverb-kinds
    rows now (`db/0043`): with none they fell to the manner default and CLAIMED «he sleeps». Each is
    unplaced with why, and the unplaced operator withholds its clause (`E3.12.5.2`)."""
    out = compiler.compile(_adverbial(f"He {word} sleeps .", [
        ("1", "He", "he", "PRON", "3", "nsubj"), ("2", word, word, "ADV", "3", "advmod"),
        ("3", "sleeps", "sleep", "VERB", "0", "root"), ("4", ".", ".", "PUNCT", "3", "punct"),
    ]))

    assert _claims(out) == [] and not rows_of(out, "quantifier")
    assert word in out.zip.unplaced
    assert any(says in why for why in out.abstained), out.abstained


@pytest.mark.parametrize("text, rows, prefix", [
    ("Do you ever sleep ?", [
        ("1", "Do", "do", "AUX", "4", "aux"), ("2", "you", "you", "PRON", "4", "nsubj"),
        ("3", "ever", "ever", "ADV", "4", "advmod"), ("4", "sleep", "sleep", "VERB", "0", "root"),
        ("5", "?", "?", "PUNCT", "4", "punct"),
    ], ["existential"]),
    ("Nobody ever sleeps .", [
        ("1", "Nobody", "nobody", "PRON", "3", "nsubj"), ("2", "ever", "ever", "ADV", "3", "advmod"),
        ("3", "sleeps", "sleep", "VERB", "0", "root"), ("4", ".", ".", "PUNCT", "3", "punct"),
    ], ["negative", "existential"]),
    ("He does not ever sleep .", [
        ("1", "He", "he", "PRON", "5", "nsubj"), ("2", "does", "do", "AUX", "5", "aux"),
        ("3", "not", "not", "PART", "5", "advmod"), ("4", "ever", "ever", "ADV", "5", "advmod"),
        ("5", "sleep", "sleep", "VERB", "0", "root"), ("6", ".", ".", "PUNCT", "5", "punct"),
    ], ["negation", "existential"]),
])
def test_EVER_is_an_existential_over_times(compiler, text, rows, prefix):
    """«ever» is ∃t (the Captain's `E3.3.11.2.9.3`) — its row said `universal` and its own force
    `existential`, and the force was right. Under a question, a negative binder or a «not»."""
    out = compiler.compile(_adverbial(text, rows))
    said = [r.quantity.value if r.kind == "quantifier" else r.kind
            for r in out.zip.rows if r.kind in ("quantifier", "negation")]

    assert said == prefix
    assert out.coverage == 1.0


def test_TWICE_is_a_count_on_the_binder(compiler):
    """«He slept twice» — ∃t with a count of two, on the binder's own `count`, as the drill's
    `freq-1` holds it (the Captain's `E3.3.11.2.9.4`)."""
    out = compiler.compile(_adverbial("He slept twice .", [
        ("1", "He", "he", "PRON", "2", "nsubj"), ("2", "slept", "sleep", "VERB", "0", "root"),
        ("3", "twice", "twice", "ADV", "2", "advmod"), ("4", ".", ".", "PUNCT", "2", "punct"),
    ]))
    (binder,) = rows_of(out, "quantifier")

    assert binder.quantity is Quantity.EXISTENTIAL and binder.count == 2
    assert main_row(out).boxes[Role.TIME].head == Var(name=binder.binds)


def _modal_never(modal, adverb="never"):
    return _adverbial(f"He {modal} {adverb} sleep .", [
        ("1", "He", "he", "PRON", "4", "nsubj"), ("2", modal, modal, "AUX", "4", "aux"),
        ("3", adverb, adverb, "ADV", "4", "advmod"), ("4", "sleep", "sleep", "VERB", "0", "root"),
        ("5", ".", ".", "PUNCT", "4", "punct"),
    ])


@pytest.mark.parametrize("modal, prefix", [
    ("can", ["negative", "modality"]),      # ¬∃t ◇ — «can»'s «not» scopes outside
    ("must", ["modality", "negative"]),     # □ ¬∃t — «must»'s stays inside
    ("need", ["negative", "modality"]),     # ¬∃t □
])
def test_a_NEGATIVE_binder_after_a_modal_follows_the_modal_s_row(compiler, modal, prefix):
    """The Captain's `E3.3.11.2.9.5`: «never» after a modal auxiliary stands in the slot «not» does,
    and the modal's `following_negation` (`db/0036`) places its negation exactly as it places a
    «not». Read by word order «can never» claimed ◇¬ — «he might never sleep»."""
    out = compiler.compile(_modal_never(modal))
    said = [r.quantity.value if r.kind == "quantifier" else r.kind
            for r in out.zip.rows if r.kind in ("quantifier", "modality")]

    assert said == prefix
    assert out.coverage == 1.0 and _claims(out)


@pytest.mark.parametrize("modal, adverb, why", [
    ("may", "never", "both inside the modality and outside it"),
    ("can", "always", "carries no negation for the modal's row to place"),
])
def test_an_adverbial_binder_after_a_modal_is_withheld_where_no_row_places_it(compiler, modal,
                                                                             adverb, why):
    """«may never» is `may`'s ambiguity again, and a positive binder carries no negation for the row
    to place (`E3.3.11.2.9.5`): both withheld, as «may not» is."""
    out = compiler.compile(_modal_never(modal, adverb))

    assert _claims(out) == []
    assert any("after a modal auxiliary" in r and why in r for r in out.abstained), out.abstained


def test_a_quantifier_nobody_binds_is_UNPLACED_and_not_counted(compiler):
    """The root of `E3.3.11.2.9`: a quantifier word was returned as placed on meeting it, trusting a
    binder someone else would build. «When does he never sleep?» has one time box and two words for
    it — «when» asks it, so «never» binds nothing, and it must say so rather than vanish."""
    out = compiler.compile(_adverbial("When does he never sleep ?", [
        ("1", "When", "when", "ADV", "5", "advmod"), ("2", "does", "do", "AUX", "5", "aux"),
        ("3", "he", "he", "PRON", "5", "nsubj"), ("4", "never", "never", "ADV", "5", "advmod"),
        ("5", "sleep", "sleep", "VERB", "0", "root"), ("6", "?", "?", "PUNCT", "5", "punct"),
    ]))

    assert "never" in out.zip.unplaced
    assert any("never: the time box it binds is already filled" in why for why in out.abstained)
    assert _claims(out) == []


def test_a_quantity_something_MODIFIES_is_not_bound_as_that_quantity(compiler):
    """«He ALMOST never sleeps» hangs «almost» off «never»; bound, the zip claimed he never sleeps.
    The format holds the quantity and not how near the speaker came to it — so the word is left
    unplaced and the clause withheld. A «not» on the quantifier is the prefix's own («NOT
    everyone»), and still binds."""
    almost = compiler.compile(_adverbial("He almost never sleeps .", [
        ("1", "He", "he", "PRON", "4", "nsubj"), ("2", "almost", "almost", "ADV", "3", "advmod"),
        ("3", "never", "never", "ADV", "4", "advmod"), ("4", "sleeps", "sleep", "VERB", "0", "root"),
        ("5", ".", ".", "PUNCT", "4", "punct"),
    ]))
    not_everyone = compiler.compile(_adverbial("Not everyone sleeps .", [
        ("1", "Not", "not", "PART", "2", "advmod"), ("2", "everyone", "everyone", "PRON", "3", "nsubj"),
        ("3", "sleeps", "sleep", "VERB", "0", "root"), ("4", ".", ".", "PUNCT", "3", "punct"),
    ]))

    assert _claims(almost) == [] and "never" in almost.zip.unplaced
    assert any("modified by «almost»" in why for why in almost.abstained)
    assert [r.kind for r in not_everyone.zip.rows][:2] == ["negation", "quantifier"]
    assert not_everyone.coverage == 1.0


def test_a_cut_circumstance_under_an_adverbial_UNIVERSAL_withholds_the_clause(compiler):
    """«He always sleeps EXCEPT ON SUNDAYS» — «except» is not compiled, and what it cuts narrows the
    times «always» ranges over: kept, the zip said he always sleeps. An adverbial binder's
    restriction is its clause's circumstances, so the cut is read as one in a universal's
    restriction, and the clause is withheld."""
    out = compiler.compile(_adverbial("He always sleeps except on Sundays .", [
        ("1", "He", "he", "PRON", "3", "nsubj"), ("2", "always", "always", "ADV", "3", "advmod"),
        ("3", "sleeps", "sleep", "VERB", "0", "root"), ("4", "except", "except", "ADP", "6", "case"),
        ("5", "on", "on", "ADP", "6", "case"), ("6", "Sundays", "Sunday", "PROPN", "3", "obl"),
        ("7", ".", ".", "PUNCT", "3", "punct"),
    ]))

    assert _claims(out) == []
    assert any("restriction of a universal" in why for why in out.abstained)
