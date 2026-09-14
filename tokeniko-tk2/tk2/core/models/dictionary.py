"""THE DICTIONARY'S POLICY, AS ROWS — the standing law of 2026-08-25, applied to E1.

«A category-2 set stated in code is a defect even when its contents are correct.» The dictionary's
seeds, its closure cuts and its acceptance bar are CURATION — authorized judgment, grown
generated-then-curated, and never finished — so they live in the db, where iteration is possible,
and they arrive through the migration door like every other r-row.

Three tables, because they answer three different questions and carry three different ledgers:

  `dictionary_policy`  the declared policy, one row per entry. Versioned as a whole: a build reads
                       ONE version and records which. The row shape is (kind · family · name ·
                       value), deliberately generic, so the entry KINDS can grow — seeds and the
                       closure cuts today, the relation weights when T3 writes them — without a
                       schema change per kind. That genericity is the point of the table and not
                       laziness: a `seeds` column and a `weights` column would make every new kind
                       a migration against the SHAPE rather than against the content.

  `dictionary_bar`     the acceptance bar. Its own version counter, because it moves on a different
                       clock than the policy does — «eighteen pairs is a draft: each discovered
                       failure should add one». Rows are epoch-stamped (`created_at`) and
                       APPEND-MOSTLY, which is the property that justified moving the bar out of
                       code at all: git made «was this pair declared before that run?» human-
                       checkable, and these rows make it machine-checkable. `why` is carried
                       verbatim because it is EVIDENCE, not a comment.

  `dictionary_builds`  the manifest. One row per build, recording the policy version and
                       fingerprint AND the bar version and fingerprint it was measured against.

...and since T3 the base itself: `base_keys` (the dimension order), `base_r` (the relation matrix,
sparse, provenance per cell), — since T4 — `base_d` (the gloss-overlap matrix, over the very same
dimension order), and — since T5 — `base_seals`, the row that says a matrix arrived WHOLE. They are
`logic` like the rest — the body reads the base and never writes it — and they are described where
they are declared, at the foot of this file.

The reading seam: nothing here reads the database and nothing here computes a fingerprint. The pure
side (`tk2.dictionary.policy`) takes ROWS AS MAPPINGS — `model_dump()` output, or raw pymongo
documents, either works — exactly as the closure engine takes an injected gloss provider. That is
what keeps `tk2/dictionary/` free of mongo while the policy it runs on lives in mongo.
"""

from typing import Annotated, Any

from bunnet import Indexed
from pydantic import BaseModel, Field
from pymongo import ASCENDING, DESCENDING, IndexModel

from tk2.core.documents import LogicDocument
from tk2.core.mixins import Timestamped

# ------------------------------------------------------------------------------------------------
# the policy
# ------------------------------------------------------------------------------------------------


class DictionaryPolicyDoc(LogicDocument, Timestamped):
    """logic (r) — the declared policy of the dictionary build, one row per entry.

    Read by the build tool before it measures anything and fingerprinted into the manifest (tooling
    req. 4: policy before results). The body may read it; only a migration writes it.

    A NEW VERSION IS A NEW SET OF ROWS. Editing version 1 in place would destroy the claim the
    manifest makes — that a recorded fingerprint identifies the policy a past build actually ran —
    so a change to any entry is version 2 written whole, and version 1 stays readable beside it.
    """

    #: The policy version these rows belong to. A build reads exactly one.
    version: Annotated[int, Indexed()] = Field(ge=1)

    #: What kind of entry this is: `seed`, `closure`, and (T3) `relation_weight`. A string rather
    #: than an enum for the reason `reward_source` is one — the roster grows, and a kind that
    #: required a code change to exist would put the policy back in code.
    kind: str = Field(min_length=1)

    #: The entry's name within its kind: the seed word, the closure setting, the relation name.
    name: str = Field(min_length=1)

    #: The value, when the entry has one. A seed HAS no value — its declaration is its presence —
    #: and None says so rather than a `True` that means nothing.
    value: Any = None

    #: The group the entry was declared in, when its declaration was grouped — for a seed, the
    #: SOURCE that argued for it, which would be lost if the rows were a flat word list: one of
    #: requirement 8's purpose families (volitional · motion · effect · identity), which say what
    #: this being must be able to think about, or `structure` (policy v2 onward), which says the
    #: resource cannot define anything without the word. They are approved under different eyes, so
    #: a seed that could not name its source could not later be retired under either.
    family: str | None = None

    #: Declared order within (version, kind). Load-bearing for seeds: the seed list is a statement,
    #: it is hashed as a list, and mongo's natural order is not a promise anyone should lean on.
    position: int = Field(ge=0)

    #: Why this entry is here. Same argument as `ParamDoc.note`: these rows are read by human
    #: probes, and a curated value with no reason attached is a value nobody can later argue with.
    note: str = ""

    class Settings:
        name = "dictionary_policy"
        indexes = [
            # One entry per name per kind per version — two would make «the policy at version N»
            # ambiguous, which is the one thing the manifest's fingerprint promises it is not.
            IndexModel(
                [("version", ASCENDING), ("kind", ASCENDING), ("name", ASCENDING)], unique=True
            ),
        ]


# ------------------------------------------------------------------------------------------------
# the bar
# ------------------------------------------------------------------------------------------------


class DictionaryBarDoc(LogicDocument, Timestamped):
    """logic (r) — one expectation the base must meet, declared before it is measured.

    The bar was the hard case of the standing law, and the Captain dissolved it: the property wanted
    was never the MEDIUM (code, immutable-ish under git) but the LEDGER. So `version` is the bar
    version in which this pair ENTERED, `created_at` is when, and the bar is append-mostly — a pair
    that has to go is RETIRED (`retired_at`), never deleted, because a bar that can lose a row
    silently is a bar whose history means nothing.

    `a` and `b` are keys (`eat.v`) or bare words; `why` is the sentence that justified the pair when
    it was declared, kept verbatim.
    """

    version: Annotated[int, Indexed()] = Field(ge=1)

    a: str = Field(min_length=1)
    b: str = Field(min_length=1)

    #: `NEAR` or `FAR`. A string for the same reason `kind` is one — and because the verdict
    #: vocabulary is the bar's own, which E1 may yet widen (a `NEARER-THAN` is a real candidate).
    verdict: str = Field(min_length=1)

    #: Evidence, not a comment. It is what a later reader argues WITH when a pair looks wrong.
    why: str = Field(min_length=1)

    #: Declared order within the version, so a version's rows read back in the order they were
    #: written down — the bar is grouped by argument (the nearnesses, the effect axis, the POS
    #: collapse, the controls) and shuffling it loses the grouping.
    position: int = Field(ge=0)

    #: Unix seconds when the pair was retired, or None while it stands. The «mostly» in
    #: append-mostly, made a column: a retirement is a fact with a date, not an absence.
    retired_at: int | None = None

    class Settings:
        name = "dictionary_bar"
        indexes = [
            IndexModel(
                [("version", ASCENDING), ("a", ASCENDING), ("b", ASCENDING)], unique=True
            ),
        ]


class CuratedEdgeDoc(LogicDocument, Timestamped):
    """logic (r) — ONE analytic edge the Captain approved, as an INPUT to a build.

    --------------------------------------------------------------------------------------------
    WHY THIS COLLECTION EXISTS: two approved edges were lost, and no check could have saved them
    --------------------------------------------------------------------------------------------
    On 2026-08-12 the Captain approved two curated edges — `bed.n -> sleep.v` («furniture that
    provides a place to *sleep*») and `hungry.a -> eat.v` — with the authorization recorded on the
    cells and in the manifest. The E1 audit of 2026-09-14 found the built base carrying **zero
    curated cells**: `mined` 51,564, `axis` 4,555, `curated` 0.

    The cause is structural rather than an oversight. `curation.py` produced proposals, `cells_of`
    turned them into cells, and the cells went into R — so **a curated edge was an OUTPUT of a
    build and never an INPUT to one.** E1b dropped the prototype database, the rebuild regenerated R
    from WordNet, and the edges were simply not among the things being regenerated. A guard would
    have reported the loss; it could not have prevented it, because the decision had nowhere to live.

    **Outputs get regenerated. Inputs survive.** That is the whole of this file's argument.

    --------------------------------------------------------------------------------------------
    APPEND-MOSTLY, LIKE THE BAR
    --------------------------------------------------------------------------------------------
    An edge that has to go is WITHDRAWN (`withdrawn_at`), never deleted — the Captain's standing
    rule that a wrong belief is retreated and not erased, applied to his own rulings. A collection
    that can lose a row silently is a collection whose history means nothing, and this one exists
    precisely because something was lost silently once.

    `evidence` is the definition VERBATIM with the naming token marked (requirement 20): a
    paraphrase is the curator arguing rather than the dictionary speaking, and it is what a later
    reader argues WITH when an edge looks wrong.
    """

    source_key: Annotated[str, Indexed()] = Field(min_length=1)
    target_key: str = Field(min_length=1)

    #: The curated relation this edge claims, from the closed vocabulary the policy declares
    #: (`used_for`, `state_of`, …). A curator who may invent a relation per edge is writing prose.
    relation: str = Field(min_length=1)
    weight: float

    #: The sense whose definition speaks, and that definition with the naming token marked.
    sense: str = Field(min_length=1)
    evidence: str = Field(min_length=1)

    #: Whether a hand moved the relation off the miner's guess — so an approved edge can say
    #: whether the machine or the reader chose its name.
    relabelled: bool = False

    #: WHO authorized it and WHEN. Not decoration: an edge is admitted because a person decided,
    #: and an edge that cannot say who decided is a cell claiming an authority it cannot show.
    approved_by: str = Field(min_length=1)
    approved_at: int = Field(ge=0)

    #: Unix seconds when it was withdrawn, or None while it stands.
    withdrawn_at: int | None = None

    class Settings:
        name = "dictionary_curated_edges"
        indexes = [
            IndexModel([("source_key", ASCENDING), ("target_key", ASCENDING)], unique=True),
        ]


# ------------------------------------------------------------------------------------------------
# the manifest
# ------------------------------------------------------------------------------------------------


class DictionaryBuildDoc(LogicDocument, Timestamped):
    """logic (r) — one row per build of the base: what was measured, under what, on whose word.

    Deliberately NOT in `ALL_MODELS`, and for `MigrationDoc`'s reason: this is a LEDGER the body
    does not interpret. Registering it would put a growing append-only table into the r-cache, which
    snapshots every registered r-collection whole on every slow tick. It is a `LogicDocument` all
    the same, so the write-class seam covers every collection in the database with no exceptions —
    a build is something that happens TO him.

    THE LEDGER FIELDS are the point of the row. `config_fingerprint` is the hash of the whole
    declared policy the engine took as an argument; the four version/fingerprint fields beside it
    say WHICH ROWS that config was assembled from. Two builds sharing all six were measured under
    the same policy AND against the same bar, and that is a claim a reader can check rather than
    assume.
    """

    #: `DictionaryConfig.fingerprint()` — the hash of what the engine actually ran on.
    config_fingerprint: Annotated[str, Indexed()] = Field(min_length=1)

    #: And the canonical policy itself, so a later reader can DIFF two builds instead of trusting
    #: two hashes to differ for the reason he assumes (`DictionaryConfig.as_dict()`).
    #: THE BUILD LABEL its rows are stored under. Added at E1c, and the reason is a defect that had
    #: been flagged as theoretical and then happened: a manifest recorded the POLICY a build ran and
    #: never the label, so the only link to its rows was that the default label IS the head of the
    #: config fingerprint. The moment two builds ran the same policy — E1b's rebuild and E1c's
    #: layer — `find_one` on that fingerprint started returning whichever row came first, and a
    #: verifier printed one build's authorization beside another build's rows with a straight face.
    build: Annotated[str, Indexed()] = ""

    policy: dict = Field(default_factory=dict)

    policy_version: int = Field(ge=1)
    policy_fingerprint: str = Field(min_length=1)

    bar_version: int = Field(ge=1)
    bar_fingerprint: str = Field(min_length=1)

    #: What came out: lexicon size, closure words, dimensions — whatever the build counted. A map
    #: rather than columns because the counts a build reports will grow with the builders (R cells,
    #: D cells, curated edges) and each new number must not be a migration against this shape.
    counts: dict[str, int] = Field(default_factory=dict)

    #: Whose hand ordered this build. A build is an authorized act (`--apply` is the Captain's), and
    #: a manifest that could not say who authorized it would be a log, not a ledger.
    authorization: str = Field(min_length=1)

    note: str = ""

    class Settings:
        name = "dictionary_builds"
        indexes = [
            IndexModel([("created_at", DESCENDING)]),
        ]


# ------------------------------------------------------------------------------------------------
# the base itself — the key registry and R
# ------------------------------------------------------------------------------------------------
#
# Added at T3, completed at T4. Three collections rather than one, because they answer different
# questions: `base_keys` is THE DIMENSION ORDER, shared by every matrix of a build, and `base_r` and
# `base_d` are two matrices over it. A build that stored its key space inside each matrix would let
# R and D drift into two orders that no reader could compare cell for cell.
#
# NEITHER IS REGISTERED WITH THE BODY (`BASE_MODELS`, not `ALL_MODELS`), for `DictionaryBuildDoc`'s
# reason and one worse: the r-cache snapshots every registered r-collection WHOLE on every slow
# tick, and R is thousands of rows carrying hundreds of thousands of cells. The base is read the way
# a dictionary is read — by key, on demand — and E2 builds that reader. What they share with the
# ledger is the write-class: `logic`, so no collection in the database escapes the seam.


class StoredCell(BaseModel):
    """One non-zero entry of a row, as it is stored (`tk2.dictionary.matrix.Cell`).

    A LIST of these, never a map keyed by the column: a base key contains a dot (`sleep.v`), and
    mongo reads a dotted field name as a path — `{"$set": {"cells.sleep.v": …}}` writes a nested
    document called `sleep` instead of the cell anybody meant. The key is a VALUE here, forever.
    """

    #: The dimension this cell is ABOUT. Row X, column Y is X's relation TO Y — asymmetric, which is
    #: what keeps the antonym column-read and the entails/entailed_by distinction alive.
    column: str = Field(min_length=1)
    #: Signed. A negative weight is opposition STATED, not a small similarity.
    w: float
    #: The relation that set the value.
    rel: str = Field(min_length=1)
    #: `mined` · `curated` · `axis`. The field that keeps a curated cell distinguishable from a
    #: mined one forever — a headline density that hides the hand is the first step back to a
    #: matrix nobody can audit.
    src: str = Field(min_length=1)
    #: Every relation that held between the two, strongest first, as `[name, weight]` pairs. The
    #: winner is what the geometry uses; this is what curation and a later retreat read.
    via: list[tuple[str, float]] = Field(default_factory=list)
    #: For a curated cell: the definition that justified it, verbatim (requirement 20).
    evidence: str = ""


class BaseKeyDoc(LogicDocument, Timestamped):
    """logic (r) — one dimension of one build, with its index. THE key space, as rows.

    The index is stored rather than derived from a sort, because it is the position a vector's
    column means: two readers that sorted differently would read every cell of every row at the
    wrong column, and nothing in the numbers would look wrong.
    """

    #: Which build these dimensions belong to. Two builds may sit in one database — that is what
    #: makes a before/after comparison possible at all — so nothing here is «the» base.
    build: Annotated[str, Indexed()] = Field(min_length=1)

    key: str = Field(min_length=1)
    word: str = Field(min_length=1)
    pos: str = Field(min_length=1)
    index: int = Field(ge=0)

    class Settings:
        name = "dictionary_base_keys"
        indexes = [
            IndexModel([("build", ASCENDING), ("key", ASCENDING)], unique=True),
            IndexModel([("build", ASCENDING), ("index", ASCENDING)], unique=True),
        ]


class SenseVectorDoc(LogicDocument, Timestamped):
    """logic (r) — one SENSE, placed in the base's space. The dictionary's second floor.

    THE BASE IS THE FRAME, THE SENSES ARE THE CONTENT, and that division is E1c's whole ruling. A
    base dimension is one word under one part of speech and it reads its definition from WordNet's
    FIRST synset — which is why `small.n` reads «the slender part of the back» and why that was
    called a defect all through E1. It stops being one here: `small.a` is a frame, and
    `small.a.01 … small.a.09` each carry their own reading. The 4,555 dimensions cover 17,257 senses
    at a mean of 3.79 apiece, and 73% of what a dimension means was being discarded until this table.

    IT RIDES ON THE BASE AND IS NEVER SQUARE (the architecture guard, tkzip req 11): a sense's cells
    are BASE DIMENSIONS, never other senses. 120,475 senses against 4,555 dimensions is half a
    billion possible cells and about half a million real ones; a senses×senses matrix would be
    14.5 BILLION and is the mistake this shape exists to make impossible.

    TWO VECTORS, MIRRORING THE TWO FLOORS. `distribution` is the sense's own gloss reduced through
    the same seam D uses — requirement 21's repair, the stop-list ruling, the name refusal and the
    structure filter all hold, because a second reduction would re-open every one of them quietly.
    `relations` is what WordNet states about THIS SYNSET, which is evidence the base structurally
    cannot hold: relations are stated per synset, and collapsing synsets to POS keys is what lost
    them. `bank.n.02` knows it is a financial institution; `bank.n` cannot.

    Measured before it was built: the gloss reaches 3.41 base dimensions on average and is empty for
    5.3% of senses; the synset's relations reach 0.86 and are empty for 54.1%. Relations alone are
    far too thin to place a sense — which is why both are here, and why `relations` may legitimately
    be empty on a row whose `distribution` is not.
    """

    #: Which build placed this sense. A sense vector is only meaningful against the key space it was
    #: computed over, and two builds may sit in one database.
    build: Annotated[str, Indexed()] = Field(min_length=1)

    #: The tk2 sense key, word-anchored: `left.a.01`. It truncates to its base key, which WordNet's
    #: own synset name does not — `left.a.01` may live in a synset called `leftover.s.01`.
    key: str = Field(min_length=1)
    #: The base dimension this sense is a reading OF. Indexed because «every sense of `small.a`» is
    #: the question the station will ask most.
    base: Annotated[str, Indexed()] = Field(min_length=1)
    #: Which reading of that dimension, 1-based, in WordNet's own sense order.
    ordinal: int = Field(ge=1)

    #: WordNet's own name for the synset, kept as PROVENANCE and never used as an identifier: it is
    #: what makes a build auditable against the resource, and what a version bump would be diffed on.
    synset: str = Field(min_length=1)
    #: The definition this sense was placed from, verbatim. Stored because a vector nobody can trace
    #: back to the words that produced it is a vector nobody can argue with.
    definition: str = ""

    #: Over BASE dimensions: what this sense's own definition shares with the base's vocabulary.
    distribution: list[StoredCell] = Field(default_factory=list)
    #: Over BASE dimensions: what WordNet states about this synset. Empty for the majority of
    #: senses, and that is a finding rather than a fault — most of a synset's relatives are not base
    #: words.
    relations: list[StoredCell] = Field(default_factory=list)

    class Settings:
        name = "dictionary_sense_vectors"
        indexes = [
            IndexModel([("build", ASCENDING), ("key", ASCENDING)], unique=True),
            IndexModel([("build", ASCENDING), ("base", ASCENDING), ("ordinal", ASCENDING)]),
        ]


class BaseDistributionDoc(LogicDocument, Timestamped):
    """logic (r) — one row of D: which dimensions this one's definition shares words with.

    THE SAME SHAPE AS R's, deliberately: R and D are two geometries over one key space and the
    difference between them is what fills a cell, never how a cell is kept. A reader that had to
    learn two row shapes to compare them cell for cell would be a reader that eventually compares
    the wrong ones.

    Sparser than its name suggests, and the floor is why: a cell exists only where two definitions
    share at least `min_shared` vocabulary words and the scored overlap clears the declared floor.
    Unsigned — there is no negative overlap, and the sign belongs to R alone.
    """

    build: Annotated[str, Indexed()] = Field(min_length=1)

    key: str = Field(min_length=1)
    #: The dimension's own index, carried so a row can be read without the registry beside it.
    index: int = Field(ge=0)

    cells: list[StoredCell] = Field(default_factory=list)

    class Settings:
        name = "dictionary_base_distribution"
        indexes = [
            IndexModel([("build", ASCENDING), ("key", ASCENDING)], unique=True),
            IndexModel([("build", ASCENDING), ("index", ASCENDING)], unique=True),
        ]


class BaseSealDoc(LogicDocument, Timestamped):
    """logic (r) — one matrix of one build, declared COMPLETE. The row a reader refuses a base for.

    Added at T5, and it is the answer to a measured hazard rather than a precaution: D is 218 MB of
    BSON that pymongo splits into several wire messages, over a network, to a body in another room.
    An interrupted apply left a partial matrix under a build label that looked exactly like a whole
    one — the rows were valid, the registry was there, and only a count nobody was taking could have
    said otherwise.

    So a build SEALS each matrix, and the seal is written LAST: after every chunk has landed and
    after the stored row count has been read back and agreed with. Until then there is no seal, and
    `MongoMatrixStore` refuses to read an unsealed matrix at all. A half-written base is therefore
    not a base that reads wrong — it is a base that does not read.

    THE FINGERPRINT is the second half of the same idea and covers what a count cannot: a truncated
    row, a re-ordered key space, a weight that came back as something else. It is
    `tk2.dictionary.matrix.fingerprint` over the matrix as it was built, and `tools/verify_base.py`
    recomputes it from the stored rows. A count says «all of it arrived»; this says «and it is what
    left».
    """

    build: Annotated[str, Indexed()] = Field(min_length=1)

    #: The matrix this seals, by its collection name (`base_r`, `base_d`) — or `base_keys` for the
    #: dimension registry, which is a matrix's worth of meaning and is written first.
    name: str = Field(min_length=1)

    #: How many rows the writer wrote AND read back. Both, or the seal would only repeat what the
    #: writer believed.
    rows: int = Field(ge=0)

    #: How many cells those rows carry, the diagonal included. A row count alone cannot notice a row
    #: that arrived with half its cells.
    cells: int = Field(ge=0)

    #: `tk2.dictionary.matrix.fingerprint` of what was written. Empty for the key registry, which is
    #: its own content and is compared as an ordered list.
    fingerprint: str = ""

    #: How the write was made, for a reader who finds a slow build in the ledger: the chunk size the
    #: rows went out in and how long the whole matrix took. A note, not a promise.
    note: str = ""

    class Settings:
        name = "dictionary_base_seals"
        indexes = [
            # One seal per matrix per build. Two would make «is this build complete?» a question
            # with two answers, which is the one thing the seal exists to prevent.
            IndexModel([("build", ASCENDING), ("name", ASCENDING)], unique=True),
        ]


class BaseRelationDoc(LogicDocument, Timestamped):
    """logic (r) — one row of R: what this dimension states about the others.

    SPARSE. A row is its cells; a zero is the absence of a statement rather than a stored one. The
    prototype's dense `vector` was free at 983 dimensions and is a hundred and fifty megabytes of
    mostly zero at the full base — and R is sparse by nature, since a cell exists because a NAMED
    relation put it there.
    """

    build: Annotated[str, Indexed()] = Field(min_length=1)

    key: str = Field(min_length=1)
    #: The dimension's own index, carried so a row can be read without the registry beside it.
    index: int = Field(ge=0)

    cells: list[StoredCell] = Field(default_factory=list)

    class Settings:
        name = "dictionary_base_relations"
        indexes = [
            IndexModel([("build", ASCENDING), ("key", ASCENDING)], unique=True),
            IndexModel([("build", ASCENDING), ("index", ASCENDING)], unique=True),
        ]
