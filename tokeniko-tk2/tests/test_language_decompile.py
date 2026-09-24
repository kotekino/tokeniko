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
    the position — and a possessor precedes its head, which is word order.

    *The box carries no article, which is what the compiler writes for «Liguria's sea»: a possessor
    and an article cannot share the determiner slot, and a box that has both is the next test's.*"""
    out = decompiler.decompile(Zip(rows=[row(
        predicate="see.v", agent=Box(head="anna.n"),
        patient=Box(head="sea.n", relation="liguria.n"))]))

    assert out.text == "Anna sees liguria's sea."


def test_a_possessor_BESIDE_an_article_is_said_after_the_noun_with_the_table_s_marker(decompiler):
    """«the result OF perception» (G3, 2026-09-24). The clitic spoke the possessor in the article's
    slot — «perception's result» — and the `definite` did not come back. English moves the possessor
    after the noun, and the WORD is the one `db/0012`'s selector settles to `relation`: read
    backwards from the table, never written here."""
    out = decompiler.decompile(Zip(rows=[row(
        predicate=None, patient=Box(head="cognition.n"),
        complement=Box(head="result.n", determination=Determination.DEFINITE,
                       relation="perception.n"))]))

    assert out.text == "Cognition is the result of perception."
    assert out.whole, out.unsaid


def test_the_post_nominal_marker_is_READ_FROM_THE_TABLE(decompiler):
    """Whatever row settles a marked phrase to the `relation` field is the word — and a table naming
    none leaves the clitic in place and SAYS what it lost, rather than choosing a preposition."""
    from tk2.language.closed import ClosedClasses

    other = ClosedClasses([
        {"version": 1, "form": "de", "word_class": "preposition", "role": "marker", "position": 0,
         "source": "a table in another language",
         "compiled": {"kind": "box", "roles": ["complement"],
                      "selector": [{"reads": "head_pos", "is": ["NOUN"], "then": "relation"},
                                   {"reads": "default", "then": "complement"}]}},
    ], "one marker for a possessor")
    assert Decompiler._markers_yielding(decompiler.table, "relation") == {"of"}
    assert Decompiler._markers_yielding(other, "relation") == {"de"}

    unmarked = Decompiler()
    unmarked._relation_markers = set()
    out = unmarked.decompile(Zip(rows=[row(
        predicate="see.v", agent=Box(head="anna.n"),
        patient=Box(head="sea.n", determination=Determination.DEFINITE, relation="liguria.n"))]))

    assert out.text == "Anna sees liguria's sea."
    assert any("possessed noun" in why for why in out.unsaid), out.unsaid


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


def _modal_zip(*prefix):
    """«a calculator thinks» under the prefix rows given, in the order given — which is scope order."""
    made = {"neg": NegationRow(name="n", scopes="t"),
            "nec": ModalityRow(name="m", scopes="t", modality=Modality.NECESSITY),
            "pos": ModalityRow(name="m", scopes="t", modality=Modality.POSSIBILITY)}
    return Zip(rows=[*(made[p] for p in prefix),
                     row("t", predicate="think.v", experiencer=Box(head="calculator.n"))])


def test_a_MODALITY_is_an_auxiliary_and_a_negation_INSIDE_it_follows_it(decompiler):
    """«a calculator can think» · «a calculator must not think» — □¬: the auxiliary stands before
    «not», so a negation after the modality in scope order is said after it in the clause."""
    assert decompiler.decompile(_modal_zip("pos")).text == "Calculator can think."
    assert decompiler.decompile(_modal_zip("nec", "neg")).text == "Calculator must not think."


def test_a_negation_OUTSIDE_a_necessity_is_said_with_the_adverb_after_it(decompiler):
    """**¬□ — «does not NECESSARILY think»** (`db/0035`, the fixpoint's G10). An auxiliary cannot say
    it: «must not» puts the negation inside and claims the opposite. An adverb stands AFTER «not»,
    so the order says the scope, and the adverb is the one curation flagged `spoken`. It rides with
    the negation, so every carrier — do, the copula, a question's inversion — takes it unchanged."""
    out = decompiler.decompile(_modal_zip("neg", "nec"))
    assert out.whole
    assert out.text == "Calculator does not necessarily think."

    copular = decompiler.decompile(Zip(rows=[
        NegationRow(name="n", scopes="t"),
        ModalityRow(name="m", scopes="t", modality=Modality.NECESSITY),
        row("t", patient=Box(head="calculator.n", determination=Determination.INDEFINITE),
            complement=Box(head="mind.n", determination=Determination.INDEFINITE)),
    ]))
    assert copular.text == "A calculator is not necessarily a mind."


def test_a_negation_OUTSIDE_a_possibility_is_said_CANNOT(decompiler):
    """¬◇ — «does not possibly think» is not how English says it, and until `db/0036` it was
    refused. «cannot» fuses the negation outside the possibility in one word, so ¬◇ is a MEANING of
    the closed classes, and they answer before the adverbs do. The voice is the row's `spoken`."""
    out = decompiler.decompile(_modal_zip("neg", "pos"))

    assert out.whole
    assert out.text == "Calculator cannot think."


def test_a_negation_INSIDE_a_possibility_is_not_can_not(decompiler):
    """◇¬ — «can» is the voice of ◇, and its «not» scopes OUTSIDE (`db/0036`): «can not think» is
    ¬◇, the opposite claim. The auxiliary has to be one whose «not» stays inside — «might»."""
    assert decompiler.decompile(_modal_zip("pos", "neg")).text == "Calculator might not think."
    assert decompiler.decompile(_modal_zip("nec", "neg")).text == "Calculator must not think."


def test_a_negation_on_BOTH_sides_of_a_necessity_is_refused_rather_than_halved(decompiler):
    """¬□¬ — one carrier for two negations. Dropping either says something the zip does not."""
    out = decompiler.decompile(Zip(rows=[
        NegationRow(name="n1", scopes="t"),
        ModalityRow(name="m", scopes="t", modality=Modality.NECESSITY),
        NegationRow(name="n2", scopes="t"),
        row("t", predicate="think.v", experiencer=Box(head="calculator.n")),
    ]))

    assert out.text == ""
    assert any("cannot both be said" in said for said in out.refused)


def test_EVERY_adverb_curation_gave_a_voice_can_be_REACHED(decompiler):
    """`test_EVERY_form_curation_gave_a_voice_can_be_REACHED` for the second roster: one voice per
    meaning, so the flags and the index keys are the same count — and a flag the lookup cannot hear
    is `db/0028`'s silent loss again."""
    flagged = [r for r in decompiler.adverbs._rows if r.get("spoken")]      # noqa: SLF001

    assert flagged, "the adverb table carries no voice — `db/0035` did not land"
    assert len(decompiler._adverb_spoken) == len(flagged), (                # noqa: SLF001
        "two flagged adverbs share a meaning and one of them will never be spoken")


def test_the_fixpoint_s_t_md_2_comes_back_as_the_zip_it_went_out_as():
    """**THE ROUND TRIP ITSELF** — the one the fixpoint scored SILENT until `db/0035`. Sentence to
    zip to sentence to zip, and the two zips must be IDENTICAL: the negation still outside the
    necessity, which is the whole of the meaning. The discourse «So» reaches neither zip."""
    from tk2.language import StanzaSkeletons, standing_closed_classes
    from tk2.language.compile import Compiler
    from tk2.language.utterance import compile_utterance
    from tools.drill_gate import DRILL_CONTEXT
    from tools.roundtrip import canonical

    provider = StanzaSkeletons()
    compiler = Compiler(standing_closed_classes())
    first = compile_utterance(compiler, provider("So a calculator does not necessarily think."),
                              DRILL_CONTEXT).zip
    assert [r.kind for r in first.rows][:2] == ["negation", "modality"], "the compiler moved"

    out = Decompiler(context=DRILL_CONTEXT).decompile(first)
    assert out.text == "A calculator does not necessarily think."

    second = compile_utterance(compiler, provider(out.text), DRILL_CONTEXT).zip
    assert canonical(second) == canonical(first)


@pytest.mark.parametrize("text, scope, back", [
    ("A calculator cannot think.", ["negation", "modality"], "A calculator cannot think."),
    ("A calculator need not think.", ["negation", "modality"],
     "A calculator does not necessarily think."),
])
def test_a_negated_modal_comes_back_as_the_scope_it_went_out_as(text, scope, back):
    """The round trip for the two meanings `db/0036` taught the compiler. ¬◇ from «cannot» is said
    «cannot»; ¬□ from «need not» keeps the voice it already had — «does not necessarily», the flagged
    adverb — and «need not» does not take it over. **The prefix ORDER is asserted apart**:
    `canonical` sorts the rows, so it cannot tell □¬ from ¬□."""
    from tk2.language import StanzaSkeletons, standing_closed_classes
    from tk2.language.compile import Compiler
    from tk2.language.utterance import compile_utterance
    from tools.drill_gate import DRILL_CONTEXT
    from tools.roundtrip import canonical

    provider = StanzaSkeletons()
    compiler = Compiler(standing_closed_classes())
    first = compile_utterance(compiler, provider(text), DRILL_CONTEXT).zip
    assert [r.kind for r in first.rows][:2] == scope

    out = Decompiler(context=DRILL_CONTEXT).decompile(first)
    assert out.text == back

    second = compile_utterance(compiler, provider(out.text), DRILL_CONTEXT).zip
    assert [r.kind for r in second.rows][:2] == scope
    assert canonical(second) == canonical(first)


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


def test_a_FUSED_quantifier_does_not_take_the_plain_one_s_slot(decompiler):
    """«nobody» is a negative quantity over PERSONS and «no» is a negative quantity, full stop —
    and until `db/0028` moved the role they compiled to the same thing and the spoken index held
    one slot for both. **The flag that arrived last won, in silence**: «There are no cats» came
    back «There is nobody cat», «I work every day» came back «I work everyone day», and the
    fixpoint lost five sentences to it on 2026-09-20.

    Both readings are asked here in one test because the defect is the PAIR, not either half.
    """
    determiner = decompiler.decompile(Zip(rows=[row(
        predicate="sleep.v", agent=Box(head="cat.n", quantity=Quantity.UNIVERSAL))]))
    assert determiner.text == "Every cat sleeps."

    fused = decompiler.decompile(Zip(rows=[
        QuantifierRow(name="q0", scopes="r0", binds="x0", quantity=Quantity.UNIVERSAL,
                      restriction=Box(head=Open(sort="person"))),
        row(predicate="sleep.v", agent=Box(head=Var(name="x0"))),
    ]))
    assert fused.text == "Everyone sleeps."


def test_EVERY_form_curation_gave_a_voice_can_be_REACHED(decompiler):
    """**THE ARITHMETIC THAT WAS NOT BEING READ.** The spoken index is a dict keyed on a meaning,
    so two flagged rows that share a key do not raise — the second silently replaces the first, and
    the form curation chose is never spoken again. That is exactly how `db/0028` cost five
    sentences: seventeen rows carried the flag and the index held twelve keys.

    A count is the whole test. If it ever drops below the flags again, curation has said something
    the decompiler cannot hear, and the migration's own `_meaning()` has drifted from `_key()`.
    """
    flagged = [r for r in decompiler.table._rows if r.get("spoken")]        # noqa: SLF001

    assert flagged, "the table carries no voices at all — `db/0021` did not land"
    assert len(decompiler._spoken) == len(flagged), (                       # noqa: SLF001
        "two flagged rows share a key and one of them will never be spoken")


def test_the_EXISTENTIAL_copula_agrees_with_the_thing_said_to_exist(decompiler):
    """«There IS a cat» · «There ARE cats» — the expletive holds the subject position and the verb
    agrees with what was displaced, not with the word holding its place.

    **TWO DEFECTS IN ONE LINE, and schema v6 uncovered both** *(found by the 1st Officier)*. The
    agreement was hard-coded third-singular, so «There are no cats» came back «There is no cats»;
    and `be` was reaching the REGULAR verb path, where a non-third-singular is spoken as the bare
    lemma — «There be no cats». An existential row is not flagged copular because existential `be`
    is content (req 31), so nothing routed it to the paradigm that has three cells.
    """
    plural = decompiler.decompile(Zip(rows=[
        QuantifierRow(name="q0", scopes="r0", binds="x0", quantity=Quantity.NEGATIVE,
                      restriction=Box(head="cat.n", number="pl", quantity=Quantity.NEGATIVE)),
        row(predicate="be.v", patient=Box(head=Var(name="x0"))),
    ]))
    assert plural.text == "There are no cats."

    single = decompiler.decompile(Zip(rows=[row(
        predicate="be.v",
        patient=Box(head="cat.n", number="sg", determination=Determination.INDEFINITE))]))
    assert single.text == "There is a cat."


def test_the_UNIVERSAL_has_two_voices_and_the_NOUN_picks(decompiler):
    """«every cat» · «all cats» — one quantity, two words, and the number of the noun chooses.

    `db/0021`'s flag answers «this meaning has several forms, which do we say?» with ONE form, and
    English has two here, so every plural universal came out «Every human beings are animals». The
    number is now part of the key on both sides (`db/0029`).

    **A row that states no number answers for either**, which is why «no» is asked for last: it is
    one word for «no cat» and «no cats» and says so by carrying nothing.
    """
    assert decompiler.the_form("quantificational", _number="sg",
                               kind="quantifier", quantity="universal") == "every"
    assert decompiler.the_form("quantificational", _number="pl",
                               kind="quantifier", quantity="universal") == "all"
    for number in ("sg", "pl", None):
        assert decompiler.the_form("quantificational", _number=number,
                                   kind="quantifier", quantity="negative") == "no"


def test_a_determiner_s_number_is_the_NOUN_S_and_not_its_own():
    """**ONE COLUMN MUST NOT CARRY TWO FACTS.** A pronoun's `number` is ITS OWN — «she» is singular
    — and `Compiler._unknown()` copies it into the `Open` a described unknown carries (schema v4).
    A determiner's is the number of the noun it TAKES, and `db/0029` puts that in `takes_number`.

    Written into the same column, «All that glitters is not gold» compiled its bare «all» to
    `Open(number='pl')` — a restriction the sentence never stated — and `aw-13`/`aw-14` went
    DISAGREED at the drill gate **while the fixpoint stayed flat at 66**. That is the whole argument
    for keeping both instruments, and the reason this test asks the migration and not the rendering.

    *`both` · `neither` · `either` carry `number: dual` from an older migration and keep it: «neither
    of the two» is a fact about the WORD, which is what that column has always been for.*
    """
    from tk2.migrations import discover

    before = next(m for m in discover() if m.number == 28).load().CLOSED_CLASS_ROWS
    after = next(m for m in discover() if m.number == 29).load().CLOSED_CLASS_ROWS

    assert len(before) == len(after)
    moved = [new["form"] for new, was in zip(after, before)
             if (new.get("features") or {}).get("number") != (was.get("features") or {}).get("number")]
    assert not moved, f"{moved} had their own `number` changed by the determiner migration"


def test_a_RESTRICTION_is_spoken_inside_the_phrase_it_restricts(decompiler):
    """«Every cat THAT SLEEPS is happy» — the clause says WHICH cats, and the compiler marks it by
    leaving the truth slot empty (a restriction is stated, never claimed).

    **DROPPING IT IS NOT BREVITY, IT IS A WIDER CLAIM THAN THE ZIP HOLDS.** «Every cat is happy»
    asserts something «every cat that sleeps is happy» does not, so the row cannot simply be left
    out — and it cannot be said as a sentence either, because a clause that claims nothing is not
    one. It goes where English puts it: after the noun.
    """
    out = decompiler.decompile(Zip(rows=[
        QuantifierRow(name="q0", scopes="r1", binds="x0", quantity=Quantity.UNIVERSAL,
                      restriction=Box(head="cat.n", number="sg")),
        ContentRow(name="r0", truth=None, predicate="sleep.v",
                   boxes={Role.AGENT: Box(head=Var(name="x0"))}),
        row("r1", predicate=None, experiencer=Box(head=Var(name="x0")),
            complement=Box(head="happy.a")),
    ]))

    assert out.text == "Every cat that sleeps is happy."


def test_a_relative_gap_in_the_AGENT_box_is_the_antecedent_not_a_passive(decompiler):
    """«You learn from every mind that TRUSTS YOU» — the gap is the agent and the row has a second
    box, which is exactly where the passive test stands: an agent nobody described is what the
    passive leaves out. The gap's head is the antecedent's VARIABLE, not an OPEN, and reading
    `.described` off it raised `AttributeError` (the fixpoint's eleven, «found outside the brief» 1).

    A known agent is not an unknown one: the clause keeps its subject, and the relative pronoun is it.
    """
    out = decompiler.decompile(Zip(rows=[
        QuantifierRow(name="q0", scopes="r0", binds="x0", quantity=Quantity.UNIVERSAL,
                      restriction=Box(head="mind.n", number="sg")),
        row("r0", predicate="learn.v", experiencer="you.n",
            source=Box(head=Var(name="x0"), marker="from")),
        ContentRow(name="r1", truth=None, predicate="trust.v",
                   boxes={Role.AGENT: Box(head=Var(name="x0")),
                          Role.PATIENT: Box(head="you.n")}),
    ]))

    assert out.text == "You learn from every mind that trusts you."


def test_a_MARKED_relative_gap_strands_its_marker(decompiler):
    """«every mind that you learn FROM» — the gap's box carries a marker (req 65), and popping the box
    for the relative pronoun used to drop it with the box: the antecedent came back unmarked, which
    is a different role. `that` cannot be pied-piped, so English strands the marker at the end.
    """
    out = decompiler.decompile(Zip(rows=[
        QuantifierRow(name="q0", scopes="r0", binds="x0", quantity=Quantity.UNIVERSAL,
                      restriction=Box(head="mind.n", number="sg")),
        row("r0", predicate="trust.v", experiencer="you.n", patient=Box(head=Var(name="x0"))),
        ContentRow(name="r1", truth=None, predicate="learn.v",
                   boxes={Role.EXPERIENCER: Box(head="you.n"),
                          Role.SOURCE: Box(head=Var(name="x0"), marker="from")}),
    ]))

    assert out.text == "You trust every mind that you learn from."


def test_a_bare_quantifier_takes_its_CLAUSE_as_its_noun(decompiler):
    """«All that glitters is not gold» — «all» says nothing about what it ranges over, so the
    restricting row is not a clause hanging off a noun: it IS the noun.

    Both `aw-13` and `aw-14` were SILENT on exactly this, and the phrase takes the PLURAL universal
    because «every» is the form that wants a singular count noun and a clause is not one.
    """
    out = decompiler.decompile(Zip(rows=[
        QuantifierRow(name="q0", scopes="r1", binds="x0", quantity=Quantity.UNIVERSAL,
                      restriction=Box(head=Open())),
        NegationRow(name="p1", scopes="r1"),
        ContentRow(name="r0", truth=None, predicate="glitter.v",
                   boxes={Role.AGENT: Box(head=Var(name="x0"))}),
        row("r1", predicate=None, patient=Box(head=Var(name="x0")),
            complement=Box(head="gold.n", number="sg")),
    ]))

    assert out.text == "All that glitters is not gold."


def test_a_join_s_unasserted_halves_are_NOT_restrictions(decompiler):
    """«If it rains, I stay home» — both halves claim nothing and a conditional over one variable
    would put them both in reach of the rule above. A join consumes its operands first, and that is
    what keeps the antecedent of a conditional out of the noun phrase it shares a variable with.

    Without the ordering, «Smoking causes cancer» — a universal over a person, with two unasserted
    halves sharing that person — would have had its own halves eaten into the subject.
    """
    out = decompiler.decompile(Zip(rows=[
        QuantifierRow(name="q0", scopes="jn", binds="x0", quantity=Quantity.UNIVERSAL,
                      restriction=Box(head="person.n", number="sg")),
        ContentRow(name="s", truth=None, predicate="smoke.v",
                   boxes={Role.AGENT: Box(head=Var(name="x0"))}),
        ContentRow(name="k", truth=None, predicate="develop.v",
                   boxes={Role.EXPERIENCER: Box(head=Var(name="x0")),
                          Role.PATIENT: Box(head="cancer.n", number="sg")}),
        JoinRow(name="jn", truth=1.0, operator=Operator.IMPLY, operands=["s", "k"]),
    ]))

    assert "smokes" in out.text and "develops" in out.text, out.text


# ------------------------------------------------------------------------------------------------
# G4 — a relative clause is its SHAPE, whatever its truth; and a consumed row is always accounted
# ------------------------------------------------------------------------------------------------


def _definite(noun, scopes, number="sg"):
    """Schema v8's quantity-less binder — what the compiler mints for «the cat THAT …»."""
    return QuantifierRow(name="q0", scopes=scopes, binds="y0",
                         restriction=Box(head=noun, determination=Determination.DEFINITE,
                                         number=number))


def test_a_CLAIMED_relative_clause_is_still_a_relative_clause(decompiler):
    """«The cat that sleeps is happy» — a definite description's clause is CLAIMED on purpose (a
    presupposition: the brain gets the fact), and `_read` knew only unclaimed restrictions, so it
    came back as two sentences, «The cat sleeps. The cat is happy.» The row shares the variable of a
    binder that does not scope it, and that shape is what makes it a relative clause."""
    out = decompiler.decompile(Zip(rows=[
        _definite("cat.n", scopes="r1"),
        row("r0", predicate="sleep.v", agent=Box(head=Var(name="y0"))),
        row("r1", experiencer=Box(head=Var(name="y0")), complement=Box(head="happy.a")),
    ]))

    assert out.text == "The cat that sleeps is happy."
    assert out.whole, (out.unsaid, out.refused)


def test_a_claimed_OBJECT_relative_fronts_its_pronoun(spoken):
    """«I like the fish that the cat eats» — the binder scopes the liking, the eating shares its
    variable in the patient box, and the gap is the object the pronoun fronts."""
    out = spoken.decompile(Zip(rows=[
        _definite("fish.n", scopes="r0"),
        row("r0", predicate="like.v", experiencer="me.n", patient=Box(head=Var(name="y0"))),
        row("r1", predicate="eat.v",
            agent=Box(head="cat.n", determination=Determination.DEFINITE, number="sg"),
            patient=Box(head=Var(name="y0"))),
    ]))

    assert out.text == "I like the fish that the cat eats."


def test_an_UNCLAIMED_clause_about_a_referring_phrase_is_REFUSED(decompiler):
    """The truth decides whether the shape can be SAID. The compiler reads a relative clause on a
    quantity-less binder back as claimed, so an unclaimed one said that way would come back a claim
    — more than the zip, the sin (req 8). Nothing is said, and the refusal names the row."""
    out = decompiler.decompile(Zip(rows=[
        _definite("cat.n", scopes="r1"),
        ContentRow(name="r0", truth=None, predicate="sleep.v",
                   boxes={Role.AGENT: Box(head=Var(name="y0"))}),
        row("r1", experiencer=Box(head=Var(name="y0")), complement=Box(head="happy.a")),
    ]))

    assert "sleeps" not in out.text
    assert any(why.startswith("r0:") for why in out.refused), out.refused


def test_a_CLAIMED_restriction_of_a_quantifier_is_said_and_its_claim_RECORDED(decompiler):
    """«every cat that sleeps» comes back a restriction — stated, not claimed. Said that way, a
    claimed row loses its claim: half-said, which is legal, and recorded so it is never silent."""
    out = decompiler.decompile(Zip(rows=[
        QuantifierRow(name="q0", scopes="r1", binds="x0", quantity=Quantity.UNIVERSAL,
                      restriction=Box(head="cat.n", number="sg")),
        row("r0", predicate="sleep.v", agent=Box(head=Var(name="x0"))),
        row("r1", experiencer=Box(head=Var(name="x0")), complement=Box(head="happy.a")),
    ]))

    assert out.text == "Every cat that sleeps is happy."
    assert any(why.startswith("r0:") and "claim" in why for why in out.unsaid), out.unsaid


def _something_you_do_not_know():
    """«If I tell you something that you do not know, you learn it.» as the station compiles it."""
    return Zip(rows=[
        QuantifierRow(name="q0", scopes="r0", binds="x0", quantity=Quantity.EXISTENTIAL,
                      restriction=Box(head=Open(sort="thing"))),
        NegationRow(name="p1", scopes="r1"),
        ContentRow(name="r0", truth=None, predicate="tell.v",
                   boxes={Role.AGENT: Box(head="me.n"), Role.RECIPIENT: Box(head="you.n"),
                          Role.PATIENT: Box(head=Var(name="x0"))}),
        ContentRow(name="r1", truth=None, predicate="know.v",
                   boxes={Role.EXPERIENCER: Box(head="you.n"),
                          Role.PATIENT: Box(head=Var(name="x0"))}),
        ContentRow(name="r2", truth=None, predicate="learn.v",
                   boxes={Role.EXPERIENCER: Box(head="you.n"),
                          Role.PATIENT: Box(head=Open(person=3, number="sg", gender="n"))}),
        JoinRow(name="j0", truth=1.0, operator=Operator.IMPLY, operands=["r0", "r2"]),
    ])


def test_a_FUSED_quantifier_still_takes_its_relative_clause(spoken):
    """«something THAT YOU DO NOT KNOW» (G4a). The fused branch returned before the restriction, and
    the row `_read` had consumed vanished with no word in `unsaid`: «If I tell you something, you
    learn it» — a wider claim than the zip. English puts the clause after the fused word."""
    out = spoken.decompile(_something_you_do_not_know())

    assert out.text == "If I tell you something that you do not know, you learn it."


def test_a_CONSUMED_row_that_never_reaches_the_text_is_NAMED(monkeypatch):
    """**THE INVARIANT, NOT THE BRANCH.** Whatever path forgets a consumed row, the account at the end
    of `decompile` names it — here the phrase is made to forget its clauses, which is exactly the
    shape of the bug G4a was, and the row still cannot vanish in silence."""
    forgetful = Decompiler(context=Context(speaker="me.n", addressee="you.n"))
    monkeypatch.setattr(forgetful, "_trailing", lambda name, binder, rd: ([], []))

    out = forgetful.decompile(_something_you_do_not_know())

    assert "know" not in out.text
    assert any("r1" in why and "never reached the text" in why for why in out.unsaid), out.unsaid


def test_a_restriction_whose_phrase_is_NEVER_SAID_is_named(decompiler):
    """The same account without any patching: a binder that reaches no box never speaks its
    phrase, so the clause consumed as its restriction is named rather than lost."""
    out = decompiler.decompile(Zip(rows=[
        QuantifierRow(name="q0", scopes="r1", binds="x0", quantity=Quantity.UNIVERSAL,
                      restriction=Box(head="cat.n", number="sg")),
        ContentRow(name="r0", truth=None, predicate="sleep.v",
                   boxes={Role.AGENT: Box(head=Var(name="x0"))}),
        row("r1", predicate="sleep.v", agent=Box(head="anna.n")),
    ]))

    assert out.text == "Anna sleeps."
    assert any(why.startswith("content row r0:") for why in out.unsaid), out.unsaid
