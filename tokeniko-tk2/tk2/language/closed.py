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

**WHAT IS FRAME HERE AND WHAT IS NOT.** `UD_POS_TO_WORD_CLASS` below is frame — it relates two
published, closed vocabularies (UD's tags and this table's own word classes), and no evidence
revises what UD's `DET` corresponds to. The MAPPING from a form to its compiled meaning is
knowledge and lives in the rows, written by `db/0008`. **Which roles a UD relation admits is
knowledge too, and lives in the UD readings** (`db/0034`): the roles it names are this table's own
rows, and a code map of db vocabulary goes stale against its rows — `db/0028`'s `fused_quantifier`
needed a code edit before the station would admit one. *Frame changes only by a fix, knowledge by
learning* (the Captain, 2026-09-24).

**AND A TIE NOBODY SETTLES ABSTAINS.** The map this replaced was ranked «best-first» and broke ties
by its order; nothing measured supported the ranking (`tools/dep_order_bench.py`), so it was deleted
rather than moved. Where the relation, the tag and the clause leave more than one reading standing,
no reading is chosen and the token is unplaced — the honest answer.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

from tk2.language.skeleton import bare
from tk2.language.ud_readings import UdReadings, standing_ud_readings

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
#: one is spelled here because the decompiler needs it, to turn a quantity plus a sort back into the
#: one word that fuses them. Which relations admit it is the UD readings' business (`db/0034`).
FUSED_QUANTIFIER = "fused_quantifier"

#: **WHERE A «NOT» AFTER A MODAL SCOPES** — the feature `db/0036` writes on every `modality` row, and
#: the three answers it may give. A name and its vocabulary, not a roster: WHICH modal takes which
#: value is the rows' («must not» □¬ · «need not» ¬□ · «may not» either). A fused form — «cannot» —
#: says where its OWN negation sits in `compiled.negation`, with the same three words, because that
#: one is part of its meaning.
FOLLOWING_NEGATION = "following_negation"
INSIDE, OUTSIDE, AMBIGUOUS = "inside", "outside", "ambiguous"

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
    `certain` is False when the table offers several rows and UD said nothing about the token. Since
    2026-09-24 that can only be several rows of ONE reading — «his» the determiner and «his» the
    pronoun — because several readings with nothing to settle them are no match at all. The meaning
    stands; which row carried it is a guess, and the confidence scalar is entitled to know that.
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

    def __init__(self, rows: Iterable[dict], source: str = "(unnamed)",
                 readings: UdReadings | None = None) -> None:
        self.source = source
        #: Which roles each UD relation admits — the UD readings' fourth question (`db/0034`). Held
        #: here, resolved ONCE, because `select` runs per token and must never reach for the db. A
        #: caller holding a live table hands in the same database's readings — as
        #: `standing_closed_classes` does — and anyone else gets the newest migration's, exactly as
        #: the compiler does for its own.
        self.readings = readings if readings is not None else standing_ud_readings()
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

    def candidates(self, form: str, upos: str | None = None,
                   dep: str | None = None) -> tuple[dict, ...]:
        """Every job UD LEAVES STANDING for this token — the rows `select` settles, or does not.

        Narrow by dependency, then by POS, and stop: the survivors come back in the table's own
        order, and **that order is not evidence** — no reader may take the first of several
        readings as the answer. Empty for a form the table lacks and for a content word.

        **A filter that would empty the set is not applied** — UD and this table were built by
        different people for different purposes, and a token UD calls `ADV` that this table only
        holds as a particle is a disagreement about labels, not evidence that the form is absent.
        What the tolerance keeps is every row the failed filter could not choose between; whether
        they are ONE reading is `select`'s question, not this one's.
        """
        rows = self._by_form.get(form.lower())
        if not rows:
            return ()
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
            return ()
        if len(rows) == 1:
            return (rows[0],)

        # **THE DEPENDENCY GOES FIRST, AND IT OUTRANKS THE POS.** Found on a live parse, 2026-09-15:
        # stanza reads «He looked UP» as `upos=ADP, dep=compound:prt` — the tag says «adposition»
        # and the relation says «this is the verb's particle». Narrowing by POS first kept the two
        # ADP rows, threw away the particle row, and returned a DIRECTION marker for a phrasal verb.
        #
        # The order is not a preference: a POS tag labels a token in isolation, a dependency states
        # its RELATION to the rest of the sentence, and the job this table records is a relational
        # fact. Where the two disagree the relation is the better witness — which is also why
        # `compound:prt` must be matched as the full label, not bared to `compound`.
        narrowed = list(rows)
        if dep:
            admitted = self.readings.admits_roles(dep)
            if admitted is not None:
                narrowed = [r for r in narrowed if r["role"] in admitted] or narrowed
        if upos and len(narrowed) > 1:
            classes = UD_POS_TO_WORD_CLASS.get(upos.upper(), ())
            narrowed = [r for r in narrowed if r["word_class"] in classes] or narrowed
        return tuple(narrowed)

    def select(self, form: str, upos: str | None = None, dep: str | None = None) -> dict | None:
        """WHICH job, given what UD says about this token — or None, if UD does not say.

        **A TIE NOBODY SETTLES ABSTAINS** (the Captain, 2026-09-24). When the survivors of
        `candidates` carry more than one READING, nothing here picks: the map this replaced ranked
        its roles «best-first», nothing measured supported the ranking, and a pick the evidence did
        not make is a guess the zip would carry as a fact. That includes the tolerance's fallback —
        a filter that emptied chose nothing, so a fallback with two readings is still a tie. The
        clause can still settle it; that is `read`'s business, and it reads `candidates` directly.

        Where the survivors are ONE reading in several rows — `his` the determiner and `his` the
        pronoun, `through` before its noun and after it — the first row is returned: the meaning is
        settled, and what differs is the word class and the features, not what the token says.
        """
        survivors = self.candidates(form, upos, dep)
        return self._settled(survivors)

    @staticmethod
    def _reading(row: dict) -> tuple[str, str]:
        """What a row SAYS: its role and its compiled meaning. Two rows that agree on both are one
        reading told twice; rows that differ on either are two things the token could be."""
        return row["role"], json.dumps(row.get("compiled") or {}, sort_keys=True, default=str)

    def _settled(self, survivors: Sequence[dict]) -> dict | None:
        """The one reading these rows carry, as its first row — or None when they carry several."""
        if not survivors:
            return None
        if len({self._reading(r) for r in survivors}) > 1:
            return None
        return survivors[0]

    def read(self, tokens: Sequence[str], at: int = 0, upos: str | None = None,
             dep: str | None = None, head_dep: str | None = None,
             in_root_clause: bool | None = None) -> Match | None:
        """`match` and the job together — what a compiler calls once per token position.

        None when no form matches AND when a form matches but nothing settles its job: the token is
        then left for the compiler to account as unplaced, which is the honest answer — «NO, some
        software is no mind» asks the station whether that `no` quantifies or answers, and neither
        the relation (`discourse`) nor the tag (`INTJ`) nor the clause says.

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
        survivors = self.candidates(form, upos, dep)
        if not survivors:
            return None
        # The clause first, then the survivors' own agreement — and the complement clause last,
        # because a `mark` on a complement asks whatever the rest would have said.
        row = (self._by_clause(form, survivors, head_dep, in_root_clause)
               or self._settled(survivors))
        row = self._by_complement(form, dep, head_dep) or row
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

    def _by_complement(self, form: str, dep: str | None, head_dep: str | None) -> dict | None:
        """The asking reading of a subordinator on a COMPLEMENT clause — else None.

        **A SUBORDINATOR ON A COMPLEMENT CLAUSE ASKS, ON AN ADVERBIAL ONE IT SUPPOSES** (req 21).
        «I wonder WHETHER the cat is hungry» and «I asked IF it rains» are embedded polar
        questions; «IF it rains, I stay» is a condition. The rows hold both readings — the
        knowledge — and the clause's own dependency picks one, exactly as it picks a wh-word's.
        Until 2026-09-18 `mark` filtered to the subordinator, so `whether` never opened a truth.

        *The asking row is sought among ALL the form's rows, not only the survivors: `mark` admits
        no `interrogative`, so the relation filtered it out — and the clause is the better witness,
        for the reason the dependency outranks the POS.*
        """
        if bare(dep or "") != "mark" or bare(head_dep or "") not in COMPLEMENT_CLAUSE_DEPS:
            return None
        return next((r for r in self._by_form[form]
                     if (r.get("compiled") or {}).get("opens") == "truth"), None)

    def _by_clause(self, form: str, survivors: Sequence[dict], head_dep: str | None,
                   in_root_clause: bool | None) -> dict | None:
        """The wh-reading the CLAUSE settles, when every survivor is a wh-reading — else None.

        **A WH-WORD HAS THREE READINGS, NOT TWO, AND R5's BINARY TEST CONFLATED THE LAST PAIR.**

          «WHO sleeps?»                 root clause          -> INTERROGATIVE: opens a slot, and
                                                                the utterance is a question
          «the cat WHO sleeps»          an `acl:relcl`       -> RELATIVE: binds an antecedent and
                                                                opens nothing — one cat, described
          «I know WHO did it»           a complement clause  -> FREE RELATIVE: opens a slot, and
                                                                the utterance is NOT a question

        R5 asks «is this the root clause» and answers the MOOD question correctly — «I am happy
        WHEN I talk» is not an interrogative. It was then read as «therefore relative», which is
        the conflation: an embedded question opens its slot exactly as a root one does, and only
        the utterance's mood differs. That is why «if you know WHO did it» left `who` unplaced.

        **UD MARKS THE DIFFERENCE AND NOTHING ELSE DOES**: a relative clause modifies a NOUN and is
        `acl:relcl`; an embedded question is a clausal COMPLEMENT — `ccomp`, `csubj`, `xcomp` — or
        an argument in its own right. So the clause's own dependency chooses, and `head_dep` is
        already that: the wh-word is `nsubj`/`obj` of its clause's verb, so its head IS the clause.

        **THE CLAUSE SETTLES ONLY THE WH-TRIO, SO IT SPEAKS ONLY WHEN THE TIE LIES WITHIN IT.**
        Survivors that include a non-wh reading — `what` the exclamative quantifier beside `what`
        the question — are a tie the clause has no evidence about, and it stays a tie. Where it
        does speak, its reading is sought among ALL the form's rows: «the day WHEN I left» is
        `advmod`, which admits no `relative`, and the clause is the better witness.
        """
        trio = ("interrogative", "relative", "free_relative")
        if not all(r["role"] in trio for r in survivors):
            return None
        if in_root_clause:
            wanted = "interrogative"
        elif bare(head_dep or "") in RELATIVE_CLAUSE_DEPS:
            wanted = "relative"
        elif in_root_clause is None:
            return None            # the caller holds no tree, and nothing else can say
        else:
            wanted = "free_relative"
        rows = self._by_form[form]
        better = next((r for r in rows if r["role"] == wanted), None)
        # **FALL BACK TO THE INTERROGATIVE READING, NOT TO WHATEVER WAS FIRST.** Not every wh-word
        # has a free-relative row — `why` has none — and an embedded «why» still ASKS. The
        # interrogative reading is the one that opens a slot, which is what an embedded question
        # needs; the mood is the compiler's business and it knows the clause is not the root.
        if better is None and wanted == "free_relative":
            better = next((r for r in rows if r["role"] == "interrogative"), None)
        return better

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
            # **THE SAME DATABASE'S READINGS, NAMED IN THE SOURCE.** Which roles a relation admits
            # is part of how this table is read (`db/0034`), so a live table read against the
            # migrations' readings — or the reverse — would be a number nobody could attribute.
            readings = standing_ud_readings(db_name)
            return ClosedClasses(rows, f"{db_name}.{ClosedClassDoc.Settings.name} v{version} · "
                                       f"readings {readings.source}", readings=readings)

    from tk2.datatier.policy_source import newest_migration_declaring

    found, module = newest_migration_declaring("CLOSED_CLASS_ROWS")
    rows = module.CLOSED_CLASS_ROWS
    version = max(r.get("version", 1) for r in rows)
    readings = standing_ud_readings()
    return ClosedClasses(rows, f"db/{found.label} v{version} (not applied) · readings "
                               f"{readings.source}", readings=readings)
