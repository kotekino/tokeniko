"""The one Mongo client, and the only way to a database.

There is a single client per process because pymongo's is already a connection POOL — building a
second one doubles the sockets and halves the reuse, which on a laptop-ceilinged body is a cost with
no purchase.

Every database handle comes through `database()`, and `database()` guards. That is the whole point:
if there is no unguarded path to a handle, there is no unguarded handle.
"""

from pymongo import MongoClient
from pymongo.database import Database

from tk2.core import constants
from tk2.core.config import MONGO_URI, SERVER_SELECTION_TIMEOUT_MS
from tk2.datatier.guard import guard_db_name

_client: MongoClient | None = None


def client() -> MongoClient:
    """The process's client, built on first use."""
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=SERVER_SELECTION_TIMEOUT_MS)
    return _client


def database(name: str | None = None) -> Database:
    """A guarded database handle. Defaults to the body's own.

    The default is the body's db and not «whatever was configured», so a caller who says nothing
    gets the intended database rather than the last one someone set.
    """
    return client()[guard_db_name(name if name is not None else constants.TK2_BODY_DB)]


def close() -> None:
    """Drop the client. For tests and for a clean shutdown — the body itself does not close its
    own connection pool while it is alive."""
    global _client
    if _client is not None:
        _client.close()
        _client = None
