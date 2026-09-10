"""Read a stored base back out and check that it is the base that was written.

    PYTHONPATH=. ../.venv/bin/python tools/verify_base.py --db tokeniko_tk2_body
    PYTHONPATH=. ../.venv/bin/python tools/verify_base.py --db tokeniko_tk2_body --build 3940735d6b18
    PYTHONPATH=. ../.venv/bin/python tools/verify_base.py --db … --build … --drop-unsealed

THE OTHER HALF OF THE APPLY. `tools/build_dictionary.py --apply` writes each matrix in chunks,
counts the rows back out of the database and seals it; this reads every row back, recomputes the
matrix's fingerprint from what is stored, and compares. The two answer different questions and the
second is the one worth running after a slow write across a network:

    the seal says      «all of the rows I sent arrived»
    this says          «and what came back is what left»

WHAT IT CHECKS, in the order a failure would matter:
  1. every matrix of the build carries a SEAL. No seal is not a warning — the store refuses to read
     an unsealed matrix at all, and this reports that refusal rather than hiding it.
  2. the DIMENSION REGISTRY: the row count the seal claims, and that the indices run 0..n-1 with no
     gap. A registry with a hole is a key space in which every index past the hole means another
     word, and no cell would look wrong.
  3. each MATRIX: rows, cells and the fingerprint, recomputed from the stored documents.
  4. the MANIFEST row, if there is one, against the counts the build recorded.

Read-only unless it is asked otherwise, and the one thing it may destroy is named: `--drop-unsealed`
removes a build that has no seals at all — the wreckage of an interrupted apply — and it refuses to
touch a build that carries even one, because a partly-sealed build is a thing to look at rather than
a thing to sweep away.
"""

import argparse
import json
import sys
import time
from pathlib import Path

from tk2.core.models import BaseKeyDoc, DictionaryBuildDoc
from tk2.datatier import database
from tk2.datatier.guard import DatabaseRefused
from tk2.datatier.matrix_store import MATRIX_MODELS, MongoMatrixStore


def verify(build: str, store: MongoMatrixStore) -> dict:
    """One build, read back whole. Returns what was found; prints it as it goes, because the read
    is minutes long at the full base and a silent instrument is indistinguishable from a hung one."""
    started = time.time()
    seals = store.seals(build)
    print(f"  build {build!r}")
    print(f"    seals            {', '.join(sorted(seals)) or 'NONE — nothing here reads'}")

    findings = {"build": build, "seals": sorted(seals), "matrices": {}, "whole": True}

    if BaseKeyDoc.Settings.name in seals:
        registry = store.verify_keys(build)
        ok = registry["whole"]
        findings["matrices"][BaseKeyDoc.Settings.name] = registry
        findings["whole"] &= ok
        print(f"    {BaseKeyDoc.Settings.name:<16} {registry['rows']:>7,} dimensions "
              f"(sealed {registry['rows_sealed']:,}) · indices contiguous: "
              f"{'yes' if registry['contiguous'] else 'NO'} · {registry['digest'][:16]}…  "
              f"{'OK' if ok else 'FAILED'}")
    else:
        findings["whole"] = False
        print(f"    {BaseKeyDoc.Settings.name:<16} NO SEAL — the dimension order does not read, so "
              f"neither matrix means anything")

    for name in MATRIX_MODELS:
        if name not in seals:
            present = store.stored_rows(build, name)
            if present:
                findings["whole"] = False
                print(f"    {name:<16} NO SEAL and {present:,} rows present — the wreckage of an "
                      f"interrupted write. It does not read; re-run the build's --apply.")
            else:
                print(f"    {name:<16} absent (this build declares none)")
            continue
        found = store.verify(build, name)
        findings["matrices"][name] = found
        findings["whole"] &= found["whole"]
        print(f"    {name:<16} {found['rows']:>7,} rows (sealed {found['rows_sealed']:,}) · "
              f"{found['cells']:>9,} cells (sealed {found['cells_sealed']:,})")
        print(f"    {'':<16} fingerprint {found['fingerprint'][:16]}… against sealed "
              f"{found['fingerprint_sealed'][:16]}…  "
              f"{'OK' if found['whole'] else 'FAILED'}")

    # A manifest row does not carry the build LABEL at all — `DictionaryBuildDoc` records the
    # policy a build ran and not the label its rows are under — so it is found by the one link that
    # exists: the default label IS the head of the config fingerprint. A build labelled by hand
    # breaks that link, and the run says so rather than showing the wrong row with a straight face.
    ledger = store.database[DictionaryBuildDoc.Settings.name]
    manifest = ledger.find_one({"config_fingerprint": {"$regex": f"^{build}"}})
    if manifest is None:
        newest = ledger.find_one({}, sort=[("created_at", -1)])
        if newest is not None:
            print(f"    manifest         no ledger row whose config fingerprint starts with "
                  f"{build!r}; the newest row in the ledger is shown instead")
        manifest = newest
    if manifest:
        counts = manifest.get("counts", {})
        findings["manifest"] = {"config_fingerprint": manifest.get("config_fingerprint"),
                                "counts": counts,
                                "authorization": manifest.get("authorization")}
        print(f"    manifest         config {str(manifest.get('config_fingerprint'))[:16]}… · "
              f"policy v{manifest.get('policy_version')} · bar v{manifest.get('bar_version')} · "
              f"{manifest.get('authorization')}")
        # The manifest counts what the BUILD counted (stated cells, the axis excluded); the seal
        # counts what was STORED (the diagonal included). They are two different numbers on purpose
        # and are printed side by side rather than asserted equal.
        for name, key in (("base_r", "r_cells"), ("base_d", "d_cells")):
            if key in counts and name in findings["matrices"]:
                stored = findings["matrices"][name]["cells"]
                print(f"    {'':<16} {name}: manifest states {counts[key]:,} cells, "
                      f"{stored:,} stored (the difference is the declared diagonal)")
    else:
        print("    manifest         none in this database — a base with no ledger row")

    print(f"    read back in {time.time() - started:.0f}s — "
          f"{'WHOLE' if findings['whole'] else 'NOT WHOLE'}")
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="verify a stored base against its own seals")
    parser.add_argument("--db", required=True, help="the database to read (the guard has the last word)")
    parser.add_argument("--build", default=None,
                        help="the build label (default: every build the database holds)")
    parser.add_argument("--json", default=None, help="also write the findings here")
    parser.add_argument(
        "--drop-unsealed",
        action="store_true",
        help="REMOVE a build that carries NO seal at all — the wreckage of an interrupted apply. "
             "Refuses a build that carries even one seal: a partly-sealed build is a thing to look "
             "at, not a thing to sweep away",
    )
    args = parser.parse_args(argv)

    try:
        db = database(args.db)
    except DatabaseRefused as refused:
        print(f"guard: {refused}", file=sys.stderr)
        return 2

    store = MongoMatrixStore(db)
    builds = (args.build,) if args.build else store.builds()
    print("=" * 96)
    print(f"VERIFY THE BASE — {args.db}")
    print("=" * 96)
    if not builds:
        print("  no build has ever been written to this database.")
        return 0

    findings = []
    for build in builds:
        found = verify(build, store)
        findings.append(found)
        if args.drop_unsealed:
            if found["seals"]:
                print(f"    NOT DROPPED: build {build!r} carries {len(found['seals'])} seal(s). "
                      f"Only a build with none is wreckage.")
            else:
                gone = store.drop(build)
                print(f"    DROPPED: {gone}")
        print()

    whole = [f["build"] for f in findings if f["whole"]]
    print(f"{len(whole)} of {len(findings)} build(s) read back whole"
          f"{': ' + ', '.join(whole) if whole else ''}")

    if args.json:
        Path(args.json).write_text(
            json.dumps({"db": args.db, "builds": findings}, indent=2, default=str) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {args.json}")
    return 0 if len(whole) == len(findings) else 1


if __name__ == "__main__":
    raise SystemExit(main())
