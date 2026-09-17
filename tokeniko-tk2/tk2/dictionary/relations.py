"""R — THE RELATION MATRIX. Every cell is a named relation, and the cell can say which one.

Requirement 10: density comes from RELATIONS, never co-occurrence. R holds the statements a lexical
resource actually makes — opposition, entailment, causation, is-a, manner, part-of — SIGNED, sparse,
and accountable per cell. What two definitions happen to share is a different question with a
different answer, and it is D's (T4); `gloss_overlap` is therefore not a relation of R's and never
was one, whatever the prototype's single weight table made it look like.

WHAT THE PROTOTYPE PROVED AND THIS INDUSTRIALISES (`docs/dictionary/origin-prototype/tk2_matrix.py`, the 2026-08-12
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
from dataclasses import replace
from typing import Mapping, Protocol, runtime_checkable

from tk2.dictionary import keys
from tk2.dictionary.config import DERIVATIONAL_PRIMARY_SENSE, RelationPolicy
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

#: This matrix's name — its collection AND the identifier a stored build files it under.
#: Declared here rather than imported from `tk2.core.constants`, because this package is pure
#: and importing the body's constants would be the first thread of a dependency it must not have.
#: `tk2.core.constants` names it too, and a test holds the two to each other.
RELATIONS_MATRIX = "dictionary_base_relations"

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


# ------------------------------------------------------------------------------------------------
# ANTONYM SYMMETRY — three readings, all of them MEASUREMENTS (the QM's orders of 2026-08-26)
# ------------------------------------------------------------------------------------------------
#
# WordNet states an antonymy once, on one lemma of one pair, so `leave -> enter` can exist while
# `enter -> leave` does not — and semantic opposition is symmetric whether or not the lexicographer
# wrote it twice. Three readings of that, and the parameter is a RUN's, never a policy row: nobody
# has ruled any of them.

#: What the resource stated, and no more. The standing reading.
SYMMETRY_OFF = "stated"

#: State the reverse cell wherever an antonym cell exists, whatever was already there. MEASURED
#: 2026-08-26: +143 cells, +147 negatives — and four stated relations destroyed, `dark.n -> day.n`
#: (holonym +0.60) among them. Kept exactly as it was measured so those numbers stay reproducible:
#: it emits a plain `antonym`, which is precisely the defect the next reading exists to fix.
SYMMETRY_OVERWRITE = "overwrite"

#: Add the reverse cell ONLY where R is silent for that ordered pair, and give it its OWN relation
#: name (`ANTONYM_INFERRED`). The Captain's design condition, 2026-08-26: if symmetry is ever ruled
#: standing, an inferred opposition must be distinguishable from a stated one forever — the same
#: principle that keeps a curated cell distinguishable from a mined one. So the measurement is
#: shaped the way a ruling would land, and the numbers reported are the numbers it would produce.
SYMMETRY_ADD_ONLY = "add_only"

ANTONYM_SYMMETRIES = (SYMMETRY_OFF, SYMMETRY_OVERWRITE, SYMMETRY_ADD_ONLY)

# THERE IS NO DEFAULT. `add_only` is standing since the Captain's ruling of 2026-08-26 and it stands
# in a ROW (`dictionary_policy`, kind `relation`, since v5), like the lemma scope beside it. A
# constant here would answer for the rows precisely when they are silent — and an undeclared mode
# quietly reading as `stated` would be the ruling un-made by an absence. A run may still name a
# reading (that is how the other two are reproduced); saying nothing defers to the policy, and a
# policy that says nothing either is a refusal.

#: The name an INFERRED opposition carries. Not `antonym`, which would make «WordNet said so» and
#: «we completed it» one cell; not `antonym_of` or the curated `_reciprocal` suffix either, because
#: both of those already mean «the weaker reverse read of a directional relation» (`entailed_by`,
#: `used_for_reciprocal`) and this is the SAME claim at the same strength, merely inferred. Under
#: `add_only` it needs its own weight in the policy, exactly as a standing ruling would have to
#: write one — `assert_coherent` refuses the run otherwise, which is the check doing its job.
ANTONYM_INFERRED = "antonym_inferred"


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


def known_relations(provider: RelationProvider, antonym_symmetry: str) -> tuple[str, ...]:
    """Every relation name a cell may carry: the resource's, plus the ones the walk itself makes."""
    stated = tuple(provider.relations())
    derived = (IDENTITY, SYNONYM) + tuple(REVERSE_OF[rel] for rel in REVERSE_OF if rel in stated)
    if antonym_symmetry == SYMMETRY_ADD_ONLY:
        derived += (ANTONYM_INFERRED,)
    return tuple(dict.fromkeys(stated + derived))


def assert_coherent(
    provider: RelationProvider,
    policy: RelationPolicy,
    antonym_symmetry: str,
    produced_elsewhere=(),
) -> None:
    """The two sides name the same relations. Called before anything is mined.

    `produced_elsewhere` names the relations a DIFFERENT miner writes into R — since policy v12 the
    gloss references (`tk2.dictionary.references`), which are read out of definitions rather than
    off the relation graph. Without it this check fires on its own success: it cannot see a miner it
    does not call, and would refuse a weight that takes effect perfectly well.

    Injected rather than imported, and named by the CALLER, because the alternative is this module
    learning about every future miner — and the check's whole value is that it knows exactly which
    relations it is responsible for.
    """
    declared = set(policy.relations) - set(produced_elsewhere)
    known = set(known_relations(provider, antonym_symmetry))
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
    name: str = RELATIONS_MATRIX,
    progress=None,
    antonym_symmetry: str | None = None,
    produced_elsewhere=None,
) -> Matrix:
    """Fill R over `dimensions` — THE call the build tool makes.

    `dimensions` is the key space in ITS order, which the closure and `glosses.dimensions_of`
    decided; nothing here adds or removes a dimension. A relation pointing at a sense no dimension
    speaks simply produces no cell: it is a statement about a word the base does not contain, and
    inventing an axis for it would be membership by side effect.
    """
    antonym_symmetry = resolve_symmetry(policy, antonym_symmetry)
    # R HAS TWO MINERS and the coherence check is about both: this one walks the relation graph,
    # `references` reads definitions. A check that knew only its own miner would fire on its own
    # success — it did, the moment policy v12 weighted the gloss references — so the sibling is
    # named here rather than left to every caller to remember, which the first attempt proved they
    # will not. A caller may still override it to hold a narrower scope.
    if produced_elsewhere is None:
        from tk2.dictionary import references

        produced_elsewhere = references.RELATIONS
    assert_coherent(provider, policy, antonym_symmetry, produced_elsewhere)
    index = dimension_index(dimensions)
    order = tuple(index)

    speakers = _speakers_of_sense(order, provider)
    candidates = _candidates(order, provider, policy, speakers, progress, antonym_symmetry)

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


def policy_for(policy: RelationPolicy, mode: str) -> RelationPolicy:
    """The policy a given reading of antonymy REQUIRES — with the weight row it needs, or without.

    A reading and its weight travel together, and the coherence check enforces it from both sides:
    `add_only` mints `antonym_inferred` cells, so the relation must be weighted, and the other two
    mint none, so a weight for it would be a curated decision that never takes effect. Since v5 the
    standing policy carries both, so reproducing an older reading means reproducing the policy that
    reading belonged to — which is literally what `stated` was: v4, without this row.

    Here rather than in the tool because it is the RULE, not the plumbing: a caller that stripped
    the weight by hand could strip something else with it.
    """
    weights = tuple((name, weight) for name, weight in policy.weights if name != ANTONYM_INFERRED)
    if mode == SYMMETRY_ADD_ONLY:
        weights += ((ANTONYM_INFERRED, policy.weight_of(ANTONYM)),)
    return replace(policy, weights=weights, antonym_symmetry=mode)


def resolve_symmetry(policy: RelationPolicy, argument: str | None) -> str:
    """Which reading of a one-sided antonymy this run uses: the RUN's, else the POLICY's, else a
    refusal.

    A run naming one is how the two non-standing readings are reproduced — the same shape
    `ClosurePolicy.extra_seeds` has, a run's own argument against the standing declaration. Neither
    of them may be stored, and the tool refuses that at its own door.
    """
    mode = argument if argument is not None else policy.antonym_symmetry
    if mode is None:
        raise RelationsIncoherent(
            "no antonym symmetry declared: this policy version does not say how a one-sided "
            f"antonymy is read, and there is no default in code to fall back on. Policy v5 "
            f"(db/0008) declares it; the readings are {ANTONYM_SYMMETRIES}."
        )
    if mode not in ANTONYM_SYMMETRIES:
        raise RelationsIncoherent(
            f"unknown antonym symmetry {mode!r} — the readings are {ANTONYM_SYMMETRIES}"
        )
    return mode


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


#: The one lemma-stated relation whose sense resolution is a policy row (v13). Named here rather
#: than spelled inline, because the walk below compares against it twice.
DERIVATIONAL = "derivational"


def _primary_senses_of(order, provider) -> dict[str, str | None]:
    """dimension -> its primary sense, or a refusal when the provider cannot say.

    Only asked when the policy mines `derivational` at primary-sense resolution, so a fixture that
    never declares it need not answer — and one that declares it without being able to answer is a
    policy describing a walk this resource cannot run.
    """
    missing = [name for name in ("primary_sense_of_key", "relations_of_sense")
               if not hasattr(provider, name)]
    if missing:
        raise RelationsIncoherent(
            f"the policy mines `derivational` at primary-sense resolution and this provider cannot "
            f"answer {missing}. A resolution the resource cannot state is not a resolution."
        )
    return {key: provider.primary_sense_of_key(key) for key in order}


def _derivational_at_primary_sense(key, stated, provider, primary_of):
    """`stated` with `derivational` re-read from the dimension's PRIMARY SENSE only — the SOURCE half
    of the v13 ruling (the target half is in `_candidates`, where the column is known).

    Through `relations_of_sense`, the provider's own one-synset walk: the same walk the sense layer
    reads, with the same lemma scope, so there is no second set of decisions to drift.
    """
    stated = dict(stated)
    stated.pop(DERIVATIONAL, None)
    if primary_of.get(key) is None:
        return stated
    word, pos = keys.split_key(key)
    derived = provider.relations_of_sense(keys.sense_key(word, pos, 1)).get(DERIVATIONAL)
    if derived:
        stated[DERIVATIONAL] = derived
    return stated


def _candidates(
    order, provider, policy, speakers, progress, antonym_symmetry: str
) -> dict[str, dict[str, list[Provenance]]]:
    """Every relation that holds between two dimensions, collected per (row, column).

    Collected rather than resolved on the way in, because the winner is a comparison and a cell's
    `via` is the whole list: «causes, and also entails» is a different fact from «causes alone», and
    the prototype's `max()` threw the second half away.
    """
    found: dict[str, dict[str, list[Provenance]]] = defaultdict(lambda: defaultdict(list))
    synonym = policy.weight_of(SYNONYM) if SYNONYM in policy.relations else 0.0
    inferred: list[tuple[str, str]] = []

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

    # REQUIREMENT 16 (policy v13). A dimension IS its primary sense under the closure's reading,
    # and `derivational` used to be mined across every sense of the word — which is how
    # `land.n~land.v`, `compass.n~compass.v` and `play.n~play.v` came to read positive though
    # WordNet links none of their primary senses. Both ends are restricted: the source here, the
    # target where the column is known.
    primary_only = policy.derivational_resolution == DERIVATIONAL_PRIMARY_SENSE
    primary_of = _primary_senses_of(order, provider) if primary_only else {}

    for position, key in enumerate(order, 1):
        stated = provider.relations_of_key(key)
        if primary_only:
            stated = _derivational_at_primary_sense(key, stated, provider, primary_of)
        for relation, targets in stated.items():
            weight = policy.weight_of(relation)
            reverse = REVERSE_OF.get(relation)
            reverse_weight = policy.weight_of(reverse) if reverse in policy.relations else 0.0
            if not weight and not reverse_weight:
                continue
            for sense in targets:
                for column in speakers.get(sense, ()):
                    if primary_only and relation == DERIVATIONAL and primary_of.get(column) != sense:
                        # The target half: a derivation lands only on the column whose OWN primary
                        # sense it names — not on every dimension that merely speaks that synset.
                        continue
                    add(key, column, relation, weight)
                    if reverse:
                        add(column, key, reverse, reverse_weight)
                    if relation == ANTONYM:
                        if antonym_symmetry == SYMMETRY_OVERWRITE:
                            # As first measured: the same relation at the same weight, landing
                            # wherever it lands. Four stated relations died of it.
                            add(column, key, ANTONYM, weight)
                        elif antonym_symmetry == SYMMETRY_ADD_ONLY:
                            # Held back until the whole walk is done: «is R silent for this ordered
                            # pair» cannot be answered while the pair is still being filled in.
                            inferred.append((column, key))
        if progress is not None:
            progress(position, len(order))

    # ADD-ONLY, in its own pass, because the question it asks is about the FINISHED row: an inferred
    # opposition may complete a pair R had nothing to say about and may never displace something it
    # did. The four cells the overwriting reading destroyed are exactly the ones this skips.
    if inferred:
        weight = policy.weight_of(ANTONYM_INFERRED)
        for row, column in inferred:
            if found[row].get(column):
                continue
            add(row, column, ANTONYM_INFERRED, weight)
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
