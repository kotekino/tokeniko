"""Reading the adverb kinds: which of requirement 23's four scopes an adverb takes.

**THE DEFAULT IS MANNER AND IT IS NOT A ROW.** 79% of WordNet's 3,767 single-word adverbs end in
`-ly` and 73% derive from an adjective; they describe the action, and a manner box is right about
them for free. `db/0013` holds only the exceptions — the epistemic, the evaluative, the discourse
connectives and the non-`-ly` circumstantials — which is what turns an open class into a curatable
one. **So a miss here is an ANSWER**, not an absence: `manner`.

**TWO ROSTERS, ONE VOCABULARY, ONE READER.** The Captain ruled (2026-09-16) that these rows live in
their own collection rather than in the closed classes, because the closed-class forms filter D's
vocabulary and sixty new ones would desynchronise the sealed base. The cost he named is that «what
does this word compile to» now has two tables — and it is paid by making only the ROSTER second:
`compiled` here holds the identical vocabulary `ClosedClassDoc.compiled` holds. **A caller asks the
closed classes first and this table second, and cannot tell which answered.**

*The order is not arbitrary. A form in both rosters is a defect `db/0013`'s own check refuses at
import, so in practice the question never arises — but if it ever did, the closed classes win,
because a form with a structural job has that job in every sentence while an adverb kind is a
reading of an open-class word.*
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

#: Requirement 23's four scopes, minus the default. A row saying `manner` would be the roster of the
#: open class `db/0013` exists to avoid writing.
EPISTEMIC = "epistemic"
EVALUATIVE = "evaluative"
DISCOURSE = "discourse"
CIRCUMSTANTIAL = "circumstantial"

#: **THE FIFTH KIND, A FOCUS PARTICLE** (`db/0039`, the Captain's `E3.12.5.9.12`): «only», «exactly».
#: None of the four says it — it restricts WHICH thing satisfies the frame, and which thing that is
#: the tree says (the particle's head, its ASSOCIATE). `compiled.focus` names the meaning, and what
#: the meaning does to a clause or a phrase is the compiler's logic.
FOCUS = "focus"
#: The two meanings a focus row may carry: the associate is NECESSARY («only»), or necessary AND
#: sufficient («exactly»). Names and not a roster — which word means which is the rows'.
EXCLUSIVE, IDENTIFYING = "exclusive", "identifying"

#: **THE MEANING «ABSTAIN»** (`db/0040`): a row whose `compiled.kind` says it tells the station that
#: nothing about the word may be written down — its meaning is not settled. The word is left
#: unplaced, the reason recorded. A name in the vocabulary both rosters share, not a roster.
ABSTAIN = "abstain"

#: What an adverb is when no row says otherwise — and it is a MEASURED default, not a shrug.
MANNER = "manner"


@dataclass(frozen=True, slots=True)
class AdverbReading:
    """What one adverb does to a zip."""

    form: str
    kind: str
    compiled: dict[str, Any] = field(default_factory=dict)

    @property
    def is_default(self) -> bool:
        """True when no row was found and the manner default answered. The caller is entitled to
        know — a default that cannot be told from a curated answer is the silently-complete nearest
        fit req 8 forbids, which is the same distinction `db/0012` drew for the markers."""
        return self.kind == MANNER and not self.compiled.get("curated", False)

    @property
    def role(self) -> str:
        """The box this fills, for a circumstantial or the manner default. Empty otherwise."""
        roles = self.compiled.get("roles") or ()
        return roles[0] if roles else ""


#: The manner default, built once. A manner adverb fills a manner box carrying no head of its own —
#: req 24: «manner is a box; the ROTATION lives in the derived layer».
def _manner(form: str) -> AdverbReading:
    return AdverbReading(form=form, kind=MANNER, compiled={"kind": "box", "roles": ["manner"]})


class AdverbKinds:
    """The table, indexed by form. Built once and held: the rows are `logic (r)`."""

    def __init__(self, rows: Iterable[dict], source: str = "(unnamed)") -> None:
        self.source = source
        self._rows = [dict(r) for r in rows]
        if self._rows:
            newest = max(r.get("version", 1) for r in self._rows)
            self._rows = [r for r in self._rows if r.get("version", 1) == newest]
            self.version = newest
        else:
            self.version = 0

        self._by_form: dict[str, list[dict]] = {}
        for row in self._rows:
            self._by_form.setdefault(row["form"], []).append(row)

    def read(self, lemma: str, dep: str | None = None) -> AdverbReading:
        """What this adverb does — a row if there is one, else the manner default.

        `dep` chooses between a form's several kinds. «he is STILL here» is `advmod` on the verb and
        a TIME box; «STILL, he left» is `discourse`, and UD labels it so. Where the dependency does
        not separate them the table's own order is the tie-break, which is best-first by
        construction.
        """
        rows = self._by_form.get((lemma or "").lower())
        if not rows:
            return _manner(lemma)
        chosen = rows[0]
        if dep and len(rows) > 1:
            # UD's `discourse` relation names the kind outright — the only dependency that does.
            wanted = DISCOURSE if dep.split(":")[0] == "discourse" else None
            if wanted:
                chosen = next((r for r in rows if r["kind"] == wanted), chosen)
            else:
                chosen = next((r for r in rows if r["kind"] != DISCOURSE), chosen)
        return AdverbReading(form=chosen["form"], kind=chosen["kind"],
                             compiled={**(chosen.get("compiled") or {}), "curated": True})

    def holds(self, form: str) -> bool:
        return (form or "").lower() in self._by_form

    def forms(self) -> tuple[str, ...]:
        return tuple(sorted(self._by_form))

    def of_kind(self, kind: str) -> tuple[str, ...]:
        return tuple(sorted(f for f, rows in self._by_form.items()
                            if any(r["kind"] == kind for r in rows)))

    def __len__(self) -> int:
        return len(self._rows)


def standing_adverb_kinds(db_name: str | None = None) -> AdverbKinds:
    """The table AS IT STANDS — live rows if a database is named, else the newest migration's.

    Same shape and same reason as `standing_closed_classes`: a measurement must be reproducible with
    no body, and a run that silently read a different table than it reported would make every number
    unattributable.
    """
    if db_name:
        from tk2.core.models import AdverbKindDoc
        from tk2.datatier.client import database

        # Read through pymongo, not the ODM — `standing_closed_classes`'s reason exactly: these rows
        # are `logic (r)`, nothing here writes them, and the guard still refuses any database not
        # whitelisted by name before a query is possible.
        rows = list(database(db_name)[AdverbKindDoc.Settings.name].find({}, {"_id": 0}))
        if rows:
            version = max(r["version"] for r in rows)
            return AdverbKinds(rows, f"{db_name}.{AdverbKindDoc.Settings.name} v{version}")

    from tk2.datatier.policy_source import newest_migration_declaring

    found, module = newest_migration_declaring("ADVERB_KIND_ROWS")
    rows = module.ADVERB_KIND_ROWS
    version = max(r.get("version", 1) for r in rows)
    return AdverbKinds(rows, f"db/{found.label} v{version} (not applied)")
