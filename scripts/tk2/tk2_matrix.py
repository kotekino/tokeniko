#!/usr/bin/env python
"""tk2 stage 2 — THE CANDIDATE MATRIX.

Rows = dimensions, POS-split, over the cherry-picked subset. Every non-zero cell is produced by a
NAMED WordNet relation and stores WHICH one — so the matrix is not merely editable in principle (the
Jurassic one already was, being a full explicit 2925x2925), it is *accountable*: you can ask of any
value which relation put it there.

The cells the Jurassic build could never produce: entails, causes, troponymy, verb_group, similar_to,
attribute, meronymy. Weights and on/off switches live in tk2_config.WEIGHTS.

    python scripts/tk2/tk2_matrix.py --subset v1 --run r1 --apply
    python scripts/tk2/tk2_matrix.py --subset v1 --run r2-no-gloss --apply     # after editing WEIGHTS
"""

import argparse
import sys
from collections import defaultdict

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import tk2_config as CFG
import tk2_common as C

from nltk.corpus import wordnet as wn


# ------------------------------------------------------------------------------------------------
# per-key precomputation — every relation is walked ONCE per key, never per pair
# ------------------------------------------------------------------------------------------------

FORWARD = (
    "synonym", "antonym", "derivational", "entails", "causes", "troponym",
    "hypernym_1", "hypernym_2", "verb_group", "similar_to", "attribute", "also_see",
    "meronym", "holonym",
)


def precompute(keys, senses_mode):
    syn_names, rels, glosses, depths = {}, {}, {}, {}

    for k in keys:
        word, pos = C.split_key(k)
        syns = [s for s in wn.synsets(word) if pos is None or C.normalize_pos(s.pos()) == pos]
        syn_names[k] = {s.name() for s in syns}

        r = defaultdict(set)
        for s in syns:
            r["synonym"].add(s.name())
            for lem in s.lemmas():
                for ant in lem.antonyms():
                    r["antonym"].add(ant.synset().name())
                for drf in lem.derivationally_related_forms():
                    r["derivational"].add(drf.synset().name())
            for t in s.entailments():
                r["entails"].add(t.name())
            for t in s.causes():
                r["causes"].add(t.name())
            for t in s.verb_groups():
                r["verb_group"].add(t.name())
            for t in s.similar_tos():
                r["similar_to"].add(t.name())
            for t in s.attributes():
                r["attribute"].add(t.name())
            for t in s.also_sees():
                r["also_see"].add(t.name())
            for t in s.part_meronyms() + s.member_meronyms() + s.substance_meronyms():
                r["meronym"].add(t.name())
            for t in s.part_holonyms() + s.member_holonyms() + s.substance_holonyms():
                r["holonym"].add(t.name())
            # taxonomy: for a verb, a hyponym IS a troponym (a manner-of) — a different relation
            # with a different meaning, so it gets its own name and its own weight.
            for t in s.hyponyms():
                r["troponym" if s.pos() == "v" else "hyponym_1"].add(t.name())
            for t in s.hypernyms() + s.instance_hypernyms():
                r["hypernym_1"].add(t.name())
                for t2 in t.hypernyms():
                    r["hypernym_2"].add(t2.name())
        rels[k] = {kk: vv for kk, vv in r.items()}

        glosses[k] = C._lemmas_in_base(" ".join(s.definition() + " " + " ".join(s.examples()) for s in syns))

        # hypernym ancestors with depth — the Wu-Palmer substitute (see _wup below)
        d = {}
        for s in (syns[:1] if senses_mode == "primary" else syns):
            for path in s.hypernym_paths():
                for depth, anc in enumerate(path):
                    name = anc.name()
                    d[name] = max(d.get(name, 0), depth)
            d[s.name()] = max(d.get(s.name(), 0), max((len(p) - 1 for p in s.hypernym_paths()), default=0))
        depths[k] = d

    return syn_names, rels, glosses, depths


def _wup(depths_x, depths_y, syn_x, syn_y) -> float:
    """Wu-Palmer over the precomputed hypernym-path depths: 2*d(LCS) / (d(x)+d(y)).

    An approximation of nltk's `wup_similarity` (which additionally walks the shortest path); it is
    used here for the same purpose the Jurassic build used the real one — a gated fallback when no
    explicit relation exists — and it is 3 orders of magnitude cheaper over n^2 pairs.
    """
    common = set(depths_x) & set(depths_y)
    if not common:
        return 0.0
    lcs = max(depths_x[c] for c in common)
    dx = max((depths_x[s] for s in syn_x if s in depths_x), default=0)
    dy = max((depths_y[s] for s in syn_y if s in depths_y), default=0)
    if dx + dy == 0:
        return 0.0
    return (2.0 * lcs) / (dx + dy)


# ------------------------------------------------------------------------------------------------
# one cell
# ------------------------------------------------------------------------------------------------


def cell(kx, ky, syn_names, rels, glosses, depths, weights=None):
    """(value, relation-that-produced-it). Row X, column Y = X's relation TO Y — asymmetric on
    purpose, so the antonym column-read (`base[X][idx(W)] < 0`) keeps working.

    `weights` defaults to CFG.WEIGHTS (the single-matrix CLI below). The two-matrix builder
    (tk2_build2.py) passes a restricted dict instead and calls this SAME function twice per pair —
    the cell logic is the instrument, and two geometries built by two copies of it would not be
    comparable. A relation switched off (weight 0.0) is simply skipped, so a dict holding only
    {identity, gloss_overlap} yields the distributional cell and nothing else.
    """
    W = CFG.WEIGHTS if weights is None else weights
    if kx == ky:
        return W["identity"], "identity"

    px, py = C.split_key(kx)[1], C.split_key(ky)[1]
    if not CFG.ALLOW_CROSS_POS and px != py:
        return 0.0, None

    sx, sy = syn_names[kx], syn_names[ky]
    rx, ry = rels[kx], rels[ky]

    def hits(owner, rel, target):
        return bool(owner.get(rel) and (owner[rel] & target))

    # synonymy first, then antonymy — antonymy RETURNS, because the sign is load-bearing.
    if W.get("synonym") and (sx & sy):
        return W["synonym"], "synonym"
    if W.get("antonym") and hits(rx, "antonym", sy):
        return W["antonym"], "antonym"

    scored: list[tuple[float, str]] = []

    for rel in ("derivational", "entails", "causes", "troponym", "hyponym_1",
                "hypernym_1", "hypernym_2", "verb_group", "similar_to", "attribute",
                "also_see", "meronym", "holonym"):
        if W.get(rel) and hits(rx, rel, sy):
            scored.append((W[rel], rel))

    # the reverse reads — the relation is directional, so «Y entails X» is its own, weaker cell
    for fwd, rev in (("entails", "entailed_by"), ("causes", "caused_by"), ("troponym", "troponym_of")):
        if W.get(rev) and hits(ry, fwd, sx):
            scored.append((W[rev], rev))

    if not scored and W.get("wup") and (CFG.ALLOW_CROSS_POS or px == py) and px == py:
        raw = _wup(depths[kx], depths[ky], sx, sy)
        if raw > CFG.WUP_FLOOR:
            scored.append((round(raw * W["wup"], 3), "wup"))

    if not scored and W.get("gloss_overlap"):
        gx, gy = glosses[kx], glosses[ky]
        if gx and gy:
            inter = gx & gy
            if len(inter) >= 2:
                jac = len(inter) / len(gx | gy)
                val = min(round(jac * 5, 3), CFG.GLOSS_JACCARD_CAP)
                if val > CFG.GLOSS_JACCARD_FLOOR:
                    scored.append((round(val * W["gloss_overlap"], 3), "gloss_overlap"))

    if not scored:
        return 0.0, None
    return max(scored, key=lambda t: abs(t[0]))


# ------------------------------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subset", default="v1")
    ap.add_argument("--run", required=True, help="name this iteration, e.g. r1 / r2-no-gloss")
    ap.add_argument("--senses", choices=["primary", "all"], default=CFG.DEFINITION_SENSES)
    ap.add_argument("--note", default="", help="what you changed for this run")
    ap.add_argument("--weight", action="append", default=[], metavar="REL=VALUE",
                    help="override a weight for this run only, e.g. --weight gloss_overlap=0")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    for spec in args.weight:
        rel, _, val = spec.partition("=")
        if rel not in CFG.WEIGHTS:
            raise SystemExit(f"unknown relation '{rel}' — known: {', '.join(sorted(CFG.WEIGHTS))}")
        CFG.WEIGHTS[rel] = float(val)
        print(f"weight override: {rel} = {val}")

    db = C.tk2_db()
    doc = db.subsets.find_one({"name": args.subset})
    if not doc:
        raise SystemExit(f"no subset '{args.subset}' in {CFG.TK2_DB}.subsets — run tk2_subset.py --apply first")
    keys = doc["keys"]
    print(f"subset '{args.subset}': {len(doc['words'])} words -> {len(keys)} dimensions", flush=True)

    print("precomputing relations per dimension ...", flush=True)
    syn_names, rels, glosses, depths = precompute(keys, args.senses)

    print(f"filling {len(keys)}x{len(keys)} = {len(keys)**2} cells ...", flush=True)
    rows = []
    by_rel = defaultdict(int)
    nonzero = 0
    for i, kx in enumerate(keys):
        vec = [0.0] * len(keys)
        edges = {}
        for j, ky in enumerate(keys):
            val, rel = cell(kx, ky, syn_names, rels, glosses, depths)
            if val:
                vec[j] = float(val)
                if kx != ky:
                    edges[ky] = {"w": float(val), "rel": rel}
                    by_rel[rel] += 1
                    nonzero += 1
        word, pos = C.split_key(kx)
        rows.append({"run": args.run, "key": kx, "word": word, "pos": pos,
                     "index": i, "vector": vec, "edges": edges})
        if (i + 1) % 50 == 0:
            print(f"  ... {i+1}/{len(keys)} rows", flush=True)

    total = len(keys) * (len(keys) - 1)
    print()
    print("=== density ===")
    print(f"  off-diagonal cells      {total}")
    print(f"  non-zero                {nonzero}  ({100*nonzero/max(1,total):.2f}%)")
    print("  by relation:")
    for rel, n in sorted(by_rel.items(), key=lambda t: -t[1]):
        print(f"    {rel:16s} {n:7d}  ({100*n/max(1,nonzero):.1f}% of non-zero)")

    jurassic_only = {"synonym", "antonym", "derivational", "wup", "gloss_overlap"}
    new = sum(n for r, n in by_rel.items() if r not in jurassic_only)
    print(f"  cells the Jurassic build could NOT produce: {new}  ({100*new/max(1,nonzero):.1f}% of non-zero)")

    if args.apply:
        db.base_candidate.delete_many({"run": args.run})
        db.base_candidate.insert_many(rows)
        db.base_candidate.create_index([("run", 1), ("key", 1)])
        db.runs.replace_one(
            {"run": args.run},
            {"run": args.run, "subset": args.subset, "senses": args.senses, "note": args.note,
             "weights": CFG.WEIGHTS, "split_by_pos": CFG.SPLIT_BY_POS,
             "allow_cross_pos": CFG.ALLOW_CROSS_POS, "dims": len(keys),
             "nonzero": nonzero, "by_relation": dict(by_rel)},
            upsert=True,
        )
        print(f"\nwritten: {CFG.TK2_DB}.base_candidate run='{args.run}' — {len(rows)} rows")
    else:
        print("\n(dry run — pass --apply to store the run)")


if __name__ == "__main__":
    main()
