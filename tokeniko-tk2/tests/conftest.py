"""Fixtures for the datatier tests.

The live-Mongo tests run against `tokeniko_tk2_body_test` — a whitelisted, test-scoped name, created
and dropped by this file and by nothing else. tk1's databases are never opened here; the guard would
refuse them anyway, and there is a test that proves it would.
"""

import pytest
from pymongo.errors import PyMongoError

from tk2.core import constants
from tk2.datatier import MigrationWriter, boot_datatier, client, close
from tests.models import ALL_MODELS, TKb, TLogic, TParam, TSeries


def _mongo_is_up() -> bool:
    try:
        client().admin.command("ping")
        return True
    except PyMongoError:
        return False


@pytest.fixture(scope="session")
def test_db():
    """The sandbox test database, with the ODM booted over every test model.

    Session-scoped because `init_bunnet` is process-global: booting it per test would mean the last
    boot silently decides what every earlier model points at.
    """
    if not _mongo_is_up():
        pytest.skip("no local MongoDB — the live datatier checks need one")

    db, _cache = boot_datatier(ALL_MODELS, db_name=constants.TK2_BODY_TEST_DB)
    yield db

    # Belt and braces before a destructive call: this must be able to drop ONLY the test database,
    # and the assertion is cheaper than the one accident it prevents.
    assert db.name == constants.TK2_BODY_TEST_DB, "refusing to drop a database that is not the test db"
    client().drop_database(constants.TK2_BODY_TEST_DB)
    close()


@pytest.fixture
def clean_db(test_db):
    """An empty test database for one test. Emptied before rather than after, so a failing test
    leaves its rows behind to be looked at."""
    for model in ALL_MODELS:
        test_db[model.Settings.name].delete_many({})
    return test_db


@pytest.fixture
def migration_writer(clean_db):
    """The other door. Tests that need r-class rows in place use this, exactly as a real migration
    would — there is no other way to create them, which is the property under test."""
    return MigrationWriter(clean_db)


@pytest.fixture
def models():
    """The test models, by name, so a test does not import four things to use one."""
    return {"param": TParam, "logic": TLogic, "kb": TKb, "series": TSeries}
