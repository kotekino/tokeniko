"""THE DICTIONARY AS THE ENGINE ASKS IT — the query layer, and the answer to a measured problem.

tk1 held one dense square matrix and got every question for free. tk2 holds sparse rows in mongo,
which is right for a base of 4,555 dimensions and 525,000 cells that a deploy writes and the body
only reads — and it is wrong for the ONE question the brain asks most: «what is near this?».

MEASURED against the body over the network, 2026-09-10, because the shape of this module is a
consequence of the numbers and not a preference:

  - one row by key ......................      6.8 ms   (a round trip; fine for a lookup)
  - every D row .........................  1,040 ms     (63 MB on the wire)
  - the SPARSE TRICK ....................  1,422 ms     and it returns 53% OF THE BASE

That third line is the finding. Only rows sharing a column with X can have a nonzero cosine to X, so
the textbook move is to ask mongo for those rows and score just them. It does not work here: D is so
broadly connected that `eat.v` shares a column with 2,418 of the 4,555 dimensions. You read half the
matrix to avoid reading all of it, and pay an unindexed multikey scan for the privilege.

So the dictionary is held DENSE AND IN MEMORY: 83 MB of float32, 1.2 s to build, and then

  - neighbours of a key .................      1.58 ms  (one matrix-vector product)

WHICH IS NOT THE R-CACHE, and the difference is deliberate. The r-cache snapshots every registered
r-collection WHOLE on every slow tick, which is why the base was kept out of it from E0: a 63 MB
re-read every sixty seconds is not a cache, it is a leak. The dictionary changes only when a build
writes it, and a build is a deploy — so this loads ONCE and never refreshes. If it ever needs to
notice a new build without a restart, that is a ruling and an epoch column, not a shorter timer.

THE BLEND IS PRE-COMPUTED, and that is the second consequence. The ruled reading is R's columns
concatenated with D's scaled by `mix` — but a concatenation is only ever read through a cosine, and
the cosine of two concatenated vectors is the cosine of one summed vector when the halves share a
key space, which R and D do BY CONSTRUCTION (`assert_square` holds it). So the two matrices become
one array at load and every later question is arithmetic.

WHAT IT DOES NOT DO: it does not judge. The verdict function is the POLICY's
(`ReadingPolicy.verdict`), it arrives with the config, and this module calls it rather than owning a
threshold — the standing law of 2026-08-25 put acceptance floors in rows, and a number in here would
be exactly the quieter of two declarations.
"""

from dataclasses import dataclass

import numpy as np

from tk2.dictionary import keys
from tk2.dictionary.config import DictionaryConfig


@dataclass(frozen=True, slots=True)
class SpaceOrigin:
    """WHAT A LOADED SPACE WAS BUILT FROM — and therefore what would make it stale.

    THE DIRTY-CHECK, and the Captain's ruling of 2026-09-10 behind it. The first design said «load
    once at boot, never refresh», on the argument that the dictionary only changes when a build
    writes it and a build is a deploy. That was wrong, and the Captain named the reason: the CURATION
    pipeline writes cells into R by his own hand (`tools/curate_dictionary.py approve`) without any
    rebuild, so a load-once space would never see an edge he had approved until somebody restarted
    the body — which is precisely the defect the r-cache exists to prevent.

    But a timer is wrong too, and that is the other half of his ruling: reloading is seven seconds
    and eighty-three megabytes. Seven seconds is not a tick. So the check is cheap and frequent and
    the RELOAD is a phase — «as brain activity» — which is where the blueprint already re-derives
    the figurative layer (tkzip req 16). The reload itself waits for E6, when there is a sleep phase
    to hang it on; what exists today is the ability to KNOW, which turns a silent staleness into a
    visible one.

    THREE THINGS MOVE IT, and the third is the one that would have been missed:

      - the BUILD LABEL, when a new base is applied beside the old;
      - the SEAL FINGERPRINTS, when a matrix's content changes under the same label — which is
        exactly what an approved curated edge does, since `approve` re-seals;
      - the POLICY VERSION, when a ruling changes the reading without touching a single cell. That
        happened the day this was written: the NEAR floor moved from +0.27 to +0.28 and every
        verdict in the space changed while every matrix stayed identical.

    MEASURED, and the second number is the one a tick has to plan for: the check costs 7-12 ms warm
    against the body, and it SPIKES to 100-215 ms on network jitter — the body is a machine on the
    other side of a wifi link, not a socket. Cheap in cpu and unreliable in latency, so whatever
    runs it must tolerate a slow answer rather than block on a fast one. That is E6's problem and it
    is written here so E6 does not discover it.
    """

    build: str
    #: `(matrix name, fingerprint)` pairs, sorted — the seals as they stood at load.
    seals: tuple[tuple[str, str], ...] = ()
    #: The policy version the space reads through. A ruling moves this and nothing else.
    policy_version: int | None = None

    def differs_from(self, other: "SpaceOrigin") -> tuple[str, ...]:
        """WHAT changed, not merely whether — a phase deciding to spend seven seconds deserves the
        reason, and a log line saying «stale» explains nothing to whoever reads it later."""
        moved = []
        if self.build != other.build:
            moved.append(f"build {self.build!r} -> {other.build!r}")
        if self.seals != other.seals:
            mine, theirs = dict(self.seals), dict(other.seals)
            for name in sorted(set(mine) | set(theirs)):
                if mine.get(name) != theirs.get(name):
                    moved.append(f"{name} reseal "
                                 f"{str(mine.get(name))[:12]} -> {str(theirs.get(name))[:12]}")
        if self.policy_version != other.policy_version:
            moved.append(f"policy v{self.policy_version} -> v{other.policy_version}")
        return tuple(moved)


#: Which layer an answer came from. Requirement 10: «every answer naming its source».
SOURCE_RELATIONAL = "relational"
SOURCE_DISTRIBUTIONAL = "distributional"
#: R had nothing to say. Not an error and not a shrug — a DIAGNOSIS, and the one E1d T3 must fix.
SOURCE_SILENT = "silent"


@dataclass(frozen=True, slots=True)
class Reading:
    """What both layers say about one pair, APART, each naming itself.

    Four numbers rather than one, because requirement 19 asks for both the cosine AND the stated
    cell on each side — the first curation round flipped a cell read while the cosine stayed mute,
    and a cosine-only verdict would have called that curation useless.

    `verdict` is R's, always. `proposal` is what D WOULD have said, present only where R is silent,
    and it is NOT a verdict: where R says nothing, D cannot separate a declared NEAR from a declared
    FAR (`eat.v~hungry.a` reads 0.338 against `bed.n~cause.n` at 0.326, on identical cells of 0.5).
    A caller that promotes a proposal to a verdict is doing the thing the blend was doing.
    """

    left: str
    right: str
    relational_cell: float
    relational_cosine: float
    distributional_cell: float
    distributional_cosine: float
    verdict: str
    source: str
    proposal: str | None = None

    @property
    def relational_speaks(self) -> bool:
        return self.source == SOURCE_RELATIONAL


@dataclass(frozen=True, slots=True)
class Neighbour:
    """One answer to «what is near this», with the verdict the policy issues on it and the LAYER it
    came from — because an answer that does not name its source is the thing requirement 10 forbids."""

    key: str
    cosine: float
    verdict: str
    source: str = SOURCE_DISTRIBUTIONAL

    @property
    def is_near(self) -> bool:
        return self.verdict == "NEAR"


@dataclass(frozen=True, slots=True)
class SenseReading:
    """One sense of a dimension, as the station will read it: the definition it means, and what its
    own synset states. The base key can answer neither — it is every reading at once."""

    key: str
    base: str
    ordinal: int
    synset: str
    definition: str
    relations: tuple[tuple[str, str, float], ...] = ()


class DictionarySpace:
    """The base, dense and in memory, with the operations the engine actually performs.

    Built from ROWS — the store hands them over, this holds no database. That seam is why the same
    object can be built from a live body, from a test fixture, or from a build nobody applied yet.
    """

    def __init__(self, config: DictionaryConfig, dimensions, relation_rows, distribution_rows,
                 sense_rows=(), origin: SpaceOrigin | None = None):
        self._config = config
        self._origin = origin
        self._keys = tuple(dimensions)
        self._index = {key: i for i, key in enumerate(self._keys)}

        size = len(self._keys)

        # TWO MATRICES, NEVER ONE. Requirement 10 has said since 2026-08-12 that R and D are
        # «consulted separately, every answer naming its source, never blended into one float», and
        # this module used to return `cos(R + mix*D)` in flat contradiction of it — found by the E1
        # audit of 2026-09-14 and ruled by the Captain the same day. Policy v11 declares the mode.
        relational = np.zeros((size, size), dtype=np.float32)
        distributional = np.zeros((size, size), dtype=np.float32)

        self._relations: dict[str, tuple[tuple[str, str, float], ...]] = {}
        #: The DIRECT cells, sparse. Requirement 19: a verdict reads both the cosine AND the stated
        #: cell, and the cosine alone would have called the first curation round useless. Sparse
        #: dicts rather than two more dense matrices — 4,555² float32 is 83 MB apiece.
        self._relational_cells: dict[tuple[str, str], float] = {}
        self._distributional_cells: dict[tuple[str, str], float] = {}

        for row in relation_rows:
            i = self._index.get(row["key"])
            if i is None:
                continue
            stated = []
            for cell in row.get("cells", ()):
                j = self._index.get(cell["column"])
                if j is None:
                    continue
                relational[i, j] += cell["w"]
                if cell.get("rel") != "identity":
                    stated.append((cell["column"], cell.get("rel", ""), float(cell["w"])))
                    self._relational_cells[(row["key"], cell["column"])] = float(cell["w"])
            self._relations[row["key"]] = tuple(stated)

        for row in distribution_rows:
            i = self._index.get(row["key"])
            if i is None:
                continue
            for cell in row.get("cells", ()):
                j = self._index.get(cell["column"])
                if j is not None:
                    distributional[i, j] += cell["w"]
                    self._distributional_cells[(row["key"], cell["column"])] = float(cell["w"])

        def _unit_of(matrix):
            norms = np.linalg.norm(matrix, axis=1, keepdims=True)
            # A silent row has no direction. Dividing by one keeps it at zero rather than at nan —
            # and zero is the honest answer: a dimension nothing reaches is near nothing.
            norms[norms == 0] = 1.0
            return matrix / norms

        self._relational = _unit_of(relational)
        self._distributional = _unit_of(distributional)
        self._resident_bytes = int(relational.nbytes + distributional.nbytes)

        self._senses: dict[str, list[SenseReading]] = {}
        self._by_sense: dict[str, SenseReading] = {}
        self._sense_distribution: dict[str, tuple[tuple[str, float], ...]] = {}
        #: word -> its sense keys. `place` asked this question by scanning all 120,475 senses and
        #: cost 37 ms for it; indexed at load it costs nothing, and the load already walks the rows.
        self._senses_by_word: dict[str, list[str]] = {}
        for row in sense_rows:
            reading = SenseReading(
                key=row["key"], base=row["base"], ordinal=row["ordinal"],
                synset=row["synset"], definition=row.get("definition", ""),
                relations=tuple(
                    (cell["column"], cell.get("rel", ""), float(cell["w"]))
                    for cell in row.get("relations", ())
                ),
            )
            self._senses.setdefault(row["base"], []).append(reading)
            self._by_sense[row["key"]] = reading
            # Kept apart from `relations` because they are scaled differently — the ruled mix is
            # about how loudly the DISTRIBUTIONAL floor speaks, and a sense has both floors too.
            self._sense_distribution[row["key"]] = tuple(
                (cell["column"], float(cell["w"])) for cell in row.get("distribution", ())
            )
            self._senses_by_word.setdefault(keys.word_of(row["base"]), []).append(row["key"])
        for readings in self._senses.values():
            readings.sort(key=lambda r: r.ordinal)

    # -- what it is ------------------------------------------------------------------------------

    @property
    def dimensions(self) -> tuple[str, ...]:
        return self._keys

    def stats(self) -> dict:
        return {
            "dimensions": len(self._keys),
            "resident_bytes": self._resident_bytes,
            "senses": len(self._by_sense),
            "bases_with_senses": len(self._senses),
            "mix": self._config.reading.mix,
            "mode": self._config.reading.mode if self._config.reading else None,
        }

    def holds(self, key: str) -> bool:
        return key in self._index

    @property
    def origin(self) -> SpaceOrigin | None:
        """What this space was loaded from, or `None` when nobody said — a space built from a test
        fixture has no provenance to check and must not pretend to one."""
        return self._origin

    def is_stale(self, current: SpaceOrigin) -> bool:
        """Whether the rows have moved since this space was built. One cheap read decides it.

        `False` when the space has no origin: a space that cannot know is not the same thing as a
        space that is current, and the honest answer for «should I reload» is «you never told me
        what I am» — which a caller holding no origin already knows.
        """
        return bool(self._origin) and bool(self._origin.differs_from(current))

    def staleness(self, current: SpaceOrigin) -> tuple[str, ...]:
        """WHY it is stale, for the phase that has to justify seven seconds."""
        return self._origin.differs_from(current) if self._origin else ()

    # -- the operations the engine performs ------------------------------------------------------

    def resolve(self, word: str) -> tuple[str, ...]:
        """A surface word to the dimensions it occupies — the station's first question.

        A word is several dimensions when it is several parts of speech (`land` is `land.n` and
        `land.v`), and ALL of them come back: which one a sentence meant is the parser's to decide
        and the geometry's to inform, never this function's to guess.
        """
        found = keys.normalize_word(word)
        return tuple(key for key in self._keys if keys.word_of(key) == found)

    def relational(self, left: str, right: str) -> float | None:
        """R's cosine — what the RESOURCE STATES about these two, and nothing else.

        `None` rather than 0.0, and the difference is load-bearing: «these two are unrelated» and «I
        have never heard of one of these» are different answers, and a caller that could not tell
        them apart would be treating ignorance as evidence.
        """
        i, j = self._index.get(left), self._index.get(right)
        if i is None or j is None:
            return None
        return float(self._relational[i] @ self._relational[j])

    def distributional(self, left: str, right: str) -> float | None:
        """D's cosine — what their DEFINITIONS SHARE. A proposal. Never a verdict."""
        i, j = self._index.get(left), self._index.get(right)
        if i is None or j is None:
            return None
        return float(self._distributional[i] @ self._distributional[j])

    def read(self, left: str, right: str) -> Reading | None:
        """BOTH LAYERS, APART, EACH NAMING ITSELF — the shape requirement 10 asked for.

        The procedure, ruled 2026-09-14 and declared by policy v11:

          **R is asked first.** Where R speaks — a stated cell, or any cosine at all — R DECIDES, and
          the reading names R as its source. **Where R is silent the verdict is ABSTAIN**, and D's
          number comes back beside it as a `proposal` that no caller may promote.

        Measured rather than preferred. R alone decides 15 of the 18 bar pairs it speaks on, and its
        one failure mode is the `derivational` edge (requirement 16, open). Where R is silent, D
        cannot separate a declared NEAR from a declared FAR: `eat.v~hungry.a` (NEAR) reads 0.338 and
        `bed.n~cause.n` (FAR) reads 0.326 on identical cells, and 7 of 8 declared NEARs sit at or
        below the highest declared FAR. **D may propose and may never decide.**
        """
        if left not in self._index or right not in self._index:
            return None
        reading = self._config.reading
        if reading is None or not reading.reads_separately:
            raise ValueError(
                "this policy does not declare `mode = separate`, so the two matrices have no ruled "
                "way of being read apart. Policy v11 (db/0003) is what rules it — and a default in "
                "code would be exactly the reading the manifest cannot vouch for."
            )

        relational_cosine = self.relational(left, right)
        distributional_cosine = self.distributional(left, right)
        relational_cell = self._relational_cells.get((left, right), 0.0)
        distributional_cell = self._distributional_cells.get((left, right), 0.0)

        speaks = relational_cell != 0.0 or relational_cosine != 0.0
        if speaks:
            verdict, source, proposal = reading.verdict(relational_cosine), SOURCE_RELATIONAL, None
        else:
            # R has nothing to say. That is a DIAGNOSIS, not a shrug — and it is what T3 has to fix.
            verdict, source = "ABSTAIN", SOURCE_SILENT
            proposal = reading.verdict(distributional_cosine)

        return Reading(
            left=left, right=right,
            relational_cell=relational_cell, relational_cosine=relational_cosine,
            distributional_cell=distributional_cell, distributional_cosine=distributional_cosine,
            verdict=verdict, source=source, proposal=proposal,
        )

    def verdict(self, left: str, right: str) -> str:
        """NEAR, ABSTAIN or FAR — R's verdict, or ABSTAIN when R is silent or the key is unknown.

        ABSTAIN covers «not a dimension» too: the same answer for a different reason, and the right
        one either way, because the geometry has nothing to say.
        """
        reading = self.read(left, right)
        return "ABSTAIN" if reading is None else reading.verdict

    def neighbours(self, key: str, count: int = 12, floor: float | None = None,
                   source: str = SOURCE_DISTRIBUTIONAL) -> list[Neighbour]:
        """The nearest dimensions to this one — «memory proposes by cosine» (brain req. 12).

        DEFAULTS TO D, and that is the architecture rather than a convenience: proposing is exactly
        what D is for, and the verdict on any proposal is R's (`read`). Ask for `relational` to see
        what the resource STATES around a key — a different question, honestly answered.

        One matrix-vector product and a partial sort: ~1.6 ms at 4,555 dimensions. The key itself is
        dropped, because a thing being nearest to itself is a property of the identity axis rather
        than an answer.
        """
        i = self._index.get(key)
        if i is None:
            return []
        space = self._relational if source == SOURCE_RELATIONAL else self._distributional
        sims = space @ space[i]
        sims[i] = -np.inf
        take = min(count, len(self._keys) - 1)
        best = np.argpartition(-sims, take)[:take]
        out = []
        for position in best[np.argsort(-sims[best])]:
            reading = float(sims[position])
            if floor is not None and reading < floor:
                continue
            out.append(Neighbour(
                key=self._keys[position],
                cosine=reading,
                verdict=self._config.reading.verdict(reading),
                source=source,
            ))
        return out

    def nearest_anchor(self, key: str, anchors) -> Neighbour | None:
        """The closest of a small declared set — THE SEMANTIC CATCH.

        «Never rely on a fixed dictionary: map any input to the nearest of a small anchor set» is a
        standing decision, and this is the operation it needs. Manageable because the anchor set is
        small, never-miss because there is always a nearest — and the verdict rides along so a
        caller can tell «nearest, and genuinely near» from «nearest of a bad lot».
        """
        candidates = [a for a in anchors if a in self._index]
        if not candidates or key not in self._index:
            return None
        i = self._index[key]
        rows = np.array([self._index[a] for a in candidates])

        # THE SAME R-FIRST RULE AS `read`, so there is one procedure in this module and not two.
        # Where R speaks about this key it decides which anchor is nearest; where R is silent the
        # catch still has to name one — that is what «never-miss» means — and it names it from D,
        # saying so in `source` and leaving the verdict to say how much to trust it.
        # STATED relations, not the raw row: every row carries its own identity axis, so a
        # row that says nothing about anything else is still non-zero. Identity is a property
        # of being a dimension, never an answer about a pair.
        source = SOURCE_RELATIONAL if self._relations.get(key) else SOURCE_DISTRIBUTIONAL
        space = self._relational if source == SOURCE_RELATIONAL else self._distributional
        sims = space[rows] @ space[i]
        best = int(np.argmax(sims))
        reading = float(sims[best])
        return Neighbour(candidates[best], reading,
                         self._config.reading.verdict(reading), source=source)

    def project(self, sense: str, source: str = SOURCE_DISTRIBUTIONAL) -> np.ndarray | None:
        """One SENSE as a unit vector in the base's space — how a word outside the base gets in.

        THE GAP THIS CLOSES, found by probing the layer above: `nearest_anchor` could only start
        from a key that was already a dimension, and the semantic catch exists for ARBITRARY input.
        `devour.v` is not one of the 4,555 — most words are not — so before E1c the space had
        nothing to say about it, and «never rely on a fixed dictionary» would have been a promise the
        dictionary could not keep.

        A sense already carries cells over base dimensions: that IS a vector in this space, and
        projecting it is reading it as one. IT NAMES WHICH HALF IT IS READING, because a sense has
        both floors and folding them together here would be the blend rebuilt one layer down —
        exactly what policy v11 ruled out. `distributional` by default, because placing a word is a
        PROPOSAL; ask for `relational` to place it by what its synset states.
        """
        reading = self._by_sense.get(sense)
        if reading is None:
            return None
        vector = np.zeros(len(self._keys), dtype=np.float32)
        if source == SOURCE_RELATIONAL:
            for column, _relation, weight in reading.relations:
                j = self._index.get(column)
                if j is not None:
                    vector[j] += weight
        else:
            for column, weight in self._distribution_of(sense):
                j = self._index.get(column)
                if j is not None:
                    vector[j] += weight
        norm = float(np.linalg.norm(vector))
        return None if norm == 0 else vector / norm

    def place(self, word: str, count: int = 12) -> dict[str, list[Neighbour]]:
        """Every reading of a word, each placed among the base's dimensions.

        The station's real question about an unknown word — not «which dimension is this» (it may be
        none) but «where does each of its readings sit». `devour` is not a dimension and its senses
        land squarely next to `eat.v`, which is the whole argument for a layer that rides on the base
        rather than a base that tries to contain everything.
        """
        out: dict[str, list[Neighbour]] = {}
        for sense_key in sorted(self._senses_by_word.get(keys.normalize_word(word), ())):
            out[sense_key] = self.neighbours_of_vector(self.project(sense_key), count)
        return out

    def neighbours_of_vector(self, vector, count: int = 12) -> list[Neighbour]:
        """The nearest dimensions to an arbitrary vector — what `place` and the catch both need.

        Separate from `neighbours` because the caller may hold a vector that is not a row of this
        matrix at all: a projected sense today, a zip's own point when E2 lands.
        """
        if vector is None:
            return []
        # Likewise a proposal: any word reaches the space through its senses, and
        # what comes back are candidates, never verdicts.
        sims = self._distributional @ vector
        take = min(count, len(self._keys))
        best = np.argpartition(-sims, take - 1)[:take]
        return [
            Neighbour(self._keys[i], float(sims[i]), self._config.reading.verdict(float(sims[i])))
            for i in best[np.argsort(-sims[best])]
        ]

    def _distribution_of(self, sense: str):
        return self._sense_distribution.get(sense, ())

    def senses_of(self, base: str) -> tuple[SenseReading, ...]:
        """Every reading of a dimension, in the resource's own sense order — the WSD candidates.

        The question the station asks most, and the reason E1c exists: `bank.n` is every reading at
        once, and only its senses can say which one a sentence meant.
        """
        return tuple(self._senses.get(base, ()))

    def sense(self, key: str) -> SenseReading | None:
        return self._by_sense.get(key)

    def relations_of(self, key: str) -> tuple[tuple[str, str, float], ...]:
        """What R STATES about this dimension — the taxonomy walk, not the geometry.

        Separate from `similarity` on purpose: «the resource says X is a kind of Y» and «X and Y read
        near» are different claims, and the is_a graph is what gates taxonomy while cosine is what
        proposes candidates (`geometry-not-isa-validity`).
        """
        return self._relations.get(key, ())
