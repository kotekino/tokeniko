"""DEFINITIONAL CURATION on the handcrafted world — the miner, the two cells, and the gate.

Requirement 20 is a ruling about WHO may add an edge, so the test that matters most in this file is
the one that proves the instrument cannot: `assert_captains_hand` is code precisely so it can be
asserted on, and a gate nobody tests is a comment with a function's clothes.

The sixteen-word world does the mining half. `bed` is defined as «furniture that provides a place to
sleep» and `sleep` as «to rest in a bed», which is the cross-reference case the Captain named — and
`left` is where the tautology lives, since its noun and its adjective are one word wearing two parts
of speech.

The curated vocabulary and the reciprocal weight come from the migration that declares them (policy
v3), never from numbers retyped here.
"""

from dataclasses import replace

import pytest

from tests.lexicon_fixture import WORDNET_RELATION_NAMES, FixtureGlossProvider
from tests.seed import relation_policy
from tk2.dictionary import curation, relations
from tk2.dictionary.matrix import SOURCE_CURATED, Cell, Matrix, MatrixRow


@pytest.fixture
def provider():
    return FixtureGlossProvider()


@pytest.fixture
def policy():
    return relation_policy()


@pytest.fixture
def R(provider, policy):
    """R over five dimensions of the sixteen-word world. The fixture world states no WordNet
    relations at all, so this matrix is all diagonal — which is the honest starting point for
    curation: it exists because R had nothing to say."""

    class _Silent:
        def senses_of_key(self, key):
            return provider.senses_of_key(key)

        def relations_of_key(self, key):
            return {}

        def relations(self):
            return WORDNET_RELATION_NAMES

        def primary_sense_of_key(self, key):
            senses = provider.senses_of_key(key)
            return senses[0] if senses else None

        def relations_of_sense(self, sense):
            return {}

    return relations.build(("bed.n", "furniture.n", "left.a", "left.n", "sleep.v"), _Silent(), policy)


# ------------------------------------------------------------------------------------------------
# the miner
# ------------------------------------------------------------------------------------------------


def test_the_edge_is_minted_from_whichever_definition_speaks(provider, policy):
    """The cross-reference: `sleep`'s gloss never mentions a bed by name — «to rest in a bed» does,
    and so does `bed`'s own. Whichever side speaks, speaks, and the edge runs in that direction."""
    proposals = curation.propose_pair("bed.n", "sleep.v", provider, policy)
    assert {p.id for p in proposals} == {"bed.n>sleep.v", "sleep.v>bed.n"}
    assert all(p.naming_token in ("sleep", "bed") for p in proposals)


def test_a_definition_that_names_nothing_proposes_nothing(provider, policy):
    """«an honest curation cannot reach this one», not a tuning failure. `work` is defined as
    «labor at a task» and says nothing about furniture."""
    assert curation.propose_pair("work.v", "furniture.n", provider, policy) == []


def test_the_evidence_is_the_definition_verbatim(provider, policy):
    """A paraphrase is the curator arguing rather than the dictionary speaking. The naming word is
    MARKED and nothing else about the sentence moves."""
    proposal = curation.propose_directed("bed.n", "sleep.v", provider, policy)
    assert proposal.definition == "furniture that provides a place to sleep"
    assert proposal.evidence == "bed.n.01 «furniture that provides a place to <sleep>»"


def test_the_cue_words_decide_which_relation_is_guessed(provider, policy):
    """`bed`'s gloss is both purposive and locative («provides a PLACE to sleep»); the cue order in
    the rows is what makes it read as purpose, which is how the Captain quoted it."""
    proposal = curation.propose_directed("bed.n", "sleep.v", provider, policy)
    assert proposal.relation == "used_for"
    assert proposal.weight == policy.curated_weight("used_for")
    assert [name for name, _cues in policy.cues][:2] == ["causes", "used_for"]


def test_the_pos_pair_decides_when_no_cue_fires(policy):
    """And when neither does, `involves` — which claims only what the miner observed: the
    definition names it."""
    world = FixtureGlossProvider(
        lexicon=("rest", "sleep", "thing"),
        glosses={"rest": "to sleep", "sleep": "to rest", "thing": "a rest"},
        glosses_all={},
        lemmas={},
        parts_of_speech={"rest": ("v",), "sleep": ("v",), "thing": ("n",)},
    )
    assert curation.propose_directed("rest.v", "sleep.v", world, policy).relation == "entails"
    assert curation.propose_directed("thing.n", "rest.v", world, policy).relation == "used_for"

    no_defaults = policy.__class__(
        weights=policy.weights, curated=policy.curated,
        reciprocal_weight=policy.reciprocal_weight, cues=(), defaults=(),
    )
    assert curation.propose_directed("rest.v", "sleep.v", world, no_defaults).relation == curation.INVOLVES


def test_a_tautology_is_refused_and_surfaced(policy):
    """«land: the land on which real estate is located» — a definition naming its own headword under
    another part of speech. Mining it would mint `land.n -> land.v` out of a tautology, which is
    precisely the over-merge requirement 16 already measured. Refused, and REPORTED: the reader is
    entitled to know the miner stayed its hand and why.

    Its own two-word world, because the sixteen-word one has no gloss that names its own headword —
    a fixture that could not produce the defect could not prove it was refused."""
    world = FixtureGlossProvider(
        lexicon=("land", "estate"),
        glosses={"land": "the land on which real estate is located", "estate": "land and buildings"},
        glosses_all={},
        lemmas={},
        parts_of_speech={"land": ("n", "v"), "estate": ("n",)},
    )
    assert curation.propose_pair("land.n", "land.v", world, policy) == []
    skips = curation.self_reference_skips([("land.n", "land.v")], world)
    # BOTH directions are surfaced: this world gives a word one gloss whatever its part of speech,
    # so each side names the other, and each is the same tautology read the other way round.
    assert [(source, target) for source, target, _evidence in skips] == [
        ("land.n", "land.v"), ("land.v", "land.n")
    ]
    assert "<land>" in skips[0][2]

    # ...and it is the SELF-reference that is refused, never the word: `land.n -> estate.n` is a
    # perfectly good analytic edge out of the same sentence.
    assert curation.propose_directed("land.n", "estate.n", world, policy) is not None


def test_relabelling_moves_the_weight_with_the_name(provider, policy):
    """The Captain's hand on the NAME of an edge he accepts. A relabelled edge that kept the old
    weight would be an edge nobody declared — and the row says a hand chose it."""
    proposal = curation.propose_directed("bed.n", "sleep.v", provider, policy)
    moved = curation.relabel(proposal, "site_of", policy)
    assert (moved.relation, moved.weight) == ("site_of", policy.curated_weight("site_of"))
    assert moved.relabelled and not proposal.relabelled


def test_a_proposal_survives_the_round_trip(provider, policy):
    """`propose` writes a table the Captain reads and `approve` reads back exactly that table —
    he must be able to approve what he saw, not a re-mining of it."""
    proposal = curation.propose_directed("bed.n", "sleep.v", provider, policy)
    assert curation.Proposal.from_dict(proposal.as_dict()) == proposal


# ------------------------------------------------------------------------------------------------
# the two cells
# ------------------------------------------------------------------------------------------------


def test_a_curated_edge_writes_a_forward_cell_and_a_weaker_reciprocal(provider, policy):
    """The Captain's ruling of 2026-08-12. The reverse cell is TAGGED rather than renamed: one
    relation, stored asymmetrically, and `used_for_reciprocal` cannot be misread as saying that
    sleep is used for a bed."""
    proposal = curation.propose_directed("bed.n", "sleep.v", provider, policy)
    cells = curation.cells_of(proposal, policy)

    assert [(row, cell.column) for row, cell in cells] == [("bed.n", "sleep.v"), ("sleep.v", "bed.n")]
    assert cells[0][1].weight == policy.curated_weight("used_for")
    assert cells[1][1].weight == policy.reciprocal_weight
    assert cells[1][1].relation == "used_for" + curation.RECIPROCAL_SUFFIX


def test_a_curated_cell_is_distinguishable_from_a_mined_one_forever(provider, policy):
    """The whole claim of R is that a cell can be asked where it came from. A headline density that
    hid the hand would be the first step back to a matrix nobody can audit."""
    proposal = curation.propose_directed("bed.n", "sleep.v", provider, policy)
    for _row, cell in curation.cells_of(proposal, policy):
        assert cell.source == SOURCE_CURATED
        assert cell.evidence == proposal.evidence


def test_an_invented_relation_is_refused(provider, policy):
    """The vocabulary is closed on purpose: a curator who may invent a relation name per edge is
    writing prose, not a matrix."""
    proposal = curation.propose_directed("bed.n", "sleep.v", provider, policy)
    invented = replace(proposal, relation="smells_like", weight=0.5)
    with pytest.raises(curation.CurationRefused) as excinfo:
        curation.cells_of(invented, policy)
    assert "smells_like" in str(excinfo.value)


# ------------------------------------------------------------------------------------------------
# simulate
# ------------------------------------------------------------------------------------------------


def test_simulating_changes_nothing_and_reports_what_it_would(R, provider, policy):
    """`apply` builds a NEW matrix. The one it was handed is the one it hands back untouched, which
    is what «nothing is committed» has to mean when both sides are in memory."""
    proposal = curation.propose_directed("bed.n", "sleep.v", provider, policy)
    applied = curation.apply(R, [proposal], policy)

    assert R.cell("bed.n", "sleep.v") is None, "the original matrix is untouched"
    assert applied.matrix.cell("bed.n", "sleep.v").relation == "used_for"
    assert applied.matrix.cell("sleep.v", "bed.n").relation == "used_for_reciprocal"
    assert len(applied.written) == 2
    assert applied.overwrites == ()


def test_both_directions_of_one_pair_overwrite_each_other_out_loud(R, provider, policy):
    """Cross-reference means both glosses may speak, and then the second edge's RECIPROCAL lands on
    the first edge's forward cell. The result is order-dependent and therefore reported: a curated
    cell silently replacing another curated cell is the one overwrite nobody would go looking for."""
    proposals = curation.propose_pair("bed.n", "sleep.v", provider, policy)
    applied = curation.apply(R, proposals, policy)

    assert len(proposals) == 2
    assert len(applied.overwrites) == 2
    assert all("becomes" in note for note in applied.overwrites)


def test_an_overwrite_is_never_silent(policy, provider):
    """A curated cell landing where the resource already spoke is a hand disagreeing with WordNet —
    a thing the Captain may well want to do, and never a thing he should discover afterwards."""
    mined = Matrix(
        name="dictionary_base_relations",
        keys=("bed.n", "sleep.v"),
        rows=(
            MatrixRow("bed.n", 0, (Cell(column="sleep.v", weight=0.6, relation="meronym"),)),
            MatrixRow("sleep.v", 1, ()),
        ),
    )
    proposal = curation.propose_directed("bed.n", "sleep.v", provider, policy)
    applied = curation.apply(mined, [proposal], policy)
    assert len(applied.overwrites) == 1
    assert "meronym" in applied.overwrites[0]


def test_a_proposal_with_no_axis_to_write_to_is_reported(R, provider, policy):
    """Requirement 15: membership is a defect too. A curated edge nobody can write is a finding, and
    silence would file it as a success."""
    stray = curation.propose_directed("bed.n", "sleep.v", provider, policy)
    stray = curation.Proposal.from_dict({**stray.as_dict(), "target_key": "runway.n"})
    applied = curation.apply(R, [stray], policy)
    assert applied.unwritable == (stray.id,)
    assert applied.written == ()


# ------------------------------------------------------------------------------------------------
# THE GATE
# ------------------------------------------------------------------------------------------------


def test_approving_without_the_captain_is_refused(R, provider, policy):
    """The mechanism requirement 20 needs to stay true. A script able to mint its own curated cell
    would have quietly taken over the judgement the ruling reserves."""
    proposals = curation.propose_pair("bed.n", "sleep.v", provider, policy)
    with pytest.raises(curation.NotTheCaptainsHand):
        curation.approve(R, proposals, policy)
    with pytest.raises(curation.NotTheCaptainsHand):
        curation.approve(R, proposals, policy, curation.Approval(i_am_the_captain=False, authorized_by="me"))


def test_an_approval_must_name_the_hand_that_gave_it(R, provider, policy):
    """A curated cell whose hand cannot be named is a cell nobody can later argue with — the
    manifest would be a log, not a ledger."""
    proposals = curation.propose_pair("bed.n", "sleep.v", provider, policy)
    with pytest.raises(curation.NotTheCaptainsHand):
        curation.approve(R, proposals, policy, curation.Approval(i_am_the_captain=True, authorized_by="  "))


def test_the_gate_lets_a_named_hand_through_and_writes_the_same_cells(R, provider, policy):
    """ONE function builds the cells, so a simulation can never measure a different edge shape than
    the one approval writes. That is what makes the simulation worth running."""
    proposals = curation.propose_pair("bed.n", "sleep.v", provider, policy)
    simulated = curation.apply(R, proposals, policy)
    approved = curation.approve(
        R, proposals, policy, curation.Approval(i_am_the_captain=True, authorized_by="the Captain, in a test")
    )
    assert approved.written == simulated.written
    assert approved.matrix.rows == simulated.matrix.rows
