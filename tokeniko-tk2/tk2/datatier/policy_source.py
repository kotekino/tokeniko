"""WHERE THE DICTIONARY'S ROWS COME FROM — a live body, or the migration that will write them.

Every instrument that measures under the standing policy needs the same three things (the policy,
the bar, the closed classes) from the same two possible places, and needs to SAY which one spoke: a
measurement whose inputs came from an unnamed place is not reproducible, and the whole difference
between a proposal and an opinion is that one can be run again.

The fallback to the migration files is not a convenience. A policy is written, reported and only
then applied — the apply is the Captain's hand — so on the day a ruling is measured, the rows exist
in `db/` and nowhere else. An instrument that could only read a database could not measure the thing
it was written to measure.

This lives in the datatier because it opens databases; the pure package it feeds
(`tk2.dictionary.policy`) takes the rows as plain mappings and never learns where they came from.
"""

from tk2.dictionary import policy


def _migration(number: int):
    """Load one migration by number, as the runner does."""
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == number), None)
    if found is None:
        raise LookupError(f"no migration numbered {number:04d}")
    return found


def newest_migration_declaring(attribute: str):
    """The newest migration file that declares `attribute`, and the module itself.

    NOT «the newest migration»: a later version declares only what it CHANGES. `0002` re-ruled one
    floor and `0003` ruled the reading mode; neither carries the closed classes, which only the
    baseline declares. Asking the newest policy migration for them raised `AttributeError` from the
    day `0002` landed, and nothing noticed until the offline mine asked — the offline path is the
    one that runs before a migration is applied, so it is exactly the path that must not assume.
    """
    from tk2.migrations import discover

    best = None
    for found in discover():
        module = found.load()
        if hasattr(module, attribute) and (best is None or found.number > best[0].number):
            best = (found, module)
    if best is None:
        raise LookupError(f"no migration declares {attribute}")
    return best


def newest_policy_migration():
    """The migration file declaring the newest policy version — 0003 wrote v1, 0005 v2, 0006 v3.

    Found by asking the files rather than by naming one: a tool with a migration number in it would
    have to be edited every time the Captain rules, and the edit that got forgotten would make it
    quietly measure a superseded policy.
    """
    from tk2.migrations import discover

    best = None
    for found in discover():
        module = found.load()
        if hasattr(module, "POLICY_ROWS") and (
            best is None or module.POLICY_VERSION > best[1].POLICY_VERSION
        ):
            best = (found, module)
    if best is None:
        raise LookupError("no migration declares POLICY_ROWS — there is no policy to read")
    return best


def standing_policy(db_name: str | None) -> tuple[list[dict], str]:
    """The policy rows AS THEY STAND, newest version only — live rows, or the migration's.

    Returns the source too, and every caller prints it.
    """
    if db_name:
        from tk2.core.models import ALL_MODELS, DictionaryPolicyDoc
        from tk2.datatier import traps
        from tk2.datatier.boot import boot_datatier

        boot_datatier(ALL_MODELS, db_name=db_name)
        rows = [r.model_dump() for r in traps.find_all(DictionaryPolicyDoc)]
        if not rows:
            raise LookupError(f"{db_name} holds no policy rows — has migration 0003 been applied?")
        rows = policy.latest_version(rows)
        return rows, f"{db_name}.dictionary_policy v{policy.policy_version(rows)}"

    found, module = newest_policy_migration()
    # The NEWEST version's rows, selected the same way the database path selects them. Since the
    # E1b baseline a single migration file carries the WHOLE ledger — all nine versions — where the
    # old chain carried one version per file, so taking `POLICY_ROWS` whole would hand the reader
    # nine alphabets and nine of every cut.
    rows = policy.latest_version([dict(row) for row in module.POLICY_ROWS])
    return (
        rows,
        f"db/{found.label} (policy v{policy.policy_version(rows)}, not read from a database)",
    )


def standing_bar(db_name: str | None):
    """The bar as it stands — the database's rows if there are any, else the pinned snapshot.

    Both are returned as ROWS as well as pairs, because the fingerprint is taken over rows and the
    whole point of printing it is that it can be compared with a manifest's.
    """
    if db_name:
        from tk2.core.models import DictionaryBarDoc
        from tk2.datatier import traps

        rows = [r.model_dump() for r in traps.find_all(DictionaryBarDoc)]
        if rows:
            return (
                policy.bar_from_rows(rows),
                rows,
                f"{db_name}.dictionary_bar v{policy.bar_version(rows)}",
            )

    document = policy.bar_snapshot()
    return policy.snapshot_bar(), document["pairs"], f"bar_snapshot.json v{document['version']}"


def closed_forms(db_name: str | None) -> tuple[tuple[str, ...], str]:
    """The closed-class forms — live rows if there are any, else migration 0004's."""
    if db_name:
        from tk2.core.models import ClosedClassDoc
        from tk2.datatier import traps

        rows = [r.model_dump() for r in traps.find_all(ClosedClassDoc)]
        if rows:
            version = max(r["version"] for r in rows)
            forms = tuple(sorted({r["form"] for r in rows if " " not in r["form"]}))
            return forms, f"{db_name}.{ClosedClassDoc.Settings.name} v{version}"

    found, module = newest_migration_declaring("CLOSED_CLASS_ROWS")
    version = max(row["version"] for row in module.CLOSED_CLASS_ROWS)
    return module.CLOSED_CLASS_FORMS, f"db/{found.label} v{version} (not applied)"
