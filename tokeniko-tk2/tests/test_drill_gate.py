"""THE DRILL GATE — requirement 18's control, and the tests that prove it can FAIL.

The gate itself needs stanza, so almost everything here is written against the pure comparison with
hand-made zips on both sides. **That is not a convenience.** A gate nobody has seen fail is a gate
nobody can trust, and the whole reason this one exists is that the drill and the UD gate had never
been able to disagree with each other for a day while a wrong role sat in every copular sentence.

The few tests that actually parse carry `@pytest.mark.skeleton`, like every other test that does.
"""

import pytest

from tests.fixtures.drill import CASES
from tk2.tkzip.schema import (
    AttitudeRow,
    Box,
    ContentRow,
    DomainRow,
    JoinRow,
    Modality,
    ModalityRow,
    Open,
    Operator,
    Role,
    Var,
    Zip,
)
from tools.drill_gate import AGREED, DISAGREED, MISSING, compare, filler, signature


def row(name, predicate=None, **boxes):
    return ContentRow(name=name, predicate=predicate, truth=1.0,
                      boxes={Role(k): (v if isinstance(v, Box) else Box(head=v))
                             for k, v in boxes.items()})


# ------------------------------------------------------------------------------------------------
# it reports a disagreement when there is one — the test that makes the gate worth having
# ------------------------------------------------------------------------------------------------


def test_the_SAME_FILLER_under_two_role_names_is_a_DISAGREEMENT():
    """**THE DEFECT THIS GATE WAS BUILT FOR, reproduced.** On 2026-09-16 the compile core put `topic`
    where E2 had ruled `patient` for every copular subject, contradicting 43 hand-compiled rows, and
    no test went red for a day."""
    station = Zip(rows=[row("r0", complement="teacher.n", topic="sue.n")])
    drill = Zip(rows=[row("r0", complement="teacher.n", patient="sue.n")])

    reading = compare(station.model_copy(), drill)

    assert reading.verdict == DISAGREED
    assert reading.conflicts == ["sue.n: the station says topic, the drill says patient"]


def test_the_same_filler_under_the_same_role_AGREES():
    station = Zip(rows=[row("r0", "chase.v", agent="cat.n", patient="dog.n")])
    drill = Zip(rows=[row("x", "chase.v", agent="cat.n", patient="dog.n")])

    reading = compare(station, drill)

    assert reading.verdict == AGREED
    assert (reading.agreed, reading.conflicts) == (2, [])


def test_the_SAME_ROLE_holding_two_different_people_is_a_DISAGREEMENT():
    """**THE MIRROR TEST, and the defect IT was built for.** Added 2026-09-17: the pass above pairs
    boxes by their FILLER and asks whether the two zips agree on its role — which cannot see the only
    shape the person axis fails in. «John said to Marie that you are late» compiled about Marie is an
    ordinary `patient` on an ordinary row, and the sole thing wrong with it is WHO is in it.
    """
    station = Zip(rows=[row("r0", complement="late.a", patient="marie.n")])
    drill = Zip(rows=[row("l", complement="late.a", patient="you.n")])

    reading = compare(station, drill)

    assert reading.verdict == DISAGREED
    assert reading.conflicts == ["patient: the station says marie.n, the drill says you.n"]


def test_a_role_the_station_did_not_reach_is_MISSING_and_never_a_conflict():
    """E3 is unfinished by construction, so «the drill has it and we do not» must be counted apart.
    Averaged in, it would make an incomplete station look like a wrong one — and the report would
    stop being read."""
    station = Zip(rows=[row("r0", "give.v", agent="she.n")])
    drill = Zip(rows=[row("x", "give.v", agent="she.n", recipient="me.n", patient="book.n")])

    reading = compare(station, drill)

    assert reading.verdict == AGREED and reading.conflicts == []
    assert sorted(reading.missing_roles) == ["book.n (patient)", "me.n (recipient)"]


def test_a_row_the_station_did_not_build_is_MISSING():
    station = Zip(rows=[row("r0", "rain.v")])
    drill = Zip(rows=[row("a", "rain.v"), row("b", "stay.v", agent="me.n")])

    reading = compare(station, drill)

    assert reading.missing_rows == ["stay.v"]
    assert reading.paired == 1


# ------------------------------------------------------------------------------------------------
# what it refuses to call a disagreement
# ------------------------------------------------------------------------------------------------


def test_a_VARIABLE_is_never_a_conflict():
    """The station and the drill number their variables independently, so `x0` against `P` is not a
    disagreement about anything. Comparing them would make the gate cry wolf on every quantified
    sentence, which is most of the drill."""
    station = Zip(rows=[row("r0", "sleep.v", agent=Box(head=Var(name="x0")))])
    drill = Zip(rows=[row("b", "sleep.v", agent=Box(head=Var(name="P")))])

    reading = compare(station, drill)

    assert reading.conflicts == []
    assert reading.verdict == MISSING, "nothing comparable was found, and that is not agreement"


def test_an_OPEN_head_is_never_a_conflict():
    station = Zip(rows=[row("r0", "sleep.v", agent=Box(head=Open()))])
    drill = Zip(rows=[row("b", "sleep.v", agent=Box(head=Open()))])

    assert compare(station, drill).conflicts == []


def test_rows_pair_by_CONTENT_and_not_by_position():
    """Two independently-built zips order their rows by their own rules — the station by clause
    order, the drill by the Captain's hand — so pairing by index would compare unrelated rows."""
    station = Zip(rows=[row("r0", "stay.v", agent="me.n"), row("r1", "rain.v")])
    drill = Zip(rows=[row("a", "rain.v"), row("b", "stay.v", agent="me.n")])

    reading = compare(station, drill)

    assert reading.paired == 2 and reading.conflicts == []


def test_a_COPULAR_row_pairs_on_its_complement():
    """A copular row earns no predicate (req 31), so there is no key to pair on — the complement's
    head is what «Sue is a teacher» is about in both zips."""
    assert signature(row("r0", complement="teacher.n", patient="sue.n")) == "=teacher.n"
    assert signature(row("r0", "chase.v", agent="cat.n")) == "chase.v"
    assert filler(Box(head=Var(name="x0"))) == "var:x0"
    assert filler(Box(head=Open())) == "open"


# ------------------------------------------------------------------------------------------------
# the live run — the only test here that parses
# ------------------------------------------------------------------------------------------------


@pytest.mark.skeleton
# ------------------------------------------------------------------------------------------------
# THE PREFIX AND THE JOINS — the fourth widening, 2026-09-19
# ------------------------------------------------------------------------------------------------


def wants(name, scopes, who="me.n", verb="want.v", to=None, strength=None):
    return AttitudeRow(name=name, scopes=scopes, verb=verb, holder=Box(head=who),
                       addressee=None if to is None else Box(head=to), strength=strength)


def test_an_attitude_whose_STRENGTH_the_station_leaves_EMPTY_is_a_DISAGREEMENT():
    """**THE FOURTH BLINDNESS, and the case it was widened for** (req 23). `aw-21` hand-compiles
    «Close the door!» as POV(me · want) at 0.9; the station wrote nothing there, and for a day the
    gate could not say so, because it compared `kind="content"` and nothing else.

    The STATE is compared and never the magnitude — «the station says nothing about how strongly
    this wants» is a defect, «0.85 where the table says 0.9» is a migration."""
    closing = row("r0", "close.v", agent="you.n")
    station = Zip(rows=[wants("p0", "r0"), closing])
    drill = Zip(rows=[wants("w", "cl", strength=0.9), row("cl", "close.v", agent="you.n")])

    reading = compare(station, drill)

    assert reading.verdict == DISAGREED
    assert reading.conflicts == [
        "attitude over close.v: strength — the station says unstated, the drill says stated"]
    assert compare(Zip(rows=[wants("p0", "r0", strength=0.4), closing]), drill).conflicts == [], (
        "a value against a value says nothing about whether a strength was stated")


def test_attitudes_over_ONE_row_pair_by_their_VERB_and_not_by_position():
    """**A MISSING DRESSED AS A DEFECT, caught the day the widening was written.** «Marie said "John
    told me 'you are late'"» holds two sayings over one row. Paired by document order, the station's
    single telling was compared against Marie's saying and reported three conflicts — while what it
    had actually done was read John's telling exactly right and miss the outer saying."""
    late = row("l", complement="late.a", patient="marie.n")
    station = Zip(rows=[wants("p0", "l", who="john.n", verb="tell.v", to="marie.n"), late])
    drill = Zip(rows=[wants("a1", "l", who="marie.n", verb="say.v"),
                      wants("a2", "l", who="john.n", verb="tell.v", to="marie.n"), late])

    reading = compare(station, drill)

    assert reading.conflicts == []
    assert reading.missing_prefix == ["attitude say.v over =late.a"]


def test_the_station_saying_something_ELSE_about_the_same_row_is_a_SUBSTITUTION():
    """Absence and substitution are different facts, and identity pairing alone can only see the
    first. A leftover on BOTH sides over the same row is the station saying something else — the
    shape `aw-20` would have, if the station built an attitude for «suppose» at all (req 24)."""
    hungry = row("h", complement="hungry.a", experiencer="cat.n")
    station = Zip(rows=[wants("p0", "h", verb="want.v"), hungry])
    drill = Zip(rows=[wants("sup", "h", verb="suppose.v"), hungry])

    reading = compare(station, drill)

    assert reading.verdict == DISAGREED
    assert reading.conflicts == [
        "attitude over =hungry.a: the station says want.v, the drill says suppose.v"]


def test_a_prefix_row_the_station_did_not_BUILD_is_MISSING_and_never_a_conflict():
    """Two thirds of the prefix is E3 unfinished — domains, most quantifiers, the negation rows. A
    widening that turned all of it red would have taught nothing."""
    driving = row("d", "drive.v", agent="you.n")
    station = Zip(rows=[ModalityRow(name="m0", scopes="d", modality=Modality.POSSIBILITY), driving])
    drill = Zip(rows=[DomainRow(name="dom", scopes="d", domain=Box(head="italy.n")),
                      ModalityRow(name="mod", scopes="d", modality=Modality.POSSIBILITY), driving])

    reading = compare(station, drill)

    assert reading.conflicts == []
    assert reading.missing_prefix == ["domain italy.n over drive.v"]
    assert reading.said == 1, "the modality paired and agreed"


def test_a_MODALITY_read_as_the_other_one_IS_a_conflict():
    """◇ against □ is not a magnitude and not an absence: «software CAN be minds» compiled as «MUST»
    is a different claim about the world."""
    being = row("d", "be.v", patient="software.n")
    station = Zip(rows=[ModalityRow(name="m0", scopes="d", modality=Modality.NECESSITY), being])
    drill = Zip(rows=[ModalityRow(name="m", scopes="d", modality=Modality.POSSIBILITY), being])

    assert compare(station, drill).conflicts == [
        "modality over be.v: modality — the station says necessity, the drill says possibility"]


def test_a_JOIN_claiming_what_the_drill_leaves_UNCLAIMED_is_a_DISAGREEMENT():
    """The joins were outside the instrument too, and `db/0017` turned on exactly this: «A or B»
    claimed its halves, and `nor` claiming both contradicted its own join. A join pairs on its
    operator over its operands' keys — no name is compared — and is read on its truth slot."""
    halves = [row("a", "rain.v"), row("b", "stay.v")]
    station = Zip(rows=[*halves, JoinRow(name="j", operator=Operator.IMPLY,
                                         operands=["a", "b"], truth=1.0)])
    drill = Zip(rows=[*halves, JoinRow(name="x", operator=Operator.IMPLY,
                                       operands=["a", "b"], truth=None)])

    reading = compare(station, drill)

    assert reading.verdict == DISAGREED
    assert reading.conflicts == [
        "truth of (imply rain.v | stay.v): the station says stated, the drill says unstated"]
    assert compare(drill, drill).conflicts == [], "the same join against itself agrees"


def test_a_question_compiled_as_a_CLAIM_is_a_DISAGREEMENT():
    """**THE THIRD BLINDNESS, and the defect it hid** (req 21, 2026-09-18). The gate compared roles
    and never truth, so «Is the cat hungry?» compiled at 1.0 against the drill's OPEN and agreed.
    The STATE is compared — a value, OPEN, or unstated — never the value itself."""
    asked = ContentRow(name="e", predicate="exist.v", truth=Open(), boxes={})
    claimed = ContentRow(name="r0", predicate="exist.v", truth=1.0, boxes={})
    denied = ContentRow(name="d", predicate="exist.v", truth=0.0, boxes={})

    reading = compare(Zip(rows=[claimed]), Zip(rows=[asked]))
    assert reading.verdict == DISAGREED
    assert reading.conflicts == [
        "truth of exist.v: the station says stated, the drill says OPEN"]

    assert compare(Zip(rows=[claimed]), Zip(rows=[denied])).conflicts == [], (
        "a value against a value is not a disagreement about whether anything was asked")


@pytest.mark.skeleton
def test_the_station_and_the_drill_disagree_only_where_a_question_is_NAMED():
    """**THE RATCHET.** Three disagreements on 2026-09-18, in three families — and the point of the
    list is that every entry is named, dated and attributable. The count may only go DOWN.

      one    ~~the station builds no `DomainRow`~~ — **`aw-15` CLOSED 2026-09-22**: the fifth
             prefix element is built, «In Italy» is the jurisdiction and France has its `location`
             box back. It had been displacing France into `unplaced` — a word LOST, not merely
             misfiled, which is why it showed as a conflict rather than a missing row.
      one    the named-individual hole — `aw-19`, «I ate with Anna» (E3b).
      one    A PROVIDER DEFECT — `t-ws-7`, «a mind CAN be an animal or a mind CAN be a software».
             Its halves are claimed ON PURPOSE (free choice, the Captain's ruling (b)), and the
             station builds free choice — but stanza reads «an animal or A MIND» as one noun phrase.
             Where the provider gives a structure we know is wrong the station abstains (`q-5`).

    **`q-2` LEFT TOO**: stanza labels the lone object of «I trust you» `iobj`, which UD reserves for
    a clause that also has a direct object, and the station now abstains on that mislabel rather
    than inventing a recipient — the role goes MISSING, which is not a defect, and the rotation the
    case exists to test is untouched.

    **THE SUBJECT-ROLE FAMILY IS GONE** (req 22, `db/0018`, 2026-09-18) — ten witnesses, the largest
    family this list ever held, closed by a supersense rule as rows plus one exception; and the
    drill itself was corrected in twelve rows where the bench showed it contradicting its own
    principle. **The polar question and the imperative went the same day** (tasks 2c, 2d).

    **AND THE LIST SURVIVED A FOURTH WIDENING, 2026-09-19** — which is the only kind of survival
    that means anything. The gate now reads the PREFIX and the JOINS as well: 89 prefix rows and 50
    joins that had never been compared. It went to five on the instant, and both new entries were
    real — `aw-21`'s empty `strength` (req 23, closed by `db/0020`) and `t-of-1`'s *happy*, the one
    witness lost to repairing a hash-order coin toss in `derived_supersense` (closed by `db/0019`).
    *Three entries, measured by a strictly larger instrument, is not the same three entries.*

    **AND A FIFTH WIDENING, 2026-09-20 — THE GATE LEARNED TO READ AN OPEN SLOT.** Every open box
    used to flatten to the word «open», so «he» compared EQUAL to «she», and a box the drill had
    described compared equal to one the station left blank. Schema v4 gives an open slot the person,
    number, gender and sort the sentence gave it, and the comparator reads them — an OPEN nobody
    described still abstains, because «I do not know» contradicts nothing.

    **It went to five, and both new entries are the same unbuilt thing, named:** `q-6` and `t-dc-5`,
    where the station says *an unidentified feminine singular person* and the drill says `marie.n`.
    **That is ANAPHORA** (req 7, never built), and it had been invisible twice over — first because
    the pronoun compiled to a bare OPEN, then because the gate could not have told the difference.
    *A red that names an unbuilt feature is worth more than a number that was measuring nothing;
    this is the second time in one day that an abstention turned out to be hiding a defect, after
    `look` and `die` (`db/0025`).*

    **TWO ENTRIES THAT WERE THE DRILL'S, NOT THE STATION'S** (`E1e.6.1`, 2026-09-26). When purpose
    became `imply(act, end)` with the end unclaimed (the Captain's 09-25 ruling), `t-ws-1` and `aw-6`
    went red on the instant: the drill hand-compiled «go to sleep» as the idiom and «to see the sea»
    as an intention with the arrow reversed. Tests follow decisions, so the drill was amended — the
    purpose part only — and the list came back to these four without a line of the station moving.

    **IT RUNS THE TOOL'S OWN PATH**, context and all. A control that compiled sentences differently
    from the instrument it guards would be free to agree while the instrument disagreed — which is
    the exact failure req 18 exists to prevent, one level down.
    """
    from tk2.language import standing_closed_classes
    from tk2.language.compile import Compiler
    from tk2.language.skeleton import StanzaSkeletons
    from tk2.language.utterance import compile_utterance
    from tools.drill_gate import DRILL_CONTEXT

    compiler = Compiler(standing_closed_classes())
    provider = StanzaSkeletons()

    disagreed = []
    for case in CASES:
        skeletons = provider(case.sentence)
        if not skeletons:
            continue
        produced = compile_utterance(compiler, skeletons, DRILL_CONTEXT)
        reading = compare(produced.zip, case.zip, case.id, case.sentence)
        if reading.verdict == DISAGREED:
            disagreed.append(case.id)

    assert sorted(disagreed) == ["aw-19", "q-6", "t-dc-5", "t-ws-7"], (
        f"the drill gate's disagreements moved: {sorted(disagreed)}")


@pytest.mark.skeleton
def test_every_compiled_drill_zip_is_a_TREE():
    """**THE SECOND RATCHET — A SENTENCE IS A TREE** (the compiler's own 09-20 rule, G2 2026-09-24).
    Over every zip the station compiles from the drill corpus, no row may be an operand of more than
    one join. A row with two parents is logic the evaluator can read and a SENTENCE nobody can: the
    decompiler takes the second parent as a second sentence («… Cognition is the result.»), and
    de-duplicating it there would only hide a zip that is not a tree.

    A prefix row is not a parent: it is the row's own scope chain, and several stacked on one row
    («not every cat…») is the format's normal shape (req 35).

    **The list went to ZERO on 2026-09-25, and it may only stay there.** Its one entry was `t-dc-5`,
    «Osaka is where you live and it is ALSO the name…» — the discourse adverb's join (`_connect`)
    named two rows the coordination had already joined. The Captain ruled it the same day: a
    coordination plus a CAUSAL discourse adverb is the adverb's join, which REPLACES the «and»
    («A and therefore B» claims A, B and A → B); an adverb repeating the coordination's operator
    («and also») adds nothing and builds nothing.
    """
    from collections import Counter

    from tk2.language import standing_closed_classes
    from tk2.language.compile import Compiler
    from tk2.language.skeleton import StanzaSkeletons
    from tk2.language.utterance import compile_utterance
    from tools.drill_gate import DRILL_CONTEXT

    compiler = Compiler(standing_closed_classes())
    provider = StanzaSkeletons()

    dags = {}
    for case in CASES:
        skeletons = provider(case.sentence)
        if not skeletons:
            continue
        produced = compile_utterance(compiler, skeletons, DRILL_CONTEXT).zip
        parents = Counter(operand for row in produced.rows if row.kind == "join"
                          for operand in row.operands)
        shared = sorted(name for name, count in parents.items() if count > 1)
        if shared:
            dags[case.id] = shared

    assert sorted(dags) == [], f"compiled zips that are not trees: {dags}"


# ------------------------------------------------------------------------------------------------
# E3.12.5.5 · E3.12.5.6 — the instruments read a withheld sentence and an annotation honestly
# ------------------------------------------------------------------------------------------------

def test_an_ANNOTATION_is_not_compiled_as_words_anybody_said():
    from tools.drill_gate import spoken

    assert spoken("All that glitters is not gold.  [¬∀ — not all of it is]") == \
        "All that glitters is not gold."
    assert spoken("The cat sleeps.") == "The cat sleeps."


def test_a_WHOLLY_withheld_zip_is_its_own_state_and_not_SILENT():
    """SILENT is a zip that held something and came back as nothing; a zip that claims nothing and
    says why is WITHHELD — `aw-13`'s amended shape is exactly one."""
    from tools.roundtrip import _wholly_withheld

    by_id = {c.id: c for c in CASES}
    assert _wholly_withheld(by_id["aw-13"].zip) and _wholly_withheld(by_id["aw-14"].zip)
    assert not _wholly_withheld(by_id["nha-4"].zip), "partial, and still claiming something"
