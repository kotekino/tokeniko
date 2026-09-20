"""THE DECOMPILER — requirement 9, and the properties it exists to have.

**Pure.** These build zips by hand and read the sentence back, so no parser is involved; the
RECOMPILE half of the contract is `tools/roundtrip.py`, which needs stanza and is measured there.

What is pinned here is the discipline rather than the prose: where the rows can say a meaning, it is
said; where they cannot, it is recorded; and where saying it wrong would change what the sentence
CLAIMS, nothing is said at all.
"""

import pytest

from tk2.language.decompile import Decompiler
from tk2.language.utterance import Context
from tk2.tkzip.schema import (
    AttitudeRow,
    Box,
    ContentRow,
    Determination,
    DomainRow,
    JoinRow,
    Modality,
    ModalityRow,
    NegationRow,
    Open,
    Operator,
    Quantity,
    QuantifierRow,
    Role,
    Theatre,
    Var,
    Zip,
)


@pytest.fixture(scope="module")
def decompiler():
    return Decompiler()


@pytest.fixture(scope="module")
def spoken():
    """A decompiler that knows who is talking — the same object the compiler is handed (req 20)."""
    return Decompiler(context=Context(speaker="me.n", addressee="you.n"))


def row(name="r0", predicate=None, truth=1.0, **boxes):
    return ContentRow(name=name, predicate=predicate, truth=truth,
                      boxes={Role(k): (v if isinstance(v, Box) else Box(head=v))
                             for k, v in boxes.items()})


# ------------------------------------------------------------------------------------------------
# the clause
# ------------------------------------------------------------------------------------------------


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


def test_an_UNMARKED_object_comes_before_a_marked_one_whatever_its_role(decompiler):
    """«she feeds milk TO THE CUB» — a marked phrase can stand anywhere after the verb and a bare one
    cannot, so the bare one goes first. Measured on `t-dc-2`, whose milk came back a destination."""
    out = decompiler.decompile(Zip(rows=[row(
        predicate="feed.v", agent=Box(head="whale.n", determination=Determination.DEFINITE),
        recipient=Box(head="cub.n", determination=Determination.DEFINITE, marker="to"),
        patient="milk.n")]))

    assert out.text == "The whale feeds milk to the cub."


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


def test_a_clause_with_no_participant_at_all_takes_the_EXPLETIVE(decompiler):
    """«It rains» — English requires a subject where the thought has no participant. The requirement
    is grammar and the word is a row."""
    out = decompiler.decompile(Zip(rows=[row(predicate="rain.v")]))

    assert out.text == "It rains."


# ------------------------------------------------------------------------------------------------
# agreement, and the person axis read backwards
# ------------------------------------------------------------------------------------------------


def test_the_SPEAKER_is_spoken_as_I_and_the_case_follows_the_position(spoken):
    """`me.n` is the key the station writes for «me» (req 20), and in subject position English says
    «I». The key carries its own person — the row for «me» has `person: 1` — so the decompiler never
    has to know which words are pronouns; it asks the rows for the same person in the case the
    POSITION calls for, and the case is grammar."""
    out = spoken.decompile(Zip(rows=[row(
        predicate="trust.v", agent=Box(head="me.n"), patient=Box(head="you.n"))]))

    assert out.text == "I trust you."


def test_the_verb_AGREES_and_the_copula_has_three_present_cells(spoken):
    """English inflects its present in one cell and its copula in three. Both are the rows': the
    `-s` is the roster's, and `am` · `are` · `is` are closed-class forms carrying the person features
    that pair them with a subject (`db/0023`)."""
    mine = spoken.decompile(Zip(rows=[row(patient=Box(head="me.n"), complement="happy.a")]))
    yours = spoken.decompile(Zip(rows=[row(patient=Box(head="you.n"), complement="happy.a")]))
    theirs = spoken.decompile(Zip(rows=[row(
        patient=Box(head="cat.n", determination=Determination.DEFINITE), complement="happy.a")]))

    assert (mine.text, yours.text, theirs.text) == (
        "I am happy.", "You are happy.", "The cat is happy.")


def test_a_pronoun_POSSESSOR_is_the_same_person_in_the_determiner_slot(spoken):
    """«my cat» — the possessor is `me.n` again, and what changes is the SLOT. `db/0021`'s flag could
    not answer this: seventeen possessives carry one meaning, so the choice is not about meaning at
    all but about position, which is what `use: determiner` records."""
    out = spoken.decompile(Zip(rows=[row(
        patient=Box(head="cat.n", determination=Determination.DEFINITE, relation="me.n"),
        complement="cute.a")]))

    assert out.text == "My cat is cute."


def test_a_possessor_that_is_not_a_pronoun_takes_the_GENITIVE(decompiler):
    """«Liguria's sea». The clitic is a row too (`genitive`, one form), so nothing is chosen here but
    the position — and a possessor precedes its head, which is word order."""
    out = decompiler.decompile(Zip(rows=[row(
        predicate="see.v", agent=Box(head="anna.n"),
        patient=Box(head="sea.n", determination=Determination.DEFINITE, relation="liguria.n"))]))

    assert out.text == "Anna sees liguria's sea."


# ------------------------------------------------------------------------------------------------
# the zip is flat and the sentence is nested
# ------------------------------------------------------------------------------------------------


def test_a_JOIN_is_a_connective_and_its_halves_are_not_sentences_of_their_own(decompiler):
    """The sentences are the ROOTS — rows nothing points at. A join operand is spoken inside its
    join, and the connective comes from the rows, keyed by the operator."""
    out = decompiler.decompile(Zip(rows=[
        row("a", predicate="rain.v"),
        row("b", predicate="sleep.v", agent=Box(head="cat.n", determination=Determination.DEFINITE)),
        JoinRow(name="j", truth=1.0, operator=Operator.AND, operands=["a", "b"]),
    ]))

    assert out.text == "It rains and the cat sleeps."


def test_what_the_halves_CLAIM_is_what_chooses_between_because_and_if(decompiler):
    """Same operator, two connectives, and the difference is written in the halves' own truth (req
    38): «I stayed home because it rained» claims both, «if it rains I stay home» claims neither. It
    is read off the zip, never guessed."""
    def implication(truth):
        return Zip(rows=[
            row("a", predicate="rain.v", truth=truth),
            row("b", predicate="sleep.v", truth=truth, agent=Box(head="cat.n")),
            JoinRow(name="j", truth=1.0, operator=Operator.IMPLY, operands=["a", "b"]),
        ])

    assert decompiler.decompile(implication(1.0)).text == "Because it rains, cat sleeps."
    assert decompiler.decompile(implication(None)).text == "If it rains, cat sleeps."


def test_a_BOUND_VARIABLE_is_spoken_where_it_first_occurs_and_is_definite_after(decompiler):
    """A variable mentioned twice is one thing mentioned twice — «some cat … the cat» — because
    saying «some cat» again would be a second cat, which is a different thought."""
    out = decompiler.decompile(Zip(rows=[
        QuantifierRow(name="b", scopes="j", binds="C", quantity=Quantity.EXISTENTIAL,
                      restriction=Box(head="cat.n")),
        row("a", predicate="sleep.v", agent=Box(head=Var(name="C"))),
        row("z", predicate="dream.v", agent=Box(head=Var(name="C"))),
        JoinRow(name="j", truth=1.0, operator=Operator.AND, operands=["a", "z"]),
    ]))

    assert out.text == "Some cat sleeps and the cat dreams."


def test_a_MODIFIER_folds_back_into_the_noun_phrase_the_compiler_took_it_out_of(decompiler):
    """«a black cat in the garden» compiles to three conjoined rows, and said back as three clauses
    it is unspeakable — the variable has no name to be the subject of one. So a claimed copular row
    whose only participant is a bound variable goes back inside the phrase, as an adjective or as a
    marked phrase. It is the inverse of the distribution the compiler performed."""
    out = decompiler.decompile(Zip(rows=[
        QuantifierRow(name="b", scopes="j", binds="C", quantity=Quantity.EXISTENTIAL,
                      restriction=Box(head="cat.n")),
        row("adj", patient=Box(head=Var(name="C")), complement="black.a"),
        row("in", patient=Box(head=Var(name="C")),
            complement=Box(head="garden.n", marker="in", determination=Determination.DEFINITE)),
        row("s", predicate="sleep.v", agent=Box(head=Var(name="C"))),
        JoinRow(name="j1", truth=1.0, operator=Operator.AND, operands=["adj", "in"]),
        JoinRow(name="j", truth=1.0, operator=Operator.AND, operands=["j1", "s"]),
    ]))

    assert out.text == "Some black cat in the garden sleeps."


def test_a_modifier_does_NOT_fold_out_of_an_implication(decompiler):
    """«every person WHO says a falsehood is wrong» is a relative clause and «every wrong person says
    a falsehood» is a different claim. A modifier distributes over «and» and nowhere else, so the
    antecedent of an implication stays a clause."""
    out = decompiler.decompile(Zip(rows=[
        QuantifierRow(name="b", scopes="j", binds="P", quantity=Quantity.UNIVERSAL,
                      restriction=Box(head="person.n", determination=Determination.GENERIC)),
        row("a", predicate="lie.v", agent=Box(head=Var(name="P"))),
        row("w", patient=Box(head=Var(name="P")), complement="wrong.a"),
        JoinRow(name="j", truth=1.0, operator=Operator.IMPLY, operands=["a", "w"]),
    ]))

    assert out.text == "Because every person lies, the person is wrong."


def test_each_clause_is_spoken_in_ITS_OWN_TENSE(decompiler):
    """**THE REASON THE THEATRE MOVED ONTO THE ROWS** (schema v5, the Captain 2026-09-20). One slot
    for a whole thought could not say «I went to Rome and I WILL GO to Genoa»: two clauses, two
    times. The field had always been documented as «the CLAUSE's spacetime» and had always sat
    somewhere else."""
    def when(at):
        return Theatre(interval=[at, at, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], epoch=1)

    out = decompiler.decompile(Zip(rows=[
        ContentRow(name="a", truth=1.0, predicate="go.v", theatre=when(-1.0),
                   boxes={Role.AGENT: Box(head="anna.n"),
                          Role.DESTINATION: Box(head="rome.n", marker="to")}),
        ContentRow(name="b", truth=1.0, predicate="go.v", theatre=when(1.0),
                   boxes={Role.AGENT: Box(head="anna.n"),
                          Role.DESTINATION: Box(head="genoa.n", marker="to")}),
        JoinRow(name="j", truth=1.0, operator=Operator.AND, operands=["a", "b"]),
    ]))

    assert out.text == "Anna went to rome and anna will go to genoa.", (
        "the past is an inflection and the future is a word, and each clause keeps its own")


def test_an_ATTITUDE_carries_its_own_time_and_not_its_content_s(decompiler):
    """«John SAID that the sky IS green» — a past saying about a present sky. The saying's own
    clause dissolves into the attitude row, so that row is the only place its tense can go."""
    out = decompiler.decompile(Zip(rows=[
        AttitudeRow(name="p", scopes="r", holder=Box(head="john.n"), verb="say.v",
                    theatre=Theatre(interval=[-1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], epoch=1)),
        row("r", patient=Box(head="sky.n", determination=Determination.DEFINITE),
            complement="green.a"),
    ]))

    assert out.text == "John said that the sky is green."


# ------------------------------------------------------------------------------------------------
# the prefix
# ------------------------------------------------------------------------------------------------


def test_an_ATTITUDE_wraps_the_clause_and_they_NEST_in_row_order(decompiler):
    """«Anna thinks that Bob believes that the cat is hungry» — two attitudes over one matrix, and
    the zip's order is the nesting. The complementizer is the table's: `that` is the one form for a
    join that asserts only its matrix, which is exactly what an attitude does."""
    out = decompiler.decompile(Zip(rows=[
        AttitudeRow(name="a1", scopes="h", holder=Box(head="anna.n"), verb="think.v"),
        AttitudeRow(name="a2", scopes="h", holder=Box(head="bob.n"), verb="believe.v"),
        row("h", patient=Box(head="cat.n", determination=Determination.DEFINITE),
            complement="hungry.a"),
    ]))

    assert out.text == "Anna thinks that bob believes that the cat is hungry."


def test_a_NEGATION_applies_to_what_FOLLOWS_it_and_that_is_the_whole_difference(decompiler):
    """«not all that glitters is gold» and «all that glitters is not gold» are two zips that differ
    only in the order of two prefix rows — and English spells them almost the same way. Row order is
    scope order (req 35), so the negation attaches to the next element in it."""
    def zip_(order):
        rows = {
            "neg": NegationRow(name="neg", scopes="g"),
            "b": QuantifierRow(name="b", scopes="g", binds="X", quantity=Quantity.UNIVERSAL,
                               restriction=Box(head="glitterer.n",
                                               determination=Determination.GENERIC)),
        }
        return Zip(rows=[*(rows[name] for name in order),
                         row("g", patient=Box(head=Var(name="X")),
                             complement=Box(head="gold.n",
                                            determination=Determination.GENERIC))])

    assert decompiler.decompile(zip_(("neg", "b"))).text == "Not every glitterer is gold."
    assert decompiler.decompile(zip_(("b", "neg"))).text == "Every glitterer is not gold."


def test_a_MODALITY_is_an_auxiliary_and_a_negation_outside_it_is_REFUSED(decompiler):
    """«a calculator can think» — and «a calculator does not NECESSARILY think» is an adverb the
    table does not carry. «must not» is not «not must», so saying the modal would move the negation
    inside it and claim the opposite: the row is not said at all."""
    plain = decompiler.decompile(Zip(rows=[
        ModalityRow(name="m", scopes="t", modality=Modality.POSSIBILITY),
        row("t", predicate="think.v", experiencer=Box(head="calculator.n")),
    ]))
    negated = decompiler.decompile(Zip(rows=[
        NegationRow(name="n", scopes="t"),
        ModalityRow(name="m", scopes="t", modality=Modality.NECESSITY),
        row("t", predicate="think.v", experiencer=Box(head="calculator.n")),
    ]))

    assert plain.text == "Calculator can think."
    assert negated.text == ""
    assert any("negation outside" in said for said in negated.refused)


def test_a_DOMAIN_is_fronted_and_an_unmarked_one_is_recorded_instead(decompiler):
    """«In Italy, he is married» — the domain is the fifth prefix element and English puts it first.
    «Legally» is an adverb DERIVED from `law.n` and the table holds no derivation, so an unmarked
    domain is recorded rather than spoken as a bare noun."""
    marked = decompiler.decompile(Zip(rows=[
        DomainRow(name="d", scopes="m", domain=Box(head="italy.n", marker="in")),
        row("m", patient=Box(head="he.n"), complement="married.a"),
    ]))
    bare = decompiler.decompile(Zip(rows=[
        DomainRow(name="d", scopes="m",
                  domain=Box(head="law.n", determination=Determination.GENERIC)),
        row("m", patient=Box(head="he.n"), complement="married.a"),
    ]))

    assert marked.text == "In italy, he is married."
    assert bare.text == "He is married."
    assert any("unmarked domain" in said for said in bare.unsaid)


def test_the_IMPERATIVE_is_recognised_as_the_shape_the_compiler_built(spoken):
    """«Close the door!» — the speaker WANTS it of the addressee and nothing is claimed (task 2d).
    Read backwards it is the same rule: without it the sentence comes back as «I want you to close
    the door», which is a different zip."""
    out = spoken.decompile(Zip(rows=[
        AttitudeRow(name="w", scopes="c", holder=Box(head="me.n"), verb="want.v"),
        ContentRow(name="c", predicate="close.v", truth=None, boxes={
            Role.AGENT: Box(head="you.n"),
            Role.PATIENT: Box(head="door.n", determination=Determination.DEFINITE)}),
    ]))

    assert out.text == "Close the door!"


# ------------------------------------------------------------------------------------------------
# the question
# ------------------------------------------------------------------------------------------------


def test_an_ASKED_truth_INVERTS_and_takes_a_question_mark(decompiler):
    """«Is the cat hungry?» — the row is fully bound and its truth is OPEN. Inversion and the mark
    are both structure, which is why the compiler never stored the `?` as a word."""
    out = decompiler.decompile(Zip(rows=[ContentRow(
        name="q", truth=Open(), boxes={
            Role.PATIENT: Box(head="cat.n", determination=Determination.DEFINITE),
            Role.COMPLEMENT: Box(head="hungry.a")})]))

    assert out.text == "Is the cat hungry?"


def test_an_EMBEDDED_question_fronts_its_word_and_takes_no_complementizer(decompiler):
    """«I don't know THAT WHO ate the fish» is not English: an embedded question is introduced by its
    own question word, which is already at the front of the clause."""
    out = decompiler.decompile(Zip(rows=[
        NegationRow(name="n", scopes="e"),
        AttitudeRow(name="a", scopes="e", holder=Box(head="anna.n"), verb="know.v"),
        row("e", predicate="eat.v", agent=Box(head=Open()),
            patient=Box(head="fish.n", determination=Determination.DEFINITE)),
    ]))

    assert out.text == "Anna does not know who eats the fish."


def test_an_OPEN_agent_in_a_plain_claim_is_said_with_the_PASSIVE(decompiler):
    """«The hammer is made of titanium» leaves its agent open because nobody knows who made it, and
    the zip records that exactly as it records a question (req 2). What separates them is the
    SENTENCE: English has one construction for a claim whose agent is not named, and it is the
    passive — so the clause is said, and nobody is asked who made the hammer."""
    out = decompiler.decompile(Zip(rows=[row(
        predicate="make.v", agent=Box(head=Open()),
        patient=Box(head="hammer.n", determination=Determination.DEFINITE),
        source=Box(head="titanium.n", marker="of"))]))

    assert out.text == "The hammer is made of titanium."


def test_the_VOICE_the_sentence_was_heard_in_is_spoken_back(decompiler):
    """req 27: roles normalize so they compare, and `topicality` is the one marker that keeps what
    that would otherwise destroy — that the speaker chose to talk about the mail. The marker had
    never been written by anything until the compiler started writing it."""
    out = decompiler.decompile(Zip(rows=[row(
        predicate="write.v",
        agent=Box(head="john.n", marker="by"),
        patient=Box(head="mail.n", determination=Determination.DEFINITE))],
        topicality=Role.PATIENT))

    assert out.text == "The mail is written by john."


# ------------------------------------------------------------------------------------------------
# and what it will not do
# ------------------------------------------------------------------------------------------------


def test_what_it_cannot_say_is_RECORDED_and_never_quietly_dropped(decompiler):
    """`unsaid` is `Compiled.unplaced`'s mirror: the thing that knows it failed to say something is
    this module, and throwing that away means re-deriving it later, worse."""
    out = decompiler.decompile(Zip(rows=[row(
        predicate="chase.v", agent=Box(head=Var(name="X")),
        patient=Box(head="dog.n", determination=Determination.DEFINITE))]))

    assert not out.whole
    assert any("nothing in the zip binds it" in said for said in out.unsaid)


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


def test_an_operator_English_does_not_MARK_is_refused_rather_than_approximated(decompiler):
    """Ten operators are closed by mathematics (req 41) and English marks six. `nimply` — «P but not
    Q» — has no row, and the nearest connective would say something else, so the join is refused and
    the reason is named."""
    out = decompiler.decompile(Zip(rows=[
        row("a", predicate="rain.v"),
        row("b", predicate="sleep.v", agent=Box(head="cat.n")),
        JoinRow(name="j", truth=1.0, operator=Operator.NIMPLY, operands=["a", "b"]),
    ]))

    assert out.text == ""
    assert any("nimply" in said for said in out.unsaid)
