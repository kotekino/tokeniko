"""The guard: refusal is the default, and tk1 is refused twice over."""

import pytest

from tk2.core import constants
from tk2.datatier.guard import DatabaseRefused, guard_db_name


def test_the_body_db_is_allowed():
    assert guard_db_name(constants.TK2_BODY_DB) == constants.TK2_BODY_DB


def test_the_test_db_is_allowed():
    assert guard_db_name(constants.TK2_BODY_TEST_DB) == constants.TK2_BODY_TEST_DB


@pytest.mark.parametrize("name", constants.TK1_BODY_DBS)
def test_tk1s_databases_are_refused_by_name(name):
    with pytest.raises(DatabaseRefused) as excinfo:
        guard_db_name(name)
    assert "BIOGRAPHY" in str(excinfo.value)


@pytest.mark.parametrize("name", constants.TK1_BODY_DBS)
def test_tk1_is_refused_even_if_someone_whitelists_it(monkeypatch, name):
    """THE control that matters. If the tk1 refusal were only the absence of a permission, then one
    careless line — a merge, a copy-paste, a widened whitelist at go-live — would open the
    biography. The named check runs FIRST, so two independent things have to go wrong, and the
    second one cannot go wrong quietly."""
    monkeypatch.setattr(
        constants, "DB_WHITELIST", frozenset(constants.DB_WHITELIST | {name})
    )
    with pytest.raises(DatabaseRefused):
        guard_db_name(name)


def test_the_instruments_sandbox_is_refused_with_its_own_reason():
    """A comprehensible mistake — it IS a tk2 database — with an incomprehensible fix if it lands."""
    with pytest.raises(DatabaseRefused) as excinfo:
        guard_db_name(constants.TK2_INSTRUMENTS_DB)
    assert "migration" in str(excinfo.value)


@pytest.mark.parametrize("name", ["admin", "local", "config", "tokeniko_tk2_bodyy", "whatever"])
def test_anything_not_whitelisted_is_refused(name):
    with pytest.raises(DatabaseRefused):
        guard_db_name(name)


def test_a_near_miss_is_still_a_miss():
    """The whitelist matches names, not shapes. A guard that accepted a PATTERN would accept every
    typo that happened to fit it."""
    with pytest.raises(DatabaseRefused):
        guard_db_name(constants.TK2_BODY_DB.upper())


@pytest.mark.parametrize("name", ["", "   ", None, 0])
def test_a_missing_name_is_refused_not_defaulted(name):
    """An empty name is a config that did not load. Falling back to a default here would turn a
    broken environment into a silent write somewhere plausible."""
    with pytest.raises(DatabaseRefused):
        guard_db_name(name)


def test_the_refusal_names_what_is_allowed():
    with pytest.raises(DatabaseRefused) as excinfo:
        guard_db_name("nope")
    message = str(excinfo.value)
    assert constants.TK2_BODY_DB in message


def test_the_refusal_never_leaks_the_connection_string():
    """Errors name DATABASES, never the URI — it may carry credentials."""
    from tk2.core.config import MONGO_URI

    with pytest.raises(DatabaseRefused) as excinfo:
        guard_db_name("nope")
    assert MONGO_URI not in str(excinfo.value)
