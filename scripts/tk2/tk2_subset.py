#!/usr/bin/env python
"""tk2 stage 1 — THE CHERRY-PICKED SUBSET.

The Captain's method, 2026-08-12: take the DEFINITIONS of base words, shorten each to use only base
words, and the subset is where the intersections are smallest. His trivial example —

    me -> not you | you -> not me | not -> negation | negation -> not
    => {me, not, you, negation} defines itself and never leaves

Formally: a set S is CLOSED when defs(S) is a subset of S. The minimal closed sets are the SINK
components of the definition digraph. This script finds them, and separately runs the closure from
the sensitive seeds (requirement 8), so the fight between «closed» and «sensitive» is MEASURED
rather than assumed.

    python scripts/tk2/tk2_subset.py                 # report only
    python scripts/tk2/tk2_subset.py --apply         # also write the chosen subset to the sandbox
    python scripts/tk2/tk2_subset.py --senses all    # denser definitions
"""

import argparse
import sys
from collections import defaultdict

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import tk2_config as CFG
import tk2_common as C


# ------------------------------------------------------------------------------------------------
# the definition digraph:  word --> the base words its definition is written with
# ------------------------------------------------------------------------------------------------


def build_graph(mode: str) -> dict[str, set[str]]:
    words = C.base_words()
    graph: dict[str, set[str]] = {}
    for i, w in enumerate(words, 1):
        graph[w] = C.definition_in_base(w, mode)
        if i % 500 == 0:
            print(f"  ... {i}/{len(words)} definitions reduced", flush=True)
    return graph


# ------------------------------------------------------------------------------------------------
# sink SCCs = the minimal closed sets. Tarjan, iterative (2925 nodes, but no recursion limit games)
# ------------------------------------------------------------------------------------------------


def sccs(graph: dict[str, set[str]]) -> list[list[str]]:
    index_of: dict[str, int] = {}
    low: dict[str, int] = {}
    on_stack: dict[str, bool] = {}
    stack: list[str] = []
    result: list[list[str]] = []
    counter = 0

    for root in graph:
        if root in index_of:
            continue
        work = [(root, iter(sorted(graph.get(root, ()))))]
        index_of[root] = low[root] = counter
        counter += 1
        stack.append(root)
        on_stack[root] = True

        while work:
            node, it = work[-1]
            advanced = False
            for nxt in it:
                if nxt not in graph:
                    continue
                if nxt not in index_of:
                    index_of[nxt] = low[nxt] = counter
                    counter += 1
                    stack.append(nxt)
                    on_stack[nxt] = True
                    work.append((nxt, iter(sorted(graph.get(nxt, ())))))
                    advanced = True
                    break
                if on_stack.get(nxt):
                    low[node] = min(low[node], index_of[nxt])
            if advanced:
                continue

            work.pop()
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[node])
            if low[node] == index_of[node]:
                comp = []
                while True:
                    m = stack.pop()
                    on_stack[m] = False
                    comp.append(m)
                    if m == node:
                        break
                result.append(sorted(comp))
    return result


def closed_sets(graph: dict[str, set[str]]) -> list[list[str]]:
    """A component is closed iff no edge leaves it (a sink in the condensation)."""
    comps = sccs(graph)
    member = {w: i for i, comp in enumerate(comps) for w in comp}
    out = []
    for i, comp in enumerate(comps):
        cs = set(comp)
        if all(t in cs for w in comp for t in graph.get(w, ()) if t in member):
            out.append(comp)
    return sorted(out, key=len)


# ------------------------------------------------------------------------------------------------
# seed closure — how far does «eat» actually reach before it swallows the dictionary?
# ------------------------------------------------------------------------------------------------


def seed_closure(graph, seeds, max_depth, max_size):
    frontier = {s for s in seeds if s in graph}
    missing = [s for s in seeds if s not in graph]
    seen = set(frontier)
    per_depth = [sorted(frontier)]
    for _ in range(max_depth):
        nxt = set()
        for w in frontier:
            nxt |= graph.get(w, set())
        nxt -= seen
        if not nxt:
            break
        if len(seen) + len(nxt) > max_size:
            per_depth.append(sorted(nxt))
            seen |= nxt
            break
        seen |= nxt
        per_depth.append(sorted(nxt))
        frontier = nxt
    return seen, per_depth, missing


def per_seed_cost(graph, seeds, depth):
    """The QM's stated counter, quantified per seed: function words close cheaply, `eat` explodes."""
    rows = []
    for s in seeds:
        if s not in graph:
            rows.append((s, None))
            continue
        seen, _, _ = seed_closure(graph, [s], depth, 10_000)
        rows.append((s, len(seen)))
    return rows


# ------------------------------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--senses", choices=["primary", "all"], default=CFG.DEFINITION_SENSES)
    ap.add_argument("--depth", type=int, default=CFG.SEED_CLOSURE_MAX_DEPTH)
    ap.add_argument("--max-size", type=int, default=CFG.SEED_CLOSURE_MAX_SIZE)
    ap.add_argument("--top", type=int, default=15, help="how many minimal closed sets to print")
    ap.add_argument("--apply", action="store_true", help="write the chosen subset to the tk2 sandbox")
    ap.add_argument("--name", default="v1", help="subset name in the sandbox")
    args = ap.parse_args()

    print(f"reading the base from '{CFG.SRC_DB}' (read-only) ...", flush=True)
    print(f"reducing {len(C.base_words())} definitions to base words [senses={args.senses}] ...", flush=True)
    graph = build_graph(args.senses)

    sizes = [len(v) for v in graph.values()]
    empty = sum(1 for v in graph.values() if not v)
    print()
    print("=== the definition graph ===")
    print(f"  nodes                    {len(graph)}")
    print(f"  mean base words per def  {sum(sizes)/max(1,len(sizes)):.2f}")
    print(f"  defs that name NO base   {empty}   <- these can never be in a closed set")

    print()
    print("=== minimal closed sets (defs(S) subset-of S) ===")
    cs = closed_sets(graph)
    interesting = [c for c in cs if len(c) > 1]
    print(f"  {len(cs)} closed components, {len(interesting)} with more than one word")
    for comp in interesting[: args.top]:
        print(f"  [{len(comp):3d}] {', '.join(comp[:24])}{' ...' if len(comp) > 24 else ''}")

    print()
    print("=== per-seed closure cost (the closed-vs-sensitive fight, measured) ===")
    for name, seeds in (
        ("volitional", CFG.SEEDS_VOLITIONAL),
        ("motion", CFG.SEEDS_MOTION),
        ("effect", CFG.SEEDS_EFFECT),
        ("identity", CFG.SEEDS_IDENTITY),
    ):
        rows = per_seed_cost(graph, seeds, args.depth)
        shown = ", ".join(f"{w}:{n if n is not None else 'NOT-BASE'}" for w, n in rows)
        print(f"  {name:11s} {shown}")

    seen, per_depth, missing = seed_closure(graph, CFG.SEEDS, args.depth, args.max_size)
    print()
    print(f"=== seed closure (depth<={args.depth}, cap={args.max_size}) ===")
    if missing:
        print(f"  NOT base words, dropped: {', '.join(missing)}")
    for d, layer in enumerate(per_depth):
        print(f"  depth {d}: +{len(layer):4d}   {', '.join(layer[:18])}{' ...' if len(layer) > 18 else ''}")
    print(f"  TOTAL {len(seen)} words")

    subset = sorted(seen)
    keys = [k for w in subset for k in C.keys_for_word(w)]
    multi = [w for w in subset if len(C.keys_for_word(w)) > 1]
    print()
    print("=== what the POS split costs on this subset ===")
    print(f"  words {len(subset)} -> dimensions {len(keys)}  (x{len(keys)/max(1,len(subset)):.2f})")
    print(f"  multi-POS words: {len(multi)}  e.g. {', '.join(multi[:20])}")

    if args.apply:
        db = C.tk2_db()
        db.subsets.replace_one(
            {"name": args.name},
            {
                "name": args.name,
                "senses": args.senses,
                "depth": args.depth,
                "words": subset,
                "keys": keys,
                "seeds": CFG.SEEDS,
            },
            upsert=True,
        )
        print(f"\nwritten: {CFG.TK2_DB}.subsets['{args.name}'] — {len(subset)} words / {len(keys)} dimensions")
    else:
        print("\n(dry run — pass --apply to store the subset in the sandbox)")


if __name__ == "__main__":
    main()
