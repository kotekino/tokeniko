"""GLOSS REFERENCES — «A's definition NAMES B», and the two rules that keep it honest.

Requirement 2 was refuted at scale by the E1 audit: `eat.v~food.n` reads a D cosine of +0.0484 and a
D DIRECT CELL of 0.0000, because their definitions share no words. D measures what two definitions
SHARE; the relation is that eat's definition NAMES food, which is R's kind of claim.
"""

import pytest

from tk2.dictionary.config import READING_SEPARATE, ReadingPolicy
from tk2.dictionary.matrix import SOURCE_MINED, Cell, Matrix, MatrixRow
from tk2.dictionary.references import (
    GLOSS_REFERENCE,
    GLOSS_REFERENCE_AMBIGUOUS,
    GLOSS_REFERENCE_RECIPROCAL,
    dimensions_by_word,
    merged_into,
    reference_cells,
)

# `sleep` is TWO dimensions and `food` is one — which is the whole distinction under test.
DIMENSIONS = ("eat.v", "food.n", "sleep.n", "sleep.v", "bed.n", "express.n", "express.v", "state.v")


def cells(weight=0.9, reciprocal=0.54, **vectors):
    return reference_cells({k: frozenset(v) for k, v in vectors.items()},
                           DIMENSIONS, weight=weight, reciprocal_weight=reciprocal)


def test_an_unambiguous_reference_is_a_deciding_claim():
    """«take in solid FOOD» — `food` occupies exactly one dimension, so the claim names a dimension
    rather than guessing among several."""
    rows = cells(**{"eat.v": {"food"}})

    forward = rows["eat.v"][0]
    assert forward.column == "food.n"
    assert forward.relation == GLOSS_REFERENCE
    assert forward.weight == 0.9


def test_the_reciprocal_is_written_at_the_lower_weight():
    """Requirement 20's `entailed_by` convention, so a MINED reference is shaped like the curated
    edges it sits beside — and it is what carries a pair where only one gloss speaks."""
    rows = cells(**{"eat.v": {"food"}})

    back = rows["food.n"][0]
    assert back.column == "eat.v"
    assert back.relation == GLOSS_REFERENCE_RECIPROCAL
    assert back.weight == 0.54


def test_an_ambiguous_reference_is_RECORDED_and_may_not_decide():
    """`lexicon_words_in` keeps no tagger on purpose, so «express in words» names express.n/v/a/r
    and one is meant. 69% of real references are ambiguous that way — harmless for D, where overlap
    is symmetric, and not harmless for a cell that DECIDES."""
    rows = cells(**{"state.v": {"express"}})

    minted = {c.column: c for c in rows["state.v"]}
    assert set(minted) == {"express.n", "express.v"}
    assert all(c.relation == GLOSS_REFERENCE_AMBIGUOUS for c in minted.values())
    assert "express.n" not in rows, "an ambiguous reference writes no reciprocal"


def test_an_ambiguous_reference_carries_its_HONEST_SHARE():
    """A claim spread over two readings is half a claim. A number saying otherwise would hide the
    ambiguity inside an accurate-looking cell."""
    rows = cells(**{"state.v": {"express"}})

    assert all(c.weight == pytest.approx(0.45) for c in rows["state.v"])


def test_the_pair_the_chapter_singled_out_is_recorded_rather_than_decided():
    """`sleep.v ~ bed.n` — «a piece of furniture that provides a place to SLEEP» — is the pair the
    2026-08-12 review called the one only R gets right, and the Captain curated it by hand. «sleep»
    is two dimensions, so the mine states the claim and refuses to decide it. That is what E1d T5's
    curation is for."""
    rows = cells(**{"bed.n": {"sleep"}})

    assert {c.column for c in rows["bed.n"]} == {"sleep.n", "sleep.v"}
    assert all(c.relation == GLOSS_REFERENCE_AMBIGUOUS for c in rows["bed.n"])

    reading = ReadingPolicy(mix=0.15, near_floor=0.28, far_ceiling=0.0, mode=READING_SEPARATE,
                            cell_decides=True,
                            structural_relations=("derivational", GLOSS_REFERENCE_AMBIGUOUS))
    assert not reading.decides_by_cell(GLOSS_REFERENCE_AMBIGUOUS)


def test_a_self_reference_is_never_mined():
    """«land: the land on which real estate is located» states nothing about two concepts, and
    mining it is how a POS-split base gets re-merged by a tautology."""
    assert cells(**{"eat.v": {"eat"}}) == {}


def test_a_mutual_reference_is_one_claim_from_both_sides():
    """Two glosses naming each other must not produce a forward cell AND a reciprocal over it."""
    rows = cells(**{"eat.v": {"food"}, "food.n": {"eat"}})

    assert [c.relation for c in rows["eat.v"]] == [GLOSS_REFERENCE]
    assert [c.relation for c in rows["food.n"]] == [GLOSS_REFERENCE]


def test_dimensions_by_word_is_what_decides_ambiguity():
    by_word = dimensions_by_word(DIMENSIONS)

    assert by_word["food"] == ["food.n"]
    assert sorted(by_word["sleep"]) == ["sleep.n", "sleep.v"]


def test_a_mined_relation_always_wins_over_a_reference():
    """`eat entails swallow` says what eating IS; «take in solid food» says what the dictionary
    happened to write. A cell that could not say which claim set it is a cell whose provenance lies."""
    stated = Cell(column="food.n", weight=0.8, relation="hypernym_1", source=SOURCE_MINED)
    matrix = Matrix(name="r", keys=DIMENSIONS,
                    rows=(MatrixRow(key="eat.v", index=0, cells=(stated,)),))

    merged = merged_into(matrix, cells(**{"eat.v": {"food"}}))

    kept = merged.rows[0].cell("food.n")
    assert kept.relation == "hypernym_1" and kept.weight == 0.8
    assert len(merged.rows[0].cells) == 1


def test_merging_does_not_mutate_what_it_was_handed():
    matrix = Matrix(name="r", keys=DIMENSIONS,
                    rows=(MatrixRow(key="eat.v", index=0, cells=()),))

    merged = merged_into(matrix, cells(**{"eat.v": {"food"}}))

    assert matrix.rows[0].cells == ()
    assert len(merged.rows[0].cells) == 1
