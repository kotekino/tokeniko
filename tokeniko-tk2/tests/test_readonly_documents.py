"""Defense in depth: the r-classes refuse their own ODM writers, with no datatier involved.

The Captain's ruling of 2026-08-23. The datatier's `assert_writable` is a door, and a door guards
only what walks through it — a caller holding the model can call `.save()` and never pass the
datatier at all.
"""

import pytest
from bunnet import Document

from tk2.core.documents import KbDocument, LogicDocument, ParamDocument, _ReadOnlyDocument
from tk2.core.write_class import WriteClassViolation

# The public write surface of bunnet's Document, audited by hand against bunnet 1.3.0. Every one of
# these must be closed on an r-class model: a single method left open is the whole lock.
WRITE_METHODS = (
    "insert",
    "insert_one",
    "insert_many",
    "save",
    "save_changes",
    "replace",
    "replace_many",
    "update",
    "update_all",
    "set",
    "inc",
    "delete",
    "delete_all",
)


@pytest.mark.parametrize("method", WRITE_METHODS)
def test_the_audited_list_still_matches_bunnet(method):
    """If a bunnet upgrade renames or removes a writer, this fails LOUDLY rather than leaving the
    audit quietly describing a version we no longer run."""
    assert hasattr(Document, method), f"bunnet's Document no longer has {method}() — re-audit"


@pytest.mark.parametrize("base", [ParamDocument, LogicDocument])
@pytest.mark.parametrize("method", WRITE_METHODS)
def test_every_writer_is_closed_on_the_r_classes(base, method):
    owner = getattr(base, method).__qualname__
    assert owner.startswith("_ReadOnlyDocument"), f"{base.__name__}.{method}() is not closed"


@pytest.mark.parametrize("method", WRITE_METHODS)
def test_the_kb_class_keeps_every_writer_open(method):
    """The lock must be on the r-classes and nowhere else — the body writes kb, and a kb model that
    inherited the refusals would make the knowledge base unwritable."""
    assert not getattr(KbDocument, method).__qualname__.startswith("_ReadOnlyDocument")


def test_kb_does_not_inherit_the_read_only_floor():
    assert not issubclass(KbDocument, _ReadOnlyDocument)
    assert issubclass(ParamDocument, _ReadOnlyDocument)
    assert issubclass(LogicDocument, _ReadOnlyDocument)


class _AParam(ParamDocument):
    key: str
    value: int = 0

    class Settings:
        name = "test_ro_param"


class _ALogic(LogicDocument):
    rule: str

    class Settings:
        name = "test_ro_logic"


@pytest.mark.parametrize("model", [_AParam, _ALogic])
def test_class_writers_refuse_without_touching_mongo(model):
    """These raise before any collection is consulted — which is why they are testable with no
    database at all, and why a misconfigured process cannot get a write in edgeways."""
    for method in ("insert_one", "insert_many", "delete_all", "update_all", "replace_many"):
        with pytest.raises(WriteClassViolation):
            getattr(model, method)({"key": "x"})


def test_the_refusal_says_what_to_do_instead():
    with pytest.raises(WriteClassViolation) as excinfo:
        _AParam.delete_all()
    message = str(excinfo.value)
    assert "migration" in message
    assert "slow tick" in message


def test_the_refusal_names_the_method_and_the_class():
    with pytest.raises(WriteClassViolation) as excinfo:
        _ALogic.insert_one({})
    message = str(excinfo.value)
    assert "_ALogic" in message and "insert_one" in message and "logic" in message
