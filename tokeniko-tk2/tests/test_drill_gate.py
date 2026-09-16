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
def test_the_station_and_the_drill_disagree_only_where_a_question_is_OPEN():
    """**THE RATCHET.** Four disagreements on 2026-09-16, and every one of them is a question the
    project has open and named rather than a defect:

      `exist-3` · `aw-11` · `aw-20`  — the subject's role depends on WHAT IS PREDICATED of it, which
                                       `RELATION_FILLS_ROLE`'s own comment defers to the geometry
      `aw-19`                        — «I ate with Anna», the named-individual hole (E3b)

    A fifth would be a new defect. The count may only go DOWN.
    """
    from tk2.language import standing_closed_classes
    from tk2.language.compile import Compiler
    from tk2.language.skeleton import StanzaSkeletons

    compiler = Compiler(standing_closed_classes())
    provider = StanzaSkeletons()

    disagreed = []
    for case in CASES:
        skeletons = provider(case.sentence)
        if not skeletons:
            continue
        reading = compare(compiler.compile(skeletons[0]).zip, case.zip, case.id, case.sentence)
        if reading.verdict == DISAGREED:
            disagreed.append(case.id)

    assert sorted(disagreed) == ["aw-11", "aw-19", "aw-20", "exist-3"], (
        f"the drill gate's disagreements moved: {sorted(disagreed)}")
