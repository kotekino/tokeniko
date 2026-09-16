"""THE UD GATE — every relation the station meets, scored against UD's own examples.

    PYTHONPATH=. ../.venv/bin/python tools/ud_gate.py [--db tokeniko_tk2] [--live] [--json out.json]

**WHY THIS IS THE STATION'S GATE AND THE DRILL IS NOT** (the Captain, 2026-09-15). E2's drill proved
the FORMAT can hold the world — 78 sentences, hand-compiled. It says nothing about whether a
skeleton was read correctly, because no parser was involved in it. This gate is the other half: UD
publishes 37 relations and 17 POS tags with examples, both ends of the mapping are CLOSED, and so
the 37 → 18-roles table can be COMPLETE rather than merely large.

**IT REPORTS THREE THINGS, AND THE THIRD IS THE POINT:**

- **ANSWERED** — the station produced what the corpus says it owes.
- **WRONG** — it produced something else. The only failure that counts.
- **ABSTAINED** — it produced nothing, or the corpus has not ruled what it owes (`OPEN`). *«Half
  understood is legal, wrongly understood is the sin»* (req 8), so these are reported apart and
  never averaged into a score that would hide them.

**AND IT REPORTS COVERAGE SEPARATELY**: how many of UD's 37 the corpus even reaches. A gate that
scored 100% on the sixteen relations someone happened to transcribe would be a gate measuring its
own corpus, so the uncovered relations are printed by name every run.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tests.fixtures.ud import CASES, OPEN, by_relation, covered  # noqa: E402
from tk2.language import standing_closed_classes  # noqa: E402
from tk2.language.markers import MarkerSelector  # noqa: E402
from tk2.language.skeleton import UD_DEPS  # noqa: E402

ANSWERED, WRONG, ABSTAINED = "answered", "WRONG", "abstained"


SELECTOR = MarkerSelector()


def read(case, table) -> tuple[str, str, str]:
    """What the station makes of the marked token. Returns (verdict, produced, why).

    The station here is what EXISTS: the closed-class table read through a UD skeleton. Roles that
    come from a relation rather than from a marker (agent, patient, recipient) are not its job yet —
    that is the compile core, E3 task 2 — so it abstains on them, honestly and by name.
    """
    skeleton = case.skeleton
    word = skeleton[case.at]
    head = skeleton[word.head]
    match = table.read(skeleton.tokens, case.at, word.upos, word.dep,
                       head_dep=None if head.index == word.index else head.dep)

    if match is None:
        return ABSTAINED, "", "no closed-class row matched this token"

    settled_why = ""
    kind = match.kind
    if kind == "box":
        if match.settled_role:
            # UD's own subtype named the role — `obl:agent`, `obl:tmod`. No ambiguity survives that.
            produced = match.settled_role
        elif len(match.roles) > 1:
            # ONE OF THE THIRTEEN. `db/0012` says what settles it, and `tk2.language.markers` runs
            # the rules: UD puts `case` on the marker and the phrase's own head one edge further
            # out, so the nominal is this token's head and the verb is the nominal's.
            nominal = skeleton[word.head]
            governor = skeleton[nominal.head]
            settled = SELECTOR.settle(match.compiled, nominal.lemma, nominal.upos,
                                      governor.lemma, governor.upos)
            if settled is None:
                return (ABSTAINED, "|".join(match.roles),
                        f"{len(match.roles)} candidates and nothing selects between them")
            produced = settled.role
            settled_why = settled.why
        else:
            produced = match.roles[0] if match.roles else ""
    elif kind == "join":
        produced = match.compiled.get("operator", "")
    elif kind == "field":
        produced = match.compiled.get("field", "field")
    elif kind in ("prefix", "structure", "entity", "determination", "restriction", "theatre",
                  "quantifier", "open", "ambiguous"):
        produced = {"determination": "determination", "quantifier": "prefix"}.get(kind, kind)
        # A CONDITIONAL ROW: copular `be` is structure, the same form under `aux` moves the theatre.
        # The row states both and names the dependency that chooses — «when: cop».
        when = match.compiled.get("when")
        if when and word.dep != when:
            produced = match.compiled.get("otherwise", produced)
    else:
        produced = kind

    if case.expect == OPEN:
        return ABSTAINED, produced, "the corpus has not ruled what this owes"
    if not produced:
        return ABSTAINED, "", f"matched {match.form!r} but it compiles to nothing nameable"
    if produced == case.expect:
        return ANSWERED, produced, settled_why
    return WRONG, produced, f"expected {case.expect}"


def run(argv=None) -> int:
    parser = argparse.ArgumentParser(description="score the station against UD's own examples")
    parser.add_argument("--db", default=None,
                        help="read the closed classes from this database (default: the newest "
                             "migration, which needs no body)")
    parser.add_argument("--live", action="store_true",
                        help="ALSO parse each sentence with stanza and compare its skeleton with "
                             "the one UD published — the «take stanza as close enough and check» "
                             "measurement, which needs the models")
    parser.add_argument("--json", default=None, help="write the whole measurement here")
    args = parser.parse_args(argv)

    table = standing_closed_classes(args.db)
    print("=" * 96)
    print("THE UD GATE — the station against Universal Dependencies' own examples")
    print("=" * 96)
    print(f"  closed classes    {len(table)} rows, v{table.version} — {table.source}")
    print(f"  corpus            {len(CASES)} cases over {len(covered())} of UD's 37 relations")
    print(f"  transcribed with UD's own annotation: "
          f"{sum(1 for c in CASES if c.annotated)} of {len(CASES)}")
    print()

    results, tally = [], {ANSWERED: 0, WRONG: 0, ABSTAINED: 0}
    print(f"  {'relation':<14} {'expected':<14} {'produced':<22} {'':<10} sentence")
    print(f"  {'-' * 14} {'-' * 14} {'-' * 22} {'-' * 10} {'-' * 30}")
    for case in sorted(CASES, key=lambda c: (c.relation, c.text)):
        verdict, produced, why = read(case, table)
        tally[verdict] += 1
        results.append({"relation": case.relation, "text": case.text, "expect": case.expect,
                        "produced": produced, "verdict": verdict, "why": why,
                        "annotated": case.annotated})
        mark = {ANSWERED: "ok", WRONG: "WRONG", ABSTAINED: "—"}[verdict]
        print(f"  {case.relation:<14} {case.expect:<14} {produced or '(nothing)':<22} "
              f"{mark:<10} « {case.text} »")
        if why and verdict != ANSWERED:
            print(f"  {'':<14} {'':<14} {'':<22} {'':<10}   {why}")

    total = len(CASES)
    print()
    print(f"  ANSWERED {tally[ANSWERED]} of {total} · WRONG {tally[WRONG]} · "
          f"ABSTAINED {tally[ABSTAINED]}")
    print("  an abstention is not a miss — «half understood is legal, wrongly understood is the "
          "sin» (req 8)")

    missing = sorted(set(UD_DEPS) - covered())
    print()
    print(f"  COVERAGE — {len(covered())} of 37 relations have at least one case.")
    print(f"  NOT YET REACHED ({len(missing)}): {' '.join(missing)}")

    live = None
    if args.live:
        live = check_against_stanza()

    if args.json:
        Path(args.json).write_text(json.dumps(
            {"source": table.source, "version": table.version, "tally": tally,
             "coverage": sorted(covered()), "missing": missing, "cases": results, "live": live},
            indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\n  wrote {args.json}")
    return 0


def check_against_stanza() -> dict:
    """«Take stanza as close enough and CHECK against UD2 and its examples» — the checking.

    For every case UD published a full annotation for, parse the same sentence and compare, token by
    token. A disagreement is NOT automatically stanza's error: UD's pages sometimes elide, and a
    tokenizer may legitimately split differently. It is reported, not scored.
    """
    from tk2.language import StanzaSkeletons

    provider = StanzaSkeletons()
    print()
    print("=" * 96)
    print("STANZA AGAINST UD's PUBLISHED ANNOTATION — reported, not scored")
    print("=" * 96)
    agree = differ = unusable = 0
    rows = []
    for case in CASES:
        if not case.annotated:
            continue
        published = case.skeleton
        parsed = provider(case.text)
        if len(parsed) != 1 or parsed[0].tokens != published.tokens:
            unusable += 1
            got = " ".join(t for s in parsed for t in s.tokens)
            print(f"  TOKENS DIFFER  « {case.text} »")
            print(f"                 stanza: {got}")
            rows.append({"text": case.text, "issue": "tokenization", "stanza": got})
            continue
        mismatch = [(p.text, p.dep, u.dep) for p, u in zip(parsed[0], published) if p.dep != u.dep]
        if mismatch:
            differ += 1
            print(f"  DEP DIFFERS    « {case.text} »")
            for token, got, expected in mismatch:
                print(f"                 {token:<12} stanza={got:<14} UD published={expected}")
            rows.append({"text": case.text, "issue": "dep", "diffs": mismatch})
        else:
            agree += 1
    print()
    print(f"  agrees with UD's published parse: {agree} · differs: {differ} · "
          f"not comparable (tokenization): {unusable}")
    return {"agree": agree, "differ": differ, "unusable": unusable, "rows": rows}


def main(argv=None) -> int:
    return run(argv)


if __name__ == "__main__":
    raise SystemExit(main())
