#!/usr/bin/env python
"""tk2 — THE CLI OVER THE TWO-MATRIX BASE. This is the draft of the tk2 API surface.

Each subcommand is written as if it were an endpoint, because it is meant to become one. The rule
that shapes all of them: **every answer names the matrix that gave it**, and an honest abstention
beats a plausible number. When R has nothing to say about a pair, it says "no stated relation"; it
never quietly falls back to D and hands the caller a topicality score dressed as a relation.

    R  base_relational      named WordNet edges. SIGNED. Opposition, entailment, causation, is-a.
    D  base_distributional  gloss overlap. Unsigned, topical. Aboutness, relatedness.
    J  the Jurassic 2925    the body's live base, POS-collapsed — shown for comparison only.

    python scripts/tk2/tk2.py near sleep.v --k 10
    python scripts/tk2/tk2.py rel eat.v food.n
    python scripts/tk2/tk2.py opposite leave
    python scripts/tk2/tk2.py effect eat
    python scripts/tk2/tk2.py bar
"""

import argparse
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import tk2_config as CFG
import tk2_common as C
import tk2_probe as P                      # the bar's verdict/local-order logic, not re-typed

GREEN, RED, DIM, BOLD, OFF = "\033[32m", "\033[31m", "\033[2m", "\033[1m", "\033[0m"

MATRICES = {"R": "base_relational", "D": "base_distributional"}
LABEL = {"R": "R (relational — named WordNet edges, signed)",
         "D": "D (distributional — gloss overlap, unsigned)"}


# ------------------------------------------------------------------------------------------------
# the base, loaded lazily — a subcommand pays only for the matrix it actually consults
# ------------------------------------------------------------------------------------------------


class Base2:
    def __init__(self, base: str):
        self.db = C.tk2_db()
        self.manifest = self.db.base2_manifest.find_one({"base": base})
        if not self.manifest:
            raise SystemExit(
                f"no two-matrix base '{base}' in {CFG.TK2_DB}.base2_manifest — "
                f"run: python scripts/tk2/tk2_build2.py --apply"
            )
        self.base = base
        self.keys: list[str] = self.manifest["keys"]
        self.idx = {k: i for i, k in enumerate(self.keys)}
        self._rows: dict[str, dict] = {}     # matrix letter -> {key: row}, cached per process

    # -- rows ------------------------------------------------------------------------------------

    def rows(self, which: str) -> dict[str, dict]:
        """The whole matrix. Loaded whole because the column read and the neighbour ranking both
        need every row; 983 rows is a prototype's worth of memory, not a design commitment."""
        if which not in self._rows:
            coll = self.db[MATRICES[which]]
            self._rows[which] = {
                r["key"]: r for r in coll.find({"base": self.base},
                                               {"key": 1, "index": 1, "vector": 1, "edges": 1})
            }
        return self._rows[which]

    def row(self, which: str, key: str) -> dict | None:
        if which in self._rows:
            return self._rows[which].get(key)
        return self.db[MATRICES[which]].find_one(
            {"base": self.base, "key": key}, {"key": 1, "index": 1, "vector": 1, "edges": 1})

    # -- key resolution --------------------------------------------------------------------------

    def resolve(self, token: str) -> list[str]:
        """`eat.v` -> [eat.v]; a bare `leave` -> every POS of it that IS a dimension. Ambiguity is
        surfaced to the caller, never silently collapsed onto the first sense."""
        token = token.strip().lower()
        if token in self.idx:
            return [token]
        word, pos = C.split_key(token)
        if pos is not None:
            return []                        # explicitly POS-qualified and absent — say so
        return [k for k in self.keys if C.split_key(k)[0] == word]

    def require(self, token: str) -> list[str]:
        keys = self.resolve(token)
        if not keys:
            print(f"{RED}'{token}' is not a dimension of base '{self.base}' "
                  f"({len(self.keys)} dims). No answer — abstaining rather than guessing.{OFF}")
        elif len(keys) > 1:
            print(f"{DIM}'{token}' is ambiguous across POS: {', '.join(keys)} — answering for each.{OFF}")
        return keys


def cos(base: Base2, which: str, ka: str, kb: str) -> float | None:
    ra, rb = base.row(which, ka), base.row(which, kb)
    if ra is None or rb is None:
        return None
    return C.cosine(ra["vector"], rb["vector"])


def edge_of(base: Base2, which: str, ka: str, kb: str) -> dict | None:
    r = base.row(which, ka)
    return (r or {}).get("edges", {}).get(kb)


# ------------------------------------------------------------------------------------------------
# 1. near — the nearest neighbours, and WHERE THE TWO MATRICES DISAGREE
# ------------------------------------------------------------------------------------------------


def cmd_near(base: Base2, args):
    import numpy as np

    for key in base.require(args.word):
        ranked = {}
        for which in ("R", "D"):
            rows = base.rows(which)
            keys = [k for k in base.keys if k in rows]
            mat = np.asarray([rows[k]["vector"] for k in keys], dtype=float)
            v = np.asarray(rows[key]["vector"], dtype=float)
            norms = np.linalg.norm(mat, axis=1)
            nv = np.linalg.norm(v)
            with np.errstate(invalid="ignore", divide="ignore"):
                sims = np.where((norms > 0) & (nv > 0), mat.dot(v) / (norms * nv), 0.0)
            order = np.argsort(-sims)
            ranked[which] = [(keys[i], float(sims[i])) for i in order if keys[i] != key][: args.k]

        print(f"\n{BOLD}near {key}{OFF}   top {args.k}, two matrices, side by side")
        print(f"  {'R — relational (signed edges)':38s}   D — distributional (gloss overlap)")
        print(f"  {'-'*38}   {'-'*38}")
        for i in range(args.k):
            lk, lv = ranked["R"][i] if i < len(ranked["R"]) else ("", None)
            rk, rv = ranked["D"][i] if i < len(ranked["D"]) else ("", None)
            left = f"{lv:7.3f}  {lk:<28}" if lv is not None else " " * 37
            right = f"{rv:7.3f}  {rk}" if rv is not None else ""
            print(f"  {left}   {right}")

        setR = {k for k, _ in ranked["R"]}
        setD = {k for k, _ in ranked["D"]}
        onlyR, onlyD = setR - setD, setD - setR
        print(f"\n  {BOLD}disagreements{OFF} — where the two geometries do not see the same word")
        print(f"    only R says: {', '.join(sorted(onlyR)) if onlyR else '(none)'}")
        print(f"    only D says: {', '.join(sorted(onlyD)) if onlyD else '(none)'}")
        print(f"    both:        {', '.join(sorted(setR & setD)) if setR & setD else '(none)'}")
        # the R-side names its edge, because that is the whole point of the signed matrix
        if onlyR:
            print(f"  {DIM}R's exclusives, with the relation that produced each:{OFF}")
            for k in sorted(onlyR):
                e = edge_of(base, "R", key, k) or edge_of(base, "R", k, key)
                print(f"    {k:<28} {e['rel'] if e else '(via a shared neighbour, no direct edge)'}")


# ------------------------------------------------------------------------------------------------
# 2. rel — the interrogation requirement (18) made usable
# ------------------------------------------------------------------------------------------------


def _rel_one(base: Base2, ka: str, kb: str):
    print(f"\n{BOLD}rel {ka} ~ {kb}{OFF}")
    for which in ("R", "D"):
        c = cos(base, which, ka, kb)
        fwd, rev = edge_of(base, which, ka, kb), edge_of(base, which, kb, ka)
        print(f"  {which}  cosine {c:+.3f}    {DIM}{LABEL[which]}{OFF}" if c is not None
              else f"  {which}  cosine   n/a")
        print(f"       cell [{ka} -> {kb}] = " +
              (f"{fwd['w']:+.3f}  via {BOLD}{fwd['rel']}{OFF}" if fwd else f"{DIM}0.000  (no cell){OFF}"))
        print(f"       cell [{kb} -> {ka}] = " +
              (f"{rev['w']:+.3f}  via {BOLD}{rev['rel']}{OFF}" if rev else f"{DIM}0.000  (no cell){OFF}"))

    eR = edge_of(base, "R", ka, kb) or edge_of(base, "R", kb, ka)
    if eR:
        print(f"  {GREEN}stated relation: {eR['rel']}{OFF} (R)")
    else:
        # the honest answer. A D score here is topicality, NOT a relation, and is labelled as such.
        eD = edge_of(base, "D", ka, kb) or edge_of(base, "D", kb, ka)
        print(f"  {RED}no stated relation{OFF} — WordNet names no edge between these two."
              + (f" D reports gloss overlap {eD['w']:+.3f}, which is co-occurrence, not a relation."
                 if eD else " D has no overlap either."))


def cmd_rel(base: Base2, args):
    ksa, ksb = base.require(args.a), base.require(args.b)
    if not ksa or not ksb:
        return
    for ka in ksa:
        for kb in ksb:
            _rel_one(base, ka, kb)


# ------------------------------------------------------------------------------------------------
# 3. opposite — the antonym COLUMN read, on R, where the sign survives
# ------------------------------------------------------------------------------------------------


def cmd_opposite(base: Base2, args):
    """antonyms(W) = { X : R[X][idx(W)] < 0 } — the same primitive as lib/llc/utils.utils_antonyms,
    read off R instead of the Jurassic base. Requirement 14: the sign is what makes this work, and
    measurement says it only survives in the sparse relational geometry."""
    keys = base.require(args.word)
    rows = base.rows("R") if keys else {}
    for key in keys:
        j = base.idx[key]
        hits = []
        for k, r in rows.items():
            if k == key:
                continue
            v = r["vector"][j]
            if v < 0:
                e = r.get("edges", {}).get(key)
                hits.append((k, v, e["rel"] if e else "?"))
        hits.sort(key=lambda t: t[1])
        print(f"\n{BOLD}opposite {key}{OFF}   column read on R  ({LABEL['R']})")
        if hits:
            for k, v, rel in hits:
                print(f"  {v:+.3f}  {k:<24} via {rel}")
        else:
            print(f"  {RED}(empty){OFF} — no dimension carries a negative cell on {key}'s axis. "
                  f"R states no opposition; abstaining rather than offering a far-neighbour.")

    # the Jurassic comparison — the live primitive on the body's 2925, for the same word
    word = C.split_key(args.word)[0]
    try:
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tokeniko"))
        from lib.core.io import init_io
        from lib.llc.utils import utils_antonyms
        init_io()
        got = sorted(utils_antonyms(word))
        print(f"\n{BOLD}J — Jurassic{OFF} `utils_antonyms('{word}')` on {CFG.SRC_DB}.base "
              f"(2925, POS-collapsed, live primitive)")
        print(f"  {', '.join(got) if got else '(empty)'}")
    except Exception as exc:                                  # noqa: BLE001 — a comparison, not a dependency
        print(f"\n{DIM}J — Jurassic utils_antonyms skipped: {type(exc).__name__}: {exc}{OFF}")


# ------------------------------------------------------------------------------------------------
# 4. effect — what the verb ENTAILS or CAUSES. Expected mostly empty, and that IS the answer.
# ------------------------------------------------------------------------------------------------

# `state_of` reads hungry.a -> eat.v («the state attached to eating»), so seen FROM the verb the
# state that follows it sits on the RECIPROCAL cell — widened per the Captain's ruling 2026-08-12.
FORWARD_EFFECT = ("entails", "causes", "state_of_reciprocal")
REVERSE_EFFECT = ("entailed_by", "caused_by", "state_of")


def cmd_effect(base: Base2, args):
    """Finding 3 of the review: `sleep~tired`, `sleep~bed`, `eat~hungry` are all 0.000 under
    relations only — there is no WordNet edge from an act to the state it ends. So an empty result
    here is a MEASUREMENT, not a failure, and it prints as exactly that. No similarity fallback:
    a near neighbour is not a consequence, and offering one would be the lie this command exists
    to avoid."""
    for key in base.require(args.verb):
        row = base.row("R", key)
        edges = (row or {}).get("edges", {})
        fwd = [(k, e) for k, e in edges.items() if e["rel"] in FORWARD_EFFECT]
        rev = [(k, e) for k, e in edges.items() if e["rel"] in REVERSE_EFFECT]
        print(f"\n{BOLD}effect {key}{OFF}   R only  ({LABEL['R']})")
        print(f"  {'entails / causes':<24} (what follows from it)")
        if fwd:
            for k, e in sorted(fwd, key=lambda t: -t[1]["w"]):
                print(f"    {e['w']:+.3f}  {k:<22} via {BOLD}{e['rel']}{OFF}")
        else:
            print(f"    {RED}(empty){OFF} — WordNet states no entailment or cause for {key}.")
        print(f"  {'entailed_by / caused_by':<24} (what it follows from)")
        if rev:
            for k, e in sorted(rev, key=lambda t: -t[1]["w"]):
                print(f"    {e['w']:+.3f}  {k:<22} via {BOLD}{e['rel']}{OFF}")
        else:
            print(f"    {RED}(empty){OFF}")
        if not fwd and not rev:
            print(f"  {DIM}the effect axis does not exist in WordNet for this verb — "
                  f"consequence is learned, not looked up (requirement 5).{OFF}")


# ------------------------------------------------------------------------------------------------
# 5. bar — tk2_config.PAIRS, scored against BOTH matrices. PAIRS is never edited to fit a result.
# ------------------------------------------------------------------------------------------------


def _cell(w):
    return f"{w:+.2f}" if w is not None else "  —  "


def _dual_read_table(scores, cells):
    """REQUIREMENT 19 — a verdict reads BOTH numbers.

    The CELL answers «is there a STATED relation between these two, and of what sign?». The COSINE
    answers «do their worlds overlap?». They are different questions and they are allowed to give
    different answers: a pair can carry a strong stated relation and still share almost no row mass
    (one directed cell out of a dozen), and a pair can share a lot of mass with nothing stated
    between them at all. Folding the two into one score is the Jurassic sin in miniature, so nothing
    below is averaged, blended or scored jointly — where the reads disagree, the disagreement is
    printed as the finding it is.
    """
    print(f"\n=== the bar, DUAL READ (requirement 19) — R cosine · R cell · D cosine ===")
    print(f"  {'pair':<24} {'exp':<5} {'R cosine':<16} {'R cell a->b':>11} {'b->a':>7}  "
          f"{'cell':<6} {'relation':<14} {'D cosine':<9}")
    print(f"  {'-'*24} {'-'*5} {'-'*16} {'-'*11} {'-'*7}  {'-'*6} {'-'*14} {'-'*9}")

    disagreements, mutes = [], []
    ok_cos = ok_cell = n_cell = 0
    for a, b, e, why in CFG.PAIRS:
        pair = (a, b, e, why)
        vR, vD = scores["R"][pair], scores["D"][pair]
        fwd, rev, rel = cells.get(pair, (None, None, None))
        w = fwd if fwd is not None else rev            # the stated relation, whichever way it runs
        vc, vk, note = P.dual_read(vR, w, e)

        if vc:
            ok_cos += 1
        if vk is not P.MUTE:
            n_cell += 1
            if vk:
                ok_cell += 1

        cos_s = f"{vR:+7.3f} {'ok ' if vc else 'MISS'}" if vR is not None else "    n/a     "
        colc = GREEN if vc else RED
        kmark = "MUTE" if vk is P.MUTE else ("ok " if vk else "MISS")
        colk = DIM if vk is P.MUTE else (GREEN if vk else RED)
        d_s = f"{vD:+7.3f}" if vD is not None else "   n/a "
        print(f"  {a+' ~ '+b:<24} {e:<5} {colc}{cos_s:<16}{OFF} {_cell(fwd):>11} {_cell(rev):>7}  "
              f"{colk}{kmark:<6}{OFF} {DIM}{(rel or '—'):<14}{OFF} {d_s}")

        if note.startswith("DISAGREE"):
            disagreements.append((a, b, e, note))
        elif vk is P.MUTE:
            mutes.append((a, b, e, vc))

    print(f"\n  cosine read: {ok_cos}/{len(CFG.PAIRS)} on the right side of the bar")
    print(f"  cell read:   {ok_cell}/{n_cell} of the pairs R actually speaks about "
          f"({len(CFG.PAIRS)-n_cell} mute — R states no relation, which is an ABSTENTION, "
          f"not a score of zero)")

    print(f"\n  {BOLD}where the two reads DISAGREE{OFF} — printed, never reconciled into one number")
    if disagreements:
        for a, b, e, note in disagreements:
            print(f"    {a:>10} ~ {b:<10} {e:4s}  {note}")
    else:
        print(f"    (none — on every pair R speaks about, the cell and the cosine agree)")

    print(f"  {BOLD}where R is MUTE{OFF} — no stated relation, so only the cosine spoke")
    for a, b, e, vc in mutes:
        print(f"    {a:>10} ~ {b:<10} {e:4s}  cosine {'ok ' if vc else 'MISS'}  "
              f"{DIM}— the cell has nothing to say; a NEAR here is carried by shared mass alone{OFF}")
    if not mutes:
        print(f"    (none)")


def cmd_bar(base: Base2, args):
    print(f"bar: NEAR >= {CFG.NEAR_FLOOR}   FAR <= {CFG.FAR_CEILING}   pairs: {len(CFG.PAIRS)}   "
          f"base '{base.base}' ({len(base.keys)} dims)")

    scores = {"R": {}, "D": {}}
    rels = {"R": {}, "D": {}}
    cells = {}                      # pair -> (fwd, rev, rel) on R, requirement 19's other half
    for a, b, e, why in CFG.PAIRS:
        pair = (a, b, e, why)
        for which in ("R", "D"):
            ka = base.resolve(a)
            kb = base.resolve(b)
            if not ka or not kb:
                scores[which][pair] = None
                rels[which][pair] = f"missing:{a if not ka else b}"
                if which == "R":
                    cells[pair] = (None, None, None)
                continue
            ka, kb = ka[0], kb[0]
            scores[which][pair] = cos(base, which, ka, kb)
            fwd, rev = edge_of(base, which, ka, kb), edge_of(base, which, kb, ka)
            edge = fwd or rev
            rels[which][pair] = edge["rel"] if edge else "—"
            if which == "R":
                cells[pair] = (fwd["w"] if fwd else None, rev["w"] if rev else None,
                               edge["rel"] if edge else None)

    for which in ("R", "D"):
        P.report(f"{which} — {LABEL[which]}", scores[which], rels[which])

    _dual_read_table(scores, cells)

    # the side-by-side that is the actual point: where does the choice of matrix flip the verdict?
    print(f"\n=== where the matrix choice FLIPS the verdict ===")
    flips = 0
    for a, b, e, why in CFG.PAIRS:
        pair = (a, b, e, why)
        vR, vD = scores["R"][pair], scores["D"][pair]
        gR, gD = P.verdict(vR, e), P.verdict(vD, e)
        if gR is None or gD is None or gR == gD:
            continue
        flips += 1
        winner = "R" if gR else "D"
        print(f"  {a:>10} ~ {b:<10} {e:4s}  R {vR:+.3f} {'ok ' if gR else 'MISS'}   "
              f"D {vD:+.3f} {'ok ' if gD else 'MISS'}   -> only {BOLD}{winner}{OFF} is right")
    if not flips:
        print("  (none — the two matrices agree on every scorable pair)")

    print(f"\n{DIM}summary: R {sum(1 for k,v in scores['R'].items() if P.verdict(v,k[2]) is True)}"
          f"/{sum(1 for v in scores['R'].values() if v is not None)}   "
          f"D {sum(1 for k,v in scores['D'].items() if P.verdict(v,k[2]) is True)}"
          f"/{sum(1 for v in scores['D'].values() if v is not None)}   "
          f"— and neither number is the answer on its own: a pair belongs to the matrix that can "
          f"honestly speak to it.{OFF}")


# ------------------------------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser(prog="tk2", description=__doc__.split("\n")[0])
    ap.add_argument("--base", default=CFG.BASE2_NAME, help="which two-matrix base to consult")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("near", help="nearest neighbours in R and D, side by side, plus disagreements")
    p.add_argument("word")
    p.add_argument("--k", type=int, default=10)
    p.set_defaults(fn=cmd_near)

    p = sub.add_parser("rel", help="the relation between two words: R signed, D topical, named edges")
    p.add_argument("a")
    p.add_argument("b")
    p.set_defaults(fn=cmd_rel)

    p = sub.add_parser("opposite", help="the antonym column read on R (+ the live Jurassic primitive)")
    p.add_argument("word")
    p.set_defaults(fn=cmd_opposite)

    p = sub.add_parser("effect", help="what the verb entails/causes — an honest empty is a result")
    p.add_argument("verb")
    p.set_defaults(fn=cmd_effect)

    p = sub.add_parser("bar", help="score tk2_config.PAIRS against both matrices")
    p.set_defaults(fn=cmd_bar)

    args = ap.parse_args()
    args.fn(Base2(args.base), args)


if __name__ == "__main__":
    main()
