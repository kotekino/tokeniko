"""THE UTTERANCE — context as an argument (req 7), and a quote that arrives as two sentences.

**E3 TASK 2b**, complete. The rotation itself lives in `Compiler._contexts`, where the tree says which
clause sits under which attitude; this module is the larger unit — several sentences as one utterance
— and the cross-boundary case of the same rule.

**WHY `compile()` COULD NOT SIMPLY GROW A PARAMETER.** Requirement 7 says *«the station is pure —
context is an ARGUMENT, never state»*, and it has been written and unbuilt since E3 opened because
nothing needed it. Two things need it now and they are different:

- **a pronoun has to resolve to somebody.** `i` and `you` carry `person: 1` and `person: 2` in their
  closed-class rows already — the axis has had its data all along and no caller to supply the other
  end.
- **a quote can arrive as a SECOND SENTENCE.** Measured 2026-09-16 and re-measured 2026-09-17:
  stanza splits «John said to Marie " You are a clever girl "» into two skeletons — but ONLY when the
  marks are spaced away from their words. `"You are a clever girl"` arrives as one skeleton with the
  quote as a `ccomp`, so **the split is the exception and not the rule**, and `Compiler._contexts` is
  where most quotations are actually handled. `Compiler.compile` takes one skeleton and should keep
  taking one — an utterance is the larger unit and it belongs here.

**THE SPEAKER IS WHATEVER THE CALLER SAYS IT IS.** This module never invents an identifier. The drill
hand-compiles «I» as `me.n`; the blueprint says the self-model is carried by named individuals with
uids (E3b). Both are legal here and the station does not choose — it fills the box with the
identifier it was handed, and with `Open()` when it was handed none. **Without a context nothing
changes**, which is what keeps this purely additive.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Iterable, Sequence

from tk2.tkzip.schema import Box, ContentRow, Ref, Var, Zip


def _is_open(value) -> bool:
    """An OPEN or absent filler is not somebody — it must not become the speaker of anything."""
    return value is None or value.__class__.__name__ == "Open"


@dataclass(frozen=True, slots=True)
class Context:
    """What the caller knows that the sentence does not. **Passed in, never held.**

    `speaker` and `addressee` are the SPEECH ACT's two participants, and they are identifiers the
    caller owns — a dictionary key, a uid, anything the layer above uses for a person. The station
    copies one into a box and never mints one.

    `recent` is for anaphora and ellipsis (req 7's other two), which are not built: it is declared so
    that the argument does not have to change shape the day they are, and so a caller can already
    pass what it holds.
    """

    speaker: object | None = None
    addressee: object | None = None
    recent: tuple[Zip, ...] = ()

    def under(self, attitude) -> "Context":
        """**THE ROTATION** — this context as it stands INSIDE an attitude (req 20).

        A first-person pronoun names the HOLDER of the innermost point of view it is under, and a
        second-person one names that POV's ADDRESSEE. «John said to Marie: YOU are a clever girl»
        means Marie because the saying was addressed to her.

        **AN ATTITUDE WITHOUT AN ADDRESSEE ROTATES ONLY THE FIRST PERSON, AND THAT IS THE POINT.**
        «John thinks I am wrong» still means the speaker: thinking addresses nobody, so there is no
        second-person slot to rotate into, and the outer addressee survives. The `addressee` field
        being EMPTY rather than `Open()` is what carries that distinction — schema v3 was ruled for
        exactly this.

        `recent` is carried through unchanged: anaphora points into the discourse, and the discourse
        does not restart inside a quotation.
        """
        holder = getattr(attitude, "holder", None)
        addressee = getattr(attitude, "addressee", None)
        speaker = getattr(holder, "head", None) if holder is not None else None
        return replace(
            self,
            speaker=speaker if speaker is not None and not _is_open(speaker) else self.speaker,
            addressee=(getattr(addressee, "head", None)
                       if addressee is not None and not _is_open(getattr(addressee, "head", None))
                       else self.addressee),
        )

    #: The two persons this context can answer for, as the closed-class rows spell them.
    def for_person(self, person: object) -> object | None:
        """Who a pronoun of this grammatical person names here, or None if this context cannot say.

        **First and second only, and third is not an oversight.** «he» and «they» are ANAPHORA — they
        point at something earlier in the discourse, not at a participant in the speech act — so they
        resolve against `recent` when that is built, and never against the speaker.
        """
        if person == 1:
            return self.speaker
        if person == 2:
            return self.addressee
        return None

    @property
    def is_empty(self) -> bool:
        return self.speaker is None and self.addressee is None and not self.recent


#: The one shared context that says nothing — so a caller that has none passes a real object rather
#: than a `None` every function has to test for.
NO_CONTEXT = Context()


# ------------------------------------------------------------------------------------------------
# merging sentences into one utterance
# ------------------------------------------------------------------------------------------------


def _rename(value, prefix: str, rows: set[str], vars_: set[str]):
    """One field, with every NAME in it prefixed. Row names and variable names are two namespaces
    and both must move, or the second sentence's `x0` binds the first sentence's variable."""
    if isinstance(value, Var):
        return Var(name=f"{prefix}{value.name}") if value.name in vars_ else value
    if isinstance(value, Ref):
        return Ref(row=f"{prefix}{value.row}") if value.row in rows else value
    if isinstance(value, Box):
        return value.model_copy(update={
            "head": _rename(value.head, prefix, rows, vars_),
            "relation": _rename(value.relation, prefix, rows, vars_),
        })
    if isinstance(value, str):
        return f"{prefix}{value}" if value in rows else value
    return value


def prefixed(zip_: Zip, prefix: str) -> Zip:
    """A zip whose every row name, variable name and reference carries `prefix`.

    **The reference sites are enumerable and that is why this is safe**: `scopes` on a prefix row,
    `operands` on a join, `binds` and `restriction` on a binder, and a box's `head` or `relation`
    when it holds a `Var` or a `Ref`. A name that is not one of this zip's own is left alone — so a
    key like `cat.n` is never mangled, which is what `rows` and `vars_` are checked against.
    """
    if not prefix:
        return zip_
    rows = {row.name for row in zip_.rows}
    vars_ = {row.binds for row in zip_.rows if getattr(row, "binds", None)}

    moved = []
    for row in zip_.rows:
        update = {"name": f"{prefix}{row.name}"}
        if getattr(row, "scopes", None):
            update["scopes"] = _rename(row.scopes, prefix, rows, vars_)
        if getattr(row, "operands", None):
            update["operands"] = [_rename(o, prefix, rows, vars_) for o in row.operands]
        if getattr(row, "binds", None):
            update["binds"] = f"{prefix}{row.binds}"
        if getattr(row, "restriction", None):
            update["restriction"] = _rename(row.restriction, prefix, rows, vars_)
        if getattr(row, "boxes", None):
            update["boxes"] = {role: _rename(box, prefix, rows, vars_)
                               for role, box in row.boxes.items()}
        # An attitude's holder and addressee, and a domain, are boxes too — «Nobody said…» binds
        # the variable its holder is, and a binder renamed without its holder unbinds it.
        for slot in ("holder", "addressee", "domain"):
            if getattr(row, slot, None) is not None:
                update[slot] = _rename(getattr(row, slot), prefix, rows, vars_)
        if getattr(row, "pov", None) is not None:
            update["pov"] = row.pov.model_copy(update={
                "holder": _rename(row.pov.holder, prefix, rows, vars_)})
        moved.append(row.model_copy(update=update))
    return zip_.model_copy(update={"rows": moved})


#: Attitude verbs that ADDRESS somebody, and therefore rotate the second person. It is a
#: placeholder and it is named as one: «which verbs are attitude verbs» is req 55's nearest-anchor
#: geometry over a small anchor set — *«attitude verbs are open, so the classification never misses
#: the verb nobody thought of»* — and E4 owns that. **ON THE FRAME/KNOWLEDGE AUDIT LIST**: it is a
#: closed set of verbs in code, which is the exact shape the Captain's rule of 2026-09-16 refuses,
#: and it is here only until the geometry that replaces it exists.
SAYING_VERBS = frozenset({"say.v", "tell.v", "ask.v", "reply.v", "answer.v", "write.v", "shout.v",
                          "whisper.v", "call.v"})


def _frame(rows: Iterable, held: Iterable[str] = ()) -> object | None:
    """Is this sentence a QUOTE FRAME — «John said to Marie» — and if so, what attitude is it?
    `rows` are a zip's rows, or the rows its compile withheld (`Compiled.withheld`); `held` names
    the rows whose clause took a complement in its own sentence (`Compiled.complemented`).

    **A SAYING THAT HELD ITS OWN COMPLEMENT FRAMES NOTHING AFTER IT** *(2026-09-27,
    `E3.3.11.2.23`)*. «Nobody said to Marie that he sleeps. It rains.» — the saying said what it
    said, in its own sentence, and was withheld there (ruling 8); read as a frame all the same, it
    took «It rains» down with it as a quotation it never introduced. What a frame IS is a saying
    whose content is still to come, and whether the content came is the tree's (`ccomp` · `xcomp`),
    so the compiler reports it and this reads it — never the verb's name.

    Returns something shaped like an `AttitudeRow` (a holder and an addressee) so that
    `Context.under` can read it without caring whether the attitude came from a dependency tree or
    from the sentence next door.

    **BEING A FRAME AND ROTATING ARE TWO DIFFERENT THINGS**, and the first draft conflated them by
    requiring a recipient for both. «I asked: "Do you know the muffin man?"» is a frame — the
    question is the content of the asking and must not be claimed — and it addresses nobody NAMED,
    so the `you` inside it stays whoever the outer utterance was addressed to. Which is correct:
    «I asked: do YOU know» is asking the listener.

    So a frame needs only a HOLDER; the addressee rides along when there is one and is `None` when
    there is not, and `Context.under` already keeps the outer addressee in that case.
    """
    from tk2.tkzip.schema import AttitudeRow, Role

    held = set(held)
    for row in rows:
        if row.name in held:
            continue
        # A predicate may be an OPEN — «WHY do you think…?» raises a row whose predicate is asked —
        # and an OPEN is no key, and not hashable either: the membership test crashed the utterance.
        predicate = getattr(row, "predicate", None)
        if row.kind != "content" or not isinstance(predicate, str) or predicate not in SAYING_VERBS:
            continue
        holder = row.boxes.get(Role.AGENT)
        if holder is None:
            continue
        return AttitudeRow(name=row.name, scopes=row.name, holder=holder,
                           verb=row.predicate, addressee=row.boxes.get(Role.RECIPIENT),
                           theatre=row.theatre)
    return None


def _keeps_its_place(rows: list, frame) -> str | None:
    """Why the FRAME row cannot hand its place to the attitude over the quote — None when it can.

    «John did not say to Marie. "You are late."» — the frame row kept its «not», and the attitude
    raised over the quote beside it claimed that he DID say it: the double claim `E3.3.11.2` was,
    one sentence later (`E3.3.11.2.12`). So the frame dissolves into the attitude exactly as a
    matrix does within a sentence — its prefix moving over the quote before the attitude — and
    where it cannot, the quote is withheld.

    **BY THE SAME RULE, NOT A COPY OF IT** — `compile.matrix_keeps_its_place`, which
    `Compiler._places` reads too. A copy had drifted within the day it was written: it had no
    restriction test, so «The man who said to Marie left. "You are late."» — `_frame` taking the
    relative clause's saying for the frame — dissolved the man's restriction in silence and left
    the attitude's holder outside its binder. What only this side has is the join: a quote cannot
    take its frame's place in a join the frame's sentence built.

    **AND WHAT FOLLOWS A «CANNOT» IS THE COMPILER'S JUDGEMENT TOO** *(2026-09-27)*: the quote is
    withheld, and the frame's sentence goes back to the compiler with the frame named in
    `quotation_withheld`, where `_unentailed` judges it as it judges a matrix that lost its
    complement (`compile_utterance`).
    """
    from tk2.language.compile import IMPERATIVE_VERB, matrix_keeps_its_place
    from tk2.tkzip.schema import QuantifierRow

    row = next((r for r in rows if r.name == frame.name), None)
    if row is None:
        return "the frame is not a row of the zip"
    # The box `_frame` read the holder from — whichever it was — is the one the attitude speaks for.
    holder = next((role for role, box in row.boxes.items() if box == frame.holder), None)
    binders = {r.binds: r for r in rows if isinstance(r, QuantifierRow)}
    parent = {operand: r for r in rows for operand in (getattr(r, "operands", None) or ())}
    above, current = {row.name}, row.name
    for _ in range(len(parent) + 1):
        join = parent.get(current)
        if join is None or join.name in above:
            break
        above.add(join.name)
        current = join.name
    # An unasserted frame under the speech act's want is wanted, not supposed (tkzip req 48).
    wanted = any(getattr(r, "scopes", None) == row.name and r.kind == "attitude"
                 and r.verb == IMPERATIVE_VERB for r in rows)
    why = matrix_keeps_its_place(row, holder, frame.verb, binders, above, wanted,
                                 "the frame's holder is no box of its row")
    if why is not None:
        return why
    if row.name in parent:
        return "the frame is joined to another clause, and the quote cannot take its place there"
    return None


def _claim_of(zip_) -> str | None:
    """Which row carries a zip's CLAIM — what an attitude must scope to cover the whole of it.

    The outermost JOIN where there is one, because a join covers its operands and everything under
    them; otherwise the first clause row. «You are a clever girl» is two content rows and an AND, and
    an attitude scoping only the copular row would leave «clever» asserted outside the quotation.
    """
    joins = [row.name for row in zip_.rows if row.kind == "join"]
    if joins:
        return joins[-1]
    clauses = [row.name for row in zip_.rows if row.kind == "content"]
    return clauses[0] if clauses else None


def quoted_under(zip_, frame):
    """A quoted sentence's zip, placed UNDER the attitude that introduced it.

    **THE SAME SHAPE `ccomp` ALREADY PRODUCES**, arriving across a sentence boundary instead of down
    a dependency tree — and since 2026-09-26 (`E3.3.11.2.16`) with the frame gone in both, the
    attitude having taken the saying's place (`compile_utterance`, `_keeps_its_place`):

        «he says that you swim»        attitude(he, say) scopes r1 · r1 keeps its truth · no r0
        «John said: "you swim"»        attitude(john, say) scopes s1.… · s1.… keeps its truth

    **THE QUOTE IS NOT CLAIMED OF THE WORLD, AND THE ATTITUDE IS WHAT SAYS SO.** «John said the sky
    is green» does not assert that the sky is green — it asserts that John said so — and the prefix
    row above is what carries that, exactly as it does for «he thinks a cat is in the garden», where
    the drill has always kept the cat at truth 1.0 and asserted no cat.

    **THE ROWS THEREFORE KEEP THEIR TRUTH** *(changed 2026-09-17 on the Captain's ruling)*. Blanking
    it here was belt-and-braces that cost a distinction: under a saying verb the truth slot records
    what the HOLDER did — asserted it, asked it, wanted it — and three speech acts were collapsing
    into one shape. See `Compiler._attitude`, which this mirrors across a sentence boundary.
    """
    from tk2.tkzip.schema import AttitudeRow

    scopes = _claim_of(zip_)
    if scopes is None:
        return zip_
    attitude = AttitudeRow(name=f"{scopes}.pov", scopes=scopes, holder=frame.holder,
                           verb=frame.verb, addressee=frame.addressee, theatre=frame.theatre)
    return zip_.model_copy(update={"rows": [attitude, *zip_.rows]})


@dataclass
class CompiledUtterance:
    """Every sentence of one utterance, in one zip — plus what each sentence cost.

    **The sentences are NOT related to one another**, and that is the honest state rather than a
    shortcut. «John said to Marie "You are a clever girl"» needs the quote to become the content of
    the saying, and what that looks like is E3 task 2b.3 — the Captain's format ruling on where an
    addressee lives. Merging them into one zip is what makes that ruling BUILDABLE: until now the
    second half was simply dropped.
    """

    zip: Zip
    sentences: int = 1
    unplaced: tuple[str, ...] = ()
    abstained: tuple[str, ...] = ()
    defaulted: tuple[str, ...] = ()
    coverage: float = 1.0
    #: True when the provider split the input — the caller is entitled to know that the rows in this
    #: zip came from more than one sentence and are not yet joined.
    split: bool = False


@dataclass
class _Sentence:
    """One sentence of an utterance, as `compile_utterance` holds it until the utterance is whole.

    **HELD WHOLE, NOT FOLDED AS IT ARRIVES**, because a later sentence can send an earlier one back
    to the compiler: a frame whose quotation cannot stand under it is judged by the compiler's own
    rule, and that judgement is a second compile of the frame's sentence (`quotation_withheld`).
    """

    skeleton: object
    context: Context
    prefix: str
    compiled: object = None
    zip: Zip | None = None
    #: The attitude this sentence frames the NEXT one with (`_frame`), and whether that frame was
    #: withheld by the sentence's own compile — a withheld frame places nothing under it.
    frame: object | None = None
    frame_withheld: bool = False
    #: This sentence is the quotation the previous one frames, and stands under that frame.
    placed: bool = False
    #: This sentence is withheld whole — a quotation with nowhere to stand. Its words are unplaced.
    withheld: bool = False
    #: This sentence is the QUOTATION of the frame before it — placed under that frame, or withheld
    #: with it, and never a claim at the top level. Its compile is told so (`Compiler.compile`'s
    #: `quoted`), so a cut from it is judged as a cut under an attitude (`E3.3.11.2.22`).
    quoted: bool = False
    #: What the utterance recorded while judging this sentence, said before its compile's own.
    notes: list = field(default_factory=list)

    def compile(self, compiler, quotation_withheld: Iterable[str] = ()) -> None:
        # Named only when there is something to judge: a first compile of a sentence that is no
        # quotation is the call it always was.
        judge = {"quotation_withheld": frozenset(quotation_withheld)} if quotation_withheld else {}
        if self.quoted:
            judge["quoted"] = True
        self.compiled = compiler.compile(self.skeleton, context=self.context, **judge)
        self.zip = prefixed(self.compiled.zip, self.prefix)
        held = self.compiled.complemented
        self.frame = _frame(self.zip.rows, {f"{self.prefix}{name}" for name in held})
        self.frame_withheld = False
        if self.frame is None:
            # A frame the sentence's own compile withheld still frames the next sentence — and that
            # quotation falls with it, as a complement falls with its matrix (`Compiler._attitude`).
            lost = _frame(self.compiled.withheld, held)
            if lost is not None:
                self.frame = lost.model_copy(update={"name": f"{self.prefix}{lost.name}"})
                self.frame_withheld = True

    @property
    def claims_nothing(self) -> bool:
        """Everything in it was withheld — the one empty row a zip of nothing is (`compile`)."""
        empty = ContentRow(name="r0").model_dump(exclude={"name"})
        return all(row.kind == "content" and row.model_dump(exclude={"name"}) == empty
                   for row in self.zip.rows)

    def words(self) -> list[str]:
        return [w.text for w in self.skeleton if w.upos not in ("PUNCT", "SYM")]


def _fold(sentences: list[_Sentence]) -> list:
    """The utterance's rows, from its sentences as they now stand.

    A quotation placed under its frame takes the frame's place (`_keeps_its_place`): the frame row
    goes, what stood over it moves over the quotation before the attitude, and the attitude scopes
    the quotation's claim (`quoted_under`). A withheld sentence contributes nothing.
    """
    rows: list = []
    for at, sentence in enumerate(sentences):
        if sentence.withheld:
            continue
        zip_ = sentence.zip
        if sentence.placed:
            frame = sentences[at - 1].frame
            over = [r for r in rows if getattr(r, "scopes", None) == frame.name]
            rows = [r for r in rows if r.name != frame.name and r not in over]
            zip_ = quoted_under(zip_, frame)
            scopes = zip_.rows[0].scopes
            moved = [r.model_copy(update={"scopes": scopes}) for r in over]
            zip_ = zip_.model_copy(update={"rows": [*moved, *zip_.rows]})
        rows.extend(zip_.rows)
    return rows


def _withhold_quotation(compiler, sentences: list[_Sentence], at: int, why: str) -> None:
    """Sentence `at` is the quotation of the frame before it, and it cannot stand there.

    **THE SAME RULE AS INSIDE A SENTENCE, NOT A COPY OF IT** (`E3.3.11.2.12`, the Captain's
    `E3.3.11.2.16`): a complement that cannot stand under its attitude is withheld, and the matrix
    it was cut from is judged on its own — kept where the cut only weakens it (a claimed saying,
    `E3.12.5.1`), withheld where it widens the claim (under a negation, in an antecedent) or moves a
    definite description. That judgement is `Compiler._unentailed`'s, so the frame's sentence is
    compiled again with its frame named in `quotation_withheld` — never re-judged here. The copy
    this replaces had drifted within a day: it withheld the whole framing sentence whenever anything
    scoped or joined the frame (a ◇ over it, an AND beside it — both weakened by the cut, both
    entailed), and kept a frame that restricted a DEFINITE description, which the compiler withholds.

    And recursively: when that second compile leaves nothing of a sentence that was itself a
    quotation, ITS frame has lost its quotation in turn. **Such a sentence is compiled `quoted`
    both times** *(2026-09-27, `E3.3.11.2.22`)*, so its frame is judged where it stands — under the
    attitude one sentence further back, where a cut widens the claim. Judged at the top level, «Anna
    said to Bob. "John said to Marie yesterday." "You sleep."» kept John's cut saying and placed it
    under Anna's: a claim the same words in one sentence never make.
    """
    quotation, framing = sentences[at], sentences[at - 1]
    quotation.withheld = True
    quotation.notes.append(f"{framing.frame.name}: {why} — the quotation it frames is withheld")
    if framing.frame_withheld or framing.withheld:
        return
    local = framing.frame.name[len(framing.prefix):]
    framing.compile(compiler, quotation_withheld={local})
    if framing.placed and framing.claims_nothing and at - 1 > 0:
        _withhold_quotation(compiler, sentences, at - 1,
                            "nothing of its quotation could be placed")


def compile_utterance(compiler, skeletons: Sequence, context: Context = NO_CONTEXT
                      ) -> CompiledUtterance:
    """Every skeleton of one utterance → one zip.

    The first sentence keeps its names so a single-sentence utterance is byte-identical to what
    `Compiler.compile` produces alone — which is what lets this be added without moving a single
    existing measurement.
    """
    if not skeletons:
        # **AN EMPTY ZIP IS NOT A ZIP** — the schema requires at least one row, and it is right to:
        # a zip is a claim about something, and «nothing» is not something. So an utterance with no
        # sentences produces the same shape the compiler already produces for a skeleton with no
        # root — one empty content row, saying «I received this and made nothing of it» — rather
        # than a second convention for the same state.
        return CompiledUtterance(zip=Zip(rows=[ContentRow(name="r0")]), sentences=0, coverage=1.0)

    sentences: list[_Sentence] = []
    for position, skeleton in enumerate(skeletons):
        # **A QUOTE ROTATES AGAINST THE SENTENCE THAT INTRODUCED IT.** «John said to Marie" You are
        # a clever girl "» is two skeletons, and the first one is the frame: a saying with an agent
        # and a recipient. So the second compiles under the first's participants, which is req 20's
        # rule applied across a sentence boundary instead of down a dependency tree.
        previous = sentences[-1] if sentences else None
        frame = previous.frame if previous is not None else None
        sentence = _Sentence(skeleton, context if frame is None else context.under(frame),
                             "" if position == 0 else f"s{position}.", quoted=frame is not None)
        sentence.compile(compiler)
        sentences.append(sentence)
        if frame is None:
            continue
        # The previous sentence introduced this one, so it is what was SAID rather than a claim of
        # its own — and the frame hands the quote its place, or the quote cannot stand.
        if previous.frame_withheld or previous.withheld:
            # **A QUOTATION FALLS WITH ITS FRAME** — «Anna did not tell Bob. "You sleep."»: the
            # telling was withheld by its own sentence (`E3.12.5`), and the quotation left behind
            # stood CLAIMED at top level — the speaker telling the listener he sleeps.
            _withhold_quotation(compiler, sentences, position, "the frame itself was withheld")
        elif sentence.claims_nothing:
            # Withheld whole by its own compile: the frame lost what it held, and is judged so.
            _withhold_quotation(compiler, sentences, position,
                                "nothing of its quotation could be placed")
        else:
            why = _keeps_its_place(_fold(sentences[:-1]), frame)
            if why is None:
                sentence.placed = True
            else:
                # **WITHHELD, AND SAID WHY** (`E3.3.11.2.16` (2)): an asked or a supposed frame, a
                # frame with boxes of its own, a frame that restricts a phrase — the attitude row
                # has no place for the quote under it.
                _withhold_quotation(compiler, sentences, position, why)

    unplaced: list[str] = []
    defaulted: list[str] = []
    notes: list[str] = []
    covered = total = 0
    for sentence in sentences:
        compiled = sentence.compiled
        words = sentence.words() if sentence.withheld else list(compiled.unplaced)
        placed = 0 if sentence.withheld else len(compiled.covered)
        unplaced.extend(words)
        notes.extend([*sentence.notes, *compiled.abstained])
        defaulted.extend(compiled.defaulted)
        covered += placed
        total += placed + len(words)

    rows = _fold(sentences)
    if not rows:
        rows = [ContentRow(name="r0")]
    # **THE FIRST SENTENCE'S VOICE IS THE UTTERANCE'S.** `topicality` is one field on the zip rather
    # than one per row, so a merge has to choose, and the first sentence is the one the utterance is
    # about. *The THEATRE needed no such choice after schema v5: it rides on the rows, so every
    # clause of every sentence keeps its own time.*
    topicality = next((s.compiled.zip.topicality for s in sentences
                       if s.compiled.zip.topicality is not None), None)
    return CompiledUtterance(
        zip=Zip(rows=rows, unplaced=list(unplaced), topicality=topicality),
        sentences=len(skeletons),
        unplaced=tuple(unplaced), abstained=tuple(notes), defaulted=tuple(defaulted),
        coverage=1.0 if not total else covered / total,
        split=len(skeletons) > 1,
    )
