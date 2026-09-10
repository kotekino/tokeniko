"""THE DECLARED POLICY — its SHAPE, and the fingerprint taken over it before it measures anything.

Tooling requirement 4, and the ruling that carries it: policy is declared BEFORE results, hashed
into the build manifest, and never edited after a measuring run. The prototype held the same idea in
module-level globals, which a `--depth 3` flag could quietly override without the manifest ever
seeing it. Here the policy is a VALUE: a run takes a config object, the manifest records that
object's fingerprint, and a variant is a different object rather than a mutated global.

**WHAT IS NO LONGER HERE, and why (T4b, the standing law of 2026-08-25).** This module used to
DECLARE the seeds, the closure cuts and the eighteen bar pairs. They are CURATION — «authorized
judgment, as complete as we can make it, grown generated-then-curated» — and «a category-2 set
stated in code is a defect even when its contents are correct». They now live in `dictionary_policy`
and `dictionary_bar`, arrive through `tk2.dictionary.policy.config_from_rows`, and are fingerprinted
into the manifest at both levels. What stays here is the SHAPE: what a closure cut IS, what a bar
pair IS, and how a policy is canonicalised and hashed. Shape is frame; content never is.

There is deliberately no `STANDING` any more, and no default for a single declared value. A default
in code is a second declaration of it, and the day the Captain moves `max_size` in a row, a bare
`ClosurePolicy()` elsewhere would still be answering 400 — with nothing to say the two disagree.
Every construction states its policy, or it reads it from the rows.

**WHAT NEVER ARRIVED HERE (T3).** R's relation weights were the standing law's own worked example —
«the relation weights you write in T3: they land as rows from the start, never as a table in
`config.py`» — so `RelationPolicy` below is a SHAPE with no values in it, and the same is true of
`keys.Alphabet`, which policy v3 declares because which parts of speech exist is WordNet's answer
rather than the key grammar. Both are optional on a config for a ledger's reason, spelled out at
`DictionaryConfig`.

Requirement 12 is enforced in code, not by care: the bar's own words are seeds (`DictionaryConfig.
seeds`). Run r1 of the prototype scored only 12 of 18 pairs because `kill`, `water` and `swallow`
were never reached by the seed closure — a subset that cannot score its own bar is not a test.
"""

import hashlib
import json
from dataclasses import asdict, dataclass, replace
from typing import Literal

from tk2.dictionary import keys

SenseMode = Literal["primary", "all"]
Verdict = Literal["NEAR", "FAR"]


# ------------------------------------------------------------------------------------------------
# the reduction's law, dated
# ------------------------------------------------------------------------------------------------

# NOT a knob — there is no other setting, and the three decisions behind this date are law: gloss
# mining keeps every POS-aware reading of a token (requirement 21), the stop list yields to lexicon
# membership (the Captain's ruling), and a reading the resource knows only as a NAME is refused at
# membership and at mining alike (option C). It is hashed anyway, because the fingerprint's claim is
# that two builds sharing it were measured under the same policy, and on 2026-08-25 the mining law
# moved underneath a config that could not see it. A build from before and one from after must not
# be able to present the same hash. Bump when the reduction's law moves again.
#
# It stays in CODE while the seeds and the bar leave, and the standing law is what says so: this
# names the shape in which a gloss becomes edges at all, it moves only by changing the mining code,
# and a row could not move it. The seeds are content; this is the grammar the content is read under.
#
# The `.2` is not decoration: the law moved TWICE on the 25th (the stop-list ruling in the morning,
# the name refusal in the afternoon), and a bare date cannot separate two builds a day cannot
# separate either. A same-day amendment takes the next ordinal.
REDUCTION_RULES = "2026-08-25.2"


# ------------------------------------------------------------------------------------------------
# THE BAR — one expectation, declared before anything is built (requirement 12)
# ------------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class BarPair:
    """One expectation. `a` and `b` are keys or bare words; `why` is the sentence that justified the
    pair when it was declared, kept verbatim because a bar whose reasons are lost is a bar nobody can
    argue with.

    The pairs themselves are rows (`dictionary_bar`) since T4b; this is the shape they are read into.
    """

    a: str
    b: str
    verdict: Verdict
    why: str


def bar_words(pairs) -> tuple[str, ...]:
    """The words the bar names, POS suffix stripped, first-mention order preserved."""
    out: list[str] = []
    for pair in pairs:
        for side in (pair.a, pair.b):
            word = keys.word_of(side) if keys.is_base_key(side) else keys.normalize_word(side)
            if word not in out:
                out.append(word)
    return tuple(out)


# ------------------------------------------------------------------------------------------------
# the closure policy
# ------------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ClosurePolicy:
    """How far the seed closure is allowed to run before we call it exploded.

    `max_depth` is THE DEPTH CUT, and it is a parameter rather than a constant because the review
    left a lesson attached to it: at depth 2 the word `right` sat exactly one ring outside the
    subset — its namers entered on the last expanded layer and were never expanded themselves. That
    is an honest boundary, not a bug, but a boundary nobody can see is a boundary nobody can rule
    on, so the closure reports what lies one ring past the cut and this number is the thing the
    Captain moves when he disagrees with it.

    `max_size` is the second cut and answers a different question: the QM's stated counter that
    `closed` and `sensitive` would fight — function words close cheaply, `eat` pulls in the world.

    Both are REQUIRED. Their values are curation and live in rows (`kind: "closure"`); a default
    here would be a second, quieter declaration of a number the Captain moves in the db.
    """

    max_depth: int
    max_size: int
    # Which senses of a word contribute its definition. `primary` = the first synset per POS (what
    # the Jurassic build used); `all` = every sense, denser and noisier.
    senses: SenseMode
    # Extra seeds beyond the declared families and the bar's own words — a run's own argument, and
    # the one field here that is NOT a row: a standing declaration is what the rows hold, and this
    # is what a single run says against it. Empty by default because «no argument» is a real
    # default, not an undeclared value.
    extra_seeds: tuple[str, ...] = ()

    def __post_init__(self):
        if self.max_depth < 0:
            raise ValueError("max_depth is a number of rings, never negative")
        if self.max_size < 1:
            raise ValueError("max_size must leave room for at least one word")
        if self.senses not in ("primary", "all"):
            raise ValueError(f"unknown sense mode {self.senses!r}")


# ------------------------------------------------------------------------------------------------
# R's policy — the relation weights, and the curator's closed vocabulary
# ------------------------------------------------------------------------------------------------

# The law of the CELL WALK, dated, for REDUCTION_RULES' reason and no other: the weights say how
# much a relation counts, and this says what «a relation holds between these two dimensions» means
# at all — every sense of the dimension's POS speaks (not only the first, which is what the closure's
# `senses` governs), synonymy is a shared synset, antonymy is read off the lemma and RETURNS so the
# sign survives, a reverse read is its own weaker cell, and cross-POS cells are allowed because
# `attribute` and `derivational` are cross-POS by nature. Two builds sharing a fingerprint must have
# been measured under the same walk; bump this when the walk moves.
#
# IT DID NOT MOVE WHEN THE LEMMA SCOPE WAS RULED (2026-08-26), and the reason is worth stating so
# the next reader does not «fix» it: whose lemma may speak LEFT this law and became a policy row
# (`RelationPolicy.lemma_scope`), so the config fingerprint now covers it directly and a bump would
# say the code changed its mind about something it no longer decides. What this date names is what
# remains in code — and a policy version that declares no scope can no longer build R at all, so no
# fingerprint is left describing a walk nobody can reproduce.
RELATION_RULES = "2026-08-26"


@dataclass(frozen=True, slots=True)
class RelationPolicy:
    """How R is filled: which relations count, how much, and in what order they are believed.

    CURATION, and rows since policy v3 (`kind` = `relation_weight` · `curated_relation` ·
    `curation` · `curation_cue` · `curation_default`). The standing law names the relation weights
    explicitly — «the relation weights you write in T3: they land as rows from the start, never as a
    table in `config.py`» — and this is the shape they are read into.

    `weights` IS ORDERED, and the order is load-bearing twice over: it is the precedence the cell
    walk breaks ties by (two relations that both hold at the same absolute weight resolve to the one
    declared first, so a rebuild cannot flip a cell's provenance), and it is the order a reader meets
    them in. `curated` is the closed vocabulary a definitional edge may claim — closed on purpose: a
    curator who may invent a relation name per edge is writing prose, not a matrix.
    """

    #: `(relation, weight)` in declared order. Signed: `antonym` is negative, and the sign is the
    #: antonym column-read primitive rather than a convention about badness.
    weights: tuple[tuple[str, float], ...]
    #: `(relation, weight)` — what a CURATED edge may claim, and at what strength.
    curated: tuple[tuple[str, float], ...] = ()
    #: The back-reference a curated edge writes (the Captain's ruling of 2026-08-12). Zero means «no
    #: reciprocal cell», which is a real declaration and not an absence.
    reciprocal_weight: float = 0.0
    #: `(relation, (cue, ...))` in TRY order — how the miner guesses which relation a gloss states.
    #: A guess, never a claim: every proposal is pending until the Captain relabels or rejects it.
    cues: tuple[tuple[str, tuple[str, ...]], ...] = ()
    #: `(source POS, target POS, relation)` — the fallback when no cue fires.
    defaults: tuple[tuple[str, str, str], ...] = ()
    #: WHOSE LEMMA may state antonymy and derivation for a dimension — `synset` (every lemma of the
    #: synset) or `word` (only its own). The Captain ruled `word` standing on 2026-08-26, on the
    #: measured A/B; before that it was a constant in the adapter, and it is a row now because it is
    #: content: it decides 6,634 cells and 257 negatives and evidence is exactly what revised it.
    #: `None` for policy v3 and earlier, which never declared it — see `DictionaryConfig`.
    lemma_scope: str | None = None
    #: HOW A ONE-SIDED ANTONYMY IS READ — `stated` (what the resource wrote), `overwrite` (state the
    #: reverse always) or `add_only` (complete a pair only where R is silent, as its own relation
    #: `antonym_inferred`). The Captain ruled `add_only` standing on 2026-08-26: the bar cannot
    #: separate the three, so it was never a measurement question but whether this being may hold an
    #: opposition the resource never wrote down. `None` for policy v4 and earlier.
    antonym_symmetry: str | None = None

    def __post_init__(self):
        names = [name for name, _weight in self.weights]
        if len(set(names)) != len(names):
            raise ValueError(f"a relation is weighted twice: {sorted({n for n in names if names.count(n) > 1})}")
        curated = [name for name, _weight in self.curated]
        if len(set(curated)) != len(curated):
            raise ValueError("a curated relation is weighted twice")
        unknown = [rel for rel, _cues in self.cues if rel not in curated]
        unknown += [rel for _src, _dst, rel in self.defaults if rel not in curated]
        if unknown:
            raise ValueError(
                f"the curator's guess may only propose a relation from the closed set {curated}; "
                f"these are not in it: {sorted(set(unknown))}"
            )

    @property
    def relations(self) -> tuple[str, ...]:
        """The relations R fills cells with, in declared order."""
        return tuple(name for name, _weight in self.weights)

    def weight_of(self, relation: str) -> float:
        """The declared weight, or a refusal. There is no «unweighted relation counts zero» here:
        a relation the walk produced and the policy never named is a policy that does not describe
        the matrix it is about to be recorded beside."""
        for name, weight in self.weights:
            if name == relation:
                return weight
        raise ValueError(f"no declared weight for the relation {relation!r}")

    def curated_weight(self, relation: str) -> float:
        for name, weight in self.curated:
            if name == relation:
                return weight
        raise ValueError(f"{relation!r} is not one of the curated relations {[n for n, _ in self.curated]}")

    def precedence(self, relation: str) -> int:
        """Where the relation sits in the declared order — the cell walk's tie-break."""
        return self.relations.index(relation)

    def as_dict(self) -> dict:
        out = {
            "rules": RELATION_RULES,
            "weights": [[name, weight] for name, weight in self.weights],
            "curated": [[name, weight] for name, weight in self.curated],
            "reciprocal_weight": self.reciprocal_weight,
            "cues": [[rel, list(cues)] for rel, cues in self.cues],
            "defaults": [list(entry) for entry in self.defaults],
        }
        # Omitted when undeclared, on `DictionaryConfig.as_dict`'s argument and for the same
        # regression: v3 declared no scope and must keep hashing exactly as it did.
        if self.lemma_scope is not None:
            out["lemma_scope"] = self.lemma_scope
        if self.antonym_symmetry is not None:
            out["antonym_symmetry"] = self.antonym_symmetry
        return out


# ------------------------------------------------------------------------------------------------
# D's policy — what a definition contributes, and what a shared word is worth
# ------------------------------------------------------------------------------------------------

# The law of the GLOSS WALK, dated, for REDUCTION_RULES' reason and no other: the parameters below
# say how much an overlap counts, and this says what «these two dimensions share a word» means at
# all — a dimension's gloss is the definitions of ITS part of speech (`land.v` reads the verb), the
# tokens land through the same reduction the closure uses (every POS-aware reading, the name refusal
# applied, the stop list yielding to membership), and a dimension's own word is dropped from its own
# gloss because a definition that names its headword states nothing about two concepts.
#
# It is the mining seam R and the closure already share, aimed at a key instead of a word — which is
# the whole reason it is stated here rather than re-derived: a D that re-opened requirement 21 or the
# name refusal would be a second reduction of the same glosses, and no fingerprint could tell the two
# builds apart. Bump when the walk moves.
DISTRIBUTION_RULES = "2026-09-09"

#: The set measures a shared vocabulary may be scored by, over the shared and the two side masses.
#: FRAME — the shape of the question («how much of the two definitions is the same»); which one is
#: asked is a row.
MEASURES = ("jaccard", "dice", "cosine")

#: What one gloss word is worth. `uniform` = one word, one vote (the prototype's, and what a plain
#: Jaccard means). `idf` = log(N / df) over the base's own rows, so a word half the base uses says
#: almost nothing and a word two rows share says nearly everything.
WEIGHTINGS = ("uniform", "idf")

#: Which words a gloss's overlap is counted over. `base` = the closure's own words (the prototype's
#: reading — the base is the vocabulary it defines itself in); `lexicon` = every word the resource
#: knows, so a definition may share a word the base does not contain.
VOCABULARIES = ("base", "lexicon")

#: What D does with a word whose job in a sentence is STRUCTURAL. `admitted` = it counts like any
#: other shared word (every build before 2026-09-10); `compiled` = it is not part of the vocabulary
#: two definitions may be said to share, because the standing law says a function word is compiled
#: and never defined — and D asking whether two glosses both contain `in` is D defining one.
STRUCTURE_READINGS = ("admitted", "compiled")


@dataclass(frozen=True, slots=True)
class DistributionPolicy:
    """How D is filled: which senses write a definition, which of its words count, and what a
    shared vocabulary is worth.

    CURATION, and rows from the start (`kind` = `distribution`), for the same reason the relation
    weights are: «a category-2 set stated in code is a defect even when its contents are correct».
    Every field is REQUIRED — there is no default here for `ClosurePolicy`'s reason, and a D built
    under a value nobody declared is a matrix the manifest cannot vouch for.

    `senses` is D's own and not the closure's, though today they agree: the closure's cut decides
    which senses write a definition for MEMBERSHIP, and this decides which write one for the
    GEOMETRY. They are the same question asked of two different things, and a ruling may yet move
    one without the other.
    """

    #: `primary` (the first synset of the dimension's POS) or `all` (every reading of it).
    senses: SenseMode
    #: `base` or `lexicon` — see `VOCABULARIES`.
    vocabulary: str
    #: `jaccard`, `dice` or `cosine` — see `MEASURES`.
    measure: str
    #: `uniform` or `idf` — see `WEIGHTINGS`.
    weighting: str
    #: How many words two definitions must share before D says anything at all. One shared word is
    #: a coincidence at this scale (`in` alone joins a fifth of the base); the prototype asked two.
    min_shared: int
    #: The multiplier on the measure. Not cosmetic: the diagonal is a declared 1.0, so what the
    #: off-diagonal is worth AGAINST it is what decides every row cosine.
    scale: float
    #: The ceiling the scaled value saturates at.
    cap: float
    #: Below this the cell is not written. The noise floor, and — at this scale — the size rail.
    floor: float
    #: D's diagonal. A matrix whose diagonal is zero has no self-similarity and its cosines stop
    #: meaning what they look like; D declares its own rather than borrowing R's, because the two
    #: matrices are two geometries and only one of them has R's weights.
    identity: float
    #: `admitted` or `compiled` — see `STRUCTURE_READINGS`. Whether a closed-class form may be one
    #: of the words two definitions are counted as sharing. The forms themselves are NOT named here:
    #: they are the `closed_classes` rows migration 0004 wrote and they arrive injected, so this row
    #: says only what to DO with them.
    #:
    #: LAST in the field order and the only one with a default, because `None` means UNDECLARED —
    #: the treatment `reading` got when the mix arrived at v7. Policy versions 6 and 7 predate this
    #: question and must keep reading back and fingerprinting exactly as they always did, so
    #: `as_dict` omits an undeclared field entirely. A build that would be CHANGED by the answer is
    #: refused rather than quietly given one (`distribution.vocabulary_of`).
    structure: str | None = None

    def __post_init__(self):
        if self.senses not in ("primary", "all"):
            raise ValueError(f"unknown sense mode {self.senses!r}")
        if self.vocabulary not in VOCABULARIES:
            raise ValueError(f"unknown gloss vocabulary {self.vocabulary!r} — the two are {VOCABULARIES}")
        if self.measure not in MEASURES:
            raise ValueError(f"unknown overlap measure {self.measure!r} — the three are {MEASURES}")
        if self.structure is not None and self.structure not in STRUCTURE_READINGS:
            raise ValueError(
                f"unknown structure reading {self.structure!r} — the two are {STRUCTURE_READINGS}"
            )
        if self.weighting not in WEIGHTINGS:
            raise ValueError(f"unknown weighting {self.weighting!r} — the two are {WEIGHTINGS}")
        if self.min_shared < 1:
            raise ValueError("min_shared counts shared words; below one it is not a floor at all")
        if self.scale <= 0:
            raise ValueError("scale multiplies the measure; zero or less would erase D rather than shape it")
        if self.cap <= 0:
            raise ValueError("cap is the ceiling a scaled overlap saturates at, and it is positive")
        if self.floor < 0:
            raise ValueError("floor is a noise floor on an unsigned measure, never negative")
        if self.floor >= self.cap:
            raise ValueError(
                f"the floor ({self.floor}) is at or above the cap ({self.cap}): every cell D could "
                f"write would be refused, which is a policy that declares an empty matrix by "
                f"accident rather than on purpose"
            )

    def as_dict(self) -> dict:
        out = {
            "rules": DISTRIBUTION_RULES,
            "senses": self.senses,
            "vocabulary": self.vocabulary,
            "measure": self.measure,
            "weighting": self.weighting,
            "min_shared": self.min_shared,
            "scale": self.scale,
            "cap": self.cap,
            "floor": self.floor,
            "identity": self.identity,
        }
        # Omitted when undeclared, so v6's and v7's fingerprints do not move under a question they
        # never faced — the same rule `reading` follows on `DictionaryConfig`.
        if self.structure is not None:
            out["structure"] = self.structure
        return out


# ------------------------------------------------------------------------------------------------
# the DUAL READ's policy — how loudly the second geometry speaks when one number is wanted
# ------------------------------------------------------------------------------------------------

# The law of the DUAL READ, dated, for REDUCTION_RULES' reason and no other: `mix` says how much of
# D a reader hears, and this says what «read R and D together» means at all — the two rows are
# CONCATENATED into one sparse vector over 2n prefixed columns (`r/eat.v` and `d/eat.v` are two
# different axes), D's half is scaled by `mix`, and one cosine is taken over the whole of it. Nothing
# is averaged with anything, neither matrix is rewritten, and `mix = 0` is R alone.
#
# The shape is not cosmetic and the review measured why: averaged into one float, a positive gloss
# overlap CANCELS a stated opposition instead of sitting beside it, and `enter~leave` reads +0.519
# where R states -0.331. Concatenated, R's sign survives as long as `mix` leaves it room — which is
# what the ruled value buys, and what a reader has to be able to check a build was measured under.
# Bump this when the shape of the read moves; the parameter itself is a row and moves on its own.
READING_RULES = "2026-09-09"


@dataclass(frozen=True, slots=True)
class ReadingPolicy:
    """How R and D are read TOGETHER. Neither matrix's policy, and that is why it is its own object.

    CURATION, and a row from its first day (`kind` = `reading`). It was deliberately kept out of
    policy v6 — «measured at T4 and ruled by the Captain before it can be a row at all» — and v7 is
    the ruling: `mix` = 0.5, measured (see `db/0010`).

    Its own object rather than a bare float on `DictionaryConfig` for one reason, and it is the
    reason `REDUCTION_RULES` exists: a parameter travels with the LAW it is applied under. A number
    in the config with no `rules` beside it could have the shape of the read change underneath it —
    concatenation becoming an average, say — and two builds would present the same fingerprint for
    two different geometries. `RelationPolicy` and `DistributionPolicy` each carry their walk's date
    for exactly this, and the dual read is the third walk.

    ONE FIELD TODAY, and not for long: the acceptance floors the bar is scored against are T5's and
    the Captain's, and they are the same category — a reading of two matrices rather than a property
    of either. They land here when they are ruled.
    """

    #: How loudly D speaks: D's columns are scaled by this before the cosine. `0.0` is R alone and
    #: is a real declaration, not an absence — «the dual read is R» is a thing a policy may say.
    mix: float

    def __post_init__(self):
        if self.mix < 0:
            raise ValueError(
                f"a negative mix ({self.mix}) would flip every D cell's sign. D is unsigned by "
                f"construction — the sign is R's alone, and it is the antonym column-read primitive."
            )

    def as_dict(self) -> dict:
        return {"rules": READING_RULES, "mix": self.mix}


@dataclass(frozen=True, slots=True)
class DictionaryConfig:
    """The whole declared policy for one build. Hash it, record the hash, then measure.

    Assembled from rows by `tk2.dictionary.policy.config_from_rows`. Still a plain value object with
    no database anywhere near it — that is the seam: the rows are somebody else's door, and this is
    what the engine is handed.

    `relations` and `alphabet` arrived with policy v3 and are OPTIONAL for one reason, stated here
    because it decides how `as_dict` behaves: `dictionary_policy` is a LEDGER, v1 and v2 are still
    readable, and neither of them declared either thing. A config assembled from those rows has
    nothing to say about relations, and must not invent a default to say it with.
    """

    closure: ClosurePolicy
    declared_seeds: tuple[str, ...]
    bar: tuple[BarPair, ...]
    #: R's weights and the curator's vocabulary. `None` for a policy version that predates them.
    relations: RelationPolicy | None = None
    #: Which parts of speech exist (`keys.Alphabet`). `None` for v1 and v2, which left it in code.
    alphabet: keys.Alphabet | None = None
    #: D's gloss walk. `None` for v1–v5, which declared no D — and that absence is readable rather
    #: than fatal for the same ledger reason `relations` is: the base T3 measured was built under a
    #: policy that had nothing to say about D, and re-reading it must stay possible.
    distribution: DistributionPolicy | None = None
    #: How the two geometries are read TOGETHER. `None` for v1–v6, which declared no dual read — and
    #: v6 declared none ON PURPOSE (the mix was a measurement until the Captain ruled it), so the
    #: absence is a record of where the ruling sits in time and not an omission.
    reading: ReadingPolicy | None = None

    @property
    def seeds(self) -> tuple[str, ...]:
        """The seeds that actually run: the declared families, then the bar's own words, then the
        run's extras — deduplicated, order preserved. Requirement 12 in code (see the module head)."""
        out: list[str] = []
        for word in (*self.declared_seeds, *bar_words(self.bar), *self.closure.extra_seeds):
            w = keys.normalize_word(word)
            if w not in out:
                out.append(w)
        return tuple(out)

    def as_dict(self) -> dict:
        """The canonical form the fingerprint is taken over — and the form the manifest stores, so a
        later reader can diff two builds' policies instead of trusting two hashes to differ.

        WHAT IS NOT DECLARED IS NOT WRITTEN, and that is deliberate rather than tidy: a policy
        version that never mentioned the relation weights hashes exactly as it did before the
        weights existed, so the claim «v1 and v2 are the policies they always were» stays true and
        machine-checkable across the move. A `"relations": null` would have moved both of their
        fingerprints and broken every manifest row that names one.
        """
        out = {
            "reduction_rules": REDUCTION_RULES,
            "closure": asdict(self.closure),
            "declared_seeds": list(self.declared_seeds),
            "seeds": list(self.seeds),
            "bar": [asdict(p) for p in self.bar],
        }
        if self.relations is not None:
            out["relations"] = self.relations.as_dict()
        if self.alphabet is not None:
            out["alphabet"] = self.alphabet.as_dict()
        if self.distribution is not None:
            out["distribution"] = self.distribution.as_dict()
        if self.reading is not None:
            out["reading"] = self.reading.as_dict()
        return out

    def fingerprint(self) -> str:
        """sha256 over the canonical JSON, sorted keys, no whitespace slack. Two builds with the
        same fingerprint were measured under the same policy; that is the whole claim.

        NOTE what is deliberately NOT in here: the policy and bar ROW versions. This hashes the
        policy as the engine received it, and it must keep answering the same hash for the same
        values however they were assembled — that is what makes «the move to rows changed nothing»
        a checkable statement rather than a promise. Which rows a build read is recorded beside this
        in the manifest, by `tk2.dictionary.policy`'s own two fingerprints.
        """
        blob = json.dumps(self.as_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def with_closure(self, **changes) -> "DictionaryConfig":
        """A variant, for the runs that argue with the standing policy. It is a NEW config with a
        new fingerprint — which is the point: a depth-3 run cannot be mistaken for a depth-2 one."""
        return replace(self, closure=replace(self.closure, **changes))

    def with_distribution(self, **changes) -> "DictionaryConfig":
        """A variant of D's walk — the shape every measurement of it takes, and the same argument:
        a run that halved the scale cannot be mistaken for the declared one."""
        if self.distribution is None:
            raise ValueError(
                "this policy declares no D, so there is nothing to vary. Policy v6 (db/0009) is "
                "what declares the gloss walk."
            )
        return replace(self, distribution=replace(self.distribution, **changes))

    def with_reading(self, **changes) -> "DictionaryConfig":
        """A variant of the dual read — how the OTHER blends are measured now that one is standing.

        Same argument as the two above, and it is the one the mix needed most: the sweep that found
        0.5 has to stay runnable, and every row of it must carry a fingerprint that says out loud it
        is not the ruled reading.
        """
        if self.reading is None:
            raise ValueError(
                "this policy declares no dual read, so there is nothing to vary. Policy v7 "
                "(db/0010) is what declares the mix."
            )
        return replace(self, reading=replace(self.reading, **changes))
