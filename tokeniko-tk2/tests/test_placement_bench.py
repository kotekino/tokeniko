"""THE PLACEMENT BENCH — E3 task 6's measurement, pinned so it cannot quietly change.

**Pure.** The forty are evidence in a fixture and the two functions under test are arithmetic over
them, so this needs no database, no base and no WordNet. The slow half of the bench — the whole
placed population — is a `--population` flag on the tool and is not a test: it is a measurement of a
build, and a build is not this suite's to hold still.

What is pinned is the FINDING, not a number: on the Captain's own verdicts the cosine does not
separate a placement worth trusting from one that is not. If a later rebuild changes that, this test
goes red and the ruling gets re-opened with evidence — which is the only way a refusal to fit a
threshold can stay honest.
"""

from tests.fixtures.placement_bar import (
    DISTRIBUTIONAL,
    FAR,
    NEAR,
    PLACEMENTS,
    RELATIONAL,
    of_half,
)
from tools.placement_bench import best_floor, gap


def test_the_bar_is_forty_pairs_ruled_across_both_halves_and_the_whole_range():
    """The sample's own shape: a bar drawn from one band or one half could be argued away."""
    assert len(PLACEMENTS) == 40
    assert len(of_half(RELATIONAL)) == len(of_half(DISTRIBUTIONAL)) == 20
    for half in (RELATIONAL, DISTRIBUTIONAL):
        cosines = [p.cosine for p in of_half(half)]
        assert max(cosines) - min(cosines) > 0.2, f"{half}: the sample must span a real range"


def test_NO_COSINE_SEPARATES_a_placement_worth_trusting_from_one_that_is_not():
    """**THE RESULT OF TASK 6, and it is a refusal.** `db/0002`'s lesson says a threshold belongs in
    the middle of a real gap. In both halves the declared verdicts CROSS — R's highest FAR (+0.4454)
    sits above its lowest NEAR (+0.2606), and D's (+0.3780) above its (+0.1654) — so there is no gap
    to sit in, and any floor fitted here would be the appearance of a measurement."""
    for half in (RELATIONAL, DISTRIBUTIONAL):
        placements = of_half(half)
        assert gap(placements) is None, f"{half}: a gap appeared — re-open the ruling"
        highest_far = max(p.cosine for p in placements if p.verdict == FAR)
        lowest_near = min(p.cosine for p in placements if p.verdict == NEAR)
        assert lowest_near < highest_far


def test_the_best_floor_for_the_DISTRIBUTIONAL_half_is_to_trust_nothing():
    """The bench's own optimum, and the argument for abstention arrived at by arithmetic rather than
    by preference: the fewest-wrong threshold over D's twenty is 1.0 — reject everything — and it is
    still wrong twice, because `attack -> act` and `barbarity -> act` are right."""
    floor, wrong, _declared = best_floor(of_half(DISTRIBUTIONAL))
    assert floor == 1.0
    assert wrong == 2


def test_the_best_floor_for_the_RELATIONAL_half_would_throw_away_its_best_placement():
    """+0.4555 is the fewest-wrong threshold for R, and `involve.v.05 -> include.v` — «contain as a
    part», the most exact placement in the whole sample — sits at +0.2606, far beneath it."""
    floor, wrong, _declared = best_floor(of_half(RELATIONAL))
    assert (floor, wrong) == (0.4555, 3)

    involve = next(p for p in PLACEMENTS if p.sense == "involve.v.05")
    assert involve.verdict == NEAR and involve.cosine < floor


def test_a_bar_with_a_real_gap_DOES_get_a_floor():
    """The control: the bench must be able to say yes. A gate that can only refuse is not measuring.

    Hand-made pairs with a clean separation — FARs below +0.20, NEARs above +0.40 — and the bench
    finds the gap and puts the floor in its middle, which is `db/0007`'s own discipline.
    """
    from tests.fixtures.placement_bar import Placement

    clean = tuple(
        Placement(f"s{i}.n.01", "d.n", cosine, RELATIONAL, (), "", verdict, "hand-made")
        for i, (cosine, verdict) in enumerate(
            [(0.05, FAR), (0.12, FAR), (0.19, FAR), (0.41, NEAR), (0.55, NEAR), (0.70, NEAR)])
    )

    found = gap(clean)
    assert found == (0.19, 0.41)
    assert abs(sum(found) / 2 - 0.30) < 1e-9, "and the floor would sit in the middle of it"
    assert best_floor(clean) == (0.41, 0, "3 NEAR / 3 FAR declared")


def test_the_STATED_EDGE_trusts_without_ever_trusting_wrongly():
    """**THE RULE THAT REPLACED THE FLOOR** (dictionary req 22, the Captain 2026-09-19). Where the
    cosine interleaves, the stated edge does not: every placement whose sense states a relation to
    the dimension it landed on is declared NEAR, and none is declared FAR.

    Its cost is coverage, and the coverage was the deciding number — 31.5% of relations placements
    over the whole build, 0.0% of distributional ones. The 0.0% is structural: a sense reaches D
    precisely because it states no relations, so this bar's D half cannot contain a counter-example
    and is not evidence that it never will.
    """
    stated = [p for p in PLACEMENTS if p.stated]

    assert stated, "a rule with no witness in the bar is a rule fitted to nothing"
    assert all(p.verdict == NEAR for p in stated)
    assert all(p.half == RELATIONAL for p in stated)
    assert not any(p.stated for p in of_half(DISTRIBUTIONAL))


def test_every_relational_FAILURE_in_the_bar_is_the_SIBLING_FALLBACK():
    """The other side of the same rule: the six R placements the Captain declared FAR state no edge
    to what they landed on. They are what the projection does when the edge a sense DOES state points
    at something that is not a dimension — it falls to siblings, and a sibling of a sibling says
    nothing. That is the failure the stated edge refuses, and it is why the rule is not «R is
    trusted»: that version would have carried all six."""
    failures = [p for p in of_half(RELATIONAL) if p.verdict == FAR]

    assert len(failures) == 6
    assert not any(p.stated for p in failures)
