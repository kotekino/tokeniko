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

from dataclasses import dataclass, field

from tk2.dictionary import keys as keymod
from tk2.language.closed import ClosedClasses
from tk2.language.markers import MarkerSelector
from tk2.language.skeleton import Skeleton, Word
from tk2.tkzip.schema import (
    AttitudeRow,
    Box,
    Var,
    ContentRow,
    Determination,
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

#: A claim the station makes with no fuzziness of its own: the speaker said it, so it is stated at
#: full strength. What the claim is WORTH is the evaluator's question, not the parser's.
CLAIMED = 1.0


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

    def __init__(self, table: ClosedClasses, selector: MarkerSelector | None = None) -> None:
        self.table = table
        #: WHICH role an ambiguous marker fills here — `db/0012`'s rules, run by
        #: `tk2.language.markers`. An argument so a test can state what the resource says instead
        #: of depending on which WordNet is installed.
        self.selector = selector or MarkerSelector()

    # -- the whole sentence -----------------------------------------------------------------------

    def compile(self, skeleton: Skeleton) -> Compiled:
        """Skeleton → zip. One content row per CLAUSE, related by joins and attitudes.

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

        covered: set[int] = set()
        abstained: list[str] = []
        defaulted: list[str] = []
        prefix_rows: list = []
        content: dict[int, ContentRow] = {}
        open_truth: set[str] = set()          # rows whose TRUTH was asked («whether», a polar)
        wants_antecedent: set[str] = set()    # rows asked «why» — an unknown row implies them

        for position, head in enumerate(heads):
            mine = {i for i, h in owner.items() if h == head.index}
            content[head.index] = self._clause(
                skeleton, head, mine, marks, covered, prefix_rows, abstained, f"r{position}",
                open_truth, wants_antecedent, defaulted)

        joins = self._relate(skeleton, heads, content, marks, covered, prefix_rows, abstained)
        extra = self._ask(content, joins, open_truth, wants_antecedent)

        unplaced = tuple(w.text for w in skeleton
                         if w.index not in covered and w.upos not in ("PUNCT", "SYM"))

        rows = [*prefix_rows, *content.values(), *extra, *joins]
        return Compiled(zip=Zip(rows=rows, unplaced=list(unplaced)),
                        covered=tuple(sorted(covered)), unplaced=unplaced,
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
                 if w.is_root or (w.bare_dep in CLAUSE_DEPS and w.upos in ("VERB", "AUX", "ADJ",
                                                                           "NOUN", "PROPN", "PRON"))]
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
                covered: set[int], prefix_rows: list, abstained: list, name: str,
                open_truth: set, wants_antecedent: set,
                defaulted: list | None = None) -> ContentRow:
        """One clause → one content row. Only the tokens this clause owns are read."""
        boxes: dict[Role, Box] = {}
        unresolved: list[tuple[Word, Box]] = []
        predicate = None
        copular = False

        if self._is_copular_root(head, skeleton, marks):
            # `be` as root, doing copular work: it earns NO predicate (req 31) and no box either —
            # it is glue, and «Where is the cat?» is a LOCATION question about the cat, not a claim
            # about `be`. The subject becomes the topic through `copular` below.
            covered.add(head.index)
            copular = True
        elif head.upos in ("VERB", "AUX"):
            predicate = self._key(head)
            covered.add(head.index)
        else:
            boxes[Role.COMPLEMENT] = self._box_for(head, skeleton, marks, covered, prefix_rows, name)
            covered.add(head.index)
            copular = True

        for index in sorted(mine):
            if index in covered:
                continue
            word = skeleton[index]
            match = marks.get(index)
            if match is not None:
                covered.update(self._compile_closed(word, match, skeleton, boxes, prefix_rows,
                                                    abstained, copular, name,
                                                    open_truth, wants_antecedent))
                continue
            role = self._role_of(word, skeleton, marks, copular, defaulted)
            if role is not None and role not in boxes:
                boxes[role] = self._box_for(word, skeleton, marks, covered, prefix_rows, name)
                covered.add(index)
            elif role is None and word.bare_dep in NOMINAL_DEPS:
                unresolved.append((word, self._box_for(word, skeleton, marks, covered)))

        for word, _box in unresolved:
            if word.index not in covered:
                abstained.append(f"{word.text}: nominal with no role")

        return ContentRow(name=name, predicate=predicate,
                          predicate_sense=Open() if predicate else None, boxes=boxes)

    def _relate(self, skeleton: Skeleton, heads: list[Word], content: dict[int, ContentRow],
                marks: dict, covered: set[int], prefix_rows: list, abstained: list) -> list[JoinRow]:
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
                                     joiner_index(skeleton, head, joiner) + joiner.length))
                continue

            operator = (joiner.compiled.get("operator") if joiner else None) or "and"
            asserts = (joiner.compiled.get("asserts") if joiner else None) or ASSERTS_BOTH
            if asserts == ASSERTS_AMBIGUOUS:
                # «when» is a generic conditional or a factual time clause, and only the theatre
                # separates them. Abstain rather than assert something the speaker may not have.
                abstained.append(f"{joiner.form}: asserts both readings; the theatre decides")
                asserts = ASSERTS_NEITHER

            inner, outer_row = content[head.index], content[outer.index]
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
                                     joiner_index(skeleton, head, joiner) + joiner.length))

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

    def _attitude(self, skeleton, head, content, outer, prefix_rows, covered, joiner) -> None:
        """«he says that you swim» — an ATTITUDE over the inner row, claiming only the saying.

        `verb` is a key rather than a member of an enum: attitude verbs are open (think, believe,
        suppose, want, fear, pretend, hope, doubt), so the classification is nearest-anchor geometry
        over a small anchor set and never misses the verb nobody thought of (req 55).
        """
        outer_row = content[outer.index]
        holder = outer_row.boxes.get(Role.AGENT) or Box(head=Open(), sense=Open())
        prefix_rows.append(AttitudeRow(
            name=f"a{len(prefix_rows)}", scopes=content[head.index].name,
            holder=holder, verb=self._key(outer)))
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
                covered.add(child.index)

    # -- the pieces -------------------------------------------------------------------------------

    def _read_closed(self, skeleton: Skeleton) -> dict[int, object]:
        return {i: m for i, m in self.table.walk_skeleton(skeleton)}

    def _key(self, word: Word) -> str:
        """A content word's dictionary key — `eat.v`. The sense stays OPEN beside it."""
        letter = POS_LETTER.get(word.upos, "n")
        return keymod.key_of(word.lemma, letter)

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
                # complement is said OF. That is topicality, not agency.
                return Role.TOPIC
            return settled
        if word.bare_dep not in NOMINAL_DEPS:
            return None

        # A NOMINAL HANGING OFF A NOUN IS THE POSSESSOR, not a box of the clause: «the office OF the
        # Chair» is one phrase, and tkzip keeps the possessor INSIDE the record (req 26). `_box_for`
        # takes it when the head phrase is built, so it must not also claim a role here.
        head = skeleton[word.head]
        if word.bare_dep == "nmod" and head.upos in ("NOUN", "PROPN"):
            return None

        # its own case marker, if it has one
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

    def _box_for(self, word: Word, skeleton: Skeleton, marks: dict, covered: set[int],
                 prefix_rows: list | None = None, scopes: str = "r0") -> Box:
        """The seven-field record for one nominal phrase — per PHRASE, never one per clause.

        Every field is independently bindable (req 47): `head` may be BOUND while `sense` is OPEN,
        `count` may be OPEN («how many cats?»), `relation` may be OPEN («whose cat?»).
        """
        determination = None
        quantity = None
        marker = None
        relation = None
        for child in skeleton.children(word.index):
            match = marks.get(child.index)
            if match is None:
                continue
            kind = match.kind
            if kind == "determination":
                determination = Determination(match.compiled["determination"])
                covered.add(child.index)
            elif kind == "quantifier" and match.compiled.get("quantity"):
                quantity = Quantity(match.compiled["quantity"])
                covered.add(child.index)
            elif kind == "box":
                marker = match.form
                # A MULTI-WORD MARKER COVERS EVERY TOKEN IT SPANS. «out OF the box» is one form and
                # `of` hangs off `out` as UD's `fixed`; marking only the first token left `of`
                # looking unplaced in a sentence that was fully understood.
                covered.update(range(child.index, child.index + match.length))
            elif kind == "field" and match.compiled.get("field") == "relation":
                # the possessive clitic: «the Chair 's office» — the possessor is a FIELD (req 26)
                covered.add(child.index)
            elif kind == "open" and match.compiled.get("opens") == "field":
                # «WHOSE cat sleeps?» — the possessor is asked. It is a FIELD of the record (req 26),
                # so the question opens the field rather than adding a box.
                relation = Open()
                covered.add(child.index)
            elif kind == "entity" and child.dep in ("nmod:poss", "det:poss"):
                # «MY friend» — a possessive pronoun is indexical, so the possessor is OPEN and
                # resolved from context, never `my.n`.
                relation = Open()
                covered.add(child.index)
        # A possessor NOUN — «the office of the Chair», «the Chair 's office». Both spellings reach
        # here, which is the pairing UD's own `case` page makes explicit.
        for child in skeleton.children(word.index):
            if child.bare_dep == "nmod" and child.upos in ("NOUN", "PROPN"):
                relation = self._key(child)
                covered.add(child.index)
                for grandchild in skeleton.children(child.index):
                    if marks.get(grandchild.index) is not None:
                        covered.add(grandchild.index)
        box = Box(head=self._key(word), sense=Open(), determination=determination,
                  quantity=quantity, marker=marker, relation=relation)
        if quantity is not None and prefix_rows is not None:
            # THE BINDER, and the box that referred to the noun now refers to the VARIABLE. That
            # indirection is req 36's whole point: one binding mechanism for quantification,
            # questions, equations and naming, instead of a quantified phrase the evaluator has to
            # synthesise a variable for.
            name = f"x{len(prefix_rows)}"
            prefix_rows.append(QuantifierRow(name=f"q{len(prefix_rows)}", scopes=scopes, binds=name,
                                             quantity=quantity, determination=determination,
                                             restriction=box))
            return Box(head=Var(name=name), sense=Open())
        return box

    def _compile_closed(self, word: Word, match, skeleton: Skeleton, boxes: dict,
                        prefix_rows: list, abstained: list,
                        copular: bool = False, scopes: str = "r0",
                        open_truth: set | None = None,
                        wants_antecedent: set | None = None) -> set[int]:
        """What a closed-class form does to the zip. Returns the token indices it accounted for."""
        kind = match.kind
        taken = {word.index + n for n in range(match.length)}
        open_truth = open_truth if open_truth is not None else set()
        wants_antecedent = wants_antecedent if wants_antecedent is not None else set()

        if kind == "prefix":
            element = match.compiled.get("element")
            if element == "negation":
                prefix_rows.append(NegationRow(name=f"n{len(prefix_rows)}", scopes=scopes))
            elif element == "modality":
                from tk2.tkzip.schema import Modality, ModalityRow

                prefix_rows.append(ModalityRow(name=f"m{len(prefix_rows)}", scopes=scopes,
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
            role = self._role_of(word, skeleton, {}, copular)
            if role is not None and role not in boxes:
                boxes[role] = Box(head=Open(), sense=Open(),
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
