"""The heart's anatomy as rows: the reader, and the two validation seams.

No database here — `HeartAnatomy` takes rows, not the r-cache, precisely so these questions are
answerable without one.
"""

import pytest

from tk2.core.models import AnatomyIncoherent, HeartAnatomy, HeartAnatomyDoc, UnknownPole
from tk2.datatier.migration_writer import shape_of
from tests.anatomy import canonical_anatomy


def _anatomy(rows: list[dict]) -> HeartAnatomy:
    """Rows → validated shapes → reader, without booting the ODM."""
    shape = shape_of(HeartAnatomyDoc)
    return HeartAnatomy([shape.model_validate(row) for row in rows])


@pytest.fixture
def heart() -> HeartAnatomy:
    return _anatomy(canonical_anatomy())


# ------------------------------------------------------------------------------------------------
# the requirements' heart is expressible as rows
# ------------------------------------------------------------------------------------------------


def test_the_canonical_anatomy_is_coherent(heart):
    heart.check_coherent()


def test_six_spheres_twelve_poles_three_spikes(heart):
    assert len(heart.spheres()) == 6
    assert len(heart.poles()) == 15
    assert len(heart.spikes()) == 3


def test_every_sphere_is_a_pair(heart):
    for sphere in heart.spheres():
        assert len(heart.poles_of(sphere)) == 2


def test_opposition_is_reciprocal(heart):
    for pole in heart.poles():
        opposite = heart.opposite_of(pole)
        if opposite is not None:
            assert heart.opposite_of(opposite) == pole


def test_the_spikes_have_triggers_and_no_opposite(heart):
    """Surprise is not a sphere: it fires and decays, and has no pole to sit against."""
    for spike in heart.spikes():
        assert heart.opposite_of(spike) is None
        assert heart.sphere_of(spike) is None
        assert heart.trigger_of(spike)
    assert set(heart.spikes()) == {"startle", "disillusion", "serendipity"}


def test_love_and_hate_target_people_including_self(heart):
    """Heart req. 7's exact phrasing — collapsing it to one target would lose self-love."""
    assert set(heart.targets_of("love")) == {"self", "person"}
    assert set(heart.targets_of("hate")) == {"self", "person"}


def test_curiosity_targets_ideas(heart):
    assert heart.targets_of("curiosity") == ["idea"]


def test_a_pole_knows_its_sphere(heart):
    assert heart.sphere_of("joy") == "joy-sadness"
    assert heart.is_spike("joy") is False
    assert heart.is_spike("startle") is True


# ------------------------------------------------------------------------------------------------
# the write-time seam
# ------------------------------------------------------------------------------------------------


def test_an_unknown_pole_is_refused(heart):
    """THE check the ruling asks for. It lives here — not in a pydantic validator — because the
    legal set is in the DATABASE, and a field validator could only reach it through global state."""
    with pytest.raises(UnknownPole) as excinfo:
        heart.validate_pole("smugness")
    message = str(excinfo.value)
    assert "smugness" in message
    assert "migration" in message


def test_a_known_pole_passes_through(heart):
    assert heart.validate_pole("joy") == "joy"


def test_a_pole_cannot_attach_to_a_kind_it_does_not_target(heart):
    """Curiosity toward a person is not a stricter rule — it is a different feeling than the
    anatomy describes."""
    assert heart.validate_target("love", "person") == "person"
    with pytest.raises(UnknownPole):
        heart.validate_target("curiosity", "person")


def test_the_refusal_lists_what_is_known(heart):
    with pytest.raises(UnknownPole) as excinfo:
        heart.validate_pole("nope")
    assert "joy" in str(excinfo.value)


def test_an_empty_anatomy_says_so_rather_than_matching_nothing():
    empty = HeartAnatomy([])
    with pytest.raises(UnknownPole) as excinfo:
        empty.validate_pole("joy")
    assert "empty" in str(excinfo.value)


# ------------------------------------------------------------------------------------------------
# the boot-time seam — every rule is one a migration could get wrong
# ------------------------------------------------------------------------------------------------


def test_an_empty_anatomy_is_incoherent():
    with pytest.raises(AnatomyIncoherent):
        HeartAnatomy([]).check_coherent()


def test_a_sphere_pole_without_an_opposite_is_refused():
    with pytest.raises(AnatomyIncoherent) as excinfo:
        _anatomy([{"pole": "joy", "sphere": "joy-sadness", "targets": ["self"]}]).check_coherent()
    assert "PAIR" in str(excinfo.value)


def test_an_opposite_that_does_not_exist_is_refused():
    rows = [{"pole": "joy", "sphere": "joy-sadness", "opposite": "ghost", "targets": ["self"]}]
    with pytest.raises(AnatomyIncoherent) as excinfo:
        _anatomy(rows).check_coherent()
    assert "does not define" in str(excinfo.value)


def test_opposition_that_is_not_reciprocal_is_refused():
    rows = [
        {"pole": "joy", "sphere": "s", "opposite": "sadness", "targets": ["self"]},
        {"pole": "sadness", "sphere": "s", "opposite": "joy", "targets": ["self"]},
        {"pole": "rage", "sphere": "t", "opposite": "joy", "targets": ["self"]},
    ]
    with pytest.raises(AnatomyIncoherent):
        _anatomy(rows).check_coherent()


def test_a_sphere_with_three_poles_is_refused():
    rows = [
        {"pole": "a", "sphere": "s", "opposite": "b", "targets": ["self"]},
        {"pole": "b", "sphere": "s", "opposite": "a", "targets": ["self"]},
        {"pole": "c", "sphere": "s", "opposite": "b", "targets": ["self"]},
    ]
    with pytest.raises(AnatomyIncoherent):
        _anatomy(rows).check_coherent()


def test_a_spike_carrying_an_opposite_is_refused():
    rows = [{"pole": "startle", "opposite": "calm", "targets": ["self"], "trigger": "noise"}]
    with pytest.raises(AnatomyIncoherent) as excinfo:
        _anatomy(rows).check_coherent()
    assert "no opposite" in str(excinfo.value)


def test_a_spike_without_a_trigger_is_refused():
    """An event signal with no event is a level wearing the wrong hat."""
    with pytest.raises(AnatomyIncoherent) as excinfo:
        _anatomy([{"pole": "startle", "targets": ["self"]}]).check_coherent()
    assert "trigger" in str(excinfo.value)


def test_a_sphere_pole_carrying_a_trigger_is_refused():
    rows = [
        {"pole": "a", "sphere": "s", "opposite": "b", "targets": ["self"], "trigger": "noise"},
        {"pole": "b", "sphere": "s", "opposite": "a", "targets": ["self"]},
    ]
    with pytest.raises(AnatomyIncoherent) as excinfo:
        _anatomy(rows).check_coherent()
    assert "Triggers belong to spikes" in str(excinfo.value)


def test_a_pole_must_target_something():
    """A level that attaches to nothing could never be written against anything."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        _anatomy([{"pole": "joy", "sphere": "s", "opposite": "x", "targets": []}])
