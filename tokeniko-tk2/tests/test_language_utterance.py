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


def _without(skeleton, text):
    """The same parse with one word taken out and every head renumbered around it."""
    gone = next(w.index for w in skeleton if w.text == text)
    at = {w.index: n for n, w in enumerate(w for w in skeleton if w.index != gone)}
    rows = [(str(at[w.index] + 1), w.text, w.lemma, w.upos,
             "0" if w.is_root else str(at[w.head] + 1), w.dep)
            for w in skeleton if w.index != gone]
    return skeleton_from_conllu(" ".join(r[1] for r in rows), rows)


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


def test_REPORTED_speech_does_not_rotate(compiler):
    """**«John said to Marie that you swim» is about the person I am talking to, not about Marie.**

    In reported speech the REPORTER has already moved the pronouns into his own frame — that is what
    reporting is — so rotating a second time lands the sentence on the wrong person while looking
    entirely confident. The first draft (2026-09-16) did exactly that, because it keyed the rotation
    on the joiner's `asserts: matrix`, a flag that lives on the word «that»: present in precisely
    the case where rotating is wrong, absent from the bare quoted `ccomp` where it is right.
    Found by the drill's quotation block the next morning (`q-2` `q-4` `q-7` `q-9`); read
    `docs/E3-parser-compiler/202609170533_the-quotation-block.md`.

    **The attitude is still raised and still records its addressee** — schema v3 is untouched. What
    changed is only what the rotation is triggered by.
    """
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
    assert swimming.boxes[Role.AGENT].head == "captain", "the listener, not the person spoken to"

    attitude = next(r for r in out.zip.rows if r.kind == "attitude")
    assert attitude.addressee.head == "marie.n", "schema v3: the attitude records who it addressed"


@pytest.mark.skeleton
def test_QUOTED_speech_rotates_and_stanza_is_what_says_which(compiler):
    """The same sentence quoted, and now it IS about Marie.

    **The signal is structural, and the station never reads a character.** A quoted complement
    carries punctuation bracketing its span; a reported one does not — so «which characters are
    quotation marks» is a question that never has to be asked. The Captain refused it as a premise:
    *«I find it weak to care about what a quotation symbol is; spacy-stanza already has the tooling
    to isolate the quote»*. Curly quotes work here for free, which is the proof.
    """
    from tk2.language.skeleton import StanzaSkeletons

    provider = StanzaSkeletons()
    for sentence in ('Bob told me "I am tired".',
                     'Bob told me \u201cI am tired\u201d.'):
        out = compiler.compile(provider(sentence)[0],
                               context=Context(speaker="kotekino", addressee="captain"))
        tired = next(r for r in out.zip.rows if r.kind == "content"
                     and r.boxes.get(Role.COMPLEMENT) and r.boxes[Role.COMPLEMENT].head == "tired.a")
        assert tired.boxes[Role.EXPERIENCER].head == "bob.n", f"«I» is Bob in {sentence!r}"

    # **`q-2`'s own «I trust you» is WITHHELD since 2026-09-26** (E3.12.5 (1)). Stanza labels the
    # only object of «trust» `iobj`, which UD reserves for a clause that also has a direct object,
    # so the station abstains on it (req 22) — and a word cut from under the saying changes what Bob
    # SAID: «Bob told me "I trust"». So the rotation is pinned on a quote with nothing cut from it.
    out = compiler.compile(provider('Bob told me "I trust you".')[0],
                           context=Context(speaker="kotekino", addressee="captain"))
    assert any("iobj" in reason for reason in out.abstained)
    assert not [r for r in out.zip.rows if r.kind == "attitude"] and "you" in out.unplaced

def test_a_CONDITIONAL_does_not_rotate(compiler):
    """Only an ATTITUDE rotates. «if you know who did it» is still the outer speaker's «you» — the
    test is the joiner saying `asserts: matrix`, not merely being a subordinate clause."""
    out = compiler.compile(case("if you know who did it , tell me").skeleton,
                           context=Context(speaker="kotekino", addressee="captain"))
    knowing = next(r for r in out.zip.rows if getattr(r, "predicate", None) == "know.v")

    assert knowing.boxes[Role.EXPERIENCER].head == "captain"  # `know` is cognition (req 22)


# ------------------------------------------------------------------------------------------------
# the quote becomes the CONTENT of the saying
# ------------------------------------------------------------------------------------------------


def test_A_QUOTE_IS_NOT_CLAIMED_OF_THE_WORLD_and_the_ATTITUDE_is_what_says_so(compiler):
    """**«John said the sky is green» does not assert that the sky is green — the PREFIX says so.**

    The rows keep their truth *(changed 2026-09-17 on the Captain's ruling)*. An attitude scoping a
    row is what keeps it out of the world, exactly as in `dere-1`, where the drill has always
    carried a cat at truth 1.0 under «he thinks» and asserted no cat.

    **Blanking the slot cost a distinction**: under a saying verb the truth records what the HOLDER
    did with the content — asserted it, asked it, wanted it — and three speech acts were collapsing
    into one shape. «John told me X», «John asked me X» and «John told me to do X» are three
    different things to the brain.
    """
    out = compile_utterance(compiler, [SAID, QUOTED],
                            Context(speaker="kotekino", addressee="captain"))

    saying = next(r for r in out.zip.rows if getattr(r, "predicate", None) == "say.v")
    assert saying.truth == 1.0, "the SAYING is claimed"

    quoted = [r for r in out.zip.rows if r.name.startswith("s1.") and r.kind in ("content", "join")]
    assert quoted and all(r.truth == 1.0 for r in quoted), "and John asserted its content"

    attitude = next(r for r in out.zip.rows if r.kind == "attitude")
    assert attitude.scopes in {r.name for r in quoted}, "the prefix is what holds it out of the world"


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
    question = skeleton_from_conllu("Do you know ?", [
        ("1", "Do", "do", "AUX", "3", "aux"),
        ("2", "you", "you", "PRON", "3", "nsubj"),
        ("3", "know", "know", "VERB", "0", "root"),
        ("4", "?", "?", "PUNCT", "3", "punct"),
    ])
    out = compile_utterance(compiler, [asked, question],
                            Context(speaker="kotekino", addressee="captain"))

    attitude = next(r for r in out.zip.rows if r.kind == "attitude")
    assert attitude.verb == "ask.v" and attitude.addressee is None
    knowing = next(r for r in out.zip.rows if getattr(r, "predicate", None) == "know.v")
    assert isinstance(knowing.truth, Open), (
        "the asking is what the attitude holds; the row's own slot says what the holder DID with "
        "it — and the holder ASKED. Pinned at 1.0 on 2026-09-17 as a named gap; OPEN since task 2c "
        "(req 21), across the sentence boundary stanza draws at the quote.")
    assert knowing.boxes[Role.EXPERIENCER].head == "captain", "and «you» is still the outer listener"


@pytest.mark.skeleton
def test_the_TENSE_reaches_the_ZIP_and_it_reaches_it_PER_CLAUSE(compiler):
    """**The station was compiling `tense_aspect` words to NOTHING** — marked covered, dropped — so
    «I walked to the station» and «I walk to the station» were one zip (tkzip req 25). It is read
    from UD's FINITE word, because a participle's `Tense=Past` is its own form and not when the
    thing happened, and it is written PER ROW (schema v5, the Captain 2026-09-20): «I went to Rome
    and I WILL GO to Genoa» is two clauses and two times, and one slot on the zip could hold one.

    *It parses for real rather than reading a hand-written skeleton, because the thing under test is
    a FEATURE the provider supplies and the conllu fixtures carry no features at all.*
    """
    from tk2.language.skeleton import StanzaSkeletons

    provider = StanzaSkeletons()
    out = compile_utterance(compiler, provider("I went to Rome and I will go to Genoa."))
    times = sorted(r.theatre.interval[0] for r in out.zip.rows
                   if r.kind == "content" and r.theatre)

    assert times == [-1.0, 1.0], f"one past and one future, and got {times}"

    now = compile_utterance(compiler, provider("The cat sleeps."))
    present = [r.theatre.interval[0] for r in now.zip.rows if r.kind == "content" and r.theatre]
    assert present == [0.0], "the present is written down too, and not left to be assumed"


def test_a_BARE_ccomp_under_a_saying_verb_is_reported_content(compiler):
    """«that» is OPTIONAL, and without it nothing raised the POV — so «I asked: "Do you know the
    muffin man?"» CLAIMED that you know him. **The UD gate found it**, on the very example this QM
    passed over when transcribing `ccomp` the first time.

    Both forms must produce the same shape: `ccomp` is `ccomp` whether or not there are quotation
    marks. **What differs is what the holder DID** (the truth-slot ruling, 2026-09-17): he SAID the
    first and ASKED the second, so the first is stated and the second is OPEN (req 21).

    *Without the muffin since 2026-09-26*: «muffin» is a `compound` the station does not build, and
    cut from under the saying it changes what was said (E3.12.5 (1)) — both UD sentences now keep
    the saying and WITHHOLD what was said (`E3.12.5.1`), and the shape is pinned on them with that
    one word taken out.
    """
    for text in ("He said that he knew the muffin man .", 'I asked : " Do you know the muffin man ? "'):
        withheld = compiled(compiler, text)
        assert not [r for r in withheld.zip.rows if r.kind == "attitude"]
        assert any("«muffin»" in why for why in withheld.abstained)

    marked = compiler.compile(_without(case("He said that he knew the muffin man .").skeleton,
                                       "muffin"))
    bare = compiler.compile(_without(case('I asked : " Do you know the muffin man ? "').skeleton,
                                     "muffin"))

    for out in (marked, bare):
        attitude = next(r for r in out.zip.rows if r.kind == "attitude")
        inner = next(r for r in out.zip.rows if getattr(r, "predicate", None) == "know.v")
        assert attitude.scopes == inner.name
        if out is marked:
            assert inner.truth == 1.0, "the holder asserted it; the attitude keeps it out of the world"
        else:
            assert isinstance(inner.truth, Open), "the holder ASKED it — the `?` closes the quote"
        # **THE SAYING IS THE ATTITUDE ROW AND NOTHING ELSE** *(2026-09-20)*. It used to be both —
        # a prefix row AND a content row for the same verb — and the decompiler said it twice.
        assert not [r for r in out.zip.rows
                    if getattr(r, "predicate", None) in ("say.v", "ask.v")], (
            "the saying dissolved into the attitude that replaced it")
