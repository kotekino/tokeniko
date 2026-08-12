#!/usr/bin/env python
"""tk2 stage 3 — THE BAR.

Scores the pairs declared in tk2_config.PAIRS *before* any matrix existed, under both geometries
side by side: the Jurassic 2925 base and a candidate run. Prints, per pair, which relation carried
the candidate cell — so a pass can be inspected rather than trusted.

    python scripts/tk2/tk2_probe.py --run r1
    python scripts/tk2/tk2_probe.py --run r1 --compare r2-no-gloss
"""

import argparse
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import tk2_config as CFG
import tk2_common as C

GREEN, RED, DIM, OFF = "\033[32m", "\033[31m", "\033[2m", "\033[0m"


def load_run(run: str):
    db = C.tk2_db()
    rows = list(db.base_candidate.find({"run": run}, {"key": 1, "index": 1, "vector": 1, "edges": 1}))
    if not rows:
        raise SystemExit(f"no run '{run}' in {CFG.TK2_DB}.base_candidate")
    return {r["key"]: r for r in rows}


def candidate_cos(rows, ka, kb):
    ra, rb = rows.get(ka), rows.get(kb)
    if ra is None or rb is None:
        return None, f"missing:{ka if ra is None else kb}"
    val = C.cosine(ra["vector"], rb["vector"])
    edge = ra.get("edges", {}).get(kb) or rb.get("edges", {}).get(ka)
    return val, (edge["rel"] if edge else "—")


def jurassic_cos(a: str, b: str):
    """The body's base is POS-collapsed, so a `.v`/`.n` qualifier is simply dropped — which is
    exactly the defect under review, and showing it as one number is the point."""
    wa, wb = C.split_key(a)[0], C.split_key(b)[0]
    va, vb = C.base_vector(wa), C.base_vector(wb)
    if va is None or vb is None:
        return None, f"not-base:{wa if va is None else wb}"
    return C.cosine(va, vb), ("collapsed" if wa == wb else "")


def verdict(val, expect):
    if val is None:
        return None
    if expect == "NEAR":
        return val >= CFG.NEAR_FLOOR
    return val <= CFG.FAR_CEILING


# ------------------------------------------------------------------------------------------------
# REQUIREMENT 19 — THE DUAL READ. The cell and the cosine answer two different questions, and the
# bar reads BOTH. Kept here rather than in tk2.py so the simulation in tk2_curate.py scores a
# proposal with exactly the same logic the bar uses — a simulated verdict that used its own rules
# would be measuring the rules, not the proposal.
# ------------------------------------------------------------------------------------------------

MUTE = "MUTE"          # R declines to speak: no cell in either direction. Not a pass, not a miss.


def cell_verdict(w, expect):
    """(verdict, why) for the DIRECT cell. `w` is the signed weight of the stated relation, or None.

    NEAR wants a stated positive relation; a negative one is R asserting the opposite of what the bar
    expects, which is a violation rather than a weak score.
    FAR is satisfied by opposition (a negative cell IS stated farness) and by silence — but silence is
    reported as MUTE, never dressed up as agreement.
    """
    if w is None:
        return (True, "mute — R states no relation") if expect == "FAR" else (MUTE, "mute — R states no relation")
    if expect == "NEAR":
        if w < 0:
            return False, f"stated OPPOSITION ({w:+.2f}) where the bar expects NEAR"
        return (True, "stated relation") if w >= CFG.CELL_NEAR_FLOOR else (False, f"stated but weak ({w:+.2f})")
    if w < 0:
        return True, "opposition stated"
    return (False, f"stated relation ({w:+.2f}) where the bar expects FAR") if w > CFG.CELL_FAR_CEILING \
        else (True, f"stated but negligible ({w:+.2f})")


def dual_read(cos_val, cell_w, expect):
    """(cosine verdict, cell verdict, agreement note). The two are never folded into one score —
    where they disagree the disagreement IS the finding, and it gets printed."""
    vc = verdict(cos_val, expect)
    vk, why = cell_verdict(cell_w, expect)
    if vk is MUTE:
        note = f"cosine {'ok' if vc else 'MISS'} / cell MUTE — no stated relation to agree or disagree with"
    elif vc is None:
        note = "unscorable"
    elif vc == vk:
        note = ""
    else:
        note = (f"DISAGREE — cosine says {'ok' if vc else 'MISS'}, cell says {'ok' if vk else 'MISS'}: {why}")
    return vc, vk, note


def local_order(scores):
    """Absolute thresholds drift between runs; the ORDER should not. Every NEAR pair must out-score
    every FAR pair that shares a word with it."""
    bad = []
    for (a1, b1, e1, _), v1 in scores.items():
        if e1 != "NEAR" or v1 is None:
            continue
        w1 = {C.split_key(a1)[0], C.split_key(b1)[0]}
        for (a2, b2, e2, _), v2 in scores.items():
            if e2 != "FAR" or v2 is None:
                continue
            if w1 & {C.split_key(a2)[0], C.split_key(b2)[0]} and v1 <= v2:
                bad.append((f"{a1}~{b1}", v1, f"{a2}~{b2}", v2))
    return bad


def report(title, scores, rels):
    ok = sum(1 for k, v in scores.items() if verdict(v, k[2]) is True)
    na = sum(1 for v in scores.values() if v is None)
    n = len(scores) - na
    print(f"\n=== {title} — {ok}/{n} pairs on the right side of the bar" + (f", {na} unscorable" if na else "") + " ===")
    for key in sorted(scores, key=lambda k: (k[2], -(scores[k] if scores[k] is not None else -9))):
        a, b, expect, why = key
        v = scores[key]
        if v is None:
            print(f"  {DIM}{'n/a':>7}  {a:>10} ~ {b:<10} {expect:4s}  {rels.get(key,'')}{OFF}")
            continue
        good = verdict(v, expect)
        col = GREEN if good else RED
        mark = "ok " if good else "MISS"
        print(f"  {col}{v:7.3f}{OFF}  {a:>10} ~ {b:<10} {expect:4s} {col}{mark}{OFF}  {DIM}{rels.get(key,'')}{OFF}")

    bad = local_order(scores) if CFG.REQUIRE_LOCAL_ORDER else []
    if bad:
        print(f"  {RED}local-order violations: {len(bad)}{OFF}")
        for n1, v1, n2, v2 in bad[:8]:
            print(f"    {n1} ({v1:.3f}) does not beat {n2} ({v2:.3f})")
    elif CFG.REQUIRE_LOCAL_ORDER:
        print(f"  {GREEN}local order: clean{OFF}")
    return ok, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--compare", help="a second candidate run to score alongside")
    ap.add_argument("--no-jurassic", action="store_true")
    args = ap.parse_args()

    print(f"bar: NEAR >= {CFG.NEAR_FLOOR}   FAR <= {CFG.FAR_CEILING}   pairs: {len(CFG.PAIRS)}")

    if not args.no_jurassic:
        s, r = {}, {}
        for a, b, e, why in CFG.PAIRS:
            v, note = jurassic_cos(a, b)
            s[(a, b, e, why)] = v
            r[(a, b, e, why)] = note
        report(f"JURASSIC base ({CFG.SRC_DB}.base, 2925 dims, POS-collapsed)", s, r)

    for run in [args.run] + ([args.compare] if args.compare else []):
        rows = load_run(run)
        s, r = {}, {}
        for a, b, e, why in CFG.PAIRS:
            v, note = candidate_cos(rows, a, b)
            s[(a, b, e, why)] = v
            r[(a, b, e, why)] = note
        meta = C.tk2_db().runs.find_one({"run": run}) or {}
        report(f"CANDIDATE '{run}' ({meta.get('dims','?')} dims){' — ' + meta['note'] if meta.get('note') else ''}", s, r)

    print(f"\n{DIM}pairs are the bar declared in tk2_config.PAIRS before any matrix existed; "
          f"changing them after a result is how a review talks itself into success.{OFF}")


if __name__ == "__main__":
    main()
