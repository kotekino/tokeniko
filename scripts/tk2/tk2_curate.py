#!/usr/bin/env python
"""tk2 stage 4 — DEFINITIONAL CURATION. PROPOSALS ONLY.

The Captain's ruling of 2026-08-12 (requirement 20): a manual edge may enter R only when it is
ANALYTIC — *stated in a definition* — never when it is contingent. Sayings, slang and context-bound
readings are knowledge, and knowledge lives in the KB (requirement 5: consequence is learned, not
looked up). What a dictionary asserts outright is a different thing, and that is what this stage
mines.

And definitions are CROSS-REFERENCED. `sleep`'s gloss is «be asleep» and never mentions a bed;
`bed`'s gloss is «a piece of furniture that provides a place to sleep» and names sleeping outright.
So the miner reads BOTH sides of a pair and mints the edge from whichever definition actually
speaks — DIRECTED, `bed.n -> sleep.v`, because that is the direction the statement runs in.

    python scripts/tk2/tk2_curate.py propose                       # the four bar misses
    python scripts/tk2/tk2_curate.py propose --pairs eat.v:food.n,bed.n:sleep.v
    python scripts/tk2/tk2_curate.py propose --word sleep.v        # one key against every dimension
    python scripts/tk2/tk2_curate.py simulate                      # would it close the gaps?
    python scripts/tk2/tk2_curate.py approve <id> ... --i-am-the-captain

NOTHING here writes to `base_relational`. `propose` and `simulate` touch exactly one collection,
`tokeniko_tk2.curation_proposals`, and `simulate` mutates only an in-memory copy of the matrix. The
matrix itself is changed by `approve`, which refuses to run without the Captain's flag: the whole
point of the ruling is that a curated cell is a HUMAN judgement, and a script that could mint one on
its own would have quietly taken that judgement over.
"""

import argparse
import copy
import sys
import time

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import tk2_config as CFG
import tk2_common as C
import tk2_probe as P                      # the bar's verdict + dual-read logic, not re-typed

GREEN, RED, YELLOW, DIM, BOLD, OFF = (
    "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[1m", "\033[0m")


# ------------------------------------------------------------------------------------------------
# the miner
# ------------------------------------------------------------------------------------------------


def proposal_id(src: str, dst: str) -> str:
    """Readable and stable: the same edge proposed twice is the same id, so `propose` can replace a
    pending row instead of accumulating duplicates, and the Captain approves by reading the table
    rather than by copying an ObjectId."""
    return f"{src}>{dst}"


def pick_rel(src_key: str, dst_key: str, gloss: str) -> str:
    """Which of the six closed relation names this gloss looks like it is stating. A GUESS — cue
    words first (tk2_config.CURATION_CUES, in order), then the POS pair, then `involves`, which
    claims only what the miner actually observed: the definition names it."""
    low = f" {gloss.lower()} "
    for rel, cues in CFG.CURATION_CUES:
        if any(f" {c} " in low for c in cues):
            return rel
    sp, dp = C.split_key(src_key)[1], C.split_key(dst_key)[1]
    return CFG.CURATION_POS_DEFAULT.get((sp, dp), "involves")


def quote(gloss: str, token: str) -> str:
    """The evidence: the gloss verbatim, with the naming word made visible. Verbatim on purpose —
    a paraphrase is the curator arguing rather than the dictionary speaking."""
    out, marked = [], False
    for w in gloss.split():
        bare = w.strip(".,;:()").lower()
        if not marked and bare == token.lower():
            out.append(w.replace(bare, f"<{bare}>") if bare in w else f"<{w}>")
            marked = True
        else:
            out.append(w)
    return "«" + " ".join(out) + "»"


def mine_directed(src_key: str, dst_key: str, senses: str) -> dict | None:
    """Does SRC's definition name DST? If so, that is a directed analytic edge src -> dst."""
    src_word, dst_word = C.split_key(src_key)[0], C.split_key(dst_key)[0]
    if src_word == dst_word:
        # self-reference across a POS boundary («land: the land on which real estate is located»)
        # is a tautology, not a stated relation between two concepts — see CURATION_SKIP_SELF_REFERENCE
        if CFG.CURATION_SKIP_SELF_REFERENCE:
            return None
    for syn in C.synsets_of_key(src_key, senses):
        gloss = syn.definition()
        token = C.gloss_names_word(gloss, dst_word)
        if not token:
            continue
        rel = pick_rel(src_key, dst_key, gloss)
        return {
            "pid": proposal_id(src_key, dst_key),
            "src_key": src_key,
            "dst_key": dst_key,
            "proposed_rel": rel,
            "weight": CFG.CURATED_WEIGHTS[rel],
            "evidence": f"{syn.name()} {quote(gloss, token)}",
            "gloss_sense": syn.name(),
            "gloss": gloss,
            "naming_token": token,
            "status": "pending",
        }
    return None


def mine_pair(a: str, b: str, senses: str) -> list[dict]:
    """Both directions. Cross-reference means neither side is privileged: whichever gloss speaks,
    speaks — and when both do, both edges are proposed, each with its own evidence."""
    return [p for p in (mine_directed(a, b, senses), mine_directed(b, a, senses)) if p]


def self_reference_skips(pairs, senses) -> list[tuple[str, str, str]]:
    """The skips, surfaced rather than silent: a same-word pair whose gloss DOES name its own
    headword would have produced an edge but for CURATION_SKIP_SELF_REFERENCE, and the reader is
    entitled to know the miner stayed its hand and why."""
    out = []
    if not CFG.CURATION_SKIP_SELF_REFERENCE:
        return out
    for a, b in pairs:
        wa, wb = C.split_key(a)[0], C.split_key(b)[0]
        if wa != wb:
            continue
        for src, dst in ((a, b), (b, a)):
            for syn in C.synsets_of_key(src, senses):
                tok = C.gloss_names_word(syn.definition(), C.split_key(dst)[0])
                if tok:
                    out.append((src, dst, f"{syn.name()} {quote(syn.definition(), tok)}"))
                    break
    return out


# ------------------------------------------------------------------------------------------------
# the table — THE deliverable of `propose`. The Captain approves BY EYE, from this.
# ------------------------------------------------------------------------------------------------


def print_table(proposals: list[dict], keyset: set[str] | None = None):
    if not proposals:
        print(f"  {RED}(no proposals){OFF} — no definition on either side names the other word.")
        return
    print(f"  {'id':<24} {'src':>10} -> {'dst':<10} {'relation':<10} {'w':>6}   sense")
    print(f"  {'-'*24} {'-'*10}    {'-'*10} {'-'*10} {'-'*6}   {'-'*18}")
    for p in proposals:
        off = "" if keyset is None or (p["src_key"] in keyset and p["dst_key"] in keyset) \
            else f"  {RED}[not a dimension of the base — no axis to write to]{OFF}"
        print(f"  {p['pid']:<24} {p['src_key']:>10} -> {p['dst_key']:<10} "
              f"{BOLD}{p['proposed_rel']:<10}{OFF} {p['weight']:+6.2f}   {DIM}{p['gloss_sense']}{OFF}{off}")
        print(f"    {DIM}evidence:{OFF} {p['evidence']}")


# ------------------------------------------------------------------------------------------------
# 1. propose
# ------------------------------------------------------------------------------------------------


def parse_pairs(spec: str) -> list[tuple[str, str]]:
    out = []
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if ":" not in chunk:
            raise SystemExit(f"--pairs wants `a.p:b.q` items; got '{chunk}'")
        a, b = chunk.split(":", 1)
        out.append((a.strip().lower(), b.strip().lower()))
    return out


def load_keys(db, base: str) -> list[str]:
    man = db.base2_manifest.find_one({"base": base}, {"keys": 1, "senses": 1})
    if not man:
        raise SystemExit(f"no two-matrix base '{base}' in {CFG.TK2_DB}.base2_manifest — "
                         f"run: python scripts/tk2/tk2_build2.py --apply")
    return man["keys"], man.get("senses", CFG.DEFINITION_SENSES)


def cmd_propose(args):
    db = C.tk2_db()
    keys, base_senses = load_keys(db, args.base)
    keyset = set(keys)
    senses = args.senses or base_senses

    if args.word:
        word = args.word.strip().lower()
        if word not in keyset:
            raise SystemExit(f"'{word}' is not a dimension of base '{args.base}'.")
        pairs = [(word, k) for k in keys if k != word]
        scope = f"--word {word} against all {len(keys)-1} other dimensions"
    else:
        pairs = parse_pairs(args.pairs) if args.pairs else list(CFG.CURATION_TARGET_PAIRS)
        scope = f"{len(pairs)} target pair(s)"

    print(f"{BOLD}tk2 stage 4 — definitional curation, PROPOSALS ONLY{OFF}")
    print(f"base '{args.base}' ({len(keys)} dims) · senses '{senses}' · {scope}")
    print(f"{DIM}requirement 20: a curated edge must be ANALYTIC — stated in a definition. "
          f"Contingent knowledge stays in the KB.{OFF}\n")

    proposals = []
    for a, b in pairs:
        proposals.extend(mine_pair(a, b, senses))

    # deterministic and readable: strongest claim first, then alphabetically
    proposals.sort(key=lambda p: (-p["weight"], p["src_key"], p["dst_key"]))

    print(f"=== PROPOSALS ({len(proposals)}) ===")
    print_table(proposals, keyset)

    skips = self_reference_skips(pairs, senses)
    if skips:
        print(f"\n=== SKIPPED as SELF-REFERENCE ({len(skips)}) ===")
        print(f"  {DIM}a definition naming its own headword under another POS is a tautology, not a "
              f"stated relation.{OFF}")
        for src, dst, ev in skips:
            print(f"  {YELLOW}{src} -> {dst}{OFF}  {ev}")

    silent = [(a, b) for a, b in pairs
              if not any(p["src_key"] in (a, b) and p["dst_key"] in (a, b) for p in proposals)]
    if silent and not args.word:
        print(f"\n=== NO DEFINITION SPEAKS ({len(silent)}) ===")
        print(f"  {DIM}neither gloss names the other word — an honest «curation cannot reach this "
              f"one», not a tuning failure.{OFF}")
        for a, b in silent:
            for k in (a, b):
                for syn in C.synsets_of_key(k, senses):
                    print(f"  {a} ~ {b}   {k:>9}  {syn.name()} «{syn.definition()}»")
                    break

    if args.dry_run:
        print(f"\n{DIM}(--dry-run: nothing stored){OFF}")
        return

    coll = db[CFG.CURATION_COLLECTION]
    for p in proposals:
        coll.delete_many({"base": args.base, "src_key": p["src_key"],
                          "dst_key": p["dst_key"], "status": "pending"})
    if proposals:
        coll.insert_many([{"base": args.base, "proposed_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                           **p} for p in proposals])
        coll.create_index([("base", 1), ("pid", 1)])
    print(f"\nstored: {CFG.TK2_DB}.{CFG.CURATION_COLLECTION} — {len(proposals)} pending proposal(s). "
          f"{BOLD}base_relational untouched.{OFF}")


# ------------------------------------------------------------------------------------------------
# 2. simulate — would it close the gaps? Nothing is committed.
# ------------------------------------------------------------------------------------------------


def load_R(db, base: str) -> dict:
    return {r["key"]: r for r in db.base_relational.find(
        {"base": base}, {"key": 1, "index": 1, "vector": 1, "edges": 1})}


def read_pair(rows, idx, a, b):
    """(cosine, directed cell a->b, directed cell b->a, relation name). The cell is read in BOTH
    directions because R is asymmetric on purpose (the antonym column-read depends on it)."""
    ra, rb = rows.get(a), rows.get(b)
    if ra is None or rb is None:
        return None, None, None, None
    cos = C.cosine(ra["vector"], rb["vector"])
    ef = ra.get("edges", {}).get(b)
    er = rb.get("edges", {}).get(a)
    best = ef or er
    return cos, (ef["w"] if ef else None), (er["w"] if er else None), (best["rel"] if best else None)


def cells_of(p: dict) -> list[tuple[str, str, dict]]:
    """The TWO cells one curated edge writes — (row key, column key, provenance).

    The Captain's ruling of 2026-08-12: forward at the proposal's weight, reverse at
    CURATED_RECIPROCAL_WEIGHT. Measured before the ruling: one-way only, `sleep.v~bed.n` reaches
    0.217 and `eat.v~hungry.a` 0.193 — the stated-relation read passes and the cosine read still
    misses. The back-reference is what makes the two reads agree, and 0.60 is R's own existing
    convention (`entails` 0.80 / `entailed_by` 0.60), not a number chosen to clear the bar.

    ONE function, called by both `simulate` and `approve`, so a simulation can never be measuring a
    different edge shape than the one approval would write.
    """
    fwd = {"w": float(p["weight"]), "rel": p["proposed_rel"], "src": "curated",
           "evidence": p["evidence"]}
    rev = {"w": float(CFG.CURATED_RECIPROCAL_WEIGHT),
           "rel": p["proposed_rel"] + CFG.CURATED_RECIPROCAL_SUFFIX,
           "src": "curated", "evidence": p["evidence"], "reciprocal": True,
           "of": f"{p['src_key']} -> {p['dst_key']}"}
    return [(p["src_key"], p["dst_key"], fwd), (p["dst_key"], p["src_key"], rev)]


def apply_proposals(rows, idx, proposals) -> list[str]:
    """IN MEMORY ONLY. Returns the notes worth printing — a proposal that lands on a cell WordNet
    already filled is an overwrite, and an overwrite must never be silent."""
    notes = []
    for p in proposals:
        if p["src_key"] not in rows or p["dst_key"] not in rows:
            notes.append(f"{RED}skipped {p['src_key']} -> {p['dst_key']}: "
                         f"not a dimension of this base{OFF}")
            continue
        for s, d, prov in cells_of(p):
            prev = rows[s].get("edges", {}).get(d)
            if prev:
                notes.append(f"{YELLOW}{s} -> {d}: OVERWRITES an existing cell "
                             f"({prev['w']:+.2f} via {prev['rel']}) with {prov['w']:+.2f} via "
                             f"{prov['rel']}{OFF}")
            rows[s]["vector"][idx[d]] = prov["w"]
            rows[s].setdefault("edges", {})[d] = prov
    return notes


def _fmt_cell(w):
    return f"{w:+.2f}" if w is not None else "  —  "


def cmd_simulate(args):
    db = C.tk2_db()
    keys, _senses = load_keys(db, args.base)
    idx = {k: i for i, k in enumerate(keys)}

    q = {"base": args.base, "status": "pending"}
    if args.ids:
        q["pid"] = {"$in": args.ids}
    proposals = list(db[CFG.CURATION_COLLECTION].find(q))
    if not proposals:
        raise SystemExit(f"no pending proposals in {CFG.TK2_DB}.{CFG.CURATION_COLLECTION} for base "
                         f"'{args.base}' — run `propose` first.")

    rows_before = load_R(db, args.base)
    rows_after = copy.deepcopy(rows_before)
    notes = apply_proposals(rows_after, idx, proposals)

    print(f"{BOLD}{YELLOW}=== SIMULATION — NOTHING IS COMMITTED ==={OFF}")
    print(f"base '{args.base}' · {len(proposals)} pending proposal(s) applied to an IN-MEMORY copy "
          f"of R.\n{DIM}base_relational on disk is unchanged; re-run the bar afterwards and it will "
          f"read exactly what it read before.{OFF}\n")
    for p in sorted(proposals, key=lambda p: p["pid"]):
        for s_, d_, prov in cells_of(p):
            tag = f"{DIM}reciprocal{OFF}" if prov.get("reciprocal") else f"{DIM}{p['gloss_sense']}{OFF}"
            print(f"  applied  {s_:>10} -> {d_:<10} {prov['rel']:<22} {prov['w']:+.2f}   {tag}")
    for n in notes:
        print(f"  {n}")

    print(f"\n{BOLD}=== the bar, before -> after (R only) ==={OFF}")
    print(f"{DIM}requirement 19: the CELL answers «is there a stated relation», the COSINE «do their "
          f"worlds overlap». Both are printed; neither is folded into the other.{OFF}")
    print(f"\n  {'pair':<24} {'exp':<5} {'cosine before -> after':<30} "
          f"{'cell a->b':<18} {'cell b->a':<18} relation")
    print(f"  {'-'*24} {'-'*5} {'-'*30} {'-'*18} {'-'*18} {'-'*10}")

    moved, closed, broken = [], [], []
    ok_before = ok_after = 0
    for a, b, expect, _why in CFG.PAIRS:
        cb, fb, rb_, relb = read_pair(rows_before, idx, a, b)
        ca, fa, ra_, rela = read_pair(rows_after, idx, a, b)
        if cb is None or ca is None:
            print(f"  {a+' ~ '+b:<24} {expect:<5} {DIM}unscorable — a key is not a dimension{OFF}")
            continue

        vb = P.verdict(cb, expect)
        va = P.verdict(ca, expect)
        ok_before += 1 if vb else 0
        ok_after += 1 if va else 0

        cell_b = fb if fb is not None else rb_
        cell_a = fa if fa is not None else ra_
        kvb, _ = P.cell_verdict(cell_b, expect)
        kva, whya = P.cell_verdict(cell_a, expect)

        changed = abs(ca - cb) > 1e-9 or fa != fb or ra_ != rb_
        mark = f"{BOLD}*{OFF}" if changed else " "
        colb = GREEN if vb else RED
        cola = GREEN if va else RED
        arrow = "->"
        print(f" {mark}{a+' ~ '+b:<24} {expect:<5} "
              f"{colb}{cb:+7.3f}{OFF} {arrow} {cola}{ca:+7.3f}{OFF} "
              f"{'ok ' if va else 'MISS':<4}      "
              f"{_fmt_cell(fb)} {arrow} {_fmt_cell(fa):<8} "
              f"{_fmt_cell(rb_)} {arrow} {_fmt_cell(ra_):<8} "
              f"{DIM}{rela or relb or '—'}{OFF}")

        if changed:
            moved.append((a, b, expect, cb, ca, cell_b, cell_a, kvb, kva, whya))
        if not vb and va:
            closed.append(f"{a}~{b} ({expect})")
        if vb and not va:
            broken.append(f"{a}~{b} ({expect})")

    print(f"\n  {DIM}* = the proposals moved this pair (cosine or cell).{OFF}")
    print(f"  cosine verdicts: {ok_before}/{len(CFG.PAIRS)} -> {ok_after}/{len(CFG.PAIRS)}")
    print(f"  {GREEN}closed by the proposals:{OFF} {', '.join(closed) if closed else '(none)'}")
    print(f"  {RED}broken by the proposals:{OFF} {', '.join(broken) if broken else '(none)'}")

    # THE ASYMMETRY. A single directed cell can flip the stated-relation read while the row cosine
    # barely moves — the two reads are measuring different things (requirement 19) and pretending
    # otherwise is exactly the collapse the ruling forbids. Printed whether or not it flatters us.
    print(f"\n{BOLD}=== the cell/cosine asymmetry, per moved pair ==={OFF}")
    if not moved:
        print("  (nothing moved)")
    for a, b, expect, cb, ca, kb_, ka_, kvb, kva, whya in moved:
        dc = ca - cb
        cellmsg = f"{_fmt_cell(kb_)} -> {_fmt_cell(ka_)}"
        vb_s = "MUTE" if kvb is P.MUTE else ("ok" if kvb else "MISS")
        va_s = "MUTE" if kva is P.MUTE else ("ok" if kva else "MISS")
        flip_cell = vb_s != va_s
        flip_cos = P.verdict(cb, expect) != P.verdict(ca, expect)
        verdictline = (
            f"cell {vb_s} -> {va_s}" + ("  (FLIPPED)" if flip_cell else "  (unchanged)")
            + f"   ·   cosine {'ok' if P.verdict(cb, expect) else 'MISS'} -> "
              f"{'ok' if P.verdict(ca, expect) else 'MISS'}" + ("  (FLIPPED)" if flip_cos else "  (unchanged)"))
        print(f"  {a} ~ {b}  [{expect}]")
        print(f"      cosine {cb:+.3f} -> {ca:+.3f}   (delta {dc:+.3f})      cell {cellmsg}")
        print(f"      {verdictline}")
        if flip_cell and not flip_cos:
            print(f"      {YELLOW}ASYMMETRY: the stated-relation read now passes while the cosine "
                  f"read does not. One directed cell states the relation; it does not by itself make "
                  f"the two rows' worlds overlap.{OFF}")
        elif flip_cos and not flip_cell:
            print(f"      {YELLOW}ASYMMETRY: the cosine moved across the bar while the stated-relation "
                  f"read did not change.{OFF}")

    print(f"\n{BOLD}{YELLOW}=== END SIMULATION — base_relational was never opened for writing ==={OFF}")


# ------------------------------------------------------------------------------------------------
# 3. approve — THE CAPTAIN'S HAND ONLY. Written, never run by the officer who wrote it.
# ------------------------------------------------------------------------------------------------


def cmd_approve(args):
    """The only subcommand that would touch `base_relational`, and it is gated on purpose.

    Requirement 20 makes a curated edge a HUMAN judgement: analytic vs contingent is exactly the call
    a miner cannot make, which is why `propose` prints a table for the eye instead of writing cells.
    A script able to mint its own curated cell would have quietly taken that judgement over, so the
    guard is not ceremony — it is the mechanism the ruling needs to stay true.
    """
    if not args.i_am_the_captain:
        print(f"{RED}{BOLD}REFUSED.{OFF} `approve` writes curated cells into "
              f"{CFG.TK2_DB}.base_relational, and requirement 20 makes that call the Captain's, not "
              f"the instrument's.")
        print(f"  A proposal is ANALYTIC or CONTINGENT, and only a reader of the evidence can say "
              f"which. Re-run with {BOLD}--i-am-the-captain{OFF} to assert you are that reader.")
        print(f"  {DIM}Nothing was written. `simulate` answers «would it work?» without this flag.{OFF}")
        raise SystemExit(2)

    db = C.tk2_db()
    keys, _ = load_keys(db, args.base)
    idx = {k: i for i, k in enumerate(keys)}
    coll = db[CFG.CURATION_COLLECTION]

    q = {"base": args.base, "status": "pending"}
    if args.ids:
        q["pid"] = {"$in": args.ids}
    proposals = list(coll.find(q))
    if not proposals:
        raise SystemExit("no pending proposals matching those ids.")

    stamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    written = []
    for p in proposals:
        if p["src_key"] not in idx or p["dst_key"] not in idx:
            print(f"{RED}skipped {p['pid']}: not a dimension of base '{args.base}'{OFF}")
            continue
        # provenance is the whole contract of R (requirement 18): the cell names the relation that
        # made it, says the hand was curated, and carries the evidence that justified it.
        for s_, d_, prov in cells_of(p):
            # the edges map is rewritten WHOLE rather than through a dotted `edges.<key>` path: a
            # dimension key contains a dot (`sleep.v`), which mongo reads as a nested path and would
            # silently write the wrong field. Read, mutate, set. The vector index is safe either
            # way, being a number.
            row = db.base_relational.find_one({"base": args.base, "key": s_},
                                              {"vector": 1, "edges": 1})
            edges = row.get("edges", {})
            edges[d_] = prov
            vec = row["vector"]
            vec[idx[d_]] = prov["w"]
            db.base_relational.update_one({"base": args.base, "key": s_},
                                          {"$set": {"vector": vec, "edges": edges}})
            written.append({"pid": p["pid"], "src_key": s_, "dst_key": d_, **prov})
            print(f"{GREEN}written{OFF} {s_:>10} -> {d_:<10} {prov['rel']:<22} {prov['w']:+.2f}")
        coll.update_one({"_id": p["_id"]},
                        {"$set": {"status": "approved", "approved_at": stamp,
                                  "authorized": args.authorized}})

    if written:
        stats = recount_R(db, args.base)
        db.base2_manifest.update_one(
            {"base": args.base},
            {"$push": {"curated_edges": {"$each": written}},
             "$set": {"curated_at": stamp,
                      "curated_authorized": args.authorized,
                      "curated_reciprocal_weight": CFG.CURATED_RECIPROCAL_WEIGHT,
                      "density.relational": stats}},
        )
        print(f"\nmanifest updated: {len(written)} curated cell(s) declared under `curated_edges`, "
              f"authorization recorded — a curated cell is never smuggled (the same rule as "
              f"`added_words`, requirement 15).")
        print(f"  R density {stats['density_pct']:.3f}%  ({stats['nonzero']} non-zero = "
              f"{stats['wordnet_nonzero']} WordNet + {stats['curated_nonzero']} curated)")
        for rel, k in sorted(stats["by_relation_curated"].items()):
            print(f"    curated  {rel:24s} {k}")


def recount_R(db, base: str) -> dict:
    """Re-derive R's density from what is actually on disk, with the CURATED cells counted APART
    from the mined ones. Two provenances must never sit in one total: the whole claim of R is that a
    cell can be asked where it came from, and a headline density that hides the hand is the first
    step back to a matrix nobody can audit."""
    rows = list(db.base_relational.find({"base": base}, {"edges": 1}))
    n = len(rows)
    by_rel, by_cur = {}, {}
    wordnet = curated = 0
    for r in rows:
        for e in r.get("edges", {}).values():
            if e.get("src") == "curated":
                curated += 1
                by_cur[e["rel"]] = by_cur.get(e["rel"], 0) + 1
            else:
                wordnet += 1
                by_rel[e["rel"]] = by_rel.get(e["rel"], 0) + 1
    total = n * (n - 1)
    return {
        "off_diagonal": total,
        "nonzero": wordnet + curated,
        "density_pct": round(100 * (wordnet + curated) / max(1, total), 3),
        "wordnet_nonzero": wordnet,
        "curated_nonzero": curated,
        "by_relation": by_rel,
        "by_relation_curated": by_cur,
        "recounted_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }


# ------------------------------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser(prog="tk2_curate", description=__doc__.split("\n")[0])
    ap.add_argument("--base", default=CFG.BASE2_NAME)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("propose", help="mine definitions for analytic edges — proposals only")
    p.add_argument("--pairs", help="override the target list: `a.p:b.q,c.r:d.s`")
    p.add_argument("--word", help="mine ONE key against every other dimension, both directions")
    p.add_argument("--senses", choices=["primary", "all"],
                   help="which senses speak (default: whatever the base was built with)")
    p.add_argument("--dry-run", action="store_true", help="print the table, store nothing")
    p.set_defaults(fn=cmd_propose)

    p = sub.add_parser("simulate", help="apply the pending proposals to an IN-MEMORY R and re-score the bar")
    p.add_argument("ids", nargs="*", help="proposal ids; default = every pending one")
    p.set_defaults(fn=cmd_simulate)

    p = sub.add_parser("approve", help="THE CAPTAIN'S HAND ONLY — writes curated cells into R")
    p.add_argument("ids", nargs="*")
    p.add_argument("--i-am-the-captain", action="store_true",
                   help="assert that a human read the evidence and judged it analytic")
    p.add_argument("--authorized", default="",
                   help="who authorized it and when — recorded on the proposal and in the manifest, "
                        "so a curated cell can always be traced back to the hand that allowed it")
    p.set_defaults(fn=cmd_approve)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
