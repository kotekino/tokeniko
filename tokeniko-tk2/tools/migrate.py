"""Apply the pending migrations. `python tools/migrate.py [--db NAME] [--list]`.

The database is NAMED and the guard has the last word — this tool can reach the body's sandbox and
the test database, and nothing else. tk1's databases are refused by name before the whitelist is
even consulted.

Run from `tokeniko-tk2/`. Applying is the Captain's hand: this script does the work, but it is
started by a person who meant to deploy.
"""

import argparse
import sys

from tk2 import migrations
from tk2.core import constants
from tk2.datatier import database
from tk2.datatier.guard import DatabaseRefused


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="apply pending tk2 migrations")
    parser.add_argument(
        "--db",
        default=constants.TK2_BODY_DB,
        help=f"target database (default: {constants.TK2_BODY_DB})",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="show what is applied and what is pending, and change nothing",
    )
    parser.add_argument(
        "--upto",
        type=int,
        default=None,
        metavar="N",
        help="stop after migration N — a deploy that must land in stages, and how the E0 gate "
        "brings a body up on 0001 and moves it while it runs",
    )
    args = parser.parse_args(argv)

    try:
        db = database(args.db)
    except DatabaseRefused as refused:
        print(f"guard: {refused}", file=sys.stderr)
        return 2

    try:
        done = migrations.applied(db)
        waiting = migrations.pending(db)
    except migrations.MigrationError as error:
        print(f"migrations: {error}", file=sys.stderr)
        return 1

    if args.upto is not None:
        waiting = [m for m in waiting if m.number <= args.upto]

    print(f"db {db.name}: {len(done)} applied, {len(waiting)} pending")

    if args.list:
        for migration in migrations.discover():
            mark = "applied" if migration.number in done else "PENDING"
            print(f"  {mark:>7}  {migration.label}")
        return 0

    if not waiting:
        print("nothing to do.")
        return 0

    for migration in waiting:
        print(f"  applying {migration.label} ...", flush=True)
        migrations.apply(db, migration)
        print(f"  applied  {migration.label}")

    print(f"done: {len(waiting)} migration(s) applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
