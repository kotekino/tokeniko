"""The closed classes learn what they compile to — `db/0008`, version 2.

The column was empty by construction until tkzip froze. What this file holds is that it is now full
AND that everything in it is a value the frozen format actually has: a `compiled` map naming a role,
an operator, a quantity or a modality that `tk2.tkzip.schema` does not define would be knowledge
about a format nobody implements.
"""

from collections import Counter

import pytest

from tk2.migrations import discover
from tk2.tkzip.schema import Determination, Modality, Operator, Quantity, Role


def migration(number: int):
    found = next((m for m in discover() if m.number == number), None)
    if found is None:
        pytest.skip(f"migration {number} is not present")
    return found.load()


@pytest.fixture(scope="module")
def rows():
    return migration(8).ROWS


@pytest.fixture(scope="module")
def v1():
    return migration(1).CLOSED_CLASS_ROWS


# ------------------------------------------------------------------------------------------------
# the column is full, and full of values the format has
# ------------------------------------------------------------------------------------------------


def test_every_row_compiles_to_something(rows):
    """«Empty» was the v1 state and the whole point of v2. A row with nothing in `compiled` is a
    form the station would meet and have no instruction for."""
    empty = [r["form"] for r in rows if not r["compiled"]]

    assert empty == [], f"{len(empty)} rows still compile to nothing: {empty[:12]}"
    assert len(rows) == 383, "v2 carries every v1 row forward, no more and no fewer"


def test_no_compiled_map_hides_a_None(rows):
    """A key present with a `None` value is worse than an absent key: it reads as «answered» to
    anything that checks for the key. The three articles and three clitics were exactly this."""
    optional = {"binds", "aspect", "tense"}
    holes = [(r["form"], r["compiled"]) for r in rows
             if any(v is None for k, v in r["compiled"].items() if k not in optional)]

    assert holes == [], f"{len(holes)} compiled maps carry a None: {holes[:6]}"


@pytest.mark.parametrize("key, enum", [
    ("operator", Operator), ("quantity", Quantity),
    ("modality", Modality), ("determination", Determination),
])
def test_named_values_exist_in_the_frozen_schema(rows, key, enum):
    allowed = {member.value for member in enum}
    wrong = [(r["form"], r["compiled"][key]) for r in rows
             if r["compiled"].get(key) is not None and r["compiled"][key] not in allowed]

    assert wrong == [], f"{key} values the format does not define: {wrong}"


def test_every_marked_role_is_one_of_the_eighteen(rows):
    allowed = {member.value for member in Role}
    wrong = [(r["form"], r["compiled"]["roles"]) for r in rows
             if r["compiled"].get("kind") == "box" and set(r["compiled"]["roles"]) - allowed]

    assert wrong == [], f"boxes naming a role tkzip has not got: {wrong}"


# ------------------------------------------------------------------------------------------------
# the re-typings — each one a defect v1 could not have avoided, and each one named
# ------------------------------------------------------------------------------------------------


def test_the_causal_markers_became_a_JOIN_not_a_box(rows):
    """E2's collapse, arriving where it was predicted: there is no CAUSE relation, because a cause
    is what implies its effect. «because of» marks no box — it joins two rows."""
    because = next(r for r in rows if r["form"] == "because of")

    assert because["role"] == "causal_marker"
    assert because["compiled"]["kind"] == "join"
    assert because["compiled"]["operator"] == Operator.IMPLY.value
    assert because["compiled"]["antecedent"] == "marked"
    assert because["compiled"]["was"] == "role_marker", "the row says what it used to be"


def test_the_concessive_loss_is_RECORDED_rather_than_hidden(rows):
    """«Despite the rain I went out» is truth-functionally «rain AND went out» — the defeated
    expectation is not truth-functional and `JoinRow` has no marker field to carry it. Compiling to
    AND is a LOSS, and the row must say so or the figurative layer will never find its own cases."""
    despite = next(r for r in rows if r["form"] == "despite")

    assert despite["compiled"]["operator"] == Operator.AND.value
    assert despite["compiled"]["pragmatic"] == "concessive"
    assert despite["compiled"]["lossy"] is True


def test_the_articles_are_DETERMINATION_and_not_quantity(rows):
    """v1's own features said «force: definite / indefinite» and the row was still typed
    quantificational. tkzip keeps determination as its own field beside quantity — «the cat» and
    «a cat» differ in determination and are both singular."""
    the, a = (next(r for r in rows if r["form"] == f) for f in ("the", "a"))

    assert the["role"] == a["role"] == "determination"
    assert the["compiled"]["determination"] == Determination.DEFINITE.value
    assert a["compiled"]["determination"] == Determination.INDEFINITE.value
    assert all(r["form"] not in ("a", "an", "the")
               for r in rows if r["compiled"].get("kind") == "quantifier")


def test_the_future_is_a_THEATRE_and_never_a_modality(rows):
    """tkzip's Modality is necessity / possibility, frozen — E2 ruled a forecast is a future
    THEATRE. v1 typed `will` and `'ll` as modality with «modality: future», which is a modal
    operator the format does not have."""
    will, ll = (next(r for r in rows if r["form"] == f) for f in ("will", "'ll"))

    assert will["compiled"]["kind"] == "theatre" and will["role"] == "tense_aspect"
    assert ll["compiled"]["kind"] == "theatre"
    assert all(r["compiled"].get("modality") in (m.value for m in Modality)
               for r in rows if r["compiled"].get("kind") == "prefix"
               and r["compiled"].get("element") == "modality")


def test_a_form_v1_called_ambiguous_keeps_BOTH_readings(rows):
    """v1's own note on `'d`: «contracted would or had — genuinely ambiguous». A row that picked one
    would be a lie the compiler could not detect."""
    d = next(r for r in rows if r["form"] == "'d")

    assert d["compiled"]["kind"] == "ambiguous"
    kinds = {c["kind"] for c in d["compiled"]["candidates"]}
    assert kinds == {"prefix", "theatre"}


# ------------------------------------------------------------------------------------------------
# the ambiguous markers, which are the reason `roles` is a list
# ------------------------------------------------------------------------------------------------


def test_an_ambiguous_marker_keeps_every_candidate_best_first(rows):
    by = next(r for r in rows if r["form"] == "by" and r["role"] == "role_marker")
    to = next(r for r in rows if r["form"] == "to" and r["role"] == "role_marker")

    assert by["compiled"]["roles"] == ["instrument", "agent", "path", "time"]
    assert to["compiled"]["roles"] == ["destination", "recipient"]


def test_patient_and_experiencer_are_marked_by_NOTHING(rows):
    """The sanity check that says the mapping is sane rather than merely complete: those two are
    core arguments, marked by POSITION. UD marks them nsubj/obj/iobj and never `case`. A preposition
    claiming to mark a patient would mean the mapping had been filled in by vibes."""
    marked = {role for r in rows if r["compiled"].get("kind") == "box"
              for role in r["compiled"]["roles"]}

    assert "patient" not in marked and "experiencer" not in marked
    assert len(marked) == 16, "the other sixteen all have at least one marker"


def test_without_negates_the_box_it_fills(rows):
    """«without a knife» is the instrument NEGATED — it fills a box and raises the negation prefix,
    which no other marker does."""
    without = next(r for r in rows if r["form"] == "without")

    assert without["compiled"]["roles"] == ["instrument", "comitative"]
    assert without["compiled"]["negates"] is True


# ------------------------------------------------------------------------------------------------
# version 2 is version 1 plus a decision — never minus a row
# ------------------------------------------------------------------------------------------------


def test_v2_carries_every_v1_form_and_invents_none(rows, v1):
    before = Counter((r["form"], r["word_class"]) for r in v1 if r.get("version") == 1)
    after = Counter((r["form"], r["word_class"]) for r in rows)

    assert after == before, "a form was added or lost between versions"


def test_v2_changes_only_compiled_role_and_note(rows, v1):
    """The forms, features and sources are v1's and must not drift: this migration is the author of
    the MAPPING and of nothing else."""
    old = {(r["form"], r["word_class"], r["position"]): r for r in v1 if r.get("version") == 1}
    for row in rows:
        was = old[(row["form"], row["word_class"], row["position"])]
        assert row["features"] == was["features"]
        assert row["source"] == was["source"]
        assert row["version"] == 2

    moved = [r["form"] for r in rows
             if r["role"] != old[(r["form"], r["word_class"], r["position"])]["role"]]
    assert len(moved) == 41, f"41 rows were re-typed, not {len(moved)}"
