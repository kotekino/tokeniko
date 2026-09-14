"""CURATED EDGES AS INPUTS — the E1d T4 repair, and the eight cases it was benched against.

Two edges the Captain approved on 2026-08-12 were found missing from the built base by the E1 audit:
`mined` 51,564 cells, `axis` 4,555, **`curated` 0**. No check would have saved them. A curated edge
was an OUTPUT of a build — a cell in a matrix that gets regenerated — and never an INPUT to one.

**Outputs get regenerated. Inputs survive.** That is what these tests hold.
"""

import pytest

from tk2.dictionary.config import RelationPolicy
from tk2.dictionary.curation import CurationRefused, merge_curated
from tk2.dictionary.matrix import SOURCE_CURATED, SOURCE_MINED, Cell, Matrix, MatrixRow, Provenance

KEYS = ("bed.n", "sleep.v", "furniture.n", "cause.n")

POLICY = RelationPolicy(
    weights=(("identity", 1.0), ("hypernym_1", 0.7)),
    curated=(("used_for", 0.7), ("state_of", 0.7)),
    reciprocal_weight=0.60,
)


def edge(source="bed.n", target="sleep.v", relation="used_for", **over):
    row = {
        "source_key": source, "target_key": target, "relation": relation, "weight": 0.7,
        "sense": "bed.n.01",
        "evidence": "bed.n.01 a piece of furniture that provides a place to *sleep*",
        "relabelled": False, "approved_by": "the Captain", "approved_at": 1_755_000_000,
        "withdrawn_at": None,
    }
    return row | over


def matrix(*rows):
    return Matrix(name="r", keys=KEYS,
                  rows=tuple(MatrixRow(key=k, index=i, cells=c)
                             for i, (k, c) in enumerate(rows)))


def empty():
    return matrix(*((k, ()) for k in KEYS))


# ------------------------------------------------------------------------------------------------
# 1 — the edges survive a rebuild, because they are inputs
# ------------------------------------------------------------------------------------------------


def test_an_approved_edge_is_written_into_a_freshly_built_matrix():
    """The whole repair in one assertion: R comes out of the WordNet walk with nothing curated in
    it, and the approved edges are merged in from rows that the walk cannot touch."""
    merged, report = merge_curated(empty(), [edge()], POLICY)

    forward = merged.rows[0].cell("sleep.v")
    assert forward.weight == 0.7
    assert forward.relation == "used_for"
    assert forward.source == SOURCE_CURATED
    assert report.edges == 1 and report.cells == 2 and report.is_clean


def test_the_reciprocal_travels_with_it():
    """Requirement 20's convention — and it is what carries `sleep.v ~ bed.n`, where only *bed*'s
    gloss speaks."""
    merged, _ = merge_curated(empty(), [edge()], POLICY)

    back = merged.rows[1].cell("bed.n")
    assert back.weight == 0.60
    assert back.relation == "used_for_reciprocal"
    assert back.source == SOURCE_CURATED


# ------------------------------------------------------------------------------------------------
# 2 — a rebuild changes MEMBERSHIP, and an edge can outlive its dimension
# ------------------------------------------------------------------------------------------------


def test_an_edge_naming_a_dimension_this_base_does_not_have_is_REPORTED():
    """THE CASE THAT WILL ACTUALLY BITE. A rebuild moves the closure's cut, so an approved edge can
    name a key the new base does not carry. Dropping it quietly is exactly the class of silence this
    whole epic came from."""
    merged, report = merge_curated(empty(), [edge(target="peckish.a")], POLICY)

    assert report.edges == 0
    assert not report.is_clean
    assert report.unresolvable == (("bed.n", "peckish.a", "not a dimension of this base: peckish.a"),)
    assert merged.rows[0].cells == (), "and nothing was written"


def test_a_resolvable_edge_still_lands_when_another_one_cannot():
    """One bad row must not take the good ones with it — the report says which, and the build says
    so out loud."""
    _merged, report = merge_curated(empty(), [edge(), edge(source="gone.n")], POLICY)

    assert report.edges == 1
    assert len(report.unresolvable) == 1


# ------------------------------------------------------------------------------------------------
# 3 — the authorization travels, verbatim
# ------------------------------------------------------------------------------------------------


def test_the_evidence_reaches_the_cell_verbatim():
    """Requirement 20: a paraphrase is the curator arguing rather than the dictionary speaking, and
    the evidence is what a later reader argues WITH when an edge looks wrong."""
    merged, _ = merge_curated(empty(), [edge()], POLICY)

    assert "*sleep*" in merged.rows[0].cell("sleep.v").evidence


def test_a_relation_outside_the_curated_vocabulary_is_refused():
    """The vocabulary is closed on purpose — a curator who may invent a relation per edge is writing
    prose, not a matrix."""
    with pytest.raises(CurationRefused, match="curated relations"):
        merge_curated(empty(), [edge(relation="is_sort_of_about")], POLICY)


# ------------------------------------------------------------------------------------------------
# 6 — a curated cell overrides a mined one, and says so
# ------------------------------------------------------------------------------------------------


def test_a_curated_cell_overrides_a_mined_one_and_the_override_is_reported():
    """A curated edge is the only cell carrying a human authorization and verbatim evidence, and an
    approval that lost to the walk it was written to correct would be theatre. But «the resource
    stated otherwise and a person disagreed» is a DISCOVERY and is reported every time."""
    mined = Cell(column="sleep.v", weight=0.7, relation="hypernym_1", source=SOURCE_MINED,
                 via=(Provenance("hypernym_1", 0.7),))
    before = matrix(("bed.n", (mined,)), ("sleep.v", ()), ("furniture.n", ()), ("cause.n", ()))

    merged, report = merge_curated(before, [edge()], POLICY)

    assert merged.rows[0].cell("sleep.v").source == SOURCE_CURATED
    assert report.overrode_mined == (("bed.n", "sleep.v", "hypernym_1"),)


def test_a_mined_cell_about_another_column_is_left_alone():
    mined = Cell(column="furniture.n", weight=0.7, relation="hypernym_1", source=SOURCE_MINED)
    before = matrix(("bed.n", (mined,)), ("sleep.v", ()), ("furniture.n", ()), ("cause.n", ()))

    merged, report = merge_curated(before, [edge()], POLICY)

    assert merged.rows[0].cell("furniture.n").source == SOURCE_MINED
    assert report.overrode_mined == ()


# ------------------------------------------------------------------------------------------------
# 8 — retreat, not delete
# ------------------------------------------------------------------------------------------------


def test_a_withdrawn_edge_is_skipped_and_COUNTED():
    """`withdrawn_at` is the «mostly» in append-mostly: a withdrawal is a fact with a date, never an
    absence. A collection that can lose a row silently is one whose history means nothing — and this
    collection exists precisely because something was lost silently once."""
    merged, report = merge_curated(empty(), [edge(withdrawn_at=1_756_000_000)], POLICY)

    assert report.withdrawn == 1 and report.edges == 0
    assert merged.rows[0].cells == ()


# ------------------------------------------------------------------------------------------------
# 4 / 5 — the manifest can finally answer «was this build curated?»
# ------------------------------------------------------------------------------------------------


def test_the_build_counts_say_what_curation_the_build_carried():
    """The manifest recorded r_cells, r_negative, r_silent_rows and d_cells and said NOTHING about
    curation — so a build that had silently lost two approved edges looked exactly like one that
    never had any."""
    from tk2.dictionary.build import BaseBuild

    _merged, report = merge_curated(empty(), [edge(), edge(target="gone.n")], POLICY)
    counts = BaseBuild(words=(), dimensions=KEYS, relational=empty(), curated=report).counts()

    assert counts["curated_edges"] == 1
    assert counts["curated_cells"] == 2
    assert counts["curated_unresolvable"] == 1
    assert counts["curated_withdrawn"] == 0


def test_a_build_offered_no_edges_is_a_different_fact_from_one_that_applied_none():
    """`None` versus zero. Two approved edges were lost once because nothing could tell those apart."""
    from tk2.dictionary.build import BaseBuild

    never_offered = BaseBuild(words=(), dimensions=KEYS, relational=empty()).counts()
    assert "curated_edges" not in never_offered

    _m, none_applied = merge_curated(empty(), [], POLICY)
    offered = BaseBuild(words=(), dimensions=KEYS, relational=empty(), curated=none_applied).counts()
    assert offered["curated_edges"] == 0


def test_the_merge_does_not_mutate_what_it_was_handed():
    before = empty()

    merge_curated(before, [edge()], POLICY)

    assert before.rows[0].cells == ()
