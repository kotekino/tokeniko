"""The tk1 traps: rows come back as rows, and a delete that removes nothing cannot happen quietly."""

from datetime import datetime, timezone

import pytest

from tk2.core.write_class import WriteClassViolation
from tk2.datatier import traps
from tests.models import TKb, TLogic, TParam, TSeries

pytestmark = pytest.mark.mongo


# ------------------------------------------------------------------------------------------------
# trap 1 — the query that looks like a row
# ------------------------------------------------------------------------------------------------


def test_get_returns_a_row_not_a_query(clean_db):
    written = traps.insert(TKb(text="hello"))
    fetched = traps.get(TKb, written.id)
    assert isinstance(fetched, TKb)
    assert fetched.text == "hello"


def test_get_returns_none_for_a_missing_row(clean_db):
    from bunnet import PydanticObjectId

    assert traps.get(TKb, PydanticObjectId()) is None


def test_find_one_returns_a_row_not_a_query(clean_db):
    traps.insert(TKb(text="findme"))
    found = traps.find_one(TKb, TKb.text == "findme")
    assert isinstance(found, TKb)


def test_find_returns_a_list_not_a_cursor(clean_db):
    for i in range(3):
        traps.insert(TKb(text=f"row-{i}"))
    rows = traps.find(TKb)
    assert isinstance(rows, list) and len(rows) == 3


def test_find_takes_limit_and_sort(clean_db):
    for i in range(5):
        traps.insert(TKb(text=f"row-{i}"))
    assert len(traps.find(TKb, limit=2)) == 2
    descending = traps.find(TKb, sort=-TKb.text)
    assert descending[0].text == "row-4"


def test_count_and_exists(clean_db):
    traps.insert(TKb(text="a"))
    traps.insert(TKb(text="b"))
    assert traps.count(TKb) == 2
    assert traps.count(TKb, TKb.text == "a") == 1
    assert traps.exists(TKb, TKb.text == "a") is True
    assert traps.exists(TKb, TKb.text == "zzz") is False


def test_find_all_reads_the_whole_collection(clean_db):
    for i in range(4):
        traps.insert(TKb(text=str(i)))
    assert len(traps.find_all(TKb)) == 4


# ------------------------------------------------------------------------------------------------
# trap 2 — the delete that removes nothing
# ------------------------------------------------------------------------------------------------


def test_delete_many_actually_deletes_and_reports_the_count(clean_db):
    """The tk1 trap in one line: `.find().delete()` without `.run()` removes nothing and says
    nothing. Here the rows go AND the caller is told how many."""
    for i in range(3):
        traps.insert(TKb(text="doomed"))
    traps.insert(TKb(text="spared"))

    removed = traps.delete_many(TKb, TKb.text == "doomed")

    assert removed == 3
    assert traps.count(TKb) == 1


def test_delete_many_returns_zero_rather_than_pretending(clean_db):
    """A caller who can see 0 can notice. That is the entire difference from the trap."""
    assert traps.delete_many(TKb, TKb.text == "never-existed") == 0


def test_delete_many_refuses_a_timeseries_model(clean_db):
    """On timeseries the ODM path deletes nothing and does not complain — the exact failure that
    must not be reachable from here."""
    with pytest.raises(WriteClassViolation) as excinfo:
        traps.delete_many(TSeries)
    assert "delete_timeseries_rows" in str(excinfo.value)


def test_timeseries_rows_delete_through_raw_pymongo(clean_db):
    now = datetime.now(timezone.utc)
    for i in range(3):
        traps.insert(TSeries(ts=now, value=float(i)))
    assert traps.count(TSeries) == 3

    removed = traps.delete_timeseries_rows(TSeries, {})

    assert removed == 3
    assert traps.count(TSeries) == 0


def test_the_raw_delete_refuses_a_normal_collection(clean_db):
    """Symmetric refusal: each function turns away the other's case, so the workaround stays where
    it is needed instead of spreading into normal code."""
    with pytest.raises(WriteClassViolation) as excinfo:
        traps.delete_timeseries_rows(TKb, {})
    assert "delete_many" in str(excinfo.value)


def test_is_timeseries_reads_the_model(clean_db):
    assert traps.is_timeseries(TSeries) is True
    assert traps.is_timeseries(TKb) is False


# ------------------------------------------------------------------------------------------------
# the write-class, asked every time
# ------------------------------------------------------------------------------------------------


def test_writing_a_param_through_the_tier_is_refused(clean_db):
    with pytest.raises(WriteClassViolation):
        traps.insert(TParam(key="k", value=1))


def test_saving_a_logic_row_through_the_tier_is_refused(clean_db):
    with pytest.raises(WriteClassViolation):
        traps.save(TLogic(name="n", rule="r"))


def test_deleting_r_class_rows_through_the_tier_is_refused(clean_db):
    with pytest.raises(WriteClassViolation):
        traps.delete_many(TParam)


def test_reading_r_class_rows_is_fine(clean_db, migration_writer):
    """Read-only means read-ONLY, not unreachable. The body reads these constantly."""
    migration_writer.insert(TParam, {"key": "a", "value": 1})
    assert traps.count(TParam) == 1
    assert traps.find_one(TParam, TParam.key == "a").value == 1
