"""THE ROUND TRIP — decompile a zip, compile it again, and ask whether it is the same thought.

    PYTHONPATH=. ../.venv/bin/python tools/roundtrip.py [--db tokeniko_tk2] [--all]

**THE TEST COMES WITH THE ANALOGY** (parser-compiler req 9, the Captain 2026-09-19). Decompiled
source is never the original source; it is A source that compiles to the same object. So the question
is never «does this read like the sentence we started from» — it is **does it compile to the zip we
started from**, which is the one property the decompiler owes.

    the drill's own zip  ->  decompile  ->  stanza  ->  compile  ->  a zip  ->  compare
                                                                               ^
                                                             `tools.drill_gate.compare`, unchanged

The comparator is the drill gate's, deliberately. It already scores AGREEMENT rather than equality,
pairs rows by what they are about, abstains on variables and OPENs, and reads the prefix and the
joins since 2026-09-19 — so the instrument that judges the compiler judges the decompiler too, and a
defect cannot hide in the seam between two graders.

**THE CORPUS IS THE DRILL'S 87 HAND-COMPILED ZIPS**, not the station's own output, and that matters:
compiling our own parse back would measure the decompiler against a reading that may itself be
wrong. The drill's zips are what the format says the world looks like.

**WHAT IT REPORTS, in three states and never two**: a zip the decompiler REFUSED to say (it would
have had to lie) is not a failure of the round trip, it is the decompiler declining, and it is
counted apart from the sentences that came back changed.
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tests.fixtures.drill import CASES  # noqa: E402
from tk2.language import standing_closed_classes  # noqa: E402
from tk2.language.compile import Compiler  # noqa: E402
from tk2.language.decompile import Decompiler  # noqa: E402
from tk2.language.utterance import compile_utterance  # noqa: E402
from tools.drill_gate import DISAGREED, DRILL_CONTEXT, compare  # noqa: E402


def fixpoint(argv, args) -> int:
    """**THE STATION AGAINST ITSELF** — sentence -> zip -> sentence -> zip, and the two zips must be
    IDENTICAL, not merely agreed.

    *The Captain, 2026-09-20: «what the decompiler can't do, either is because the compiler doesn't
    encode the missed information in the zip OR the decompiler doesn't extract the information
    encoded in the tkzip … until everything is fixed and the input sentence is 100% equivalent to
    the output one».*

    That instruction needs a different instrument from the one above. The drill's zips are what the
    FORMAT says the world looks like, and they hold things the station cannot yet produce — so
    measuring against them mixes two questions. This asks only the second one: **does the decompiler
    say back everything the compiler wrote down?** Whatever the compiler failed to encode is absent
    from both sides here and cannot hide the decompiler's own gaps; whatever it encoded and the
    decompiler drops shows up immediately, as a zip that is not the zip it came from.

    Equality, not agreement, and deliberately: the gate's comparator is generous by design (it
    abstains on variables, pairs rows by what they are about) and generosity is right when judging a
    parse against a hand-compiled truth. Here both sides come from the same machine, so anything
    less than equality is a loss.
    """
    from tk2.language.skeleton import StanzaSkeletons

    table = standing_closed_classes(args.db)
    compiler, provider = Compiler(table), StanzaSkeletons()
    decompiler = Decompiler(table, context=DRILL_CONTEXT)

    print("=" * 96)
    print("THE FIXPOINT — the station against itself: sentence -> zip -> sentence -> zip")
    print("=" * 96)
    print(f"  closed classes    {len(table)} rows, v{table.version} — {table.source}")
    print(f"  the corpus        {len(CASES)} sentences\n")

    same = changed = silent = 0
    whole_same = whole_changed = 0
    for case in CASES:
        # The drill annotates a few of its sentences — «… [de dicto]» — and the bracket is a note to
        # the reader, not words anybody said. Compiling it makes a second sentence out of nothing.
        sentence = re.sub(r"\s*\[[^\]]*\]\s*$", "", case.sentence).strip()
        skeletons = provider(sentence)
        if not skeletons:
            silent += 1
            continue
        compiled = compile_utterance(compiler, skeletons, DRILL_CONTEXT)
        first = compiled.zip
        # **A SENTENCE THE COMPILER DID NOT FULLY READ CANNOT TEST THE DECOMPILER.** What the zip
        # never held is not something the decompiler dropped, so the two populations are reported
        # apart — the same discipline the UD gate uses for its ratchet and its frontier.
        covered = not first.unplaced
        out = decompiler.decompile(first)
        if not out.text.strip():
            silent += 1
            if args.all:
                print(f"  {case.id:8} SILENT   « {sentence[:60]} »")
                for why in (out.refused + out.unsaid)[:3]:
                    print(f"      ⚑ {why}")
            continue
        again = provider(out.text)
        second = compile_utterance(compiler, again, DRILL_CONTEXT).zip if again else None
        if second is not None and canonical(second) == canonical(first):
            same += 1
            whole_same += 1 if covered else 0
            if args.all:
                print(f"  {case.id:8} FIXED    « {out.text[:60]} »")
            continue
        changed += 1
        whole_changed += 1 if covered else 0
        print(f"  {case.id:8} MOVED  {'' if covered else '*'}  « {out.text[:62]} »")
        print(f"           in   « {sentence[:62]} »")
        for line in _differences(first, second)[:3]:
            print(f"      ⚑ {line}")

    print(f"\n  FIXED           {same} of {len(CASES)} — the zip came back exactly as it went out")
    print(f"  MOVED           {changed} — the decompiler dropped or changed something the zip held")
    print(f"  SILENT          {silent} — the decompiler said nothing at all")
    print(f"\n  OF THE SENTENCES THE COMPILER READ WHOLE — no word left unplaced:")
    print(f"  FIXED           {whole_same} of {whole_same + whole_changed}")
    print(f"  MOVED           {whole_changed} — and these are the decompiler's own, because the "
          f"zip held everything the sentence said")
    print(f"  *               a MOVED line marked `*` is one the COMPILER did not read whole")
    return 1 if changed else 0


#: The operators that are ASSOCIATIVE and COMMUTATIVE, so that `and(and(a,b),c)` and `and(a,and(b,c))`
#: are one thought written two ways. Closed by mathematics (req 41), not by English: `nand` and `nor`
#: are commutative and NOT associative, and the four implications are neither.
FLAT = {"and", "or", "xor", "eq"}


def canonical(zip_) -> dict:
    """A zip with its row NAMES removed and its associative chains flattened — so two zips compare
    as THOUGHTS and not as spellings.

    Three things are normalised, each because the format itself says they carry no meaning:

    - **Row names** are zip-local and arbitrary (req 64): `r0` and `s1.r0` are the same row when two
      sentences merge into one utterance. Each name is replaced by a SIGNATURE built from the row's
      own content, with the names inside it replaced by the signatures of what they point at.
    - **The shape of an `and` chain.** English says «a and b and c» with no brackets, so a
      decompiled conjunction comes back nested however the parser chose. `AND` is associative by
      mathematics, so the two nestings are one thought, and a comparison that called them different
      would be measuring punctuation nobody wrote.
    - **`unplaced`**, which req 21 makes a diagnostic that is recorded and never compared. The
      decompiled sentence cannot contain a word the zip never held, so comparing it would measure
      the compiler's coverage twice and call it a decompiler defect.
    """
    rows = {row["name"]: row for row in zip_.model_dump(exclude_none=True).get("rows", [])}
    absorbed: set[str] = set()
    # **A VARIABLE IS NAMED BY WHAT BINDS IT, NOT BY ITS SPELLING.** The drill writes `X` and the
    # station writes `x0` for the same variable, and the gate has abstained on that since it was
    # built. Here the binder is in the zip, so the name can be replaced by what the binder SAYS —
    # its quantity and what it ranges over — which is stable across parses and still distinguishes
    # «every cat» from «some dog».
    bound = {}
    for row in rows.values():
        if row.get("kind") == "quantifier":
            restriction = row.get("restriction") or {}
            bound[row["binds"]] = (f"<{row.get('quantity')} "
                                   f"{restriction.get('head')} {restriction.get('determination')}>")

    def members(name: str, operator: str, depth: int) -> list[str]:
        """Every leaf of one associative chain — the operands, and the operands of any operand that
        repeats the same operator."""
        row = rows.get(name)
        if depth > len(rows) or row is None or row.get("operator") != operator:
            return [name]
        absorbed.add(name)
        return [leaf for operand in row["operands"] for leaf in members(operand, operator, depth + 1)]

    def sign(name: str, depth: int = 0) -> str:
        row = rows.get(name)
        if row is None or depth > len(rows):
            return f"<{name}>"
        if row.get("kind") == "join" and row["operator"] in FLAT:
            leaves = [leaf for operand in row["operands"]
                      for leaf in members(operand, row["operator"], depth + 1)]
            inside = " ".join(sorted(sign(leaf, depth + 1) for leaf in leaves))
            return f"({row['operator']}{'' if row.get('truth') is None else '!'} {inside})"
        body = {key: _rename(value, sign, rows, depth, bound) for key, value in row.items()
                if key != "name"}
        return json.dumps(body, sort_keys=True, default=str)

    signed = {name: sign(name) for name in rows}
    body = zip_.model_dump(exclude_none=True)
    body.pop("unplaced", None)
    body["rows"] = sorted(text for name, text in signed.items() if name not in absorbed)
    return body


def _rename(value, sign, rows: dict, depth: int, bound: dict):
    """Every row name inside a value replaced by that row's signature, and every VARIABLE name by
    what its binder says about it. Both are numbered independently by each parse."""
    if isinstance(value, dict):
        if set(value) == {"name"} and value["name"] in bound:
            return {"name": bound[value["name"]]}
        return {key: ("<var>" if key == "binds" else _rename(val, sign, rows, depth, bound))
                for key, val in value.items()}
    if isinstance(value, list):
        return [_rename(item, sign, rows, depth, bound) for item in value]
    if isinstance(value, str) and value in rows:
        return sign(value, depth + 1)
    return value


def _differences(first, second) -> list[str]:
    """What moved between two zips of the same machine, named in the reader's terms."""
    if second is None:
        return ["stanza made nothing of the decompiled sentence"]
    out = []
    was, now = first.model_dump(exclude_none=True), second.model_dump(exclude_none=True)
    for field in ("topicality", "unplaced"):
        if was.get(field) != now.get(field):
            out.append(f"{field}: was {was.get(field)!r}, came back {now.get(field)!r}")
    before = {row["name"]: row for row in was.get("rows", [])}
    after = {row["name"]: row for row in now.get("rows", [])}
    for name in sorted(set(before) | set(after)):
        if name not in after:
            out.append(f"row {name} ({before[name].get('kind')}) did not come back")
        elif name not in before:
            out.append(f"row {name} ({after[name].get('kind')}) is new")
        elif before[name] != after[name]:
            keys = {k for k in set(before[name]) | set(after[name])
                    if before[name].get(k) != after[name].get(k)}
            out.append(f"row {name}: {', '.join(sorted(keys))} moved")
    if not out:
        out.append("the rows are equal but the zips are not — a field outside `rows` moved")
    return out


def run(argv=None) -> int:
    parser = argparse.ArgumentParser(description="zip -> sentence -> zip, and are they the same?")
    parser.add_argument("--db", default=None, help="read the closed classes from this database")
    parser.add_argument("--all", action="store_true", help="print every case, not only the failures")
    parser.add_argument("--fixpoint", action="store_true",
                        help="the station against itself: sentence -> zip -> sentence -> zip")
    args = parser.parse_args(argv)
    if args.fixpoint:
        return fixpoint(argv, args)

    from tk2.language.skeleton import StanzaSkeletons

    table = standing_closed_classes(args.db)
    # The SAME context the compiler is given — the person axis has two directions, and a
    # decompiler that does not know who is speaking cannot say «I».
    compiler, provider = Compiler(table), StanzaSkeletons()
    decompiler = Decompiler(table, context=DRILL_CONTEXT)

    print("=" * 96)
    print("THE ROUND TRIP — the drill's own zips, decompiled and compiled again (req 9)")
    print("=" * 96)
    print(f"  closed classes    {len(table)} rows, v{table.version} — {table.source}")
    print(f"  the corpus        {len(CASES)} hand-compiled zips\n")

    said = refused = unparsed = 0
    agreed, changed = [], []
    for case in CASES:
        out = decompiler.decompile(case.zip)
        if not out.text.strip():
            refused += 1
            continue
        said += 1
        skeletons = provider(out.text)
        if not skeletons:
            unparsed += 1
            continue
        again = compile_utterance(compiler, skeletons, DRILL_CONTEXT).zip
        reading = compare(again, case.zip, case.id, out.text)
        (changed if reading.verdict == DISAGREED else agreed).append((case, out, reading))

    for case, out, reading in (changed if not args.all else changed + agreed):
        mark = "CHANGED" if reading.verdict == DISAGREED else "same"
        print(f"  {case.id:8} {mark:8} « {out.text[:62]} »")
        print(f"           was « {case.sentence[:62]} »")
        for conflict in reading.conflicts[:3]:
            print(f"      ⚑ {conflict}")

    print(f"\n  SAID            {said} of {len(CASES)} zips reached a sentence")
    print(f"  REFUSED         {refused} — the decompiler declined rather than say something the "
          f"zip does not")
    print(f"  SAME THOUGHT    {len(agreed)} of the {said - unparsed} that were read back")
    print(f"  CHANGED         {len(changed)} — the round trip's only real failure")
    if unparsed:
        print(f"  UNPARSED        {unparsed} — stanza made nothing of the sentence")
    print("\n  **REFUSED IS NOT A FAILURE.** A zip the decompiler cannot say without lying is one it")
    print("  must not say at all (req 8, in the other direction). The number to watch is CHANGED.")
    return 1 if changed else 0


if __name__ == "__main__":
    raise SystemExit(run())
