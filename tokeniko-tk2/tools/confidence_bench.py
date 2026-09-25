"""THE CONFIDENCE BENCH — do the station's own signals SEPARATE its good reads from its bad ones?

    PYTHONPATH=. ../.venv/bin/python tools/confidence_bench.py [--db NAME] [--all]

**THE BENCH BEFORE THE ANSWER** (the Captain's PRIO 1: *«establish the criteria and the test bench
BEFORE proposing an answer — enumerate the cases a mechanism must handle, then measure candidates
against them; never pick the tidy one and defend it»*). Requirement 4 says a zip carries «a
calibrated aggregate of coverage · repairs-taken · self-round-trip», and the aggregation weights are
E5's seventh micro-nn site. **Before any weight is chosen, the question is whether the signals carry
any separation at all** — a scalar built from signals that do not separate would be a number that
looks like knowledge and is noise, which is the placement floor's lesson (`db/0002`, `db/0007`, and
`docs/E1-dictionary/202609191500_the-placement-floor.md`, where the honest answer was that no floor
exists).

**THE TRUTH COLUMN IS THE DRILL GATE'S.** For each of the 87 hand-compiled sentences the gate says
whether the station read it as the drill did. That is the only thing here that knows the right
answer, and it is deliberately NOT one of the signals: a confidence that read the gate would be
marking its own homework.

**THE SIGNALS, all produced by the one pass that was happening anyway (req 6):**

    coverage     the fraction of tokens that reached the zip
    unplaced     words the compiler could not place — the same fact, counted
    abstained    readings the station declined rather than guess (req 8)
    defaulted    roles an ambiguous marker filled with its best-first answer, nobody choosing
    round trip   ESCALATION-ONLY: decompile, recompile, and ask whether it is the same zip

The round trip is printed for every case here because a bench measures; **the station will fire it
only when the cheap band is ambiguous**, which is the whole of req 6 and the answer to the author's
fear that this would be enormously slow.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tests.fixtures.drill import CASES  # noqa: E402
from tk2.language import standing_closed_classes  # noqa: E402
from tk2.language.compile import Compiler  # noqa: E402
from tk2.language.decompile import Decompiler  # noqa: E402
from tk2.language.utterance import compile_utterance  # noqa: E402
from tools.drill_gate import AGREED, DISAGREED, DRILL_CONTEXT, compare  # noqa: E402
from tools.roundtrip import canonical  # noqa: E402


def signals(compiled, decompiler, compiler, provider) -> dict:
    """Everything the station knows about its own read, and nothing it does not."""
    zip_ = compiled.zip
    said = decompiler.decompile(zip_)
    again = None
    if said.text.strip():
        skeletons = provider(said.text)
        if skeletons:
            again = compile_utterance(compiler, skeletons, DRILL_CONTEXT).zip
    return {
        "coverage": compiled.coverage,
        "unplaced": len(compiled.unplaced),
        "abstained": len(compiled.abstained),
        "defaulted": len(compiled.defaulted),
        "unsaid": len(said.unsaid),
        "refused": len(said.refused),
        "fixpoint": (again is not None and canonical(again) == canonical(zip_)),
    }


def run(argv=None) -> int:
    parser = argparse.ArgumentParser(description="do the station's signals separate its reads?")
    parser.add_argument("--db", default=None)
    parser.add_argument("--all", action="store_true", help="print every case, not the summary only")
    args = parser.parse_args(argv)

    from tk2.language.skeleton import StanzaSkeletons

    table = standing_closed_classes(args.db)
    compiler, provider = Compiler(table), StanzaSkeletons()
    decompiler = Decompiler(table, context=DRILL_CONTEXT)

    print("=" * 100)
    print("THE CONFIDENCE BENCH — the station's own signals against the drill gate's verdict")
    print("=" * 100)
    print(f"  closed classes    {len(table)} rows, v{table.version}")
    print(f"  the corpus        {len(CASES)} hand-compiled sentences\n")

    rows = []
    for case in CASES:
        skeletons = provider(case.sentence)
        if not skeletons:
            continue
        compiled = compile_utterance(compiler, skeletons, DRILL_CONTEXT)
        reading = compare(compiled.zip, case.zip, case.id, case.sentence)
        rows.append((case, signals(compiled, decompiler, compiler, provider), reading.verdict))

    if args.all:
        print(f"  {'case':<10} {'gate':<8} {'cover':>6} {'unpl':>5} {'abst':>5} {'dflt':>5} "
              f"{'unsaid':>7} {'refus':>6} {'fixpoint':>9}")
        print(f"  {'-' * 10} {'-' * 8} {'-' * 6} {'-' * 5} {'-' * 5} {'-' * 5} {'-' * 7} "
              f"{'-' * 6} {'-' * 9}")
        for case, got, verdict in rows:
            print(f"  {case.id:<10} {verdict:<8} "
                  f"{got['coverage']:>6.2f} {got['unplaced']:>5} {got['abstained']:>5} "
                  f"{got['defaulted']:>5} {got['unsaid']:>7} {got['refused']:>6} "
                  f"{str(got['fixpoint']):>9}")
        print()

    # **THE GATE HAS THREE VERDICTS AND THEY ARE THREE POPULATIONS.** `missing` is not agreement:
    # it is the station and the drill failing to reach common ground, which is E3 unfinished. Folding
    # it into `agreed` would flatter every signal at once.
    cheap = ("coverage", "unplaced", "abstained", "defaulted")
    dear = ("unsaid", "refused", "fixpoint")
    _report(rows, cheap + dear)

    # **AND A SECOND TRUTH COLUMN, WHICH IS THE ONE REQUIREMENT 6 ACTUALLY NEEDS.** The gate answers
    # «did the station read this as the drill did», and it can only answer it for a hand-compiled
    # corpus — 87 sentences, of which it disagrees with a handful. The FIXPOINT answers «did this zip
    # survive being said back and read again», it needs no hand-compiled truth at all, and it is what
    # the escalation ladder is FOR: the cheap band decides whether to pay for the second read, so the
    # question that matters is whether the cheap signals predict the expensive one.
    print("\n" + "=" * 100)
    print("  THE LADDER'S OWN QUESTION — do the CHEAP signals predict the ROUND TRIP? (req 6)")
    print("=" * 100)
    survived = [(case, got) for case, got, _ in rows if got["fixpoint"]]
    moved = [(case, got) for case, got, _ in rows if not got["fixpoint"]]
    print(f"  {len(survived)} came back as themselves · {len(moved)} did not\n")
    print(f"  {'signal':<12} {'survived':>12} {'moved':>12}   overlap")
    print(f"  {'-' * 12} {'-' * 12} {'-' * 12}   {'-' * 46}")
    for name in cheap:
        ours = [float(got[name]) for _, got in survived]
        theirs = [float(got[name]) for _, got in moved]
        print(f"  {name:<12} {sum(ours) / max(len(ours), 1):>12.3f} "
              f"{sum(theirs) / max(len(theirs), 1):>12.3f}   "
              f"survived [{min(ours, default=0):.2f}–{max(ours, default=0):.2f}]  "
              f"moved [{min(theirs, default=0):.2f}–{max(theirs, default=0):.2f}]")

    print("\n  **A MEAN IS NOT A SEPARATION, AND AN OVERLAPPING RANGE IS A REFUSAL** — for a")
    print("  THRESHOLD. The ladder does not need one; it needs its ENDS to be clean.\n")

    # **AND THAT IS THE QUESTION, ASKED PROPERLY.** Requirement 6 does not ask for a number that
    # ranks every sentence — it asks for a BAND: high enough to proceed on, low enough to ask on,
    # and an ambiguous middle that pays for the second read. A band needs its ends to be reliable
    # and does not care what the middle does, so a signal that overlaps everywhere can still be
    # perfectly good at saying «this one is clean».
    print("=" * 100)
    print("  THE BANDS — where the cheap signals are DECISIVE, and how much of the corpus that is")
    print("=" * 100)
    bands = (
        ("nothing to report   ", lambda g: (g["coverage"] == 1.0 and not g["unplaced"]
                                            and not g["abstained"] and not g["defaulted"])),
        ("a word unplaced     ", lambda g: g["unplaced"] > 0),
        ("a role DEFAULTED    ", lambda g: g["defaulted"] > 0),
        ("the station ABSTAIN ", lambda g: g["abstained"] > 0),
        ("anything at all     ", lambda g: (g["coverage"] < 1.0 or g["unplaced"] or g["abstained"]
                                            or g["defaulted"])),
    )
    print(f"  {'band':<22} {'cases':>6} {'survived':>9} {'moved':>7}   what it would be worth")
    print(f"  {'-' * 22} {'-' * 6} {'-' * 9} {'-' * 7}   {'-' * 38}")
    for label, holds in bands:
        inside = [got for _, got, _ in rows if holds(got)]
        kept = [got for got in inside if got["fixpoint"]]
        share = len(kept) / len(inside) if inside else 0.0
        verdict = ("DECISIVE" if inside and (share == 1.0 or share == 0.0)
                   else f"{share:.0%} survive — not decisive")
        print(f"  {label:<22} {len(inside):>6} {len(kept):>9} {len(inside) - len(kept):>7}   "
              f"{verdict}")

    print("\n  A band is worth having when it is DECISIVE — every case inside it goes the same way.")
    print("  One that is 80% right is a guess with a number on it, and requirement 8 calls that the")
    print("  sin: half-understood is legal, wrongly-understood is not.")
    return 0


def _report(rows, names) -> None:
    """Each signal's mean in each of the gate's three verdicts, and the range it actually spans."""
    groups = {AGREED: [], DISAGREED: [], "missing": []}
    for _, got, verdict in rows:
        groups.setdefault(verdict, []).append(got)
    counts = " · ".join(f"{len(v)} {k}" for k, v in groups.items())
    print(f"  {counts}\n")
    print(f"  {'signal':<12} {'agreed':>10} {'DISAGREED':>11} {'missing':>10}   "
          f"the range each one spans")
    print(f"  {'-' * 12} {'-' * 10} {'-' * 11} {'-' * 10}   {'-' * 40}")
    for name in names:
        means = []
        for key in (AGREED, DISAGREED, "missing"):
            values = [float(got[name]) for got in groups.get(key, ())]
            means.append(sum(values) / len(values) if values else float("nan"))
        everything = [float(got[name]) for got in sum(groups.values(), [])]
        print(f"  {name:<12} {means[0]:>10.3f} {means[1]:>11.3f} {means[2]:>10.3f}   "
              f"[{min(everything, default=0):.2f} – {max(everything, default=0):.2f}]")


if __name__ == "__main__":
    raise SystemExit(run())
