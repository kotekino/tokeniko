"""THE DECOMPILER — requirement 9, and the property it exists to have.

**Pure.** These build zips by hand and read the sentence back, so no parser is involved; the
RECOMPILE half of the contract is `tools/roundtrip.py`, which needs stanza and is measured there.

What is pinned here is the discipline rather than the prose: where the rows can say a meaning, it is
said; where they cannot, it is recorded; and where saying it wrong would change what the sentence
CLAIMS, nothing is said at all.
"""

import pytest

from tk2.language.decompile import Decompiler
from tk2.tkzip.schema import (
    Box,
    ContentRow,
    Determination,
    NegationRow,
    Open,
    Quantity,
    Role,
    Var,
    Zip,
)


@pytest.fixture(scope="module")
def decompiler():
    return Decompiler()


def row(name="r0", predicate=None, truth=1.0, **boxes):
    return ContentRow(name=name, predicate=predicate, truth=truth,
                      boxes={Role(k): (v if isinstance(v, Box) else Box(head=v))
                             for k, v in boxes.items()})


def test_a_clause_is_subject_verb_object_and_the_verb_is_INFLECTED(decompiler):
    """«the cat chases the dog» — and `chases`, not `chase`. A lemma verb is an IMPERATIVE to the
    parser, which is how 26 of the round trip's first 32 failures happened: the decompiled claim came
    back as a command."""
    out = decompiler.decompile(Zip(rows=[row(
        predicate="chase.v",
        agent=Box(head="cat.n", determination=Determination.DEFINITE),
        patient=Box(head="dog.n", determination=Determination.DEFINITE))]))

    assert out.text == "The cat chases the dog."
    assert out.whole


def test_a_COPULAR_row_says_be_and_the_copula_is_not_vocabulary(decompiler):
    """A copular row earns no predicate (req 31) because «be» carries no meaning there — it is the
    structure of a predication. So it is frame, and it inflects like anything else."""
    out = decompiler.decompile(Zip(rows=[row(
        patient=Box(head="cat.n", determination=Determination.DEFINITE),
        complement="hungry.a")]))

    assert out.text == "The cat is hungry."


def test_the_MARKER_the_zip_recorded_is_the_marker_it_speaks(decompiler):
    """Thirty-two prepositions mean `location`, so the meaning cannot choose one — but a parsed zip
    never has to ask, because `Box.marker` recorded the one actually used (req 65). «in» and
    «beside» are not the same thought."""
    beside = decompiler.decompile(Zip(rows=[row(
        predicate="sleep.v", agent=Box(head="cat.n", determination=Determination.DEFINITE),
        location=Box(head="fire.n", determination=Determination.DEFINITE, marker="beside"))]))

    assert beside.text == "The cat sleeps beside the fire."


def test_an_indefinite_takes_AN_before_a_vowel_because_that_is_spelling_not_word_choice(decompiler):
    """«a» and «an» are one word in two spellings and the sound that follows settles it — orthography,
    and therefore frame. It is the ONE place this module chooses a form itself, and it is allowed to
    because it is not choosing a word."""
    a = decompiler.decompile(Zip(rows=[row(
        patient=Box(head="cat.n", determination=Determination.INDEFINITE),
        complement=Box(head="mammal.n", determination=Determination.INDEFINITE))]))
    an = decompiler.decompile(Zip(rows=[row(
        patient=Box(head="animal.n", determination=Determination.INDEFINITE),
        complement=Box(head="idiot.n", determination=Determination.INDEFINITE))]))

    assert a.text == "A cat is a mammal."
    assert an.text == "An animal is an idiot.", "the article follows the word it introduces"


def test_a_DENIED_row_says_not_and_the_auxiliary_carries_the_inflection(decompiler):
    """«the cat does not chase the dog» — English's own rule, and frame. The alternative was to
    inflect the main verb under a negation, which no English sentence does."""
    out = decompiler.decompile(Zip(rows=[row(
        predicate="chase.v", truth=0.0,
        agent=Box(head="cat.n", determination=Determination.DEFINITE),
        patient=Box(head="dog.n", determination=Determination.DEFINITE))]))

    assert out.text == "The cat does not chase the dog."


def test_the_quantifier_is_SPOKEN_with_the_form_curation_chose(decompiler):
    """Ten forms mean `universal` — «all», «each», «every», «always»… — so the rows cannot answer by
    themselves and `db/0021`'s flag does. Without it this module would be choosing our own set and
    hard-coding it, which is the standing law's failure wearing a `next(iter(...))`."""
    out = decompiler.decompile(Zip(rows=[row(
        predicate="sleep.v", agent=Box(head="cat.n", quantity=Quantity.UNIVERSAL))]))

    assert out.text == "Every cat sleeps."


def test_what_it_cannot_say_is_RECORDED_and_never_quietly_dropped(decompiler):
    """`unsaid` is `Compiled.unplaced`'s mirror: the thing that knows it failed to say something is
    this module, and throwing that away means re-deriving it later, worse."""
    out = decompiler.decompile(Zip(rows=[row(
        predicate="chase.v", agent=Box(head=Var(name="X")),
        patient=Box(head="dog.n", determination=Determination.DEFINITE))]))

    assert not out.whole
    assert any("variable" in said for said in out.unsaid)
    assert out.text == "Chases the dog.", (
        "what it CAN say, it still says — and the missing subject is in `unsaid`, not invented")


def test_a_row_whose_NEGATION_cannot_be_spoken_is_not_spoken_at_all():
    """**THE ONE RULE THAT IS NOT ABOUT TIDINESS.** Dropping a determiner loses a shade; dropping a
    negation says the OPPOSITE of the zip. So a table with no `spoken` negation makes the clause
    refused rather than rendered — half-said is legal, wrongly-said is the sin (req 8), in this
    direction as in the other."""
    from tk2.language.closed import ClosedClasses

    mute = Decompiler(table=ClosedClasses([
        {"version": 1, "form": "not", "word_class": "adverb", "role": "negation", "position": 0,
         "source": "a table with no voice", "compiled": {"kind": "prefix", "element": "negation"}},
        {"version": 1, "form": "no", "word_class": "determiner", "role": "negation", "position": 1,
         "source": "a table with no voice", "compiled": {"kind": "prefix", "element": "negation"}},
    ], "two negations and no ruling"))

    out = mute.decompile(Zip(rows=[row(predicate="chase.v", truth=0.0, agent="cat.n")]))

    assert out.text == ""
    assert out.refused and "negation" in out.refused[0]


def test_a_prefix_row_is_named_as_unsaid_until_its_slice_is_built(decompiler):
    """The first slice renders content rows. A zip that says MORE than the sentence does must say so,
    or the round trip's number is a lie about how much of the format is reached."""
    out = decompiler.decompile(Zip(rows=[
        row(predicate="chase.v", agent="cat.n"),
        NegationRow(name="n0", scopes="r0"),
    ]))

    assert any("negation row" in said for said in out.unsaid)


def test_an_OPEN_head_is_an_abstention_and_stays_one(decompiler):
    """The parser reads a wh-word INTO an open slot; the decompiler will read it back out when the
    question slice is built. Until then it is recorded, never guessed — «something» would be a claim
    the zip does not make."""
    out = decompiler.decompile(Zip(rows=[row(predicate="chase.v", agent=Box(head=Open()))]))

    assert any("wh-word" in said for said in out.unsaid)
