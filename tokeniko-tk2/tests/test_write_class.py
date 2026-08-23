"""The write-class: three classes, one of them writable, and a refusal that is loud."""

import pytest

from tk2.core import WriteClass, WriteClassViolation, assert_writable
from tk2.core.documents import KbDocument, LogicDocument, ParamDocument


def test_the_three_classes_and_nothing_else():
    """The set is closed. A fourth write-class would be a fourth kind of row, and the seam only
    holds because there are exactly three."""
    assert {wc.value for wc in WriteClass} == {"kb", "param", "logic"}


def test_only_kb_is_writable():
    assert WriteClass.KB.writable is True
    assert WriteClass.PARAM.writable is False
    assert WriteClass.LOGIC.writable is False


def test_value_is_the_string_itself():
    """A str enum so a row carries the value verbatim and a mongo query reads it as itself."""
    assert WriteClass.KB == "kb"
    assert f"{WriteClass.PARAM.value}" == "param"


class _AKbThing(KbDocument):
    class Settings:
        name = "test_kb_thing"


class _AParamThing(ParamDocument):
    class Settings:
        name = "test_param_thing"


class _ALogicThing(LogicDocument):
    class Settings:
        name = "test_logic_thing"


def test_assert_writable_lets_kb_through():
    assert_writable(_AKbThing) is None


@pytest.mark.parametrize("model", [_AParamThing, _ALogicThing])
def test_assert_writable_refuses_the_r_classes(model):
    with pytest.raises(WriteClassViolation) as excinfo:
        assert_writable(model)
    # The refusal has to say what to do instead, or the next person reaches for a flag.
    assert "migration" in str(excinfo.value)


def test_the_refusal_is_raised_not_returned():
    """The tk1 trap this exists to not repeat: `.find().delete()` without `.run()` is a silent
    no-op — a write that does nothing and says nothing. A refusal that returned False would be the
    same failure wearing a different hat."""
    with pytest.raises(WriteClassViolation):
        assert_writable(_AParamThing)
