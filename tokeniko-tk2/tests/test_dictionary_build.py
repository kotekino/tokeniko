"""THE ASSEMBLY — closure to dimensions to R, on the handcrafted world.

Three commands in the prototype, one call here, and the reason is the manifest: a base is ONE
measurement under ONE declared policy, and three commands each reading a config file are three
chances for a build to be assembled out of parts nobody measured together. What this file holds to
account is that the three steps really do share one policy and one key space — the property T4 will
lean on when D lands beside R over the same dimensions.
"""

import pytest

from tests.lexicon_fixture import (
    LEXICON,
    FixtureGlossProvider,
    FixtureRelationProvider,
)
from tests.seed import relation_policy
from tk2.dictionary import build, glosses
from tk2.dictionary.config import BarPair, ClosurePolicy, DictionaryConfig


class World(FixtureGlossProvider):
    """The sixteen-word world, answering the relation seam as well.

    One object because it is one resource: two would be two chances for the membership and the
    geometry to be measured against different WordNets, which is exactly what `build_base` takes a
    single provider to prevent.
    """

    def __init__(self, edges=None, **kwargs):
        super().__init__(**kwargs)
        self._relations = FixtureRelationProvider(
            senses={word: (f"{word}.{pos}.01",)
                    for word in self.lexicon()
                    for pos in self.parts_of_speech(word)},
            edges=edges or {},
        )

    def senses_of_key(self, key):
        word, _, pos = key.rpartition(".")
        return (f"{word}.{pos}.01",) if pos in self.parts_of_speech(word) else ()

    def relations_of_key(self, key):
        return self._relations.relations_of_key(key)

    def relations(self):
        return self._relations.relations()


def config(relations=None, **closure):
    """A whole declared policy for the fixture world. Stated, never defaulted — since T4b there is
    no default anywhere in code to fall back on."""
    cuts = {"max_depth": 2, "max_size": 1000, "senses": "primary"} | closure
    return DictionaryConfig(
        closure=ClosurePolicy(**cuts),
        declared_seeds=("sleep", "leave"),
        bar=(BarPair("sleep.v", "bed.n", "NEAR", "the fixture's own nearness"),),
        relations=relation_policy() if relations is None else relations,
    )


def test_the_three_steps_share_one_policy_and_one_key_space():
    """The whole point of the single call. The dimensions R is square over are the ones the closure's
    words earn — not a list assembled beside them."""
    world = World(edges={"sleep.v": {"entails": frozenset({"rest.v.01"})}})
    built = build.build_base(config(), world)

    assert set(built.words) <= set(LEXICON)
    assert built.dimensions == tuple(glosses.dimensions_of(built.words, world))
    assert built.relational.keys == built.dimensions
    assert built.relational.cell("sleep.v", "rest.v").relation == "entails"


def test_the_bars_own_words_are_in_the_base_it_will_be_measured_against():
    """Requirement 12, at the assembly: a subset that cannot score its own bar is not a test. The
    bar's words are seeds by construction, so the closure cannot leave them out."""
    built = build.build_base(config(), World())
    assert "bed" in built.words and "sleep" in built.words


def test_the_closures_own_account_of_itself_survives_into_the_build():
    """A build's manifest is not only its counts: where the closure stopped, and what sits one ring
    past the cut, is what a later reader rules on."""
    built = build.build_base(config(max_depth=1), World())
    assert built.closure.stopped == "depth"
    assert built.one_ring_past
    assert built.counts()["one_ring_past"] == len(built.one_ring_past)
    assert built.counts()["keys"] == len(built.dimensions)


def test_a_policy_with_no_weights_builds_nothing_rather_than_something_smaller():
    """R without weights is not a sparser R — it is no matrix at all. A default here would be R's
    weights back in code with extra steps."""
    with pytest.raises(build.PolicyIncomplete):
        build.build_base(
            DictionaryConfig(
                closure=ClosurePolicy(max_depth=1, max_size=10, senses="primary"),
                declared_seeds=("sleep",),
                bar=(BarPair("sleep.v", "bed.n", "NEAR", "why"),),
            ),
            World(),
        )
