"""Mine the definitions for analytic edges, simulate them, and — the Captain's hand — approve them.

    PYTHONPATH=. ../.venv/bin/python tools/curate_dictionary.py propose [--pairs a.p:b.q,…]
    PYTHONPATH=. ../.venv/bin/python tools/curate_dictionary.py simulate --proposals PATH
    PYTHONPATH=. ../.venv/bin/python tools/curate_dictionary.py approve  --proposals PATH \\
        --db tokeniko_tk2_body --build … --i-am-the-captain --authorized "the Captain, …"

Requirement 20, the Captain's ruling of 2026-08-12: a manual edge may enter R only when it is
ANALYTIC — stated in a definition — never when it is contingent. Sayings, slang and context-bound
readings are knowledge, and knowledge lives in the KB.

`propose` and `simulate` write nothing at all: they mine, they print, and `simulate` moves an
in-memory copy of R. `approve` is the only subcommand that touches the base, and it refuses to run
without `--i-am-the-captain` and `--authorized`. The guard is not ceremony — analytic versus
contingent is exactly the call a miner cannot make, and a script able to mint its own curated cell
would have quietly taken that judgement over. The refusal itself lives in
`tk2.dictionary.curation.assert_captains_hand`, where a test can hold it to account.

THE DEFAULT WORKLIST IS DERIVED, NOT TYPED. The prototype carried «the four bar misses» as a list in
its config; here the same four are computed — the bar's NEAR pairs that R leaves MUTE are exactly
the pairs a definitional edge might close, and a list would go stale the first time R moved.
"""

import argparse
import json
import sys
import time
from pathlib import Path

from tk2.datatier.policy_source import standing_bar, standing_policy
from tk2.dictionary import curation, policy, relations
from tk2.dictionary.build import build_base
from tk2.dictionary.wordnet import WordNetProvider, wordnet_lexicon


def load(args):
    """The standing policy, and the base it describes. Printed before anything is mined."""
    rows, policy_source = standing_policy(args.db)
    bar, bar_rows, bar_source = standing_bar(args.db)
    config = policy.config_from_rows(rows, bar_rows)
    print(f"policy        {policy_source}")
    print(f"bar           {bar_source}, {len(bar)} pairs")
    print(f"config        {config.fingerprint()[:12]}…")

    if args.db and args.build:
        from tk2.datatier import database
        from tk2.datatier.matrix_store import MongoMatrixStore

        store = MongoMatrixStore(database(args.db))
        built = store.matrix(args.build, "base_r")
        print(f"base          {args.db}.base_r build='{args.build}' — {len(built.keys):,} dimensions")
        return config, rows, bar_rows, built

    started = time.time()
    provider = WordNetProvider(wordnet_lexicon())
    print("base          rebuilt in memory from the rows (no --build named)", flush=True)
    matrix = build_base(config, provider).relational
    print(f"              {len(matrix.keys):,} dimensions · {matrix.stats()['nonzero']:,} cells "
          f"({time.time() - started:.0f}s)")
    return config, rows, bar_rows, matrix


def worklist(args, matrix, bar) -> list[tuple[str, str]]:
    """The pairs to mine: what `--pairs` names, or the bar's own misses."""
    if args.pairs:
        out = []
        for chunk in args.pairs.split(","):
            chunk = chunk.strip()
            if ":" not in chunk:
                raise SystemExit(f"--pairs wants `a.p:b.q` items; got {chunk!r}")
            a, b = chunk.split(":", 1)
            out.append((a.strip().lower(), b.strip().lower()))
        return out

    misses = []
    for pair in bar:
        if pair.verdict != "NEAR":
            continue
        forward, reverse = relations.stated_between(matrix, pair.a, pair.b)
        if forward is None and reverse is None:
            misses.append((pair.a, pair.b))
    return misses


# ------------------------------------------------------------------------------------------------
# propose
# ------------------------------------------------------------------------------------------------


def cmd_propose(args) -> int:
    config, _rows, _bar_rows, matrix = load(args)
    provider = WordNetProvider(wordnet_lexicon())
    pairs = worklist(args, matrix, config.bar)

    print()
    print("=" * 96)
    print(f"PROPOSALS — {len(pairs)} pair(s), mined from definitions only")
    print("=" * 96)
    print("requirement 20: a curated edge must be ANALYTIC — stated in a definition. Contingent")
    print("knowledge stays in the KB. Nothing here is written; the Captain approves by eye.")
    print()

    proposals = []
    for a, b in pairs:
        proposals.extend(curation.propose_pair(a, b, provider, config.relations, config.closure.senses))
    proposals.sort(key=lambda p: (-p.weight, p.source_key, p.target_key))

    space = set(matrix.keys)
    for proposal in proposals:
        outside = "" if {proposal.source_key, proposal.target_key} <= space else \
            "   [not a dimension of the base — no axis to write to]"
        print(f"  {proposal.id:<26} {proposal.relation:<10} {proposal.weight:+.2f}{outside}")
        print(f"      {proposal.evidence}")

    silent = [
        (a, b) for a, b in pairs
        if not any({p.source_key, p.target_key} == {a, b} for p in proposals)
    ]
    if silent:
        print()
        print(f"=== NO DEFINITION SPEAKS ({len(silent)}) ===")
        print("  neither gloss names the other word — an honest «curation cannot reach this one»,")
        print("  not a tuning failure.")
        for a, b in silent:
            print(f"  {a} ~ {b}")

    skips = curation.self_reference_skips(pairs, provider, config.closure.senses)
    if skips:
        print()
        print(f"=== SKIPPED AS SELF-REFERENCE ({len(skips)}) ===")
        print("  a definition naming its own headword under another POS is a tautology, not a")
        print("  stated relation between two concepts.")
        for source, target, evidence in skips:
            print(f"  {source} -> {target}   {evidence}")

    if args.proposals:
        Path(args.proposals).write_text(
            json.dumps([p.as_dict() for p in proposals], indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print()
        print(f"wrote {args.proposals} — {len(proposals)} pending proposal(s). The base is untouched.")
    return 0


# ------------------------------------------------------------------------------------------------
# simulate
# ------------------------------------------------------------------------------------------------


def read_proposals(path: str) -> list[curation.Proposal]:
    """The proposals as they were PROPOSED — the table the Captain read, not a re-mining of it.

    Re-mining at approval time would let a resource update or a policy edit change what he approved
    between the reading and the writing, which is the one thing an approval must not allow.
    """
    stored = json.loads(Path(path).read_text(encoding="utf-8"))
    return [curation.Proposal.from_dict(row) for row in stored]


def cmd_simulate(args) -> int:
    config, _rows, _bar_rows, matrix = load(args)
    proposals = read_proposals(args.proposals)
    applied = curation.apply(matrix, proposals, config.relations)

    print()
    print("=" * 96)
    print("SIMULATION — NOTHING IS COMMITTED")
    print("=" * 96)
    for row_key, cell in applied.written:
        print(f"  applied   {row_key:>14} -> {cell.column:<14} {cell.relation:<24} {cell.weight:+.2f}")
    for note in applied.overwrites:
        print(f"  OVERWRITE {note}")
    for pid in applied.unwritable:
        print(f"  SKIPPED   {pid}: not a dimension of this base — no axis to write to")

    print()
    print(f"  {'pair':<26} {'exp':<5} {'cosine before':>14} {'after':>10}   cell after")
    print(f"  {'-' * 26} {'-' * 5} {'-' * 14} {'-' * 10}   {'-' * 30}")
    moved = 0
    for pair in config.bar:
        before = matrix.cosine(pair.a, pair.b)
        after = applied.matrix.cosine(pair.a, pair.b)
        if before is None or after is None:
            print(f"  {pair.a + ' ~ ' + pair.b:<26} {pair.verdict:<5} "
                  f"{'unscorable — a key is not a dimension':>26}")
            continue
        forward, reverse = relations.stated_between(applied.matrix, pair.a, pair.b)
        changed = "*" if abs(after - before) > 1e-9 else " "
        moved += 1 if changed == "*" else 0
        cell = forward or reverse
        print(f" {changed}{pair.a + ' ~ ' + pair.b:<26} {pair.verdict:<5} {before:>+14.3f} "
              f"{after:>+10.3f}   {(cell.relation + ' ' + format(cell.weight, '+.2f')) if cell else 'MUTE'}")

    print()
    print(f"  * = the proposals moved this pair ({moved} of {len(config.bar)})")
    print("  requirement 19: the CELL answers «is there a stated relation», the COSINE «do their")
    print("  worlds overlap». Both are printed; neither is folded into the other.")
    print()
    print("=== END SIMULATION — the base was never opened for writing ===")
    return 0


# ------------------------------------------------------------------------------------------------
# approve — THE CAPTAIN'S HAND
# ------------------------------------------------------------------------------------------------


def cmd_approve(args) -> int:
    approval = curation.Approval(
        i_am_the_captain=args.i_am_the_captain,
        authorized_by=args.authorized,
    )
    try:
        curation.assert_captains_hand(approval)
    except curation.NotTheCaptainsHand as refusal:
        print(refusal)
        print("Nothing was written. `simulate` answers «would it work?» without this.")
        return 2
    if not (args.db and args.build):
        print("REFUSED: approving writes into a stored base, so it must name one (--db --build).")
        return 2

    from tk2.core.models import DictionaryBuildDoc
    from tk2.datatier import MigrationWriter, database
    from tk2.datatier.matrix_store import MongoMatrixStore

    config, rows, bar_rows, matrix = load(args)
    proposals = read_proposals(args.proposals)
    applied = curation.approve(matrix, proposals, config.relations, approval)

    db = database(args.db)
    written = MongoMatrixStore(db).write(applied.matrix, args.build)

    stats = applied.matrix.stats()
    counts = {
        "keys": len(applied.matrix.keys),
        "r_cells": stats["nonzero"],
        "r_curated_cells": stats["by_source"].get("curated", 0),
        "r_negative": stats["negative"],
    }
    MigrationWriter(db).insert(
        DictionaryBuildDoc,
        policy.manifest_row(
            config, rows, bar_rows, counts, approval.authorized_by,
            note=f"curation: {len(applied.written)} curated cell(s) approved into build "
                 f"'{args.build}' from {args.proposals}",
        ),
    )
    print()
    print(f"written: {args.db}.base_r build='{args.build}' — {written:,} rows, "
          f"{counts['r_curated_cells']} curated cell(s), and a manifest row recording the hand.")
    for note in applied.overwrites:
        print(f"  OVERWROTE {note}")
    return 0


# ------------------------------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="curate_dictionary", description=__doc__.split("\n")[0])
    parser.add_argument("--db", default=None, help="read the policy (and the base) from this database")
    parser.add_argument("--build", default=None, help="the stored build label to read and amend")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("propose", help="mine definitions for analytic edges — proposals only")
    p.add_argument("--pairs", help="`a.p:b.q,c.r:d.s` (default: the bar's NEAR pairs R leaves mute)")
    p.add_argument("--proposals", help="write the pending proposals here, for simulate and approve")
    p.set_defaults(run=cmd_propose)

    p = sub.add_parser("simulate", help="apply pending proposals to an IN-MEMORY R and re-read the bar")
    p.add_argument("--proposals", required=True)
    p.set_defaults(run=cmd_simulate)

    p = sub.add_parser("approve", help="THE CAPTAIN'S HAND ONLY — writes curated cells into R")
    p.add_argument("--proposals", required=True)
    p.add_argument("--i-am-the-captain", action="store_true",
                   help="assert that a human read the evidence and judged it analytic")
    p.add_argument("--authorized", default="",
                   help="who authorized it and when — recorded in the manifest, so a curated cell "
                        "can always be traced back to the hand that allowed it")
    p.set_defaults(run=cmd_approve)

    args = parser.parse_args(argv)
    try:
        return args.run(args)
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
