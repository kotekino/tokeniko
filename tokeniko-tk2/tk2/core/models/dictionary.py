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

The reading seam: nothing here reads the database and nothing here computes a fingerprint. The pure
side (`tk2.dictionary.policy`) takes ROWS AS MAPPINGS — `model_dump()` output, or raw pymongo
documents, either works — exactly as the closure engine takes an injected gloss provider. That is
what keeps `tk2/dictionary/` free of mongo while the policy it runs on lives in mongo.
"""

from typing import Annotated, Any

from bunnet import Indexed
from pydantic import Field
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

    #: The group the entry was declared in, when its declaration was grouped: the seed families
    #: (volitional · motion · effect · identity), which say WHY those words are seeded and would be
    #: lost if the rows were a flat word list.
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
