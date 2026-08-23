"""The document bases: the declaration is unforgettable, and it is not a column."""

import pytest

from tk2.core.documents import KbDocument, LogicDocument, ParamDocument, TkDocument
from tk2.core.write_class import WriteClass


def test_each_base_declares_its_class():
    assert KbDocument.write_class is WriteClass.KB
    assert ParamDocument.write_class is WriteClass.PARAM
    assert LogicDocument.write_class is WriteClass.LOGIC


def test_a_model_inherits_the_declaration_from_its_base():
    class HeartLevelish(KbDocument):
        sphere: str

        class Settings:
            name = "test_heart_levelish"

    assert HeartLevelish.write_class is WriteClass.KB


def test_declaring_nothing_fails_at_import_time():
    """The check that makes the seam real. A model that forgot its class must not survive to the
    first write, where the failure would be a runtime surprise on a live db instead of a red import
    in front of whoever wrote it."""
    with pytest.raises(TypeError) as excinfo:

        class Undeclared(TkDocument):
            class Settings:
                name = "test_undeclared"

    message = str(excinfo.value)
    assert "write-class" in message
    # ...and it must name the way out, all three of them.
    assert "KbDocument" in message and "ParamDocument" in message and "LogicDocument" in message


def test_the_write_class_is_not_a_field():
    """It is a property of the COLLECTION, not a column repeated on every row — a per-row copy could
    disagree with its own collection, and then the seam has two answers."""

    class Thing(KbDocument):
        sphere: str

        class Settings:
            name = "test_thing_fields"

    assert "write_class" not in Thing.model_fields
    assert set(Thing.model_fields) == {"id", "revision_id", "sphere"}


def test_the_bases_themselves_are_exempt():
    """The three bases exist to be inherited from; they are not collections, so the declaration
    check must not fire while they are being defined (it would make the module unimportable)."""
    for base in (KbDocument, ParamDocument, LogicDocument):
        assert base.__dict__.get("__tk_abstract__") is True


def test_an_intermediate_base_can_be_abstract_too():
    """A shared parent for a family of collections is legal, and stays out of the check by saying
    so — the abstract flag is read off the class's own dict, never inherited."""

    class HeartDocBase(KbDocument):
        __tk_abstract__ = True
        sphere: str

    class Levels(HeartDocBase):
        class Settings:
            name = "test_levels"

    assert Levels.write_class is WriteClass.KB
    # the flag did NOT ride down to the concrete model
    assert Levels.__dict__.get("__tk_abstract__") is None
