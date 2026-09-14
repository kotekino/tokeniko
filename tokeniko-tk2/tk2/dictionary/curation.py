"""DEFINITIONAL CURATION — the edges a definition states outright, and the hand that admits them.

The Captain's ruling of 2026-08-12 (requirement 20): a manual edge may enter R only when it is
ANALYTIC — *stated in a definition* — never when it is contingent. Sayings, slang and context-bound
readings are knowledge, and knowledge lives in the KB (requirement 5: consequence is learned, not
looked up). What a dictionary asserts outright is a different thing, and that is what is mined here.

AND DEFINITIONS ARE CROSS-REFERENCED. `sleep`'s gloss is «be asleep» and never mentions a bed;
`bed`'s gloss is «a piece of furniture that provides a place to sleep» and names sleeping outright.
So both sides are read and the edge is minted from whichever definition actually speaks — DIRECTED,
`bed.n -> sleep.v`, because that is the direction the statement runs in.

THE GATE IS THE POINT AND IT IS CODE, not a comment. `propose` and `apply` are instruments: they
mine, they simulate, they change nothing. `assert_captains_hand` is what stands between a proposal
and R, and it is a function rather than a CLI flag so that it can be TESTED — a script able to mint
its own curated cell would have quietly taken over exactly the judgement the ruling reserves.
Analytic or contingent is the call a miner cannot make.

ONE FUNCTION BUILDS THE CELLS, and both simulate and approve call it (`cells_of`). The prototype's
own lesson: a simulation that measured a different edge shape than approval would write is worse
than no simulation at all.

THE RECIPROCAL, measured before it was ruled: a curated edge written one way only moves
`sleep.v~bed.n` to 0.217 and `eat.v~hungry.a` to 0.193 — both under the 0.30 NEAR floor, so the
stated-relation read passes while the cosine read still misses. A weaker back-reference at 0.60
carries them to 0.353 and 0.329 and closes both. The value is not invented: it is the convention R
already uses for the edges it mines (`entails` 0.80 / `entailed_by` 0.60), so a curated edge is
shaped like the edges it sits beside. It is a ROW since policy v3 (`RelationPolicy.reciprocal_weight`).

Pure. The resource arrives as a provider, the vocabulary and the weights arrive as policy, and what
comes out is proposals and an in-memory matrix — never a write.
"""

from dataclasses import dataclass, replace
from typing import Iterable, Protocol, runtime_checkable

from tk2.dictionary import glosses, keys
from tk2.dictionary.config import RelationPolicy, SenseMode
from tk2.dictionary.matrix import SOURCE_CURATED, Cell, Matrix, Provenance

#: The reverse cell is TAGGED rather than renamed. Inventing an English inverse for each curated
#: relation (`involved_in`? `site_for`?) would double the closed vocabulary without making a second
#: claim — the relation is ONE relation, stored asymmetrically. Derived mechanically so it cannot
#: drift, and it keeps the reverse cell from reading as the forward one: `sleep.v -> bed.n` prints
#: `used_for_reciprocal`, never `used_for`, which would say sleep is used for a bed.
RECIPROCAL_SUFFIX = "_reciprocal"

#: The weakest curated claim, and the one the miner falls back to: «the definition names it», which
#: is the one thing it actually observed. Named because the fallback table in the rows may not cover
#: every POS pair and a miner with nothing to say must still say something honest.
INVOLVES = "involves"


class NotTheCaptainsHand(PermissionError):
    """An approval that no one authorized.

    Requirement 20 makes a curated edge a HUMAN judgement. This is the mechanism that ruling needs
    to stay true, so it raises rather than warning: a run that could continue past it would be a run
    in which the gate was decoration.
    """


class CurationRefused(ValueError):
    """A proposal that may not become a cell — an unknown relation, or a key that is not a
    dimension. Refused rather than skipped: a curated edge nobody can write to is a membership
    finding (requirement 15), and silence would file it as a success."""


@runtime_checkable
class DefinitionProvider(Protocol):
    """A `GlossProvider` that can also be asked about ONE SENSE — which curation needs and mining
    does not: an edge's evidence is a particular definition, quoted verbatim, and «the word's gloss»
    (every sense joined) could not be quoted as anything."""

    def senses_of_key(self, key: str) -> tuple[str, ...]:
        ...

    def definition_of_sense(self, sense: str) -> str:
        ...


# ------------------------------------------------------------------------------------------------
# what a proposal is
# ------------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Proposal:
    """One directed analytic edge, pending. The Captain approves BY EYE, from these."""

    source_key: str
    target_key: str
    #: The curated relation the miner GUESSES the gloss is stating. A guess, and relabelled freely:
    #: `relabelled` records that a hand moved it, so an approved edge can say whether the machine or
    #: the reader chose its name.
    relation: str
    weight: float
    #: The sense whose definition speaks, and the definition itself, VERBATIM.
    sense: str
    definition: str
    #: The surface token that named the target — what makes the evidence quotable.
    naming_token: str
    relabelled: bool = False

    @property
    def id(self) -> str:
        """Readable and stable: the same edge proposed twice is the same id, so a re-run replaces a
        pending proposal instead of accumulating duplicates, and the Captain approves by reading the
        table rather than by copying an identifier nobody can pronounce."""
        return f"{self.source_key}>{self.target_key}"

    @property
    def evidence(self) -> str:
        """The gloss as the resource wrote it, with the naming word marked. Verbatim on purpose — a
        paraphrase is the curator arguing rather than the dictionary speaking."""
        return f"{self.sense} {quote(self.definition, self.naming_token)}"

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "source_key": self.source_key,
            "target_key": self.target_key,
            "relation": self.relation,
            "weight": self.weight,
            "sense": self.sense,
            "definition": self.definition,
            "naming_token": self.naming_token,
            "relabelled": self.relabelled,
            "evidence": self.evidence,
        }

    @classmethod
    def from_dict(cls, stored) -> "Proposal":
        return cls(
            source_key=stored["source_key"],
            target_key=stored["target_key"],
            relation=stored["relation"],
            weight=stored["weight"],
            sense=stored["sense"],
            definition=stored["definition"],
            naming_token=stored["naming_token"],
            relabelled=stored.get("relabelled", False),
        )


def quote(definition: str, token: str) -> str:
    """The definition, with the first occurrence of the naming token marked for the eye."""
    out, marked = [], False
    for word in definition.split():
        bare = word.strip(".,;:()").lower()
        if not marked and bare == token.lower():
            out.append(word.replace(bare, f"<{bare}>") if bare in word else f"<{word}>")
            marked = True
        else:
            out.append(word)
    return "«" + " ".join(out) + "»"


# ------------------------------------------------------------------------------------------------
# the miner
# ------------------------------------------------------------------------------------------------


def guess_relation(source_key: str, target_key: str, definition: str, policy: RelationPolicy) -> str:
    """Which of the curated relations this gloss looks like it is stating.

    A GUESS, and the order of the attempts is the rows': cue words first, in declared order, so a
    gloss that is both purposive and locative («provides a place to sleep») reads as purpose — which
    is how the Captain himself quoted it («a piece of furniture ... for sleeping»). Then the POS
    pair. Then `involves`, which claims only what the miner observed.
    """
    padded = f" {definition.lower()} "
    for relation, cues in policy.cues:
        if any(f" {cue} " in padded for cue in cues):
            return relation
    source_pos = keys.pos_of(source_key)
    target_pos = keys.pos_of(target_key)
    for declared_source, declared_target, relation in policy.defaults:
        if (declared_source, declared_target) == (source_pos, target_pos):
            return relation
    if INVOLVES not in dict(policy.curated):
        raise CurationRefused(
            f"no cue fired, no default covers {source_pos}->{target_pos}, and the curated "
            f"vocabulary has no {INVOLVES!r} to fall back on. The fallback is the claim «the "
            f"definition names it» — the one thing the miner actually observed — so a vocabulary "
            f"without it can describe an edge it cannot name."
        )
    return INVOLVES


def propose_directed(
    source_key: str,
    target_key: str,
    provider: DefinitionProvider,
    policy: RelationPolicy,
    senses: SenseMode = "primary",
) -> Proposal | None:
    """Does SOURCE's definition name TARGET? Then that is a directed analytic edge source -> target.

    A definition naming its own headword under a different part of speech is SELF-REFERENCE, not a
    stated relation between two concepts — «land: the land on which real estate is located» would
    mint `land.n -> land.v` out of a tautology, which is precisely the over-merge requirement 16
    already measured. It is refused here rather than configurable, because the reduction refuses it
    too (`glosses.definition_in_lexicon`) and one law with two settings is two laws.
    """
    source_word = keys.word_of(source_key)
    target_word = keys.word_of(target_key)
    if source_word == target_word:
        return None
    for sense in _senses(provider, source_key, senses):
        definition = provider.definition_of_sense(sense)
        token = glosses.names_word(definition, target_word, provider)
        if not token:
            continue
        relation = guess_relation(source_key, target_key, definition, policy)
        return Proposal(
            source_key=source_key,
            target_key=target_key,
            relation=relation,
            weight=policy.curated_weight(relation),
            sense=sense,
            definition=definition,
            naming_token=token,
        )
    return None


def propose_pair(
    a: str,
    b: str,
    provider: DefinitionProvider,
    policy: RelationPolicy,
    senses: SenseMode = "primary",
) -> list[Proposal]:
    """Both directions. Cross-reference means neither side is privileged: whichever gloss speaks,
    speaks — and when both do, both edges are proposed, each with its own evidence."""
    found = (
        propose_directed(a, b, provider, policy, senses),
        propose_directed(b, a, provider, policy, senses),
    )
    return [proposal for proposal in found if proposal is not None]


def self_reference_skips(
    pairs,
    provider: DefinitionProvider,
    senses: SenseMode = "primary",
) -> list[tuple[str, str, str]]:
    """The skips, surfaced rather than silent: a same-word pair whose gloss DOES name its own
    headword would have produced an edge, and the reader is entitled to know the miner stayed its
    hand and why."""
    out: list[tuple[str, str, str]] = []
    for a, b in pairs:
        if keys.word_of(a) != keys.word_of(b):
            continue
        for source, target in ((a, b), (b, a)):
            for sense in _senses(provider, source, senses):
                definition = provider.definition_of_sense(sense)
                token = glosses.names_word(definition, keys.word_of(target), provider)
                if token:
                    out.append((source, target, f"{sense} {quote(definition, token)}"))
                    break
    return out


def relabel(proposal: Proposal, relation: str, policy: RelationPolicy) -> Proposal:
    """The Captain's hand on the NAME of an edge he accepts. The weight follows the relation — a
    relabelled edge that kept the old weight would be an edge nobody declared."""
    return replace(
        proposal,
        relation=relation,
        weight=policy.curated_weight(relation),
        relabelled=True,
    )


def _senses(provider: DefinitionProvider, key: str, senses: SenseMode) -> tuple[str, ...]:
    """Which senses of a dimension may speak. `primary` is the first — the mode the base's
    definitions were mined under, and curation is about definitions."""
    found = tuple(provider.senses_of_key(key))
    return found[:1] if senses == "primary" and found else found


# ------------------------------------------------------------------------------------------------
# the cells a proposal writes
# ------------------------------------------------------------------------------------------------


def cells_of(proposal: Proposal, policy: RelationPolicy) -> list[tuple[str, Cell]]:
    """The TWO cells one curated edge writes: `(row key, cell)` forward, then the reciprocal.

    ONE function, called by simulate and by approve, so a simulation can never be measuring a
    different edge shape than the one approval would write.
    """
    if proposal.relation not in dict(policy.curated):
        raise CurationRefused(
            f"{proposal.id}: {proposal.relation!r} is not one of the curated relations "
            f"{[name for name, _weight in policy.curated]}. The vocabulary is closed on purpose — a "
            f"curator who may invent a relation name per edge is writing prose, not a matrix."
        )
    forward = Cell(
        column=proposal.target_key,
        weight=proposal.weight,
        relation=proposal.relation,
        source=SOURCE_CURATED,
        via=(Provenance(proposal.relation, proposal.weight),),
        evidence=proposal.evidence,
    )
    cells = [(proposal.source_key, forward)]
    if policy.reciprocal_weight:
        reverse_relation = proposal.relation + RECIPROCAL_SUFFIX
        cells.append(
            (
                proposal.target_key,
                Cell(
                    column=proposal.source_key,
                    weight=policy.reciprocal_weight,
                    relation=reverse_relation,
                    source=SOURCE_CURATED,
                    via=(Provenance(reverse_relation, policy.reciprocal_weight),),
                    evidence=proposal.evidence,
                ),
            )
        )
    return cells


@dataclass(frozen=True, slots=True)
class Applied:
    """What applying a set of proposals did — the matrix, and everything worth saying out loud."""

    matrix: Matrix
    written: tuple[tuple[str, Cell], ...] = ()
    #: A curated cell landing where the resource had already spoken. Never silent: an overwrite is
    #: a hand disagreeing with WordNet, which is a thing the Captain may want to do and never a
    #: thing he should discover afterwards.
    overwrites: tuple[str, ...] = ()
    #: Proposals that name a key the base has no axis for (requirement 15).
    unwritable: tuple[str, ...] = ()


def apply(matrix: Matrix, proposals: Iterable[Proposal], policy: RelationPolicy) -> Applied:
    """Apply proposals to a COPY of the matrix. Nothing on disk is touched by anything in here."""
    proposals = list(proposals)
    space = set(matrix.keys)
    cells_by_row: dict[str, list[Cell]] = {}
    written: list[tuple[str, Cell]] = []
    unwritable: list[str] = []
    overwrites: list[str] = []

    for proposal in proposals:
        if proposal.source_key not in space or proposal.target_key not in space:
            unwritable.append(proposal.id)
            continue
        for row_key, cell in cells_of(proposal, policy):
            # Read against what the batch has ALREADY written, not only against the matrix it
            # started from. Both directions of one pair are normally proposed together, and the
            # second one's reciprocal lands on the first one's forward cell — a curated edge
            # overwriting a curated edge, which the reader has at least as much right to know about
            # as one overwriting WordNet.
            existing = next(
                (c for c in cells_by_row.get(row_key, ()) if c.column == cell.column),
                matrix.cell(row_key, cell.column),
            )
            if existing is not None:
                overwrites.append(
                    f"{row_key} -> {cell.column}: {existing.weight:+.2f} via {existing.relation} "
                    f"becomes {cell.weight:+.2f} via {cell.relation}"
                )
            cells_by_row.setdefault(row_key, []).append(cell)
            written.append((row_key, cell))

    index = {key: position for position, key in enumerate(matrix.keys)}
    rows = []
    for row in matrix.rows:
        additions = cells_by_row.get(row.key)
        if not additions:
            rows.append(row)
            continue
        merged = {cell.column: cell for cell in row.cells}
        for cell in additions:
            merged[cell.column] = cell
        rows.append(
            replace(row, cells=tuple(sorted(merged.values(), key=lambda cell: index[cell.column])))
        )

    return Applied(
        matrix=Matrix(name=matrix.name, keys=matrix.keys, rows=tuple(rows), note=matrix.note),
        written=tuple(written),
        overwrites=tuple(overwrites),
        unwritable=tuple(unwritable),
    )


# ------------------------------------------------------------------------------------------------
# the gate
# ------------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Approval:
    """The claim an approving run makes: a human read the evidence and judged it analytic.

    Two fields and both are required, because they are two different statements. `i_am_the_captain`
    asserts that the reader of the evidence is the person entitled to rule on it; `authorized_by`
    records WHO and WHEN, so a curated cell can always be traced back to the hand that allowed it
    (the same rule as `added_words`, requirement 15).
    """

    i_am_the_captain: bool = False
    authorized_by: str = ""


def assert_captains_hand(approval: Approval | None) -> Approval:
    """THE gate. Everything that would write a curated cell into R passes through here first."""
    if approval is None or not approval.i_am_the_captain:
        raise NotTheCaptainsHand(
            "REFUSED: writing a curated cell into R is the Captain's call, not the instrument's "
            "(requirement 20). A proposal is ANALYTIC or CONTINGENT, and only a reader of the "
            "evidence can say which. `simulate` answers «would it work?» without this."
        )
    if not approval.authorized_by.strip():
        raise NotTheCaptainsHand(
            "REFUSED: an approval must record who authorized it. A curated cell whose hand cannot "
            "be named is a cell nobody can later argue with — the manifest would be a log, not a "
            "ledger."
        )
    return approval


def approve(
    matrix: Matrix,
    proposals: Iterable[Proposal],
    policy: RelationPolicy,
    approval: Approval | None = None,
) -> Applied:
    """The same application as `apply`, behind the gate. The tool that writes calls THIS one."""
    assert_captains_hand(approval)
    return apply(matrix, proposals, policy)


__all__ = [
    "Applied",
    "Approval",
    "CurationRefused",
    "DefinitionProvider",
    "INVOLVES",
    "NotTheCaptainsHand",
    "Proposal",
    "RECIPROCAL_SUFFIX",
    "apply",
    "approve",
    "assert_captains_hand",
    "cells_of",
    "guess_relation",
    "propose_directed",
    "propose_pair",
    "quote",
    "relabel",
    "self_reference_skips",
]


# ------------------------------------------------------------------------------------------------
# curated edges as an INPUT to a build — the E1d T4 repair
# ------------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CuratedMerge:
    """What consuming the curated edges did. Every field exists because something was once silent.

    `unresolvable` is the one that matters. A rebuild changes MEMBERSHIP — the closure's cut moves,
    a word joins or leaves — so an approved edge can name a key the new base does not have. Dropping
    it quietly is exactly the class of silence this whole epic came from, so it is returned, counted
    and printed, and the build says so out loud.

    `overrode_mined` is a DISCOVERY, not an error: the resource already stated something about that
    pair and a human decided otherwise. Worth reading every time it happens.
    """

    edges: int
    cells: int
    withdrawn: int
    unresolvable: tuple[tuple[str, str, str], ...] = ()
    overrode_mined: tuple[tuple[str, str, str], ...] = ()

    @property
    def is_clean(self) -> bool:
        return not self.unresolvable


def proposal_of_row(row) -> Proposal:
    """A stored curated edge back into the shape `cells_of` already knows how to write.

    The row is the record; the `Proposal` is the shape. Keeping one writer means an edge approved in
    August and an edge approved today cannot land as two different cells.
    """
    return Proposal(
        source_key=row["source_key"],
        target_key=row["target_key"],
        relation=row["relation"],
        weight=float(row["weight"]),
        sense=row.get("sense", ""),
        # The row stores the evidence already marked up; `Proposal.evidence` would rebuild it from
        # a definition and a token the row no longer carries separately.
        definition=row.get("evidence", ""),
        naming_token="",
        relabelled=bool(row.get("relabelled", False)),
    )


def merge_curated(matrix, rows, policy: RelationPolicy) -> tuple[object, CuratedMerge]:
    """R with every standing curated edge written into it, and a report of what that took.

    **A CURATED CELL OVERRIDES A MINED ONE.** It is the only cell in the system carrying a human
    authorization and verbatim evidence, and an approval that loses to the walk it was written to
    correct would be theatre. It is reported when it happens, because «the resource said otherwise
    and a person disagreed» is a thing worth reading.

    A WITHDRAWN edge is skipped and counted — `withdrawn_at` is the «mostly» in append-mostly, and a
    withdrawal is a fact with a date rather than an absence.

    Pure: `rows` are plain mappings, so the same function serves a live database, a fixture and a
    build nobody applied yet.
    """
    from dataclasses import replace

    known = set(matrix.keys)
    written: dict[str, list[Cell]] = {}
    unresolvable: list[tuple[str, str, str]] = []
    withdrawn = 0
    edges = 0

    for row in rows:
        if row.get("withdrawn_at"):
            withdrawn += 1
            continue
        missing = [k for k in (row["source_key"], row["target_key"]) if k not in known]
        if missing:
            unresolvable.append((row["source_key"], row["target_key"],
                                 f"not a dimension of this base: {', '.join(missing)}"))
            continue
        edges += 1
        for key, cell in cells_of(proposal_of_row(row), policy):
            written.setdefault(key, []).append(cell)

    overrode: list[tuple[str, str, str]] = []
    out_rows = []
    for row in matrix.rows:
        additions = written.get(row.key, ())
        if not additions:
            out_rows.append(row)
            continue
        replaced = {cell.column: cell for cell in additions}
        for cell in row.cells:
            if cell.column in replaced and cell.source != SOURCE_CURATED:
                overrode.append((row.key, cell.column, cell.relation))
        kept = [c for c in row.cells if c.column not in replaced]
        out_rows.append(replace(row, cells=(*kept, *additions)))

    return replace(matrix, rows=tuple(out_rows)), CuratedMerge(
        edges=edges,
        cells=sum(len(v) for v in written.values()),
        withdrawn=withdrawn,
        unresolvable=tuple(unresolvable),
        overrode_mined=tuple(overrode),
    )
