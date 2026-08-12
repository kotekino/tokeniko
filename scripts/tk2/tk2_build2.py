#!/usr/bin/env python
"""tk2 stage 2b — THE TWO-MATRIX BASE.

Finding 4 of the 2026-08-12 review is the reason this file exists: `eat` and `food` have NO WordNet
relation between them, so a relations-only matrix scores them 0.000 and requirement 2 (eat stays near
food) cannot hold in the same matrix as requirement 10 (density from relations, never co-occurrence).
Blending the two into one float destroys the antonym sign AND hides the provenance — measured:
`enter~leave` reads -0.331 relations-only and +0.519 with the gloss tail switched on.

So this builder stops treating them as two settings of one thing and writes TWO collections:

    base_relational      R — named WordNet edges only. SIGNED, sparse, accountable per cell.
    base_distributional  D — gloss overlap only. Unsigned, dense, topical.

ONE key space, ONE dimension order, shared by both, recorded in `base2_manifest` — so a query can
consult either matrix, or both, and compare the answers cell for cell. The cell logic is NOT
duplicated: `tk2_matrix.cell` is called twice per pair with two different weight dicts (requirement:
two geometries built by two copies of the same code would not be comparable).

MEMBERSHIP REPAIR (requirement 15): the words the bar names but the Jurassic 2925 lacks — `want`,
`swallow`, `chew`, `runway`, `negation` — are added as dimensions here, and every one of them is
listed in the manifest under `added_words`. Declared, never smuggled.

    python scripts/tk2/tk2_build2.py                 # report only
    python scripts/tk2/tk2_build2.py --apply         # write both matrices + the manifest
"""

import argparse
import sys
import time
from collections import defaultdict

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import tk2_config as CFG
import tk2_common as C
import tk2_matrix as M


# ------------------------------------------------------------------------------------------------
# the two weight dicts — derived from the ONE weight table in tk2_config, never re-typed
# ------------------------------------------------------------------------------------------------


def weights_relational() -> dict[str, float]:
    """Every named relation EXCEPT the two the config excludes (gloss_overlap = co-occurrence,
    which is D's job; wup = a score over the taxonomy rather than an edge — see MATRIX_WUP_NOTE)."""
    return {k: v for k, v in CFG.WEIGHTS.items() if k not in CFG.MATRIX_R_EXCLUDE}


def weights_distributional() -> dict[str, float]:
    """Gloss overlap plus `identity`. Everything else is 0.0 rather than absent, because
    `tk2_matrix.cell` reads a weight of 0.0 as "this relation is switched off for this run" —
    the same mechanism `--weight gloss_overlap=0` already uses on the single-matrix CLI."""
    return {k: (v if k in CFG.MATRIX_D_INCLUDE else 0.0) for k, v in CFG.WEIGHTS.items()}


# ------------------------------------------------------------------------------------------------
# the key space — subset v1 plus the membership repair, in ONE deterministic order
# ------------------------------------------------------------------------------------------------


def build_key_space(subset_words: list[str]) -> tuple[list[str], list[str], list[dict]]:
    """(words, keys, added) — the dimension list both matrices share.

    Sorted by word, then by POS in WordNet order, so the order is a function of the word set alone:
    rebuild it tomorrow from the same subset and the indices land in the same places. The added
    words are interleaved alphabetically rather than appended, precisely so nothing about a
    dimension's position encodes whether it came from the Jurassic base or from the repair.
    """
    have = set(subset_words)
    added = []
    for word, why in CFG.BASE2_ADDED_WORDS:
        if word in have:
            continue                      # already a dimension — nothing to repair, say nothing
        keys = C.keys_for_word(word)
        if not keys:
            added.append({"word": word, "keys": [], "why": why,
                          "status": "NOT IN WORDNET — no axis could be created"})
            continue
        have.add(word)
        added.append({"word": word, "keys": keys, "why": why,
                      "status": "added as a dimension (not a Jurassic base word)"})

    words = sorted(have)
    keys = [k for w in words for k in C.keys_for_word(w)]
    return words, keys, added


# ------------------------------------------------------------------------------------------------
# the fill — one pass over the pairs, two cells per pair
# ------------------------------------------------------------------------------------------------


def build(keys, senses_mode):
    """Returns (rows_R, rows_D, stats). One walk over n^2 pairs producing both geometries, because
    the expensive part is the precompute and the pair loop, not the cell decision."""
    print(f"precomputing relations for {len(keys)} dimensions ...", flush=True)
    t0 = time.time()
    syn_names, rels, glosses, depths = M.precompute(keys, senses_mode)
    print(f"  ... {time.time()-t0:.1f}s", flush=True)

    wR, wD = weights_relational(), weights_distributional()

    rows_R, rows_D = [], []
    by_rel = {"relational": defaultdict(int), "distributional": defaultdict(int)}
    nonzero = {"relational": 0, "distributional": 0}
    n = len(keys)

    print(f"filling 2 x {n}x{n} = {2*n*n} cells ...", flush=True)
    for i, kx in enumerate(keys):
        vecR, vecD = [0.0] * n, [0.0] * n
        edgesR, edgesD = {}, {}
        for j, ky in enumerate(keys):
            vr, rr = M.cell(kx, ky, syn_names, rels, glosses, depths, weights=wR)
            if vr:
                vecR[j] = float(vr)
                if i != j:
                    edgesR[ky] = {"w": float(vr), "rel": rr}
                    by_rel["relational"][rr] += 1
                    nonzero["relational"] += 1
            vd, rd = M.cell(kx, ky, syn_names, rels, glosses, depths, weights=wD)
            if vd:
                vecD[j] = float(vd)
                if i != j:
                    edgesD[ky] = {"w": float(vd), "rel": rd}
                    by_rel["distributional"][rd] += 1
                    nonzero["distributional"] += 1
        word, pos = C.split_key(kx)
        common = {"key": kx, "word": word, "pos": pos, "index": i}
        rows_R.append({**common, "vector": vecR, "edges": edgesR})
        rows_D.append({**common, "vector": vecD, "edges": edgesD})
        if (i + 1) % 100 == 0:
            print(f"  ... {i+1}/{n} rows  ({time.time()-t0:.0f}s)", flush=True)

    total = n * (n - 1)
    stats = {}
    for name in ("relational", "distributional"):
        stats[name] = {
            "off_diagonal": total,
            "nonzero": nonzero[name],
            "density_pct": round(100 * nonzero[name] / max(1, total), 3),
            "by_relation": dict(by_rel[name]),
        }
    return rows_R, rows_D, stats


def report_density(stats):
    print()
    print("=== density ===")
    for name, s in stats.items():
        tag = "R" if name == "relational" else "D"
        print(f"  {tag} {name:15s} {s['nonzero']:8d} / {s['off_diagonal']} non-zero  ({s['density_pct']:.2f}%)")
        for rel, k in sorted(s["by_relation"].items(), key=lambda t: -t[1]):
            print(f"      {rel:16s} {k:8d}  ({100*k/max(1, s['nonzero']):.1f}% of non-zero)")


# ------------------------------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subset", default="v1")
    ap.add_argument("--base", default=CFG.BASE2_NAME, help="name of the two-matrix base")
    ap.add_argument("--senses", choices=["primary", "all"], default=CFG.DEFINITION_SENSES)
    ap.add_argument("--note", default="", help="what you changed for this build")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    db = C.tk2_db()
    doc = db.subsets.find_one({"name": args.subset})
    if not doc:
        raise SystemExit(f"no subset '{args.subset}' in {CFG.TK2_DB}.subsets — run tk2_subset.py --apply first")

    words, keys, added = build_key_space(doc["words"])
    print(f"subset '{args.subset}': {len(doc['words'])} words -> {len(doc['keys'])} dimensions")
    print(f"membership repair (requirement 15): +{len(words)-len(doc['words'])} words")
    for a in added:
        print(f"    {a['word']:10s} -> {', '.join(a['keys']) or '(none)':20s} {a['status']}")
    print(f"two-matrix key space: {len(words)} words -> {len(keys)} dimensions")
    print(f"wup decision: {CFG.MATRIX_WUP_NOTE}")

    rows_R, rows_D, stats = build(keys, args.senses)
    report_density(stats)

    jurassic_only = {"synonym", "antonym", "derivational", "wup", "gloss_overlap"}
    r = stats["relational"]
    new = sum(k for rel, k in r["by_relation"].items() if rel not in jurassic_only)
    print(f"\n  R cells the Jurassic build could NOT produce: {new}  ({100*new/max(1,r['nonzero']):.1f}% of R)")
    neg = sum(1 for row in rows_R for e in row["edges"].values() if e["w"] < 0)
    print(f"  R cells with a NEGATIVE value (the antonym sign, which only R carries): {neg}")

    if not args.apply:
        print("\n(dry run — pass --apply to store the two matrices and the manifest)")
        return

    for coll, rows in (("base_relational", rows_R), ("base_distributional", rows_D)):
        db[coll].delete_many({"base": args.base})
        db[coll].insert_many([{"base": args.base, **row} for row in rows])
        db[coll].create_index([("base", 1), ("key", 1)])
        db[coll].create_index([("base", 1), ("index", 1)])
        print(f"written: {CFG.TK2_DB}.{coll} base='{args.base}' — {len(rows)} rows")

    db.base2_manifest.replace_one(
        {"base": args.base},
        {
            "base": args.base,
            "subset": args.subset,
            "senses": args.senses,
            "built_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "note": args.note,
            "split_by_pos": CFG.SPLIT_BY_POS,
            "allow_cross_pos": CFG.ALLOW_CROSS_POS,
            "dims": len(keys),
            "words": words,
            "keys": keys,                       # THE dimension order, shared by both matrices
            "added_words": added,               # requirement 15, declared out loud
            "collections": {"relational": "base_relational", "distributional": "base_distributional"},
            "weights": {"relational": weights_relational(), "distributional": weights_distributional()},
            "wup_decision": CFG.MATRIX_WUP_NOTE,
            "density": stats,
        },
        upsert=True,
    )
    print(f"written: {CFG.TK2_DB}.base2_manifest base='{args.base}' — {len(keys)} dimensions")


if __name__ == "__main__":
    main()
