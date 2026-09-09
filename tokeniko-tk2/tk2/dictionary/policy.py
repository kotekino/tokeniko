"""POLICY FROM ROWS — the seam where curation reaches a pure engine.

`config.py` holds the SHAPE of a policy (what a closure cut is, what a bar pair is, how a policy is
fingerprinted); this module turns ROWS into one. The rows come from `dictionary_policy` and
`dictionary_bar`, and nothing here knows that: they arrive as plain mappings, exactly as the gloss
provider arrives as an injected object. `model_dump()` output and raw pymongo documents both work,
because both are mappings and this reads only the fields it names.

That is what lets the standing law hold on both sides at once — the policy lives in the db, and
`tk2/dictionary/` still imports no database.

TWO FINGERPRINTS, and they are not the config's. `DictionaryConfig.fingerprint()` hashes the policy
as the engine received it; the two here hash the ROWS as they were read, one for the policy and one
for the bar. The manifest records all three, because they answer different questions: the config
hash says «two builds ran the same policy», the row hashes say «and it came from these rows, at
these versions». A build that assembled its config from somewhere else would agree on the first and
disagree on the last two, which is precisely the drift worth being able to see.

THE OFFLINE SNAPSHOT. The acceptance suite must run with no body reachable, so the bar is exported
to `bar_snapshot.json` beside this file, pinned by its own fingerprint. Loading it VERIFIES the pin:
a hand edit of the pairs that does not recompute the hash is refused here, offline, and a test
asserts the snapshot's fingerprint against the db's whenever the db is reachable. Between the two
the snapshot cannot silently drift from the rows.
"""

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable, Mapping

from tk2.dictionary import keys
from tk2.dictionary.config import BarPair, ClosurePolicy, DictionaryConfig, RelationPolicy

Row = Mapping[str, Any]

# ------------------------------------------------------------------------------------------------
# the vocabulary of a policy row
# ------------------------------------------------------------------------------------------------

#: One seeded word. Its declaration IS its presence, so the row carries no value — the `family` says
#: which of the declared families put it there.
KIND_SEED = "seed"

#: The `family` of a seed the RESOURCE argued for: the definitional core, by in-degree over the
#: definition digraph. Named here rather than in the migration that first wrote it because it is
#: read — a caller that wants the PURPOSE half of a policy (the seed proposal does, every time it
#: re-argues the structural half) has to be able to say which half is which.
FAMILY_STRUCTURE = "structure"

#: One closure cut. `name` is the `ClosurePolicy` field, `value` is what it is set to.
KIND_CLOSURE = "closure"

#: The `ClosurePolicy` fields a closure row may name. `extra_seeds` is deliberately NOT among them:
#: it is a RUN's own argument (a variant arguing with the standing policy), never a standing
#: declaration, and a row that could set it would let a stored policy pretend to be the standard one.
CLOSURE_SETTINGS = ("max_depth", "max_size", "senses")

#: One WordNet relation R fills cells with. `name` is the relation, `value` its signed weight, and
#: `position` its PRECEDENCE — the order the cell walk believes two relations in when both hold at
#: the same absolute weight. Since policy v3.
KIND_RELATION_WEIGHT = "relation_weight"

#: One relation a CURATED (definitional) edge may claim, and at what strength. A separate kind from
#: the mined weights rather than a `family` of them, because a row is unique per (version, kind,
#: name) and `entails` is BOTH — the same claim from two provenances, which is the PoC's own choice
#: («same name as the WordNet edge on purpose») and must not collapse into one row.
KIND_CURATED_RELATION = "curated_relation"

#: A setting of the MINING of relations — today only `lemma_scope`, ruled by the Captain on
#: 2026-08-26 and a row since policy v4. Its own kind rather than a `relation_weight` with a
#: non-numeric value: a weight and a reading of the resource are two different statements, and a
#: table that mixed them could not be read strictly.
KIND_RELATION_SETTING = "relation"

#: The `RelationPolicy` fields a `relation` row may name. Strict for `CLOSURE_SETTINGS`' reason.
RELATION_SETTINGS = ("lemma_scope", "antonym_symmetry")

#: A setting of the curation mechanism itself — today only the reciprocal weight.
KIND_CURATION = "curation"

#: The `RelationPolicy` fields a `curation` row may name. Strict for `CLOSURE_SETTINGS`' reason.
CURATION_SETTINGS = ("reciprocal_weight",)

#: A cue word list: `name` is the curated relation it argues for, `value` the cue words, `position`
#: the order the cues are tried in (a gloss that is both purposive and locative reads as purpose).
KIND_CURATION_CUE = "curation_cue"

#: The fallback when no cue fires: `name` is the POS pair as `src>dst`, `value` the relation.
KIND_CURATION_DEFAULT = "curation_default"

#: The separator inside a `curation_default` row's name. A pair of parts of speech is one statement
#: and has to be one row name; `>` because the default is DIRECTED (`n>v` is not `v>n`).
POS_PAIR_SEPARATOR = ">"

#: One part of speech that exists. `name` is the letter, `value` the long name, `position` the order
#: a multi-POS word's keys are listed in. Since policy v3 — the Captain's ruling of 2026-08-25: the
#: alphabet is WordNet's answer about English, not the key grammar.
KIND_POS = "pos"

#: A spelling the resource uses for a part of speech already in the alphabet: `name` is the
#: spelling, `value` the letter it folds onto (WordNet's satellite adjective `s` -> `a`).
KIND_POS_ALIAS = "pos_alias"


class PolicyRowsInvalid(ValueError):
    """The rows cannot be read as a policy.

    Raised, never worked around: a policy assembled from rows that half-parsed is exactly the silent
    failure the fingerprint exists to make impossible — the build would run, the manifest would
    record a hash, and the hash would describe something nobody declared.
    """


# ------------------------------------------------------------------------------------------------
# reading the policy rows
# ------------------------------------------------------------------------------------------------


def _of_kind(rows: Iterable[Row], kind: str) -> list[Row]:
    """The rows of one kind, in declared order. Ties broken by name so the order is total: two rows
    at one position is a defective declaration, and it must not read back differently each time."""
    return sorted((r for r in rows if r["kind"] == kind), key=lambda r: (r["position"], r["name"]))


def policy_version(rows: Iterable[Row]) -> int:
    """The version these rows are. Refuses a mixed set rather than picking one.

    A build reads ONE version — that is what makes the manifest's `policy_version` mean anything —
    so rows from two versions arriving together is a caller bug, not a set to be reconciled here.
    """
    versions = {r["version"] for r in rows}
    if len(versions) != 1:
        raise PolicyRowsInvalid(
            f"a policy is read at ONE version; these rows carry {sorted(versions) or 'none'}. "
            f"Select the version before reading it — the manifest records which one was used."
        )
    return versions.pop()


def latest_version(rows: Iterable[Row]) -> list[Row]:
    """The rows of the NEWEST version present, for a caller holding the whole table.

    `policy_version` refuses a mixed set on purpose — a build reads one version — so choosing which
    one is a separate and explicit act, and this is it. Since 0005 the collection really does hold
    two versions: v1 is not history to be cleaned up, it is what a manifest row recording v1 still
    points at.
    """
    rows = list(rows)
    if not rows:
        raise PolicyRowsInvalid("no policy rows at all — there is no version to select.")
    newest = max(r["version"] for r in rows)
    return [r for r in rows if r["version"] == newest]


def seed_rows(rows: Iterable[Row]) -> list[Row]:
    """The seed rows themselves, in declared order — for a caller that needs more than the word:
    which source argued for it (`family`) and what was written down about it (`note`)."""
    return _of_kind(rows, KIND_SEED)


def seeds_from_rows(rows: Iterable[Row]) -> tuple[str, ...]:
    """The declared seeds, in declared order. Requirement 8's families, as they were written down."""
    return tuple(row["name"] for row in seed_rows(rows))


def closure_from_rows(rows: Iterable[Row], extra_seeds: tuple[str, ...] = ()) -> ClosurePolicy:
    """The closure cuts, as a `ClosurePolicy`.

    Every setting must be present and no unknown setting is tolerated. The strictness is the whole
    value of the table: a missing `max_size` that fell back to a default in code would be a policy
    the manifest names and the build did not run, and an unknown name silently ignored would be a
    curated decision that never took effect and never said so.
    """
    declared = {row["name"]: row["value"] for row in _of_kind(rows, KIND_CLOSURE)}

    unknown = sorted(set(declared) - set(CLOSURE_SETTINGS))
    if unknown:
        raise PolicyRowsInvalid(
            f"closure rows name settings the policy has no field for: {unknown}. "
            f"The settings are {list(CLOSURE_SETTINGS)}."
        )
    missing = [name for name in CLOSURE_SETTINGS if name not in declared]
    if missing:
        raise PolicyRowsInvalid(
            f"closure rows are incomplete: {missing} unset. Every cut is declared, because a cut "
            f"that falls back to a default in code is a cut the manifest cannot vouch for."
        )

    return ClosurePolicy(
        max_depth=declared["max_depth"],
        max_size=declared["max_size"],
        senses=declared["senses"],
        extra_seeds=tuple(extra_seeds),
    )


# ------------------------------------------------------------------------------------------------
# reading R's rows — the relation weights and the curator's vocabulary (policy v3)
# ------------------------------------------------------------------------------------------------


def relation_policy_from_rows(rows: Iterable[Row]) -> RelationPolicy | None:
    """R's declared weights, or `None` when this policy version never declared any.

    `None` is not a failure and must not become an empty `RelationPolicy`: v1 and v2 are still
    readable and neither of them had anything to say about relations, so a config assembled from
    them says nothing either (see `DictionaryConfig`). A version that declares SOME of it and not
    the rest is a different matter and is refused — a curated vocabulary with no reciprocal weight
    would write half an edge.
    """
    rows = list(rows)
    weights = [(r["name"], float(r["value"])) for r in _of_kind(rows, KIND_RELATION_WEIGHT)]
    mining = {r["name"]: r["value"] for r in _of_kind(rows, KIND_RELATION_SETTING)}
    curated = [(r["name"], float(r["value"])) for r in _of_kind(rows, KIND_CURATED_RELATION)]
    settings = {r["name"]: r["value"] for r in _of_kind(rows, KIND_CURATION)}
    cues = [(r["name"], tuple(r["value"])) for r in _of_kind(rows, KIND_CURATION_CUE)]
    defaults = []
    for row in _of_kind(rows, KIND_CURATION_DEFAULT):
        source, _, target = row["name"].partition(POS_PAIR_SEPARATOR)
        if not source or not target:
            raise PolicyRowsInvalid(
                f"a curation default names a POS pair as `src{POS_PAIR_SEPARATOR}dst`; "
                f"{row['name']!r} is not one."
            )
        defaults.append((source, target, row["value"]))

    if not weights:
        if curated or settings or cues or defaults or mining:
            raise PolicyRowsInvalid(
                "these rows declare the curator's vocabulary and no relation weights. R's weights "
                "are what a curated edge sits beside; half a declaration is not a policy."
            )
        return None

    unknown = sorted(set(settings) - set(CURATION_SETTINGS))
    if unknown:
        raise PolicyRowsInvalid(
            f"curation rows name settings the policy has no field for: {unknown}. "
            f"The settings are {list(CURATION_SETTINGS)}."
        )
    unknown = sorted(set(mining) - set(RELATION_SETTINGS))
    if unknown:
        raise PolicyRowsInvalid(
            f"relation rows name settings the policy has no field for: {unknown}. "
            f"The settings are {list(RELATION_SETTINGS)}."
        )
    if curated and "reciprocal_weight" not in settings:
        raise PolicyRowsInvalid(
            "a curated vocabulary is declared with no `reciprocal_weight` row. The back-reference "
            "is half of what a curated edge writes (the Captain's ruling of 2026-08-12), and a "
            "default in code would be a second declaration of it."
        )

    try:
        return RelationPolicy(
            weights=tuple(weights),
            curated=tuple(curated),
            reciprocal_weight=float(settings.get("reciprocal_weight", 0.0)),
            cues=tuple(cues),
            defaults=tuple(defaults),
            lemma_scope=mining.get("lemma_scope"),
            antonym_symmetry=mining.get("antonym_symmetry"),
        )
    except ValueError as error:
        raise PolicyRowsInvalid(str(error)) from error


def alphabet_from_rows(rows: Iterable[Row]) -> keys.Alphabet | None:
    """The parts of speech these rows declare, or `None` when they declare none (v1, v2).

    Returned AS DECLARED and not checked against the compiled grammar here: reading a policy to look
    at it must stay possible. The refusal fires one level up, in `config_from_rows`, which is where
    rows become the thing a build measures under.
    """
    rows = list(rows)
    letters = _of_kind(rows, KIND_POS)
    aliases = _of_kind(rows, KIND_POS_ALIAS)
    if not letters:
        if aliases:
            raise PolicyRowsInvalid(
                "these rows alias parts of speech they never declare. An alphabet is its letters; "
                "an alias alone points at nothing."
            )
        return None
    try:
        return keys.Alphabet(
            order=tuple(r["name"] for r in letters),
            names=tuple((r["name"], r["value"]) for r in letters),
            aliases=tuple((r["name"], r["value"]) for r in aliases),
        )
    except keys.InvalidKey as error:
        raise PolicyRowsInvalid(str(error)) from error


# ------------------------------------------------------------------------------------------------
# reading the bar rows
# ------------------------------------------------------------------------------------------------


def live_bar_rows(rows: Iterable[Row]) -> list[Row]:
    """The pairs that still stand, oldest declaration first.

    Retired rows are kept in the table and dropped here: the ledger keeps them, the bar does not
    include them. Sorted by (version, position, a, b) so a version's own grouping survives the
    round-trip and the order is total.
    """
    return sorted(
        (r for r in rows if r.get("retired_at") is None),
        key=lambda r: (r["version"], r["position"], r["a"], r["b"]),
    )


def bar_version(rows: Iterable[Row]) -> int:
    """The bar's version: the highest version among the pairs that stand.

    Unlike the policy, the bar is read across versions on purpose — it is APPEND-mostly, so version
    3 of the bar is versions 1, 2 and 3's live rows together, and the number names the last time it
    grew. That is what makes «was this pair declared before that run?» answerable from a build's
    recorded `bar_version` alone.
    """
    live = live_bar_rows(rows)
    if not live:
        raise PolicyRowsInvalid("the bar is empty: a build measured against no expectation is not measured.")
    return max(r["version"] for r in live)


def bar_from_rows(rows: Iterable[Row]) -> tuple[BarPair, ...]:
    """The bar as the engine takes it: the live pairs, in declared order."""
    return tuple(
        BarPair(a=r["a"], b=r["b"], verdict=r["verdict"], why=r["why"]) for r in live_bar_rows(rows)
    )


# ------------------------------------------------------------------------------------------------
# the config the engine takes as an argument
# ------------------------------------------------------------------------------------------------


def config_from_rows(
    policy_rows: Iterable[Row],
    bar_rows: Iterable[Row],
    extra_seeds: tuple[str, ...] = (),
) -> DictionaryConfig:
    """THE call the build tool makes: rows in, the declared policy out.

    `extra_seeds` stays an argument rather than a row (see `CLOSURE_SETTINGS`): it is what a run
    argues with the standing policy, and it lands in the fingerprint like everything else, so a run
    that added seeds can never be mistaken for the standard one.

    THE ALPHABET IS CHECKED HERE, and only here: this is the call that turns rows into the thing a
    build measures under, so it is where a policy declaring parts of speech the key convention was
    not compiled for must stop (`keys.assert_compiled`). Reading those rows to look at them stays
    possible next door.
    """
    policy_rows = list(policy_rows)
    bar_rows = list(bar_rows)
    alphabet = alphabet_from_rows(policy_rows)
    if alphabet is not None:
        keys.assert_compiled(alphabet)
    return DictionaryConfig(
        closure=closure_from_rows(policy_rows, extra_seeds),
        declared_seeds=seeds_from_rows(policy_rows),
        bar=bar_from_rows(bar_rows),
        relations=relation_policy_from_rows(policy_rows),
        alphabet=alphabet,
    )


# ------------------------------------------------------------------------------------------------
# the row fingerprints
# ------------------------------------------------------------------------------------------------


def _sha256_of(blob: Any) -> str:
    text = json.dumps(blob, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def policy_fingerprint(rows: Iterable[Row]) -> str:
    """sha256 over the policy rows as declared — version, and every entry in order.

    `created_at` is NOT in it, and that is deliberate: two databases that received the same
    migration at different moments hold the same policy, and a fingerprint that disagreed with that
    would be measuring the deploy rather than the declaration.
    """
    rows = list(rows)
    entries = sorted(
        (
            {
                "kind": r["kind"],
                "family": r.get("family"),
                "name": r["name"],
                "value": r.get("value"),
                "position": r["position"],
            }
            for r in rows
        ),
        key=lambda e: (e["kind"], e["position"], e["name"]),
    )
    return _sha256_of({"version": policy_version(rows), "entries": entries})


def bar_fingerprint(rows: Iterable[Row]) -> str:
    """sha256 over the bar as it stands — the live pairs, their verdicts and their reasons.

    `why` is inside the hash because it is part of the declaration: a pair whose justification was
    rewritten after a run is a different expectation, whatever its verdict still says.
    """
    rows = list(rows)
    entries = [
        {
            "version": r["version"],
            "position": r["position"],
            "a": r["a"],
            "b": r["b"],
            "verdict": r["verdict"],
            "why": r["why"],
        }
        for r in live_bar_rows(rows)
    ]
    return _sha256_of({"version": bar_version(rows), "entries": entries})


# ------------------------------------------------------------------------------------------------
# the manifest row a build leaves behind
# ------------------------------------------------------------------------------------------------


def manifest_row(
    config: DictionaryConfig,
    policy_rows: Iterable[Row],
    bar_rows: Iterable[Row],
    counts: Mapping[str, int],
    authorization: str,
    note: str = "",
) -> dict:
    """THE ledger entry, assembled from the same rows the build read — `DictionaryBuildDoc`'s shape.

    Here rather than in the build tool, and taking the ROWS rather than four hand-passed numbers,
    because a manifest is only worth anything if it cannot disagree with what the build actually
    used. A tool that copied a version number in by hand would be free to copy the wrong one, and
    the resulting row would be a confident record of a policy nobody ran.
    """
    policy_rows = list(policy_rows)
    bar_rows = list(bar_rows)
    return {
        "config_fingerprint": config.fingerprint(),
        "policy": config.as_dict(),
        "policy_version": policy_version(policy_rows),
        "policy_fingerprint": policy_fingerprint(policy_rows),
        "bar_version": bar_version(bar_rows),
        "bar_fingerprint": bar_fingerprint(bar_rows),
        "counts": dict(counts),
        "authorization": authorization,
        "note": note,
    }


# ------------------------------------------------------------------------------------------------
# the offline snapshot
# ------------------------------------------------------------------------------------------------

#: Beside this module so it ships with the package and needs no path argument to read — the
#: acceptance suite must run on a machine with no body reachable and no repo layout assumed.
SNAPSHOT_PATH = Path(__file__).resolve().parent / "bar_snapshot.json"


class SnapshotStale(RuntimeError):
    """The snapshot's pairs and its recorded fingerprint do not agree.

    Nearly always a hand edit: the file is an EXPORT, and the way to change it is to change the rows
    and export again (`tools/export_bar_snapshot.py`), never to type into it.
    """


def bar_snapshot(path: Path | None = None) -> dict:
    """The exported bar, verified against its own pin.

    Returns the whole document — `version`, `fingerprint`, `pairs`, and the provenance of the export
    — because a test that asserts against the db needs the fingerprint, and a test that runs offline
    needs the pairs.
    """
    document = json.loads((path or SNAPSHOT_PATH).read_text(encoding="utf-8"))
    recomputed = bar_fingerprint(document["pairs"])
    if recomputed != document["fingerprint"]:
        raise SnapshotStale(
            f"{(path or SNAPSHOT_PATH).name} records fingerprint {document['fingerprint'][:12]}… "
            f"but its pairs hash to {recomputed[:12]}…. The snapshot is an export of "
            f"`dictionary_bar`; regenerate it with tools/export_bar_snapshot.py rather than editing "
            f"it by hand."
        )
    return document


def snapshot_bar() -> tuple[BarPair, ...]:
    """The snapshot as the engine takes it — the offline stand-in for `bar_from_rows`."""
    return bar_from_rows(bar_snapshot()["pairs"])


def snapshot_document(rows: Iterable[Row], source: str) -> dict:
    """The document `tools/export_bar_snapshot.py` writes. Here, not in the tool, so the shape the
    reader verifies and the shape the writer produces are one piece of code.

    It carries the bar's CONTENT and nothing else — no `created_at`, for the reason the fingerprint
    excludes it: two databases that received the same migration at different moments hold the same
    bar, and a snapshot that recorded one of those moments would churn on every re-export while
    pinning nothing extra. The epoch stamps are the LEDGER's, and the ledger is the rows.
    """
    live = live_bar_rows(rows)
    return {
        "source": source,
        "version": bar_version(live),
        "fingerprint": bar_fingerprint(live),
        "pairs": [
            {
                "version": r["version"],
                "position": r["position"],
                "a": r["a"],
                "b": r["b"],
                "verdict": r["verdict"],
                "why": r["why"],
            }
            for r in live
        ],
    }


# ------------------------------------------------------------------------------------------------
# the other direction — a declared policy as rows, for the migration that first writes it
# ------------------------------------------------------------------------------------------------


def policy_rows_of(config: DictionaryConfig, version: int, families: Mapping[str, str] | None = None) -> list[dict]:
    """A `DictionaryConfig` written out as `dictionary_policy` rows.

    Used by the migration that moves an existing declaration into the db, and by tests that need a
    round trip. It is NOT how a policy is normally authored — the normal direction is rows first,
    which is the whole point of the table — but the first set of rows has to come from somewhere,
    and reading them off the object that already held them is how they cross unchanged.

    `families` is keyed by row NAME and serves the seeds and the relation weights alike (a seed's
    family is the source that argued for it; a relation's is the group it belongs to). The curated
    vocabulary and the alphabet carry a fixed family instead, because there is only one source for
    either and a map entry that could be forgotten would leave a row unable to say where it came
    from. A policy version that declares no relations and no alphabet writes exactly the rows it
    always did.
    """
    families = families or {}
    rows: list[dict] = [
        {
            "version": version,
            "kind": KIND_SEED,
            "name": word,
            "value": None,
            "family": families.get(word),
            "position": i,
            "note": "",
        }
        for i, word in enumerate(config.declared_seeds)
    ]
    closure = asdict(config.closure)
    rows += [
        {
            "version": version,
            "kind": KIND_CLOSURE,
            "name": name,
            "value": closure[name],
            "family": None,
            "position": i,
            "note": "",
        }
        for i, name in enumerate(CLOSURE_SETTINGS)
    ]

    def entry(kind: str, name: str, value, position: int, family: str | None = None) -> dict:
        return {
            "version": version,
            "kind": kind,
            "name": name,
            "value": value,
            "family": families.get(name) if family is None else family,
            "position": position,
            "note": "",
        }

    if config.relations is not None:
        relations = config.relations
        rows += [
            entry(KIND_RELATION_WEIGHT, name, weight, i)
            for i, (name, weight) in enumerate(relations.weights)
        ]
        rows += [
            entry(KIND_CURATED_RELATION, name, weight, i, family="definitional")
            for i, (name, weight) in enumerate(relations.curated)
        ]
        rows += [
            entry(KIND_CURATION, "reciprocal_weight", relations.reciprocal_weight, 0, family="definitional")
        ]
        for position, name in enumerate(RELATION_SETTINGS):
            value = getattr(relations, name)
            if value is not None:
                rows += [entry(KIND_RELATION_SETTING, name, value, position, family="mining")]
        rows += [
            entry(KIND_CURATION_CUE, name, list(cues), i, family="definitional")
            for i, (name, cues) in enumerate(relations.cues)
        ]
        rows += [
            entry(
                KIND_CURATION_DEFAULT,
                f"{source}{POS_PAIR_SEPARATOR}{target}",
                relation,
                i,
                family="definitional",
            )
            for i, (source, target, relation) in enumerate(relations.defaults)
        ]

    if config.alphabet is not None:
        long_names = dict(config.alphabet.names)
        rows += [
            entry(KIND_POS, letter, long_names.get(letter), i, family="alphabet")
            for i, letter in enumerate(config.alphabet.order)
        ]
        rows += [
            entry(KIND_POS_ALIAS, spelling, letter, i, family="alphabet")
            for i, (spelling, letter) in enumerate(config.alphabet.aliases)
        ]

    return rows


def bar_rows_of(pairs: Iterable[BarPair], version: int) -> list[dict]:
    """A declared bar written out as `dictionary_bar` rows, in the order it was declared."""
    return [
        {
            "version": version,
            "a": pair.a,
            "b": pair.b,
            "verdict": pair.verdict,
            "why": pair.why,
            "position": i,
            "retired_at": None,
        }
        for i, pair in enumerate(pairs)
    ]
