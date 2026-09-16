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

    FOUR THINGS MOVE IT, and the last two are the ones that would have been missed:

      - the BUILD LABEL, when a new base is applied beside the old;
      - the SEAL FINGERPRINTS, when a matrix's content changes under the same label — which is
        exactly what an approved curated edge does, since `approve` re-seals;
      - the POLICY VERSION, when a ruling changes the reading without touching a single cell. That
        happened the day this was written: the NEAR floor moved from +0.27 to +0.28 and every
        verdict in the space changed while every matrix stayed identical.
      - **the CLOSED-CLASS VERSION** *(added 2026-09-16, before it cost anything)*. The closed-class
        forms are a STRUCTURE FILTER on D's vocabulary — `distribution.vocabulary` drops them,
        because *«a function word is compiled and never defined»* and two glosses sharing `in` is D
        defining one. So a closed-class migration changes what D WOULD be built from, and until this
        field existed nothing recorded which set a sealed base had actually been filtered by. **The
        drift would have been silent**: the base keeps its label and its seals, the table moves
        underneath it, and no check anywhere disagrees.

        It is recorded rather than enforced, and that is the point. A table may legitimately move
        ahead of a base — E3 wrote four closed-class versions in one day without a rebuild, and each
        was correct. What must never happen is that the two disagree and nobody can SEE it.

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
    #: The closed-class version whose forms filtered D's vocabulary at build time. `None` on a space
    #: loaded by a caller that did not say — honest, and distinguishable from «version 0».
    closed_class_version: int | None = None

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
        if self.closed_class_version != other.closed_class_version:
            moved.append(f"closed classes v{self.closed_class_version} -> "
                         f"v{other.closed_class_version} — D's vocabulary filter moved, so this "
                         f"base was built against a different set of function words")
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
    #: The relation that set the stated cell, when there is one — «every answer naming its source»
    #: taken one step further than the layer: which CLAIM answered, not merely which matrix.
    relational_relation: str = ""

    @property
    def relational_speaks(self) -> bool:
        return self.source == SOURCE_RELATIONAL


@dataclass(frozen=True, slots=True)
class Projection:
    """A sense read as a vector in the base's space, WITH the half it was read from.

    The source is not decoration: since the ruling of 2026-09-14 a sense is placed by its RELATIONS
    where it states any and by its DISTRIBUTION where it does not, so the caller cannot know which
    half answered unless the answer says. And the vector must be ranked in the half it came from —
    see `neighbours_of_vector`.
    """

    vector: object
    source: str


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
        self._relational_cells: dict[tuple[str, str], tuple[float, str]] = {}
        self._distributional_cells: dict[tuple[str, str], float] = {}

        reading = config.reading
        for row in relation_rows:
            i = self._index.get(row["key"])
            if i is None:
                continue
            stated = []
            for cell in row.get("cells", ()):
                j = self._index.get(cell["column"])
                if j is None:
                    continue
                relation = cell.get("rel", "")
                # REFERENCE CELLS ARE CLAIMS ABOUT A PAIR, NOT STATEMENTS ABOUT A PROFILE, so they
                # are recorded and kept out of the cosine. Measured (E1d T3): with them in, and the
                # reciprocal on, `land.n~land.v`, `state.n~state.v` and `play.n~play.v` all flip to
                # a wrong NEAR, because reciprocal references inflate POS-sibling profiles.
                if reading is None or reading.enters_the_cosine(relation):
                    relational[i, j] += cell["w"]
                if relation != "identity":
                    stated.append((cell["column"], relation, float(cell["w"])))
                    self._relational_cells[(row["key"], cell["column"])] = (
                        float(cell["w"]), relation)
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
        relational_cell, relation = self._relational_cells.get((left, right), (0.0, ""))
        distributional_cell = self._distributional_cells.get((left, right), 0.0)

        # THE CELL IS ASKED BEFORE THE COSINE — requirement 19, which says a verdict reads BOTH, and
        # which this module honoured only halfway until policy v12: the cell decided whether R spoke
        # and never what it said. That is why `eat.v -> food.n` could be a STATED claim and still
        # abstain, and closing it is what finally satisfies requirement 2.
        #
        # A structural relation may not decide: `derivational` states «same root», not «same
        # meaning» — it is exactly why `land.n~land.v`, `compass.n~compass.v` and `play.n~play.v`
        # are declared FAR and read positive — and `gloss_reference_ambiguous` is a claim about one
        # of several readings that the gloss itself does not choose between.
        if relational_cell != 0.0 and reading.decides_by_cell(relation):
            verdict = "FAR" if relational_cell < 0 else "NEAR"
            return Reading(
                left=left, right=right,
                relational_cell=relational_cell, relational_cosine=relational_cosine,
                relational_relation=relation,
                distributional_cell=distributional_cell,
                distributional_cosine=distributional_cosine,
                verdict=verdict, source=SOURCE_RELATIONAL, proposal=None,
            )

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
            relational_relation=relation,
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
                   source: str = SOURCE_RELATIONAL) -> list[Neighbour]:
        """The nearest dimensions to this one — «memory proposes by cosine» (brain req. 12).

        **R PROPOSES, AND THERE IS NO FALLBACK** (the Captain's ruling, 2026-09-14). Brain req 12
        says memory proposes by cosine; it does not say whose, and D's was benched and cannot rank.
        Measured over 300 sampled keys against gold (synonyms + same-hypernym siblings): D 5.9%
        precision@10 with 36.6% junk, R 28.7% with 9.8% — and NO variant of D helps, because D's
        cosine asks «which common gloss word do you contain» and `eat.v` shares 49 of its ~50
        columns with `lead.v` and `bring.v` on the word «take».

        **Where R is silent, nothing is proposed.** That is 14 of 4,555 dimensions (0.3%), and the
        fallback it replaces was offering them cosines of +0.000 — an arbitrary ordering of zeros
        dressed as an answer. An abstention is honest; a wrong proposal is not.

        `source` is kept because «what does the resource STATE around this key» and «whose
        definitions look like this one» are two real questions, and D still answers the second.
        Nothing DEFAULTS to it any more.

        One matrix-vector product and a partial sort: ~2 ms at 4,555 dimensions. The key itself is
        dropped, because a thing being nearest to itself is a property of the identity axis rather
        than an answer.
        """
        i = self._index.get(key)
        if i is None:
            return []
        if source == SOURCE_RELATIONAL and not self._relations.get(key):
            # R states nothing about this dimension, so it proposes nothing. The identity axis is
            # not an answer about a pair, which is why the STATED relations are what is asked.
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

        # R ONLY, NO FALLBACK — the same ruling as `neighbours`, so this module has ONE procedure
        # rather than two. STATED relations, not the raw row: every row carries its own identity
        # axis, so a row that says nothing about anything else is still non-zero, and identity is a
        # property of being a dimension rather than an answer about a pair.
        #
        # THIS NARROWS «NEVER-MISS», and the narrowing is deliberate. The catch used to name an
        # anchor whatever happened — falling back to D where R was silent — but D's cosines there
        # are +0.000, so «the nearest» was `argmax` over zeros: the first candidate, dressed as a
        # measurement. `None` is the honest answer, and it joins the two refusals already here
        # (the key is not a dimension; no anchor is).
        if not self._relations.get(key):
            return None
        i = self._index[key]
        rows = np.array([self._index[a] for a in candidates])
        sims = self._relational[rows] @ self._relational[i]
        best = int(np.argmax(sims))
        reading = float(sims[best])
        return Neighbour(candidates[best], reading,
                         self._config.reading.verdict(reading), source=SOURCE_RELATIONAL)

    def projection(self, sense: str, source: str | None = None) -> Projection | None:
        """One SENSE as a unit vector in the base's space, NAMING the half it was read from.

        **R FIRST, D WHERE THE SENSE STATES NO RELATIONS** — the Captain's ruling of 2026-09-14,
        and it is deliberately NOT the rule `neighbours` follows. That one refuses its fallback
        because the fallback was worth nothing: R is silent on 14 of 4,555 dimensions and D's
        cosines there are +0.000. Here the trade is real. `place` exists for words the base does not
        contain — 85.7% of senses are of such words — and of those, relations place **56.3%** where
        the distribution places **94.5%**, so relations-only would leave **43.7% unplaceable**.

        Measured over 400 out-of-base senses against gold (the base keys the sense IS or IS-A-KIND-OF):
        distribution **4.0% prec@5 / 18.8% hit@5** · relations **15.6% / 60.5%** · this rule
        **at 96.6% coverage**. Relations are three times better and D is NOT zero — so the honest
        move is to LABEL the weaker answer rather than refuse it, which is what `source` is for and
        what requirement 10 asks for in its own words: *every answer names its source.*

        THE GAP THIS CLOSES, found by probing the layer above: `nearest_anchor` could only start
        from a key that was already a dimension, and the semantic catch exists for ARBITRARY input.
        `devour.v` is not one of the 4,555 — most words are not — so before E1c the space had
        nothing to say about it, and «never rely on a fixed dictionary» would have been a promise the
        dictionary could not keep.

        Pass `source` to force one half and get `None` when it is mute — that is how a caller asks
        «place this by what its synset STATES» and accepts silence for an answer.
        """
        reading = self._by_sense.get(sense)
        if reading is None:
            return None
        wanted = (SOURCE_RELATIONAL, SOURCE_DISTRIBUTIONAL) if source is None else (source,)
        for half in wanted:
            vector = np.zeros(len(self._keys), dtype=np.float32)
            if half == SOURCE_RELATIONAL:
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
            if norm:
                return Projection(vector / norm, half)
        return None

    def project(self, sense: str, source: str | None = None) -> np.ndarray | None:
        """`projection` without the label — for a caller that already knows which half it asked for.

        Prefer `projection`: a vector whose half is not carried alongside it is a vector that can be
        ranked in the wrong space, which is the defect this pair was written to make impossible.
        """
        found = self.projection(sense, source)
        return None if found is None else found.vector

    def place(self, word: str, count: int = 12) -> dict[str, list[Neighbour]]:
        """Every reading of a word, each placed among the base's dimensions, each naming its half.

        The station's real question about an unknown word — not «which dimension is this» (it may be
        none) but «where does each of its readings sit». `devour` is not a dimension and its senses
        land squarely next to `eat.v`, which is the whole argument for a layer that rides on the base
        rather than a base that tries to contain everything.

        Each reading is ranked IN THE HALF IT WAS PROJECTED FROM (`projection` picks the half), so
        the `source` on every neighbour is a true statement about how that answer was reached.
        """
        out: dict[str, list[Neighbour]] = {}
        for sense_key in sorted(self._senses_by_word.get(keys.normalize_word(word), ())):
            found = self.projection(sense_key)
            out[sense_key] = ([] if found is None else
                              self.neighbours_of_vector(found.vector, count, source=found.source))
        return out

    def neighbours_of_vector(self, vector, count: int = 12,
                             source: str = SOURCE_DISTRIBUTIONAL) -> list[Neighbour]:
        """The nearest dimensions to an arbitrary vector — what `place` and the catch both need.

        Separate from `neighbours` because the caller may hold a vector that is not a row of this
        matrix at all: a projected sense today, a zip's own point when E2 lands.

        **IT RANKS IN THE HALF IT IS TOLD**, and that is a correctness property rather than an
        option. This used to rank everything in D. A relations-projected sense read against D's
        columns asks «whose DEFINITION mentions the words this synset is RELATED to» — a
        cross-space question whose top hit is carried by D's identity axis, and it measured worse:
        `devour.v.01` («destroy completely») returned `fail.v, compulsion.n, spots.n` crossed and
        **`ruin.v, destroy.v, defeat.v, overcome.v`** in its own space (15.6% prec@5 against 13.3%).
        Ranking a vector somewhere other than where it came from also makes its `source` label a
        false statement, which is the one thing requirement 10 forbids.
        """
        if vector is None:
            return []
        # Likewise a proposal: any word reaches the space through its senses, and
        # what comes back are candidates, never verdicts.
        space = self._relational if source == SOURCE_RELATIONAL else self._distributional
        sims = space @ vector
        take = min(count, len(self._keys))
        best = np.argpartition(-sims, take - 1)[:take]
        return [
            Neighbour(self._keys[i], float(sims[i]), self._config.reading.verdict(float(sims[i])),
                      source=source)
            for i in best[np.argsort(-sims[best])]
        ]

    def nearest_anchor_of_vector(self, vector, anchors, source: str = SOURCE_DISTRIBUTIONAL):
        """The nearest of a NAMED anchor set to an arbitrary vector — the catch, for a word that is
        not a dimension and had to reach the space through one of its senses.

        Here rather than in the bench because the bench had been reaching into `_distributional` and
        `_index` to do it by hand, which is how a caller ends up ranking in the wrong half without
        anyone noticing.
        """
        held = [a for a in anchors if a in self._index]
        if vector is None or not held:
            return None
        space = self._relational if source == SOURCE_RELATIONAL else self._distributional
        rows = np.array([self._index[a] for a in held])
        sims = space[rows] @ vector
        best = int(np.argmax(sims))
        reading = float(sims[best])
        if reading == 0.0:
            # NOTHING was measured: this vector and every anchor share no column at all, so
            # `argmax` is returning whichever anchor was listed first. That is the defect the
            # proposer ruling removed from `nearest_anchor` and it must not come back through the
            # door the senses opened. A negative reading is kept — that is R's own sign, and real.
            return None
        return Neighbour(held[best], reading, self._config.reading.verdict(reading), source=source)

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
