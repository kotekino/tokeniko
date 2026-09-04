"""R — THE RELATION MATRIX. Every cell is a named relation, and the cell can say which one.

Requirement 10: density comes from RELATIONS, never co-occurrence. R holds the statements a lexical
resource actually makes — opposition, entailment, causation, is-a, manner, part-of — SIGNED, sparse,
and accountable per cell. What two definitions happen to share is a different question with a
different answer, and it is D's (T4); `gloss_overlap` is therefore not a relation of R's and never
was one, whatever the prototype's single weight table made it look like.

WHAT THE PROTOTYPE PROVED AND THIS INDUSTRIALISES (`scripts/tk2/tk2_matrix.py`, the 2026-08-12
review): the walk, the weights, the sign, and the four decisions worth restating because a rewrite
is exactly where they get lost —

  1. SYNONYMY FIRST, THEN ANTONYMY, AND ANTONYMY RETURNS. The sign IS the antonym column-read
     primitive: `row[X][index(W)] < 0` is how opposition is asked. A blended average would destroy
     it (measured: `enter~leave` reads -0.331 relations-only and +0.519 once a gloss tail is mixed
     in), so nothing here averages two relations into one number.
  2. THE ROW IS ASYMMETRIC. Row X, column Y is X's relation TO Y. `entails` and `entailed_by` are
     two statements of different strength, not one symmetric cell, which is why a reverse read is
     emitted as its own weaker cell rather than mirrored.
  3. CROSS-POS CELLS ARE ALLOWED, and that is the whole reason the base splits by POS in the first
     place: `attribute` (hot ~ temperature) and `derivational` (able ~ ability) are cross-POS by
     nature, and a same-POS-only matrix could not state them at all. Not a knob — a knob here would
     be a second base no fingerprint could tell from the first.
  4. WU-PALMER IS IN NEITHER MATRIX. It is not a named edge (it fails R's provenance criterion:
     `wup` names a SCORE OVER the taxonomy, not a relation between two words) and it is not
     co-occurrence (it fails D's). Recoverable later as its own graded-taxonomy layer if a question
     needs it. The prototype recorded the ruling in `MATRIX_WUP_NOTE`; it is repeated here because
     a weight table that no longer lists it would otherwise look like an oversight.

WHICH SENSES SPEAK. Every sense of the dimension's part of speech — `land.v` asks WordNet about all
of the verb's readings, not only the first. The closure's `senses` cut governs which senses write a
DEFINITION (membership); relations are a different question about the same dimension, and a row that
heard only sense 1 would drop `eat entails chew` the moment WordNet ordered another reading first.
This is the prototype's behaviour, carried across deliberately, and it is inside `RELATION_RULES`.

THE WALK IS INVERTED, and that is a performance decision with a correctness argument. The prototype
compared every ordered pair of keys — 19.8 million of them at the full base, most to discover that
nothing at all relates the two. Here every relation is walked once per key and its TARGETS are
mapped onto the dimensions that speak them, which produces exactly the same cells (a cell exists iff
some relation of X names a sense Y speaks) in time proportional to the edges rather than to n².

Pure: a `RelationProvider` and a `RelationPolicy` go in, a `Matrix` comes out. The resource lives
behind the provider, the weights live in rows.
"""

from collections import defaultdict
from typing import Mapping, Protocol, runtime_checkable

from tk2.dictionary import keys
from tk2.dictionary.config import RelationPolicy
from tk2.dictionary.matrix import (
    SOURCE_AXIS,
    SOURCE_MINED,
    Cell,
    Matrix,
    MatrixRow,
    Provenance,
    assert_square,
    dimension_index,
)

#: The diagonal. A dimension owns its own axis; the weight is declared like every other.
IDENTITY = "identity"

#: Two dimensions that share a synset. Computed here rather than asked of the provider, because it
#: is not a relation the resource STATES — it is what «the same sense speaks for both» means, and a
#: provider that answered it separately could disagree with its own sense lists.
SYNONYM = "synonym"

#: Opposition, and the one negative weight in the table. Read off the LEMMA (WordNet puts antonymy
#: between lemmas, not synsets) and returned by the provider like any other relation.
ANTONYM = "antonym"

#: The relations that have a weaker reverse read: «Y entails X» is a real statement about X, and a
#: different one from «X entails Y». FRAME — the shape of the walk, not its content: which relations
#: invert is a fact about what the relation MEANS, and what the inverse is worth is a row.
REVERSE_OF = {
    "entails": "entailed_by",
    "causes": "caused_by",
    "troponym": "troponym_of",
}


class RelationsIncoherent(ValueError):
    """The provider states a relation the policy does not weight, or the reverse.

    Loud, for `PolicyRowsInvalid`'s reason: a relation mined and never weighted would be a cell
    silently dropped, and a weight declared for a relation nothing produces would be a curated
    decision that never took effect and never said so. Switching a relation OFF is a weight of
    0.0 — a declaration — never an absent row.
    """


@runtime_checkable
class RelationProvider(Protocol):
    """What R needs from a lexical resource, and nothing more.

    Both answers are about ONE DIMENSION, in the resource's own vocabulary of sense identifiers. The
    builder never learns what a synset is: it intersects opaque identifiers, which is what lets a
    twenty-word fixture and WordNet drive the same walk.
    """

    def senses_of_key(self, key: str) -> tuple[str, ...]:
        """The senses this dimension speaks for — every reading of its part of speech."""
        ...

    def relations_of_key(self, key: str) -> Mapping[str, frozenset[str]]:
        """`relation -> the sense identifiers it points at`, for this dimension.

        Only relations the resource actually states. `synonym` and `identity` are not among them
        (see their constants above), and a reverse read is the builder's to derive.
        """
        ...

    def relations(self) -> tuple[str, ...]:
        """Every relation name this provider can produce. Declared so a weight naming a relation the
        resource does not have is caught at build time rather than by an empty column."""
        ...


# ------------------------------------------------------------------------------------------------
# the walk
# ------------------------------------------------------------------------------------------------


def known_relations(provider: RelationProvider) -> tuple[str, ...]:
    """Every relation name a cell may carry: the resource's, plus the three the walk itself makes."""
    stated = tuple(provider.relations())
    derived = (IDENTITY, SYNONYM) + tuple(REVERSE_OF[rel] for rel in REVERSE_OF if rel in stated)
    return tuple(dict.fromkeys(stated + derived))


def assert_coherent(provider: RelationProvider, policy: RelationPolicy) -> None:
    """The two sides name the same relations. Called before anything is mined."""
    declared = set(policy.relations)
    known = set(known_relations(provider))
    unweighted = sorted(known - declared)
    unknown = sorted(declared - known)
    if unweighted:
        raise RelationsIncoherent(
            f"the resource states relations the policy does not weight: {unweighted}. A relation "
            f"is switched off with a weight of 0.0 — a declaration — never by leaving it out."
        )
    if unknown:
        raise RelationsIncoherent(
            f"the policy weights relations nothing produces: {unknown}. A curated decision that "
            f"never takes effect is one nobody can see failing."
        )


def build(
    dimensions,
    provider: RelationProvider,
    policy: RelationPolicy,
    name: str = "base_r",
    progress=None,
) -> Matrix:
    """Fill R over `dimensions` — THE call the build tool makes.

    `dimensions` is the key space in ITS order, which the closure and `glosses.dimensions_of`
    decided; nothing here adds or removes a dimension. A relation pointing at a sense no dimension
    speaks simply produces no cell: it is a statement about a word the base does not contain, and
    inventing an axis for it would be membership by side effect.
    """
    assert_coherent(provider, policy)
    index = dimension_index(dimensions)
    order = tuple(index)

    speakers = _speakers_of_sense(order, provider)
    candidates = _candidates(order, provider, policy, speakers, progress)

    rows = []
    identity = policy.weight_of(IDENTITY)
    for key in order:
        cells = []
        if identity:
            cells.append(
                Cell(
                    column=key,
                    weight=identity,
                    relation=IDENTITY,
                    source=SOURCE_AXIS,
                    via=(Provenance(IDENTITY, identity),),
                )
            )
        stated = candidates.get(key, {})
        for column in sorted(stated, key=lambda k: index[k]):
            cell = _resolve(column, stated[column], policy)
            if cell is not None:
                cells.append(cell)
        rows.append(MatrixRow(key=key, index=index[key], cells=tuple(cells)))

    matrix = Matrix(name=name, keys=order, rows=tuple(rows))
    assert_square(matrix)
    return matrix


def _speakers_of_sense(order, provider: RelationProvider) -> dict[str, list[str]]:
    """sense identifier -> the dimensions that speak it, in dimension order.

    The inversion the whole walk rests on. A synset spoken by two dimensions is what synonymy IS
    (`eat.v` and `devour.v` share `eat.v.02`), and a synset spoken by one is how every other
    relation lands: the target of `kill causes die` is a sense, and the cell is written to whatever
    dimension speaks it.
    """
    speakers: dict[str, list[str]] = defaultdict(list)
    for key in order:
        for sense in provider.senses_of_key(key):
            speakers[sense].append(key)
    return speakers


def _candidates(order, provider, policy, speakers, progress) -> dict[str, dict[str, list[Provenance]]]:
    """Every relation that holds between two dimensions, collected per (row, column).

    Collected rather than resolved on the way in, because the winner is a comparison and a cell's
    `via` is the whole list: «causes, and also entails» is a different fact from «causes alone», and
    the prototype's `max()` threw the second half away.
    """
    found: dict[str, dict[str, list[Provenance]]] = defaultdict(lambda: defaultdict(list))
    synonym = policy.weight_of(SYNONYM) if SYNONYM in policy.relations else 0.0

    def add(row: str, column: str, relation: str, weight: float) -> None:
        if row == column or not weight:
            return
        entries = found[row][column]
        if any(entry.relation == relation for entry in entries):
            return
        entries.append(Provenance(relation, weight))

    if synonym:
        for sense, spoken_by in speakers.items():
            if len(spoken_by) < 2:
                continue
            for row in spoken_by:
                for column in spoken_by:
                    add(row, column, SYNONYM, synonym)

    for position, key in enumerate(order, 1):
        for relation, targets in provider.relations_of_key(key).items():
            weight = policy.weight_of(relation)
            reverse = REVERSE_OF.get(relation)
            reverse_weight = policy.weight_of(reverse) if reverse in policy.relations else 0.0
            if not weight and not reverse_weight:
                continue
            for sense in targets:
                for column in speakers.get(sense, ()):
                    add(key, column, relation, weight)
                    if reverse:
                        add(column, key, reverse, reverse_weight)
        if progress is not None:
            progress(position, len(order))
    return found


def _resolve(column: str, stated: list[Provenance], policy: RelationPolicy) -> Cell | None:
    """One cell out of everything that held between two dimensions.

    THE PROTOTYPE'S PRECEDENCE, kept exactly: synonymy answers first, then antonymy (and antonymy
    RETURNS, so the sign survives a pair that is also taxonomically close), then the strongest claim
    by absolute weight. Ties go to the relation declared FIRST in the policy rows — which is why the
    weight rows carry a position: a rebuild must not be free to flip a cell's provenance because two
    relations happened to be worth the same.
    """
    if not stated:
        return None
    via = tuple(sorted(stated, key=lambda p: (-abs(p.weight), policy.precedence(p.relation))))
    winner = next((p for p in via if p.relation == SYNONYM), None)
    if winner is None:
        winner = next((p for p in via if p.relation == ANTONYM), None)
    if winner is None:
        winner = via[0]
    return Cell(
        column=column,
        weight=winner.weight,
        relation=winner.relation,
        source=SOURCE_MINED,
        via=via,
    )


# ------------------------------------------------------------------------------------------------
# reading R back — the half of requirement 19 that R answers
# ------------------------------------------------------------------------------------------------


def stated_between(matrix: Matrix, a: str, b: str) -> tuple[Cell | None, Cell | None]:
    """The two directed cells of a pair, `(a->b, b->a)`.

    Both, never one: R is asymmetric on purpose, and a reader that took whichever direction it found
    first would report `bed.n -> sleep.v` and `sleep.v -> bed.n` as the same statement. An absent
    cell is MUTE — R declining to speak — and that is a third answer beside near and far.
    """
    return matrix.cell(a, b), matrix.cell(b, a)


def relations_of(matrix: Matrix, key: str) -> dict[str, list[str]]:
    """A dimension's row read as «which relation reaches which key» — for a probe, and for the eye
    the Captain walks the map with."""
    out: dict[str, list[str]] = defaultdict(list)
    row = matrix.row(key)
    if row is None:
        raise keys.InvalidKey(f"{key!r} is not a dimension of {matrix.name}")
    for cell in row.cells:
        out[cell.relation].append(cell.column)
    return dict(out)
