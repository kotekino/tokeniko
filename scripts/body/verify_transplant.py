#!/usr/bin/env python3
"""verify_transplant.py — the body transplant, turned from an eyeball check into arithmetic.

Runbook `doc/ref/deploy-body.md` §3.5 says «verify before deleting anything» and then lists three
things to look at. This makes that list a MEASUREMENT: capture a baseline on the MacBook before the
move, run the identical probe on the mini after the copy, diff the two. "The counts match" stops
being a memory and becomes an exit code.

READ-ONLY BY CONSTRUCTION. This script opens the databases and NEVER writes to them: no insert, no
update, no delete, no index creation, no `$merge`/`$out` stage, no `getMore` side effect that
mutates anything. It uses raw pymongo — deliberately NOT `init_io()`/Bunnet, because `init_io` +
`get_tokeniko()` UPSERT the stakeholder singleton, and a verification tool must be incapable of
touching the biography it is verifying. It is therefore safe to run against the live body at any
moment, mid-thought.

    verify_transplant.py                                  # snapshot the live DBs, print the table
    verify_transplant.py --out baseline-macbook.json      # ... and save it as evidence
    verify_transplant.py --compare baseline-macbook.json  # diff live against a saved baseline
    verify_transplant.py --fast                           # estimated counts (metadata, no scan)
    verify_transplant.py --uri mongodb://mini.local:27018/?directConnection=true

`--compare` exits NON-ZERO on any mismatch, so it can gate the "only then delete the source" step.

A missing database or collection is reported as ABSENT, never a crash: on the mini, before the copy,
everything is absent — and that is a legitimate, informative run.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from datetime import datetime, timezone
from typing import Any, Optional

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import OperationFailure, PyMongoError
from pymongo.uri_parser import parse_uri

# the package dir is two levels up from scripts/body/ ... plus the package name.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_PKG_DIR = os.path.join(_REPO_ROOT, "tokeniko-tk1")
sys.path.insert(0, _PKG_DIR)

from lib.core.models import _VECTOR_INDEX  # noqa: E402  (path is set above)

# the birth stamp the transplant must preserve — runbook §3.5, and the one number in this file that
# is an assertion about WHO HE IS rather than about how much data there is.
_BIRTH_STAMP_UTC = "2026-07-09T06:21:37Z"

_DICTIONARY_COLLECTION = "dictionary"
_BRAIN_STATE_COLLECTION = "brain_state"
_MEMORY_COLLECTION = "memory"
_MEMORY_TIME_FIELD = "timestamp"          # TKMemoryItemDoc.Settings.timeseries.time_field

# the brain_state continuity fields worth carrying across a move. Scalars are compared by value;
# the containers below are compared by SIZE (their contents are working state, not identity).
_BRAIN_STATE_SCALARS = (
    "wake_at",                # THE BIRTH STAMP — «alive since», never reset
    "awake_s",                # the folded lived-awake ledger
    "awake_mark",             # the open awake stretch (None while asleep)
    "asleep_since",
    "last_thinking_at",
    "last_wondering_at",
    "last_wondered_kb_at",
    "last_untangled_kb_at",
)
_BRAIN_STATE_SIZED = (
    "source_cursors",         # per-speaker memory cursors
    "wonder_queue",
    "digest_buffer",
    "wondering_window",
)


# ==================================================================================================
# snapshot
# ==================================================================================================

def _redact(uri: str) -> str:
    """The URI may carry credentials. Only the nodes are ever printed or written to disk."""
    try:
        parsed = parse_uri(uri)
        return ",".join(f"{host}:{port}" for host, port in parsed["nodelist"])
    except Exception:
        return "<unparseable>"


def _count(collection, fast: bool) -> Optional[int]:
    try:
        if fast:
            return collection.estimated_document_count()
        return collection.count_documents({})
    except PyMongoError as error:
        return f"<error: {type(error).__name__}>"  # type: ignore[return-value]


def _search_indexes(collection) -> Any:
    """`mongot` metadata — the thing whose survival is the real risk of moving the volume.

    Not every server offers `listSearchIndexes`; a server that refuses is reported as such rather
    than treated as "no indexes", because those two facts must never be confused.
    """
    try:
        rows = [
            {
                "name": index.get("name"),
                "type": index.get("type"),
                "status": index.get("status"),
                "queryable": index.get("queryable"),
                "fields": (index.get("latestDefinition") or {}).get("fields"),
            }
            for index in collection.list_search_indexes()
        ]
        return sorted(rows, key=lambda row: str(row.get("name")))
    except OperationFailure:
        return "<listSearchIndexes unsupported>"
    except PyMongoError as error:
        return f"<error: {type(error).__name__}>"


def _snapshot_db(client: MongoClient, name: str, fast: bool) -> dict:
    if name not in client.list_database_names():
        return {"present": False, "collections": {}}

    database = client[name]
    collections: dict[str, dict] = {}
    for collection_name in sorted(database.list_collection_names()):
        collection = database[collection_name]
        entry: dict[str, Any] = {"count": _count(collection, fast)}
        indexes = _search_indexes(collection)
        # only carry the key when there is something to carry — a snapshot of forty collections
        # should not be forty "<unsupported>" strings.
        if isinstance(indexes, list) and indexes:
            entry["search_indexes"] = indexes
        elif isinstance(indexes, str) and not indexes.startswith("<listSearchIndexes"):
            entry["search_indexes"] = indexes
        collections[collection_name] = entry

    return {"present": True, "collections": collections}


# --------------------------------------------------------------------------------------------------
# the three targeted probes
# --------------------------------------------------------------------------------------------------

def _probe_vector_search(client: MongoClient, kb_db: str) -> dict:
    """SELF-PROVING: take one dictionary row, query with ITS OWN vector, expect itself back at ~1.0.

    The pipeline shape mirrors `lib/llc/evaluator/e_label._nearestWord` exactly (same index name,
    same `path: "vector"`), so a pass here is a pass for the machinery the mind actually uses. If
    `mongot` did not survive the move this is what fails — and it fails loudly, not subtly.
    """
    result: dict[str, Any] = {"ok": False, "index": _VECTOR_INDEX}
    try:
        if kb_db not in client.list_database_names():
            result["error"] = "kb database absent"
            return result
        collection = client[kb_db][_DICTIONARY_COLLECTION]
        seed = collection.find_one({"vector": {"$exists": True}}, {"word": 1, "sense": 1, "vector": 1})
        if not seed:
            result["error"] = "no dictionary row with a vector"
            return result

        result["probe_word"] = seed.get("word")
        result["probe_sense"] = seed.get("sense")
        result["dimensions"] = len(seed.get("vector") or [])

        hits = list(collection.aggregate([
            {"$vectorSearch": {
                "index": _VECTOR_INDEX,
                "path": "vector",
                "queryVector": list(seed["vector"]),
                "numCandidates": 50,
                "limit": 1,
            }},
            {"$project": {"_id": 0, "word": 1, "sense": 1, "score": {"$meta": "vectorSearchScore"}}},
        ]))
        if not hits:
            result["error"] = "$vectorSearch returned nothing (mongot down or index not queryable?)"
            return result

        top = hits[0]
        result["top_word"] = top.get("word")
        result["top_score"] = top.get("score")
        # a vector against itself is a cosine of 1; Atlas maps cosine to (1+cos)/2, so ~1.0 either
        # way. Band-assert, never an exact float.
        result["ok"] = (top.get("word") == seed.get("word")) and float(top.get("score") or 0.0) > 0.99
        if not result["ok"]:
            result["error"] = "nearest neighbour of a vector was not itself"
    except PyMongoError as error:
        result["error"] = f"{type(error).__name__}: {error}"
    return result


def _probe_brain_state(client: MongoClient, mem_db: str) -> dict:
    """The continuity singleton. `wake_at` is the birth stamp — the truth the move must preserve."""
    result: dict[str, Any] = {"ok": False}
    try:
        if mem_db not in client.list_database_names():
            result["error"] = "memory database absent"
            return result
        state = client[mem_db][_BRAIN_STATE_COLLECTION].find_one({"key": "singleton"})
        if not state:
            result["error"] = "brain_state singleton absent"
            return result

        for field in _BRAIN_STATE_SCALARS:
            result[field] = state.get(field)
        for field in _BRAIN_STATE_SIZED:
            value = state.get(field)
            result[f"{field}_size"] = len(value) if value is not None else None

        wake_at = state.get("wake_at")
        result["wake_at_utc"] = _epoch_to_utc(wake_at)
        # the stamp is a sub-second float; compare at second granularity, which is what §3.5 states.
        result["birth_stamp_expected"] = _BIRTH_STAMP_UTC
        result["birth_stamp_ok"] = result["wake_at_utc"] == _BIRTH_STAMP_UTC
        result["ok"] = bool(result["birth_stamp_ok"])
        if not result["ok"]:
            result["error"] = f"wake_at reads {result['wake_at_utc']}, expected {_BIRTH_STAMP_UTC}"
    except PyMongoError as error:
        result["error"] = f"{type(error).__name__}: {error}"
    return result


def _probe_memory_timeseries(client: MongoClient, mem_db: str, fast: bool) -> dict:
    """The time-series log: how many moments, and does the record reach the present."""
    result: dict[str, Any] = {"ok": False, "collection": _MEMORY_COLLECTION, "time_field": _MEMORY_TIME_FIELD}
    try:
        if mem_db not in client.list_database_names():
            result["error"] = "memory database absent"
            return result
        database = client[mem_db]
        if _MEMORY_COLLECTION not in database.list_collection_names():
            result["error"] = "memory collection absent"
            return result

        collection = database[_MEMORY_COLLECTION]
        result["count"] = _count(collection, fast)
        latest = list(collection.find({}, {_MEMORY_TIME_FIELD: 1}).sort(_MEMORY_TIME_FIELD, -1).limit(1))
        earliest = list(collection.find({}, {_MEMORY_TIME_FIELD: 1}).sort(_MEMORY_TIME_FIELD, 1).limit(1))
        # pymongo hands back NAIVE datetimes — stamp them UTC rather than let them read as local.
        result["latest"] = _dt_to_utc(latest[0].get(_MEMORY_TIME_FIELD)) if latest else None
        result["earliest"] = _dt_to_utc(earliest[0].get(_MEMORY_TIME_FIELD)) if earliest else None
        result["ok"] = bool(result["latest"])
        if not result["ok"]:
            result["error"] = "the timeseries is empty"
    except PyMongoError as error:
        result["error"] = f"{type(error).__name__}: {error}"
    return result


def _epoch_to_utc(value: Any) -> Optional[str]:
    if value is None:
        return None
    try:
        return datetime.fromtimestamp(float(value), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except (TypeError, ValueError, OSError):
        return f"<unreadable: {value!r}>"


def _dt_to_utc(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return str(value)


def snapshot(uri: str, kb_db: str, mem_db: str, sandbox_db: str, fast: bool) -> dict:
    client = MongoClient(uri, serverSelectionTimeoutMS=10000)
    try:
        server_info = client.server_info()
        return {
            "captured_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "captured_on": platform.node(),
            "mongo_nodes": _redact(uri),
            "mongo_version": server_info.get("version"),
            "exact_counts": not fast,
            "databases_on_server": sorted(client.list_database_names()),
            "roles": {"kb": kb_db, "memory": mem_db, "sandbox": sandbox_db},
            "databases": {
                name: _snapshot_db(client, name, fast) for name in (kb_db, mem_db, sandbox_db)
            },
            "probes": {
                "vector_search": _probe_vector_search(client, kb_db),
                "brain_state": _probe_brain_state(client, mem_db),
                "memory_timeseries": _probe_memory_timeseries(client, mem_db, fast),
            },
        }
    finally:
        client.close()


# ==================================================================================================
# rendering
# ==================================================================================================

_GREEN, _RED, _YELLOW, _DIM, _OFF = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"


def _paint(text: str, color: str) -> str:
    return f"{color}{text}{_OFF}" if sys.stdout.isatty() else text


def render(snap: dict) -> None:
    print("\n  tokeniko — transplant snapshot")
    print(f"  {'captured':<14} {snap['captured_at']}  on  {snap['captured_on']}")
    print(f"  {'mongo':<14} {snap['mongo_nodes']}  (server {snap['mongo_version']})")
    print(f"  {'counts':<14} {'exact' if snap['exact_counts'] else 'ESTIMATED (--fast)'}")
    print(f"  {'databases':<14} {', '.join(snap['databases_on_server'])}")

    for role, name in snap["roles"].items():
        entry = snap["databases"].get(name, {})
        print(f"\n  {role.upper()}  —  {name}")
        if not entry.get("present"):
            print(f"    {_paint('ABSENT', _YELLOW)}")
            continue
        collections = entry.get("collections", {})
        if not collections:
            print("    (no collections)")
        total = 0
        for collection_name, row in collections.items():
            count = row.get("count")
            if isinstance(count, int):
                total += count
            marker = ""
            if "search_indexes" in row:
                indexes = row["search_indexes"]
                if isinstance(indexes, list):
                    marker = "   search: " + ", ".join(
                        f"{i.get('name')}[{i.get('status')}]" for i in indexes
                    )
                else:
                    marker = f"   search: {indexes}"
            printable = f"{count:>10,}" if isinstance(count, int) else f"{str(count):>10}"
            print(f"    {collection_name:<28} {printable}{marker}")
        print(f"    {_DIM}{'(total documents)':<28} {total:>10,}{_OFF}")

    print("\n  PROBES")
    vector = snap["probes"]["vector_search"]
    status = _paint("PASS", _GREEN) if vector.get("ok") else _paint("FAIL", _RED)
    detail = (
        f"index {vector.get('index')} · '{vector.get('probe_word')}' -> '{vector.get('top_word')}' "
        f"@ {vector.get('top_score')} · {vector.get('dimensions')} dims"
        if vector.get("ok") else vector.get("error", "?")
    )
    print(f"    {'$vectorSearch':<20} {status}  {detail}")

    brain = snap["probes"]["brain_state"]
    status = _paint("PASS", _GREEN) if brain.get("ok") else _paint("FAIL", _RED)
    if brain.get("wake_at_utc"):
        print(f"    {'brain_state':<20} {status}  born {brain.get('wake_at_utc')} "
              f"(expected {brain.get('birth_stamp_expected')})")
    else:
        print(f"    {'brain_state':<20} {status}  {brain.get('error', '?')}")
    if brain.get("wake_at_utc"):
        awake_hours = (brain.get("awake_s") or 0) / 3600.0
        print(f"    {'':<20}        awake_s {awake_hours:,.1f}h · asleep_since {brain.get('asleep_since')} "
              f"· last_thinking_at {_epoch_to_utc(brain.get('last_thinking_at'))}")
        print(f"    {'':<20}        source_cursors {brain.get('source_cursors_size')} "
              f"· wonder_queue {brain.get('wonder_queue_size')} "
              f"· digest_buffer {brain.get('digest_buffer_size')}")

    mem = snap["probes"]["memory_timeseries"]
    status = _paint("PASS", _GREEN) if mem.get("ok") else _paint("FAIL", _RED)
    if mem.get("ok"):
        print(f"    {'memory timeseries':<20} {status}  {mem.get('count'):,} items · "
              f"{mem.get('earliest')} -> {mem.get('latest')}")
    else:
        print(f"    {'memory timeseries':<20} {status}  {mem.get('error','?')}")
    print()


# ==================================================================================================
# comparison
# ==================================================================================================

def _flatten(snap: dict) -> dict[str, Any]:
    """The comparable surface of a snapshot: one flat key -> value map."""
    flat: dict[str, Any] = {}
    for role, name in snap.get("roles", {}).items():
        entry = snap.get("databases", {}).get(name, {})
        flat[f"db:{role}:present"] = bool(entry.get("present"))
        for collection_name, row in (entry.get("collections") or {}).items():
            flat[f"count:{role}:{collection_name}"] = row.get("count")
            if isinstance(row.get("search_indexes"), list):
                flat[f"search:{role}:{collection_name}"] = ",".join(
                    sorted(str(i.get("name")) for i in row["search_indexes"])
                )

    vector = snap.get("probes", {}).get("vector_search", {})
    flat["probe:vector_search:ok"] = bool(vector.get("ok"))

    brain = snap.get("probes", {}).get("brain_state", {})
    flat["probe:brain_state:ok"] = bool(brain.get("ok"))
    flat["probe:brain_state:wake_at_utc"] = brain.get("wake_at_utc")
    for field in _BRAIN_STATE_SIZED:
        flat[f"probe:brain_state:{field}_size"] = brain.get(f"{field}_size")

    mem = snap.get("probes", {}).get("memory_timeseries", {})
    flat["probe:memory:count"] = mem.get("count")
    flat["probe:memory:earliest"] = mem.get("earliest")
    flat["probe:memory:latest"] = mem.get("latest")
    return flat


# keys that must be IDENTICAL for the move to be a move rather than a partial copy. Everything else
# is reported too, but these are the ones that mean "his history did not survive".
_IDENTITY_KEYS = (
    "probe:brain_state:wake_at_utc",
    "probe:brain_state:ok",
    "probe:vector_search:ok",
    "probe:memory:earliest",
)


def compare(baseline: dict, live: dict) -> int:
    base_flat, live_flat = _flatten(baseline), _flatten(live)
    keys = sorted(set(base_flat) | set(live_flat))

    print(f"\n  BASELINE  {baseline.get('captured_at')} on {baseline.get('captured_on')} "
          f"({baseline.get('mongo_nodes')})")
    print(f"  LIVE      {live.get('captured_at')} on {live.get('captured_on')} "
          f"({live.get('mongo_nodes')})")
    if baseline.get("exact_counts") != live.get("exact_counts"):
        print(_paint("  ! one side used --fast (estimated counts) — the diff below is not arithmetic",
                     _YELLOW))
    print()

    mismatches = 0
    identity_broken = 0
    for key in keys:
        base_value, live_value = base_flat.get(key, "<absent>"), live_flat.get(key, "<absent>")
        if base_value == live_value:
            print(f"    {_paint('=', _DIM)} {key:<48} {base_value}")
            continue
        mismatches += 1
        delta = ""
        if isinstance(base_value, int) and isinstance(live_value, int):
            difference = live_value - base_value
            delta = f"   ({difference:+,})"
        severity = _RED if key in _IDENTITY_KEYS else _YELLOW
        if key in _IDENTITY_KEYS:
            identity_broken += 1
        print(f"    {_paint('!', severity)} {key:<48} {base_value}  ->  {live_value}{delta}")

    print()
    if mismatches == 0:
        print(_paint("  MATCH — every measured value is identical. Safe to proceed.", _GREEN))
        return 0

    if identity_broken:
        print(_paint(f"  MISMATCH — {mismatches} value(s) differ, {identity_broken} of them on the "
                     f"IDENTITY keys (birth stamp / vector search / first memory).", _RED))
        print("  DO NOT DELETE THE SOURCE. Something did not survive the copy.")
    else:
        print(_paint(f"  MISMATCH — {mismatches} value(s) differ; none on the identity keys.", _YELLOW))
        print("  Most likely the mind kept living between the two captures. Stop him, RE-CAPTURE the")
        print("  baseline, and compare again — an exact match is the only acceptable proof.")
    return 1


# ==================================================================================================
# main
# ==================================================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="read-only transplant verifier for tokeniko's databases (runbook §3.5)",
    )
    parser.add_argument("--uri", default=None, help="MongoDB URI (default: MONGO_URI from the package .env)")
    parser.add_argument("--out", default=None, help="write the snapshot to this JSON file")
    parser.add_argument("--compare", default=None, help="diff the live snapshot against this saved JSON")
    parser.add_argument("--fast", action="store_true",
                        help="estimated counts instead of exact ones (fast, but this is a VERIFICATION tool)")
    args = parser.parse_args()

    load_dotenv(os.path.join(_PKG_DIR, ".env"))
    uri = args.uri or os.getenv("MONGO_URI")
    if not uri:
        print("MONGO_URI is neither given with --uri nor set in the package .env", file=sys.stderr)
        return 2

    kb_db = os.getenv("MONGO_DB_NAME") or "tokeniko"
    mem_db = os.getenv("MONGO_DB_NAME_MEMORY") or "tokeniko_mem"
    sandbox_db = f"{mem_db}_test"     # tests/conftest.py: test_mem_db = f"{live_mem_db}_test"

    try:
        snap = snapshot(uri, kb_db, mem_db, sandbox_db, args.fast)
    except PyMongoError as error:
        print(f"could not reach mongo at {_redact(uri)}: {type(error).__name__}: {error}", file=sys.stderr)
        return 2

    render(snap)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            json.dump(snap, handle, indent=2, sort_keys=True, default=str)
            handle.write("\n")
        print(f"  snapshot written to {args.out}\n")

    if args.compare:
        with open(args.compare, encoding="utf-8") as handle:
            baseline = json.load(handle)
        return compare(baseline, snap)

    # a plain run still reports the health of the three probes through its exit code
    probes = snap["probes"]
    return 0 if all(probes[name].get("ok") for name in probes) else 1


if __name__ == "__main__":
    sys.exit(main())
