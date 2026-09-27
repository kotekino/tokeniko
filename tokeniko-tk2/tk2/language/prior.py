"""HOW STRONGLY A QUESTION EXPECTS ITS ANSWER — the reader for `language_open_priors` (tkzip req 50,
`db/0042`).

`tk2.language.strength`'s shape, on the Captain's ruling that the prior is knowledge «exactly as
`strength` is» (2026-09-27, `E3.3.11.2.21`): the rows hold the number, this file only finds the row.
A new shape of asking is a migration plus whatever lets the station RECOGNISE it — and recognising
it is the tree's, so that second half is the code change.
"""

from __future__ import annotations

from dataclasses import dataclass

#: The two shapes of a TAG, told apart by the tree alone: the tag's polarity against its host's.
#: «It's cold, ISN'T it?» REVERSES it — req 50's own witness, and the one shape with a row. «So she
#: slept, DID she?» keeps it, and whether that expects, infers or doubts is what no row says yet.
REVERSED_TAG = "reversed_tag"
CONSTANT_TAG = "constant_tag"


@dataclass(frozen=True, slots=True)
class OpenPriors:
    """The priors as they stand, one per shape of asking."""

    rules: dict
    source: str = "(unnamed)"

    @classmethod
    def from_rows(cls, rows, source: str = "(unnamed)") -> "OpenPriors":
        rows = list(rows)
        if rows:
            newest = max(r.get("version", 1) for r in rows)
            rows = [r for r in rows if r.get("version", 1) == newest]
        return cls({r["shape"]: r.get("compiled") or {} for r in rows}, source)

    def of(self, shape: str) -> float | None:
        """How strongly this shape expects *yes* — or None with no row.

        **None is an answer, and here it is a WITHHOLDING, not an empty slot.** An OPEN truth with
        no prior is req 50's OTHER question — «Is it cold?», which expects nothing — so a tag whose
        shape has no row would be stored as a question the sentence did not ask. The caller
        withholds it (`Compiler._tags`); it never opens the host without the number.
        """
        found = (self.rules.get(shape) or {}).get("prior")
        return None if found is None else float(found)


def standing_open_priors(db_name: str | None = None) -> OpenPriors:
    """The priors AS THEY STAND — live rows if a database is named, else the newest migration's.

    `standing_attitude_strengths`'s shape and reason: a measurement must be reproducible with no
    body.
    """
    if db_name:
        from tk2.core.models import OpenPriorDoc
        from tk2.datatier.client import database

        rows = list(database(db_name)[OpenPriorDoc.Settings.name].find({}, {"_id": 0}))
        if rows:
            return OpenPriors.from_rows(rows, f"{db_name}.{OpenPriorDoc.Settings.name}")

    from tk2.datatier.policy_source import newest_migration_declaring

    found, module = newest_migration_declaring("OPEN_PRIOR_ROWS")
    return OpenPriors.from_rows(module.OPEN_PRIOR_ROWS, f"db/{found.label} (not applied)")
