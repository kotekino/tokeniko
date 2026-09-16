"""THE UTTERANCE — context as an argument (req 7), and a quote that arrives as two sentences.

**TWO OF E3 TASK 2b's FOUR SUB-TASKS**, and deliberately not the other two: the rotation itself waits
on the Captain's format ruling about where an ADDRESSEE lives, and nothing here guesses at it.

**WHY `compile()` COULD NOT SIMPLY GROW A PARAMETER.** Requirement 7 says *«the station is pure —
context is an ARGUMENT, never state»*, and it has been written and unbuilt since E3 opened because
nothing needed it. Two things need it now and they are different:

- **a pronoun has to resolve to somebody.** `i` and `you` carry `person: 1` and `person: 2` in their
  closed-class rows already — the axis has had its data all along and no caller to supply the other
  end.
- **a quote arrives as a SECOND SENTENCE.** Measured 2026-09-16: stanza splits «John said to Marie
  " You are a clever girl "» into two skeletons, so the frame and the words it governs never meet.
  `Compiler.compile` takes one skeleton and should keep taking one — an utterance is the larger unit
  and it belongs here.

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


def _frame(zip_) -> object | None:
    """Is this sentence a QUOTE FRAME — «John said to Marie» — and if so, what attitude is it?

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

    for row in zip_.rows:
        if row.kind != "content" or getattr(row, "predicate", None) not in SAYING_VERBS:
            continue
        holder = row.boxes.get(Role.AGENT)
        if holder is None:
            continue
        return AttitudeRow(name=row.name, scopes=row.name, holder=holder,
                           verb=row.predicate, addressee=row.boxes.get(Role.RECIPIENT))
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
    a dependency tree:

        «he says that you swim»        attitude(he, say) scopes r1 · r1 is EMPTY · r0 is CLAIMED
        «John said: "you swim"»        attitude(john, say) scopes s1.… · s1.… is EMPTY

    **THE QUOTE IS NOT CLAIMED AND THAT IS THE WHOLE POINT.** «John said the sky is green» does not
    assert that the sky is green — it asserts that John said so. A quote whose rows stayed CLAIMED
    would put every reported sentence into the KB as a fact, which is the one thing the truth slot
    exists to prevent, and it is the same distinction req 38 rests on.
    """
    from tk2.tkzip.schema import AttitudeRow

    scopes = _claim_of(zip_)
    if scopes is None:
        return zip_
    unasserted = [row.model_copy(update={"truth": None})
                  if row.kind in ("content", "join") else row
                  for row in zip_.rows]
    attitude = AttitudeRow(name=f"{scopes}.pov", scopes=scopes, holder=frame.holder,
                           verb=frame.verb, addressee=frame.addressee)
    return zip_.model_copy(update={"rows": [attitude, *unasserted]})


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

    rows, unplaced, abstained, defaulted, covered, total = [], [], [], [], 0, 0
    quoting = None          # the attitude the PREVIOUS sentence set up, if it set one up
    for position, skeleton in enumerate(skeletons):
        # **A QUOTE ROTATES AGAINST THE SENTENCE THAT INTRODUCED IT.** «John said to Marie" You are
        # a clever girl "» is two skeletons, and the first one is the frame: a saying with an agent
        # and a recipient. So the second compiles under the first's participants, which is req 20's
        # rule applied across a sentence boundary instead of down a dependency tree.
        compiled = compiler.compile(skeleton, context=context if quoting is None
                                    else context.under(quoting))
        frame, quoting = quoting, _frame(compiled.zip)
        zip_ = prefixed(compiled.zip, "" if position == 0 else f"s{position}.")
        if frame is not None:
            # The previous sentence introduced this one, so it is what was SAID rather than a claim
            # of its own.
            zip_ = quoted_under(zip_, frame)
        rows.extend(zip_.rows)
        unplaced.extend(compiled.unplaced)
        abstained.extend(compiled.abstained)
        defaulted.extend(compiled.defaulted)
        covered += len(compiled.covered)
        total += len(compiled.covered) + len(compiled.unplaced)

    return CompiledUtterance(
        zip=Zip(rows=rows, unplaced=list(unplaced)),
        sentences=len(skeletons),
        unplaced=tuple(unplaced), abstained=tuple(abstained), defaulted=tuple(defaulted),
        coverage=1.0 if not total else covered / total,
        split=len(skeletons) > 1,
    )
