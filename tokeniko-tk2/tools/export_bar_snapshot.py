"""Export `dictionary_bar` to the offline snapshot. `python tools/export_bar_snapshot.py [--db NAME]`.

The acceptance suite has to run on a machine with no body reachable — the workshop, a fresh clone, a
CI box — and the bar lives in the db since T4b. So the rows are exported to
`tk2/dictionary/bar_snapshot.json`, pinned by their own fingerprint, and the suite reads that.

The pin is what keeps the copy honest, from both sides:

  - reading it verifies the pin (`policy.bar_snapshot`), so a hand edit of the pairs that does not
    recompute the hash is refused offline, with no database in sight;
  - `tests/test_dictionary_policy.py` asserts the snapshot's fingerprint against the DATABASE's
    whenever one is reachable, so rows that moved without an export are caught the first time
    anybody runs the suite near a body.

Run this after every bar version — which is after every migration that appends a pair. It reads and
writes nothing in the database: `--apply` has no meaning here, and the only thing it changes is one
file in the repo, for the Captain to read in the diff before it is committed.
"""

import argparse
import json
import sys
from pathlib import Path

from tk2.core import constants
from tk2.core.models import ALL_MODELS, DictionaryBarDoc
from tk2.datatier import boot_datatier, traps
from tk2.datatier.guard import DatabaseRefused
from tk2.dictionary import policy


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="export the acceptance bar to its offline snapshot")
    parser.add_argument(
        "--db",
        default=constants.TK2_BODY_DB,
        help=f"the database to read the bar from (default: {constants.TK2_BODY_DB})",
    )
    parser.add_argument(
        "--out",
        default=str(policy.SNAPSHOT_PATH),
        help="where to write the snapshot (default: the packaged one the suite reads)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare and report, writing nothing — what a gate would run",
    )
    args = parser.parse_args(argv)

    try:
        boot_datatier(ALL_MODELS, db_name=args.db)
    except DatabaseRefused as refused:
        print(f"guard: {refused}", file=sys.stderr)
        return 2

    rows = [row.model_dump() for row in traps.find_all(DictionaryBarDoc)]
    if not rows:
        print(f"{args.db} holds no bar rows — has migration 0003 been applied?", file=sys.stderr)
        return 1

    document = policy.snapshot_document(rows, source=args.db)
    path = Path(args.out)

    print(f"bar v{document['version']}: {len(document['pairs'])} live pairs")
    print(f"fingerprint {document['fingerprint']}")

    if path.exists():
        stored = json.loads(path.read_text(encoding="utf-8"))
        if stored.get("fingerprint") == document["fingerprint"]:
            print(f"{path.name} is already this bar; nothing to write.")
            return 0
        print(f"{path.name} holds {stored.get('fingerprint', '(none)')} — it is behind the rows.")
        if args.check:
            return 1

    if args.check:
        print(f"{path.name} does not exist yet.")
        return 1

    # Trailing newline and two-space indent: this file is read in diffs by a person.
    path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
