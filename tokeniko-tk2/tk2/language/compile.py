"""The compile core: a skeleton and the closed classes in, a zip out.

**WHAT THIS IS AND IS NOT.** It fills boxes from the dependency tree and compiles the function words
into structure. It does **not** resolve senses — every `sense` slot is emitted OPEN, because binding
is the evaluator's one algorithm and it has a KB to check itself against (evaluator req 5). It does
not decide truth, and it does not consult the dictionary for meaning: *«the station consults the
dictionary for SHAPE, never for MEANING»*.

**THE 37 → 18 MAPPING HAS TWO HALVES** (parser-compiler req 12, found by the gate). This file owns
both and keeps them apart:

- **BY RELATION** — `nsubj → agent`, `obj → patient`, `iobj → recipient`. No marker exists for
  these; English marks them by position. The table holds no row for `patient` or `experiencer`, and
  that absence is the proof.
- **BY MARKER** — `case` + the closed-class row. «after the rehearsal» is a TIME box because the
  table says `after` marks time, and a UD subtype settles it where the row alone cannot.

**HALF-UNDERSTOOD IS LEGAL; WRONGLY-UNDERSTOOD IS THE SIN** (req 8). Every failure here is visible:
a word that reaches no box lands in `Zip.unplaced`, a slot nobody can fill is OPEN, and a marker with
several readings and nothing to choose between them abstains rather than picking its first
candidate. None of that is an error path — it is the normal output of a station meeting a sentence
larger than its format.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from tk2.dictionary import keys as keymod
from tk2.language.adverbs import AdverbKinds, standing_adverb_kinds
from tk2.language.closed import ClosedClasses
from tk2.language.markers import MarkerSelector
from tk2.language.skeleton import UD_POS, Skeleton, Word
from tk2.language.utterance import NO_CONTEXT, Context
from tk2.tkzip.schema import (
    AttitudeRow,
    Box,
    Var,
    ContentRow,
    Determination,
    Modality,
    ModalityRow,
    JoinRow,
    NegationRow,
    Open,
    Operator,
    Quantity,
    QuantifierRow,
    Role,
    Zip,
)

#: **THE RELATION HALF OF THE MAPPING.** Every entry is a UD relation whose own definition names the
#: role, so this is a reading of UD's documentation and not a judgement about English. FRAME: it
#: relates two closed vocabularies, and no evidence revises what `obj` corresponds to.
#:
#: `nsubj` is deliberately `agent` and not «agent or experiencer»: which one it is depends on the
#: VERB («the cat chased» vs «the cat saw»), that is a head-verb question the geometry answers, and
#: a station that guessed here would be doing the compile core's job badly instead of leaving it.
RELATION_FILLS_ROLE: dict[str, Role] = {
    "nsubj": Role.AGENT,
    "nsubj:pass": Role.PATIENT,     # the passive subject IS the patient — «the cat was chased»
    "obj": Role.PATIENT,
    "iobj": Role.RECIPIENT,         # the double-object recipient: «she gave ME a raise»
    "obl:tmod": Role.TIME,
    "obl:lmod": Role.LOCATION,
    "obl:agent": Role.AGENT,
}

#: UD POS → the dictionary's POS letter. Only the content classes: a function word never earns a key.
POS_LETTER = {"NOUN": "n", "PROPN": "n", "VERB": "v", "AUX": "v", "ADJ": "a", "ADV": "r"}

#: The relations that hang a NOMINAL off a head — the candidates for a box.
NOMINAL_DEPS = frozenset({"nsubj", "obj", "iobj", "obl", "nmod"})

#: THE RELATIONS THAT OPEN A CLAUSE OF THEIR OWN — each one becomes its own content row, related to
#: the row above it by a join, an attitude, or a shared variable.
#:
#: `xcomp` is deliberately ABSENT. «you like TO SWIM» is one predication with a controlled subject,
#: not two claims: nobody asserts that you swim. Treating it as a second row would put an unasserted
#: proposition in the zip with nothing marking it unasserted — the one thing the truth slot exists to
#: prevent. It stays inside its matrix clause until there is a reason it cannot.
CLAUSE_DEPS = frozenset({"conj", "advcl", "ccomp", "acl", "csubj", "parataxis"})

#: What a joining word claims about its halves (closed classes v4, `db/0010`).
ASSERTS_BOTH, ASSERTS_NEITHER = "both", "neither"
ASSERTS_MATRIX, ASSERTS_AMBIGUOUS = "matrix", "ambiguous"

#: Kinds a LATER pass owns. A joining word is built by `_relate` once every clause exists, and a
#: relative pronoun by `_share_variable` — so neither is an abstention when the per-clause walk meets
#: it, and saying so made the abstention list untrustworthy.
LATER_PASS_OWNS = frozenset({"join", "open"})

#: **ROW-NAME PREFIXES, GATHERED HERE BECAUSE THEY MUST NOT COLLIDE.** The schema requires names to
#: be unique within a zip (`Zip` validates it), and they were being minted in six places from four
#: different counters — so `m` meant «modality prefix» in one and «modifier row» in another, and
#: «In Italy, you MAY drive in France with a FOREIGN licence» produced two rows called `m0`.
#:
#: **The drill gate found it on its first run** (req 18): no sentence in UD's corpus carries both a
#: modal and an attributive adjective, so neither existing gate could have. Listed rather than
#: merely fixed, because the next row kind will want a letter and this is where to look.
#:
#:   r  a clause         m  an attributive modifier    q  a quantifier binder
#:   j  a join           p  a PREFIX row (negation · modality · attitude · domain)
ROW_PREFIXES = {"clause": "r", "modifier": "m", "binder": "q", "join": "j", "prefix": "p"}

#: A closed-class `kind` -> the word for WHERE that form went, when the two differ. A form whose
#: `compiled.kind` is `box` is a MARKER on somebody else's box, never a box of its own, and calling
#: its placement `box` would make the trace say the preposition filled the role.
CLOSED_KIND_PLACES = {"box": "marker"}

def numeral_value(lemma: str, text: str = "") -> int | None:
    """A numeral's VALUE, or None when this station cannot read it.

    **DIGITS ONLY, AND THE LIMIT IS DELIBERATE.** `3` is orthography — the same mechanical
    transformation `keys.normalize_word` performs, carrying no judgement about English and revisable
    by nothing. **`forty` is not**: converting an English number WORD needs a roster of atoms plus
    composition rules, and `db/0001` ruled numerals out of the closed classes for exactly that
    reason — *«two, seventeen, three hundred and four — productive and infinite, so not a closed
    class at all however finite the words below ten look»*.

    tk1 solved it with `word2number`, and **the Captain admitted it on 2026-09-16** — the fifth
    entry in `pyproject.toml`, on the same terms as `nltk`: **it enters through ONE door, and this
    function is the door.** Nothing else in tk2 may import it, so a machine without the package
    still parses and only the count abstains.

    **THE IMPORT IS LOCAL AND ITS FAILURE IS AN ABSTENTION, NOT A CRASH.** A station that could not
    read a numeral must still read the sentence — «half understood is legal, wrongly understood is
    the sin» — and a count the station guessed would be a number in a zip that nobody put there.

    A comma or a space inside a digit string is a thousands separator in most of the world and a
    decimal point in some of it, so neither is stripped: `1,5` is not read at all rather than read
    as fifteen. **And the library's own failure mode is checked rather than trusted**: it raises on
    a word it cannot read, and it returns 0 for some non-numerals, so a 0 that did not come from a
    word meaning zero is refused.
    """
    for candidate in (lemma, text):
        found = (candidate or "").strip()
        if found.isdigit():
            return int(found)

    word = (lemma or text or "").strip().lower().replace("-", " ")
    if not word:
        return None
    try:
        from word2number import w2n

        value = w2n.word_to_num(word)
    except (ImportError, ValueError, IndexError, AttributeError, TypeError):
        # ImportError: the package is not installed, and the station goes on without it.
        # The rest: `word_to_num` raises on a word it cannot read, and its internals are not
        # defensive — an unexpected shape reaches the caller as an IndexError. All of them mean the
        # same thing here, which is «no number», and none of them may stop the parse.
        return None
    if not isinstance(value, int):
        return None
    if value == 0 and "zero" not in word and "naught" not in word and "nought" not in word:
        # It returns 0 for some strings that are not numerals at all. A zero that no word in the
        # phrase asked for is the library shrugging, and a shrug is not a count.
        return None
    return value


#: The relations that hang an ADVERB off its head. `advmod` is the ordinary one; `discourse` is UD's
#: own name for a connective, and it is the only dependency that names an adverb's KIND outright.
#:
#: **ON THE FRAME/KNOWLEDGE AUDIT LIST** with `CLAUSE_DEPS` and `DEPS_THAT_COMPILE_TO_NOTHING`: it
#: is a set of UD relations in code. Weaker than those two — it selects WHERE to look rather than
#: ruling what a thing means — but it is the same shape and the audit should see it.
ADVERB_DEPS = frozenset({"advmod", "discourse"})

#: UD relations whose dependent COMPILES TO NOTHING — it is addressing or framing, not content.
#: `vocative` is E2's own ruling, made in the drill: *«the vocative is addressing, not content»* —
#: «Guys, take it easy» is an instruction to a room, and the room is not a participant in it.
#: **ON THE FRAME/KNOWLEDGE AUDIT LIST** (E3 task 8): this is a set of UD relations living in code,
#: the same family as `CLAUSE_DEPS`, and the reading «a vocative is not content» is a ruling.
DEPS_THAT_COMPILE_TO_NOTHING = frozenset({"vocative"})

#: A claim the station makes with no fuzziness of its own: the speaker said it, so it is stated at
#: full strength. What the claim is WORTH is the evaluator's question, not the parser's.
CLAIMED = 1.0


class Placements:
    """Which tokens reached the zip, **and where each one went.**

    A `set` of covered indices answers «how much of this sentence was understood» and nothing else,
    and that was enough while the gate only exercised the closed-class table. It is not enough now:
    most of UD's relations are questions for the COMPILER — *what did `amod` become, what did `conj`
    become* — and «the token is covered» does not distinguish a role from a prefix from a row.

    So the same bookkeeping carries a LABEL. It behaves as the set it replaces (`in`, `len`, `add`,
    `update`) so every existing call site is unchanged, and a caller that knows where a token went
    says so. **The first non-empty label wins**: a token is placed once, and a later unlabelled
    `add` — the generic accounting that runs after the specific one — must not erase it.

    This is also what req 4's confidence scalar will read, and what req 3 means by a reading that can
    be handed back: «which word became which part of this zip» is the question both of them ask.
    """

    __slots__ = ("_where",)

    def __init__(self) -> None:
        self._where: dict[int, str] = {}

    def add(self, index: int, label: str = "") -> None:
        if label or index not in self._where:
            if not self._where.get(index):
                self._where[index] = label

    def update(self, indices, label: str = "") -> None:
        for index in indices:
            self.add(index, label)

    def label(self, index: int) -> str:
        return self._where.get(index, "")

    def as_dict(self) -> dict[int, str]:
        return dict(self._where)

    def __contains__(self, index: int) -> bool:
        return index in self._where

    def __iter__(self):
        return iter(self._where)

    def __len__(self) -> int:
        return len(self._where)


@dataclass
class Compiled:
    """A zip and the bookkeeping the confidence scalar will need (req 4).

    The counts are kept as the compile runs rather than recomputed afterwards: «how much of this
    sentence reached the zip» is only cheap while the mapping from token to box still exists.
    """

    zip: Zip
    covered: tuple[int, ...] = ()
    unplaced: tuple[str, ...] = ()
    abstained: tuple[str, ...] = field(default_factory=tuple)
    #: token index -> WHERE it went: `box:location`, `prefix`, `join`, `predicate`, `structure`, …
    #: Empty for a token that was covered by accounting nobody labelled — which is itself a finding,
    #: and the gate reports it rather than guessing.
    placement: dict[int, str] = field(default_factory=dict)

    #: Roles filled by an ambiguous marker's DEFAULT — the curation's best-first answer, taken
    #: because nothing in the sentence chose. Counted rather than silent: that distinction is the
    #: whole of req 8 here, and it is what req 4's confidence scalar reads.
    defaulted: tuple[str, ...] = field(default_factory=tuple)

    @property
    def coverage(self) -> float:
        total = len(self.covered) + len(self.unplaced)
        return 1.0 if not total else len(self.covered) / total


class Compiler:
    """Skeleton → zip. Pure: context is an argument and never state (req 7)."""

    def __init__(self, table: ClosedClasses, selector: MarkerSelector | None = None,
                 adverbs: AdverbKinds | None = None) -> None:
        self.table = table
        #: Requirement 23's four-way split, as rows (`db/0013`). A miss is the MANNER default, which
        #: is measured rather than assumed: 79% of English's adverbs are `-ly` and describe the
        #: action. Two rosters, one vocabulary — `compiled` here is the closed classes' own.
        self.adverbs = adverbs if adverbs is not None else standing_adverb_kinds()
        #: WHICH role an ambiguous marker fills here — `db/0012`'s rules, run by
        #: `tk2.language.markers`. An argument so a test can state what the resource says instead
        #: of depending on which WordNet is installed.
        self.selector = selector or MarkerSelector()

    # -- the whole sentence -----------------------------------------------------------------------

    def compile(self, skeleton: Skeleton, context: Context = NO_CONTEXT) -> Compiled:
        """Skeleton → zip. One content row per CLAUSE, related by joins and attitudes.

        **`context` IS REQUIREMENT 7, FINALLY BUILT** — *«the station is pure: context is an ARGUMENT,
        never state»*. It carries what the caller knows and the sentence does not: who is speaking,
        who is being spoken to, and (when anaphora is built) the recent zips. It is READ and never
        stored, so the compiler stays pure and two calls with different contexts cannot influence
        each other.

        **Defaulting to `NO_CONTEXT` is what keeps this additive**: with no context every pronoun
        stays OPEN exactly as before, and not one existing measurement moves.

        The clauses are found first and compiled independently, because a box belongs to the clause
        whose head governs it: «if it RAINS I stay HOME» has two subjects and two predicates, and a
        single pass would put them all in one row and lose which went with which.
        """
        root = skeleton.root
        if root is None:
            return Compiled(zip=Zip(rows=[ContentRow(name="r0")]), unplaced=skeleton.tokens)

        marks = self._read_closed(skeleton)
        heads = self._clause_heads(skeleton)
        owner = self._owners(skeleton, heads)

        covered = Placements()
        abstained: list[str] = []
        defaulted: list[str] = []
        prefix_rows: list = []
        modifiers: list = []   # (var, adjective key, its binder, the row it belongs to)
        adverb_joins: list = []   # (row, operator, pragmatic) — a discourse adverb needs two rows
        content: dict[int, ContentRow] = {}
        open_truth: set[str] = set()          # rows whose TRUTH was asked («whether», a polar)
        wants_antecedent: set[str] = set()    # rows asked «why» — an unknown row implies them

        # **THE ROTATION IS DECIDED BEFORE THE CLAUSES ARE COMPILED, AND IT HAS TO BE.** A pronoun
        # is resolved where it is met, and the attitude that governs it is built later, in
        # `_relate` — so by the time the POV exists the `you` inside it has already been given the
        # outer addressee. The tree says which clause sits under which attitude, and the tree is
        # known now, so the contexts are worked out first and the walk uses them.
        inner = self._contexts(skeleton, heads, marks, context)

        for position, head in enumerate(heads):
            mine = {i for i, h in owner.items() if h == head.index}
            content[head.index] = self._clause(
                skeleton, head, mine, marks, covered, prefix_rows, abstained, f"r{position}",
                open_truth, wants_antecedent, defaulted, modifiers, adverb_joins,
                inner.get(head.index, context))

        joins = self._relate(skeleton, heads, content, marks, covered, prefix_rows, abstained)
        extra = self._ask(content, joins, open_truth, wants_antecedent)
        extra += self._modify(modifiers, joins)
        self._connect(adverb_joins, content, joins, abstained)

        unplaced = tuple(w.text for w in skeleton
                         if w.index not in covered and w.upos not in ("PUNCT", "SYM"))

        rows = [*prefix_rows, *content.values(), *extra, *joins]
        return Compiled(zip=Zip(rows=rows, unplaced=list(unplaced)),
                        covered=tuple(sorted(covered)), unplaced=unplaced,
                        placement=covered.as_dict(),
                        abstained=tuple(abstained), defaulted=tuple(defaulted))

    # -- the clauses ------------------------------------------------------------------------------

    def _is_copular_root(self, head: Word, skeleton: Skeleton, marks: dict) -> bool:
        """Is this root `be` doing COPULAR work, and therefore earning no predicate (req 31)?

        «Where is the cat?» has `be` as its root because there is no other verb — and it is still
        glue: the question is a LOCATION box on a row about the cat. But **existential `be` IS
        content** and req 31 says so («there is a cat»), so the expletive is what separates them.

        The row for `be` already states the conditional («structure when `cop`»); this is the same
        judgement one dependency further out, where the word is the root and there is no `cop` to
        read.
        """
        if head.upos != "AUX":
            return False
        match = marks.get(head.index)
        if match is None or match.compiled.get("when") != "cop":
            return False
        return not any(child.bare_dep == "expl" for child in skeleton.children(head.index))

    def _clause_heads(self, skeleton: Skeleton) -> list[Word]:
        """The root, and every word that opens a clause of its own — in sentence order.

        Sentence order rather than tree order because row order carries SCOPE (req 35), and the
        order the speaker used is the only scope information the surface gives.
        """
        found = [w for w in skeleton
                 if self._readable(w)
                 and (w.is_root or (w.bare_dep in CLAUSE_DEPS and w.upos in ("VERB", "AUX", "ADJ",
                                                                            "NOUN", "PROPN", "PRON")))]
        return sorted(found, key=lambda w: w.index)

    def _owners(self, skeleton: Skeleton, heads: list[Word]) -> dict[int, int]:
        """Which clause each token belongs to — walk up until a clause head is reached.

        Bounded like every walk over this structure: a malformed skeleton with a head cycle must
        fail rather than stop responding.
        """
        names = {w.index for w in heads}
        owner: dict[int, int] = {}
        for word in skeleton:
            node = word
            for _ in range(len(skeleton)):
                if node.index in names:
                    owner[word.index] = node.index
                    break
                if node.is_root:
                    owner[word.index] = node.index
                    break
                node = skeleton[node.head]
            else:
                owner[word.index] = skeleton.root.index
        return owner

    def _clause(self, skeleton: Skeleton, head: Word, mine: set[int], marks: dict,
                covered: Placements, prefix_rows: list, abstained: list, name: str,
                open_truth: set, wants_antecedent: set,
                defaulted: list | None = None, modifiers: list | None = None,
                adverb_joins: list | None = None,
                context: Context = NO_CONTEXT) -> ContentRow:
        """One clause → one content row. Only the tokens this clause owns are read."""
        boxes: dict[Role, Box] = {}
        unresolved: list[tuple[Word, Box]] = []
        adverbs_here: list[Word] = []
        predicate = None
        copular = False

        if self._is_copular_root(head, skeleton, marks):
            # `be` as root, doing copular work: it earns NO predicate (req 31) and no box either —
            # it is glue, and «Where is the cat?» is a LOCATION question about the cat, not a claim
            # about `be`. The subject becomes the topic through `copular` below.
            covered.add(head.index, "structure")
            copular = True
        elif head.upos in ("VERB", "AUX"):
            predicate = self._key(head)
            covered.add(head.index, f"predicate:{name}")
        else:
            # A NON-VERB ROOT IS THE COMPLEMENT — «Sue is a teacher» — **unless it carries a role
            # marker and there is no copula to make it one.** «out of the box» is a SOURCE that the
            # speaker said out loud, and defaulting it to `complement` threw the marker's meaning
            # into the default while keeping the marker's spelling, which reads as understood and is
            # not. In a copular clause the root IS the complement by construction (req 31), so the
            # marker does not get to override; in a bare fragment it is the only evidence there is.
            marked = None
            if not any(c.bare_dep == "cop" for c in skeleton.children(head.index)):
                marked = self._marker_role(head, skeleton, marks, defaulted)
            role = marked or Role.COMPLEMENT
            boxes[role] = self._box_for(head, skeleton, marks, covered, prefix_rows, name,
                                        modifiers, abstained)
            covered.add(head.index, f"box:{role.value}")
            copular = True

        for index in sorted(mine):
            if index in covered:
                continue
            word = skeleton[index]
            match = marks.get(index)
            if match is not None:
                covered.update(self._compile_closed(word, match, skeleton, boxes, prefix_rows,
                                                    abstained, copular, name,
                                                    open_truth, wants_antecedent, context),
                               label=CLOSED_KIND_PLACES[match.kind] if match.kind in
                               CLOSED_KIND_PLACES else (match.kind or "structure"))
                continue
            if word.bare_dep in ADVERB_DEPS and word.upos == "ADV" and match is None:
                # **AN ADVERB TAKES ONE OF REQUIREMENT 23's FOUR SCOPES**, and the rows say which —
                # but it is placed AFTER this loop, not here. See `adverbs_here` below.
                adverbs_here.append(word)
                continue
            if word.bare_dep in DEPS_THAT_COMPILE_TO_NOTHING:
                # Addressing, not content. Dropped ON PURPOSE and recorded as such — a word that is
                # merely LEFT OUT and a word that compiles to nothing are different answers, and
                # `Zip.unplaced` is for the first (req 21).
                covered.add(index, "structure")
                continue
            role = self._role_of(word, skeleton, marks, copular, defaulted)
            if role is not None and role not in boxes:
                boxes[role] = self._box_for(word, skeleton, marks, covered, prefix_rows, name,
                                            modifiers, abstained)
                covered.add(index, f"box:{role.value}")
            elif role is None and word.bare_dep in NOMINAL_DEPS:
                unresolved.append((word, self._box_for(word, skeleton, marks, covered,
                                                       abstained=abstained)))

        # **THE ADVERBS GO LAST, AND A MARKED NOMINAL OUTRANKS A BARE ONE FOR THE SAME BOX.** «left
        # EARLY in the MORNING» has two time expressions and one time box: `early` is `advmod` with
        # no marker, «in the morning» is a nominal whose marker SAYS time. The speaker chose the
        # marker, so it is the stronger evidence — and placing adverbs in token order let `early`
        # take the box and pushed `morning` out, which is the same coverage and the worse reading.
        for word in adverbs_here:
            reading = self.adverbs.read(word.lemma, word.dep)
            if reading.is_default and defaulted is not None:
                defaulted.append(f"{word.text}: manner (no row; the default)")
            covered.update(
                self._compile_adverb(word, reading, skeleton, boxes, prefix_rows, name,
                                     adverb_joins if adverb_joins is not None else [], abstained),
                label=f"adverb:{reading.kind}")

        for word, _box in unresolved:
            if word.index not in covered:
                abstained.append(f"{word.text}: nominal with no role")

        return ContentRow(name=name, predicate=predicate,
                          predicate_sense=Open() if predicate else None, boxes=boxes)

    def _relate(self, skeleton: Skeleton, heads: list[Word], content: dict[int, ContentRow],
                marks: dict, covered: Placements, prefix_rows: list, abstained: list) -> list[JoinRow]:
        """How the clauses stand to one another — a join, an attitude, or a shared variable.

        **THE TRUTH SLOT IS WHERE «IF» AND «BECAUSE» PART.** Both are IMPLY; what differs is whether
        the halves are claimed, and the row for the joining word is what says so (closed classes v4).
        Setting `truth` on a content row is therefore not bookkeeping — it is the assertion, and the
        heart reads it as supposition (heart 16) exactly as the evaluator reads it as a claim.
        """
        joins: list[JoinRow] = []
        # **A ROW IS CLAIMED UNLESS A JOIN SAYS OTHERWISE**, and the joins have not spoken yet. The
        # root is NOT claimed by being the root: «if it rains I stay home» asserts neither the rain
        # NOR the staying — only the conditional — and the main clause is the root in that sentence.
        # Deciding its truth before reading the joiner got that backwards, which is the whole
        # distinction req 38 rests on.
        unasserted: set[str] = set()
        for head in heads:
            if head.is_root:
                continue
            outer = self._enclosing(skeleton, head, content)
            if outer is None:
                continue
            joiner = self._joiner(skeleton, head, marks)

            if head.bare_dep == "acl":
                # A RELATIVE CLAUSE SHARES A VARIABLE with the phrase it modifies, rather than
                # joining it: «the cat that sleeps» is one cat, described twice (req 36).
                self._share_variable(skeleton, head, content, outer, prefix_rows, covered, marks)
                continue

            if joiner is not None and joiner.compiled.get("asserts") == ASSERTS_MATRIX:
                # A POV, not a join: «he says THAT you swim» claims the saying, never the swimming.
                self._attitude(skeleton, head, content, outer, prefix_rows, covered, joiner)
                unasserted.add(content[head.index].name)
                covered.update(range(joiner_index(skeleton, head, joiner),
                                     joiner_index(skeleton, head, joiner) + joiner.length),
                               label="join")
                continue

            operator = (joiner.compiled.get("operator") if joiner else None) or "and"
            asserts = (joiner.compiled.get("asserts") if joiner else None) or ASSERTS_BOTH
            if asserts == ASSERTS_AMBIGUOUS:
                # «when» is a generic conditional or a factual time clause, and only the theatre
                # separates them. Abstain rather than assert something the speaker may not have.
                abstained.append(f"{joiner.form}: asserts both readings; the theatre decides")
                asserts = ASSERTS_NEITHER

            inner, outer_row = content[head.index], content[outer.index]
            if outer_row.name in unasserted and asserts == ASSERTS_BOTH:
                # **UNASSERTION PROPAGATES DOWN, AND NOT PROPAGATING IT IS A TRUTH ERROR.** «if you
                # know WHO DID IT, tell me» does not assert that anybody did it — the whole antecedent
                # is supposed, and a clause inside it is inside the supposition. The AND that relates
                # them is honest; what was wrong was claiming its operand while the other half of the
                # conditional was explicitly not claimed.
                #
                # The heads are walked in SENTENCE ORDER, so an enclosing clause has always spoken
                # before the clause it encloses — which is why this reads `unasserted` rather than
                # needing a second pass.
                unasserted.add(inner.name)
            if asserts == ASSERTS_NEITHER:
                # STATED, NOT CLAIMED — both halves. The JOIN carries the claim, and the heart reads
                # this shape as supposition (heart 16) exactly as the evaluator reads a claim.
                unasserted.add(inner.name)
                unasserted.add(outer_row.name)

            # Row order is scope order, and the surface order is what the speaker chose: «if it
            # rains I stay home» and «I stay home if it rains» are the same two rows in the order
            # they were said. The ANTECEDENT is the subordinate clause either way.
            operands = ([inner.name, outer_row.name] if operator == "imply"
                        else sorted([outer_row.name, inner.name],
                                    key=lambda n: 0 if n == outer_row.name else 1))
            joins.append(JoinRow(name=f"j{len(joins)}", operator=Operator(operator),
                                 operands=operands, truth=CLAIMED))
            if joiner is not None:
                covered.update(range(joiner_index(skeleton, head, joiner),
                                     joiner_index(skeleton, head, joiner) + joiner.length),
                               label="join")

        # Now every join has spoken. What no join left unasserted, the speaker claimed.
        for row in content.values():
            if row.truth is None and row.name not in unasserted:
                row.truth = CLAIMED
        return joins

    def _ask(self, content: dict, joins: list, open_truth: set, wants_antecedent: set) -> list:
        """The two questions that are not boxes: an OPEN truth, and an unknown antecedent.

        Both are done after the clauses exist, because both are about a ROW rather than about a word:
        «whether» opens the truth of the clause it introduces, and «why» needs a second row to imply
        the first.
        """
        raised = []
        by_name = {row.name: row for row in content.values()}

        for name in open_truth:
            row = by_name.get(name)
            if row is not None:
                # «Is the cat hungry?» — every box bound, and the TRUTH is what is asked (E2).
                row.truth = Open()

        for name in wants_antecedent:
            row = by_name.get(name)
            if row is None:
                continue
            # A wholly OPEN row implying the one that was asserted. There is no cause box (req 37),
            # and this is the shape the collapse left in place of one.
            unknown = ContentRow(name=f"{name}_why", predicate=Open())
            raised.append(unknown)
            joins.append(JoinRow(name=f"j{len(joins)}", operator=Operator.IMPLY,
                                 operands=[unknown.name, row.name], truth=CLAIMED))
        return raised

    def _connect(self, adverb_joins: list, content: dict, joins: list, abstained: list) -> None:
        """A DISCOURSE adverb relates two ROWS, so it can only be built once both exist.

        «He was tired. Therefore he left.» — `therefore` is an IMPLY between the row it sits in and
        the one before it. That is requirement 23's fourth kind, and it is the same operator set the
        joining WORDS use, because it is the same relation: `db/0008` gave «because of» IMPLY and
        `db/0013` gives «therefore» IMPLY, one from a preposition and one from an adverb.

        **A CONNECTIVE WITH ONLY ONE ROW ABSTAINS.** «However, he left» in isolation names a contrast
        with something the sentence does not contain — usually the previous utterance, which is
        context and therefore an ARGUMENT (req 7) that this call does not have. Inventing the missing
        operand would be the silently-complete nearest fit.
        """
        order = [row.name for row in content.values()]
        for owner, operator, pragmatic in adverb_joins:
            position = order.index(owner) if owner in order else -1
            if position <= 0:
                abstained.append(f"a {operator} connective with no row before it — the other half is "
                                 f"context, which is an argument this call does not have (req 7)")
                continue
            join = JoinRow(name=f"j{len(joins)}", operator=Operator(operator),
                           operands=[order[position - 1], owner], truth=CLAIMED)
            joins.append(join)
            if pragmatic:
                # Parked by name, exactly as `db/0008` parked the concessive prepositions: the
                # defeated expectation is not truth-functional and the figurative layer will want
                # its cases when it is built.
                abstained.append(f"{operator} carries a parked `{pragmatic}` reading")

    def _compile_adverb(self, word: Word, reading, skeleton: Skeleton, boxes: dict,
                        prefix_rows: list, scopes: str, adverb_joins: list,
                        abstained: list) -> set[int]:
        """One adverb, placed by its KIND — requirement 23's four-way split, from the rows.

        Each kind lands somewhere the format already has, which is the whole reason the split is
        worth making:

          `circumstantial` -> a BOX, and `roles` says which (time, location, direction)
          `manner`         -> a manner box, carrying no head of its own (req 24)
          `epistemic`      -> the prefix's MODALITY element — the adverbial spelling of `may`/`must`
          `evaluative`     -> the prefix's ATTITUDE element; it does not touch truth
          `discourse`      -> a JOIN between this row and the one before it

        The discourse case is deferred to `_relate`'s neighbourhood, because a join needs two rows
        and only one exists here.
        """
        taken = {word.index}
        kind = reading.kind
        compiled = reading.compiled

        if compiled.get("kind") == "box":
            role = Role(reading.role) if reading.role else None
            if role is None or role in boxes:
                return taken if role is not None else set()
            # A circumstantial adverb IS its own filler — «yesterday» is the time, with no nominal
            # under it. The head is the adverb's own key, and the sense stays OPEN like every other.
            boxes[role] = Box(head=self._key(word), sense=Open())
            return taken

        if compiled.get("kind") == "prefix":
            element = compiled.get("element")
            if element == "modality" and compiled.get("modality"):
                prefix_rows.append(ModalityRow(name=f"p{len(prefix_rows)}", scopes=scopes,
                                               modality=Modality(compiled["modality"])))
                return taken
            if element == "attitude":
                # **AN ATTITUDE SCOPES A MATRIX AND DOES NOT CHANGE ITS TRUTH** — «luckily he left»
                # asserts that he left. tkzip's prefix has an attitude element and E2 put it there
                # for exactly this; what it holds is an ATTITUDE HOLDER, and an evaluative adverb
                # names no holder — it is the speaker's, and the speaker is the POV's business.
                # So it is recorded as an abstention rather than compiled into something it is not.
                abstained.append(f"{word.text}: evaluative — an attitude whose holder is the "
                                 f"speaker, and the prefix wants a holder")
                return taken
            return set()

        if compiled.get("kind") == "join" and compiled.get("operator"):
            adverb_joins.append((scopes, compiled["operator"], compiled.get("pragmatic")))
            return taken

        return set()

    def _modify(self, modifiers: list, joins: list) -> list:
        """**ATTRIBUTIVE ADJECTIVES BECOME ROWS** — tkzip req 70, and the shape is the drill's own.

        «I live in a human body» is hand-compiled in E2's drill as

            EXISTS B restricted to body.n, scoping the JOIN
            hu:  patient = B, complement = human.a
            me:  live.v, agent = me.n, location = (B, marker «in»)
            j1:  AND (hu, me)

        Three things in that are not obvious and all three are load-bearing. The adjective row has
        **no predicate** — req 31, «the cat is cute» is cat + cute and no verb. Its subject is the
        **patient**, not the topic, which is the copular row's shape E2 ruled and the drill uses 43
        times. And **the binder scopes the JOIN, not either row**, because the variable is shared
        across both and a binder scoping one of them would leave the other's `B` unbound.

        Several adjectives chain: «large hot dogs» is AND(large, AND(hot, eats)), one join apiece,
        exactly as the drill chains j1, j2, j3.
        """
        raised = []
        attached: dict[str, str] = {}      # owner row -> the conjunction built over it so far
        binders: dict[str, list] = {}      # owner row -> every binder whose scope must follow it
        for position, (var, key, binder, owner) in enumerate(modifiers):
            row = ContentRow(
                name=f"m{position}", truth=CLAIMED,
                boxes={Role.PATIENT: Box(head=Var(name=var), sense=Open()),
                       Role.COMPLEMENT: Box(head=key, sense=Open())})
            raised.append(row)
            # **ONE TREE PER CLAUSE, NOT ONE JOIN PER ADJECTIVE.** Two nouns each carrying an
            # adjective would otherwise produce two joins both naming the content row — logically
            # sound, and not what the drill does: it chains j1, j2, j3 into a single conjunction.
            # A zip with two unrelated top-level assertions says the same thing in a shape nothing
            # else in the format uses.
            join = JoinRow(name=f"j{len(joins)}", operator=Operator.AND,
                           operands=[row.name, attached.get(owner, owner)], truth=CLAIMED)
            joins.append(join)
            attached[owner] = join.name
            binders.setdefault(owner, []).append(binder)

        # THE BINDERS MOVE TO SCOPE THE WHOLE CONJUNCTION. Each was raised scoping the content row,
        # because that was all that existed when `_box_for` ran; now its variable lives in two rows
        # and only the outermost join covers both. Their ORDER is unchanged, and row order is scope
        # order (req 35) — so the prefix still reads left to right as the speaker said it.
        for owner, raised_binders in binders.items():
            for binder in raised_binders:
                binder.scopes = attached[owner]
        return raised

    def _enclosing(self, skeleton: Skeleton, head: Word, content: dict) -> Word | None:
        """The clause this one hangs off — its head's own clause."""
        node = skeleton[head.head]
        for _ in range(len(skeleton)):
            if node.index in content and node.index != head.index:
                return node
            if node.is_root:
                return node if node.index != head.index else None
            node = skeleton[node.head]
        return None

    def _joiner(self, skeleton: Skeleton, head: Word, marks: dict):
        """The `mark` or `cc` that introduces this clause — where the operator and the assertion
        status both come from."""
        for child in skeleton.children(head.index):
            if child.bare_dep in ("mark", "cc") and child.index in marks:
                return marks[child.index]
        return None

    def _contexts(self, skeleton: Skeleton, heads: list[Word], marks: dict,
                  context: Context) -> dict[int, Context]:
        """Which context each clause is compiled under — the person axis, rotated by the tree.

        **Only an ATTITUDE rotates.** A conditional does not: «if you know who did it» is still the
        outer speaker's «you». What makes a clause an attitude is its joiner saying `asserts: matrix`
        — «he says THAT you swim» claims the saying and not the swimming — which is the same test
        `_relate` uses to raise the `AttitudeRow`, read here one pass earlier.

        The holder and addressee are read from the SKELETON rather than from the compiled row,
        because the rows do not exist yet. That is a small duplication of `_role_of`'s job and it is
        the honest one: the alternative is to compile the clauses twice.
        """
        if context.is_empty:
            return {}
        found: dict[int, Context] = {}
        for head in heads:
            if head.is_root:
                continue
            joiner = self._joiner(skeleton, head, marks)
            if joiner is None or joiner.compiled.get("asserts") != ASSERTS_MATRIX:
                continue
            outer = self._enclosing(skeleton, head, {w.index: None for w in heads})
            if outer is None:
                continue
            holder = addressee = None
            for child in skeleton.children(outer.index):
                if child.bare_dep == "nsubj" and self._readable(child):
                    holder = self._key(child)
                elif self._role_of(child, skeleton, marks) is Role.RECIPIENT:
                    addressee = self._key(child) if self._readable(child) else None
            found[head.index] = replace(
                context,
                speaker=holder if holder is not None else context.speaker,
                addressee=addressee if addressee is not None else context.addressee,
            )
        return found

    def _attitude(self, skeleton, head, content, outer, prefix_rows, covered, joiner) -> None:
        """«he says that you swim» — an ATTITUDE over the inner row, claiming only the saying.

        `verb` is a key rather than a member of an enum: attitude verbs are open (think, believe,
        suppose, want, fear, pretend, hope, doubt), so the classification is nearest-anchor geometry
        over a small anchor set and never misses the verb nobody thought of (req 55).
        """
        outer_row = content[outer.index]
        holder = outer_row.boxes.get(Role.AGENT) or Box(head=Open(), sense=Open())
        # **THE ADDRESSEE, schema v3.** «John said TO MARIE that…» — the person the attitude is
        # directed at, which an attitude with only a holder could not say. It is the `recipient` of
        # the attitude verb's own row, and it is EMPTY where there is none: thinking addresses
        # nobody, and that absence is what stops «John thinks I am wrong» rotating.
        prefix_rows.append(AttitudeRow(
            name=f"p{len(prefix_rows)}", scopes=content[head.index].name,
            holder=holder, addressee=outer_row.boxes.get(Role.RECIPIENT),
            verb=self._key(outer)))
        # the inner row stays EMPTY: the attitude is claimed, its content is not

    def _share_variable(self, skeleton, head, content, outer, prefix_rows, covered, marks) -> None:
        """A relative clause describes the SAME thing as the phrase it modifies — one variable in
        two rows, which is req 36's one binding mechanism doing the work a second box would fake."""
        inner = content[head.index]
        name = f"y{len(prefix_rows) + len(content)}"
        target = skeleton[head.head]
        for role, box in content[outer.index].boxes.items():
            if box.head == self._key(target):
                content[outer.index].boxes[role] = Box(
                    head=Var(name=name), sense=Open(), determination=box.determination,
                    quantity=box.quantity, marker=box.marker, relation=box.relation)
                break
        for role, box in list(inner.boxes.items()):
            if isinstance(box.head, Open) or box.head is None:
                inner.boxes[role] = Box(head=Var(name=name), sense=Open())
                break
        else:
            inner.boxes[Role.AGENT] = Box(head=Var(name=name), sense=Open())
        # The relative pronoun IS the variable — «the cat THAT sleeps» has no third participant.
        for child in skeleton.children(head.index):
            if child.bare_dep in ("nsubj", "obj") and marks.get(child.index) is not None:
                covered.add(child.index, "var")

    # -- the pieces -------------------------------------------------------------------------------

    def _read_closed(self, skeleton: Skeleton) -> dict[int, object]:
        return {i: m for i, m in self.table.walk_skeleton(skeleton)}

    def _readable(self, word: Word) -> bool:
        """Can this token become a dictionary key at all?

        **A PROVIDER EMITS TOKENS UD DOES NOT DEFINE.** stanza tags trailing whitespace `SPACE`,
        which is not one of UD's seventeen, and its lemma normalises to nothing — so `key_of` raised
        `InvalidKey` and **the compiler stopped**. A station that stops is neither half-understood nor
        wrongly-understood: it is a station that produced no zip at all, which req 8 does not even
        contemplate. The drill gate found it on its first run (req 18), on five of the Captain's own
        sentences, because his annotations («[de dicto]») leave trailing space that UD's tidy
        examples never have.
        """
        return word.upos in UD_POS and bool(keymod.normalize_word(word.lemma or ""))

    def _key(self, word: Word) -> str:
        """A content word's dictionary key — `eat.v`. The sense stays OPEN beside it."""
        letter = POS_LETTER.get(word.upos, "n")
        return keymod.key_of(word.lemma, letter)

    def _marks_a_possessor(self, word: Word, skeleton: Skeleton, marks: dict) -> bool:
        """Is this `nmod` a POSSESSOR, or a modifier that merely happens to hang off a noun?

        «the office OF the Chair» is a possessor; «the cafe UP BESIDE the lookout» is a LOCATION, and
        reading the second as a possessor said the cafe belonged to the lookout. `nmod` + a noun head
        is not enough — **the marker decides**, exactly as it decides under `obl`.

        **AND THE MARKER IS ASKED, NOT LISTED** (the Captain's rule of 2026-09-16: before a set goes
        in code, is it frame or knowledge?). «Which prepositions spell a possessor» is a contingent
        fact about English, so `{"of", "'s"}` would have been a hand list in a file whose whole
        purpose is to end them. The rows already say it: `'s` compiles to `field: relation`, and
        `db/0012` gives `of` the rule «head is a NOUN -> relation». So the test is *what does this
        marker produce here*, and a new possessive spelling is a migration.
        """
        markers = [marks[c.index] for c in skeleton.children(word.index)
                   if marks.get(c.index) is not None and marks[c.index].kind in ("box", "field")]
        if not markers:
            return True          # a bare `nmod` under a noun — «the Chair office», the plain case
        head = skeleton[word.head]
        for match in markers:
            if match.kind == "field" and match.compiled.get("field") == "relation":
                return True
            settled = self.selector.settle(match.compiled, word.lemma, word.upos,
                                           head.lemma, head.upos)
            if settled is not None and settled.role == "relation":
                return True
        return False

    def _role_of(self, word: Word, skeleton: Skeleton, marks: dict,
                 copular: bool = False, defaulted: list | None = None) -> Role | None:
        """Which box this nominal fills — by RELATION first, then by its MARKER.

        Relation first because it is the stronger evidence and the narrower claim: `obj` means
        patient in every sentence, while `in` means four things. Where the relation says nothing
        (`obl`, `nmod` — «a nominal dependent», which is not a role) the marker is asked.
        """
        settled = RELATION_FILLS_ROLE.get(word.dep) or RELATION_FILLS_ROLE.get(word.bare_dep)
        if settled is not None:
            if settled is Role.AGENT and copular:
                # Nobody is acting in «Sue is a teacher» — the subject of a copula is what the
                # complement is said OF.
                #
                # **IT IS `patient`, AND THIS WAS WRONG UNTIL 2026-09-16.** The compile core reasoned
                # its way to `topic` from «what the complement is said of», which is sound English
                # and the wrong role name: in THIS inventory `topic` is SUBJECT MATTER — the thing
                # «about» and «on» mark, «a lecture ON physics» — and the drill uses it for exactly
                # that and for nothing else. E2 ruled the copular row's shape explicitly
                # (`202609111511_notes.md`: row · POV · **patient** · complement) and the drill hand-
                # compiles it **43 times**. A lone deviation in code against the format's own gate is
                # the deviation that moves.
                return Role.PATIENT
            return settled
        if word.bare_dep not in NOMINAL_DEPS:
            return None

        # A NOMINAL HANGING OFF A NOUN IS THE POSSESSOR, not a box of the clause: «the office OF the
        # Chair» is one phrase, and tkzip keeps the possessor INSIDE the record (req 26). `_box_for`
        # takes it when the head phrase is built, so it must not also claim a role here.
        head = skeleton[word.head]
        if word.bare_dep == "nmod" and head.upos in ("NOUN", "PROPN") \
                and self._marks_a_possessor(word, skeleton, marks):
            return None

        return self._marker_role(word, skeleton, marks, defaulted)

    def _marker_role(self, word: Word, skeleton: Skeleton, marks: dict,
                     defaulted: list | None = None) -> Role | None:
        """The role this nominal's own CASE MARKER gives it, or None if it has none that decides.

        Split out of `_role_of` because a ROOT has to be able to ask it. `_role_of` gates on
        `NOMINAL_DEPS` — `obl`, `nmod`, `nsubj`… — and `root` is in none of them, so «out of the
        box» could never reach its marker and fell to the `complement` default with the marker's
        spelling kept and its meaning discarded.
        """
        head = skeleton[word.head]
        for child in skeleton.children(word.index):
            match = marks.get(child.index)
            if match is None or match.kind != "box":
                continue
            if match.settled_role:
                return Role(match.settled_role)
            if len(match.roles) == 1:
                return Role(match.roles[0])
            # **ONE OF THE THIRTEEN**, and `db/0012` says what settles it: the head's POS for «of»,
            # the marked nominal's SUPERSENSE for «at noon» against «at the door», the head verb's
            # for «walk to the station» against «talk to my friend». A rule that fires is evidence
            # from the sentence; a rule that does not leaves the curation's best-first default —
            # and the two are kept apart rather than averaged, because req 8 forbids the SILENTLY
            # complete nearest fit and a default that is counted is not silent.
            settled = self.selector.settle(
                match.compiled, word.lemma, word.upos, head.lemma, head.upos)
            if settled is None:
                return None
            if settled.role not in {role.value for role in Role}:
                # The selector named a FIELD, not a box — «the office OF the Chair» is a possessor
                # and req 26 keeps it INSIDE the record. `_box_for` takes it when the head phrase is
                # built, so there is no role to fill here and no abstention to report.
                return None
            if settled.is_default and defaulted is not None:
                defaulted.append(f"{match.form} {word.text}: {settled.role} (nothing chose)")
            return Role(settled.role)
        return None

    def _box_for(self, word: Word, skeleton: Skeleton, marks: dict, covered: Placements,
                 prefix_rows: list | None = None, scopes: str = "r0",
                 modifiers: list | None = None, abstained: list | None = None) -> Box:
        """The seven-field record for one nominal phrase — per PHRASE, never one per clause.

        Every field is independently bindable (req 47): `head` may be BOUND while `sense` is OPEN,
        `count` may be OPEN («how many cats?»), `relation` may be OPEN («whose cat?»).
        """
        determination = None
        quantity = None
        count = None
        marker = None
        relation = None
        for child in skeleton.children(word.index):
            match = marks.get(child.index)
            if match is None:
                continue
            kind = match.kind
            if kind == "determination":
                determination = Determination(match.compiled["determination"])
                covered.add(child.index, "determination")
            elif kind == "quantifier" and match.compiled.get("quantity"):
                quantity = Quantity(match.compiled["quantity"])
                covered.add(child.index, "quantifier")
            elif kind == "box":
                marker = match.form
                # A MULTI-WORD MARKER COVERS EVERY TOKEN IT SPANS. «out OF the box» is one form and
                # `of` hangs off `out` as UD's `fixed`; marking only the first token left `of`
                # looking unplaced in a sentence that was fully understood.
                covered.update(range(child.index, child.index + match.length), label="marker")
            elif kind == "field" and match.compiled.get("field") == "relation":
                # the possessive clitic: «the Chair 's office» — the possessor is a FIELD (req 26)
                covered.add(child.index, "field:relation")
            elif kind == "open" and match.compiled.get("opens") == "field":
                # «WHOSE cat sleeps?» — the possessor is asked. It is a FIELD of the record (req 26),
                # so the question opens the field rather than adding a box.
                relation = Open()
                covered.add(child.index, "field:relation")
            elif kind == "entity" and child.dep in ("nmod:poss", "det:poss"):
                # «MY friend» — a possessive pronoun is indexical, so the possessor is OPEN and
                # resolved from context, never `my.n`.
                relation = Open()
                covered.add(child.index, "field:relation")
        # **THE NUMERAL FILLS `count`, WHICH IS NOT `quantity` AND NOT `determination`** (req 26:
        # the three are orthogonal, and «the three cats» is definite AND counted). A numeral is not a
        # quantifier — it does not bind — so it raises no binder and changes no scope; it is a field
        # of the record, exactly as the possessor is.
        for child in skeleton.children(word.index):
            if child.bare_dep != "nummod" or marks.get(child.index) is not None:
                continue
            value = numeral_value(child.lemma, child.text)
            if value is None:
                # A number WORD, and this station cannot read one — see `numeral_value`. The phrase
                # still lands; only the count is missing, which is what a seven-field record is for.
                if abstained is not None:
                    abstained.append(f"{child.text}: a numeral this station cannot read — digits "
                                     f"only until `word2number` is admitted")
                continue
            count = value
            covered.add(child.index, "count")

        # A possessor NOUN — «the office of the Chair», «the Chair 's office». Both spellings reach
        # here, which is the pairing UD's own `case` page makes explicit.
        for child in skeleton.children(word.index):
            if child.bare_dep == "nmod" and child.upos in ("NOUN", "PROPN") \
                    and self._marks_a_possessor(child, skeleton, marks):
                relation = self._key(child)
                covered.add(child.index, "field:relation")
                # AND EVERY WORD THE POSSESSOR PHRASE SPANS SAYS WHERE IT WENT. These used to be
                # covered with no label — «counted as understood without saying what it became» —
                # and the placement trace is what made that visible: three cases reported `of`,
                # `'s` and `beside` as never reaching the zip, in sentences that compiled fine.
                for grandchild in skeleton.children(child.index):
                    found = marks.get(grandchild.index)
                    if found is None:
                        continue
                    covered.update(range(grandchild.index, grandchild.index + found.length),
                                   label="determination" if found.kind == "determination"
                                   # «the office OF the Chair» — the marker went to the FIELD, not
                                   # to a box, because that is where the possessor lives (req 26).
                                   else "field:relation" if found.kind in ("box", "field")
                                   else found.kind)
        box = Box(head=self._key(word), sense=Open(), determination=determination,
                  quantity=quantity, count=count, marker=marker, relation=relation)
        # **AN ATTRIBUTIVE ADJECTIVE IS A SECOND ROW, AND A SECOND ROW NEEDS A VARIABLE** (tkzip
        # req 70): «a human body» is EXISTS B (body(B) AND human(B)). There is no other way to say
        # it — a row reading `patient=body.n, complement=human.a` would claim that BODIES are human,
        # which is a statement about the kind and not about this one. So the adjective forces the
        # binder that req 36 already provides, and the box refers to the variable.
        adjectives = [c for c in skeleton.children(word.index)
                      if c.bare_dep == "amod" and c.upos in ("ADJ", "VERB")]
        if adjectives and quantity is None:
            # No quantifier word, so the force comes from the phrase itself. EXISTENTIAL, because
            # «a human body» is the drill's own worked case and it is existential — and the
            # determination rides along beside it, which is exactly what req 26 split them for.
            # *A bare plural («large dogs») is genericity, which E2 parked; it reads existential
            # here and that is the honest approximation rather than a silent universal.*
            quantity = Quantity.EXISTENTIAL
        if quantity is not None and prefix_rows is not None:
            # THE BINDER, and the box that referred to the noun now refers to the VARIABLE. That
            # indirection is req 36's whole point: one binding mechanism for quantification,
            # questions, equations and naming, instead of a quantified phrase the evaluator has to
            # synthesise a variable for.
            name = f"x{len(prefix_rows)}"
            binder = QuantifierRow(name=f"q{len(prefix_rows)}", scopes=scopes, binds=name,
                                   quantity=quantity, determination=determination,
                                   restriction=box)
            prefix_rows.append(binder)
            for adjective in adjectives:
                if modifiers is not None:
                    modifiers.append((name, self._key(adjective), binder, scopes))
                covered.add(adjective.index, "row")
            return Box(head=Var(name=name), sense=Open())
        return box

    def _compile_closed(self, word: Word, match, skeleton: Skeleton, boxes: dict,
                        prefix_rows: list, abstained: list,
                        copular: bool = False, scopes: str = "r0",
                        open_truth: set | None = None,
                        wants_antecedent: set | None = None,
                        context: Context = NO_CONTEXT) -> set[int]:
        """What a closed-class form does to the zip. Returns the token indices it accounted for."""
        kind = match.kind
        taken = {word.index + n for n in range(match.length)}
        open_truth = open_truth if open_truth is not None else set()
        wants_antecedent = wants_antecedent if wants_antecedent is not None else set()

        if kind == "prefix":
            element = match.compiled.get("element")
            if element == "negation":
                prefix_rows.append(NegationRow(name=f"p{len(prefix_rows)}", scopes=scopes))
            elif element == "modality":
                from tk2.tkzip.schema import Modality, ModalityRow

                prefix_rows.append(ModalityRow(name=f"p{len(prefix_rows)}", scopes=scopes,
                                              modality=Modality(match.compiled["modality"])))
            return taken

        if kind == "quantifier":
            # **A QUANTIFIER IS BUILT WITH THE PHRASE IT RESTRICTS, never on meeting the word.**
            # `QuantifierRow.restriction` is a Box — «all CATS» — and the schema's own docstring
            # says why: «All cats are mammals» becomes a binder for X restricted to cats, then a
            # content row saying X is a mammal. Emitting the binder here would have to invent a
            # restriction the sentence has not reached yet. `_box_for` raises it instead, when the
            # noun this determiner hangs off is built.
            return taken

        if kind == "box":
            # The MARKER itself is accounted for here; which role it fills is decided where the
            # nominal it marks is read (`_role_of`), because that is where the head and the noun
            # are both in hand. A marker with several readings and NO selector — a row an older
            # migration wrote — still abstains, which is what the absence of a rule means.
            if not match.settled_role and len(match.roles) > 1 \
                    and not match.compiled.get("selector"):
                abstained.append(f"{match.form}: {'|'.join(match.roles)}")
            return taken

        if kind == "open" and match.compiled.get("opens"):
            # **A QUESTION IS SOMETHING OPEN** — there is no mood field (E2). Which slot, the row
            # says; five kinds, and three of them are not boxes at all.
            opens = match.compiled["opens"]

            if opens == "box":
                boxes[Role(match.compiled["role"])] = Box(head=Open(), sense=Open())
                return taken

            if opens == "participant":
                # The role arrives by RELATION, exactly as it does for every other nominal
                # (req 12): «WHO sleeps» is `nsubj` and «WHAT did you eat» is `obj`.
                role = (RELATION_FILLS_ROLE.get(word.dep)
                        or RELATION_FILLS_ROLE.get(word.bare_dep))
                if role is not None and role not in boxes:
                    boxes[role] = Box(head=Open(), sense=Open())
                    return taken
                abstained.append(f"{match.form}: a participant, and the relation does not say which")
                return set()

            if opens == "truth":
                # The polar question, in its subordinate spelling: every box bound, truth OPEN.
                open_truth.add(scopes)
                return taken

            if opens == "antecedent":
                # **THERE IS NO CAUSE BOX TO OPEN** (req 37): «why do you sleep?» asks for an
                # unknown row implying this one. The antecedent is raised in `_relate`, where the
                # rows exist to be joined.
                wants_antecedent.add(scopes)
                return taken

            if opens == "field":
                # «WHOSE cat sleeps?» — the possessor is a field of the record (req 26). It is set
                # on the box its noun builds, so nothing is done here but accounting for the word.
                return taken

        if kind == "entity":
            # A PRONOUN FILLS ITS BOX. «I sleep» has an agent — it is not an unplaced word. Content
            # is defined, structure is compiled (the second standing law): a pronoun is INDEXICAL,
            # resolved to an entity from context before the dictionary is consulted, so the box is
            # filled with an OPEN head rather than with `i.n`. It never earns a dimension.
            # **A REFERENTIAL ADVERB CARRIES ITS OWN BOX** (closed classes v7, `db/0014`). «They come
            # HERE» is a location and «I left THEN» a time, and `advmod` is not a nominal relation,
            # so `_role_of` could never reach one — the word was left unplaced in a sentence
            # otherwise understood. The ROW says which box; the head stays OPEN because the form is
            # indexical and context resolves it (req 7).
            named = match.compiled.get("roles") or ()
            role = Role(named[0]) if named else self._role_of(word, skeleton, {}, copular)
            if role is not None and role not in boxes:
                # **THE PERSON AXIS, AS FAR AS IT GOES WITHOUT THE ROTATION.** `i` and `you` carry
                # `person: 1` and `person: 2` in their own rows — the axis has had its data since
                # v1 and no caller to supply the other end. The context is that caller.
                #
                # **THIRD PERSON IS NOT HERE AND THAT IS NOT AN OVERSIGHT**: «he» and «they» are
                # ANAPHORA — they point at something earlier in the discourse, not at a participant
                # in the speech act — so `Context.for_person` answers for 1 and 2 only.
                #
                # **AND THIS DOES NOT ROTATE YET.** A first-person pronoun under a POV names that
                # POV's holder, not the outer speaker (req 20), and building that waits on the
                # Captain's ruling about where an ADDRESSEE lives. What is here is the outer speech
                # act's own participants, which is right whenever there is no POV above the word.
                who = context.for_person(match.features.get("person"))
                boxes[role] = Box(head=who if who is not None else Open(), sense=Open(),
                                  determination=Determination.DEFINITE)
                return taken
            # A possessive pronoun («MY friend») is the possessor of the phrase it hangs off, and is
            # taken by `_box_for` when that phrase is built.
            return taken if word.bare_dep in ("nmod:poss", "det:poss", "det") else set()

        if kind in ("structure", "determination", "field", "theatre", "join",
                    "restriction", "open", "ambiguous"):
            # Handled where they attach (determination, field), or not yet compiled (join,
            # restriction, open) — and in the second case the word stays UNPLACED rather than
            # vanishing, which is what `Zip.unplaced` is for.
            if kind in ("determination", "field", "structure", "theatre"):
                return taken
            if kind in LATER_PASS_OWNS:
                # **NOT AN ABSTENTION: A LATER PASS OWNS IT.** `_relate` builds the joins and
                # `_share_variable` the relative pronouns, and both run after every clause is
                # compiled — so reporting them here said the station had given up on words it
                # goes on to place correctly. A report that cries wolf is worse than no report,
                # and «if» was in the abstention list of a sentence whose IMPLY it had built.
                return taken
            abstained.append(f"{match.form}: {kind} is not compiled yet")
            return set()
        return taken


def joiner_index(skeleton: Skeleton, head: Word, joiner) -> int:
    """Where the joining word sits — needed to mark it covered, since it is read from the clause it
    introduces rather than walked over in order."""
    for child in skeleton.children(head.index):
        if child.bare_dep in ("mark", "cc"):
            return child.index
    return head.index


def compile_sentence(skeleton: Skeleton, table: ClosedClasses) -> Compiled:
    """One call, for a caller that holds no compiler."""
    return Compiler(table).compile(skeleton)
