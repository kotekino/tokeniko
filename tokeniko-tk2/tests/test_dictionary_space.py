"""THE QUERY LAYER — the operations the engine performs, on a world small enough to reason about.

`DictionarySpace` exists because of a measurement, not a preference: tk1 held a dense square matrix
and got every question free, tk2 holds sparse rows, and the sparse trick for «what is near this»
does not work (`eat.v` shares a D column with 53% of the base). So the base is held dense in memory.

What is held to account here is the CONTRACT, on a handcrafted space where every number can be
checked by hand: that the blend is the ruled reading, that the verdict is the POLICY's and not this
module's, that «I have never heard of this» is a different answer from «these are unrelated», and
that a word outside the base still reaches the space through its senses.
"""

import numpy as np
import pytest

from tk2.dictionary.config import BarPair, ClosurePolicy, DictionaryConfig, ReadingPolicy
from tk2.dictionary.space import DictionarySpace, SpaceOrigin


def cell(column, weight, relation="hypernym_1"):
    return {"column": column, "w": weight, "rel": relation, "src": "mined", "via": [], "evidence": ""}


DIMENSIONS = ("eat.v", "food.n", "devour.v", "sleep.v")


def space(mix=0.15, near=0.28, far=0.0, senses=()):
    """A four-dimension world with one stated relation and one gloss overlap.

    Small on purpose: every cosine below is checkable with a pencil, which is the only way to know
    that the blend is the reading the policy declares rather than the one the code happens to do.
    """
    config = DictionaryConfig(
        closure=ClosurePolicy(max_depth=2, max_size=100, senses="primary"),
        declared_seeds=("eat",),
        bar=(BarPair("eat.v", "food.n", "NEAR", "the review's own pair"),),
        reading=ReadingPolicy(mix=mix, near_floor=near, far_ceiling=far),
    )
    relations = [
        {"key": "eat.v", "cells": [cell("eat.v", 1.0, "identity"), cell("devour.v", 0.7)]},
        {"key": "devour.v", "cells": [cell("devour.v", 1.0, "identity"), cell("eat.v", 0.7)]},
        {"key": "food.n", "cells": [cell("food.n", 1.0, "identity")]},
        {"key": "sleep.v", "cells": [cell("sleep.v", 1.0, "identity")]},
    ]
    distribution = [
        {"key": "eat.v", "cells": [cell("food.n", 0.5, "gloss_overlap")]},
        {"key": "food.n", "cells": [cell("eat.v", 0.5, "gloss_overlap")]},
    ]
    return DictionarySpace(config, DIMENSIONS, relations, distribution, senses)


# ------------------------------------------------------------------------------------------------
# what it holds
# ------------------------------------------------------------------------------------------------


def test_the_blend_is_the_ruled_reading_and_not_a_second_one():
    """R at full weight and D scaled by the mix, summed into one array — the cosine of two
    concatenated vectors IS the cosine of one summed vector when the halves share a key space, and
    R and D share one by construction. A space that kept them apart would pay for the separation on
    every query and buy nothing with it."""
    quiet = space(mix=0.0)
    loud = space(mix=1.0)

    # With D silent, `eat.v ~ food.n` has nothing but D between them.
    assert quiet.similarity("eat.v", "food.n") == pytest.approx(0.0)
    assert loud.similarity("eat.v", "food.n") > quiet.similarity("eat.v", "food.n")
    # R's own edge is untouched by the mix — only D is scaled.
    assert loud.similarity("eat.v", "devour.v") > 0


def test_a_silent_row_is_near_nothing_rather_than_nan():
    """`sleep.v` states only its own axis. Dividing a zero row by its zero norm would put nan
    through every later comparison, and nan is not an answer — zero is, and it is the true one."""
    held = space()

    assert held.similarity("sleep.v", "eat.v") == pytest.approx(0.0)
    assert not np.isnan(held.similarity("sleep.v", "food.n"))


def test_the_resident_size_is_reported_because_it_is_the_whole_design_argument():
    held = space()

    assert held.stats()["dimensions"] == 4
    assert held.stats()["resident_bytes"] == 4 * 4 * 4  # float32, four by four
    assert held.stats()["mix"] == 0.15


# ------------------------------------------------------------------------------------------------
# ignorance is not evidence
# ------------------------------------------------------------------------------------------------


def test_an_unknown_key_reads_none_and_not_zero():
    """«these two are unrelated» and «I have never heard of one of these» are different answers, and
    a caller that could not tell them apart would be treating ignorance as evidence."""
    held = space()

    assert held.similarity("eat.v", "sleep.v") == pytest.approx(0.0)
    assert held.similarity("eat.v", "banana.n") is None
    assert not held.holds("banana.n")


def test_an_unknown_key_abstains_rather_than_being_judged():
    held = space()

    assert held.verdict("eat.v", "banana.n") == "ABSTAIN"
    assert held.neighbours("banana.n") == []


# ------------------------------------------------------------------------------------------------
# the verdict is the policy's
# ------------------------------------------------------------------------------------------------


def test_the_verdict_comes_from_the_policy_and_not_from_this_module():
    """The standing law of 2026-08-25 put acceptance floors in ROWS. A threshold in the space would
    be the quieter of two declarations — so moving the row must move the answer."""
    strict = space(near=0.99)
    loose = space(near=0.01)

    reading = strict.similarity("eat.v", "devour.v")
    assert reading == loose.similarity("eat.v", "devour.v"), "the reading is the same number"
    assert strict.verdict("eat.v", "devour.v") == "ABSTAIN"
    assert loose.verdict("eat.v", "devour.v") == "NEAR"


def test_a_negative_reading_is_FAR_because_only_R_can_produce_one():
    """D is unsigned, so a negative dual read IS R's sign. The FAR edge is a theorem."""
    config = DictionaryConfig(
        closure=ClosurePolicy(max_depth=2, max_size=100, senses="primary"),
        declared_seeds=("eat",),
        bar=(BarPair("eat.v", "food.n", "NEAR", "unused here"),),
        reading=ReadingPolicy(mix=0.15, near_floor=0.28, far_ceiling=0.0),
    )
    opposed = DictionarySpace(config, ("up.r", "down.r"), [
        {"key": "up.r", "cells": [cell("up.r", 1.0, "identity"), cell("down.r", -1.0, "antonym")]},
        {"key": "down.r", "cells": [cell("down.r", 1.0, "identity"), cell("up.r", -1.0, "antonym")]},
    ], [])

    assert opposed.similarity("up.r", "down.r") < 0
    assert opposed.verdict("up.r", "down.r") == "FAR"


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
        reading=ReadingPolicy(mix=0.15, near_floor=0.28, far_ceiling=0.0),
    )
    held = DictionarySpace(config, ("land.n", "land.v", "eat.v"), [], [])

    assert held.resolve("land") == ("land.n", "land.v")
    assert held.resolve("LAND") == ("land.n", "land.v"), "normalised, not case-sensitive"
    assert held.resolve("banana") == ()


def test_neighbours_drops_the_key_itself():
    """A thing being nearest to itself is a property of the identity axis, not an answer."""
    held = space()

    found = held.neighbours("eat.v", count=3)
    assert "eat.v" not in [n.key for n in found]
    assert found[0].key == "devour.v", "the stated relation is the nearest thing to it"
    assert found[0].cosine > 0


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

    assert held.neighbours("eat.v", count=4, floor=0.99) == []
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
# the semantic catch, and the half E1c added
# ------------------------------------------------------------------------------------------------


def test_the_catch_always_returns_a_nearest_and_says_how_near_it_is():
    """«Never rely on a fixed dictionary: map any input to the nearest of a small anchor set» —
    manageable because the set is small, never-miss because there is always a nearest. The verdict
    rides along so a caller can tell «nearest, and genuinely near» from «nearest of a bad lot»."""
    held = space(near=0.1)

    caught = held.nearest_anchor("devour.v", ["eat.v", "sleep.v"])
    assert caught.key == "eat.v"
    assert caught.verdict == "NEAR"

    # sleep.v is silent: its nearest anchor is still named, and the verdict says not to trust it.
    weak = held.nearest_anchor("sleep.v", ["eat.v", "food.n"])
    assert weak is not None
    assert weak.verdict != "NEAR"


def test_the_catch_refuses_when_it_has_nothing_to_measure_against():
    held = space()

    assert held.nearest_anchor("eat.v", ["banana.n"]) is None
    assert held.nearest_anchor("banana.n", ["eat.v"]) is None


def test_a_word_outside_the_base_reaches_the_space_through_its_senses():
    """The gap E1c closes, and the reason `place` exists. Most words are not dimensions — the base
    is 4,555 keys out of 68,779 words — so a space that could only answer about its own rows would
    make «never rely on a fixed dictionary» a promise it could not keep."""
    readings = [{
        "key": "gobble.v.01", "base": "gobble.v", "ordinal": 1, "synset": "devour.v.04",
        "definition": "eat greedily",
        "relations": [cell("eat.v", 0.7)],
        "distribution": [cell("food.n", 0.5, "gloss_overlap")],
    }]
    held = space(near=0.1, senses=readings)

    assert not held.holds("gobble.v"), "the word is not a dimension"
    placed = held.place("gobble")
    assert list(placed) == ["gobble.v.01"]
    assert placed["gobble.v.01"][0].key == "eat.v"
    assert placed["gobble.v.01"][0].verdict == "NEAR"


def test_a_sense_with_no_cells_is_unplaced_rather_than_placed_at_the_origin():
    """5.3% of real senses name no base word and 54.1% reach none by relation. An unplaced sense is
    one the station will ABSTAIN on — and a zero vector normalised would be a direction it does not
    have."""
    readings = [{"key": "quux.n.01", "base": "quux.n", "ordinal": 1, "synset": "quux.n.01",
                 "definition": "", "relations": [], "distribution": []}]
    held = space(senses=readings)

    assert held.project("quux.n.01") is None
    assert held.place("quux") == {"quux.n.01": []}
    assert held.neighbours_of_vector(None) == []


def test_the_senses_of_a_dimension_come_back_in_the_resources_own_order():
    """«Every sense of `small.a`» is the question the station asks most, and the order is WordNet's
    because sense one is not an arbitrary reading — it is the one the base itself took."""
    readings = [
        {"key": "eat.v.02", "base": "eat.v", "ordinal": 2, "synset": "feed.v.06",
         "definition": "take in food", "relations": [], "distribution": []},
        {"key": "eat.v.01", "base": "eat.v", "ordinal": 1, "synset": "eat.v.01",
         "definition": "take in solid food", "relations": [cell("food.n", 0.7)], "distribution": []},
    ]
    held = space(senses=readings)

    found = held.senses_of("eat.v")
    assert [s.ordinal for s in found] == [1, 2]
    assert found[0].definition == "take in solid food"
    assert held.sense("eat.v.01").relations == (("food.n", "hypernym_1", 0.7),)
    assert held.sense("nothing.n.01") is None
    assert held.senses_of("sleep.v") == ()


# ------------------------------------------------------------------------------------------------
# the dirty-check — knowing when the rows have moved
# ------------------------------------------------------------------------------------------------


def loaded(**changes):
    base = {"build": "9824ef465c86",
            "seals": (("dictionary_base_distribution", "d1"), ("dictionary_base_relations", "r1")),
            "policy_version": 10}
    return SpaceOrigin(**(base | changes))


def test_an_unchanged_origin_is_not_stale():
    held = space()
    held._origin = loaded()

    assert held.is_stale(loaded()) is False
    assert held.staleness(loaded()) == ()


def test_a_curated_edge_shows_as_a_RESEAL_and_not_as_a_new_build():
    """The reason the seals are compared and not the label alone. `curate_dictionary.py approve`
    writes cells into R under the SAME build and re-seals — so a check that watched only the label
    would go on serving a base the Captain had already corrected by hand."""
    held = space()
    held._origin = loaded()
    approved = loaded(seals=(("dictionary_base_distribution", "d1"),
                             ("dictionary_base_relations", "r2")))

    assert held.is_stale(approved)
    assert held.staleness(approved) == ("dictionary_base_relations reseal r1 -> r2",)


def test_a_ruling_shows_even_when_no_cell_moved():
    """The staleness source that would have been missed, and it happened the day this was written:
    the NEAR floor moved +0.27 -> +0.28, every verdict in the space changed, and every matrix stayed
    byte-identical."""
    held = space()
    held._origin = loaded()

    assert held.staleness(loaded(policy_version=11)) == ("policy v10 -> v11",)


def test_a_new_build_beside_the_old_one_shows_as_a_build():
    held = space()
    held._origin = loaded()

    assert held.staleness(loaded(build="ffffffffffff"))[0].startswith("build ")


def test_a_space_with_no_origin_says_so_rather_than_claiming_to_be_current():
    """«I cannot know» and «I am current» are different answers. A space built from a fixture has no
    provenance and must not pretend to one."""
    held = space()

    assert held.origin is None
    assert held.is_stale(loaded()) is False
    assert held.staleness(loaded()) == ()


def test_the_reason_is_reported_and_not_just_the_verdict():
    """A phase deciding to spend seven seconds deserves the reason: «stale» in a log explains
    nothing to whoever reads it later."""
    held = space()
    held._origin = loaded()
    everything = loaded(build="other", policy_version=11,
                        seals=(("dictionary_base_relations", "r9"),))

    moved = held.staleness(everything)
    assert len(moved) == 4, "the build, both seals and the policy"
    assert any("build" in line for line in moved)
    assert any("reseal" in line for line in moved)
    assert any("policy" in line for line in moved)
