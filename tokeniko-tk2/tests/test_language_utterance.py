"""THE UTTERANCE — context as an argument (req 7) and a quote that arrives as two sentences.

E3 task 2b.1 and 2b.2. **The other two sub-tasks are deliberately absent**, and the last test here
is what keeps that honest: it asserts the rotation is WRONG, so the day it is right the test fails
and somebody has to come and read this file.
"""

import pytest

from tests.fixtures.ud import CASES
from tk2.language import standing_closed_classes
from tk2.language.compile import Compiler
from tk2.language.skeleton import skeleton_from_conllu
from tk2.language.utterance import (
    NO_CONTEXT, Context, CompiledUtterance, compile_utterance, prefixed,
)
from tk2.tkzip.schema import Box, ContentRow, JoinRow, Open, Operator, Quantity, QuantifierRow, \
    Ref, Role, Var, Zip


@pytest.fixture(scope="module")
def compiler():
    return Compiler(standing_closed_classes())


def case(text):
    return next(c for c in CASES if c.text == text)


def compiled(compiler, text):
    return compiler.compile(case(text).skeleton)


# ------------------------------------------------------------------------------------------------
# 2b.1 — context as an ARGUMENT
# ------------------------------------------------------------------------------------------------


def test_a_first_person_pronoun_resolves_to_the_SPEAKER(compiler):
    """Req 7, built at last. `i` carries `person: 1` in its closed-class row — the axis has had its
    data since v1 and no caller to supply the other end."""
    out = compiler.compile(case("I sleep").skeleton, context=Context(speaker="me.n"))

    assert out.zip.rows[-1].boxes[Role.AGENT].head == "me.n"


def test_WITHOUT_a_context_nothing_changes(compiler):
    """What keeps this purely additive: every pronoun stays OPEN exactly as before, and not one
    existing measurement moves."""
    out = compiler.compile(case("I sleep").skeleton)

    assert isinstance(out.zip.rows[-1].boxes[Role.AGENT].head, Open)
    assert out.coverage == 1.0


def test_THIRD_person_is_not_the_speakers_business():
    """«he» and «they» are ANAPHORA — they point at something earlier in the discourse, not at a
    participant in the speech act — so a context that knows the speaker must still say nothing."""
    context = Context(speaker="me.n", addressee="anna.n")

    assert context.for_person(1) == "me.n"
    assert context.for_person(2) == "anna.n"
    assert context.for_person(3) is None
    assert context.for_person(None) is None


def test_the_station_stays_PURE(compiler):
    """Context is an argument and NEVER state: the same skeleton compiled twice with two different
    contexts gives two different zips, and neither call can influence the other."""
    skeleton = case("I sleep").skeleton
    mine = compiler.compile(skeleton, context=Context(speaker="me.n"))
    yours = compiler.compile(skeleton, context=Context(speaker="you.n"))
    none = compiler.compile(skeleton)

    assert mine.zip.rows[-1].boxes[Role.AGENT].head == "me.n"
    assert yours.zip.rows[-1].boxes[Role.AGENT].head == "you.n"
    assert isinstance(none.zip.rows[-1].boxes[Role.AGENT].head, Open), "no leakage between calls"


def test_the_station_never_invents_an_identifier(compiler):
    """The drill hand-compiles «I» as `me.n`; the blueprint says the self-model is carried by named
    individuals with uids (E3b). Both are legal, and the station chooses neither — it copies what it
    was handed."""
    out = compiler.compile(case("I sleep").skeleton,
                           context=Context(speaker="kotekino@discord:42"))

    assert out.zip.rows[-1].boxes[Role.AGENT].head == "kotekino@discord:42"


# ------------------------------------------------------------------------------------------------
# 2b.2 — a quote arrives as a SECOND SENTENCE
# ------------------------------------------------------------------------------------------------


SAID = skeleton_from_conllu("John said to Marie", [
    ("1", "John", "john", "PROPN", "2", "nsubj"),
    ("2", "said", "say", "VERB", "0", "root"),
    ("3", "to", "to", "ADP", "4", "case"),
    ("4", "Marie", "marie", "PROPN", "2", "obl"),
])
QUOTED = skeleton_from_conllu("You are a clever girl", [
    ("1", "You", "you", "PRON", "5", "nsubj"),
    ("2", "are", "be", "AUX", "5", "cop"),
    ("3", "a", "a", "DET", "5", "det"),
    ("4", "clever", "clever", "ADJ", "5", "amod"),
    ("5", "girl", "girl", "NOUN", "0", "root"),
])

ONE = skeleton_from_conllu("the cat sleeps", [
    ("1", "the", "the", "DET", "2", "det"),
    ("2", "cat", "cat", "NOUN", "3", "nsubj"),
    ("3", "sleeps", "sleep", "VERB", "0", "root"),
])
TWO = skeleton_from_conllu("the dog barks", [
    ("1", "the", "the", "DET", "2", "det"),
    ("2", "dog", "dog", "NOUN", "3", "nsubj"),
    ("3", "barks", "bark", "VERB", "0", "root"),
])


def test_two_sentences_become_ONE_zip(compiler):
    out = compile_utterance(compiler, [ONE, TWO])

    assert out.sentences == 2 and out.split
    assert {r.predicate for r in out.zip.rows if r.kind == "content"} == {"sleep.v", "bark.v"}


def test_the_FIRST_sentence_keeps_its_names(compiler):
    """So a single-sentence utterance is identical to what `Compiler.compile` produces alone — which
    is what let this be added without moving a single existing measurement."""
    alone = compiler.compile(ONE)
    together = compile_utterance(compiler, [ONE])

    assert [r.name for r in alone.zip.rows] == [r.name for r in together.zip.rows]
    assert together.split is False


def test_the_LATER_sentence_is_renamed_and_its_REFERENCES_MOVE_WITH_IT():
    """**The part that could go quietly wrong.** Row names and variable names are two namespaces and
    both must move, or the second sentence's `x0` binds the first sentence's variable."""
    zip_ = Zip(rows=[
        QuantifierRow(name="q0", scopes="j0", binds="x0", quantity=Quantity.UNIVERSAL,
                      restriction=Box(head="cat.n")),
        ContentRow(name="r0", predicate="sleep.v", truth=1.0,
                   boxes={Role.AGENT: Box(head=Var(name="x0"))}),
        ContentRow(name="r1", truth=1.0, boxes={Role.PATIENT: Box(head=Ref(row="r0"))}),
        JoinRow(name="j0", operator=Operator.AND, operands=["r0", "r1"], truth=1.0),
    ])
    moved = prefixed(zip_, "s1.")

    assert [r.name for r in moved.rows] == ["s1.q0", "s1.r0", "s1.r1", "s1.j0"]
    assert moved.rows[0].scopes == "s1.j0" and moved.rows[0].binds == "s1.x0"
    assert moved.rows[1].boxes[Role.AGENT].head == Var(name="s1.x0")
    assert moved.rows[2].boxes[Role.PATIENT].head == Ref(row="s1.r0")
    assert moved.rows[3].operands == ["s1.r0", "s1.r1"]


def test_renaming_never_mangles_a_DICTIONARY_KEY():
    """`cat.n` is not a row name and must survive untouched — which is why the rename checks every
    string against this zip's OWN names rather than prefixing whatever it finds."""
    zip_ = Zip(rows=[ContentRow(name="r0", predicate="sleep.v", truth=1.0,
                                boxes={Role.AGENT: Box(head="cat.n", relation="anna.n")})])
    moved = prefixed(zip_, "s1.")

    assert moved.rows[0].predicate == "sleep.v"
    assert moved.rows[0].boxes[Role.AGENT].head == "cat.n"
    assert moved.rows[0].boxes[Role.AGENT].relation == "anna.n"


def test_an_empty_utterance_is_ONE_EMPTY_ROW_and_not_an_empty_zip(compiler):
    """**The frame refused the first draft of this test, and it was right.** `Zip` requires at least
    one row: a zip is a claim about something, and «nothing» is not something. So no-sentences
    produces the shape the compiler already produces for a skeleton with no root — one empty content
    row — rather than a second convention for the same state."""
    out = compile_utterance(compiler, [])

    assert out.sentences == 0 and out.coverage == 1.0
    assert len(out.zip.rows) == 1 and out.zip.rows[0].boxes == {}


# ------------------------------------------------------------------------------------------------
# 2b.3 + 2b.4 — THE ROTATION (schema v3, the Captain's ruling of 2026-09-16)
# ------------------------------------------------------------------------------------------------


def test_THE_CAPTAINS_OWN_SENTENCE(compiler):
    """**«John said to Marie: YOU are a clever girl» — and the `you` is MARIE.**

    The sentence he asked about, working. It is TWO skeletons — stanza splits a quote — so the
    rotation crosses a sentence boundary: the first sentence is a FRAME (a saying with an agent and
    a recipient) and the second compiles under its participants.

    *This test replaces one that asserted the WRONG answer on purpose, with an instruction to delete
    it the day the rotation landed. It landed.*
    """
    out = compile_utterance(compiler, [SAID, QUOTED],
                            Context(speaker="kotekino", addressee="captain"))

    saying = next(r for r in out.zip.rows if getattr(r, "predicate", None) == "say.v")
    assert saying.boxes[Role.AGENT].head == "john.n"
    assert saying.boxes[Role.RECIPIENT].head == "marie.n"

    quoted = next(r for r in out.zip.rows if r.name.startswith("s1.")
                  and Role.PATIENT in getattr(r, "boxes", {}))
    assert quoted.boxes[Role.PATIENT].head == "marie.n", "the `you` is MARIE, not the outer listener"


def test_a_frame_WITHOUT_a_recipient_does_not_rotate(compiler):
    """«John said.» addresses nobody in particular, so there is nothing for a second person to
    rotate into and the outer addressee rightly survives."""
    said = skeleton_from_conllu("John said", [
        ("1", "John", "john", "PROPN", "2", "nsubj"),
        ("2", "said", "say", "VERB", "0", "root"),
    ])
    out = compile_utterance(compiler, [said, QUOTED],
                            Context(speaker="kotekino", addressee="captain"))

    quoted = next(r for r in out.zip.rows if r.name.startswith("s1.")
                  and Role.PATIENT in getattr(r, "boxes", {}))
    assert quoted.boxes[Role.PATIENT].head == "captain"


def test_an_attitude_that_ADDRESSES_NOBODY_rotates_only_the_first_person():
    """**«John thinks I am wrong» still means the SPEAKER.** Thinking addresses nobody, so there is
    no second-person slot to rotate into — and `addressee` being EMPTY rather than `Open()` is what
    carries that. Schema v3 was ruled for exactly this distinction."""
    from tk2.tkzip.schema import AttitudeRow

    outer = Context(speaker="kotekino", addressee="captain")
    saying = AttitudeRow(name="p0", scopes="r1", holder=Box(head="john.n"), verb="say.v",
                         addressee=Box(head="marie.n"))
    thinking = AttitudeRow(name="p0", scopes="r1", holder=Box(head="john.n"), verb="think.v")

    assert outer.under(saying).for_person(2) == "marie.n"
    assert outer.under(thinking).for_person(2) == "captain", "thinking addresses nobody"
    assert outer.under(thinking).for_person(1) == "john.n", "but the holder IS the first person"


def test_an_OPEN_holder_never_becomes_the_speaker():
    """An unresolved filler is not somebody. «Somebody said you are wrong» must not make the speaker
    of the quote an `Open()`."""
    from tk2.tkzip.schema import AttitudeRow

    outer = Context(speaker="kotekino", addressee="captain")
    vague = AttitudeRow(name="p0", scopes="r1", holder=Box(head=Open()), verb="say.v")

    assert outer.under(vague).for_person(1) == "kotekino"


def test_the_rotation_inside_ONE_sentence(compiler):
    """The same rule down a dependency tree instead of across a sentence boundary — «John said to
    Marie THAT YOU swim». The context is worked out BEFORE the clauses are compiled, because a
    pronoun is resolved where it is met and the attitude that governs it is built later."""
    skeleton = skeleton_from_conllu("John said to Marie that you swim", [
        ("1", "John", "john", "PROPN", "2", "nsubj"),
        ("2", "said", "say", "VERB", "0", "root"),
        ("3", "to", "to", "ADP", "4", "case"),
        ("4", "Marie", "marie", "PROPN", "2", "obl"),
        ("5", "that", "that", "SCONJ", "7", "mark"),
        ("6", "you", "you", "PRON", "7", "nsubj"),
        ("7", "swim", "swim", "VERB", "2", "ccomp"),
    ])
    out = compiler.compile(skeleton, context=Context(speaker="kotekino", addressee="captain"))

    swimming = next(r for r in out.zip.rows if getattr(r, "predicate", None) == "swim.v")
    assert swimming.boxes[Role.AGENT].head == "marie.n"

    attitude = next(r for r in out.zip.rows if r.kind == "attitude")
    assert attitude.addressee.head == "marie.n", "schema v3: the attitude records who it addressed"


def test_a_CONDITIONAL_does_not_rotate(compiler):
    """Only an ATTITUDE rotates. «if you know who did it» is still the outer speaker's «you» — the
    test is the joiner saying `asserts: matrix`, not merely being a subordinate clause."""
    out = compiler.compile(case("if you know who did it , tell me").skeleton,
                           context=Context(speaker="kotekino", addressee="captain"))
    knowing = next(r for r in out.zip.rows if getattr(r, "predicate", None) == "know.v")

    assert knowing.boxes[Role.AGENT].head == "captain"


# ------------------------------------------------------------------------------------------------
# the quote becomes the CONTENT of the saying
# ------------------------------------------------------------------------------------------------


def test_A_QUOTE_IS_NOT_CLAIMED(compiler):
    """**«John said the sky is green» does not assert that the sky is green.** A quote whose rows
    stayed CLAIMED would put every reported sentence into the KB as a fact, which is the one thing
    the truth slot exists to prevent — the same distinction req 38 rests on.

    The shape is the one `ccomp` already produces, arriving across a sentence boundary: an attitude
    scoping the quote, the saying claimed, the quote EMPTY.
    """
    out = compile_utterance(compiler, [SAID, QUOTED],
                            Context(speaker="kotekino", addressee="captain"))

    saying = next(r for r in out.zip.rows if getattr(r, "predicate", None) == "say.v")
    assert saying.truth == 1.0, "the SAYING is claimed"

    quoted = [r for r in out.zip.rows if r.name.startswith("s1.") and r.kind in ("content", "join")]
    assert quoted and all(r.truth is None for r in quoted), "and its content is not"


def test_the_attitude_scopes_the_WHOLE_quote(compiler):
    """«You are a clever girl» is two content rows and an AND. An attitude scoping only the copular
    row would leave «clever» asserted OUTSIDE the quotation — so it scopes the outermost join."""
    out = compile_utterance(compiler, [SAID, QUOTED],
                            Context(speaker="kotekino", addressee="captain"))

    attitude = next(r for r in out.zip.rows if r.kind == "attitude")
    joins = [r.name for r in out.zip.rows if r.kind == "join"]

    assert attitude.scopes == joins[-1], "the outermost join, not one of the rows under it"
    assert attitude.holder.head == "john.n" and attitude.verb == "say.v"


def test_a_frame_with_NO_recipient_still_raises_its_attitude(compiler):
    """**Being a frame and ROTATING are two different things**, and the first draft conflated them.
    «I asked: "Do you know the muffin man?"» is a frame — the question is the content of the asking
    and must not be claimed — and it addresses nobody NAMED, so the `you` stays whoever the outer
    utterance was addressed to. Which is right: «I asked: do YOU know» is asking the listener."""
    asked = skeleton_from_conllu("I asked", [
        ("1", "I", "i", "PRON", "2", "nsubj"),
        ("2", "asked", "ask", "VERB", "0", "root"),
    ])
    question = skeleton_from_conllu("Do you know", [
        ("1", "Do", "do", "AUX", "3", "aux"),
        ("2", "you", "you", "PRON", "3", "nsubj"),
        ("3", "know", "know", "VERB", "0", "root"),
    ])
    out = compile_utterance(compiler, [asked, question],
                            Context(speaker="kotekino", addressee="captain"))

    attitude = next(r for r in out.zip.rows if r.kind == "attitude")
    assert attitude.verb == "ask.v" and attitude.addressee is None
    knowing = next(r for r in out.zip.rows if getattr(r, "predicate", None) == "know.v")
    assert knowing.truth is None, "the question is the content of the asking"
    assert knowing.boxes[Role.AGENT].head == "captain", "and «you» is still the outer listener"


def test_a_BARE_ccomp_under_a_saying_verb_is_reported_content(compiler):
    """«that» is OPTIONAL, and without it nothing raised the POV — so «I asked: "Do you know the
    muffin man?"» CLAIMED that you know him. **The UD gate found it**, on the very example this QM
    passed over when transcribing `ccomp` the first time.

    Both forms must produce the same shape: `ccomp` is `ccomp` whether or not there are quotation
    marks.
    """
    marked = compiled(compiler, "He said that he knew the muffin man .")
    bare = compiled(compiler, 'I asked : " Do you know the muffin man ? "')

    for out in (marked, bare):
        attitude = next(r for r in out.zip.rows if r.kind == "attitude")
        inner = next(r for r in out.zip.rows if getattr(r, "predicate", None) == "know.v")
        assert attitude.scopes == inner.name
        assert inner.truth is None, "the complement is not claimed"
        assert next(r for r in out.zip.rows if r.name == "r0").truth == 1.0, "the saying is"
