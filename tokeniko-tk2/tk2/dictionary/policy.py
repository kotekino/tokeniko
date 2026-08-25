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

from tk2.dictionary.config import BarPair, ClosurePolicy, DictionaryConfig

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
    """
    policy_rows = list(policy_rows)
    bar_rows = list(bar_rows)
    return DictionaryConfig(
        closure=closure_from_rows(policy_rows, extra_seeds),
        declared_seeds=seeds_from_rows(policy_rows),
        bar=bar_from_rows(bar_rows),
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
