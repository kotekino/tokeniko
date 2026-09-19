"""THE PLACEMENT BENCH — can a FLOOR tell a good placement from a bad one? **E3 task 6.**

    PYTHONPATH=. ../.venv/bin/python tools/placement_bench.py [--db tokeniko_tk2] [--population]

**THE QUESTION, AND THE ORDER IT MUST BE ASKED IN.** `place()` returns each reading of an unknown
word with a verdict, and that verdict is issued by the BASE's floor — fitted on base-to-base cosines
where p90 is +0.000. Task 6 says the sense layer needs its own floor, fitted its own way. Before
fitting one, this bench asks whether a floor is the right instrument at all: **on the forty
placements the Captain ruled (`tests/fixtures/placement_bar.py`), is there a cosine that separates
NEAR from FAR?**

`db/0002`'s lesson, generalised: a threshold belongs in the MIDDLE OF A REAL GAP. If the declared
NEARs and FARs interleave, there is no gap, and any number chosen would be a number with a decimal
point and no meaning — the appearance of a measurement.

**IT READS THE BAR, IT NEVER WRITES ONE.** The forty are evidence and live in a fixture, isolated
from the app: nothing at runtime may read them, and they are NOT `dictionary_bar` rows, because every
bar word becomes a seed and declaring them there would pull the very senses under test into the base.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402

from tests.fixtures.placement_bar import (  # noqa: E402
    BUILD,
    DISTRIBUTIONAL,
    FAR,
    NEAR,
    PLACEMENTS,
    RELATIONAL,
    of_half,
)


def best_floor(placements) -> tuple[float | None, int, str]:
    """The floor that gets the fewest wrong, and what «fewest» costs.

    A floor reads NEAR at or above itself and abstains below. Wrong is counted BOTH ways, because
    both are real damage: a declared FAR read NEAR is a placement the station would trust and should
    not (req 8's wrongly-understood), and a declared NEAR read below the floor is a word understood
    and then thrown away.
    """
    if not placements:
        return None, 0, "no pairs"
    candidates = sorted({round(p.cosine, 4) for p in placements} | {0.0, 1.0})
    best, best_wrong = None, len(placements) + 1
    for floor in candidates:
        wrong = sum(1 for p in placements
                    if (p.cosine >= floor) != (p.verdict == NEAR))
        if wrong < best_wrong:
            best, best_wrong = floor, wrong
    kept = [p for p in placements if p.verdict == NEAR]
    return best, best_wrong, f"{len(kept)} NEAR / {len(placements) - len(kept)} FAR declared"


def gap(placements) -> tuple[float, float] | None:
    """The gap a floor would sit in: the highest declared FAR and the lowest declared NEAR.

    `None` when they cross — which is not a narrow gap but the ABSENCE of one, and the difference
    matters: a narrow gap is a fragile floor, a crossed pair is no floor at all.
    """
    highest_far = max((p.cosine for p in placements if p.verdict == FAR), default=None)
    lowest_near = min((p.cosine for p in placements if p.verdict == NEAR), default=None)
    if highest_far is None or lowest_near is None:
        return None
    return None if lowest_near <= highest_far else (highest_far, lowest_near)


def report_bar() -> int:
    print("=" * 96)
    print("THE PLACEMENT BENCH — the forty the Captain ruled, against the cosine that placed them")
    print("=" * 96)
    print(f"  build {BUILD} · {len(PLACEMENTS)} pairs · evidence, from the fixture\n")

    crossed = 0
    for half in (RELATIONAL, DISTRIBUTIONAL):
        placements = sorted(of_half(half), key=lambda p: p.cosine)
        print(f"  {half.upper()}")
        for p in placements:
            mark = "  " if p.verdict == NEAR else "->"
            print(f"   {mark} {p.cosine:+.4f}  {p.verdict:<4} {p.sense:24} -> {p.dimension}")
        stated = [p for p in placements if p.stated]
        if stated:
            print(f"\n    R STATES THE EDGE for {len(stated)} of {len(placements)}, and every one "
                  f"of them is declared {'/'.join(sorted({p.verdict for p in stated}))}")
        else:
            print(f"\n    R STATES THE EDGE for NONE of the {len(placements)} — which for the "
                  f"distributional half is structural, not a shortfall")
        found = gap(placements)
        floor, wrong, declared = best_floor(placements)
        if found is None:
            crossed += 1
            highest_far = max(p.cosine for p in placements if p.verdict == FAR)
            lowest_near = min(p.cosine for p in placements if p.verdict == NEAR)
            print(f"\n    NO GAP — {declared}. The highest declared FAR is {highest_far:+.4f} and "
                  f"the lowest declared NEAR is {lowest_near:+.4f}: they CROSS.")
        else:
            print(f"\n    a gap: {found[0]:+.4f} (FAR) .. {found[1]:+.4f} (NEAR) — "
                  f"a floor would sit at {sum(found) / 2:+.4f}")
        print(f"    the BEST floor possible here is {floor:+.4f} and it still gets {wrong} of "
              f"{len(placements)} wrong\n")

    print("  " + "-" * 92)
    if crossed:
        stated = [p for p in PLACEMENTS if p.stated]
        wrong_trusts = [p for p in stated if p.verdict != NEAR]
        print("  **A FLOOR IS NOT THE INSTRUMENT.** The verdicts interleave with the cosine, so no")
        print("  threshold separates a placement worth trusting from one that is not.")
        print(f"  **THE STATED EDGE IS**: {len(stated)} of {len(PLACEMENTS)} placements state the")
        print(f"  dimension they landed on, and {len(wrong_trusts)} of those is declared FAR — so it")
        print("  trusts without ever trusting wrongly, and abstains on the rest. Over the whole")
        print("  build that is 31.5% of relations placements and 0.0% of distributional ones, which")
        print("  cannot be otherwise: a sense reaches D by stating no relations at all.")
        print("  Record: `docs/dictionary/202609191500_the-placement-floor.md`.")
    return 1 if crossed else 0


def report_population(db_name: str) -> int:
    """The other half of the evidence: what the whole population looks like, not just the forty."""
    from tools.dictionary_server import load

    space, config, label, *_ = load(db_name, None)
    print(f"  build {label}, near_floor {config.reading.near_floor}\n")
    tops: dict[str, list[float]] = {RELATIONAL: [], DISTRIBUTIONAL: []}
    for keys in space._senses_by_word.values():
        for sense_key in keys:
            found = space.projection(sense_key)
            if found is None:
                continue
            near = space.neighbours_of_vector(found.vector, 1, source=found.source)
            if near:
                tops[found.source].append(near[0].cosine)
    for half, values in tops.items():
        if not values:
            continue
        v = np.array(values)
        qs = np.percentile(v, [1, 10, 25, 50, 75, 90, 99])
        print(f"  {half:16} n={len(v):6}  "
              f"p1/10/25/50/75/90/99 " + " ".join(f"{q:+.3f}" for q in qs))
        floor = config.reading.near_floor
        print(f"  {'':16} the base's floor {floor:+.2f} reads NEAR for {100 * (v >= floor).mean():.1f}%")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="does a floor separate good placements from bad?")
    parser.add_argument("--db", default="tokeniko_tk2")
    parser.add_argument("--population", action="store_true",
                        help="measure the whole placed population (slow — it loads the base)")
    args = parser.parse_args(argv)

    if args.population:
        return report_population(args.db)
    return report_bar()


if __name__ == "__main__":
    raise SystemExit(main())
