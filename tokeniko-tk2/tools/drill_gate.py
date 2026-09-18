"""THE DRILL GATE — the station against the Captain's own hand-compiled zips. **Requirement 18.**

    PYTHONPATH=. ../.venv/bin/python tools/drill_gate.py [--db tokeniko_tk2] [--json out.json]

**WHY THIS EXISTS, AND THE COST OF ITS NOT EXISTING.** The drill is the FORMAT's gate: 87 sentences
compiled BY HAND, with no parser involved, proving tkzip can hold the world. The UD gate is the
STATION's: it compiles strangers' sentences and never looks at the drill. **Nothing compared what the
station PRODUCES with what the Captain hand-COMPILED** — and on 2026-09-16 that cost something
concrete: the compile core put `topic` where E2 had ruled `patient` for every copular subject,
contradicting 43 hand-compiled rows, and no test went red for a day.

*A gate that cannot disagree with the other gate is two gates measuring one thing twice.*

**IT SCORES AGREEMENT, NOT EQUALITY, AND THAT IS THE WHOLE DESIGN.** Most of the drill needs features
E3 has not built — attitudes, domains, negation rows, most quantifier scoping — so a zip-equality
check would fail all 87 and teach nothing. What is asked instead is: **where both the station and the
drill speak about the same thing, do they say the same thing?**

    AGREED      the station produced a row or a role and the drill has the same one
    DISAGREED   both name the same filler and give it DIFFERENT roles — the only failure that counts
    MISSING     the drill has it and the station does not. Expected, counted, never averaged in

**THE MATCHING IS BY CONTENT, NOT BY POSITION.** Rows pair on their predicate key (and, for copular
rows which have no predicate by req 31, on their complement's head); boxes pair on their HEAD key.
That is what makes a disagreement meaningful: `patient: sue.n` against `topic: sue.n` is the same
filler under two names, which is precisely the defect this gate was built for.
"""

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tests.fixtures.drill import CASES  # noqa: E402
from tk2.language import standing_closed_classes  # noqa: E402
from tk2.language.compile import Compiler  # noqa: E402
from tk2.language.utterance import Context, compile_utterance  # noqa: E402
from tk2.tkzip.schema import Open  # noqa: E402

AGREED, DISAGREED, MISSING = "agreed", "DISAGREED", "missing"

#: **THE DRILL'S OWN DEICTIC CENTRE.** The station resolves a first- or second-person pronoun against
#: the context it is handed, and hands back the bare closed-class key when it is handed none — so a
#: gate that passed no context could not see the person axis AT ALL, and the quotation block added on
#: 2026-09-17 to exercise `addressee` would have been measured by an instrument blind to it.
#:
#: The values are not arbitrary and they are not the station's business: the drill hand-compiles «I»
#: as `me.n` and «you» as `you.n` throughout, so passing exactly those makes every UNROTATED sentence
#: compile to what it compiled to before, and leaves only the rotation visible. *The comparison is
#: against the Captain's convention, stated as the argument req 7 says it must be.*
DRILL_CONTEXT = Context(speaker="me.n", addressee="you.n")


def filler(box) -> str:
    """A box's head as a comparable string — the key, the variable's name, or a marker for OPEN.

    A VARIABLE is compared by NAME and that is deliberately weak: the station and the drill number
    their variables independently, so `x0` against `P` is not a disagreement about anything. Those
    pairs are reported as unmatched rather than as a conflict.
    """
    head = getattr(box, "head", None)
    if head is None:
        return ""
    if isinstance(head, str):
        return head
    name = getattr(head, "name", None)
    return f"var:{name}" if name else "open"


def rows_of(zip_, kind="content"):
    return [r for r in zip_.rows if r.kind == kind]


def signature(row) -> str:
    """What a content row is ABOUT, for pairing across two independently-built zips.

    The predicate where there is one. Where there is not — a copular row earns no predicate (req 31)
    — the complement's head, because «Sue is a teacher» is the teacher row in both zips whatever else
    differs.
    """
    predicate = getattr(row, "predicate", None)
    if predicate:
        return str(predicate)
    boxes = getattr(row, "boxes", {})
    for role, box in boxes.items():
        if role.value == "complement":
            return f"={filler(box)}"
    return "=" + "|".join(sorted(filler(b) for b in boxes.values()))


@dataclass
class Reading:
    """What the gate makes of one drill sentence."""

    case_id: str
    sentence: str
    paired: int = 0
    agreed: int = 0
    conflicts: list = field(default_factory=list)
    missing_roles: list = field(default_factory=list)
    missing_rows: list = field(default_factory=list)
    unparsed: str = ""

    @property
    def verdict(self) -> str:
        if self.conflicts:
            return DISAGREED
        return AGREED if self.agreed else MISSING


def compare(produced, expected, case_id="", sentence="") -> Reading:
    """One produced zip against one hand-compiled zip. **Pure** — no parser, no database.

    Split out from the run so the comparison can be tested with hand-made zips on both sides, which
    is the only way to know the instrument reports a disagreement when there is one. A gate nobody
    has seen fail is a gate nobody can trust.
    """
    reading = Reading(case_id=case_id, sentence=sentence)
    mine = rows_of(produced)
    theirs = rows_of(expected)

    taken = set()
    for row in mine:
        match = next((i for i, other in enumerate(theirs)
                      if i not in taken and signature(other) == signature(row)), None)
        if match is None:
            continue
        taken.add(match)
        reading.paired += 1
        other = theirs[match]

        # Pair the BOXES by their filler, then ask whether the two zips give it the same role.
        their_roles = {}
        for role, box in other.boxes.items():
            their_roles.setdefault(filler(box), []).append(role.value)
        for role, box in row.boxes.items():
            found = filler(box)
            if not found or found.startswith("var:") or found == "open":
                continue
            if found not in their_roles:
                continue
            if role.value in their_roles[found]:
                reading.agreed += 1
            else:
                reading.conflicts.append(
                    f"{found}: the station says {role.value}, the drill says "
                    f"{'/'.join(their_roles[found])}")
        for found, roles in their_roles.items():
            if not found or found.startswith("var:") or found == "open":
                continue
            if found not in {filler(b) for b in row.boxes.values()}:
                reading.missing_roles.append(f"{found} ({'/'.join(roles)})")

        # **THE MIRROR TEST — the right role holding the WRONG SOMEBODY.** The pass above pairs by
        # FILLER and asks whether the two zips agree on its role. That is blind in exactly the
        # direction the person axis fails in: «John said to Marie that you are late» compiled about
        # Marie puts a perfectly ordinary `patient` on a perfectly ordinary row, and the only thing
        # wrong with it is WHO. The two tests are mirrors and neither implies the other, so the gate
        # runs both. Added 2026-09-17 with the quotation block, which it was built blind to.
        for role, box in row.boxes.items():
            their_box = other.boxes.get(role)
            if their_box is None:
                continue
            mine_key, their_key = filler(box), filler(their_box)
            if not mine_key or not their_key:
                continue
            # A variable or an OPEN is not a disagreement about anybody — the same abstention the
            # filler pass makes, and for the same reason: the two zips number and abstain
            # independently.
            if {mine_key, their_key} & {"open"} or mine_key.startswith("var:") \
                    or their_key.startswith("var:"):
                continue
            if mine_key != their_key:
                reading.conflicts.append(
                    f"{role.value}: the station says {mine_key}, the drill says {their_key}")

        # **THE TRUTH SLOT — the third blindness, closed 2026-09-18 (req 21).** Roles were compared
        # and truth never was, so «Is the cat hungry?» compiled at 1.0 against a drill that
        # hand-compiles it OPEN (`exist-4`, `t-mo-1`) and nothing disagreed. The STATE is compared,
        # not the value: the drill writes a negated row as `truth=0.0` where the station raises a
        # negation prefix, and a forecast as a confidence — a value against a value is not a
        # disagreement about whether anything was claimed or asked.
        mine_state, their_state = truth_state(row), truth_state(other)
        if mine_state != their_state:
            reading.conflicts.append(
                f"truth of {signature(row)}: the station says {mine_state}, "
                f"the drill says {their_state}")

    for i, other in enumerate(theirs):
        if i not in taken:
            reading.missing_rows.append(signature(other))
    return reading


def truth_state(row) -> str:
    """What a row's truth slot SAYS, not its value: `stated` (a value — claimed, denied, or held at
    a confidence) · `OPEN` (asked) · `unstated` (neither claimed nor asked: a supposition, a want)."""
    truth = getattr(row, "truth", None)
    if truth is None:
        return "unstated"
    return "OPEN" if isinstance(truth, Open) else "stated"


def run(argv=None) -> int:
    parser = argparse.ArgumentParser(description="score the station against the drill's own zips")
    parser.add_argument("--db", default=None, help="read the closed classes from this database")
    parser.add_argument("--json", default=None, help="write the whole measurement here")
    parser.add_argument("--all", action="store_true",
                        help="print every sentence, not only the disagreements")
    args = parser.parse_args(argv)

    from tk2.language.skeleton import StanzaSkeletons

    table = standing_closed_classes(args.db)
    compiler = Compiler(table)
    provider = StanzaSkeletons()

    print("=" * 96)
    print("THE DRILL GATE — the station against the Captain's own hand-compiled zips (req 18)")
    print("=" * 96)
    print(f"  closed classes    {len(table)} rows, v{table.version} — {table.source}")
    print(f"  the drill         {len(CASES)} sentences, hand-compiled at E2 with no parser involved")
    print()

    readings = []
    for case in CASES:
        try:
            skeletons = provider(case.sentence)
        except Exception as problem:                      # noqa: BLE001 — a provider stumble is data
            readings.append(Reading(case.case_id if hasattr(case, "case_id") else case.id,
                                    case.sentence, unparsed=str(problem)[:90]))
            continue
        if not skeletons:
            readings.append(Reading(case.id, case.sentence, unparsed="no skeleton"))
            continue
        # **EVERY SENTENCE OF THE UTTERANCE, since E3 task 2b.2.** This gate is what reported the
        # gap — five of the drill's sentences were split by stanza and only the first half read —
        # and `compile_utterance` is what closed it. The sentences are merged into one zip and are
        # not yet RELATED to one another; that is 2b.3, the Captain's format ruling.
        produced = compile_utterance(compiler, skeletons, DRILL_CONTEXT)
        reading = compare(produced.zip, case.zip, case.id, case.sentence)
        if produced.split:
            reading.unparsed = f"stanza split this into {len(skeletons)} sentences; all were read"
        readings.append(reading)

    conflicts = [r for r in readings if r.verdict == DISAGREED]
    agreed = [r for r in readings if r.verdict == AGREED]
    split = [r for r in readings if r.unparsed]

    if conflicts or args.all:
        print(f"  {'case':<10} {'verdict':<11} {'rows':<8} {'roles':<8} sentence")
        print(f"  {'-' * 10} {'-' * 11} {'-' * 8} {'-' * 8} {'-' * 40}")
        for reading in readings:
            if not args.all and reading.verdict != DISAGREED:
                continue
            print(f"  {reading.case_id:<10} {reading.verdict:<11} "
                  f"{reading.paired}/{reading.paired + len(reading.missing_rows):<6} "
                  f"{reading.agreed}/{reading.agreed + len(reading.missing_roles):<6} "
                  f"« {reading.sentence[:44]} »")
            for conflict in reading.conflicts:
                print(f"      ⚑ {conflict}")
        print()

    paired = sum(r.paired for r in readings)
    rows_total = paired + sum(len(r.missing_rows) for r in readings)
    roles_agreed = sum(r.agreed for r in readings)
    roles_total = roles_agreed + sum(len(r.missing_roles) for r in readings)

    print(f"  ROWS PAIRED    {paired} of {rows_total} the drill hand-compiled")
    print(f"  ROLES AGREED   {roles_agreed} of {roles_total} on the rows that paired")
    print(f"  SENTENCES      {len(agreed)} agreed · {len(conflicts)} DISAGREED · "
          f"{len(readings) - len(agreed) - len(conflicts)} reached no common ground")
    if split:
        print(f"  MULTI-SENTENCE {len(split)} were split by stanza and ALL halves were read "
              f"(2b.2); a quote rotates against its frame and becomes its CONTENT, unclaimed "
              f"(2b.4)")
    print()
    print("  **ONLY `DISAGREED` IS A DEFECT.** A missing row is E3 not being finished, and it is")
    print("  counted apart so it can never be averaged into something that looks like agreement.")

    if args.json:
        import json

        Path(args.json).write_text(json.dumps([{
            "case": r.case_id, "sentence": r.sentence, "verdict": r.verdict,
            "paired": r.paired, "agreed": r.agreed, "conflicts": r.conflicts,
            "missing_roles": r.missing_roles, "missing_rows": r.missing_rows,
            "note": r.unparsed,
        } for r in readings], indent=2))
        print(f"\n  written to {args.json}")

    return 1 if conflicts else 0


if __name__ == "__main__":
    raise SystemExit(run())
