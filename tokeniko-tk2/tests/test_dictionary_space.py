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


def test_neighbours_answer_from_the_layer_they_were_asked_and_say_which():
    """«What is near this» is TWO questions. D proposes (brain req 12, the working set); R states.
    The space answers the one it was asked and names it."""
    held = space(near=0.1)

    proposed = held.neighbours("eat.v", count=3)
    assert proposed[0].key == "food.n", "D's answer: what their definitions share"
    assert proposed[0].source == SOURCE_DISTRIBUTIONAL

    stated = held.neighbours("eat.v", count=3, source=SOURCE_RELATIONAL)
    assert stated[0].key == "devour.v", "R's answer: what the resource states"
    assert stated[0].source == SOURCE_RELATIONAL


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


def test_the_catch_follows_the_same_R_first_rule_as_the_reader():
    """One procedure in this module, not two: where R speaks about the key it decides which anchor
    is nearest; where R is silent the catch still names one — «never-miss» — and says it came from D
    so the caller knows how much to trust it."""
    held = space(near=0.1)

    caught = held.nearest_anchor("devour.v", ["eat.v", "sleep.v"])
    assert caught.key == "eat.v"
    assert caught.source == SOURCE_RELATIONAL
    assert caught.verdict == "NEAR"

    # `food.n` states nothing but its own axis — and the identity axis is not an answer about a
    # pair, so R is SILENT about it and D is what has anything to say.
    fallen_back = held.nearest_anchor("food.n", ["eat.v", "sleep.v"])
    assert fallen_back.key == "eat.v"
    assert fallen_back.source == SOURCE_DISTRIBUTIONAL


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
    proposed = held.project("devour.v.01")
    assert stated is not None and proposed is not None
    assert not np.allclose(stated, proposed), "the two halves are different vectors"
    assert stated[held._index["eat.v"]] > 0
    assert proposed[held._index["food.n"]] > 0
