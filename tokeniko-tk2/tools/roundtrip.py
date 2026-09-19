"""THE ROUND TRIP — decompile a zip, compile it again, and ask whether it is the same thought.

    PYTHONPATH=. ../.venv/bin/python tools/roundtrip.py [--db tokeniko_tk2] [--all]

**THE TEST COMES WITH THE ANALOGY** (parser-compiler req 9, the Captain 2026-09-19). Decompiled
source is never the original source; it is A source that compiles to the same object. So the question
is never «does this read like the sentence we started from» — it is **does it compile to the zip we
started from**, which is the one property the decompiler owes.

    the drill's own zip  ->  decompile  ->  stanza  ->  compile  ->  a zip  ->  compare
                                                                               ^
                                                             `tools.drill_gate.compare`, unchanged

The comparator is the drill gate's, deliberately. It already scores AGREEMENT rather than equality,
pairs rows by what they are about, abstains on variables and OPENs, and reads the prefix and the
joins since 2026-09-19 — so the instrument that judges the compiler judges the decompiler too, and a
defect cannot hide in the seam between two graders.

**THE CORPUS IS THE DRILL'S 87 HAND-COMPILED ZIPS**, not the station's own output, and that matters:
compiling our own parse back would measure the decompiler against a reading that may itself be
wrong. The drill's zips are what the format says the world looks like.

**WHAT IT REPORTS, in three states and never two**: a zip the decompiler REFUSED to say (it would
have had to lie) is not a failure of the round trip, it is the decompiler declining, and it is
counted apart from the sentences that came back changed.
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
from tools.drill_gate import DISAGREED, DRILL_CONTEXT, compare  # noqa: E402


def run(argv=None) -> int:
    parser = argparse.ArgumentParser(description="zip -> sentence -> zip, and are they the same?")
    parser.add_argument("--db", default=None, help="read the closed classes from this database")
    parser.add_argument("--all", action="store_true", help="print every case, not only the failures")
    args = parser.parse_args(argv)

    from tk2.language.skeleton import StanzaSkeletons

    table = standing_closed_classes(args.db)
    compiler, decompiler, provider = Compiler(table), Decompiler(table), StanzaSkeletons()

    print("=" * 96)
    print("THE ROUND TRIP — the drill's own zips, decompiled and compiled again (req 9)")
    print("=" * 96)
    print(f"  closed classes    {len(table)} rows, v{table.version} — {table.source}")
    print(f"  the corpus        {len(CASES)} hand-compiled zips\n")

    said = refused = unparsed = 0
    agreed, changed = [], []
    for case in CASES:
        out = decompiler.decompile(case.zip)
        if not out.text.strip():
            refused += 1
            continue
        said += 1
        skeletons = provider(out.text)
        if not skeletons:
            unparsed += 1
            continue
        again = compile_utterance(compiler, skeletons, DRILL_CONTEXT).zip
        reading = compare(again, case.zip, case.id, out.text)
        (changed if reading.verdict == DISAGREED else agreed).append((case, out, reading))

    for case, out, reading in (changed if not args.all else changed + agreed):
        mark = "CHANGED" if reading.verdict == DISAGREED else "same"
        print(f"  {case.id:8} {mark:8} « {out.text[:62]} »")
        print(f"           was « {case.sentence[:62]} »")
        for conflict in reading.conflicts[:3]:
            print(f"      ⚑ {conflict}")

    print(f"\n  SAID            {said} of {len(CASES)} zips reached a sentence")
    print(f"  REFUSED         {refused} — the decompiler declined rather than say something the "
          f"zip does not")
    print(f"  SAME THOUGHT    {len(agreed)} of the {said - unparsed} that were read back")
    print(f"  CHANGED         {len(changed)} — the round trip's only real failure")
    if unparsed:
        print(f"  UNPARSED        {unparsed} — stanza made nothing of the sentence")
    print("\n  **REFUSED IS NOT A FAILURE.** A zip the decompiler cannot say without lying is one it")
    print("  must not say at all (req 8, in the other direction). The number to watch is CHANGED.")
    return 1 if changed else 0


if __name__ == "__main__":
    raise SystemExit(run())
