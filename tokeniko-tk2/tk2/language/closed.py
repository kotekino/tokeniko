"""Reading the closed classes: which form is here, and which JOB is it doing.

TWO PROBLEMS, and the table alone solves neither.

**ONE — a form can be several words.** 47 of the rows are multi-word (`in front of`, `as long as`,
`by means of`). A matcher that walked token by token would see `in`, and hand the compiler a
LOCATION marker for a phrase that marks nothing of the kind. So matching is LONGEST-FIRST, always.

**TWO — a form can be several jobs.** 45 of the 331 distinct forms hold more than one:

    that      subordinator · demonstrative · relative
    there     referential · existential
    no        quantificational · negation
    through   preposition · postposition · verb particle

The row cannot say which, because which one it is depends on the sentence. **UD says.** `that` under
`mark` is a subordinator; under `det` a demonstrative; heading an `acl:relcl` a relative. That is
why stanza is the skeleton provider and why it is chosen for targeting a standard: the dependency
label IS the selector, and a parser that invented its own labels could not drive this table.

**WHAT IS FRAME HERE AND WHAT IS NOT.** The two maps below are frame — they relate two published,
closed vocabularies (UD's tags and this table's own columns), and no evidence revises what UD's
`DET` corresponds to. The MAPPING from a form to its compiled meaning is knowledge and lives in the
rows, written by `db/0008`. Keep the seam: a new marker is a migration, a new UD relation is a code
change, and neither is ever the other.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

#: UD universal POS -> the `word_class` values this table uses. Several-to-several on purpose:
#: UD's `AUX` covers our auxiliaries AND our modals, and our prepositions and postpositions are both
#: UD's `ADP` — English's handful of postpositions differ by POSITION, which the dependency carries.
UD_POS_TO_WORD_CLASS: dict[str, tuple[str, ...]] = {
    "ADP": ("preposition", "postposition"),
    "PRON": ("pronoun",),
    "DET": ("determiner",),
    "AUX": ("auxiliary", "modal"),
    "CCONJ": ("conjunction",),
    "SCONJ": ("conjunction",),
    "PART": ("particle", "clitic"),
    "ADV": ("adverb", "particle"),
    "SCONJ_OR_ADP": ("conjunction", "preposition"),
}

#: UD dependency relation -> the `role` values it admits, BEST-FIRST. A relation absent from this map
#: puts no constraint on the role, which is the honest default: UD has 37 relations and this table
#: has 25 roles, and most pairs simply do not interact.
UD_DEP_TO_ROLE: dict[str, tuple[str, ...]] = {
    # the marker relations — where the role markers and their re-typed cousins live
    "case": ("role_marker", "causal_marker", "concessive_marker", "exceptive_marker", "genitive"),
    "mark": ("subordinator", "infinitive_marker", "complementizer", "causal_marker",
             "concessive_marker"),
    "cc": ("coordinator",),
    "cc:preconj": ("coordinator",),
    # the determiner relations
    "det": ("determination", "demonstrative", "quantificational", "possessive", "interrogative"),
    "det:poss": ("possessive",),
    "det:predet": ("quantificational",),
    "nmod:poss": ("possessive",),
    # the auxiliary relations
    "aux": ("tense_aspect", "modality"),
    "aux:pass": ("tense_aspect",),
    "cop": ("tense_aspect",),
    # the pronoun relations — a pronoun is whatever its own row says; the dependency says only that
    # it is filling an argument slot rather than marking one
    "nsubj": ("referential", "relative", "interrogative", "free_relative", "reflexive",
              "reciprocal", "demonstrative", "existential"),
    "obj": ("referential", "relative", "interrogative", "free_relative", "reflexive", "reciprocal",
            "demonstrative"),
    "iobj": ("referential", "reflexive", "reciprocal", "demonstrative"),
    "obl": ("referential", "reflexive", "demonstrative"),
    "expl": ("expletive", "existential"),
    # the rest
    "advmod": ("quantificational", "negation", "interrogative", "free_relative", "referential",
               "affirmation"),
    "compound:prt": ("verb_particle",),
    "fixed": ("role_marker", "subordinator"),
}


#: UD dependency -> the tkzip ROLE it settles, for markers the table alone cannot disambiguate.
#: FRAME, and narrow on purpose: every entry is a relation whose UD definition NAMES the role, so
#: nothing here is a judgement about English — it is a reading of UD's own documentation.
#:
#:   `obl:agent`   "used for agents in passive constructions" — «the cat was chased BY the dog».
#:                 `by` is instrument/agent/path/time in the table and this settles it outright.
#:   `nmod:poss`   a possessor, and tkzip keeps the possessor INSIDE the record (Box.relation),
#:                 which is why the answer is a field name and not one of the eighteen roles.
#:   `obl:tmod`    a temporal modifier, named as such by UD.
#:   `obl:lmod`    a locative modifier, likewise.
UD_DEP_SETTLES_ROLE: dict[str, str] = {
    "obl:agent": "agent",
    "obl:tmod": "time",
    "obl:lmod": "location",
    "nmod:poss": "relation",
    "det:poss": "relation",
}


@dataclass(frozen=True, slots=True)
class Match:
    """One closed-class form found in a token stream, with the job it is doing.

    `length` is in TOKENS, so the caller advances past a multi-word form without re-deriving it.
    `certain` is False when the table offers several jobs and UD narrowed it to none of them — the
    match still stands (the form IS a closed-class form) but the job is a guess, and the confidence
    scalar is entitled to know that.
    """

    form: str
    length: int
    word_class: str
    role: str
    compiled: dict[str, Any]
    features: dict[str, Any] = field(default_factory=dict)
    certain: bool = True

    #: Set when a UD subtype SETTLED which role this marker fills — `obl:agent` for «by», say. The
    #: candidates stay in `roles` so the evidence is visible; this is what the compiler should use.
    settled_role: str | None = None

    @property
    def role_or_settled(self) -> str:
        """The role to fill, preferring what UD settled over the table's own best guess."""
        if self.settled_role:
            return self.settled_role
        return self.roles[0] if self.roles else ""

    @property
    def kind(self) -> str:
        """What the form compiles to — `box`, `join`, `quantifier`, `theatre`, `prefix`, …"""
        return self.compiled.get("kind", "")

    @property
    def roles(self) -> tuple[str, ...]:
        """The candidate tkzip roles, best-first. Empty unless this compiles to a box."""
        return tuple(self.compiled.get("roles", ()))


class ClosedClasses:
    """The table, indexed for the two questions the station actually asks.

    Built once and held: the rows are `logic (r)` — a migration writes them and the body reads them —
    so the index is as static as the table is, and rebuilding it per sentence would be a per-token
    cost paid for nothing.
    """

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

        #: Longest first, so `in front of` is tried before `in` and the compiler never sees the
        #: short one. Three tokens is the longest form English's complex prepositions reach here.
        self.longest = max((len(f.split()) for f in self._by_form), default=1)

    # -- the form ---------------------------------------------------------------------------------

    def match(self, tokens: Sequence[str], at: int = 0) -> str | None:
        """The LONGEST closed-class form starting at `at`, or None.

        Case-folded, because the table is lower case and a sentence-initial `The` is the same row as
        `the`. Nothing else is normalised here: `'d` and `'ll` are rows in their own right, and a
        matcher that stripped punctuation would lose them.
        """
        span = min(self.longest, len(tokens) - at)
        for size in range(span, 0, -1):
            form = " ".join(t.lower() for t in tokens[at:at + size])
            if form in self._by_form:
                return form
        return None

    def holds(self, form: str) -> bool:
        return form.lower() in self._by_form

    def jobs(self, form: str) -> tuple[dict, ...]:
        """Every job this form can do — one row each. More than one for 45 of the forms."""
        return tuple(self._by_form.get(form.lower(), ()))

    # -- the job ----------------------------------------------------------------------------------

    def select(self, form: str, upos: str | None = None, dep: str | None = None) -> dict | None:
        """WHICH job, given what UD says about this token.

        Narrow by POS, then by dependency, and take the first survivor in the table's own order.
        **A filter that would empty the set is not applied** — UD and this table were built by
        different people for different purposes, and a token UD calls `ADV` that this table only
        holds as a particle is a disagreement about labels, not evidence that the form is absent.
        Dropping the match there would lose a form the station can see perfectly well; keeping it
        and marking it uncertain is what `Match.certain` is for.
        """
        rows = self._by_form.get(form.lower())
        if not rows:
            return None
        if len(rows) == 1:
            return rows[0]

        # **THE DEPENDENCY GOES FIRST, AND IT OUTRANKS THE POS.** Found on a live parse, 2026-09-15:
        # stanza reads «He looked UP» as `upos=ADP, dep=compound:prt` — the tag says «adposition»
        # and the relation says «this is the verb's particle». Narrowing by POS first kept the two
        # ADP rows, threw away the particle row, and returned a DIRECTION marker for a phrasal verb.
        #
        # The order is not a preference: a POS tag labels a token in isolation, a dependency states
        # its RELATION to the rest of the sentence, and the job this table records is a relational
        # fact. Where the two disagree the relation is the better witness — which is also why
        # `compound:prt` must be matched as the full label, not bared to `compound`.
        narrowed = rows
        if dep:
            allowed = UD_DEP_TO_ROLE.get(dep) or UD_DEP_TO_ROLE.get(dep.split(":")[0])
            if allowed:
                kept = [r for r in narrowed if r["role"] in allowed]
                if kept:
                    # the table's own order is the tie-break, and `allowed` is best-first
                    narrowed = sorted(kept, key=lambda r: allowed.index(r["role"]))
        if upos and len(narrowed) > 1:
            classes = UD_POS_TO_WORD_CLASS.get(upos.upper(), ())
            kept = [r for r in narrowed if r["word_class"] in classes]
            narrowed = kept or narrowed
        return narrowed[0]

    def read(self, tokens: Sequence[str], at: int = 0, upos: str | None = None,
             dep: str | None = None, head_dep: str | None = None) -> Match | None:
        """`match` and `select` together — what a compiler calls once per token position.

        `head_dep` is the dependency of the word this token ATTACHES TO, and it is what settles an
        ambiguous marker. UD puts `case` on the marker and the informative label on the nominal:
        «the cat was chased BY the dog» is `case(dog, by)` + `obl:agent(chased, dog)`. The marker's
        own dep is `case` in every one of these sentences and says nothing; the head's dep says
        which role the phrase fills. A caller with a skeleton always has it — `skeleton[w.head].dep`.
        """
        form = self.match(tokens, at)
        if form is None:
            return None
        row = self.select(form, upos, dep)
        if row is None:
            return None
        candidates = self._by_form[form]
        certain = len(candidates) == 1 or bool(upos or dep)
        compiled = dict(row.get("compiled") or {})
        # A UD SUBTYPE CAN SETTLE AN AMBIGUOUS MARKER OUTRIGHT, and where it does, the table's
        # best-first order is not the answer — «the cat was chased BY the dog» is `obl:agent`, and
        # `by` reads instrument-first in the rows because that is its commonest job, not its job
        # here. Only applied to a marker that actually offers that role: a subtype naming something
        # this form cannot fill is a disagreement to report, never a role to invent.
        settled = UD_DEP_SETTLES_ROLE.get(head_dep or "") or UD_DEP_SETTLES_ROLE.get(dep or "")
        if settled and settled not in compiled.get("roles", ()) and settled != "relation":
            settled = None
        return Match(
            form=form,
            length=len(form.split()),
            word_class=row["word_class"],
            role=row["role"],
            compiled=compiled,
            features=dict(row.get("features") or {}),
            certain=certain,
            settled_role=settled,
        )

    def walk_skeleton(self, skeleton):
        """Every closed-class form in a SKELETON — the walk a compiler actually runs.

        Separate from `walk` because it can see the whole sentence: the head's dependency is what
        settles an ambiguous marker, and a caller holding only `(upos, dep)` pairs cannot supply it.
        """
        i = 0
        words = skeleton.words
        while i < len(words):
            word = words[i]
            head = words[word.head]
            found = self.read(skeleton.tokens, i, word.upos, word.dep,
                              head_dep=None if head.index == word.index else head.dep)
            if found is None:
                i += 1
                continue
            yield i, found
            i += found.length

    def walk(self, tokens: Sequence[str], tags: Sequence[tuple[str, str]] | None = None):
        """Every closed-class form in a token stream, left to right, multi-word forms consumed whole.

        `tags` is UD `(upos, dep)` per token when the caller has a skeleton, and None when it does
        not — the matcher works either way, and says through `Match.certain` which it had.
        """
        i = 0
        while i < len(tokens):
            upos, dep = (tags[i] if tags and i < len(tags) else (None, None))
            found = self.read(tokens, i, upos, dep)
            if found is None:
                i += 1
                continue
            yield i, found
            i += found.length

    # -- what the table knows about itself --------------------------------------------------------

    def forms(self) -> tuple[str, ...]:
        return tuple(sorted(self._by_form))

    def ambiguous_forms(self) -> tuple[str, ...]:
        """The forms holding more than one job — the ones UD has to decide."""
        return tuple(sorted(f for f, rows in self._by_form.items() if len(rows) > 1))

    def multiword_forms(self) -> tuple[str, ...]:
        return tuple(sorted(f for f in self._by_form if " " in f))

    def __len__(self) -> int:
        return len(self._rows)


def standing_closed_classes(db_name: str | None = None) -> ClosedClasses:
    """The table AS IT STANDS — live rows if a database is named, else the newest migration's.

    Same shape as the dictionary's `standing_*` readers, and for the same reason: a measurement must
    be reproducible with no body, and a run that silently read a different table than it reported
    would make every number unattributable.
    """
    if db_name:
        from tk2.core.models import ClosedClassDoc
        from tk2.datatier.client import database

        # READ THROUGH PYMONGO, not the ODM. `policy_source`'s live readers assume the caller has
        # already booted bunnet — true inside a tool, false in a bare script, and the failure is an
        # `AttributeError: _inheritance_inited` from deep inside the ODM rather than anything that
        # names the real problem. These rows are `logic (r)`: nothing here writes them, and the
        # write classes are enforced on the WRITE path, so reading them raw costs no protection and
        # buys a reader that works wherever it is called from. The guard still has the last word —
        # `database()` refuses anything not whitelisted, by name, before a query is possible.
        rows = list(database(db_name)[ClosedClassDoc.Settings.name].find({}, {"_id": 0}))
        if rows:
            version = max(r["version"] for r in rows)
            return ClosedClasses(rows, f"{db_name}.{ClosedClassDoc.Settings.name} v{version}")

    from tk2.datatier.policy_source import newest_migration_declaring

    found, module = newest_migration_declaring("CLOSED_CLASS_ROWS")
    rows = module.CLOSED_CLASS_ROWS
    version = max(r.get("version", 1) for r in rows)
    return ClosedClasses(rows, f"db/{found.label} v{version} (not applied)")
