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
from tk2.language.skeleton import Skeleton, Word
from tk2.tkzip.schema import (
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
POS_LETTER = {"NOUN": "n", "PROPN": "n", "VERB": "v", "ADJ": "a", "ADV": "r"}

#: The relations that hang a NOMINAL off a head — the candidates for a box.
NOMINAL_DEPS = frozenset({"nsubj", "obj", "iobj", "obl", "nmod"})


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

    @property
    def coverage(self) -> float:
        total = len(self.covered) + len(self.unplaced)
        return 1.0 if not total else len(self.covered) / total


class Compiler:
    """Skeleton → zip. Pure: context is an argument and never state (req 7)."""

    def __init__(self, table: ClosedClasses) -> None:
        self.table = table

    # -- the whole sentence -----------------------------------------------------------------------

    def compile(self, skeleton: Skeleton) -> Compiled:
        root = skeleton.root
        if root is None:
            return Compiled(zip=Zip(rows=[ContentRow(name="r0")]), unplaced=skeleton.tokens)

        marks = self._read_closed(skeleton)
        covered: set[int] = set()
        prefix_rows: list = []
        boxes: dict[Role, Box] = {}
        abstained: list[str] = []
        unresolved: list[tuple[Word, Box]] = []

        # THE PREDICATE. Plain copular `be` compiles to STRUCTURE and earns no dimension (req 31):
        # «the cat is cute» is *cat + cute, no verb*. The row for `be` states that conditionally and
        # names the dependency that decides, so the check is «did the table say glue here», never a
        # list of verbs in this file.
        predicate = None
        copular = False
        if root.upos in ("VERB", "AUX"):
            predicate = self._key(root)
            covered.add(root.index)
        else:
            # A nominal or adjectival root IS the complement — the copula's predicate. «The cat is
            # cute» is *cat + cute, no verb* (req 31): `cute` is the complement and `cat` is the
            # thing it is said of, which is the TOPIC rather than an agent — nobody is acting.
            boxes[Role.COMPLEMENT] = self._box_for(root, skeleton, marks, covered, prefix_rows)
            covered.add(root.index)
            copular = True

        for word in skeleton:
            if word.index in covered:
                continue
            match = marks.get(word.index)

            if match is not None:
                consumed = self._compile_closed(word, match, skeleton, boxes, prefix_rows,
                                                abstained, copular)
                covered.update(consumed)
                continue

            role = self._role_of(word, skeleton, marks, copular)
            if role is not None and role not in boxes:
                boxes[role] = self._box_for(word, skeleton, marks, covered, prefix_rows)
                covered.add(word.index)
            elif role is None and word.bare_dep in NOMINAL_DEPS:
                # A nominal the station SAW and could not place: its marker is ambiguous, or it is a
                # possessor its head will take. Recorded either way — `_box_for` marks the tokens it
                # consumes, so a possessor is already covered and only the truly unplaced survives.
                unresolved.append((word, self._box_for(word, skeleton, marks, covered)))

        # A phrase whose ROLE is unknown is not a phrase that was not understood: its head, its
        # determination and its marker are all read. It lands in `unplaced` as the words it covers,
        # because the zip has no box to put it in — and that is the honest report (req 21: material
        # no box fits is RECORDED, never given a position it did not earn).
        for word, box in unresolved:
            if word.index not in covered:
                abstained.append(f"{word.text}: nominal with no role")

        unplaced = tuple(w.text for w in skeleton
                         if w.index not in covered and w.upos not in ("PUNCT", "SYM"))

        row = ContentRow(name="r0", predicate=predicate,
                         predicate_sense=Open() if predicate else None, boxes=boxes)
        rows = [*prefix_rows, row] if prefix_rows else [row]
        return Compiled(zip=Zip(rows=rows, unplaced=list(unplaced)),
                        covered=tuple(sorted(covered)), unplaced=unplaced,
                        abstained=tuple(abstained))

    # -- the pieces -------------------------------------------------------------------------------

    def _read_closed(self, skeleton: Skeleton) -> dict[int, object]:
        return {i: m for i, m in self.table.walk_skeleton(skeleton)}

    def _key(self, word: Word) -> str:
        """A content word's dictionary key — `eat.v`. The sense stays OPEN beside it."""
        letter = POS_LETTER.get(word.upos, "n")
        return keymod.key_of(word.lemma, letter)

    def _role_of(self, word: Word, skeleton: Skeleton, marks: dict,
                 copular: bool = False) -> Role | None:
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
            # **AMBIGUOUS, AND THE PHRASE STILL LANDS.** «I swam IN the pool» reads
            # location|time|instrument|manner and nothing here chooses — but dropping the phrase
            # would lose `pool` entirely, which is worse than admitting the role is unknown. Req 8
            # is explicit: the caught parts stay bound and the rest is OPEN, never a silently
            # complete nearest fit. So the box is built with its marker recorded and no role yet;
            # the head-verb geometry is what will settle it (E3's remaining task).
            return None
        return None

    def _box_for(self, word: Word, skeleton: Skeleton, marks: dict, covered: set[int],
                 prefix_rows: list | None = None) -> Box:
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
            prefix_rows.append(QuantifierRow(name=f"q{len(prefix_rows)}", scopes="r0", binds=name,
                                             quantity=quantity, determination=determination,
                                             restriction=box))
            return Box(head=Var(name=name), sense=Open())
        return box

    def _compile_closed(self, word: Word, match, skeleton: Skeleton, boxes: dict,
                        prefix_rows: list, abstained: list,
                        copular: bool = False) -> set[int]:
        """What a closed-class form does to the zip. Returns the token indices it accounted for."""
        kind = match.kind
        taken = {word.index + n for n in range(match.length)}

        if kind == "prefix":
            element = match.compiled.get("element")
            if element == "negation":
                prefix_rows.append(NegationRow(name=f"n{len(prefix_rows)}", scopes="r0"))
            elif element == "modality":
                from tk2.tkzip.schema import Modality, ModalityRow

                prefix_rows.append(ModalityRow(name=f"m{len(prefix_rows)}", scopes="r0",
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
            # A marker with several readings and nothing to choose between them ABSTAINS. Picking
            # the first candidate would be the silently-complete nearest fit req 8 forbids.
            if not match.settled_role and len(match.roles) > 1:
                abstained.append(f"{match.form}: {'|'.join(match.roles)}")
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


def compile_sentence(skeleton: Skeleton, table: ClosedClasses) -> Compiled:
    """One call, for a caller that holds no compiler."""
    return Compiler(table).compile(skeleton)
