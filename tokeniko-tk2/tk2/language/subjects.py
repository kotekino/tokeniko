"""THE SUBJECT'S ROLE — the reader for `language_subject_roles` (parser-compiler req 22, `db/0018`).

The rows say which predicates make an `nsubj` an experiencer, a patient or an agent; this file only
RUNS them, through the ambiguous markers' own selector — one rule vocabulary, one runner. A new
exception is a migration; a new kind of probe is a code change. That seam is the first standing law.
"""

from __future__ import annotations

from dataclasses import dataclass

from tk2.language.markers import MarkerSelector, Settled

VERB_PREDICATE, COPULAR_PREDICATE = "verb", "copular"


@dataclass(frozen=True, slots=True)
class SubjectRoles:
    """The rules as they stand, one per kind of predicate."""

    rules: dict
    source: str = "(unnamed)"

    @classmethod
    def from_rows(cls, rows, source: str = "(unnamed)") -> "SubjectRoles":
        rows = list(rows)
        if rows:
            newest = max(r.get("version", 1) for r in rows)
            rows = [r for r in rows if r.get("version", 1) == newest]
        return cls({r["predicate"]: r.get("compiled") or {} for r in rows}, source)

    def settle(self, selector: MarkerSelector, head_lemma: str, head_upos: str,
               copular: bool) -> Settled | None:
        """The subject's role for a clause whose head is this word — or None with no rule."""
        compiled = self.rules.get(COPULAR_PREDICATE if copular else VERB_PREDICATE)
        if not compiled:
            return None
        return selector.settle(compiled, head_lemma=head_lemma, head_upos=head_upos)


def standing_subject_roles(db_name: str | None = None) -> SubjectRoles:
    """The rules AS THEY STAND — live rows if a database is named, else the newest migration's.

    `standing_closed_classes`'s shape and reason: a measurement must be reproducible with no body.
    """
    if db_name:
        from tk2.core.models import SubjectRoleDoc
        from tk2.datatier.client import database

        rows = list(database(db_name)[SubjectRoleDoc.Settings.name].find({}, {"_id": 0}))
        if rows:
            return SubjectRoles.from_rows(rows, f"{db_name}.{SubjectRoleDoc.Settings.name}")

    from tk2.datatier.policy_source import newest_migration_declaring

    found, module = newest_migration_declaring("SUBJECT_ROLE_ROWS")
    return SubjectRoles.from_rows(module.SUBJECT_ROLE_ROWS, f"db/{found.label} (not applied)")
