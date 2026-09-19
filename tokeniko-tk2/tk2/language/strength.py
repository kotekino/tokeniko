"""THE STRENGTH OF A WANTING — the reader for `language_attitude_strengths` (req 23, `db/0020`).

The rows hold the number; this file only finds the row. A new shape of wanting is a migration plus
whatever lets the station RECOGNISE it — that second half is the code change, and it is why the
seam is drawn here rather than at a float in the compiler.
"""

from __future__ import annotations

from dataclasses import dataclass

IMPERATIVE = "imperative"


@dataclass(frozen=True, slots=True)
class AttitudeStrengths:
    """The strengths as they stand, one per shape of wanting."""

    rules: dict
    source: str = "(unnamed)"

    @classmethod
    def from_rows(cls, rows, source: str = "(unnamed)") -> "AttitudeStrengths":
        rows = list(rows)
        if rows:
            newest = max(r.get("version", 1) for r in rows)
            rows = [r for r in rows if r.get("version", 1) == newest]
        return cls({r["shape"]: r.get("compiled") or {} for r in rows}, source)

    def of(self, shape: str) -> float | None:
        """How strongly this shape wants — or None with no row, which leaves the slot EMPTY.

        None is an answer and not a failure (`supersense_of`'s own rule): a station whose table has
        not reached a shape says nothing about its strength rather than inventing a number, and
        req 8's half-understood stays legal while wrongly-understood does not.
        """
        found = (self.rules.get(shape) or {}).get("strength")
        return None if found is None else float(found)


def standing_attitude_strengths(db_name: str | None = None) -> AttitudeStrengths:
    """The strengths AS THEY STAND — live rows if a database is named, else the newest migration's.

    `standing_subject_roles`'s shape and reason: a measurement must be reproducible with no body.
    """
    if db_name:
        from tk2.core.models import AttitudeStrengthDoc
        from tk2.datatier.client import database

        rows = list(database(db_name)[AttitudeStrengthDoc.Settings.name].find({}, {"_id": 0}))
        if rows:
            return AttitudeStrengths.from_rows(rows, f"{db_name}.{AttitudeStrengthDoc.Settings.name}")

    from tk2.datatier.policy_source import newest_migration_declaring

    found, module = newest_migration_declaring("ATTITUDE_STRENGTH_ROWS")
    return AttitudeStrengths.from_rows(module.ATTITUDE_STRENGTH_ROWS, f"db/{found.label} (not applied)")
