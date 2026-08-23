"""THE GUARD — standard equipment, not a precaution taken when someone remembers.

One pattern for every entry point (datatier req. 4): a database is named, and a name that was not
explicitly allowed is refused. The refusal is the default. Being allowed is the thing that has to be
written down.

The order of the checks below is the design, not an accident:

  1. tk1's databases are refused FIRST, by name, ahead of the whitelist. So the prohibition does not
     merely rest on the absence of a permission — if someone ever adds `tokeniko` to the whitelist,
     by hand or by merge, the biography is still refused. Two independent things would have to go
     wrong, and the second one cannot go wrong quietly.
  2. the instruments' sandbox is refused with its own message, because reaching for it is a
     comprehensible mistake (it IS a tk2 database) with an incomprehensible fix if it succeeds:
     assets cross into the body by migration, never by a live read across the fence.
  3. everything else must be on the whitelist.

The whitelist is read off the constants module at call time, on purpose — a test that needs to prove
the tk1 refusal outranks the whitelist has to be able to move the whitelist.
"""

from tk2.core import constants


class DatabaseRefused(RuntimeError):
    """A database was named that this process is not allowed to open.

    Raised, never warned: the whole value of the guard is that the wrong name produces no client at
    all. A guard that logged and continued would be a guard that documents the accident.
    """


def guard_db_name(name: str) -> str:
    """Return `name` if this process may open it; raise `DatabaseRefused` otherwise."""
    if not isinstance(name, str) or not name.strip():
        raise DatabaseRefused(
            "REFUSING to open a database with no name. Every entry point names its db explicitly — "
            "an empty name is a config that did not load, and the fix is upstream of here."
        )

    if name in constants.TK1_BODY_DBS:
        raise DatabaseRefused(
            f"REFUSING to open '{name}': that is tk1's live body — the BIOGRAPHY. tk2 never opens "
            f"it, not to read and not to write. What crosses between the generations crosses by "
            f"migration (E9), under the Captain's hand."
        )

    if name == constants.TK2_INSTRUMENTS_DB:
        raise DatabaseRefused(
            f"REFUSING to open '{name}': that is the dictionary-review instruments' sandbox, not "
            f"the body's. The body never writes it; its assets arrive by migration (E1), never by "
            f"a live read across the fence."
        )

    if name not in constants.DB_WHITELIST:
        allowed = ", ".join(sorted(constants.DB_WHITELIST))
        raise DatabaseRefused(
            f"REFUSING to open '{name}': not on the whitelist. Allowed: {allowed}. Widening this "
            f"is a deliberate act — go-live (E10) is the one planned occasion, and it moves the "
            f"boundary knowingly rather than by a name that happened to work."
        )

    return name
