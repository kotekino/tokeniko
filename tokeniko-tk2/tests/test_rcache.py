"""The r-cache: what it refuses to hold, how it reads its own interval, and the live pickup."""

import pytest

from tk2.core import constants
from tk2.datatier.rcache import RCache
from tests.models import TKb, TLogic, TParam

# ------------------------------------------------------------------------------------------------
# registration — checked, not trusted
# ------------------------------------------------------------------------------------------------


def test_a_kb_collection_cannot_be_r_cached():
    """The body writes kb, so a snapshot of it would be stale in milliseconds, not minutes. The
    r-cache holds what only migrations change."""
    with pytest.raises(ValueError) as excinfo:
        RCache([TKb])
    assert "kb" in str(excinfo.value)


def test_a_param_collection_without_key_and_value_is_refused():
    """The parameter store is a key/value store; the r-cache says so at registration rather than
    returning None for every lookup later."""
    from tk2.core import ParamDocument

    class Shapeless(ParamDocument):
        whatever: str

        class Settings:
            name = "test_shapeless"

    with pytest.raises(ValueError) as excinfo:
        RCache([Shapeless])
    assert "key" in str(excinfo.value)


def test_logic_collections_need_no_key_value_shape():
    """Only the parameter store is a key/value store. A logic table is a table."""
    assert RCache([TLogic]).models == (TLogic,)


# ------------------------------------------------------------------------------------------------
# the interval — read from the snapshot it refreshes
# ------------------------------------------------------------------------------------------------


def test_the_interval_defaults_before_any_row_exists():
    """The bootstrap value. The cache has to read the db before it can read its own settings."""
    assert RCache([TParam]).refresh_seconds == constants.RCACHE_INTERVAL_DEFAULT
    assert constants.RCACHE_INTERVAL_DEFAULT == 60


@pytest.mark.parametrize("bad", [0, -1, -3600])
def test_a_non_positive_interval_falls_back_instead_of_being_obeyed(bad):
    """A zero or negative interval would turn the slow tick into a hot loop re-reading the whole
    r-tier forever. One bad row must not be able to cost the body its ability to think."""
    cache = RCache([TParam])
    cache._params[constants.RCACHE_INTERVAL_PARAM] = bad
    assert cache.refresh_seconds == constants.RCACHE_INTERVAL_DEFAULT


@pytest.mark.parametrize("bad", ["soon", None, [1]])
def test_an_unreadable_interval_falls_back(bad):
    cache = RCache([TParam])
    cache._params[constants.RCACHE_INTERVAL_PARAM] = bad
    assert cache.refresh_seconds == constants.RCACHE_INTERVAL_DEFAULT


def test_a_sane_interval_is_obeyed():
    cache = RCache([TParam])
    cache._params[constants.RCACHE_INTERVAL_PARAM] = 5
    assert cache.refresh_seconds == 5


def test_a_string_that_is_a_number_is_read_as_one():
    """Mongo will hand back whatever a migration put in; an interval stored as "30" is still 30."""
    cache = RCache([TParam])
    cache._params[constants.RCACHE_INTERVAL_PARAM] = "30"
    assert cache.refresh_seconds == 30


# ------------------------------------------------------------------------------------------------
# loading and the slow tick
# ------------------------------------------------------------------------------------------------

live = pytest.mark.mongo


@live
def test_load_indexes_the_parameter_rows(migration_writer):
    migration_writer.insert(TParam, {"key": "a.b", "value": 7})
    migration_writer.insert(TParam, {"key": "c.d", "value": "text"})

    cache = RCache([TParam])
    cache.load()

    assert cache.param("a.b") == 7
    assert cache.param("c.d") == "text"


@live
def test_a_missing_param_degrades_to_the_callers_default(migration_writer):
    cache = RCache([TParam])
    cache.load()
    assert cache.param("nobody.set.this", 42) == 42
    assert cache.param("nobody.set.this") is None


@live
def test_rows_returns_a_whole_logic_table(migration_writer):
    migration_writer.insert(TLogic, {"name": "modus-ponens", "rule": "p, p->q |- q"})
    cache = RCache([TLogic])
    cache.load()

    rows = cache.rows("t_logic")
    assert len(rows) == 1 and rows[0].name == "modus-ponens"


@live
def test_rows_hands_back_a_copy(migration_writer):
    """A caller that mutated what it got back would be editing the cache from the outside."""
    migration_writer.insert(TLogic, {"name": "a", "rule": "r"})
    cache = RCache([TLogic])
    cache.load()

    cache.rows("t_logic").clear()

    assert len(cache.rows("t_logic")) == 1


@live
def test_the_first_maybe_refresh_loads(migration_writer):
    cache = RCache([TParam])
    assert cache.loaded_at is None
    assert cache.maybe_refresh(now=1000.0) is True
    assert cache.loaded_at == 1000.0


@live
def test_the_tick_does_nothing_before_the_interval_elapses(migration_writer):
    migration_writer.insert(TParam, {"key": constants.RCACHE_INTERVAL_PARAM, "value": 60})
    cache = RCache([TParam])
    cache.load(now=1000.0)

    assert cache.maybe_refresh(now=1030.0) is False
    assert cache.maybe_refresh(now=1059.9) is False
    assert cache.maybe_refresh(now=1060.0) is True


@live
def test_a_param_edit_lands_without_a_restart(migration_writer):
    """THE property this whole tier exists for (datatier req. 3, body req. 4).

    The cache is loaded once and never re-created — standing in for a running body that is not
    restarted. A migration edits the row; the slow tick picks it up; the body is different.
    """
    migration_writer.upsert(TParam, {"key": "heart.decay"}, {"key": "heart.decay", "value": 1})
    cache = RCache([TParam])
    cache.load(now=1000.0)
    assert cache.param("heart.decay") == 1

    # ...a migration runs while the body is alive...
    migration_writer.upsert(TParam, {"key": "heart.decay"}, {"key": "heart.decay", "value": 99})

    # ...the body has not noticed yet: it is fixed between ticks...
    assert cache.param("heart.decay") == 1

    # ...and the slow tick reconciles it.
    assert cache.maybe_refresh(now=1060.0) is True
    assert cache.param("heart.decay") == 99


@live
def test_the_interval_itself_is_refreshable(migration_writer):
    """The refresh rate is a parameter row like any other. A slow tick that could only be changed
    by restarting would be the one setting contradicting the property it provides."""
    migration_writer.upsert(
        TParam, {"key": constants.RCACHE_INTERVAL_PARAM},
        {"key": constants.RCACHE_INTERVAL_PARAM, "value": 60},
    )
    cache = RCache([TParam])
    cache.load(now=1000.0)
    assert cache.refresh_seconds == 60

    migration_writer.upsert(
        TParam, {"key": constants.RCACHE_INTERVAL_PARAM},
        {"key": constants.RCACHE_INTERVAL_PARAM, "value": 5},
    )
    assert cache.maybe_refresh(now=1060.0) is True

    assert cache.refresh_seconds == 5
    # the new, shorter interval governs from here on
    assert cache.maybe_refresh(now=1064.0) is False
    assert cache.maybe_refresh(now=1065.0) is True


@live
def test_a_deleted_row_disappears_from_the_snapshot(migration_writer):
    """The snapshot is replaced wholesale, never merged: a parameter that survived its own removal
    would be worse than a stale one."""
    migration_writer.insert(TParam, {"key": "temporary", "value": 1})
    cache = RCache([TParam])
    cache.load(now=1000.0)
    assert cache.param("temporary") == 1

    migration_writer.delete(TParam, {"key": "temporary"})
    cache.maybe_refresh(now=2000.0)

    assert cache.param("temporary") is None


@live
def test_boot_snapshots_only_the_r_classes(clean_db):
    """`boot_datatier` registers every model with the ODM but caches only what migrations own."""
    from tk2.datatier import boot_datatier
    from tests.models import ALL_MODELS

    _db, cache = boot_datatier(ALL_MODELS, db_name=clean_db.name)
    cached = {m.__name__ for m in cache.models}
    assert cached == {"TParam", "TLogic"}
