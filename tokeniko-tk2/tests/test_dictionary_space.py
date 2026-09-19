"""THE QUERY LAYER — the operations the engine performs, on a world small enough to reason about.

`DictionarySpace` exists because of a measurement, not a preference: tk1 held a dense square matrix
and got every question free, tk2 holds sparse rows, and the sparse trick for «what is near this»
does not work (`eat.v` shares a D column with 53% of the base). So the base is held dense in memory.

**REWRITTEN 2026-09-14, E1d T2.** These tests used to assert that «the blend is the ruled reading».
It was not: requirement 10 has said since 2026-08-12 that R and D are *«consulted separately, every
answer naming its source, never blended into one float»*, and the E1 audit found the reader returning
`cos(R + 0.15·D)` in flat contradiction of it. What is held to account here is the contract as the
requirement states it — **R decides · D proposes · ABSTAIN when R is silent** — on a handcrafted space
where every number can be checked by hand.
"""

import numpy as np
import pytest

from tk2.dictionary.config import (
    READING_SEPARATE, BarPair, ClosurePolicy, DictionaryConfig, ReadingPolicy,
)
from tk2.dictionary.space import (
    SOURCE_DISTRIBUTIONAL, SOURCE_RELATIONAL, SOURCE_SILENT, DictionarySpace, SpaceOrigin,
)


def cell(column, weight, relation="hypernym_1"):
    return {"column": column, "w": weight, "rel": relation, "src": "mined", "via": [], "evidence": ""}


DIMENSIONS = ("eat.v", "food.n", "devour.v", "sleep.v", "meal.n", "hunger.n")


def reading_policy(mix=0.15, near=0.28, far=0.0, mode=READING_SEPARATE):
    return ReadingPolicy(mix=mix, near_floor=near, far_ceiling=far, mode=mode)


def space(mix=0.15, near=0.28, far=0.0, senses=(), mode=READING_SEPARATE):
    """A four-dimension world with one stated relation and one gloss overlap.

    Deliberately built so the two layers DISAGREE: R relates `eat.v` to `devour.v` and says nothing
    about `food.n`; D relates `eat.v` to `food.n` and says nothing about `devour.v`. That is the
    whole point — a space where the layers agreed could not show which one answered.
    """
    config = DictionaryConfig(
        closure=ClosurePolicy(max_depth=2, max_size=100, senses="primary"),
        declared_seeds=("eat",),
        bar=(BarPair("eat.v", "food.n", "NEAR", "the review's own pair"),),
        reading=reading_policy(mix, near, far, mode),
    )
    relations = [
        {"key": "eat.v", "cells": [cell("eat.v", 1.0, "identity"), cell("devour.v", 0.7)]},
        {"key": "devour.v", "cells": [cell("devour.v", 1.0, "identity"), cell("eat.v", 0.7)]},
        {"key": "food.n", "cells": [cell("food.n", 1.0, "identity")]},
        {"key": "sleep.v", "cells": [cell("sleep.v", 1.0, "identity")]},
    ]
    # D's COSINE is «do these share neighbours», not «does one name the other» — two rows that
    # only point at each other are ORTHOGONAL. That is a property of the real D too, and getting it
    # wrong here first is how it got written down.
    distribution = [
        {"key": "eat.v", "cells": [cell("meal.n", 1.0, "gloss_overlap"),
                                   cell("hunger.n", 1.0, "gloss_overlap")]},
        {"key": "food.n", "cells": [cell("meal.n", 1.0, "gloss_overlap"),
                                    cell("hunger.n", 1.0, "gloss_overlap")]},
        {"key": "meal.n", "cells": [cell("eat.v", 1.0, "gloss_overlap")]},
        {"key": "hunger.n", "cells": [cell("eat.v", 1.0, "gloss_overlap")]},
    ]
    return DictionarySpace(config, DIMENSIONS, relations, distribution, senses)


# ------------------------------------------------------------------------------------------------
# the two layers are kept apart
# ------------------------------------------------------------------------------------------------


def test_the_two_layers_are_read_apart_and_each_names_itself():
    """Requirement 10. The proof is that they DISAGREE and both answers survive: R relates eat to
    devour, D relates eat to food, and neither number is folded into the other."""
    held = space()

    assert held.relational("eat.v", "devour.v") > 0
    assert held.relational("eat.v", "food.n") == pytest.approx(0.0)

    assert held.distributional("eat.v", "food.n") > 0
    assert held.distributional("eat.v", "devour.v") == pytest.approx(0.0)


def test_there_is_no_single_similarity_function():
    """A function called `similarity` returning ONE number is precisely what requirement 10 forbids:
    a caller could not tell which layer answered. Removing it is the fix, not renaming it."""
    assert not hasattr(DictionarySpace, "similarity")


def test_the_mix_no_longer_moves_a_verdict():
    """Under `separate` the verdict is R's, and R is never scaled. A mix that could still move a
    verdict would mean the blend was living on somewhere."""
    quiet, loud = space(mix=0.0), space(mix=1.0)

    assert quiet.read("eat.v", "devour.v").verdict == loud.read("eat.v", "devour.v").verdict
    assert quiet.relational("eat.v", "devour.v") == loud.relational("eat.v", "devour.v")


# ------------------------------------------------------------------------------------------------
# R decides · D proposes · ABSTAIN when R is silent
# ------------------------------------------------------------------------------------------------


def test_where_R_speaks_R_decides_and_the_reading_says_so():
    held = space(near=0.1)

    found = held.read("eat.v", "devour.v")
    assert found.source == SOURCE_RELATIONAL
    assert found.verdict == "NEAR"
    assert found.proposal is None, "R answered; D was not asked to"


def test_where_R_is_silent_the_verdict_is_ABSTAIN_and_D_only_PROPOSES():
    """THE MEASUREMENT THAT SETTLED IT (E1 audit, 2026-09-14): with R silent, D cannot separate a
    declared NEAR from a declared FAR — `eat.v~hungry.a` reads 0.338 against `bed.n~cause.n` at
    0.326, on identical cells. So D may propose and may never decide."""
    held = space(near=0.1)

    found = held.read("eat.v", "food.n")
    assert found.relational_cosine == pytest.approx(0.0)
    assert found.distributional_cosine > 0
    assert found.verdict == "ABSTAIN", "D is not allowed to decide"
    assert found.source == SOURCE_SILENT
    assert found.proposal == "NEAR", "what D WOULD have said, carried and not promoted"


def test_a_reading_carries_the_stated_cell_as_well_as_the_cosine():
    """Requirement 19 — the first curation round flipped a cell read while the cosine stayed mute,
    and a cosine-only verdict would have called that curation useless."""
    held = space()

    found = held.read("eat.v", "devour.v")
    assert found.relational_cell == pytest.approx(0.7)
    assert found.distributional_cell == pytest.approx(0.0)

    # `eat.v` and `food.n` share neighbours rather than naming each other, so the CELL is empty
    # while the COSINE is high — the two D reads answer different questions and the shape keeps both.
    other = held.read("eat.v", "food.n")
    assert other.distributional_cell == pytest.approx(0.0)
    assert other.distributional_cosine > 0.9
    assert held.read("eat.v", "meal.n").distributional_cell == pytest.approx(1.0)


def test_the_verdict_shortcut_agrees_with_the_reading():
    held = space(near=0.1)

    for left, right in (("eat.v", "devour.v"), ("eat.v", "food.n"), ("eat.v", "sleep.v")):
        assert held.verdict(left, right) == held.read(left, right).verdict


# ------------------------------------------------------------------------------------------------
# the mode is a ROW, and an undeclared one refuses
# ------------------------------------------------------------------------------------------------


def test_a_policy_that_never_ruled_the_mode_refuses_to_read():
    """The standing law of 2026-08-25: a reading that fell back to a value in code would be one the
    manifest cannot vouch for. v7-v10 ruled the mix and never faced this question."""
    undeclared = space(mode=None)

    with pytest.raises(ValueError, match="mode = separate"):
        undeclared.read("eat.v", "devour.v")


def test_an_unknown_mode_is_refused_at_the_policy_and_not_here():
    with pytest.raises(ValueError, match="unknown reading mode"):
        reading_policy(mode="blended")


def test_the_mode_travels_in_the_stats():
    assert space().stats()["mode"] == READING_SEPARATE


# ------------------------------------------------------------------------------------------------
# ignorance is not evidence
# ------------------------------------------------------------------------------------------------


def test_an_unknown_key_reads_none_and_not_zero():
    """«these two are unrelated» and «I have never heard of one of these» are different answers, and
    a caller that could not tell them apart would be treating ignorance as evidence."""
    held = space()

    assert held.relational("eat.v", "sleep.v") == pytest.approx(0.0)
    assert held.relational("eat.v", "banana.n") is None
    assert held.distributional("eat.v", "banana.n") is None
    assert held.read("eat.v", "banana.n") is None
    assert not held.holds("banana.n")


def test_an_unknown_key_abstains_rather_than_being_judged():
    held = space()

    assert held.verdict("eat.v", "banana.n") == "ABSTAIN"
    assert held.neighbours("banana.n") == []


def test_a_silent_row_is_near_nothing_rather_than_nan():
    """`sleep.v` states only its own axis. Dividing a zero row by its zero norm would put nan
    through every later comparison, and nan is not an answer — zero is, and it is the true one."""
    held = space()

    assert held.relational("sleep.v", "eat.v") == pytest.approx(0.0)
    assert not np.isnan(held.distributional("sleep.v", "food.n"))


def test_the_resident_size_is_reported_because_it_is_the_whole_design_argument():
    held = space()

    # TWO matrices now, and the cost of the ruling is visible rather than hidden.
    assert held.stats()["dimensions"] == 6
    assert held.stats()["resident_bytes"] == 2 * 6 * 6 * 4


# ------------------------------------------------------------------------------------------------
# the verdict is the policy's
# ------------------------------------------------------------------------------------------------


def test_the_verdict_comes_from_the_policy_and_not_from_this_module():
    """The standing law of 2026-08-25 put acceptance floors in ROWS. A threshold in the space would
    be the quieter of two declarations — so moving the row must move the answer."""
    strict, loose = space(near=0.99), space(near=0.01)

    assert strict.relational("eat.v", "devour.v") == loose.relational("eat.v", "devour.v")
    assert strict.verdict("eat.v", "devour.v") == "ABSTAIN"
    assert loose.verdict("eat.v", "devour.v") == "NEAR"


def test_a_negative_reading_is_FAR_and_the_theorem_is_cleaner_than_before():
    """Under the blend, FAR < 0 held because D is unsigned. Under `separate` it holds because ONLY R
    is read, so a reading below zero IS the resource's own statement of opposition."""
    config = DictionaryConfig(
        closure=ClosurePolicy(max_depth=2, max_size=100, senses="primary"),
        declared_seeds=("up",),
        bar=(BarPair("up.r", "down.r", "FAR", "unused here"),),
        reading=reading_policy(),
    )
    opposed = DictionarySpace(config, ("up.r", "down.r"), [
        {"key": "up.r", "cells": [cell("up.r", 1.0, "identity"), cell("down.r", -1.0, "antonym")]},
        {"key": "down.r", "cells": [cell("down.r", 1.0, "identity"), cell("up.r", -1.0, "antonym")]},
    ], [])

    assert opposed.relational("up.r", "down.r") < 0
    assert opposed.verdict("up.r", "down.r") == "FAR"


def test_a_weak_negative_survives_a_loud_D():
    """THE GAIN THAT IS NOT IN THE BAR. On the real base `thick.a~thin.a` is R −0.049 and D +0.676:
    the blend read +0.011 and ABSTAINED, and separate reads recover FAR. Two of the eight measurable
    opposition pairs get their sign back this way."""
    config = DictionaryConfig(
        closure=ClosurePolicy(max_depth=2, max_size=100, senses="primary"),
        declared_seeds=("thick",),
        bar=(BarPair("thick.a", "thin.a", "FAR", "the sign D was drowning"),),
        reading=reading_policy(mix=1.0),
    )
    held = DictionarySpace(config, ("thick.a", "thin.a", "size.n"), [
        {"key": "thick.a", "cells": [cell("thick.a", 1.0, "identity"), cell("thin.a", -0.05, "antonym")]},
        {"key": "thin.a", "cells": [cell("thin.a", 1.0, "identity"), cell("thick.a", -0.05, "antonym")]},
    ], [
        {"key": "thick.a", "cells": [cell("size.n", 0.9, "gloss_overlap")]},
        {"key": "thin.a", "cells": [cell("size.n", 0.9, "gloss_overlap")]},
    ])

    assert held.verdict("thick.a", "thin.a") == "FAR"
    assert held.read("thick.a", "thin.a").distributional_cosine > 0, "D still says topical"


# ------------------------------------------------------------------------------------------------
# the operations
# ------------------------------------------------------------------------------------------------


def test_resolve_returns_every_part_of_speech_and_picks_none():
    """`land` is `land.n` and `land.v`. Which one a sentence meant is the parser's to decide and the
    geometry's to inform — never this function's to guess."""
    config = DictionaryConfig(
        closure=ClosurePolicy(max_depth=2, max_size=100, senses="primary"),
        declared_seeds=("land",),
        bar=(BarPair("land.n", "land.v", "FAR", "the collapse that costs us"),),
        reading=reading_policy(),
    )
    held = DictionarySpace(config, ("land.n", "land.v", "eat.v"), [], [])

    assert held.resolve("land") == ("land.n", "land.v")
    assert held.resolve("LAND") == ("land.n", "land.v"), "normalised, not case-sensitive"
    assert held.resolve("banana") == ()


def test_R_PROPOSES_and_d_has_to_be_asked_for():
    """THE RULING OF 2026-09-14. Brain req 12 says memory proposes by cosine and does not say whose;
    D's was benched and cannot rank — 5.9% precision@10 against R's 28.7%, and no variant of D
    helps. So R is the default and D is a question a caller must ask explicitly."""
    held = space(near=0.1)

    proposed = held.neighbours("eat.v", count=3)
    assert proposed[0].key == "devour.v", "R's answer: what the resource states"
    assert proposed[0].source == SOURCE_RELATIONAL

    asked = held.neighbours("eat.v", count=3, source=SOURCE_DISTRIBUTIONAL)
    assert asked[0].key == "food.n", "D still answers «whose definitions look like this one»"
    assert asked[0].source == SOURCE_DISTRIBUTIONAL


def test_where_R_is_silent_NOTHING_is_proposed():
    """No fallback. On the real base R is silent for 14 of 4,555 dimensions (0.3%), and the D
    fallback this replaces was offering them cosines of +0.000 — an arbitrary ordering of zeros
    dressed as an answer. An abstention is honest; a wrong proposal is not."""
    held = space(near=0.1)

    assert held.relations_of("food.n") == (), "R states nothing about it but its own axis"
    assert held.neighbours("food.n") == []
    assert held.neighbours("food.n", source=SOURCE_DISTRIBUTIONAL), "D is still there to be asked"


def test_neighbours_drop_the_key_itself():
    """A thing being nearest to itself is a property of the identity axis, not an answer."""
    held = space()

    assert "eat.v" not in [n.key for n in held.neighbours("eat.v", count=3)]
    assert "eat.v" not in [n.key for n in held.neighbours("eat.v", count=3,
                                                         source=SOURCE_RELATIONAL)]


def test_neighbours_are_ordered_and_carry_their_verdict():
    held = space(near=0.1)

    found = held.neighbours("eat.v", count=4)
    assert [n.cosine for n in found] == sorted((n.cosine for n in found), reverse=True)
    assert all(n.verdict in ("NEAR", "ABSTAIN", "FAR") for n in found)
    assert found[0].is_near is (found[0].verdict == "NEAR")


def test_a_floor_on_neighbours_is_a_filter_and_not_a_verdict():
    """Asking for «the nearest above 0.5» is a different question from «which of these are NEAR»,
    and the space answers the one it was asked."""
    held = space()

    assert held.neighbours("eat.v", count=4, floor=1.01) == []
    assert held.neighbours("eat.v", count=4, floor=-1.0)


def test_relations_are_stated_separately_from_the_geometry():
    """«the resource says X is a kind of Y» and «X and Y read near» are different claims: the is_a
    graph gates taxonomy, cosine proposes candidates. The identity axis is not a relation."""
    held = space()

    stated = held.relations_of("eat.v")
    assert stated == (("devour.v", "hypernym_1", 0.7),)
    assert "identity" not in [relation for _column, relation, _weight in stated]
    assert held.relations_of("sleep.v") == ()


# ------------------------------------------------------------------------------------------------
# the semantic catch
# ------------------------------------------------------------------------------------------------


def test_the_catch_follows_THE_SAME_RULE_as_the_proposer():
    """One procedure in this module, not two: R decides which anchor is nearest, and where R is
    silent the catch REFUSES.

    This narrows «never-miss» deliberately. The catch used to name an anchor whatever happened,
    falling back to D — but D's cosines where R is silent are +0.000, so «the nearest» was `argmax`
    over zeros: the first candidate, dressed as a measurement. `None` joins the two refusals that
    were already here (the key is not a dimension; no anchor is)."""
    held = space(near=0.1)

    caught = held.nearest_anchor("devour.v", ["eat.v", "sleep.v"])
    assert caught.key == "eat.v"
    assert caught.source == SOURCE_RELATIONAL
    assert caught.verdict == "NEAR"

    # `food.n` states nothing but its own axis, and the identity axis is not an answer about a pair.
    assert held.relations_of("food.n") == ()
    assert held.nearest_anchor("food.n", ["eat.v", "sleep.v"]) is None


def test_the_catch_refuses_when_it_has_nothing_to_measure_against():
    held = space()

    assert held.nearest_anchor("eat.v", ["banana.n"]) is None
    assert held.nearest_anchor("banana.n", ["eat.v"]) is None


def test_a_projection_names_the_half_it_read():
    """A sense has both floors, and folding them together here would be the blend rebuilt one layer
    down — exactly what policy v11 ruled out."""
    senses = [{
        "key": "devour.v.01", "base": "devour.v", "ordinal": 1, "synset": "devour.v.01",
        "definition": "eat greedily",
        "relations": [{"column": "eat.v", "w": 0.8, "rel": "hypernym_1"}],
        "distribution": [{"column": "food.n", "w": 0.5}],
    }]
    held = space(senses=senses)

    stated = held.project("devour.v.01", source=SOURCE_RELATIONAL)
    proposed = held.project("devour.v.01", source=SOURCE_DISTRIBUTIONAL)
    assert stated is not None and proposed is not None
    assert not np.allclose(stated, proposed), "the two halves are different vectors"
    assert stated[held._index["eat.v"]] > 0
    assert proposed[held._index["food.n"]] > 0


def test_a_sense_is_placed_by_its_RELATIONS_where_it_states_any():
    """THE RULING OF 2026-09-14: R first, D where the sense states no relations, and the answer
    NAMES the half. Deliberately not `neighbours`' rule, which refuses its fallback — there the
    fallback was +0.000, here D still answers 18.8% hit@5 and relations reach only 56.3% of the
    out-of-base senses this exists for."""
    senses = [
        {"key": "devour.v.01", "base": "devour.v", "ordinal": 1, "synset": "devour.v.01",
         "definition": "eat greedily",
         "relations": [{"column": "eat.v", "w": 0.8, "rel": "hypernym_1"}],
         "distribution": [{"column": "food.n", "w": 0.5}]},
        # States nothing — 40.2% of senses are like this, which is why the fallback stays.
        {"key": "devour.v.02", "base": "devour.v", "ordinal": 2, "synset": "devour.v.02",
         "definition": "read greedily", "relations": [],
         "distribution": [{"column": "food.n", "w": 0.5}]},
    ]
    held = space(senses=senses)

    stated = held.projection("devour.v.01")
    assert stated.source == SOURCE_RELATIONAL
    assert stated.vector[held._index["eat.v"]] > 0

    fallen_back = held.projection("devour.v.02")
    assert fallen_back.source == SOURCE_DISTRIBUTIONAL, "D where the sense states nothing"
    assert fallen_back.vector[held._index["food.n"]] > 0

    # A caller may still force one half and get silence rather than the other one.
    assert held.projection("devour.v.02", source=SOURCE_RELATIONAL) is None


def test_a_placement_is_ranked_IN_THE_HALF_it_was_projected_from():
    """A correctness property, not an option. Ranking a relations-projected sense against D's
    columns asks «whose DEFINITION mentions the words this synset is RELATED to» — a cross-space
    question, and it makes the `source` label a false statement. Measured worse too: devour.v.01
    («destroy completely») returns fail.v/compulsion.n crossed and ruin.v/destroy.v/defeat.v in its
    own space, 15.6% prec@5 against 13.3%."""
    senses = [{
        "key": "devour.v.01", "base": "devour.v", "ordinal": 1, "synset": "devour.v.01",
        "definition": "eat greedily",
        "relations": [{"column": "eat.v", "w": 0.8, "rel": "hypernym_1"}],
        "distribution": [{"column": "food.n", "w": 0.5}],
    }]
    held = space(senses=senses)

    placed = held.place("devour")["devour.v.01"]
    assert placed[0].key == "eat.v", "ranked among what R states, because R is what placed it"
    assert all(n.source == SOURCE_RELATIONAL for n in placed), "every neighbour names the half"

    crossed = held.neighbours_of_vector(held.project("devour.v.01"), source=SOURCE_DISTRIBUTIONAL)
    assert all(n.source == SOURCE_DISTRIBUTIONAL for n in crossed), "and says so when asked to"


# ------------------------------------------------------------------------------------------------
# the placement rule — dictionary req 22, the Captain's ruling of 2026-09-19 (E3 task 6)
# ------------------------------------------------------------------------------------------------


DEVOURS = [{
    "key": "devour.v.01", "base": "devour.v", "ordinal": 1, "synset": "devour.v.01",
    "definition": "eat greedily",
    "relations": [{"column": "eat.v", "w": 0.8, "rel": "hypernym_1"}],
    "distribution": [{"column": "food.n", "w": 0.5}],
}, {
    "key": "devour.v.02", "base": "devour.v", "ordinal": 2, "synset": "devour.v.02",
    "definition": "destroy completely",
    "relations": [],
    "distribution": [{"column": "food.n", "w": 0.5}, {"column": "eat.v", "w": 0.2}],
}]


def test_a_placement_is_trusted_only_where_R_STATES_THE_EDGE():
    """**THE FLOOR, MEASURED AND REFUSED** (E3 task 6). The verdict used to come from the BASE's
    floor, fitted on base-to-base cosines where p90 is +0.000 — which read NEAR for 99.5% of
    relations placements and 91.1% of distributional ones. On the forty placements the Captain ruled
    the cosine does not separate the good from the bad in EITHER half, so no floor replaced it: a
    placement is trusted where the sense STATES an edge to that dimension, and abstains otherwise.

    `devour.v.01` states `eat.v` and is trusted there; the dimensions it merely ranks NEAR abstain,
    which is the sibling fallback that produced every one of the bar's six relational failures.
    """
    held = space(senses=DEVOURS)

    placed = held.place("devour")["devour.v.01"]
    assert placed[0].key == "eat.v" and placed[0].verdict == "NEAR"
    assert all(n.verdict == "ABSTAIN" for n in placed[1:]), (
        "a dimension the sense does not state is a sibling of a sibling, whatever its cosine")


def test_a_DISTRIBUTIONAL_placement_can_never_be_trusted_and_that_is_structural():
    """It is not a policy choice: a sense reaches D precisely BECAUSE it states no relations, so a
    stated edge cannot exist there. Measured over the whole build: 0.0% of 44,666 distributional
    placements state their nearest dimension, against 31.5% of the relational ones."""
    held = space(senses=DEVOURS)

    placed = held.place("devour")["devour.v.02"]
    assert placed, "it is still PLACED — the abstention is about trust, not about coverage"
    assert all(n.source == SOURCE_DISTRIBUTIONAL for n in placed)
    assert all(n.verdict == "ABSTAIN" for n in placed)


def test_a_placement_never_issues_FAR():
    """«I cannot vouch for this» and «the resource says these are opposed» are different statements.
    A placement has no opposition to declare: below the FAR ceiling is R's own signed reading of two
    DIMENSIONS, and a sense that states nothing states nothing in either direction."""
    held = space(senses=DEVOURS)

    every = [n for placed in held.place("devour").values() for n in placed]
    assert every and not any(n.verdict == "FAR" for n in every)
    assert held.placement_verdict("devour.v.01", "eat.v") == "NEAR"
    assert held.placement_verdict("devour.v.01", "food.n") == "ABSTAIN"
    assert held.placement_verdict("nobody.v.99", "eat.v") == "ABSTAIN", "an unknown sense abstains"


# ------------------------------------------------------------------------------------------------
# the cell decides — requirement 19, honoured at last (policy v12)
# ------------------------------------------------------------------------------------------------


def cell_first(near=0.28, structural=("derivational",), reference=("gloss_reference",)):
    """A world where R's COSINE says nothing and a stated cell says everything — which is `eat.v ~
    food.n` on the real base: D cosine +0.0484, D direct cell 0.0000, and the only true statement is
    that eat's definition NAMES food."""
    config = DictionaryConfig(
        closure=ClosurePolicy(max_depth=2, max_size=100, senses="primary"),
        declared_seeds=("eat",),
        bar=(BarPair("eat.v", "food.n", "NEAR", "the Captain's line"),),
        reading=ReadingPolicy(mix=0.15, near_floor=near, far_ceiling=0.0, mode=READING_SEPARATE,
                              cell_decides=True, structural_relations=structural,
                              reference_relations=reference),
    )
    relations = [
        {"key": "eat.v", "cells": [cell("eat.v", 1.0, "identity"),
                                   cell("food.n", 0.9, "gloss_reference")]},
        {"key": "food.n", "cells": [cell("food.n", 1.0, "identity")]},
        {"key": "land.n", "cells": [cell("land.n", 1.0, "identity"),
                                    cell("land.v", 0.45, "derivational")]},
        {"key": "land.v", "cells": [cell("land.v", 1.0, "identity"),
                                    cell("land.n", 0.45, "derivational")]},
    ]
    return DictionarySpace(config, ("eat.v", "food.n", "land.n", "land.v"), relations, [])


def test_a_stated_cell_decides_where_the_cosine_is_silent():
    """REQUIREMENT 2, CLOSED. The reader used to consult the cell only to ask whether R SPOKE — never
    what it SAID — which is why a stated 0.9 could still abstain."""
    held = cell_first()

    found = held.read("eat.v", "food.n")
    assert found.verdict == "NEAR"
    assert found.source == SOURCE_RELATIONAL
    assert found.relational_relation == "gloss_reference"
    assert found.relational_cosine == pytest.approx(0.0), "the cosine had nothing to say"


def test_a_structural_relation_may_not_decide():
    """`derivational` states «same root», not «same meaning» — which is exactly why land.n~land.v,
    compass.n~compass.v and play.n~play.v are declared FAR and read positive (req 16).

    Held by comparing two policies that differ ONLY in whether the relation is structural, with the
    NEAR floor put out of the cosine's reach so the cell is the only thing that could decide."""
    excluded = cell_first(near=0.99, structural=("derivational",))
    admitted = cell_first(near=0.99, structural=())

    assert excluded.read("land.n", "land.v").relational_cell == pytest.approx(0.45), "recorded"
    assert excluded.verdict("land.n", "land.v") == "ABSTAIN", "and not allowed to decide"
    assert admitted.verdict("land.n", "land.v") == "NEAR", "the same cell, admitted, decides"


def test_a_reference_cell_stays_out_of_the_relational_cosine():
    """MEASURED, not preferred: with reference cells in the cosine and the reciprocal on,
    land.n~land.v, state.n~state.v and play.n~play.v all flip to a wrong NEAR."""
    inside = cell_first(reference=())
    outside = cell_first()

    assert inside.relational("eat.v", "food.n") > 0
    assert outside.relational("eat.v", "food.n") == pytest.approx(0.0)


def test_a_policy_that_never_ruled_the_cell_rule_reads_as_it_always_read():
    """v7-v11 are still readable, and a default here would be a reading the manifest cannot vouch
    for. The cell still says whether R SPEAKS; it just may not decide."""
    held = space(near=0.1)

    found = held.read("eat.v", "devour.v")
    assert found.source == SOURCE_RELATIONAL
    assert found.relational_cosine > 0, "the COSINE answered, as it did before v12"


def test_the_catch_over_a_vector_refuses_a_ZERO_reading():
    """The same defect, through the door the senses opened. If a projected sense shares no column
    with any anchor, `argmax` returns whichever anchor was listed first — nothing was measured, and
    naming one anyway is the zeros-dressed-as-an-answer this project already refused once."""
    senses = [{
        "key": "devour.v.01", "base": "devour.v", "ordinal": 1, "synset": "devour.v.01",
        "definition": "destroy completely",
        "relations": [{"column": "sleep.v", "w": 0.8, "rel": "hypernym_1"}],
        "distribution": [],
    }]
    held = space(senses=senses)
    found = held.projection("devour.v.01")

    # `sleep.v` is what it states, so an anchor set containing it is measurable ...
    caught = held.nearest_anchor_of_vector(found.vector, ["sleep.v", "food.n"], source=found.source)
    assert caught is not None and caught.key == "sleep.v" and caught.source == found.source

    # ... and one that shares no column with it at all is not: `meal.n`'s R row is empty, so every
    # reading is 0.0 and the winner would be whichever anchor happened to be listed first.
    assert held.nearest_anchor_of_vector(found.vector, ["meal.n"], source=found.source) is None


# ------------------------------------------------------------------------------------------------
# the dirty-check's fourth field
# ------------------------------------------------------------------------------------------------


def test_the_closed_class_version_moves_the_origin():
    """**THE DRIFT THAT WOULD HAVE BEEN SILENT** (the Captain, 2026-09-16: «fix it now, before any
    v7»). The closed-class forms are a STRUCTURE FILTER on D's vocabulary — a function word is
    compiled and never defined — so a closed-class migration changes what D would be built from.

    Until this field existed, nothing recorded which set a sealed base had been filtered by: the
    base keeps its label and its seals, the table moves underneath it, and no check disagrees.
    """
    before = SpaceOrigin(build="b", seals=(("relational", "aaa"),), policy_version=14,
                         closed_class_version=6)
    after = SpaceOrigin(build="b", seals=(("relational", "aaa"),), policy_version=14,
                        closed_class_version=7)

    moved = before.differs_from(after)
    assert moved, "a closed-class migration must make the space visibly stale"
    assert "closed classes v6 -> v7" in moved[0]
    assert "D's vocabulary filter moved" in moved[0], "and it must say WHY that matters"


def test_a_space_that_was_not_told_its_closed_class_version_says_so():
    """`None` rather than 0 — «nobody said» and «version zero» are different answers, and a caller
    that could not tell them apart would be treating ignorance as evidence. The same distinction
    `relational()` makes between a zero cosine and an unknown key."""
    quiet = SpaceOrigin(build="b", policy_version=14)

    assert quiet.closed_class_version is None
    assert quiet.differs_from(SpaceOrigin(build="b", policy_version=14)) == ()
