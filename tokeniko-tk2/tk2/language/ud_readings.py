"""Reading the UD readings: where a UD label does not mean for us what it names.

**MOST LABELS NEED NO ROW.** `nsubj` IS a subject and `acl` IS a clausal modifier of a noun; reading
the tree's shape that way is frame (the Captain, 2026-09-18) and it is what `SUBJECT_DEPS` and its
siblings do in code. This table holds only the handful where the station makes a JUDGEMENT on top of
the label — and a judgement is knowledge.

**A MISS IS AN ANSWER.** `db/0013`'s shape: the defaults live here, one line each, and the rows hold
what differs. A caller asks a question about a label and always gets a verdict; it never has to know
whether a row existed.
"""

from __future__ import annotations

from typing import Any, Iterable

#: The ordinary reading of a label nobody wrote a row about. **These are not a roster** — they are
#: the three questions the station asks, and their answers where UD's own definition is taken at
#: face value. A fourth question means a fourth default and a migration to go with it.
DEFAULTS: dict[str, Any] = {
    #: Does this relation's dependent become content at all? A vocative does not (`db/0032`).
    "compiles_to_content": True,
    #: Does this relation open a content row of its own? `xcomp` does not (`db/0032`).
    "opens_clause": True,
    #: Does this part of speech state a number the SPEAKER chose? Only `NOUN` does (`db/0032`).
    "states_number": False,
}


class UdReadings:
    """The table, indexed by (inventory, label). Built once and held: the rows are `logic (r)`."""

    def __init__(self, rows: Iterable[dict], source: str = "(unnamed)") -> None:
        self.source = source
        self._rows = [dict(r) for r in rows]
        if self._rows:
            newest = max(r.get("version", 1) for r in self._rows)
            self._rows = [r for r in self._rows if r.get("version", 1) == newest]
            self.version = newest
        else:
            self.version = 0

        self._by_label: dict[tuple[str, str], dict] = {
            (row["inventory"], row["label"]): row for row in self._rows
        }

    def reads(self, inventory: str, label: str, question: str) -> Any:
        """What this label reads as, for this question — the row if there is one, else the default.

        The default is returned for an unknown label AND for a known one whose row is silent on this
        question, which are the same thing: nothing said, so the ordinary reading holds.
        """
        if question not in DEFAULTS:
            raise KeyError(f"{question!r} is not a question this table answers — add it to "
                           f"`DEFAULTS` and write the migration that can differ from it")
        row = self._by_label.get((inventory, label))
        if row is None:
            return DEFAULTS[question]
        return (row.get("reads") or {}).get(question, DEFAULTS[question])

    def compiles_to_content(self, dep: str) -> bool:
        """Does this relation's dependent become content? «Guys, take it easy» — the room does not."""
        return bool(self.reads("relation", dep, "compiles_to_content"))

    def opens_clause(self, dep: str) -> bool:
        """Does this relation earn a content row of its own? «you like TO SWIM» does not."""
        return bool(self.reads("relation", dep, "opens_clause"))

    def states_number(self, upos: str) -> bool:
        """Did the speaker CHOOSE this word's number? «cats» yes; «Marie» no (schema v6)."""
        return bool(self.reads("pos", upos, "states_number"))

    def __len__(self) -> int:
        return len(self._rows)


def standing_ud_readings(db_name: str | None = None) -> UdReadings:
    """The table AS IT STANDS — live rows if a database is named, else the newest migration's.

    Same shape and same reason as `standing_closed_classes` and `standing_adverb_kinds`: a
    measurement must be reproducible with no body, and a run that silently read a different table
    than it reported would make every number unattributable.
    """
    if db_name:
        from tk2.core.models import UdReadingDoc
        from tk2.datatier.client import database

        rows = list(database(db_name)[UdReadingDoc.Settings.name].find({}, {"_id": 0}))
        if rows:
            version = max(r["version"] for r in rows)
            return UdReadings(rows, f"{db_name}.{UdReadingDoc.Settings.name} v{version}")

    from tk2.datatier.policy_source import newest_migration_declaring

    found, module = newest_migration_declaring("UD_READING_ROWS")
    rows = module.UD_READING_ROWS
    version = max(r.get("version", 1) for r in rows)
    return UdReadings(rows, f"db/{found.label} v{version} (not applied)")
