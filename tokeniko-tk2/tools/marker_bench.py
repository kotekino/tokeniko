"""THE AMBIGUOUS MARKERS' BENCH — the selector against 52 cases with their gold.

    PYTHONPATH=. ../.venv/bin/python tools/marker_bench.py [--db tokeniko_tk2] [--geometry]

**WHY THIS IS NOT THE UD GATE.** The gate measures the PARSE — a skeleton in, and did the station
read the relation UD says is there. This measures the SELECTOR, whose input is not a sentence but a
tuple: which marker, on which nominal, under which verb. Putting a parser in front of it would make
a wrong number unattributable between the two.

**THE THREE BUCKETS ARE NOT WORTH THE SAME AND ARE NEVER AVERAGED.**

- **independent** — E2's hand-compiled drill and the UD gate's own examples. Nobody who wrote them
  was thinking about a selector. This is the number a claim may rest on.
- **the curation's own** — `db/0008`'s worked examples («at the door / at noon / at speed»). A
  selector that reproduces them has agreed with the curation and discovered nothing; they are here
  because a selector that could not hold the curation's own examples would be refuted.
- **named individuals** — «Anna», «Genoa». The base refuses them by name and the identity layer that
  replaces them is not built. WordNet reads `anna` as an Indian coin. Averaging that into a score
  would hide a known, parked hole.

`--geometry` re-runs the rejected candidate — nearest-anchor over role anchors, the instrument
`db/0008` predicted — so the ruling stays checkable rather than remembered. It needs a body with a
base applied; everything else here is offline.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tests.fixtures.markers import CASES, CURATION, DRILL, UD  # noqa: E402
from tk2.language import standing_closed_classes  # noqa: E402
from tk2.language.markers import MarkerSelector  # noqa: E402

#: The anchor sets the REJECTED geometry candidate ranked against — kept with the bench that
#: refuted it, because a rejection nobody can re-run is a memory rather than a measurement.
GEOMETRY_ANCHORS = {
    "location": ("place.n", "building.n", "city.n", "room.n", "area.n", "house.n", "region.n",
                 "land.n"),
    "time": ("time.n", "day.n", "month.n", "year.n", "period.n", "season.n", "date.n"),
    "instrument": ("instrument.n", "device.n", "equipment.n", "weapon.n", "tool.n"),
    "recipient": ("person.n", "people.n", "man.n", "woman.n", "child.n"),
    "comitative": ("person.n", "people.n", "man.n", "woman.n", "child.n"),
    "beneficiary": ("person.n", "people.n", "man.n", "woman.n", "child.n"),
    "agent": ("person.n", "people.n", "man.n", "woman.n", "child.n"),
    "destination": ("place.n", "city.n", "building.n", "region.n"),
    "duration": ("time.n", "period.n", "year.n", "month.n"),
    "path": ("road.n", "route.n", "way.n", "line.n"),
    "topic": ("subject.n", "idea.n", "knowledge.n", "science.n"),
    "manner": ("way.n", "style.n", "method.n"),
    "measure": ("measure.n", "amount.n", "degree.n"),
    "source": ("material.n", "substance.n", "origin.n"),
    "complement": ("relation.n", "part.n", "property.n"),
}

BUCKETS = (
    ("independent", lambda c: c.source in (DRILL, UD) and not c.name),
    ("the curation's own", lambda c: c.source == CURATION and not c.name),
    ("named individuals", lambda c: c.name),
)


def compiled_for(table, marker: str) -> dict:
    for row in table.jobs(marker):
        found = row.get("compiled") or {}
        if found.get("kind") == "box" and found.get("roles"):
            return found
    return {}


def by_selector(selector, table, case):
    compiled = compiled_for(table, case.marker)
    settled = selector.settle(compiled, case.nominal, case.nominal_upos, case.head, case.head_upos)
    if settled is None:
        return None, "no selector on the row"
    return settled.role, settled.why


def by_first(table, case):
    roles = compiled_for(table, case.marker).get("roles") or ()
    return (roles[0] if roles else None), "first candidate"


def by_geometry(space, table, case):
    """The rejected candidate: place the nominal's primary sense and take the nearest role anchor."""
    roles = compiled_for(table, case.marker).get("roles") or ()
    owner, anchors = {}, []
    for role in roles:
        for anchor in GEOMETRY_ANCHORS.get(role, ()):
            if space.holds(anchor) and anchor not in owner:
                owner[anchor] = role
                anchors.append(anchor)
    if not anchors:
        return None, "no anchors for these candidates"
    found = space.projection(f"{case.nominal}.n.01")
    if found is None:
        return None, "the sense is not placeable"
    near = space.nearest_anchor_of_vector(found.vector, tuple(anchors), source=found.source)
    if near is None:
        return None, "no column in common with any anchor"
    return owner[near.key], f"{found.source[0]}:{near.key} {near.cosine:+.2f} {near.verdict}"


def score(name, read, show_errors=True):
    print(f"\n  {name}")
    for bucket, keep in BUCKETS:
        ok = wrong = mute = defaulted = 0
        errors = []
        for case in CASES:
            if not keep(case):
                continue
            got, why = read(case)
            defaulted += why == "default"
            if got is None:
                mute += 1
            elif got == case.expect:
                ok += 1
            else:
                wrong += 1
                errors.append(f"        {case.marker:6s} « {case.phrase:30s} »  want {case.expect:12s}"
                              f" got {got:12s} ({why})")
        total = ok + wrong + mute
        print(f"    {bucket:20s} {ok:3d}/{total} ok · {wrong} WRONG · {mute} mute"
              + (f" · {defaulted} by default" if defaulted else ""))
        if show_errors and errors:
            print("\n".join(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default=None, help="read the live rows from this database")
    parser.add_argument("--geometry", action="store_true",
                        help="also re-run the rejected nearest-anchor candidate (needs a base)")
    args = parser.parse_args()

    table = standing_closed_classes(args.db)
    selector = MarkerSelector()
    print("=" * 96)
    print("THE AMBIGUOUS MARKERS' BENCH — the selector against 52 cases with their gold")
    print("=" * 96)
    print(f"  closed classes    {len(table)} rows, v{table.version} — {table.source}")
    print(f"  cases             {len(CASES)} over {len({c.marker for c in CASES})} of the "
          f"seventeen ambiguous forms")

    score("THE SUPERSENSE SELECTOR — what db/0012 rules", lambda c: by_selector(selector, table, c))
    score("the baseline: take the first candidate", lambda c: by_first(table, c), show_errors=False)

    if args.geometry:
        from tools.dictionary_server import load
        space = load(args.db or "tokeniko_tk2", None)[0]
        score("REJECTED — nearest-anchor geometry (db/0008's prediction)",
              lambda c: by_geometry(space, table, c), show_errors=False)

    print("\n  a `default` is the curation's best-first answer with nothing in the sentence to")
    print("  choose otherwise. It is COUNTED, never silent — req 8's distinction, and req 4's input.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
