"""THE TK1 TRAPS, WRAPPED AWAY (datatier req. 2).

Two of them, and they share one cruel property: they fail SILENTLY. Not an exception, not a log
line — the call returns something plausible and nothing happened.

  1. `Document.get(id)` and `.find_one(...)` return QUERY objects, not documents. Forget `.run()`
     and you are holding a query where you think you hold a row; `.find(...)` wants `.to_list()`.
  2. `.find().delete()` without `.run()` is ALWAYS a no-op — on any collection. And on a TIMESERIES
     collection the ODM path does not delete at all: that one needs raw pymongo.

The fix is not a rule anyone has to remember. It is that the caller never holds a query: every
function here takes a model and returns rows, so there is no `.run()` to forget because there is no
query object in the caller's hands. A wrapper that still handed back queries would only be
documentation.

Every writer asks the write-class first. That is the datatier half of the seam — the model half is
the r-classes refusing their own ODM writers (`tk2.core.documents`).
"""

from typing import Any, TypeVar

from tk2.core.documents import TkDocument, assert_writable
from tk2.core.write_class import WriteClassViolation

D = TypeVar("D", bound=TkDocument)


def is_timeseries(model: type[TkDocument]) -> bool:
    """Read off the model's own `Settings`, which works before bunnet is initialised — unlike
    `get_settings()`, which needs the collection to exist."""
    return getattr(getattr(model, "Settings", None), "timeseries", None) is not None


# ------------------------------------------------------------------------------------------------
# readers — trap 1
# ------------------------------------------------------------------------------------------------


def get(model: type[D], doc_id: Any) -> D | None:
    """One row by id, or None. The `.run()` is here so it cannot be anywhere else."""
    return model.get(doc_id).run()


def find_one(model: type[D], *conditions: Any) -> D | None:
    return model.find_one(*conditions).run()


def find(
    model: type[D],
    *conditions: Any,
    sort: Any = None,
    limit: int | None = None,
) -> list[D]:
    """Rows as a list — never a cursor.

    `sort` takes bunnet's own sort expressions. Where rows are written inside the same second,
    sort by `-_id` as the tiebreaker: tk2 stores time as int SECONDS (`Timestamped`), which cannot
    order two writes in one second, and the tk1 probes learned that the hard way.
    """
    query = model.find(*conditions)
    if sort is not None:
        query = query.sort(sort)
    if limit is not None:
        query = query.limit(limit)
    return query.to_list()


def find_all(model: type[D], *, sort: Any = None, limit: int | None = None) -> list[D]:
    """The whole collection. Used at boot by the r-cache, where «all of it» is the point."""
    return find(model, sort=sort, limit=limit)


def count(model: type[TkDocument], *conditions: Any) -> int:
    return model.find(*conditions).count()


def exists(model: type[TkDocument], *conditions: Any) -> bool:
    return model.find_one(*conditions).run() is not None


# ------------------------------------------------------------------------------------------------
# writers — the write-class asked every time
# ------------------------------------------------------------------------------------------------


def insert(doc: D) -> D:
    assert_writable(type(doc))
    return doc.insert()


def insert_many(model: type[D], docs: list[D]) -> None:
    assert_writable(model)
    if docs:
        model.insert_many(docs)


def save(doc: D) -> D:
    assert_writable(type(doc))
    return doc.save()


def replace(doc: D) -> D:
    assert_writable(type(doc))
    return doc.replace()


# ------------------------------------------------------------------------------------------------
# deletes — trap 2, in both directions
# ------------------------------------------------------------------------------------------------


def delete_many(model: type[TkDocument], *conditions: Any) -> int:
    """Delete matching rows through the ODM. Returns how many actually went.

    The count is returned rather than discarded because the trap this replaces was a delete that
    removed nothing and said nothing: a caller who can see `0` can notice.

    Refuses timeseries models — on those the ODM path does not delete, and it does not complain
    either, which is precisely the failure that must never be reachable from here.
    """
    assert_writable(model)
    if is_timeseries(model):
        raise WriteClassViolation(
            f"{model.__name__} is a TIMESERIES collection: the ODM delete path silently removes "
            f"nothing there. Use delete_timeseries_rows(), which goes through raw pymongo and says "
            f"how many rows it took."
        )
    return model.find(*conditions).delete().run().deleted_count


def delete_timeseries_rows(model: type[TkDocument], mongo_filter: dict[str, Any]) -> int:
    """Delete from a timeseries collection through raw pymongo. Returns how many went.

    The filter is a raw mongo document and not a bunnet expression, because that is what this call
    honestly is: the one place where the tier steps around its own ODM. Hiding that behind a
    model-shaped signature would make the exception look like the rule.
    """
    assert_writable(model)
    if not is_timeseries(model):
        raise WriteClassViolation(
            f"{model.__name__} is not a timeseries collection — use delete_many(), which goes "
            f"through the ODM and takes bunnet conditions. This function exists for the one case "
            f"the ODM cannot serve; using it elsewhere spreads a workaround into normal code."
        )
    return model.get_motor_collection().delete_many(mongo_filter).deleted_count
