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
# what is NOT built — asserted, so that building it breaks this and somebody reads the note
# ------------------------------------------------------------------------------------------------


def test_THE_ROTATION_IS_NOT_BUILT_AND_THIS_TEST_SAYS_SO(compiler):
    """**«John said to Marie: YOU are a clever girl» resolves `you` to the OUTER addressee.** That is
    wrong — it should be Marie — and it is E3 task 2b.3 and 2b.4, waiting on the Captain's format
    ruling about where an ADDRESSEE lives (`Pov` has no fourth field and tkzip is frozen at v2).

    **What 2b.2 bought is that the information is now IN THE ZIP**: the saying row carries
    `recipient = marie.n`, and before this the second half of the sentence was simply dropped. The
    rotation has something to read.

    *This test asserts the WRONG answer on purpose. The day it fails, the rotation works — and
    whoever made it fail should come here, read `202609161349_the-person-axis.md`, and delete it.*
    """
    said = skeleton_from_conllu("John said to Marie", [
        ("1", "John", "john", "PROPN", "2", "nsubj"),
        ("2", "said", "say", "VERB", "0", "root"),
        ("3", "to", "to", "ADP", "4", "case"),
        ("4", "Marie", "marie", "PROPN", "2", "obl"),
    ])
    quoted = skeleton_from_conllu("You are a clever girl", [
        ("1", "You", "you", "PRON", "5", "nsubj"),
        ("2", "are", "be", "AUX", "5", "cop"),
        ("3", "a", "a", "DET", "5", "det"),
        ("4", "clever", "clever", "ADJ", "5", "amod"),
        ("5", "girl", "girl", "NOUN", "0", "root"),
    ])
    out = compile_utterance(compiler, [said, quoted],
                            Context(speaker="kotekino", addressee="captain"))

    saying = next(r for r in out.zip.rows if getattr(r, "predicate", None) == "say.v")
    assert saying.boxes[Role.RECIPIENT].head == "marie.n", "the addressee IS in the zip now"

    quoted_row = next(r for r in out.zip.rows
                      if r.name.startswith("s1.") and Role.PATIENT in getattr(r, "boxes", {}))
    assert quoted_row.boxes[Role.PATIENT].head == "captain", (
        "THE ROTATION NOW WORKS — delete this test and read the person-axis note")
