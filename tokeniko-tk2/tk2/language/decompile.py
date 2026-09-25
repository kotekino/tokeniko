"""THE DECOMPILER — a zip back into a sentence that compiles to that zip. **Requirement 9.**

**THE NAME IS THE DESIGN** (the Captain, 2026-09-19): *«I would call it decompiler, mimicking the
compiler/decompiler of computer languages»*. Decompiled source is never the original source — it is
A source that compiles to the same object — so the acceptance test arrives with the analogy:
**recompile and compare the zips** (`tools/roundtrip.py`, using the drill gate's own comparator).

**IT IS FAITHFUL TO THE ZIP, NOT TO THE SENTENCE.** Where the parse normalised — a passive folded to
active, «you» resolved to an entity, a word left unplaced — the decompilation says what the zip
holds. That gap is not a defect: it is the misparse signal the brain speaks back («so you mean…?»,
req 3) and an input to the confidence scalar (reqs 4, 6).

**TWO CONSUMERS, AND THE SECOND ONE SETS THE BAR.** Internally the round trip feeds the confidence
scalar. Outwardly the senses speak this text, and rag-out only POLISHES it (senses req 4) — with rag
OFF, this is what ships (rag req 5). So the output must be honest English, not a debug readout, and
the LLM can never invent content because it is handed a sentence that already says exactly what the
zip says.

**THE SPINE IS SYMMETRY, AND IT SETTLES THE FRAME/KNOWLEDGE LINE ONCE.** A decompiling decision lives
where the matching COMPILING decision lives:

    word order · punctuation · clause structure · orthography   FRAME, as decoding is frame
    WHICH WORD carries a meaning                                 KNOWLEDGE — the rows, read backwards

So this module holds no vocabulary. A marker comes from `Box.marker`, which records the preposition
actually used (req 65); everything else is looked up in `language_closed_classes` BY MEANING.

**AND WHERE THE ROWS CANNOT ANSWER, IT REFUSES RATHER THAN CHOOSING.** The inverse map is not a
function — 385 rows carry 81 distinct meanings and 47 of those are many-formed (32 prepositions all
mean `location`, 18 subordinators all mean an asserted `imply`). Where a meaning has exactly one
form, or where curation has flagged one as `spoken`, that form is the answer. Where it has several
and curation has not chosen, this module says nothing and records what it could not say. **An
omission that changes what the sentence CLAIMS is not an omission but a lie**, so a row whose
negation cannot be spoken is not rendered at all: half-said is legal, wrongly-said is the sin
(req 8), in this direction as in the other.

--------------------------------------------------------------------------------------------------
THE SECOND SLICE — A ZIP IS NOT A LIST OF SENTENCES *(2026-09-20)*
--------------------------------------------------------------------------------------------------
The first slice said one content row as one clause. That is right for a zip of one row and wrong for
every other, because **the zip is FLAT and the sentence is NESTED** — Tseitin naming is what made the
format arbitrary-depth without arbitrary nesting (req 33), and the decompiler is where that
transformation is paid back. Four things follow, all of them clause structure and therefore frame:

1. **A row that something else names is not a sentence of its own.** The sentences are the ROOTS —
   rows nothing points at. A join operand is spoken inside its join; a prefix target is spoken
   inside its prefix.
2. **A join is a connective, and which connective is the rows read backwards** — by `operator` AND by
   what the halves claim, which is the difference between «because» and «if» (req 38) and is read
   off the halves' own truth rather than guessed.
3. **A bound variable is spoken where it first occurs**, as the noun phrase its binder describes.
   Later occurrences are definite: a variable mentioned twice is one thing mentioned twice.
4. **AND THE COMPILER DISTRIBUTED WHAT ENGLISH KEEPS TOGETHER.** «a human body in Japan» compiles to
   three rows — B is a body, B is human, B is in Japan — conjoined. Said back as three clauses it is
   unspeakable, because B has no name. So a claimed copular row whose only participant is a variable
   is FOLDED into that variable's phrase, as an adjective or as a marked phrase. It is the inverse of
   the distribution the compiler performed, and it is what lets the join above collapse to the one
   clause that is really being made.

--------------------------------------------------------------------------------------------------
THE THIRD SLICE — AN UNKNOWN IS NOT NOTHING *(schema v4, 2026-09-20)*
--------------------------------------------------------------------------------------------------
An `Open` slot used to say «unbound» and nothing else, so «who» and «what», «he» and «she», «its»
and «his» arrived here indistinguishable — and a word this module cannot tell apart is a word it
cannot say. v4 gives the slot what the SENTENCE said about it, and three kinds of unknown separate
with no heuristic anywhere:

    Open(sort="person")           the sentence ASKED         ->  a question word
    Open(person=3, gender="f")    the sentence DESCRIBED it  ->  «she»
    Open()                        nobody described it        ->  the passive leaves it out
    Open(deixis="place", ...)     the sentence POINTED       ->  «here», never «where» (v10)

*What is still not said is still recorded: `unsaid` names every row and every element that did not
reach the text, so the round trip's number can never flatter itself. And the acceptance test grew a
second half — `tools/roundtrip.py --fixpoint` runs the station against itself, sentence to zip to
sentence to zip, where the two zips must be IDENTICAL.*
"""

from __future__ import annotations

from dataclasses import dataclass, field

from tk2.dictionary import keys
from tk2.language.adverbs import AdverbKinds, standing_adverb_kinds
from tk2.language.compile import ANTECEDENT, ASSERTS_ANTECEDENT, MATRIX, RELATION_FILLS_ROLE
from tk2.language.closed import (
    FOLLOWING_NEGATION,
    FUSED_QUANTIFIER,
    INSIDE,
    OUTSIDE,
    ClosedClasses,
    standing_closed_classes,
)
from tk2.language.inflect import (
    PARTICIPLE, PAST, PLURAL, PRESENT, Inflections, standing_inflections,
)
from tk2.language.utterance import NO_CONTEXT, Context
from tk2.tkzip.schema import (
    Box,
    ContentRow,
    Determination,
    Open,
    Operator,
    Quantity,
    Ref,
    Role,
    Var,
    Zip,
)

#: The subject is the first of these the row fills — the inverse of the compile core's own reading:
#: an agent outranks an experiencer («I love the dog»), and a patient is the subject only when
#: nothing else is («God exists», «the cat is hungry»). WORD ORDER, therefore frame.
SUBJECT_ORDER = (Role.AGENT, Role.EXPERIENCER, Role.PATIENT, Role.TOPIC, Role.COMPLEMENT)

#: What follows the verb directly, in order, before any marked circumstance. `recipient` sits here
#: because English says «give Anna a book» with no marker at all.
OBJECT_ORDER = (Role.RECIPIENT, Role.PATIENT, Role.TOPIC, Role.MEASURE, Role.COMPLEMENT)

#: Manner, then place, then the rest, then time — English's own ordering of circumstances, and frame
#: for the same reason the two above are. A box with a marker carries it; one without is placed by
#: position.
#:
#: **PLACE BEFORE INSTRUMENT**, measured: «you can drive with a licence IN FRANCE» puts the place at
#: the end of the clause, where a FRONTED domain — «In Italy, …» — is the nearer candidate for the
#: location box, and the round trip read `aw-15` as being about the wrong country.
CIRCUMSTANCE_ORDER = (
    Role.MANNER,
    Role.SOURCE, Role.PATH, Role.DIRECTION, Role.DESTINATION, Role.LOCATION,
    Role.INSTRUMENT, Role.COMITATIVE, Role.BENEFICIARY,
    Role.TIME, Role.DURATION,
)

#: The copula. It is not vocabulary in the sense the rows own: a copular row earns no predicate
#: (req 31) because English's «be» carries no meaning there — it is the structure of a predication,
#: which is frame. Recorded here so the audit sees it rather than having to find it.
COPULA = "be"

#: Do-support: English's own repair for a clause that needs a carrier for negation or inversion and
#: has only a lexical verb. Frame — it is word order and nothing else, and the WORD comes from the
#: inflection roster like every other.
DO = "do"

#: The two cases a box position calls for. WHICH form spells a case is knowledge and sits in the
#: rows' `features`; that the subject takes the nominative is grammar, and grammar is frame.
NOMINATIVE = "nominative"
ACCUSATIVE = "accusative"

#: The theatre's time axis, relative to the utterance (`Theatre.interval`): before it, at it,
#: after it. The compiler writes the point and this reads it back — the same three values, because a
#: tense that survives one direction and not the other is a tense that is lost.
BEFORE, AT, AFTER = -1.0, 0.0, 1.0

CLAIMED = 1.0
DENIED = 0.0

#: The roles a joining word is said in, and the clause structure each one is: a coordinator
#: between two clauses, a subordinator in front of the one it marks. Frame: which WORD carries a
#: meaning in each is the rows'.
JOINING_ROLES = ("coordinator", "subordinator")
#: The job of the word that makes a clause an INFINITIVE — «TO sleep» — whose verb is bare and
#: whose subject is somebody else's. A role name of the table's, as the two above are.
INFINITIVE = "infinitive_marker"

#: The boxes a matrix's COMPLEMENTS fill — `obj` and `iobj`, the relations the Captain's control
#: rule names (2026-09-25), read through the compiler's own map so the two directions cannot part.
CONTROLLING = frozenset({RELATION_FILLS_ROLE["obj"], RELATION_FILLS_ROLE["iobj"]})


@dataclass
class Decompiled:
    """The sentence, and an honest account of what did not reach it.

    `unsaid` is `Compiled.unplaced`'s mirror and exists for the same reason: the thing that knows it
    failed to say something is this module, and throwing that away means re-deriving it later,
    expensively and imperfectly. `refused` names the rows that could not be said WITHOUT LYING and
    were therefore not said at all.
    """

    text: str = ""
    unsaid: list[str] = field(default_factory=list)
    refused: list[str] = field(default_factory=list)

    @property
    def whole(self) -> bool:
        return not self.unsaid and not self.refused


@dataclass
class _Said:
    """A rendered stretch of text and the mark that ends it, when it ends one.

    Punctuation is structure on the way in — the compiler reads `?` and `!` and never stores them as
    words — so it is structure on the way out, decided by the row and not by the vocabulary.
    """

    text: str
    mark: str = "."
    #: True when the text already opens with a question word, which is what makes a complementizer
    #: wrong in front of it: «I don't know THAT WHO ate the fish» is not English.
    asks: bool = False


@dataclass
class _Reading:
    """One zip being read backwards: the indexes a sentence needs that a flat row list does not give.

    Built per call and thrown away. The decompiler itself stays stateless — two zips decompiled in
    either order give the same two sentences.
    """

    out: Decompiled
    rows: dict[str, object] = field(default_factory=dict)
    #: target row name -> the prefix rows scoping it, in ZIP ORDER, which is scope order (req 35).
    prefix: dict[str, list] = field(default_factory=dict)
    #: variable name -> the binder that introduces it.
    binders: dict[str, object] = field(default_factory=dict)
    #: variable name -> the claimed copular rows that are really modifiers of its noun phrase.
    modifiers: dict[str, list] = field(default_factory=dict)
    #: content row -> the row an attitude built FROM it scopes. «Suppose the cat is hungry» keeps
    #: both, because the imperative's want must scope a matrix and a prefix row may not scope
    #: another prefix row — so the supposing is a content row AND an attitude, and the content row
    #: is the one that gets spoken.
    complements: dict = field(default_factory=dict)
    #: the attitude rows that link one — already spoken as their content row's verb, so they must
    #: not also wrap the clause they point at.
    linking: set = field(default_factory=set)
    #: rows spoken somewhere other than as a sentence of their own.
    consumed: set = field(default_factory=set)
    #: rows that became part of a noun phrase and must not be said again as clauses.
    folded: set = field(default_factory=set)
    #: rows whose words REACHED the text — rolled back when what they were said inside fails, so a
    #: row counts as spoken only if the sentence carrying it survived. Read once, by `_account`.
    spoken: set = field(default_factory=set)
    #: variable name -> the rows that RESTRICT it, spoken as relative clauses inside its phrase.
    restrictions: dict[str, list] = field(default_factory=dict)
    #: the variable whose box is the ANTECEDENT of the clause being rendered right now, and is
    #: therefore a gap rather than a phrase. Pushed and popped around one clause, like `when`.
    gap: str | None = None
    #: variables already introduced; a second mention is definite, not a second thing.
    said: set = field(default_factory=set)
    #: variables whose BINDER is negated — «not every glitterer is gold». The negation is spoken at
    #: the quantifier, so the phrase is where it has to be delivered.
    negated_binders: set = field(default_factory=set)
    #: WHEN the clause being rendered is set, off its own theatre's time axis (schema v5). Pushed
    #: and popped per row, because «I went to Rome and I WILL GO to Genoa» is two times in one
    #: thought and the tense belongs to the clause, not to the utterance.
    when: float = AT
    #: WHICH ROLE the speaker foregrounded (req 27) — the voice the sentence was heard in.
    topic: object = None
    #: content row -> the head its subject must be, for a row said as a BARE INFINITIVE — the end
    #: of a purpose, whose subject its partner controls and English leaves unsaid (`db/0037`).
    #: Pushed and popped around the one join that says it, like `gap`.
    bare: dict = field(default_factory=dict)


class Decompiler:
    """Zip → sentence. Pure: it reads the rows it is handed and keeps no state between calls."""

    def __init__(self, table: ClosedClasses | None = None,
                 inflections: Inflections | None = None,
                 context: Context = NO_CONTEXT,
                 adverbs: AdverbKinds | None = None) -> None:
        self.table = table if table is not None else standing_closed_classes()
        #: **THE SECOND ROSTER, READ BACKWARDS** (`db/0035`) — the compiler's own `adverbs`, and for
        #: the compiler's reason: «what does this word compile to» has two tables. Asked only where
        #: the closed classes cannot voice a meaning in its position, and never before them.
        self.adverbs = adverbs if adverbs is not None else standing_adverb_kinds()
        #: The spelling rule and the words it gets wrong (`db/0022`). Without it every clause is a
        #: string of lemmas, and a lemma verb is an IMPERATIVE to the parser — 26 of the round
        #: trip's first 32 failures were that one artefact.
        self.inflections = inflections if inflections is not None else standing_inflections()
        #: **THE SAME CONTEXT THE COMPILER TOOK** (`Context`, req 20). The station resolved «I» to
        #: the speaker's key on the way in; without the same object on the way out, `me.n` is spoken
        #: as «me» in subject position and the sentence is not English. Symmetry again: what one
        #: direction consumed, the other needs.
        self.context = context
        self._by_meaning = self._invert(self.table)
        self._spoken = self._voices(self.table)
        self._by_following = self._modals_by_following(self.table)
        self._adverb_forms, self._adverb_spoken = self._adverbs_by_meaning(self.adverbs)
        self._pronouns = self._persons(self.table)
        #: The marker a possessor is said with after its noun — «the result OF perception». The
        #: name is the Box's own FIELD, as `_possessive`'s clitic is looked up by it.
        self._relation_markers = self._markers_yielding(self.table, "relation")

    # -- the rows, read backwards -----------------------------------------------------------------

    @staticmethod
    def _key(role, compiled: dict, sort: str | None = None, number: str | None = None) -> tuple:
        """A row's VOICE — its meaning, the SORT it ranges over, and the NUMBER of noun it takes.

        **`db/0028`'s AND `db/0029`'s `_meaning()` KEY ON THIS AND IT MUST STAY THAT WAY.** Twice in
        two days the key was coarser than the meaning and the loser was silent both times:

            no · nobody      the same `compiled`, and one takes a noun while the other IS one
            every · all      the same quantity, and English picks by the noun's NUMBER

        A dict does not raise when two rows want one slot — it keeps whichever it met last — so a
        check keyed on anything but this is checking a table that does not exist.
        """
        return (role, tuple(sorted((k, str(v)) for k, v in compiled.items())), sort, number)

    @classmethod
    def _invert(cls, table: ClosedClasses) -> dict[tuple, set[str]]:
        """MEANING → the forms that carry it. Built once, like the forward index it mirrors."""
        found: dict[tuple, set[str]] = {}
        for row in table._rows:                       # noqa: SLF001 — the table's own inverse index
            compiled = row.get("compiled") or {}
            if not compiled:
                continue
            features = row.get("features") or {}
            found.setdefault(cls._key(row.get("role"), compiled,
                                      features.get("sort"), features.get("takes_number")),
                             set()).add(row["form"])
        return found

    @classmethod
    def _voices(cls, table: ClosedClasses) -> dict[tuple, str]:
        """MEANING → the one form curation says it is SPOKEN with (`db/0021`'s flag).

        This is where the inverse map stops being a guess. The table's own check holds that at most
        one row per meaning carries it, so a lookup here cannot become a choice made in code.
        """
        found: dict[tuple, str] = {}
        for row in table._rows:                       # noqa: SLF001 — the table's own inverse index
            if not row.get("spoken"):
                continue
            features = row.get("features") or {}
            found[cls._key(row.get("role"), row.get("compiled") or {},
                           features.get("sort"), features.get("takes_number"))] = row["form"]
        return found

    @classmethod
    def _modals_by_following(cls, table: ClosedClasses) -> dict[tuple, set[str]]:
        """(MEANING, where a following «not» scopes) → the forms (`db/0036`). `_invert`, narrowed by
        the one feature that decides which auxiliary can carry a negation inside its modality."""
        found: dict[tuple, set[str]] = {}
        for row in table._rows:                       # noqa: SLF001 — the table's own inverse index
            features = row.get("features") or {}
            where = features.get(FOLLOWING_NEGATION)
            if where is None or not row.get("compiled"):
                continue
            key = cls._key(row.get("role"), row["compiled"], features.get("sort"),
                           features.get("takes_number"))
            found.setdefault((key, where), set()).add(row["form"])
        return found

    def the_modal(self, following: str, **compiled) -> str | None:
        """The auxiliary that says this modality with a «not» after it scoping `following` — the
        flagged voice if it qualifies, else the only form that does, else nothing (`db/0036`'s
        check asks exactly this). «can» is the voice of ◇ and its «not» scopes OUTSIDE, so ◇¬ is
        not «can not»: it is the one possibility whose «not» stays inside, «might»."""
        key = self._key("modality", compiled)
        fits = self._by_following.get((key, following), set())
        spoken = self._spoken.get(key)
        if spoken in fits:
            return spoken
        return next(iter(fits)) if len(fits) == 1 else None

    def _follows_inside(self, form: str) -> bool:
        """Does a «not» after this form stay inside it — «cannot NOT think»?"""
        return any(form in forms for (_key, where), forms in self._by_following.items()
                   if where == INSIDE)

    @classmethod
    def _adverbs_by_meaning(cls, adverbs: AdverbKinds) -> tuple[dict, dict]:
        """MEANING → the adverbs that carry it, and MEANING → the one flagged `spoken` (`db/0035`) —
        `_invert` and `_voices` for the second roster, built the same way and for the same reason.

        **THE KEY IS `_key(None, compiled)`, and `db/0035`'s `_meaning()` is the same key.** An
        adverb row has no closed-class role, sort or number; what it shares with the closed classes
        is the `compiled` vocabulary, and that is the whole of its meaning here.
        """
        forms: dict[tuple, set[str]] = {}
        spoken: dict[tuple, str] = {}
        for row in adverbs._rows:                     # noqa: SLF001 — the table's own inverse index
            compiled = row.get("compiled") or {}
            if not compiled:
                continue
            key = cls._key(None, compiled)
            forms.setdefault(key, set()).add(row["form"])
            if row.get("spoken"):
                spoken[key] = row["form"]
        return forms, spoken

    def the_adverb(self, **compiled) -> str | None:
        """The adverb that voices this meaning — `the_form`'s discipline on the second roster: the
        flagged row answers, a meaning with exactly one adverb answers, and otherwise nothing does
        and the caller records the silence."""
        key = self._key(None, compiled)
        if key in self._adverb_spoken:
            return self._adverb_spoken[key]
        found = self._adverb_forms.get(key, set())
        return next(iter(found)) if len(found) == 1 else None

    @staticmethod
    def _persons(table: ClosedClasses) -> list[dict]:
        """The rows that carry a grammatical PERSON — the person axis, as data rather than as code.

        One list, not three: a pronoun's person, number and gender are the same three features
        whether it is standing in a box (`referential`), possessing something (`possessive`) or
        pointing back at the subject (`reflexive`), and the row's `role` is what says which job it
        does. Reading them together is what lets `me.n` become «I» in one place and «my» in another
        without this module knowing either word.
        """
        return [row for row in table._rows                       # noqa: SLF001
                if (row.get("features") or {}).get("person") is not None
                and not (row.get("features") or {}).get("archaic")
                and not (row.get("features") or {}).get("generic")]

    def forms_for(self, _role: str, _number: str | None = None, **compiled) -> set[str]:
        """Every form the table gives this meaning — empty when it gives none.

        The leading underscore is not decoration: `role` is itself a COLUMN of some meanings —
        an interrogative names the role it opens — so the parameter that carries the row's role
        must not collide with a compiled field of the same name. `_number` is underscored for the
        same reason and is the NOUN's, not the word's.
        """
        return set(self._by_meaning.get(self._key(_role, compiled, number=_number), ()))

    def the_form(self, _role: str, _number: str | None = None, **compiled) -> str | None:
        """The form, when the table names exactly ONE. None when it names several or none.

        This is the whole of the module's vocabulary discipline: a meaning with one spelling is a
        lookup, and a meaning with several is a CHOICE — which is curation, does not live in code,
        and is not made here. The caller records the silence.

        **`_number` IS THE NOUN'S, AND A ROW THAT STATES NONE ANSWERS FOR EITHER** (`db/0029`).
        «every cat» against «all cats» is one quantity and two words that the noun chooses between;
        «no cat» and «no cats» are one word, and its row says so by carrying no number at all. So
        the restricted slot is asked first and the unrestricted one answers only when that slot is
        EMPTY — an ambiguous restricted slot is still an abstention, never a fall-through to a
        different set of words. It is the same «does not distinguish» the pronouns' `either` has
        always meant.
        """
        for wanted in ((_number, None) if _number is not None else (None,)):
            spoken = self._spoken.get(self._key(_role, compiled, number=wanted))
            if spoken is not None:
                return spoken
            found = self.forms_for(_role, _number=wanted, **compiled)
            if found:
                return next(iter(found)) if len(found) == 1 else None
        return None

    # -- the person axis, read backwards -----------------------------------------------------------

    def _features_of(self, key: object) -> dict | None:
        """The person features of the word a key names, when that word is a pronoun of this table.

        `me.n` is the dictionary key the station writes for «me» (req 20), and «me» is a row with
        `person: 1, number: sg`. So the key carries its own person — it does not have to be told —
        and the decompiler never has to know which words are pronouns.
        """
        if not isinstance(key, str) or not keys.is_base_key(key):
            return None
        word = keys.word_of(key).lower()
        for row in self._pronouns:
            if row["form"] == word and row.get("role") == "referential":
                return dict(row.get("features") or {})
        return None

    def _same_person(self, features: dict, role: str, **wanted) -> str | None:
        """The form of `role` that matches these features — the rows answering, not this module.

        `either` on a row's case or number is the row saying it does not distinguish, so it matches
        whatever is asked; a feature the asker does not name is not compared at all.
        """
        found = []
        for row in self._pronouns:
            if row.get("role") != role:
                continue
            feats = row.get("features") or {}
            if feats.get("person") != features.get("person"):
                continue
            if not self._agrees(feats.get("number"), features.get("number")):
                continue
            if not self._agrees(feats.get("gender"), features.get("gender")):
                continue
            if any(not self._agrees(feats.get(k), v) for k, v in wanted.items()):
                continue
            found.append(row)
        if len(found) != 1:
            return None
        return found[0]["form"]

    @staticmethod
    def _agrees(theirs: object, ours: object) -> bool:
        if theirs is None or ours is None or theirs == "either" or ours == "either":
            return True
        return theirs == ours

    def _pronoun(self, key: object, case: str, rd: _Reading) -> str | None:
        """A key spoken as a pronoun in the case its position calls for, or None if it is not one."""
        features = self._features_of(key)
        if features is None:
            return None
        form = self._same_person(features, "referential", case=case)
        if form is None:
            rd.out.unsaid.append(f"«{keys.word_of(str(key))}» in the {case}: no single form")
            return None
        # **«I» IS WRITTEN CAPITALISED** wherever it stands — orthography, like `a`/`an` and like the
        # full stop, and derived from the features rather than from the spelling of the word.
        if features.get("person") == 1 and form != form.upper() and case == NOMINATIVE \
                and self._agrees(features.get("number"), "sg"):
            return form.upper() if len(form) == 1 else form
        return form

    # -- reading the zip ----------------------------------------------------------------------------

    def _read(self, zip_: Zip, out: Decompiled) -> _Reading:
        """The indexes a nested sentence needs from a flat list of rows."""
        rd = _Reading(out=out, rows={row.name: row for row in zip_.rows})
        for row in zip_.rows:
            target = getattr(row, "scopes", None)
            if target is not None:
                rd.prefix.setdefault(target, []).append(row)
            if row.kind == "quantifier":
                rd.binders[row.binds] = row
            if row.kind == "join":
                rd.consumed.update(row.operands)
        # **A ROW THAT CLAIMS NOTHING AND SHARES A BINDER'S VARIABLE IS THAT BINDER'S RELATIVE
        # CLAUSE**, not a sentence of its own. «Every cat THAT SLEEPS is happy» — the clause says
        # WHICH cats are meant, and the compiler marks it by leaving the truth slot empty (the 1st
        # Officier's rule: a restriction is stated, never claimed).
        #
        # **DROPPING IT IS NOT BREVITY, IT IS A WIDER CLAIM THAN THE ZIP HOLDS** — «Every cat is
        # happy» says something «every cat that sleeps is happy» does not, which is req 8's sin
        # wearing the appearance of a shorter sentence. So the row is consumed here and spoken
        # inside the phrase, where English puts it.
        #
        # *A join's operands are already consumed above, which is what keeps the halves of «if it
        # rains I stay home» — both unasserted, both over the same variable — out of this.*
        #
        # **WHATEVER ITS TRUTH** *(2026-09-24, G4b)*. Keyed on an empty truth slot, the rule missed
        # the relative clauses that ARE claimed: a definite description's («the cat that sleeps» —
        # a presupposition, so the brain gets the fact) and schema v8's quantity-less binder's.
        # Both came back as two sentences, «The cat sleeps. The cat is happy.» What makes a row a
        # relative clause is its SHAPE — it shares the variable of a binder that does not scope it,
        # and no join names it — and the truth decides only whether it can be said as one
        # (`_restricting`).
        for row in zip_.rows:
            if row.kind != "content" or row.name in rd.consumed:
                continue
            shared = {box.head.name for box in row.boxes.values()
                      if isinstance(box.head, Var) and box.head.name in rd.binders
                      and rd.binders[box.head.name].scopes != row.name}
            if len(shared) == 1:
                rd.restrictions.setdefault(shared.pop(), []).append(row)
                rd.consumed.add(row.name)
        # **AN ATTITUDE WHOSE OWN CLAUSE SURVIVED IS THAT CLAUSE'S COMPLEMENT.** The compiler
        # dissolves a clause into the attitude it became — unless something else names it, which is
        # exactly the imperative's shape: «Suppose the cat is hungry» is a WANT over a supposing,
        # and the supposing must stay a content row for the want to scope. Both rows are one clause,
        # and the sentence says the verb once with its content after it.
        for row in zip_.rows:
            if row.kind != "attitude":
                continue
            source = next((other for other in zip_.rows
                           if other.kind == "content" and other.predicate == row.verb
                           and other.name != row.scopes), None)
            if source is not None:
                rd.complements[source.name] = row.scopes
                rd.consumed.add(row.scopes)
                rd.linking.add(row.name)
        self._fold(zip_, rd)
        return rd

    def _fold(self, zip_: Zip, rd: _Reading) -> None:
        """Put back inside the noun phrase what the compiler distributed out of it.

        «a human body in Japan» is three rows and one phrase. A claimed copular row whose only
        participant is a bound variable is not a clause at all — it is what English says as an
        adjective or as a marked phrase hanging off the noun — and saying it as a clause is
        impossible anyway, because a variable has no name to be the subject of one.
        """
        conjoined = {operand for row in zip_.rows if row.kind == "join"
                     and row.operator is Operator.AND for operand in row.operands}
        for row in zip_.rows:
            if row.kind != "content" or row.truth != CLAIMED or row.pov is not None:
                continue
            if row.predicate is not None or len(row.boxes) != 2:
                continue
            # **ONLY OUT OF A CONJUNCTION.** A modifier distributes over «and» and nowhere else: the
            # antecedent of an implication says «every person WHO says a falsehood», which is a
            # relative clause and a different thing from «every wrong person». Folding it would move
            # what is asserted, which is the one move this module may never make.
            if row.name not in conjoined:
                continue
            carrier = [(role, box) for role, box in row.boxes.items()
                       if isinstance(box.head, Var) and self._bare(box)]
            if len(carrier) != 1:
                continue
            var = carrier[0][1].head.name
            if var not in rd.binders or rd.prefix.get(row.name):
                continue
            other = next(box for role, box in row.boxes.items() if role != carrier[0][0])
            if other.marker is None and not self._adjective(other):
                continue
            rd.modifiers.setdefault(var, []).append(row)
            rd.consumed.add(row.name)
            rd.folded.add(row.name)

    @staticmethod
    def _said_marked(box: Box) -> bool:
        """Is this box's marker SAID? — a box may carry one the sentence only understood."""
        return bool(box.marker) and not box.marker_implicit

    @staticmethod
    def _bare(box: Box) -> bool:
        """A box that holds a variable and says nothing else about it."""
        return (box.marker is None and box.quantity is None and box.count is None
                and box.determination is None and box.relation is None)

    @staticmethod
    def _adjective(box: Box) -> bool:
        return (isinstance(box.head, str) and keys.is_base_key(box.head)
                and keys.pos_of(box.head) == "a" and box.marker is None)

    # -- the sentence ------------------------------------------------------------------------------

    def decompile(self, zip_: Zip) -> Decompiled:
        """Every ROOT row as a sentence — a root being a row nothing else in the zip names.

        A join operand is spoken inside its join, a prefix target inside its prefix, a folded
        modifier inside a noun phrase. What is left is what the zip is actually saying.
        """
        out = Decompiled()
        rd = self._read(zip_, out)
        rd.topic = zip_.topicality
        sentences = []
        for row in zip_.rows:
            if row.name in rd.consumed or getattr(row, "scopes", None) is not None:
                continue
            if row.kind not in ("content", "join"):
                continue
            said = self._render(row.name, rd)
            if said is None or not said.text.strip():
                out.refused.append(f"{row.kind} row {row.name}")
                continue
            sentences.append(said)
        out.text = " ".join(self._finish(s) for s in sentences)
        self._account(zip_, rd)
        return out

    @staticmethod
    def _account(zip_: Zip, rd: _Reading) -> None:
        """**EVERY ROW `_read` CONSUMED IS SPOKEN OR NAMED** *(2026-09-24, G4a)*.

        Consuming a row is a promise: it will be said inside something else, so it is not said as a
        sentence. A promise the phrase then fails to keep — a fused «something» that returned before
        its relative clause, a modifier whose phrase came back empty — used to leave no trace at
        all, and a phrase without its restriction claims MORE than the zip (req 8). So the promise
        is checked where it can no longer be forgotten: after the last sentence, against what
        actually reached the text.

        *Named even when another entry already mentions it*: a row can be mentioned for one reason
        («held at None») and lost for another, and matching on the mention would let the second
        hide behind the first. A duplicate costs a line; a masked loss costs the invariant.
        """
        for row in zip_.rows:
            name = row.name
            if name not in rd.consumed or name in rd.spoken:
                continue
            rd.out.unsaid.append(f"{row.kind} row {name}: read as part of another row, and it "
                                 f"never reached the text")

    @staticmethod
    def _finish(said: _Said) -> str:
        """Capital, then the mark the structure asked for. Orthography, and orthography is frame —
        the compiler reads the `?` and the `!` as structure and never as vocabulary, so the
        decompiler writes them the same."""
        text = said.text.strip()
        return (text[:1].upper() + text[1:] + said.mark) if text else ""

    # -- a row, with everything that scopes it ------------------------------------------------------

    def _render(self, name: str, rd: _Reading, embedded: bool = False) -> _Said | None:
        """One row and its prefix — the five scope-bearing elements, in the order the zip holds them.

        Each element is placed where English places it: a quantifier inside the noun phrase it binds,
        a modality on the verb, a domain at the front, an attitude wrapped around the whole. A
        NEGATION attaches to whatever comes NEXT in scope order, which is the whole of the difference
        between «not all that glitters is gold» and «all that glitters is not gold» — two zips that
        differ only in the order of two prefix rows, and two readings English spells the same way.
        """
        row = rd.rows.get(name)
        if row is None:
            return None
        # **THE TENSE IS THE CLAUSE'S** (schema v5). Pushed for the rows under this one and popped
        # after, so a conjunction of two times says both: «I went to Rome and I will go to Genoa».
        outer_when, rd.when = rd.when, self._when(row)
        before = set(rd.spoken)
        try:
            said = self._say(row, name, rd, embedded)
        finally:
            rd.when = outer_when
        if said is None or not said.text.strip():
            rd.spoken = before                         # what was said under it never arrived
            return said
        rd.spoken.add(name)
        return said

    @staticmethod
    def _when(row) -> float:
        """The point on the theatre's time axis this row is set at — the present where none is
        given, because a tenseless row is one the brain built for itself."""
        theatre = getattr(row, "theatre", None)
        return AT if theatre is None else theatre.interval[0]

    def _say(self, row, name: str, rd: _Reading, embedded: bool) -> _Said | None:
        """`_render`'s body, with this row's tense already in force."""
        # An attitude that only links a clause to its complement is spoken as that clause's VERB,
        # so it must not wrap the complement as well — «Suppose that (somebody) supposes the cat…».
        prefix = [element for element in rd.prefix.get(name, [])
                  if element.name not in rd.linking]

        # **A NEGATION APPLIES TO WHAT FOLLOWS IT IN SCOPE ORDER**, and where it cannot be
        # delivered the ROW IS REFUSED. Dropping it would not lose half a sentence: it would produce
        # the sentence's own opposite, which is the one thing req 8 forbids in either direction.
        negated_by: set[int] = set()
        negate_clause = False
        owed = []
        for at, element in enumerate(prefix):
            if element.kind != "negation":
                continue
            following = prefix[at + 1] if at + 1 < len(prefix) else None
            if following is None:
                negate_clause = True
            elif following.kind == "quantifier":
                rd.negated_binders.add(following.binds)
                owed.append(following.binds)
            elif following.kind in ("attitude", "modality"):
                negated_by.add(id(following))
            else:
                rd.out.refused.append(f"{name}: a negation over a {following.kind} cannot be said")
                return None

        # **A «NOT» INSIDE THE MODALITY IS SAID AFTER ITS AUXILIARY** — and only an auxiliary whose
        # row says its «not» scopes inside can carry it (`db/0036`): «can not» is ¬◇, not ◇¬.
        inside = negate_clause or getattr(row, "truth", None) == DENIED
        modal = adverb = ""
        fused = False
        for element in prefix:
            if element.kind != "modality":
                continue
            if id(element) in negated_by:
                # **A FORM THAT FUSES THE NEGATION OUTSIDE ITS MODALITY SAYS IT FIRST** — «cannot»
                # is ¬◇ in one word (`db/0036`), and the closed classes answer before the adverbs.
                form = self.the_form("modality", kind="prefix", element="modality",
                                     modality=element.modality.value, negation=OUTSIDE)
                if form is not None:
                    if modal or adverb or (inside and not self._follows_inside(form)):
                        rd.out.refused.append(f"{name}: a negated {element.modality.value} beside "
                                              f"another modality or negation cannot be ordered")
                        return None
                    modal, fused = form, True
                    continue
                # **«must not» is not «not must».** An auxiliary stands BEFORE the negation, so it
                # can only put the negation inside: saying the modal here would claim the opposite.
                # An adverb stands AFTER it — «does NOT NECESSARILY think» — and that is the one
                # order English has for a negation outside a modality. The order is frame; WHICH
                # adverb is the second roster's, read backwards (`db/0035`).
                form = self.the_adverb(kind="prefix", element="modality",
                                       modality=element.modality.value)
                if form is None:
                    rd.out.refused.append(f"{name}: a negation outside a {element.modality.value} "
                                          f"has no form in the table")
                    return None
                if negate_clause or adverb or getattr(row, "truth", None) == DENIED:
                    # «does not necessarily NOT think» — a second negation inside the first has no
                    # carrier left, and dropping either one says something the zip does not.
                    rd.out.refused.append(f"{name}: a negation outside a {element.modality.value} "
                                          f"and another one inside it cannot both be said")
                    return None
                adverb = form
                continue
            if inside:
                form = self.the_modal(INSIDE, kind="prefix", element="modality",
                                      modality=element.modality.value)
                if form is None:
                    rd.out.refused.append(f"{name}: no auxiliary says a negation inside a "
                                          f"{element.modality.value}")
                    return None
            else:
                form = self.the_form("modality", kind="prefix", element="modality",
                                     modality=element.modality.value)
            if form is None:
                rd.out.refused.append(f"{name}: the table names several forms for "
                                      f"{element.modality.value} and none is preferred")
                return None
            if fused:
                rd.out.refused.append(f"{name}: a negated modality beside another modality cannot "
                                      f"be ordered in one clause")
                return None
            modal = form
        if adverb and modal:
            # Two modalities and one of them outside a negation: which one the negation sits between
            # is the whole claim, and one auxiliary slot plus one adverb slot cannot show it.
            rd.out.refused.append(f"{name}: a negated modality beside another modality cannot be "
                                  f"ordered in one clause")
            return None

        attitudes = [element for element in prefix if element.kind == "attitude"]
        imperative = self._imperative(row, attitudes, rd)
        if imperative is not None:
            if adverb:
                rd.out.refused.append(f"{name}: an imperative has no place for «not {adverb}»")
                return None
            return imperative

        # **THE NEGATION CARRIES THE ADVERB**: «not necessarily» is said where «not» is, so every
        # carrier the clause already knows — do · is · will — takes it with no rule of its own.
        body = self._body(row, rd, negated=negate_clause or bool(adverb), modal=modal,
                          embedded=embedded or bool(attitudes), asks=bool(attitudes),
                          adverb=adverb)
        if body is None:
            return None

        for element in reversed(attitudes):
            body = self._attitude(element, body, negated=id(element) in negated_by, rd=rd)
            if body is None:
                return None

        for element in prefix:
            if element.kind != "domain":
                continue
            if element.domain.marker is None:
                # «legally» is an ADVERB derived from `law.n`, and the table holds no derivation.
                # Fronting the bare noun would say «Law, he is married», which is not the claim.
                rd.out.unsaid.append(f"{element.name}: an unmarked domain has no form to be said in")
                continue
            said = self._phrase(element.domain, rd)
            if said:
                body = _Said(f"{said}, {body.text}", body.mark, asks=body.asks)
            else:
                rd.out.unsaid.append(f"{element.name}: the domain could not be said")

        # A binder that never reached a variable site said nothing at all — and if it was the one
        # carrying a NEGATION, the sentence that came back is the opposite of the zip.
        for element in prefix:
            if element.kind == "quantifier" and element.binds not in rd.said:
                rd.out.unsaid.append(f"{name}: the binder for {element.binds} reached no box")
        undelivered = [binds for binds in owed if binds in rd.negated_binders]
        if undelivered:
            rd.out.refused.append(f"{name}: a negation over {', '.join(undelivered)} was not said")
            return None
        return body

    def _body(self, row, rd: _Reading, negated: bool, modal: str,
              embedded: bool, asks: bool, adverb: str = "") -> _Said | None:
        if row.kind == "join":
            if negated or modal:
                rd.out.unsaid.append(f"{row.name}: a join cannot carry a modality or a negation yet")
            return self._join(row, rd, embedded=embedded)
        if row.kind == "content":
            return self._clause(row, rd, negated=negated, modal=modal, embedded=embedded,
                                asks=asks, adverb=adverb)
        rd.out.unsaid.append(f"{row.kind} row {row.name}")
        return None

    # -- the join ------------------------------------------------------------------------------------

    def _join(self, row, rd: _Reading, embedded: bool) -> _Said | None:
        """`Y = A op B` as a connective between two clauses — the rows read backwards by MEANING.

        The meaning of a connective is its operator AND what it asserts about its halves, and the
        second half of that is not a guess: it is written in the halves' own `truth`. «I stayed home
        because it rained» claims both; «if it rains I stay home» claims neither; same operator, and
        `db/0010` ruled that the difference is exactly this (req 38). So the key is read off the zip
        and the form comes from the table.
        """
        if not any(operand in rd.folded for operand in row.operands) \
                and self._asserts(row, rd) == ASSERTS_ANTECEDENT:
            return self._purpose(row, rd)
        halves = [None if operand in rd.folded else self._render(operand, rd, embedded=True)
                  for operand in row.operands]
        alive = [half for half in halves if half is not None and half.text.strip()]
        if not alive:
            return None
        if len(alive) == 1:
            # Everything the other half said was folded into a noun phrase — which is the normal
            # outcome, not a loss: «a human body in Japan» IS those rows. **Unless the survivor is
            # the half that claims nothing**: without its connective, a clause standing alone is a
            # declarative, and a declarative asserts by being one. That is the join's own version of
            # the negation rule, and it was found by the round trip saying «You learn the thing» for
            # a row the zip only SUPPOSES.
            survivor = next(operand for operand, half in zip(row.operands, halves)
                            if half is not None and half.text.strip())
            # *A row said as a bare infinitive does not stand alone* — «to see the Ligurian sea» is
            # the end of a purpose, and its partner is what claims (`_purpose`).
            if getattr(rd.rows.get(survivor), "truth", None) is None and survivor not in rd.bare:
                rd.out.refused.append(f"{row.name}: its unclaimed half would stand alone as a claim")
                return None
            return alive[0]

        asserts = self._asserts(row, rd)
        if asserts == "neither" and row.truth is None:
            # **A JOIN SUPPOSED WITH ITS HALVES** (G9) — «If I go AND you stay, …». Its halves
            # claim exactly what it does, which is the `both` of a claimed join one level down, and
            # the truth slot cannot tell that from a supposed `neither`. So it is said only where
            # the operator has ONE of the two in the table — «and» has no `neither` — and refused
            # where it has both: a supposed «because» and a supposed «if» are one zip.
            readings = [key for key in ("both", "neither")
                        if self._connective(row.operator.value, key)[0] is not None]
            if len(readings) != 1:
                rd.out.refused.append(f"{row.name}: supposed with its halves, and the table has "
                                      f"{len(readings)} readings of {row.operator.value} for that")
                return None
            asserts = readings[0]
        if asserts is None:
            rd.out.unsaid.append(f"{row.name}: halves claimed unevenly, and no connective says that")
            return None
        form, role = self._connective(row.operator.value, asserts)
        if form is None:
            rd.out.unsaid.append(f"{row.name}: no form in the table for {row.operator.value} "
                                 f"asserting {asserts}")
            return None
        if role != "coordinator" and any(half.mark == "!" for half in alive):
            # «If go, you sleep» — an imperative is a clause of its own; no subordinator marks one,
            # and a zip whose shape reads that way has lost which half was wanted.
            rd.out.refused.append(f"{row.name}: an imperative cannot be the clause a {role} marks")
            return None
        if role == "subordinator":
            # «Because it rained, I stayed home» — the marked half is the FIRST operand, which is the
            # antecedent for every implication in the table and is order-free for the rest.
            return _Said(f"{form} {alive[0].text}, {alive[1].text}", alive[1].mark,
                         asks=alive[0].asks)
        return _Said(f"{alive[0].text} {form} {alive[1].text}", alive[1].mark, asks=alive[0].asks)

    def _purpose(self, row, rd: _Reading) -> _Said | None:
        """`imply(act, end)` with the act claimed and the end not — «I go TO SLEEP» (`db/0037`).

        **THE INVERSE OF THE COMPILER'S CONTROL, AND NOTHING ELSE.** The end's subject is the one
        its partner controls — the partner's `obj`/`iobj` if it has one, else its subject — and
        English leaves it unsaid, so it must BE that one: a purpose whose subject is somebody else
        («I go for you to sleep») has no form here and is refused, never said with the wrong
        sleeper. The word comes from the table, which voices the purpose with the infinitive.
        """
        form, _role = self._connective(row.operator.value, ASSERTS_ANTECEDENT)
        if form is None:
            rd.out.unsaid.append(f"{row.name}: no form in the table says a purpose")
            return None
        # **BARE WHEN THE VOICE IS THE INFINITIVE'S OWN WORD** — «to» is the purpose's voice and also
        # the infinitive marker, so its clause is said the way an infinitive is: no subject, no
        # tense. A finite voice («so that») would take a clause of its own.
        bare = any(r["form"] == form and r.get("role") == INFINITIVE
                   for r in self.table._rows)                           # noqa: SLF001
        act_name, end_name = row.operands
        controller = None
        if bare:
            act_row = self._matrix_of(act_name, rd)
            controller = self._controller(act_row) if act_row is not None else None
            if controller is None:
                rd.out.refused.append(f"{row.name}: nothing in its act controls the purpose")
                return None
        act = self._render(act_name, rd, embedded=True)
        if act is None or not act.text.strip():
            return None
        ends = self._contents_under(end_name, rd) if bare else set()
        for name in ends:
            rd.bare[name] = controller
        try:
            end = self._render(end_name, rd, embedded=True)
        finally:
            for name in ends:
                rd.bare.pop(name, None)
        if end is None or not end.text.strip():
            rd.out.unsaid.append(f"{row.name}: the end of the purpose could not be said")
            return None
        return _Said(f"{act.text} {form} {end.text}", act.mark, asks=act.asks)

    def _matrix_of(self, name: str, rd: _Reading):
        """The content row a join stands for when everything else in it was folded into a phrase —
        «the old man» is a join of the man's row and the adjective's. None when two rows remain."""
        row = rd.rows.get(name)
        if row is None or row.kind == "content":
            return row
        if row.kind != "join":
            return None
        left = [operand for operand in row.operands if operand not in rd.folded]
        return self._matrix_of(left[0], rd) if len(left) == 1 else None

    def _contents_under(self, name: str, rd: _Reading) -> set[str]:
        """Every content row a join spells out, through its joins and never into a phrase."""
        row = rd.rows.get(name)
        if row is None or name in rd.folded:
            return set()
        if row.kind == "content":
            return {name}
        if row.kind == "join":
            return {found for operand in row.operands for found in self._contents_under(operand, rd)}
        return set()

    @staticmethod
    def _controller(row) -> object | None:
        """Who controls a purpose this row is the act of — the compiler's rule read backwards: the
        one complement said bare after the verb, else the subject. Two complements name none."""
        subject = next((role for role in SUBJECT_ORDER if role in row.boxes), None)
        complements = [role for role in row.boxes
                       if role in CONTROLLING and role is not subject
                       and not Decompiler._said_marked(row.boxes[role])]
        if len(complements) > 1:
            return None
        chosen = complements[0] if complements else subject
        return row.boxes[chosen].head if chosen is not None else None

    def _asserts(self, row, rd: _Reading) -> str | None:
        """What this join's halves claim, as the table spells it: `both` · `neither` ·
        `antecedent` — the last a purpose's (`db/0037`): the act, first, claimed; the end not."""
        claims = []
        for operand in row.operands:
            half = rd.rows.get(operand)
            truth = getattr(half, "truth", None)
            claims.append("open" if isinstance(truth, Open) else
                          "empty" if truth is None else "claimed")
        if claims == ["claimed", "claimed"]:
            return "both"
        if claims == ["empty", "empty"]:
            return "neither"
        if claims == ["claimed", "empty"] and row.operator is Operator.IMPLY \
                and row.truth == CLAIMED:
            return ASSERTS_ANTECEDENT
        return None

    def _connective(self, operator: str, asserts: str) -> tuple[str | None, str | None]:
        """The word for an operator-and-assertion, and the ROLE it is said in — which is the clause
        structure: `JOINING_ROLES`.

        A coordinator and a subordinator carrying the same meaning are two clause structures for one
        thought, and which structure is used is frame; but the WORD is the table's, so a meaning with
        two roles both flagged `spoken` is curation contradicting itself and is reported rather than
        resolved here.

        **A PURPOSE'S ANTECEDENT IS ITS MATRIX** (`db/0037`), and that is part of its meaning: the
        first operand is said as the main clause, so the rows asked are the ones whose antecedent is
        the matrix. `db/0037`'s check asks the same question.
        """
        meaning = {"kind": "join", "operator": operator, "asserts": asserts}
        if asserts == ASSERTS_ANTECEDENT:
            meaning[ANTECEDENT] = MATRIX
        found = [(role, self._spoken.get(self._key(role, meaning))) for role in JOINING_ROLES]
        voiced = [(role, form) for role, form in found if form is not None]
        if len(voiced) == 1:
            return voiced[0][1], voiced[0][0]
        if len(voiced) > 1:
            return None, None
        single = [(role, self.forms_for(role, **meaning)) for role in JOINING_ROLES]
        lone = [(role, forms) for role, forms in single if len(forms) == 1]
        if len(lone) == 1:
            return next(iter(lone[0][1])), lone[0][0]
        return None, None

    # -- the attitude --------------------------------------------------------------------------------

    def _attitude(self, element, body: _Said, negated: bool, rd: _Reading) -> _Said | None:
        """«Anna thinks that …» — a holder, a verb, and the complementizer the table names.

        The complementizer is not punctuation and not a choice: `that` is the one form the table
        gives for a join that asserts only its matrix, which is precisely what an attitude does to
        the clause under it.
        """
        # **THE SAYING HAS ITS OWN TIME** (schema v5): «John SAID that the sky IS green». Restored
        # before the body is appended, so what is quoted keeps the tense it was quoted in.
        inner_when, rd.when = rd.when, self._when(element)
        try:
            return self._attitude_said(element, body, negated, rd, inner_when)
        finally:
            rd.when = inner_when

    def _attitude_said(self, element, body: _Said, negated: bool, rd: _Reading,
                       inner_when: float) -> _Said | None:
        agreement = self._agreement(element.holder, rd)
        holder = self._phrase(element.holder, rd, case=NOMINATIVE)
        if not holder:
            rd.out.unsaid.append(f"{element.name}: the attitude's holder could not be said")
            return None
        said = [holder]
        if negated:
            form = self.the_form("negation", kind="prefix", element="negation")
            if form is None:
                rd.out.refused.append(f"{element.name}: the negation has no single form")
                return None
            said += [self._agreeing(DO, agreement, rd), form, keys.word_of(element.verb)]
        else:
            said.append(self._agreeing(keys.word_of(element.verb), agreement, rd))
        if element.addressee is not None:
            # **MARKED, AND THE MARKER IS THE TABLE'S.** «say TO Marie» is right and «tell TO me» is
            # not: whether an attitude verb marks its addressee or takes it bare is LEXICAL, and
            # nothing in tk2 holds that fact yet (req 55 rules the CLASSIFICATION of attitude verbs,
            # not their syntax). Measured both ways on the corpus: marking costs one case and
            # leaving it bare costs two, and a marked phrase names its role out loud.
            # The box may already carry the word the sentence used (req 65); only an addressee that
            # arrived unmarked has to be asked about.
            to = "" if element.addressee.marker else self._marker_for("recipient")
            spoken = self._phrase(element.addressee, rd, case=ACCUSATIVE)
            if spoken:
                said.append(f"{to} {spoken}" if to else spoken)
        if element.strength is not None:
            rd.out.unsaid.append(f"{element.name}: a strength of {element.strength} is not spoken")
        rd.when = inner_when
        complementizer = self._complementizer(body)
        said.append(f"{complementizer} {body.text}" if complementizer else body.text)
        return _Said(" ".join(said), "." if body.mark != "?" else "?")

    def _marker_for(self, role: str) -> str:
        """The preposition that marks a role, when the table names exactly one that CAN mark it.

        A parsed box already carries the word it met (req 65) and never asks this. An attitude's
        addressee is not a box the sentence marked — it is a field of the row — so the marker has to
        be found, and `roles` is the column that knows: exactly one form in the table can mark a
        recipient, which is why this is a lookup rather than a choice.
        """
        return self.table.marker_for(role) or ""

    def _complementizer(self, body: _Said) -> str:
        """`that`, except before a clause that already opens with its own wh-word.

        «I don't know THAT WHO ate the fish» is not English: an embedded question is introduced by
        the question word itself, which the clause has already put at its front.
        """
        if body.asks:
            return ""
        return self.the_form("subordinator", kind="join", operator="and", asserts="matrix") or ""

    def _imperative(self, row, attitudes: list, rd: _Reading) -> _Said | None:
        """«Close the door!» — the inverse of the compiler's own imperative (task 2d).

        The shape is the drill's and the compiler builds exactly it: the SPEAKER wants something of
        the ADDRESSEE, and nothing is claimed. Recognising it here is not a special case bolted on —
        it is the same rule read in the other direction, and without it the sentence comes back as
        «I want you to close the door», which is a different zip.
        """
        if len(attitudes) != 1 or row.kind != "content" or row.truth is not None:
            return None
        element = attitudes[0]
        if keys.word_of(element.verb) != "want":
            return None
        holder = getattr(element.holder, "head", None)
        if holder is None or holder != self.context.speaker:
            return None
        subject_role = next((role for role in SUBJECT_ORDER if role in row.boxes), None)
        if subject_role is None:
            return None
        if getattr(row.boxes[subject_role], "head", None) != self.context.addressee:
            return None
        rest = dict(row.boxes)
        rest.pop(subject_role)
        said = self._clause(row.model_copy(update={"boxes": rest, "truth": CLAIMED}), rd,
                            negated=False, modal="", embedded=False, imperative=True)
        if said is None:
            return None
        if element.strength is not None:
            rd.out.unsaid.append(f"{element.name}: a strength of {element.strength} is not spoken")
        return _Said(said.text, "!")

    # -- the clause -----------------------------------------------------------------------------------

    def _clause(self, row: ContentRow, rd: _Reading, negated: bool, modal: str,
                embedded: bool, asks: bool = False, imperative: bool = False,
                adverb: str = "") -> _Said | None:
        """One content row to one clause, or None when it cannot be said without lying."""
        if row.name in rd.bare and not imperative:
            return self._infinitive(row, rd, negated or bool(modal) or bool(adverb))
        boxes = dict(row.boxes)
        asked = isinstance(row.truth, Open)

        if row.truth is None and not imperative and not embedded:
            # **A ROW THAT CLAIMS NOTHING IS SAYABLE EXACTLY WHEN SOMETHING ABOVE IT SAYS SO.** The
            # antecedent of «if it rains, I stay home» claims nothing and the JOIN is what is
            # asserted there (req 38); standing alone, the same row is a sentence English has no
            # form for, because a declarative clause asserts by being one.
            rd.out.unsaid.append(f"{row.name} is stated but claims nothing, and no form says that")
            return None
        if not asked and not imperative and row.truth not in (CLAIMED, DENIED):
            rd.out.unsaid.append(f"{row.name} is held at {row.truth} and a hedge is not built yet")

        negated = negated or (not asked and row.truth == DENIED)
        negation = self.the_form("negation", kind="prefix", element="negation")
        if negated and negation is None:
            # The table gives «not» and «no» the same meaning, so nothing here can choose. Saying
            # the clause without its negation would say the OPPOSITE of the zip.
            rd.out.refused.append(f"{row.name}: the negation has no single form in the table")
            return None
        if adverb:
            negation = f"{negation} {adverb}"
        if row.pov is not None:
            rd.out.unsaid.append(f"{row.name}: a point of view held by "
                                 f"«{keys.word_of(str(getattr(row.pov.holder, 'head', '?')))}»")

        # **AN OPEN BOX IS NOT ALWAYS A QUESTION.** «The hammer is made of titanium» leaves its
        # agent open because nobody knows who made it, not because anybody is asking; the zip records
        # both as OPEN and nothing distinguishes them (req 2 — an unbound slot is a variable at every
        # depth). What distinguishes them here is the SENTENCE: an open box is asked when the clause
        # is a question, or when it stands under an attitude, which is what an embedded question is.
        # **AN OPEN BOX IS A SLOT TO SOLVE FOR** (req 2), and English has two ways of saying one:
        # ask about it, or — for an AGENT, and only for an agent — leave it out with the passive.
        # «The hammer is made of titanium» does not ask who made it; «Who ate the fish?» does. The
        # agent is where the two readings meet, and what separates them is whether anything is being
        # asked at all: a clause under an attitude is an embedded question, a clause standing alone
        # and claiming something is not.
        wh, wh_role = self._question_word(boxes, rd)
        gap_marker = None
        if rd.gap is not None:
            # **THE ANTECEDENT IS NOT SAID TWICE.** Inside a relative clause the shared variable IS
            # the noun the phrase already named, and English leaves a gap with a relative pronoun in
            # it: «the cat THAT sleeps», «the fish THAT the cat ate». That is the same shape a
            # question leaves behind, so it takes the same path — which is what makes a subject
            # relative not invert and an object relative front its pronoun, for free.
            antecedent = next((role for role, box in boxes.items()
                               if isinstance(box.head, Var) and box.head.name == rd.gap), None)
            if antecedent is not None:
                relative = self.the_form("relative", kind="open", binds="antecedent")
                if relative is None:
                    rd.out.unsaid.append(f"{row.name}: the table names no single relative pronoun")
                    return None
                wh, wh_role = relative, antecedent
                # **A MARKED GAP STRANDS ITS MARKER** — «the minds that you learn FROM». Popping the
                # box with the relative pronoun in it would drop the marker with it, and the
                # antecedent would come back in the wrong role: «the house that I live» is not a
                # place. `that` cannot be pied-piped («in that I live»), so English strands.
                gap_marker = boxes[antecedent].marker
        if wh_role is Role.AGENT and not (asked or asks) and row.predicate is not None \
                and len(boxes) > 1 and isinstance(boxes[wh_role].head, Open) \
                and not boxes[wh_role].head.described:
            # An agent nobody described and nobody asked about is what the PASSIVE leaves out.
            # One the sentence described — «who», «what» — is a question, wherever it stands.
            #
            # **AND A RELATIVE GAP IS NEITHER** *(2026-09-24)*: its head is the antecedent's
            # VARIABLE, which is not an unknown agent but a known one — «every mind that TRUSTS
            # you». Reading `.described` off it raised, and passivising it would have said the
            # clause without its subject; only an OPEN head can be the agent nobody named.
            wh, wh_role = None, None
        # **A CONJUNCT WITH NOTHING BUT A COMPLEMENT HAS AN ELIDED SUBJECT.** «The cat is dead and
        # alive» — English says the shared subject once, and the second half is the complement
        # alone. Said with a subject of its own it becomes «and alive is», which makes the adjective
        # the thing that is. Only inside a join: standing alone, «is alive» is not a sentence.
        if (embedded and not imperative and row.predicate is None and row.truth == CLAIMED
                and set(boxes) == {Role.COMPLEMENT} and not rd.prefix.get(row.name)):
            said = self._phrase(boxes[Role.COMPLEMENT], rd)
            return _Said(said) if said else None

        # **AN IMPERATIVE HAS NO SUBJECT** — the compiler put the addressee in the box a subject
        # would have taken, and this is the same step backwards: the box is already gone.
        subject_role = None if imperative else next(
            (role for role in SUBJECT_ORDER if role in boxes), None)

        # **A QUESTION WORD THAT IS THE SUBJECT DOES NOT MOVE, AND NOTHING INVERTS.** «Who ate the
        # fish?» — the gap is already at the front, so English leaves the clause alone; it is «What
        # did he eat?» that fronts a word and pulls the auxiliary with it. Said the other way round,
        # «who the fish eats» makes the fish the eater.
        wh_is_subject = wh is not None and wh_role is subject_role
        if wh is not None:
            boxes.pop(wh_role)
            if wh_is_subject:
                subject_role = next((role for role in SUBJECT_ORDER if role in boxes), None)

        # **THE VOICE THE SENTENCE WAS HEARD IN** (req 27). Roles normalize, so «the mail was written
        # by John» and «John wrote the mail» are one zip — and `topicality` is the one marker that
        # keeps what normalization would otherwise destroy. Where it names a role that the active
        # voice would not have made the subject, English has exactly one way to say it, and that way
        # is the passive.
        # **TOPICALITY NAMING A NON-AGENT IS WHAT A PASSIVE IS.** Not «the foregrounded role is not
        # the one the active voice would pick» — that test fails exactly where the passive matters
        # most, on «The hammer is made of titanium», whose agent is not in the zip at all, so the
        # patient is already the only subject candidate and the two roles coincide.
        passive = (rd.topic is not None and rd.topic in boxes and rd.topic is not Role.AGENT
                   and row.predicate is not None and not imperative)
        agent_role = subject_role if passive else None
        if passive:
            subject_role = rd.topic
        lemma = self._lemma(row, rd)
        if lemma is None:
            return None

        # **EXISTENTIAL `be` IS CONTENT, AND ENGLISH SAYS IT WITH THE EXPLETIVE** (req 31). «There is
        # a cat» — the thing said to exist is not the subject of the clause, the expletive is, and
        # the compiler separates the two readings by exactly this word; said the other way round,
        # «A cat is» is not a sentence anybody would parse back as an existential.
        #
        # **DECIDED BEFORE THE SUBJECT IS RENDERED**, which is not tidiness: rendering the phrase and
        # then moving it says a bound variable TWICE, and a variable's second mention is definite —
        # «There are no cats» came back as «There is the cat».
        existential = (lemma == COPULA and row.predicate is not None and not imperative
                       and subject_role is not None and len(boxes) == 1)
        there = self.the_form("existential", kind="structure") if existential else None
        if existential and not there:
            rd.out.unsaid.append(f"{row.name}: the existential has no form in the table")

        subject, agreement = "", {"person": 3, "number": "sg"}
        if there:
            # **THE EXPLETIVE IS NOT WHAT THE VERB AGREES WITH** *(2026-09-21, the 1st Officier)*.
            # «There IS a cat» · «There ARE cats» — English agrees the existential copula with the
            # thing said to exist, and the expletive is only holding the subject position for it.
            # The default third-singular was invisible until schema v6 let the zip carry the plural
            # at all, and then it said «There is no cats».
            agreement = self._agreement(boxes[subject_role], rd)
            subject, subject_role = there, None
        elif wh_is_subject:
            subject, subject_role = wh, None
        elif subject_role is not None:
            agreement = self._agreement(boxes[subject_role], rd)
            subject = self._phrase(boxes.pop(subject_role), rd, case=NOMINATIVE)
            if not subject and passive:
                rd.out.refused.append(f"{row.name}: the foregrounded role could not be said")
                return None
            if not subject:
                # **THE PASSIVE IS FOR AN AGENT NOBODY NAMED, AND FOR NOTHING ELSE.** «The hammer is
                # made of titanium» leaves out an agent the zip never had. A subject that is a BOUND
                # VARIABLE is a different thing entirely: the zip has it, this module failed to say
                # it, and passivising there turns «Nobody knows the answer» into «The answer is
                # known» — the truth inverted, which is the sin (req 8) and not a word dropped.
                # *Found by the 1st Officier's `aw-13` work, which made the station produce binders
                # whose restriction this module could not yet speak.*
                if isinstance(row.boxes[subject_role].head, Var):
                    rd.out.refused.append(
                        f"{row.name}: its subject is a variable whose binder cannot be said")
                    return None
                if row.predicate is not None:
                    passive, agent_role = True, subject_role
                    subject_role = next((role for role in SUBJECT_ORDER if role in boxes), None)
                    if subject_role is not None:
                        agreement = self._agreement(boxes[subject_role], rd)
                        subject = self._phrase(boxes.pop(subject_role), rd, case=NOMINATIVE)
                if not subject:
                    rd.out.refused.append(f"{row.name}: nothing in the row can be its subject")
                    return None
        elif not imperative and row.predicate is not None:
            # «It rains» — a clause with a predicate and no participant at all. English requires a
            # subject and the table holds the word it requires; the requirement is frame, the word
            # is a row.
            subject = self.the_form("expletive", kind="structure") or ""
            if not subject:
                rd.out.unsaid.append(f"{row.name}: nothing fills the subject and no expletive does")


        after_agent = ""
        if passive and agent_role is not None and agent_role in boxes:
            agent = boxes.pop(agent_role)
            said = self._phrase(agent, rd)
            # **THE PARSE ALREADY RECORDED THE MARKER** (req 65) — «written BY John» stored `by` on
            # the box — so a marked agent needs nothing from the table. Only an agent that arrived
            # unmarked (a zip built by hand, or by the brain) has to be asked about.
            by = "" if agent.marker else self._marker_for("agent")
            if said and (agent.marker or by):
                after_agent = f"{by} {said}" if by else said
            elif said:
                rd.out.unsaid.append(f"{row.name}: the agent of the passive could not be marked")

        # **AN UNMARKED OBJECT COMES FIRST, WHATEVER ITS ROLE.** «She feeds milk TO THE CUBS» —
        # a marked phrase can stand anywhere after the verb, and a bare one cannot, so putting the
        # bare one first is the order that is always readable. Measured on `t-dc-2`, which came back
        # with its milk as a destination.
        after = []
        for marked in (False, True):
            for role in (*OBJECT_ORDER, *CIRCUMSTANCE_ORDER):
                if role not in boxes or self._said_marked(boxes[role]) is not marked:
                    continue
                said = self._phrase(boxes.pop(role), rd,
                                    predicative=(role is Role.COMPLEMENT
                                                 and row.predicate is None))
                if said:
                    after.append(said)
        for role in list(boxes):
            rd.out.unsaid.append(f"{row.name}: the {role.value} box has no place in a clause yet")
            boxes.pop(role)

        # **INVERSION.** A question that is not embedded puts its carrier before the subject, and a
        # negation needs a carrier whether or not anything is asked. Word order, therefore frame;
        # do-support is the repair English itself uses when the clause has only a lexical verb.
        # The agent of a passive is a marked phrase like any other, and the marker is the table's:
        # exactly one form in it can mark an agent.
        fronted = "" if wh is None or wh_is_subject else wh
        invert = bool(asked or fronted) and not embedded
        parts = self._verb_phrase(lemma, subject, negated, modal, negation or "", invert,
                                  imperative, row, agreement, rd, passive)
        after = ([after_agent] if after_agent else []) + after
        complement = rd.complements.get(row.name)
        if complement is not None:
            inner = self._render(complement, rd, embedded=True)
            if inner is None or not inner.text.strip():
                rd.out.unsaid.append(f"{row.name}: what is {lemma}d could not be said")
            else:
                that = self._complementizer(inner)
                after.append(f"{that} {inner.text}" if that else inner.text)

        if gap_marker and wh is not None:
            after.append(gap_marker)
        said = " ".join(part for part in (fronted, *parts, *after) if part)
        if not said.strip():
            return None
        return _Said(said, "?" if (asked or wh is not None) and not embedded else ".",
                     asks=wh is not None)

    def _infinitive(self, row: ContentRow, rd: _Reading, scoped: bool) -> _Said | None:
        """The end of a purpose as English says it: the bare verb and everything after it, and no
        subject — «(to) SEE THE LIGURIAN SEA». The subject is the controller's, so the box must hold
        exactly that one; anything else would be spoken as the controller doing it.

        The imperative's shape, borrowed whole: it is the other clause English says bare.
        """
        if scoped:
            rd.out.unsaid.append(f"{row.name}: a purpose under its own negation or modality is not "
                                 f"said yet")
            return None
        boxes = dict(row.boxes)
        subject = next((role for role in SUBJECT_ORDER if role in boxes), None)
        if subject is not None:
            if boxes[subject].head != rd.bare[row.name]:
                rd.out.refused.append(f"{row.name}: the purpose's subject is not the one its act "
                                      f"controls, and «for X to» is not built")
                return None
            boxes.pop(subject)
        return self._clause(row.model_copy(update={"boxes": boxes, "truth": CLAIMED}), rd,
                            negated=False, modal="", embedded=True, imperative=True)

    def _lemma(self, row: ContentRow, rd: _Reading) -> str | None:
        if row.predicate is None:
            return COPULA
        if isinstance(row.predicate, (Open, Var)):
            rd.out.unsaid.append(f"{row.name}: the predicate itself is unbound")
            return None
        return keys.word_of(str(row.predicate))

    def _verb_phrase(self, lemma: str, subject: str, negated: bool, modal: str,
                     negation: str, invert: bool, imperative: bool, row,
                     agreement: dict, rd: _Reading, passive: bool = False) -> list[str]:
        """Subject and verb in the order and the shape the clause asked for.

        Seven English rules, all of them word order or inflection and none of them vocabulary: the
        verb AGREES with its subject and carries the TENSE; the future is an auxiliary rather than an
        inflection; a modal takes the agreement and leaves the verb bare; the passive is `be` plus a
        participle; a negated lexical verb needs do-support; an inverted clause puts the carrier
        first; and the copula inverts and negates on its own.

        **The carrier is whatever comes first** — will · can · is · does — and everything after it
        is bare. That is one rule rather than five, and it is why this reads as a list.
        """
        copular = row.predicate is None
        if imperative:
            return [lemma]

        if passive:
            # «the mail WAS WRITTEN by John» — be, in the tense and the agreement, then the
            # participle. Under a modal the modal is the carrier and `be` goes bare.
            participle = self.inflections.of(lemma, PARTICIPLE)
            if modal:
                head = [modal] + ([negation] if negated else []) + [COPULA, participle]
            else:
                head = ([self._copula(agreement, rd)]
                        + ([negation] if negated else []) + [participle])
            return [head[0], subject, *head[1:]] if invert else [subject, *head]

        if rd.when == AFTER:
            # **THE FUTURE IS A WORD.** English inflects the past and not the future, so the carrier
            # is an auxiliary, and which auxiliary is the table's to say.
            future = self.the_form("tense_aspect", kind="theatre", aspect=None, tense="future",
                                   was="modality")
            if future is None:
                rd.out.unsaid.append(f"{row.name}: the table names several futures and none is "
                                     f"preferred")
            else:
                head = [future] + ([negation] if negated else []) + [lemma]
                return [head[0], subject, *head[1:]] if invert else [subject, *head]

        if modal:
            head = [modal] + ([negation] if negated else []) + [lemma]
            return [*head[:1], subject, *head[1:]] if invert else [subject, *head]
        if copular:
            be = self._copula(agreement, rd)
            tail = [be] + ([negation] if negated else [])
            return [tail[0], subject, *tail[1:]] if invert else [subject, *tail]
        if negated or invert:
            do = self._agreeing(DO, agreement, rd)
            tail = [do] + ([negation] if negated else []) + [lemma]
            return [tail[0], subject, *tail[1:]] if invert else [subject, *tail]
        return [subject, self._agreeing(lemma, agreement, rd)]

    # -- agreement -----------------------------------------------------------------------------------

    def _agreement(self, box: Box, rd: _Reading) -> dict:
        """The person and number the verb has to agree with. Grammar, therefore frame.

        A pronoun carries both in its row. Everything else is third person — «the cat», «Anna», a
        bound variable — and singular unless the box counts otherwise, which is the reading the
        compiler took on the way in.
        """
        head = box.head
        if isinstance(head, Var):
            binder = rd.binders.get(head.name)
            box = binder.restriction if binder is not None else box
            head = box.head
        features = self._features_of(head)
        if features is not None:
            return {"person": features.get("person"), "number": features.get("number")}
        if isinstance(head, Open) and head.person is not None:
            return {"person": head.person, "number": head.number}
        # **THE BOX'S OWN NUMBER FIRST** (schema v6), then a numeral that implies one: «the three
        # cats sleep» agrees plural whether or not anybody wrote `number` down.
        plural = box.number == "pl" or (isinstance(box.count, int) and box.count > 1)
        return {"person": 3, "number": "pl" if plural else "sg"}

    def _agreeing(self, lemma: str, agreement: dict, rd: _Reading) -> str:
        """A lexical verb in the tense the theatre gives, agreeing where English agrees.

        **THE PAST DOES NOT AGREE** — «I walked», «she walked», «they walked» — so the roster answers
        once. The present inflects in exactly one cell, which is why `db/0022` only ever had to
        answer for `VBZ`: everywhere else the form IS the lemma, and that is a fact about the
        language rather than a gap in the data.

        **EXCEPT FOR `be`, WHICH IS NOT A REGULAR VERB AND WHOSE PARADIGM THIS IS NOT.** It has its
        own reader because its present has three cells, and a row can reach here holding it without
        being *copular*: an EXISTENTIAL has a predicate, because existential `be` is content (req
        31). Falling through to the bare lemma said «There be no cats» the moment schema v6 let the
        zip carry a plural at all — the rule above is true of every verb English has but this one.
        """
        if lemma == COPULA:
            return self._copula(agreement, rd)
        if rd.when == BEFORE:
            return self.inflections.of(lemma, PAST)
        third_singular = (agreement.get("person") in (3, None)
                          and agreement.get("number") in ("sg", "either", None))
        return self.inflections.of(lemma, PRESENT) if third_singular else lemma

    def _copula(self, agreement: dict, rd: _Reading) -> str:
        """`be`, agreeing — «I am» · «you are» · «the cat is».

        The copula is the one English verb whose present has three cells, and its forms are already
        closed-class rows: they are function words, they sit in the table beside the pronouns whose
        person they agree with, and the features that pair them are the same three. Where the table
        does not carry those features the roster answers instead, which is `is` — right for the
        third person and visibly wrong elsewhere, so the gap reports itself.
        """
        wanted = "past" if rd.when == BEFORE else "present"
        cells = [row for row in self.table._rows                       # noqa: SLF001
                 if (row.get("features") or {}).get("lemma") == COPULA
                 and (row["features"]).get("tense") == wanted
                 and not (row["features"]).get("clitic")]
        exact = [row for row in cells
                 if (row["features"]).get("person") == agreement.get("person")
                 and self._agrees((row["features"]).get("number"), agreement.get("number"))]
        if len(exact) == 1:
            return exact[0]["form"]
        elsewhere = [row for row in cells if (row["features"]).get("elsewhere")]
        if len(elsewhere) == 1 and not exact:
            return elsewhere[0]["form"]
        if cells:
            rd.out.unsaid.append(f"the copula for person {agreement.get('person')}: the paradigm "
                                 f"gives {len(exact) or len(elsewhere)} forms and not one")
        return self.inflections.of(COPULA, PAST if rd.when == BEFORE else PRESENT)

    def _question_word(self, boxes: dict, rd: _Reading) -> tuple[str | None, object]:
        """The box that is ASKED, and the word English asks it with — by ROLE, from the rows.

        The interrogatives are indexed on the role they open (`where` a location, `when` a time) and
        on «a participant» for the rest, which is where the table stops being able to answer: what ·
        which · who · whom all open a participant, and the zip does not record the animacy that
        chooses between them.
        """
        for role, box in boxes.items():
            if not isinstance(box.head, Open) or box.head.person is not None:
                continue           # a described person is an anaphor; `_head` says it as a pronoun
            if box.head.deixis is not None:
                continue           # «here», «then» — a deictic is said back, never asked (v10)
            form = self.the_form("interrogative", kind="open", binds=None, opens="box",
                                 role=role.value)
            if form is not None:
                return form, role

            # **THE SORT IS WHAT SEPARATES «who» FROM «what»**, and it is in the zip now (v4):
            # «who» asks for a person and «what» for a thing, which is a restriction on the answer
            # and not a matter of taste. Where the zip says nothing, the gap the POSITION opens
            # narrows the rows instead — and where that still leaves a choice, nothing is said.
            subject = next((other for other in SUBJECT_ORDER if other in boxes), None)
            gap = "subject" if role is subject else "predicate"
            found = [row["form"] for row in self.table._rows          # noqa: SLF001
                     if row.get("role") == "interrogative"
                     and (row.get("compiled") or {}).get("opens") == "participant"
                     and ((row.get("features") or {}).get("sort") == box.head.sort
                          if box.head.sort else
                          (row.get("features") or {}).get("gap") == gap)
                     and not (row.get("features") or {}).get("selective")
                     and not (row.get("features") or {}).get("archaic")]
            if len(found) > 1 and box.head.sort:
                # «who» and «whom» are one sort in two gaps, and the position settles that.
                found = [row["form"] for row in self.table._rows      # noqa: SLF001
                         if row["form"] in found
                         and (row.get("features") or {}).get("gap") == gap]
            if len(found) != 1:
                rd.out.unsaid.append(f"an OPEN {role.value}: {len(found)} question words fit, and "
                                     f"the rows do not choose between them")
                return None, None
            return found[0], role
        return None, None

    # -- the noun phrase ---------------------------------------------------------------------------

    def _phrase(self, box: Box, rd: _Reading, case: str = ACCUSATIVE,
                predicative: bool = False) -> str:
        """A box as a phrase: its marker, its determiner, its head — in that order, which is frame."""
        if isinstance(box.head, Var):
            return self._variable(box, rd, case)
        head = self._head(box, rd, case)
        if not head:
            return ""
        return self._dress(box, rd, head, pronoun=self._features_of(box.head) is not None,
                           predicative=predicative)

    def _dress(self, box: Box, rd: _Reading, head: str, pronoun: bool = False,
               quantity: Quantity | None = None, adjectives: tuple = (), tails: tuple = (),
               negation: str = "", predicative: bool = False) -> str:
        """Marker · determiner · count · adjectives · head · marked phrases. English's own order."""
        words = []
        if self._said_marked(box):
            # req 65: the preposition actually used — and one the sentence only UNDERSTOOD is not
            # said (schema v9): «I gave Anna a book» comes back bare, as it came in.
            words.append(box.marker)
        # **A POSSESSOR AND AN ARTICLE CANNOT SHARE THE DETERMINER SLOT** *(2026-09-24, G3)*. «the
        # result of perception» carries both — `relation` AND `definite` — and the clitic spoke the
        # possessor where the article goes: «perception's result», which compiles back without the
        # `definite`. English moves the possessor after the noun instead, so that is where it goes.
        of = self._post_possessor(box, rd) if not pronoun else None
        possessor = "" if of else self._possessive(box, rd)
        if of:
            tails = (of, *tails)
        if not pronoun:
            determiner = possessor or self._determiner(box, rd, head, quantity, predicative)
            if determiner:
                # «NOT every glitterer» — a negation that outscopes a quantifier is spoken in front
                # of it, which is the only place English puts it.
                words.append(f"{negation} {determiner}" if negation else determiner)
            if box.count is not None and not isinstance(box.count, (Open, Var)):
                words.append(str(box.count))
        words += [word for word in adjectives if word]
        words.append(head)
        words += [word for word in tails if word]
        return " ".join(words)

    def _variable(self, box: Box, rd: _Reading, case: str) -> str:
        """A bound variable, spoken as the noun phrase its binder describes.

        **FIRST OCCURRENCE ONLY.** «Every man loves a woman and the woman loves him» introduces the
        woman once; saying «a woman» twice would be two women, which is a different thought. A later
        mention is DEFINITE, which is what English does and what the compiler will read back.
        """
        before = set(rd.spoken)
        said = self._variable_said(box, rd, case)
        if not said:
            rd.spoken = before                         # the phrase carrying them never arrived
        return said

    def _variable_said(self, box: Box, rd: _Reading, case: str) -> str:
        """`_variable`'s body, with the bookkeeping of what reached the text kept outside it."""
        name = box.head.name
        binder = rd.binders.get(name)
        if binder is None:
            rd.out.unsaid.append(f"the variable {name}: nothing in the zip binds it")
            return ""
        restriction = binder.restriction
        # **A QUANTIFIER CAN BE ITS OWN NOUN.** «nobody» is a negative quantity ranging over persons
        # and there is no separate word for the persons — the restriction says only what the phrase
        # said (`Open(sort='person')`, schema v4) and English fuses the two into one word. The rows
        # carry both halves already: every fused form has its `sort` beside its quantity.
        if isinstance(restriction.head, Open) and restriction.head.sort and binder.quantity:
            # **A BINDER WITHOUT A QUANTITY FUSES WITH NOTHING** (schema v8): «nobody» is a QUANTITY
            # and a sort in one word, and a binder that quantifies nothing has only half of that.
            fused = self._fused(binder.quantity, restriction.head.sort)
            if fused is None:
                rd.out.unsaid.append(f"a {binder.quantity.value} over "
                                     f"{restriction.head.sort}s: no single word fuses them")
                return ""
            rd.said.add(name)
            # **AND THE FUSED WORD STILL TAKES ITS CLAUSE** *(2026-09-24, G4a)*. «something THAT YOU
            # DO NOT KNOW» — this branch returned before the restriction, and the row `_read` had
            # consumed vanished without a word in `unsaid`: «If I tell you something, you learn it»,
            # a wider claim than the zip (req 8). English puts everything after a fused word —
            # «something good», «nobody in the room», «something that you do not know».
            trailing = self._trailing(name, binder, rd)
            if trailing is None:
                return ""
            adjectives, tails = trailing
            negation = self._negation_owed(name, rd)
            if negation is None:
                return ""                              # the caller refuses; it is owed this word
            said = box if self._said_marked(box) else restriction
            marker = said.marker if self._said_marked(said) else None
            return " ".join(word for word in (marker, negation, fused, *adjectives, *tails)
                            if word)
        head = self._head(restriction, rd, case)
        if not head and not rd.restrictions.get(name):
            # No noun, and no clause to stand in for one. «all» alone names nothing.
            return ""
        if head and name in rd.said:
            again = box.model_copy(update={"determination": Determination.DEFINITE,
                                           "head": restriction.head})
            return self._dress(again, rd, head)
        rd.said.add(name)

        trailing = self._trailing(name, binder, rd)
        if trailing is None:
            return ""
        adjectives, tails = trailing

        if not head:
            # **«ALL THAT GLITTERS» — THE QUANTIFIER IS THE PHRASE AND THE CLAUSE IS ITS NOUN.**
            # A bare `all` says nothing about what it ranges over, so the restriction row is not a
            # clause hanging off a noun: it IS the noun, and English puts it exactly where one
            # goes. The fused forms take the other road — «nobody» is a quantity and a sort in one
            # word — and this is the same hole filled by the sentence instead of by the table.
            if not tails:
                return ""
            head, tails = tails[0], tails[1:]
            # **AND «EVERY» IS NOT THE WORD FOR IT.** `db/0029` picks the universal by the number of
            # the noun, and «every» is the one that takes a SINGULAR COUNT noun — which a clause is
            # not. «All that glitters», never «every that glitters». Asked with no number at all the
            # lookup reaches the slot no measured row occupies, so the clause is read as the plural
            # it patterns with. *The verb still agrees singular, which is English's own mismatch and
            # not this module's: «all that glitters IS not gold».*
            restriction = restriction.model_copy(update={"number": "pl"})

        merged = restriction.model_copy(update={
            "marker": box.marker or restriction.marker,
            "marker_implicit": box.marker_implicit if box.marker else restriction.marker_implicit,
            "count": box.count if box.count is not None else restriction.count,
        })
        negation = self._negation_owed(name, rd)
        if negation is None:
            return ""                                  # the caller refuses; it is owed this word
        return self._dress(merged, rd, head, quantity=binder.quantity,
                           adjectives=tuple(adjectives), tails=tuple(tails), negation=negation)

    def _negation_owed(self, name: str, rd: _Reading) -> str | None:
        """The «not» a negated binder is owed at its quantifier — "" when none is owed, None when one
        is and the table has no single form for it."""
        if name not in rd.negated_binders:
            return ""
        negation = self.the_form("negation", kind="prefix", element="negation")
        if not negation:
            return None
        rd.negated_binders.discard(name)
        return negation

    def _trailing(self, name: str, binder, rd: _Reading) -> tuple[list, list] | None:
        """What the zip put in rows of their own and English puts around the noun: the folded
        modifiers — adjectives, marked phrases — and the relative clauses, in that order.

        None when a restriction cannot be said: the phrase without it would claim more than the
        zip, so the caller must not say the phrase at all.
        """
        adjectives, tails = [], []
        for row in rd.modifiers.get(name, ()):
            carrier = next(role for role, other in row.boxes.items()
                           if isinstance(other.head, Var) and other.head.name == name)
            other = next(other for role, other in row.boxes.items() if role != carrier)
            said = self._phrase(other, rd)
            if not said:
                # Folded out of a conjunction, so the phrase without it says less and not more —
                # but the zip holds it, and a silent drop is what the account at the end forbids.
                rd.out.unsaid.append(f"{row.name}: a modifier of {name} could not be said")
                continue
            rd.spoken.add(row.name)
            (tails if other.marker else adjectives).append(said)

        # **AND THE RESTRICTION THE ZIP PUT IN A ROW OF ITS OWN**, which English puts after the
        # noun. Popped rather than read, so a phrase said twice does not say its clause twice and a
        # clause that mentions its own antecedent cannot recurse into this.
        for restricting in rd.restrictions.pop(name, ()):
            if not self._restricting(binder, restricting, rd):
                return None
            outer_gap, rd.gap = rd.gap, name
            try:
                clause = self._render(restricting.name, rd, embedded=True)
            finally:
                rd.gap = outer_gap
            if clause is None or not clause.text.strip():
                rd.out.unsaid.append(f"the clause restricting {name}: it could not be said, and "
                                     f"the phrase without it would claim more than the zip")
                return None
            tails.append(clause.text.strip())
        return adjectives, tails

    @staticmethod
    def _restricting(binder, row, rd: _Reading) -> bool:
        """Can this row be said as its binder's relative clause and come back with the same truth?

        **THE COMPILER DECIDES THE TRUTH OF A RELATIVE CLAUSE BY ITS BINDER, SO THIS READS IT THE
        SAME WAY** (`Compiler._share_variable`). A binder that quantifies — «every cat that sleeps»
        — makes its clause a restriction, stated and not claimed; the quantity-less binder schema v8
        mints for a referring phrase — «the cat that sleeps» — leaves it claimed, a presupposition
        the brain should get. So:

            quantity-less binder, row claimed or denied    said — it comes back claimed
            quantity-less binder, row unclaimed            REFUSED — said, it would come back a claim
            quantifying binder, row unclaimed              said — it comes back a restriction
            quantifying binder, row claimed                said, and the claim is recorded unsaid:
                                                           it comes back a restriction, claiming less
        """
        claims = row.truth in (CLAIMED, DENIED)
        if binder.quantity is None:
            if claims:
                return True
            rd.out.refused.append(f"{row.name}: an unclaimed clause about a phrase that quantifies "
                                  f"nothing would be read back as a claim")
            return False
        if claims:
            rd.out.unsaid.append(f"{row.name}: said as a restriction, so its claim is not spoken")
        return True

    def _fused(self, quantity: Quantity, sort: str) -> str | None:
        """The one word that is a quantity AND the thing it ranges over — «nobody», «everywhere».

        Chosen by the rows and never here: the `spoken` flag settles «nobody» against «no one» and
        «everyone» against «everybody», and a form whose polarity binds it to a negative context
        («anyone») is not a candidate for a plain statement.
        """
        found = [row for row in self.table._rows                     # noqa: SLF001
                 if row.get("role") == FUSED_QUANTIFIER
                 and (row.get("compiled") or {}).get("quantity") == quantity.value
                 and (row.get("features") or {}).get("sort") == sort
                 # **THE FORCE MUST BE THE PLAIN ONE.** «often» and «seldom» range over times and
                 # say HOW MANY as well — `force: many`, `force: few` — which is more than a bare
                 # quantity states; «once» and «twice» carry a count. A word that says more than
                 # the zip does is the sin in this direction too (req 8).
                 and (row.get("features") or {}).get("force") == quantity.value
                 and (row.get("features") or {}).get("count") is None
                 and not (row.get("features") or {}).get("polarity")]
        if len(found) > 1:
            found = [row for row in found if row.get("spoken")] or found
        return found[0]["form"] if len(found) == 1 else None

    def _head(self, box: Box, rd: _Reading, case: str = ACCUSATIVE) -> str:
        """The word in the box — a key becomes its word, and an abstention stays an abstention."""
        if isinstance(box.head, Open):
            # **AN OPEN THE SENTENCE DESCRIBED IS AN ANAPHOR** (schema v4): «she» is a slot nobody
            # has resolved and a person the speaker told us three things about, so it is SAID, as
            # the pronoun those three things pick. An undescribed OPEN is a hole, and the clause has
            # already decided what to do with it — ask, or leave it out of a passive.
            if box.head.deixis is not None:
                return self._deictic(box.head, rd)
            if box.head.person is not None:
                form = self._same_person(
                    {"person": box.head.person, "number": box.head.number,
                     "gender": box.head.gender}, "referential", case=case)
                if form is not None:
                    return form
                rd.out.unsaid.append(f"a person-{box.head.person} pronoun in the {case}: "
                                     f"no single form")
            return ""
        if isinstance(box.head, Var):
            return self._variable(box, rd, case)
        if isinstance(box.head, Ref):
            rd.out.unsaid.append(f"a box valued by row {box.head.row}: not built yet")
            return ""
        if box.head is None:
            return ""
        pronoun = self._pronoun(box.head, case, rd)
        if pronoun is not None:
            return pronoun
        word = keys.word_of(str(box.head))
        # **THE NUMBER THE SPEAKER STATED** (schema v6). A noun with none is spoken singular, which
        # is what a mass noun and a box the brain built for itself both want; `db/0027` holds the
        # 276 plurals the spelling rule gets wrong.
        if box.number == "pl" and keys.is_base_key(str(box.head)) \
                and keys.pos_of(str(box.head)) == "n":
            return self.inflections.of(word, PLURAL)
        return word

    def _deictic(self, unknown: Open, rd: _Reading) -> str:
        """«here» · «there» · «now» · «then» — the referential adverb whose row carries these
        features (schema v10, E3.2.1.5). **THE ROWS ANSWER, AS THEY DO FOR A PRONOUN**: the compiler
        copied `deixis` and `distance` off the word it matched, and this matches them back."""
        found = {row["form"] for row in self.table._rows          # noqa: SLF001
                 if row.get("role") == "referential"
                 and (row.get("features") or {}).get("deixis") == unknown.deixis
                 and (row.get("features") or {}).get("distance") == unknown.distance
                 and not (row.get("features") or {}).get("archaic")}
        if len(found) == 1:
            return next(iter(found))
        rd.out.unsaid.append(f"a {unknown.deixis} deictic ({unknown.distance}): "
                             f"{len(found)} forms fit")
        return ""

    def _possessive(self, box: Box, rd: _Reading) -> str:
        """«my cat» · «Liguria's sea» — the possessor, in the form English gives a possessor.

        A pronoun possessor has a WORD of its own and the rows carry it, keyed by the same person
        features that spell «I» and «me». Anything else takes the genitive clitic, which is also a
        row. Neither is chosen here; what is chosen here is that a possessor precedes its head, and
        that is word order.
        """
        if box.relation is None:
            return ""
        if isinstance(box.relation, Open):
            # «ITS cubs» — the possessor is unresolved and the sentence still said whose kind of
            # thing it is. Same three features, different slot, and the rows hold both paradigms.
            if box.relation.person is not None:
                form = self._same_person(
                    {"person": box.relation.person, "number": box.relation.number,
                     "gender": box.relation.gender}, "possessive", use="determiner")
                if form is not None:
                    return form
            rd.out.unsaid.append("a possessor the rows give no single form for")
            return ""
        if isinstance(box.relation, (Var, Ref)):
            rd.out.unsaid.append("a possessor that is a variable or a row: not built yet")
            return ""
        features = self._features_of(box.relation)
        if features is not None:
            form = self._same_person(features, "possessive", use="determiner")
            if form is None:
                rd.out.unsaid.append(f"a possessor «{keys.word_of(str(box.relation))}»: the table "
                                     f"gives several possessive forms and none is preferred")
                return ""
            return form
        clitic = self.the_form("genitive", kind="field", field="relation", was="structure")
        if clitic is None:
            rd.out.unsaid.append("a possessor: the genitive has no single form in the table")
            return ""
        return f"{keys.word_of(str(box.relation))}{clitic}"

    def _post_possessor(self, box: Box, rd: _Reading) -> str | None:
        """«of perception» — the possessor said AFTER the noun, when the box also has an article.

        **THE WORD IS THE MARKER WHOSE RULE YIELDS THE FIELD**, read backwards from `db/0012`: the
        selector that settles a marked phrase hanging off a noun to `relation` is the one row the
        compiler reads «the office OF the Chair» by, so it is the one row to say it with. The forms
        are the table's, never this module's; where the table names none or several, the clitic
        stays and what it loses is recorded.
        """
        if box.relation is None or not isinstance(box.determination, Determination):
            return None
        if isinstance(box.relation, (Var, Ref)):
            return None                                # `_possessive` records it as not built
        if isinstance(box.relation, Open) or self._features_of(box.relation) is not None:
            # «my cat», never «the cat of me»: a possessive PRONOUN is a determiner of its own, and
            # English has no article beside it. The compiler writes none for «my», so a box
            # carrying one was built elsewhere — the article is what goes unsaid.
            rd.out.unsaid.append(f"a {box.determination.value} noun with a pronoun possessor: "
                                 f"the article is not spoken")
            return None
        if len(self._relation_markers) != 1:
            rd.out.unsaid.append(f"a {box.determination.value} possessed noun: the table names "
                                 f"{len(self._relation_markers)} markers for a possessor, not one")
            return None
        said = self._phrase(Box(head=box.relation), rd, case=ACCUSATIVE)
        if not said:
            return None
        return f"{next(iter(self._relation_markers))} {said}"

    @staticmethod
    def _markers_yielding(table: ClosedClasses, field_name: str) -> set[str]:
        """The forms whose selector can settle a marked phrase to this box FIELD (`db/0012`)."""
        return {row["form"] for row in table._rows                   # noqa: SLF001
                if any(rule.get("then") == field_name
                       for rule in ((row.get("compiled") or {}).get("selector") or ()))}

    def _determiner(self, box: Box, rd: _Reading, head: str,
                    quantity: Quantity | None = None, predicative: bool = False) -> str:
        """«the» / «a» / «every» where the table names one form, and silence where it names several.

        `determination` is lucky — English has ONE definite article — and `indefinite` is «a» or
        «an», which is not a choice of word but a SPELLING of one, so the vowel rule is applied here
        as orthography.
        """
        quantity = quantity if quantity is not None else box.quantity
        # **THE DETERMINATION IS THE FINER READING AND IT WINS.** They are orthogonal (req 26), so a
        # phrase can carry both — «a clever girl» is EXISTENTIAL and INDEFINITE, because the
        # attributive adjective raised a binder (req 70) over a phrase that already had an article.
        # English says «a» there and keeps «some» for an existential nobody made indefinite.
        if isinstance(quantity, Quantity) and isinstance(box.determination, Determination) \
                and quantity is Quantity.EXISTENTIAL:
            quantity = None
        if isinstance(quantity, Quantity):
            # **THE NOUN PICKS THE WORD** (`db/0029`) — «every cat» against «all cats» is one
            # quantity and two forms, and the box has just been told which noun it is. Asking
            # without the number made every plural universal come out «every human beings».
            # **THE DETERMINER AGREES WITH THE WORD THIS MODULE IS ABOUT TO WRITE**, which is the
            # singular unless the box says `pl` — the same rule `_dress` spells the head by. A box
            # with no number at all is not a third case to choose in: English writes «cat», so the
            # determiner that goes in front of it is the one that takes «cat».
            form = self.the_form("quantificational",
                                 _number="pl" if box.number == "pl" else "sg",
                                 kind="quantifier", quantity=quantity.value)
            if form is None:
                rd.out.unsaid.append(f"a {quantity.value} quantity over a "
                                     f"{box.number or 'numberless'} noun: the table names several "
                                     f"forms and none is preferred")
                return ""
            return form
        if isinstance(box.determination, Determination):
            if box.determination is Determination.GENERIC:
                # **A GENERIC IS BARE**, and that is measured rather than assumed: rendering it with
                # the indefinite article instead («a mind thinks») cost the round trip a case and
                # produced «some a foreign licence», because a generic can also carry a quantity.
                return ""
            found = self.forms_for("determination", kind="determination",
                                   determination=box.determination.value, was="quantificational")
            if not found:
                rd.out.unsaid.append(f"a {box.determination.value} determination: no form")
                return ""
            if len(found) == 1:
                return next(iter(found))
            # «a» and «an» are one word in two spellings, and which one is settled by the sound that
            # follows — orthography, and therefore frame. Nothing else in this module chooses.
            return self._indefinite(found, head)

        # **A PREDICATE NOMINAL NEEDS AN ARTICLE AND THIS MODULE MUST NOT INVENT ONE.** «Software
        # can be mind» is not a sentence, and «a mind» was tried: it MEASURED WORSE — the fixpoint
        # fell 65 to 61 of 87, because an article the zip does not hold comes back as a
        # determination the zip did not have. The prose improved and the thought changed, which is
        # the wrong trade in this direction as in the other (req 8).
        #
        # **The defect is upstream**: «minds» and «mind» compile to the same box, because the format
        # records no NUMBER — the third thing in two days found to be in the sentence and not in the
        # zip, after the sort of an unknown and the tense of a clause. `predicative` is kept so the
        # caller's knowledge of WHERE the phrase stands is not thrown away a second time.
        return ""

    @staticmethod
    def _indefinite(found: set, head: str) -> str:
        """«a» or «an» — one word in two spellings, settled by the sound that follows. Orthography,
        and the one form this module picks for itself, because it is not picking a WORD."""
        vowel = head[:1].lower() in "aeiou"
        return next((f for f in sorted(found) if (f.endswith("n") == vowel)), sorted(found)[0])
