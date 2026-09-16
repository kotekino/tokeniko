"""THE UD GATE — the station scored against Universal Dependencies' own examples.

The drill is the FORMAT's gate: 78 hand-compiled sentences proving tkzip can hold the world, with no
parser involved. This is the STATION's: can it read a skeleton correctly. Both ends are closed — 37
relations in, 18 roles and 10 operators out — so the mapping can be complete rather than merely
large, and what is missing can be NAMED.
"""

import pytest

from tests.fixtures.ud import CASES, OPEN, RELATION_FILLS_ROLE, covered
from tk2.language import standing_closed_classes
from tk2.language.compile import Compiler
from tk2.language.skeleton import UD_DEPS, UD_POS
from tools.ud_gate import ABSTAINED, ANSWERED, WRONG, read


@pytest.fixture(scope="module")
def table():
    return standing_closed_classes()


@pytest.fixture(scope="module")
def compiler(table):
    return Compiler(table)


@pytest.fixture(scope="module")
def scored(table, compiler):
    """**The gate scores the ZIP, not the table** — since 2026-09-16. It used to ask the closed-class
    table what a token was, which was half a station and could never reach the relations that are
    compiler questions. Now the sentence is compiled and the marked token is looked up in
    `Compiled.placement`, the compiler's own record of where each word went."""
    return [(case, *read(case, table, compiler)) for case in CASES]


def test_the_station_is_never_WRONG_on_ud_s_own_examples(scored):
    """THE ONLY FAILURE THAT COUNTS. «Half understood is legal, wrongly understood is the sin»
    (req 8): an abstention is a diagnosis, a wrong answer is a defect."""
    wrong = [(c.relation, c.text, produced, why) for c, verdict, produced, why in scored
             if verdict == WRONG]

    assert wrong == [], f"{len(wrong)} wrong: {wrong}"


def test_the_gate_answers_what_it_can_and_the_number_is_held(scored):
    """A floor, not a ceiling. It may only go up — and if a change lowers it, that is the change
    saying something about itself."""
    answered = sum(1 for _, verdict, _, _ in scored if verdict == ANSWERED)

    assert answered >= 33, f"the gate answered {answered} of {len(CASES)}; 33 on 2026-09-16"


def test_every_abstention_says_WHY(scored):
    """An abstention with no reason is indistinguishable from a bug that returned nothing."""
    silent = [c.text for c, verdict, _, why in scored if verdict == ABSTAINED and not why]

    assert silent == [], f"abstained without saying why: {silent}"


def test_a_ud_subtype_settles_an_ambiguous_marker(table):
    """«the cat was chased BY the dog». `by` is instrument/agent/path/time in the table, and UD's
    own `obl:agent` — "used for agents in passive constructions" — settles it outright. One of the
    thirteen, solved by the standard rather than by us.

    And the settling label is on the HEAD, not on the marker: UD puts `case` on `by` and the
    informative relation on the nominal it attaches to."""
    settled = table.read(["by", "the", "dog"], 0, "ADP", "case", head_dep="obl:agent")
    unsettled = table.read(["by", "the", "river"], 0, "ADP", "case", head_dep="obl")

    assert settled.settled_role == "agent"
    assert settled.role_or_settled == "agent"
    assert unsettled.settled_role is None
    assert unsettled.role_or_settled == "instrument", "the table's own best-first, unaided"


def test_a_subtype_cannot_invent_a_role_the_marker_cannot_fill(table):
    """A guard on the mechanism: `obl:tmod` says «time», but if the marked form has no time reading
    the answer is a disagreement to report, never a role to invent."""
    odd = table.read(["with", "Anna"], 0, "ADP", "case", head_dep="obl:tmod")

    assert odd.settled_role is None, "`with` has no time reading and must not be given one"
    assert odd.roles == ("instrument", "comitative")


def test_the_corpus_reaches_a_real_share_of_ud_and_names_what_it_misses():
    """A gate that scored 100% on the relations someone happened to transcribe would be measuring
    its own corpus. What it does NOT reach is part of the report, every run."""
    missing = set(UD_DEPS) - covered()

    assert len(covered()) >= 16, f"only {len(covered())} of 37 relations are reached"
    assert missing, "when this is empty the gate is complete — and the assertion should be deleted"
    assert "case" in covered() and "obl" in covered(), "the marker relations at least"


def test_the_two_halves_of_the_mapping_do_not_overlap(table):
    """37 → 18 has two halves that must not collide: a role that comes from a RELATION (agent,
    patient, recipient) is never also marked by a preposition, and the table proves it by holding no
    marker for them."""
    marked = {role for row in table._rows if row["compiled"].get("kind") == "box"
              for role in row["compiled"]["roles"]}

    assert "patient" not in marked
    assert RELATION_FILLS_ROLE["obj"] == "patient"
    assert RELATION_FILLS_ROLE["nsubj:pass"] == "patient", "the passive subject IS the patient"


def test_the_transcription_carries_ud_s_own_annotation_where_there_was_one():
    """«An origin that cannot be read is not documentation» — the rule that produced CLAUDE.md. A
    case marked `annotated` was transcribed WITH the published parse; the rest say so."""
    annotated = [c for c in CASES if c.annotated]

    assert len(annotated) >= 12
    assert all(c.rows and c.note is not None for c in annotated)


def test_every_case_names_a_relation_and_a_pos_ud_actually_defines():
    """The corpus itself must speak UD, or the gate is measuring a private vocabulary."""
    for case in CASES:
        skeleton = case.skeleton
        assert skeleton.non_ud() == (), f"{case.text!r} carries non-UD labels: {skeleton.non_ud()}"
        assert case.relation.split(":")[0] in UD_DEPS
    assert len(UD_POS) == 17 and len(UD_DEPS) == 37
