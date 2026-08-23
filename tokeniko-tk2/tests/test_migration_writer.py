"""The migration door: validated by pydantic, written by pymongo, and the only way into an r-class."""

import pytest
from pydantic import ValidationError

from tk2.datatier.migration_writer import MigrationWriter, shape_of
from tests.models import TKb, TLogic, TParam

# ------------------------------------------------------------------------------------------------
# the derived validator — no ODM needed
# ------------------------------------------------------------------------------------------------


def test_the_shape_drops_the_odm_bookkeeping():
    """`id` is mongo's `_id`, which the server assigns; `revision_id` belongs to the ODM's
    optimistic locking, which a migration is not participating in."""
    fields = set(shape_of(TParam).model_fields)
    assert fields == {"key", "value"}
    assert "id" not in fields and "revision_id" not in fields


def test_the_shape_keeps_the_models_constraints():
    """Including the mixins' — a shape that validated less than the model would let a migration
    write a row the body cannot read back."""
    shape = shape_of(TKb)
    assert set(shape.model_fields) == {"text", "created_at"}
    with pytest.raises(ValidationError):
        shape.model_validate({})


def test_the_shape_needs_no_bunnet_init():
    """The point of deriving a twin: constructing a real bunnet Document requires an initialised
    collection, and a migration is a script against a database, not an app with an ODM booted."""
    assert shape_of(TLogic).model_validate({"name": "n", "rule": "r"}).name == "n"


def test_the_shape_is_built_once_per_model():
    assert shape_of(TParam) is shape_of(TParam)


def test_defaults_are_materialised_into_the_row():
    """A stored row should be complete and readable by someone who has never seen the model."""
    stored = shape_of(TKb).model_validate({"text": "x"}).model_dump()
    assert "created_at" in stored and isinstance(stored["created_at"], int)


# ------------------------------------------------------------------------------------------------
# writing
# ------------------------------------------------------------------------------------------------

pytestmark_live = pytest.mark.mongo


@pytest.mark.mongo
def test_it_writes_a_param_row_the_odm_refuses(migration_writer):
    """THE two-door property. `TParam` refuses every ODM writer it has; this door is not that
    door — it does not use the ODM at all."""
    from tk2.core.write_class import WriteClassViolation

    with pytest.raises(WriteClassViolation):
        TParam.insert_one({"key": "k", "value": 1})

    new_id = migration_writer.insert(TParam, {"key": "k", "value": 1})

    assert new_id is not None
    assert migration_writer.collection(TParam).count_documents({}) == 1


@pytest.mark.mongo
def test_it_validates_before_writing(migration_writer):
    with pytest.raises(ValidationError):
        migration_writer.insert(TLogic, {"name": "no-rule-field"})
    assert migration_writer.collection(TLogic).count_documents({}) == 0


@pytest.mark.mongo
def test_a_bad_row_late_in_a_batch_writes_nothing(migration_writer):
    """Every row is validated before any row is written, so a broken migration does not leave the
    first half of a batch behind for someone to reconcile by hand."""
    rows = [{"name": "a", "rule": "r"}, {"name": "b", "rule": "r"}, {"name": "c"}]

    with pytest.raises(ValidationError):
        migration_writer.insert_many(TLogic, rows)

    assert migration_writer.collection(TLogic).count_documents({}) == 0


@pytest.mark.mongo
def test_insert_many_writes_them_all(migration_writer):
    ids = migration_writer.insert_many(
        TLogic, [{"name": f"r{i}", "rule": "x"} for i in range(4)]
    )
    assert len(ids) == 4
    assert migration_writer.collection(TLogic).count_documents({}) == 4


@pytest.mark.mongo
def test_insert_many_of_nothing_is_not_an_error(migration_writer):
    assert migration_writer.insert_many(TLogic, []) == []


@pytest.mark.mongo
def test_upsert_creates_then_replaces(migration_writer):
    created = migration_writer.upsert(TParam, {"key": "k"}, {"key": "k", "value": 1})
    assert created is True

    created_again = migration_writer.upsert(TParam, {"key": "k"}, {"key": "k", "value": 2})
    assert created_again is False

    assert migration_writer.collection(TParam).count_documents({}) == 1
    assert migration_writer.collection(TParam).find_one({"key": "k"})["value"] == 2


@pytest.mark.mongo
def test_upsert_validates_too(migration_writer):
    with pytest.raises(ValidationError):
        migration_writer.upsert(TLogic, {"name": "a"}, {"name": "a"})


@pytest.mark.mongo
def test_delete_reports_how_many_went(migration_writer):
    migration_writer.insert_many(TParam, [{"key": f"k{i}", "value": i} for i in range(3)])
    assert migration_writer.delete(TParam, {"key": "k1"}) == 1
    assert migration_writer.delete(TParam, {"key": "nope"}) == 0
    assert migration_writer.collection(TParam).count_documents({}) == 2


@pytest.mark.mongo
def test_the_collection_name_comes_off_the_model(migration_writer):
    """So a migration and the body can never disagree about where the rows live."""
    assert migration_writer.collection(TParam).name == TParam.Settings.name


@pytest.mark.mongo
def test_it_writes_kb_collections_too(migration_writer):
    """Migration 0001 creates the WORLD, not only the parameters — seeding kb rows is a migration's
    job as much as seeding params."""
    migration_writer.insert(TKb, {"text": "seeded"})
    assert migration_writer.collection(TKb).count_documents({}) == 1


@pytest.mark.mongo
def test_it_holds_the_database_it_was_given(clean_db):
    """It takes the handle rather than reaching for one — the guard has already spoken by the time
    this object exists."""
    writer = MigrationWriter(clean_db)
    assert writer.database.name == clean_db.name
