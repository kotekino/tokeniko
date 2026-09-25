"""The format, as a frozen shape: what it accepts, what it refuses, and why each refusal exists."""

import pytest
from pydantic import ValidationError

from tk2.tkzip.schema import (
    SCHEMA_VERSION, Box, ContentRow, Determination, DomainRow, JoinRow, Modality, ModalityRow,
    NegationRow, Open, Operator, Pov, QuantifierRow, Quantity, Ref, Role, Theatre, Var, Zip,
)


def _cat_sleeps() -> Zip:
    return Zip(rows=[ContentRow(name="c", predicate="sleep.v", truth=1.0,
                                boxes={Role.AGENT: Box(head="cat.n",
                                                       determination=Determination.DEFINITE)})])


# ------------------------------------------------------------------------------------------------
# the alphabets are closed, and their sizes are the ruling
# ------------------------------------------------------------------------------------------------


def test_eighteen_roles_and_the_reason_direction_is_one_of_them():
    """Seventeen at task 1; `direction` was the eighteenth, forced by the drill («He looked up»)."""
    assert len(list(Role)) == 18
    assert Role.DIRECTION in Role
    assert {Role.SOURCE, Role.PATH, Role.DESTINATION, Role.DIRECTION} <= set(Role)


def test_ten_operators_and_conv_is_not_imply_reversed():
    """Closed by mathematics, not by what English marks — and CONV survives because row order is
    already carrying scope and cannot also carry direction (req 42)."""
    assert len(list(Operator)) == 10
    assert Operator.CONV in Operator and Operator.NCONV in Operator


def test_quantity_and_determination_are_separate_alphabets():
    """OQ7: «the three cats» is definite AND counted; one seven-valued field could say only one."""
    box = Box(head="cat.n", quantity=None, count=3, determination=Determination.DEFINITE)
    assert box.count == 3 and box.determination is Determination.DEFINITE


# ------------------------------------------------------------------------------------------------
# binding — three states, and EMPTY costs nothing
# ------------------------------------------------------------------------------------------------


def test_empty_is_absence_and_is_not_stored():
    """~80% of every row is unused (measured). A marker for «nothing here» would be paid on every
    one of them."""
    stored = _cat_sleeps().model_dump(exclude_none=True, exclude_defaults=True)
    agent = stored["rows"][0]["boxes"]["agent"]
    assert set(agent) == {"head", "determination"}
    assert "patient" not in stored["rows"][0]["boxes"]


def test_the_three_states_are_three_different_things():
    """v1 wrote `*` for all three, and the evaluator needs them apart: it must not hunt for a patient
    `sleep` never had, and must not treat «someone» as a question."""
    assert Box().head is None                      # EMPTY
    assert isinstance(Box(head=Var(name="X")).head, Var)   # BOUND to a variable
    assert isinstance(Box(head=Open()).head, Open)          # OPEN
    assert Box(head=Open(prior=0.8)).head.prior == 0.8


def test_a_slot_may_be_open_while_its_neighbour_is_bound():
    """brain req 7 — the parser emits the lemma with the sense slot OPEN."""
    box = Box(head="cat.n", sense=Open())
    assert box.head == "cat.n" and isinstance(box.sense, Open)


# ------------------------------------------------------------------------------------------------
# the truth slot IS the assertion status
# ------------------------------------------------------------------------------------------------


def test_because_and_if_differ_only_in_whether_the_halves_are_claimed():
    """Same IMPLY. The join is claimed in both; «if» claims neither half (req 38)."""
    def zipped(half_truth):
        return Zip(rows=[ContentRow(name="r", predicate="rain.v", truth=half_truth),
                         ContentRow(name="s", predicate="stay.v", truth=half_truth),
                         JoinRow(name="j", operator=Operator.IMPLY, operands=["r", "s"], truth=1.0)])
    assert zipped(1.0) != zipped(None)


def test_a_polar_question_opens_the_truth_and_nothing_else():
    z = Zip(rows=[ContentRow(name="c", truth=Open(),
                             boxes={Role.EXPERIENCER: Box(head="cat.n"),
                                    Role.COMPLEMENT: Box(head="hungry.a")})])
    assert isinstance(z.rows[0].truth, Open)


def test_there_is_no_mood_field_anywhere():
    """Question, imperative, supposition and forecast are all consequences of other machinery."""
    fields = set(ContentRow.model_fields) | set(Zip.model_fields)
    assert not {"mood", "dubitative", "imperative", "ironic"} & fields


# ------------------------------------------------------------------------------------------------
# scope — the prefix, and the invariant that keeps row order meaningful
# ------------------------------------------------------------------------------------------------


def test_a_prefix_element_may_not_scope_another_prefix_element():
    """Otherwise ¬∀ has two spellings — chained pointers and sibling order — and two spellings of one
    reading is what this schema keeps refusing."""
    with pytest.raises(ValidationError, match="prefix element nests over a MATRIX"):
        Zip(rows=[NegationRow(name="neg", scopes="q"),
                  QuantifierRow(name="q", binds="X", quantity=Quantity.UNIVERSAL,
                                restriction=Box(head="cat.n"), scopes="c"),
                  ContentRow(name="c", predicate="glitter.v", truth=1.0)])


def test_scope_order_is_row_order_for_elements_over_one_matrix():
    """¬∀ and ∀¬ are the same two rows in the other order."""
    def glitters(negation_first):
        neg = NegationRow(name="neg", scopes="g")
        every = QuantifierRow(name="b", binds="X", quantity=Quantity.UNIVERSAL,
                              restriction=Box(head="glitterer.n"), scopes="g")
        rows = [neg, every] if negation_first else [every, neg]
        return Zip(rows=[*rows, ContentRow(name="g", truth=1.0,
                                           boxes={Role.PATIENT: Box(head=Var(name="X"))})])
    assert glitters(True) != glitters(False)


def test_two_modalities_over_two_conjuncts():
    """«software CAN be minds and humans MUST be minds» — the sentence that forced `scopes`."""
    z = Zip(rows=[ModalityRow(name="m1", modality=Modality.POSSIBILITY, scopes="a"),
                  ModalityRow(name="m2", modality=Modality.NECESSITY, scopes="b"),
                  ContentRow(name="a", truth=1.0), ContentRow(name="b", truth=1.0),
                  JoinRow(name="j", operator=Operator.AND, operands=["a", "b"], truth=1.0)])
    assert {r.modality for r in z.rows if isinstance(r, ModalityRow)} == set(Modality)


# ------------------------------------------------------------------------------------------------
# names and references resolve, or the zip does not exist
# ------------------------------------------------------------------------------------------------


def test_row_names_are_unique():
    with pytest.raises(ValidationError, match="unique"):
        Zip(rows=[ContentRow(name="c", truth=1.0), ContentRow(name="c", truth=1.0)])


def test_a_join_may_not_name_an_unknown_operand():
    with pytest.raises(ValidationError, match="unknown operand"):
        Zip(rows=[ContentRow(name="a", truth=1.0),
                  JoinRow(name="j", operator=Operator.AND, operands=["a", "ghost"], truth=1.0)])


def test_a_box_may_not_reference_an_unknown_row():
    """Without this, a dangling `Ref` reaches the evaluator as a row that is not there."""
    with pytest.raises(ValidationError, match="references unknown row"):
        Zip(rows=[ContentRow(name="c", truth=1.0,
                             boxes={Role.PATIENT: Box(head=Ref(row="ghost"))})])


def test_a_ref_is_not_a_key():
    """req 34 — a box may hold a ROW NAME, and it must not be mistaken for a dictionary key."""
    assert isinstance(Box(head=Ref(row="j2")).head, Ref)
    assert isinstance(Box(head="cat.n").head, str)


# ------------------------------------------------------------------------------------------------
# the caches are caches
# ------------------------------------------------------------------------------------------------


def test_the_geometry_cache_carries_one_epoch_for_the_whole_zip():
    """Every vector here was derived at the same time against the same base; a per-vector stamp would
    restate that on every entry, and a stamp whose halves can disagree is worse than none."""
    from tk2.tkzip.schema import GeometryCache

    assert "epoch" in GeometryCache.model_fields
    assert "epoch" not in Box.model_fields


def test_a_zip_carries_the_schema_version_it_was_compiled_against():
    assert _cat_sleeps().schema_version == SCHEMA_VERSION


def test_provenance_is_not_in_the_zip():
    """It describes the BELIEF and lives on the document (req 59)."""
    assert not {"parents", "derived_by", "original"} & set(Zip.model_fields)


def test_unplaced_material_is_not_a_slot():
    """It is a diagnostic: never compared, never given a position (req 21)."""
    z = Zip(rows=[ContentRow(name="c", predicate="die.v", truth=0.0)], unplaced=["almost"])
    assert z.unplaced == ["almost"]
    assert "other" not in {r.value for r in Role}


def test_parse_confidence_may_be_empty():
    """Self-talk invokes no parser; 1.0 would claim perfect understanding of an utterance that never
    happened (req 58)."""
    assert _cat_sleeps().parse_confidence is None


def test_a_NUMBER_is_sg_or_pl_or_either_and_the_format_refuses_the_rest():
    """**ONE COLUMN MUST NOT CARRY TWO FACTS, AND THE FORMAT IS WHERE THAT IS ENFORCED.**

    `both` · `neither` · `either` · `each other` carried `number: dual` in the closed-class rows,
    meaning *this word is about exactly TWO* — a fact about the SET, not the grammatical number of
    anything. `Compiler._unknown()` copies a row's `number` into the OPEN a described unknown
    carries (schema v4), so «I saw both» and «They praised each other» compiled to
    `Open(number='dual')`: a value the field's own docstring did not admit, sitting in a zip, with
    nothing able to say it back. Both decompiled to the empty string.

    `db/0030` moved the cardinality onto `count`, which is the column the table already uses for HOW
    MANY. This is the other half: **the next such value raises where it is WRITTEN** instead of
    travelling to where it cannot be read.

    *`either` is admitted and is a real answer — English's «you» does not distinguish, and a zip
    recording «the speaker used a word that does not tell us» is saying something different from a
    zip that says nothing at all.*
    """
    for good in ("sg", "pl", "either"):
        assert Open(number=good).number == good
        assert Box(head="cat.n", number=good).number == good

    for bad in ("dual", "plural", "SG", "2"):
        with pytest.raises(ValidationError):
            Open(number=bad)
        with pytest.raises(ValidationError):
            Box(head="cat.n", number=bad)


def test_no_closed_class_row_carries_a_number_the_format_refuses():
    """The guard above only helps if nothing is trying to write one. `_unknown()` copies `number`
    off a row without looking, so a row and the schema disagreeing is a compile that cannot produce
    a valid zip — which is exactly what «I saw both» was."""
    from typing import get_args

    from tk2.language import standing_closed_classes
    from tk2.tkzip.schema import Number

    legal = (None, *get_args(Number))
    rows = standing_closed_classes()._rows                       # noqa: SLF001
    illegal = [(row["form"], (row.get("features") or {}).get("number")) for row in rows
               if (row.get("features") or {}).get("number") not in legal]

    assert not illegal, f"{illegal} would be written into an `Open` the schema refuses"


# ------------------------------------------------------------------------------------------------
# v9 — an understood marker is stored, and so is the fact that nobody said it (G7, 2026-09-25)
# ------------------------------------------------------------------------------------------------


def test_v9_an_UNDERSTOOD_marker_is_the_marker_plus_one_flag_on_the_box():
    """«I gave ANNA a book» means «to Anna» — the marker is stored — and was said bare, which is
    surface the decompiler needs. One optional field, on the box the marker already lives on."""
    assert SCHEMA_VERSION == 9
    understood = Box(head="anna.n", marker="to", marker_implicit=True)
    said = Box(head="anna.n", marker="to")

    assert understood.marker == said.marker, "one meaning"
    assert understood != said, "two surfaces, and the zip keeps them apart"
    assert "marker_implicit" in Box.model_fields
    assert not {"marker_implicit"} & (set(Pov.model_fields) | set(ContentRow.model_fields))


def test_v9_a_WRITTEN_marker_costs_no_stored_field():
    stored = Box(head="anna.n", marker="to").model_dump(exclude_none=True, exclude_defaults=True)
    assert set(stored) == {"head", "marker"}
