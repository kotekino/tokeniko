"""The sense layer — the dictionary's second floor, on the handcrafted world and on the resource.

E1c's ruling in one line: THE BASE IS THE FRAME, THE SENSES ARE THE CONTENT. What is held to account
here is that the layer rides on the base rather than beside it, that it reads through the same seams
the base does, and that a sense carries the relational evidence a POS key structurally cannot.
"""

import pytest

from tests.lexicon_fixture import LEXICON, FixtureGlossProvider
from tests.seed import closed_class_forms, distribution_policy, reading_policy, relation_policy
from tk2.dictionary import build, keys, senses
from tk2.dictionary.config import BarPair, ClosurePolicy, DictionaryConfig


def config():
    return DictionaryConfig(
        closure=ClosurePolicy(max_depth=2, max_size=25_000, senses="primary"),
        declared_seeds=("sleep", "leave"),
        bar=(BarPair("sleep.v", "bed.n", "NEAR", "the fixture's own nearness"),),
        relations=relation_policy(),
        distribution=distribution_policy(),
        reading=reading_policy(),
    )


# ------------------------------------------------------------------------------------------------
# the shape — what makes it a layer and not a second matrix
# ------------------------------------------------------------------------------------------------


@pytest.mark.wordnet
def test_a_sense_is_placed_against_BASE_dimensions_and_never_against_other_senses():
    """The architecture guard, as a test rather than as a comment. 120,475 senses against 4,555
    dimensions is half a billion possible cells; senses against senses would be 14.5 BILLION, and
    the shape of a row is what makes that impossible to write by accident."""
    cfg, provider, dimensions = _real_base()
    placed = senses.build(dimensions, ["bank"], provider, cfg, closed=closed_class_forms())

    columns = {cell.column for sense in placed for cell in sense.distribution + sense.relations}
    assert columns <= set(dimensions)
    assert all(keys.is_base_key(column) for column in columns)
    assert not any(keys.is_sense_key(column) for column in columns)


@pytest.mark.wordnet
def test_a_sense_truncates_to_the_dimension_it_is_a_reading_of():
    """The whole reason the key is word-anchored: `bank.n.02` is a reading of `bank.n`, and a key
    that did not truncate would need a lookup table to say so."""
    cfg, provider, dimensions = _real_base()
    placed = senses.build(dimensions, ["bank"], provider, cfg, closed=closed_class_forms())

    for sense in placed:
        assert keys.base_of(sense.key) == sense.base
        assert sense.key.startswith(sense.base + ".")


# ------------------------------------------------------------------------------------------------
# the evidence the base cannot hold
# ------------------------------------------------------------------------------------------------


@pytest.mark.wordnet
def test_two_senses_of_one_word_reach_different_dimensions():
    """E1c's reason for existing, on the clearest pair in the language. WordNet states relations per
    SYNSET, and collapsing synsets to POS keys is what lost them: `bank.n.01` is a slope and
    `bank.n.02` is a financial institution, and `bank.n` is both at once and so is neither."""
    cfg, provider, dimensions = _real_base()
    placed = {s.key: s for s in senses.build(dimensions, ["bank"], provider, cfg,
                                             closed=closed_class_forms())}

    slope = {c.column for c in placed["bank.n.01"].relations}
    money = {c.column for c in placed["bank.n.02"].relations}

    assert slope and money
    assert not slope & money, "the two readings must not resolve to the same evidence"
    assert "slope.n" in slope
    assert "institution.n" in money


@pytest.mark.wordnet
def test_the_rot_that_ran_through_E1_stops_being_one():
    """`small.n` reads «the slender part of the back» because a dimension takes WordNet's FIRST
    synset, and that was called a defect all epic. It is not a defect once the other readings have
    somewhere to live: the dimension stays the frame, and its senses carry what the word means.

    Checked on the adjective, where the payoff is visible rather than merely argued: `small.a` is
    one dimension with TEN readings, and the first of them states the opposition to `large` that
    the dimension itself — every reading at once — cannot state cleanly."""
    cfg, provider, dimensions = _real_base()
    placed = [s for s in senses.build(dimensions, ["small"], provider, cfg,
                                      closed=closed_class_forms()) if s.base == "small.a"]

    assert len(placed) == 10, "small.a is one dimension and ten readings"
    first = placed[0]
    assert "large.a" in {cell.column for cell in first.relations}


# ------------------------------------------------------------------------------------------------
# the seams — a second reduction would re-open every ruling quietly
# ------------------------------------------------------------------------------------------------


def test_the_gloss_is_reduced_through_the_SAME_seam_the_base_uses():
    """Requirement 21's repair, the stop-list ruling, the name refusal and the structure filter all
    live in `glosses.lexicon_words_in`. A layer with its own tokeniser would re-open all four, and
    the two builds would differ with no fingerprint able to say why."""
    cfg, world, dimensions = _fixture_world()
    placed = senses.build(dimensions, sorted(LEXICON), world, cfg, closed=closed_class_forms())

    named = {cell.evidence for sense in placed for cell in sense.distribution}
    assert named, "the fixture world has to place something or this proves nothing"
    # `me`, `not` and `you` are closed-class forms: compiled, never defined — so no sense may be
    # placed BY them, exactly as no base dimension may be.
    assert not named & closed_class_forms()


def test_a_sense_never_names_its_own_word():
    """«land: the land on which real estate is located» states nothing about two concepts, and
    counting it would give every sense of a word a free cell on its own base key."""
    cfg, world, dimensions = _fixture_world()
    placed = senses.build(dimensions, sorted(LEXICON), world, cfg, closed=closed_class_forms())

    for sense in placed:
        own = keys.word_of(sense.base)
        assert own not in {cell.evidence for cell in sense.distribution}


# ------------------------------------------------------------------------------------------------
# the honest failures — an unplaced sense is a fact, not a fault
# ------------------------------------------------------------------------------------------------


@pytest.mark.wordnet
def test_an_unplaced_sense_says_so_rather_than_pretending():
    """Measured before the layer was built: 5.3% of senses name no base word and 54.1% reach none by
    relation. A sense the geometry cannot see is one the station will have to ABSTAIN on, and the
    count is what makes that predictable instead of surprising."""
    cfg, provider, dimensions = _real_base()
    placed = senses.build(dimensions, ["bank", "cytokinin"], provider, cfg,
                          closed=closed_class_forms())

    reported = senses.stats(placed)
    assert reported["senses"] == len(placed)
    assert reported["placed"] + reported["unplaced"] == reported["senses"]
    assert all(s.is_placed == bool(s.distribution or s.relations) for s in placed)


def test_a_policy_that_cannot_place_a_sense_refuses_rather_than_inventing_one():
    """Same law as everywhere else in this package: a build that would be CHANGED by an undeclared
    value is refused, never quietly given one."""
    from dataclasses import replace

    cfg, world, dimensions = _fixture_world()

    with pytest.raises(senses.PolicyIncomplete):
        senses.build(dimensions, ["bed"], world, replace(cfg, distribution=None))
    with pytest.raises(senses.PolicyIncomplete):
        senses.build(dimensions, ["bed"], world, replace(cfg, relations=None))


# ------------------------------------------------------------------------------------------------
# the fingerprint — what the seal vouches for
# ------------------------------------------------------------------------------------------------


def test_the_layers_fingerprint_is_its_content_and_not_its_order():
    """The layer has no canonical row order, so a hash that depended on one would fail the first
    time a read sorted differently — which is exactly when a verifier is most needed."""
    cfg, world, dimensions = _fixture_world()
    placed = senses.build(dimensions, sorted(LEXICON), world, cfg, closed=closed_class_forms())

    assert senses.fingerprint(placed) == senses.fingerprint(list(reversed(placed)))
    assert senses.fingerprint(placed) != senses.fingerprint(placed[:-1])


def _fixture_world():
    """The handcrafted world and ITS dimensions — computed directly rather than through a full base
    build, because a pure test of the sense layer has no business needing R built beside it."""
    from tk2.dictionary import glosses

    world = FixtureGlossProvider()
    dimensions = glosses.dimensions_of(sorted(LEXICON), world)
    return config(), world, dimensions


def _real_base():
    """The standing policy over the real resource — the only way to test a claim about WordNet."""
    from tk2.datatier.policy_source import standing_bar, standing_policy
    from tk2.dictionary import policy
    from tk2.dictionary.wordnet import WordNetProvider, wordnet_lexicon

    rows, _ = standing_policy(None)
    _bar, bar_rows, _source = standing_bar(None)
    cfg = policy.config_from_rows(rows, bar_rows)
    provider = WordNetProvider(wordnet_lexicon(), lemma_scope=cfg.relations.lemma_scope)
    built = build.build_base(cfg, provider, closed_forms=closed_class_forms())
    return cfg, provider, built.dimensions
