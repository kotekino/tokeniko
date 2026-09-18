"""THE DRILL GATE — requirement 18's control, and the tests that prove it can FAIL.

The gate itself needs stanza, so almost everything here is written against the pure comparison with
hand-made zips on both sides. **That is not a convenience.** A gate nobody has seen fail is a gate
nobody can trust, and the whole reason this one exists is that the drill and the UD gate had never
been able to disagree with each other for a day while a wrong role sat in every copular sentence.

The one test that actually parses carries `@pytest.mark.skeleton`, like the rest of the few that do.
"""

import pytest

from tests.fixtures.drill import CASES
from tk2.tkzip.schema import Box, ContentRow, Open, Operator, Role, Var, Zip
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


def test_the_station_and_the_drill_disagree_only_where_a_question_is_NAMED():
    """**THE RATCHET.** Twelve disagreements on 2026-09-18, in three families — and the point of the
    list is that every entry is named, dated and attributable. The count may only go DOWN.

      ten    the SUBJECT'S ROLE depends on what is predicated of it — `exist-3` `t-ws-1` `t-ws-8`
             `t-dc-4` `t-of-1` `t-mo-1` `aw-11` `aw-16` `aw-20` `q-2`. E3's standing open question,
             which `RELATION_FILLS_ROLE`'s own comment defers to the geometry. It had three
             witnesses until this gate was given a context; it has ten.
      one    the station builds no `DomainRow` yet — `aw-15`, where «In Italy» lands in `location`
             and displaces the France that belongs there. E3 unfinished, showing as a conflict
             rather than as a missing row because the wrong filler reached a real box.
      one    the named-individual hole — `aw-19`, «I ate with Anna» (E3b).

    **THE POLAR QUESTION AND THE IMPERATIVE ARE GONE** (tasks 2c, 2d — 2026-09-18). The gate began
    comparing TRUTH that morning and flagged `t-mo-1` «Do you exist?» (asked, compiled as a claim)
    and `aw-21` «Close the door!» (wanted, compiled as a claim). Both fixed the same day; `aw-21`
    now agrees outright, its understood subject included.

    **THE ROTATION FAMILY IS GONE.** `q-4` `q-7` `q-9` disagreed for one morning — the station
    rotated reported speech and did not rotate quoted speech, having keyed the rotation on the word
    «that». Fixed the same day on the Captain's ruling, by asking stanza what it had already parsed
    instead of asking what a quotation mark is. `q-2` stays, but its rotation is right: what is left
    of it is the subject-role question above.

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

    assert sorted(disagreed) == ["aw-11", "aw-15", "aw-16", "aw-19", "aw-20", "exist-3",
                                 "q-2", "t-dc-4", "t-mo-1", "t-of-1", "t-ws-1", "t-ws-8"], (
        f"the drill gate's disagreements moved: {sorted(disagreed)}")
