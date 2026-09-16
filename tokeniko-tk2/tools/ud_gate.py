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

from tests.fixtures.ud import (  # noqa: E402
    CASES, NOT_IN_ENGLISH, OPEN, UD_ABSTAINS, by_relation, covered,
)
from tk2.language import standing_closed_classes  # noqa: E402
from tk2.language.compile import Compiler  # noqa: E402
from tk2.language.skeleton import UD_DEPS  # noqa: E402

ANSWERED, WRONG, ABSTAINED = "answered", "WRONG", "abstained"


def read(case, table, compiler) -> tuple[str, str, str]:
    """What the station makes of the marked token. Returns (verdict, produced, why).

    **IT SCORES THE ZIP NOW, NOT THE TABLE.** Until 2026-09-16 this asked the closed-class table what
    a token was, because the table was all that existed — and its own docstring said so: *«roles that
    come from a relation rather than from a marker are not its job yet»*. That was a gate measuring
    half a station, and it could never reach the twenty-one relations that are COMPILER questions:
    what does `amod` become, what does `conj` become, where did `nummod` go. «The token is covered»
    does not distinguish a role from a prefix from a row.

    So the sentence is COMPILED and the marked token is looked up in `Compiled.placement` — the
    compiler's own record of where each word went. A relation the station handles badly now shows up
    as a wrong placement or as an unplaced word, which is what a gate is for.

    **The `expect` vocabulary is unchanged**, and deliberately: a case still marks the MARKER and
    still expects a ROLE, because «what did this `case` edge produce» is the natural question and
    re-pointing 25 transcribed cases at their nominals would have rewritten the corpus to suit the
    instrument.
    """
    skeleton = case.skeleton
    word = skeleton[case.at]
    out = compiler.compile(skeleton)
    where = out.placement.get(case.at, "")

    if not where:
        if word.upos in ("PUNCT", "SYM"):
            # Punctuation compiles to nothing and that IS the answer — it is structure, dropped on
            # purpose, and the zip is not missing anything.
            produced, why = "structure", "punctuation compiles to nothing"
        else:
            return (ABSTAINED, "", f"{word.text!r} reached no part of the zip")
    else:
        produced, why = _produced(where, case, skeleton, out, table)
        if produced is None:
            return ABSTAINED, "", why

    if case.expect == OPEN:
        return ABSTAINED, produced, "the corpus has not ruled what this owes"
    if produced == case.expect:
        return ANSWERED, produced, why
    return WRONG, produced, f"expected {case.expect}" + (f" ({why})" if why else "")


def _produced(where: str, case, skeleton, out, table) -> tuple[str | None, str]:
    """A placement label -> the word the corpus uses for it.

    The two that need the zip rather than the label are the ones where the token is not itself the
    thing it produced: a MARKER names a box it does not fill, and a JOINER names an operator that
    lives on a row of its own.
    """
    kind, _, detail = where.partition(":")

    if kind == "box":
        return detail, "filled by relation"
    if kind == "field":
        return detail, "a field of the record, not a box (req 26)"
    if kind == "predicate":
        return "predicate", f"the predicate of {detail}"
    if kind == "marker":
        form = _form_at(table, skeleton, case.at)
        for row in out.zip.rows:
            for role, box in getattr(row, "boxes", {}).items():
                if box.marker == form:
                    return role.value, f"marks the {role.value} box"
        return None, f"{form!r} marked a phrase that reached no box"
    if kind == "join":
        for row in out.zip.rows:
            operator = getattr(row, "operator", None)
            if operator is not None:
                return operator.value, "the operator it compiled to"
        return None, "joined nothing"
    if kind == "quantifier":
        return "prefix", "a binder in the prefix"
    return kind, ""


def _form_at(table, skeleton, at: int) -> str:
    """The closed-class FORM starting at this token — multi-word forms included, so «out of» is one
    marker and not two."""
    return table.match(skeleton.tokens, at) or skeleton[at].text.lower()


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
    compiler = Compiler(table)
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
        verdict, produced, why = read(case, table, compiler)
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

    # THREE STATES, NOT TWO. «We have not got to it» and «it does not arise in English» are
    # different things, and folding the second into the first makes the coverage number a lie in
    # the flattering direction — while folding it the other way makes the gate look permanently
    # incomplete for a reason nobody can fix.
    missing = sorted(set(UD_DEPS) - covered() - set(NOT_IN_ENGLISH) - set(UD_ABSTAINS))
    print()
    print(f"  COVERAGE — {len(covered())} of 37 relations have at least one case; "
          f"{len(NOT_IN_ENGLISH)} do not arise in English and {len(UD_ABSTAINS)} is UD's own "
          f"abstention.")
    print(f"  NOT IN ENGLISH ({len(NOT_IN_ENGLISH)}): {' '.join(NOT_IN_ENGLISH)}"
          f"   — UD's own pages print no English example")
    print(f"  UD ABSTAINS ({len(UD_ABSTAINS)}): {' '.join(UD_ABSTAINS)}"
          f"   — «we could not decide which relation this is»; the station owes nothing")
    if missing:
        print(f"  NOT YET REACHED ({len(missing)}): {' '.join(missing)}")
    else:
        print("  NOT YET REACHED: none — **every relation UD publishes for English is in the "
              "corpus.**")

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
