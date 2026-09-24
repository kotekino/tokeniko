"""THE DEP-ORDER BENCH — where a UD relation leaves a closed-class form more than one job, WHO decides?

    PYTHONPATH=. ../.venv/bin/python tools/dep_order_bench.py [--db tokeniko_tk2] [--json out.json]
                                                              [--no-live]

**WHAT IT ASKED FIRST, AND WHAT WAS RULED** (the frame/knowledge audit, 2026-09-22,
`docs/parser-compiler/202609220930_the-frame-knowledge-audit.md`). `ClosedClasses.select` used a
code map, `UD_DEP_TO_ROLE`, twice: as a FILTER — which roles a relation admits — and as a TIE-BREAK,
«best-first». This bench's first version refused every tie the order decided, and reversed every
tuple: **neither moved a single verdict** on the drill, the UD gate or the fixpoint, and the one
wrong live pick (t-ng-4's «No, …») was not the tuple's at all — an emptied filter fell back and the
migration's first row won. The Captain, 2026-09-24: the admissible sets MOVE to the UD readings
(`db/0034`), the ranking is DELETED, and **a tie nobody settles abstains**.

**WHAT IT ASKS NOW.** With no ranking left, every multi-reading token is settled by one of three
witnesses or by nobody:

    the relation · the tag    `candidates` leaves ONE reading — `select` answers
    the clause                the survivors are all wh-readings and the clause says which
                              (`_by_clause`), or a `mark` sits on a complement (`_by_complement`)
    nobody                    the token ABSTAINS — `read` returns None and the compiler unplaces it

and the bench measures each road: STATIC over every ambiguous form × relation × tag, LIVE over the
three corpora with the reader wrapped IN THIS PROCESS ONLY, each live abstention FORCED to each
candidate and scored against the Captain's hand-compiled answers (would ANY pick have beaten the
silence?), and four readings-level counterfactuals — the retired fallback restored (a tie takes the
table's first row), the clause confined to the candidates, every admissible set dropped, and each
relation's set dropped alone, which is what says whether a row of `db/0034` earns its keep.

**NOTHING HERE WRITES.** The closed classes and the readings are read, never touched; every patch
lives in this process and dies with it.
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tk2.language.closed import (  # noqa: E402
    CONTENT_POS, UD_POS_TO_WORD_CLASS, ClosedClasses, standing_closed_classes,
)
from tk2.language.ud_readings import UdReadings  # noqa: E402

_ORIGINAL = {name: getattr(ClosedClasses, name)
             for name in ("read", "_settled", "_by_clause", "_by_complement")}

STATE = {
    "mode": "baseline",   # baseline · first · confined · force
    "forced": {},         # key -> role, for `force`
    "context": {},        # corpus · case · pass — stamped on every log entry
    "log": [],
}

#: The tree contexts `read()` distinguishes — (in_root_clause, head_dep); `notree` is a caller
#: holding no skeleton at all.
TREE_CONTEXTS = {
    "root": (True, "root"),
    "relcl": (False, "acl:relcl"),
    "complement": (False, "ccomp"),
    "adverbial": (False, "advcl"),
    "notree": (None, None),
}


def readings_of(table: ClosedClasses) -> list[str]:
    """Every relation the table's readings answer `admits_roles` for — the rows `db/0034` wrote."""
    return sorted(row["label"] for row in table.readings._rows            # noqa: SLF001
                  if (row.get("reads") or {}).get("admits_roles") is not None)


def reading_count(table, survivors) -> int:
    return len({table._reading(r) for r in survivors})                    # noqa: SLF001


def road(table, form, upos, dep) -> str:
    """How the relation and the tag left this form: the static question, before any clause."""
    rows = table.jobs(form)
    if upos and upos.upper() in CONTENT_POS:
        return "content word"
    survivors = table.candidates(form, upos, dep)
    n = reading_count(table, survivors)
    if n == 1:
        return "settled" if len({table._reading(r) for r in rows}) > 1 else "one reading"  # noqa: SLF001
    admitted = table.readings.admits_roles(dep) if dep else None
    dep_emptied = admitted is not None and not any(r["role"] in admitted for r in rows)
    classes = UD_POS_TO_WORD_CLASS.get((upos or "").upper(), ())
    pos_emptied = bool(upos) and not any(r["word_class"] in classes for r in survivors)
    if dep_emptied:
        return "TIE — the relation's set emptied"
    if admitted is None:
        return "TIE — the relation admits anything" + (" · tag emptied" if pos_emptied else "")
    return "TIE — both filters kept several" + (" · tag emptied" if pos_emptied else "")


# -- the patched reader -----------------------------------------------------------------------------

def _patched_read(self, tokens, at=0, upos=None, dep=None, head_dep=None, in_root_clause=None):
    form = self.match(tokens, at)
    survivors = self.candidates(form, upos, dep) if form else ()
    several = reading_count(self, survivors) > 1
    trace = {"survivors": survivors}
    STATE["trace"] = trace
    try:
        match = _ORIGINAL["read"](self, tokens, at, upos, dep, head_dep, in_root_clause)
    finally:
        STATE["trace"] = None
    # a token the clause re-read is logged even when the relation had settled it: that is where the
    # clause reaches PAST the admissible set, which the `confined` counterfactual measures
    if form and (several or trace.get("clause_outside")):
        if trace.get("complement"):
            by = "the complement clause"
        elif trace.get("clause"):
            by = "the clause"
        elif match is None:
            by = "NOBODY — abstained"
        else:
            by = "one reading"
        STATE["log"].append({
            **STATE["context"], "form": form, "dep": dep, "upos": upos, "head_dep": head_dep,
            "in_root": in_root_clause, "by": by, "several": several,
            "outside": bool(trace.get("clause_outside")),
            "candidates": sorted({r["role"] for r in survivors}),
            "final": match.role if match is not None else None,
            "key": (tuple(tokens), at, upos, dep),
        })
    return match


def _patched_settled(self, survivors):
    mode = STATE["mode"]
    if mode == "force":
        key = STATE.get("key")
        role = STATE["forced"].get(key)
        if role is not None:
            return next((r for r in survivors if r["role"] == role), None)
    if mode == "first" and survivors:
        return survivors[0]           # the retired fallback, with no ranking: the table's row order
    return _ORIGINAL["_settled"](self, survivors)


def _patched_by_clause(self, form, survivors, head_dep, in_root_clause):
    row = _ORIGINAL["_by_clause"](self, form, survivors, head_dep, in_root_clause)
    trace = STATE.get("trace")
    if row is not None and trace is not None:
        trace["clause"] = True
        if row not in survivors:
            trace["clause_outside"] = True
    if row is not None and row not in survivors and STATE["mode"] == "confined":
        return None
    return row


def _patched_by_complement(self, form, dep, head_dep):
    row = _ORIGINAL["_by_complement"](self, form, dep, head_dep)
    trace = STATE.get("trace")
    if row is not None and trace is not None:
        trace["complement"] = True
        if row not in trace["survivors"]:
            trace["clause_outside"] = True
            if STATE["mode"] == "confined":
                return None
    return row


def _keyed_read(self, tokens, at=0, upos=None, dep=None, head_dep=None, in_root_clause=None):
    STATE["key"] = (tuple(tokens), at, upos, dep)
    return _patched_read(self, tokens, at, upos, dep, head_dep, in_root_clause)


@contextmanager
def patched(mode="baseline", forced=None):
    ClosedClasses.read = _keyed_read
    ClosedClasses._settled = _patched_settled                   # noqa: SLF001
    ClosedClasses._by_clause = _patched_by_clause               # noqa: SLF001
    ClosedClasses._by_complement = _patched_by_complement       # noqa: SLF001
    STATE["mode"], STATE["forced"] = mode, forced or {}
    try:
        yield
    finally:
        for name, fn in _ORIGINAL.items():
            setattr(ClosedClasses, name, fn)
        STATE["mode"], STATE["forced"] = "baseline", {}


def without(table: ClosedClasses, labels) -> ClosedClasses:
    """The same closed classes, read against readings whose `admits_roles` is gone for `labels`
    (every relation, if `labels` is None) — the counterfactual `db/0034` is measured against."""
    rows = []
    for row in table.readings._rows:                            # noqa: SLF001
        new = dict(row)
        reads = dict(new.get("reads") or {})
        if labels is None or new["label"] in labels:
            reads.pop("admits_roles", None)
        new["reads"] = reads
        rows.append(new)
    readings = UdReadings(rows, f"{table.readings.source} minus admits_roles of "
                                f"{'every relation' if labels is None else ','.join(labels)}")
    return ClosedClasses(table._rows, table.source, readings=readings)   # noqa: SLF001


# -- STATIC -----------------------------------------------------------------------------------------

def static(table) -> list[dict]:
    """Every (ambiguous form, relation, tag) — the relations the readings name plus two they do not
    (`discourse`, which admits anything, and None) — and the road each one takes, then what the
    clause makes of every TIE in each tree context. A subtype with no row (`nsubj:pass`) behaves
    exactly like its bare label and adds no case; a tag outside the POS map (`VERB`, `NUM`) empties
    that filter exactly as `INTJ` does, which is why `INTJ` stands for all of them."""
    out = []
    deps = (*readings_of(table), "discourse", None)
    uposes = (*UD_POS_TO_WORD_CLASS, "INTJ", None)
    for form in table.ambiguous_forms():
        for dep in deps:
            for upos in uposes:
                way = road(table, form, upos, dep)
                entry = {"form": form, "dep": dep, "upos": upos, "road": way,
                         "candidates": sorted({r["role"] for r in table.candidates(form, upos, dep)})}
                if way.startswith("TIE"):
                    entry["by_context"] = {
                        name: (m.role if (m := table.read(form.split(), 0, upos, dep,
                                                          head_dep=hd, in_root_clause=ir))
                               else None)
                        for name, (ir, hd) in TREE_CONTEXTS.items()}
                out.append(entry)
    return out


# -- LIVE: the three corpora ------------------------------------------------------------------------

class Cached:
    """stanza, memoised by text — a Skeleton is frozen, so handing the same one out twice is safe,
    and every counterfactual re-reads the same eighty-seven sentences."""

    def __init__(self):
        from tk2.language.skeleton import StanzaSkeletons

        self.inner, self.memo = StanzaSkeletons(), {}

    def __call__(self, text):
        if text not in self.memo:
            self.memo[text] = self.inner(text)
        return self.memo[text]


def drill_case(case, compiler, provider):
    from tk2.language.utterance import compile_utterance
    from tools.drill_gate import DRILL_CONTEXT, compare

    STATE["context"] = {"corpus": "drill", "case": case.id, "pass": "in"}
    skeletons = provider(case.sentence)          # the gate reads the sentence raw, and so does this
    if not skeletons:
        return {"verdict": "missing", "conflicts": [], "score": 0}
    produced = compile_utterance(compiler, skeletons, DRILL_CONTEXT)
    r = compare(produced.zip, case.zip, case.id, case.sentence)
    return {"verdict": r.verdict, "conflicts": list(r.conflicts), "score": r.agreed + r.said,
            "paired": r.paired + r.prefix_paired + r.joins_paired}


def drill(compiler, provider):
    from tests.fixtures.drill import CASES

    return {case.id: drill_case(case, compiler, provider) for case in CASES}


def ud(table, compiler):
    from tests.fixtures.ud import CASES
    from tools.ud_gate import read

    out = {}
    for n, case in enumerate(CASES):
        STATE["context"] = {"corpus": "ud", "case": f"ud-{n:02d}", "pass": "in", "at": case.at}
        verdict, produced, _ = read(case, table, compiler)
        out[f"ud-{n:02d}"] = {"verdict": verdict, "produced": produced, "expect": case.expect,
                              "text": case.text, "relation": case.relation}
    return out


def fixpoint(compiler, decompiler, provider):
    """`tools/roundtrip.py --fixpoint`, the same loop, returning each case's state."""
    from tests.fixtures.drill import CASES
    from tk2.language.utterance import compile_utterance
    from tools.drill_gate import DRILL_CONTEXT
    from tools.roundtrip import canonical

    out = {}
    for case in CASES:
        sentence = re.sub(r"\s*\[[^\]]*\]\s*$", "", case.sentence).strip()
        STATE["context"] = {"corpus": "fixpoint", "case": case.id, "pass": "in"}
        skeletons = provider(sentence)
        if not skeletons:
            out[case.id] = {"state": "SILENT", "whole": False, "text": ""}
            continue
        first = compile_utterance(compiler, skeletons, DRILL_CONTEXT).zip
        whole = not first.unplaced
        text = decompiler.decompile(first).text
        if not text.strip():
            out[case.id] = {"state": "SILENT", "whole": whole, "text": ""}
            continue
        STATE["context"] = {"corpus": "fixpoint", "case": case.id, "pass": "back"}
        again = provider(text)
        second = compile_utterance(compiler, again, DRILL_CONTEXT).zip if again else None
        same = second is not None and canonical(second) == canonical(first)
        out[case.id] = {"state": "FIXED" if same else "MOVED", "whole": whole, "text": text}
    return out


def tally_drill(res):
    c = Counter(v["verdict"] for v in res.values())
    return f"{c['agreed']} agreed · {c['DISAGREED']} DISAGREED · {c['missing']} no common ground"


def tally_fix(res):
    c = Counter(v["state"] for v in res.values())
    whole = [v for v in res.values() if v["whole"]]
    w = Counter(v["state"] for v in whole)
    return (f"{c['FIXED']} of {len(res)} FIXED · {c['MOVED']} MOVED · {c['SILENT']} SILENT · "
            f"read whole {len(whole)} ({w['FIXED']} FIXED · {w['MOVED']} MOVED · "
            f"{w['SILENT']} SILENT)")


def tally_ud(res):
    c = Counter(v["verdict"] for v in res.values())
    return f"ANSWERED {c['answered']} · WRONG {c['WRONG']} · ABSTAINED {c['abstained']}"


def deltas(base, other, field):
    return [(k, base[k][field], other[k][field]) for k in base if base[k][field] != other[k][field]]


def run_all(table, provider, mode="baseline", forced=None):
    from tk2.language.compile import Compiler
    from tk2.language.decompile import Decompiler
    from tools.drill_gate import DRILL_CONTEXT

    STATE["log"] = []
    compiler = Compiler(table)
    decompiler = Decompiler(table, context=DRILL_CONTEXT)
    with patched(mode, forced):
        res = {"drill": drill(compiler, provider), "ud": ud(table, compiler),
               "fixpoint": fixpoint(compiler, decompiler, provider)}
    return res, list(STATE["log"])


def judge(table, provider, log):
    """Each live ABSTENTION forced to each candidate, one at a time, and scored by the drill (or the
    UD gate) on that one case, beside the abstention itself. SILENCE HOLDS if no candidate scores
    better than abstaining; a candidate BEATS it if one scores strictly better; BLIND if all alike.

    Better = fewer conflicts, then more agreed slots. Only the drill's and the UD gate's own cases
    are judged: the fixpoint is the station against itself and has no truth to prefer."""
    from tk2.language.compile import Compiler
    from tests.fixtures.drill import CASES as DRILL
    from tests.fixtures.ud import CASES as UDC
    from tools.ud_gate import read

    drill_by_id = {c.id: c for c in DRILL}
    compiler = Compiler(table)
    judged = []
    seen = set()
    for entry in log:
        if entry["by"] != "NOBODY — abstained" or entry["corpus"] not in ("drill", "ud"):
            continue
        ident = (entry["corpus"], entry["case"], entry["key"])
        if ident in seen:
            continue
        seen.add(ident)
        scores = {}
        for role in (None, *entry["candidates"]):
            with patched("force", {entry["key"]: role} if role else {}):
                STATE["log"] = []
                if entry["corpus"] == "drill":
                    r = drill_case(drill_by_id[entry["case"]], compiler, provider)
                    scores[role or "(abstain)"] = (len(r["conflicts"]), -r["score"], r["verdict"],
                                                   r["conflicts"])
                else:
                    case = UDC[int(entry["case"].split("-")[1])]
                    verdict, produced, _ = read(case, table, compiler)
                    scores[role or "(abstain)"] = ({"WRONG": 1}.get(verdict, 0),
                                                   -(verdict == "answered"), verdict, produced)
        silence = scores["(abstain)"]
        better = [role for role, s in scores.items() if s[:2] < silence[:2]]
        if len({s[:2] for s in scores.values()}) == 1:
            outcome = "BLIND"
        elif not better:
            outcome = "SILENCE HOLDS"
        else:
            outcome = "BEATEN by " + "/".join(better)
        judged.append({**{k: v for k, v in entry.items() if k != "key"}, "outcome": outcome,
                       "scores": {k: list(v) for k, v in scores.items()}})
    return judged


def _print_counterfactual(label, base, cf):
    print("\n" + "=" * 100)
    print(f"COUNTERFACTUAL — {label}")
    print("=" * 100)
    print(f"  drill     {tally_drill(cf['drill'])}")
    print(f"  fixpoint  {tally_fix(cf['fixpoint'])}")
    print(f"  UD gate   {tally_ud(cf['ud'])}")
    moved = 0
    for name, field in (("drill", "verdict"), ("fixpoint", "state"), ("ud", "verdict")):
        for k, was, now in deltas(base[name], cf[name], field):
            print(f"    {name:<8} {k:<8} {was} -> {now}")
            moved += 1
    for k in base["drill"]:
        b, c = base["drill"][k], cf["drill"][k]
        if b["conflicts"] != c["conflicts"] or b["score"] != c["score"]:
            print(f"    drill    {k:<8} score {b['score']} -> {c['score']} · conflicts "
                  f"{len(b['conflicts'])} -> {len(c['conflicts'])}"
                  + (f"  new: {[x for x in c['conflicts'] if x not in b['conflicts']][:2]}"
                     if c["conflicts"] != b["conflicts"] else ""))
            moved += 1
    text_moves = [k for k in base["fixpoint"]
                  if base["fixpoint"][k]["text"] != cf["fixpoint"][k]["text"]]
    for k in text_moves:
        print(f"    fixpoint {k:<8} «{base['fixpoint'][k]['text']}» -> «{cf['fixpoint'][k]['text']}»")
    return moved + len(text_moves)


# -- the report -------------------------------------------------------------------------------------

def run(argv=None) -> int:
    parser = argparse.ArgumentParser(description="who settles a closed-class form's job?")
    parser.add_argument("--db", default=None, help="read the closed classes from this database")
    parser.add_argument("--json", default=None, help="write the whole measurement here")
    parser.add_argument("--no-live", action="store_true", help="the static half only")
    args = parser.parse_args(argv)

    table = standing_closed_classes(args.db)
    relations = readings_of(table)
    print("=" * 100)
    print("THE DEP-ORDER BENCH — where a relation leaves a form several jobs, who decides?")
    print("=" * 100)
    print(f"  closed classes    {len(table)} rows, v{table.version} — {table.source}")
    print(f"  ambiguous forms   {len(table.ambiguous_forms())}")
    print(f"  admissible sets   {len(relations)} relations: {' · '.join(relations)}\n")
    if not relations:
        print("  **NO RELATION ADMITS ANYTHING** — these readings predate `db/0034`; every number "
              "below measures a station with no dependency filter at all.\n")

    # ---- STATIC
    exposure = static(table)
    roads = Counter(e["road"] for e in exposure)
    print("STATIC — every ambiguous form × relation (+discourse, +none) × UPOS (+INTJ, +none)")
    for way, n in roads.most_common():
        forms = len({e["form"] for e in exposure if e["road"] == way})
        print(f"  {way:<52} {n:>5} combinations · {forms} forms")
    ties = [e for e in exposure if e["road"].startswith("TIE")]
    settled_by = Counter()
    for e in ties:
        for name, role in e["by_context"].items():
            settled_by[(name, "settled" if role else "abstains")] += 1
    print("\n  the TIES, by tree context — what the clause makes of them:")
    for name in TREE_CONTEXTS:
        print(f"    {name:<12} settled {settled_by[(name, 'settled')]:>5} · "
              f"abstains {settled_by[(name, 'abstains')]:>5}")
    grouped = defaultdict(list)
    for e in ties:
        # only where the relation's set held — an emptied set or an unconstrained relation is the
        # same tie for every relation, counted above and not worth a line each
        if not e["road"].startswith("TIE — both filters"):
            continue
        grouped[(e["form"], e["dep"], tuple(e["candidates"]),
                 tuple(sorted(k for k, v in e["by_context"].items() if v)))].append(e["upos"] or "-")
    print(f"\n  the ties a relation's set LEAVES, its filter applied: {len(grouped)} distinct")
    print(f"  {'form':<10} {'dep':<12} {'candidates':<44} {'the clause settles in':<28} upos")
    for (form, dep, cands, where), uposes in sorted(grouped.items()):
        print(f"  {form:<10} {dep:<12} {' · '.join(cands):<44} {','.join(where) or '—':<28} "
              f"{','.join(uposes)}")

    report = {"source": table.source, "static": exposure}
    if args.no_live:
        return _write(args, report)

    # ---- LIVE
    provider = Cached()
    base, log = run_all(table, provider, "baseline")
    print("\n" + "=" * 100)
    print("LIVE — the drill · the UD gate · the fixpoint, the reader wrapped in this process only")
    print("=" * 100)
    print(f"  drill     {tally_drill(base['drill'])}")
    print(f"  fixpoint  {tally_fix(base['fixpoint'])}")
    print(f"  UD gate   {tally_ud(base['ud'])}")
    by = Counter(e["by"] for e in log if e["several"])
    print(f"\n  calls the relation and the tag left SEVERAL readings: {sum(by.values())}")
    for who, n in by.most_common():
        print(f"    settled by {who:<28} {n:>4}")
    outside = [e for e in log if e["outside"]]
    print(f"  calls where the clause reached PAST the relation's admissible set: {len(outside)}")
    per = Counter((e["by"], e["form"], str(e["dep"]), str(e["upos"]), str(e["head_dep"]),
                   " · ".join(e["candidates"]), str(e["final"]), e["outside"]) for e in log)
    print(f"\n  {'by':<24} {'form':<9} {'dep':<11} {'upos':<6} {'head_dep':<10} {'final':<16} "
          f"{'n':>3}  candidates")
    for (who, form, dep, upos, hd, cands, final, out), n in sorted(per.items()):
        print(f"  {who[:24]:<24} {form:<9} {dep:<11} {upos:<6} {hd:<10} {final:<16} {n:>3}  "
              f"{cands}{'  [past the set]' if out else ''}")
    print("\n  every abstention, by case:")
    for e in log:
        if e["by"].startswith("NOBODY"):
            toks = " ".join(e["key"][0])
            print(f"    {e['corpus']:<8} {e['case']:<8} {e['pass']:<4} {e['form']!r:<8} "
                  f"dep={e['dep']} upos={e['upos']} head_dep={e['head_dep']} "
                  f"candidates={e['candidates']}  « {toks[:60]} »")

    judged = judge(table, provider, log)
    print(f"\n  JUDGED against the hand-compiled answers (drill zips, UD `expect`): {len(judged)}")
    print(f"    {Counter(j['outcome'].split(' by ')[0] for j in judged)}")
    for j in judged:
        print(f"    {j['corpus']:<6} {j['case']:<8} {j['form']!r:<8} dep={str(j['dep']):<10} "
              f"{j['outcome']}")
        for role, s in j["scores"].items():
            print(f"        {role:<18} conflicts={s[0]} agreed={-s[1]} verdict={s[2]}"
                  + (f"  {s[3][:2]}" if j["corpus"] == "drill" and s[3] else
                     (f"  produced={s[3]}" if j["corpus"] == "ud" else "")))

    report.update({"live_log": [{k: v for k, v in e.items() if k != "key"} for e in log],
                   "judged": judged, "baseline": base})

    # ---- COUNTERFACTUALS
    for mode, label in (("first", "the retired fallback RESTORED — a tie takes the table's first "
                                  "row (no ranking)"),
                        ("confined", "the clause CONFINED to the candidates — it may not reach "
                                     "past the relation's admissible set")):
        cf, _ = run_all(table, provider, mode)
        _print_counterfactual(label, base, cf)
        report[f"cf_{mode}"] = cf
    cf, _ = run_all(without(table, None), provider)
    _print_counterfactual("EVERY admissible set dropped — no relation constrains the role", base, cf)
    report["cf_no_admits"] = cf

    print("\n" + "=" * 100)
    print("EACH RELATION'S SET DROPPED ALONE — does its row in `db/0034` earn its keep here?")
    print("=" * 100)
    earns = {}
    for label in relations:
        cf, _ = run_all(without(table, [label]), provider)
        moved = [f"{name}:{k} {was}->{now}"
                 for name, field in (("drill", "verdict"), ("fixpoint", "state"), ("ud", "verdict"))
                 for k, was, now in deltas(base[name], cf[name], field)]
        moved += [f"drill:{k} score" for k in base["drill"]
                  if base["drill"][k]["score"] != cf["drill"][k]["score"]
                  or base["drill"][k]["conflicts"] != cf["drill"][k]["conflicts"]]
        moved += [f"text:{k}" for k in base["fixpoint"]
                  if base["fixpoint"][k]["text"] != cf["fixpoint"][k]["text"]]
        earns[label] = moved
        print(f"  {label:<14} {len(moved):>3} moves  {' · '.join(moved[:6])}"
              + (" …" if len(moved) > 6 else ""))
    report["cf_each_relation"] = earns
    return _write(args, report)


def _write(args, report) -> int:
    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=2, default=str, ensure_ascii=False))
        print(f"\n  written to {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
