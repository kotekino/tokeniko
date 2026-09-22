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

from tk2.language.skeleton import bare

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

#: **THE TAGS THAT SAY «THIS IS A CONTENT WORD», AND THEREFORE NOT IN THIS TABLE** *(2026-09-22)*.
#: UD designates its open classes, and `UD_POS_TO_WORD_CLASS` above has no entry for these four —
#: the table holds pronouns, determiners, adpositions, conjunctions, auxiliaries, modals, particles,
#: clitics and adverbs, and not one noun, adjective or lexical verb. **That absence is evidence.**
#:
#: **`VERB` IS DELIBERATELY NOT HERE, AND THE DIFFERENCE IS WHETHER THE TAG IS CREDIBLE.** `being`
#: tagged `NOUN` is right — English has that noun, and the table's `being` is the copula's
#: participle. `through` tagged `VERB` is a parse error: there is no such verb, and deleting the
#: preposition over it would lose a form the station can see perfectly well. That is the
#: disagreement the note on `select` forgives, and `tests/test_language_closed.py` pins it.
#:
#: `ADV` and `INTJ` are UD open classes too and are also NOT here: the table DOES hold adverbs
#: (`always` · `never` · `somewhere`), and «no» as an `INTJ` answering a question is the same kind
#: of genuine label disagreement.
CONTENT_POS = frozenset({"NOUN", "PROPN", "ADJ"})

#: The role of a quantifier that IS its own noun phrase — «nobody» · «everywhere» · «nothing» ·
#: «none» — against the `quantificational` determiner that takes a noun under it. Written by
#: `db/0028`, which moved every quantificational row whose word class is not `determiner`.
#:
#: **A NAME, NOT A ROSTER.** The roles live in the rows and this file holds no list of them; this
#: one is spelled here because two readers need the same spelling — the map below, and the
#: decompiler, which turns a quantity plus a sort back into the one word that fuses them.
FUSED_QUANTIFIER = "fused_quantifier"

#: UD dependency relation -> the `role` values it admits, BEST-FIRST. A relation absent from this map
#: puts no constraint on the role, which is the honest default: UD has 37 relations and this table
#: has 27 roles, and most pairs simply do not interact.
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
              "reciprocal", "demonstrative", "existential", FUSED_QUANTIFIER),
    "obj": ("referential", "relative", "interrogative", "free_relative", "reflexive", "reciprocal",
            "demonstrative", FUSED_QUANTIFIER),
    "iobj": ("referential", "reflexive", "reciprocal", "demonstrative"),
    "obl": ("referential", "reflexive", "demonstrative", FUSED_QUANTIFIER),
    "expl": ("expletive", "existential"),
    # the rest
    "advmod": (FUSED_QUANTIFIER, "quantificational", "negation", "interrogative",
               "free_relative", "referential", "affirmation"),
    "compound:prt": ("verb_particle",),
    "fixed": ("role_marker", "subordinator"),
}


#: The dependencies of a clause that MODIFIES A NOUN — which is what separates a relative clause
#: from an embedded question, and the only evidence there is for it. FRAME: `acl` is UD's own
#: «clausal modifier of a noun», and `acl:relcl` its relative-clause subtype.
#:
#: **ON THE FRAME/KNOWLEDGE AUDIT LIST** with `CLAUSE_DEPS` and the rest — a set of UD relations in
#: code — though this one is a reading of UD's own definition rather than a judgement about English.
RELATIVE_CLAUSE_DEPS = frozenset({"acl"})

#: The dependencies of a clause that is an ARGUMENT — a complement or a clausal subject — which is
#: what separates «I wonder WHETHER it rains» (the question: its truth is asked) from «WHETHER it
#: rains or not, I go» and «IF it rains I stay» (an `advcl`: supposed). Nothing else in the tree
#: separates them: the word is `mark` in all three. FRAME: the tree's shape, and decoding is frame
#: (root `CLAUDE.md`, 2026-09-18; parser-compiler req 21).
COMPLEMENT_CLAUSE_DEPS = frozenset({"ccomp", "csubj"})

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
        if upos and upos.upper() in CONTENT_POS:
            # **A CONTENT WORD IS NOT A FUNCTION WORD THAT HAPPENS TO BE SPELLED THE SAME**
            # *(2026-09-22)*. «Every human BEING is an animal» was compiling to «An animal is»: the
            # noun matched the row for `being`, the participle of the copula, was read as STRUCTURE
            # and compiled to nothing — so the subject vanished and its adjective went `unplaced`.
            #
            # 221 of the 331 forms here have exactly ONE row, and the shortcut below returned it
            # without ever consulting the POS. At least seventeen of those are ordinary English
            # words — `back` · `can` · `will` · `need` · `like` · `one` · `past` · `round` — and
            # «the BACK of the house», «a CAN of soup», «the WILL of the people» each lost a noun.
            #
            # *This is NOT the disagreement the note above forgives. A token UD calls `ADP` that
            # this table holds as a particle is two names for one function word; a token UD calls
            # `NOUN` is a word this table does not contain at all.*
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
             dep: str | None = None, head_dep: str | None = None,
             in_root_clause: bool | None = None) -> Match | None:
        """`match` and `select` together — what a compiler calls once per token position.

        `in_root_clause` is tk1's R5 test, and it is what tells an INTERROGATIVE `who` from a
        RELATIVE one. Both are `nsubj` of their own clause and no label separates them: «WHO sleeps»
        asks, «the cat WHO sleeps» describes — and the difference is whether the clause hangs off
        the root or off a noun. The dependency alone cannot say, so the caller that holds the
        skeleton does.

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
        # **A WH-WORD HAS THREE READINGS, NOT TWO, AND R5's BINARY TEST CONFLATED THE LAST PAIR.**
        #
        #   «WHO sleeps?»                 root clause          -> INTERROGATIVE: opens a slot, and
        #                                                         the utterance is a question
        #   «the cat WHO sleeps»          an `acl:relcl`       -> RELATIVE: binds an antecedent and
        #                                                         opens nothing — one cat, described
        #   «I know WHO did it»           a complement clause  -> FREE RELATIVE: opens a slot, and
        #                                                         the utterance is NOT a question
        #
        # R5 asks «is this the root clause» and answers the MOOD question correctly — «I am happy
        # WHEN I talk» is not an interrogative. It was then read as «therefore relative», which is
        # the conflation: an embedded question opens its slot exactly as a root one does, and only
        # the utterance's mood differs. That is why «if you know WHO did it» left `who` unplaced.
        #
        # **UD MARKS THE DIFFERENCE AND NOTHING ELSE DOES**: a relative clause modifies a NOUN and is
        # `acl:relcl`; an embedded question is a clausal COMPLEMENT — `ccomp`, `csubj`, `xcomp` — or
        # an argument in its own right. So the clause's own dependency chooses, and `head_dep` is
        # already that: the wh-word is `nsubj`/`obj` of its clause's verb, so its head IS the clause.
        if row["role"] in ("interrogative", "relative", "free_relative"):
            if in_root_clause:
                wanted = "interrogative"
            elif bare(head_dep or "") in RELATIVE_CLAUSE_DEPS:
                wanted = "relative"
            elif in_root_clause is None:
                wanted = None          # the caller holds no tree; the table's own order stands
            else:
                wanted = "free_relative"
            if wanted is not None:
                better = next((r for r in self._by_form[form] if r["role"] == wanted), None)
                # **FALL BACK TO THE INTERROGATIVE READING, NOT TO WHATEVER WAS FIRST.** Not every
                # wh-word has a free-relative row — `why` has none — and an embedded «why» still
                # ASKS. The interrogative reading is the one that opens a slot, which is what an
                # embedded question needs; the mood is the compiler's business and it knows the
                # clause is not the root.
                if better is None and wanted == "free_relative":
                    better = next((r for r in self._by_form[form]
                                   if r["role"] == "interrogative"), None)
                if better is not None:
                    row = better
        # **A SUBORDINATOR ON A COMPLEMENT CLAUSE ASKS, ON AN ADVERBIAL ONE IT SUPPOSES** (req 21).
        # «I wonder WHETHER the cat is hungry» and «I asked IF it rains» are embedded polar
        # questions; «IF it rains, I stay» is a condition. The rows hold both readings — the
        # knowledge — and the clause's own dependency picks one, exactly as it picks a wh-word's.
        # Until 2026-09-18 `mark` filtered to the subordinator, so `whether` never opened a truth.
        if bare(dep or "") == "mark" and bare(head_dep or "") in COMPLEMENT_CLAUSE_DEPS:
            asking = next((r for r in self._by_form[form]
                           if (r.get("compiled") or {}).get("opens") == "truth"), None)
            if asking is not None:
                row = asking
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
                              head_dep=None if head.index == word.index else head.dep,
                              in_root_clause=skeleton.attaches_to_root(i))
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
