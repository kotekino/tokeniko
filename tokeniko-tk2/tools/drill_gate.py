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

**AND SINCE 2026-09-19 IT READS THE PREFIX AND THE JOINS.** For three widenings it compared
`kind="content"` and nothing else, so 89 prefix rows and 50 joins the Captain hand-compiled — every
attitude's holder, verb, addressee and strength, every negation, modality, domain and quantifier, and
every join's truth slot — were outside the instrument. A prefix row is resolved to the row it SCOPES
(`target_keys`, so no name is ever compared), pairs on what it IS (`about`) and is compared on what
it SAYS (`says_what`). Record: `docs/parser-compiler/202609190900_the-gate-sees-the-prefix.md`.
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
    """A box's head as a comparable string — the key, the variable's name, or what is known about an
    OPEN one.

    A VARIABLE is compared by NAME and that is deliberately weak: the station and the drill number
    their variables independently, so `x0` against `P` is not a disagreement about anything. Those
    pairs are reported as unmatched rather than as a conflict.

    **AN OPEN IS COMPARED BY WHAT THE SENTENCE SAID ABOUT IT** *(schema v4, 2026-09-20)*. Every open
    slot used to flatten to the word «open», so two boxes that disagreed about WHO — «he» against
    «she» — compared equal, and a box the drill described compared equal to one the station left
    blank. It is still weak where it should be: an undescribed OPEN on either side matches anything,
    because «I do not know» is not a claim that can conflict with one.
    """
    head = getattr(box, "head", None)
    if head is None:
        return ""
    if isinstance(head, str):
        return head
    name = getattr(head, "name", None)
    if name:
        return f"var:{name}"
    told = {field: getattr(head, field, None)
            for field in ("sort", "person", "number", "gender")}
    told = {k: v for k, v in told.items() if v is not None}
    return "open " + " ".join(f"{k}={v}" for k, v in sorted(told.items())) if told else "open"


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


#: The five scope-bearing kinds (tkzip req 35), in the order the schema declares them.
PREFIX_KINDS = ("quantifier", "negation", "modality", "attitude", "domain")


def target_keys(zip_) -> dict[str, str]:
    """Every row's name mapped to a NAME-FREE key, so two zips can pair rows they named differently.

    A prefix element scopes a row BY NAME (`scopes`), and the two zips number their rows
    independently — `aw-21`'s want scopes `cl`, the station's scopes `r0`. Comparing the prefix at
    all therefore needs the target resolved to something both sides produce: a content row's
    signature, or, for a join, its operator over its operands' keys, recursively.

    The schema guarantees `scopes` names a content or join row, so this terminates on any valid zip;
    the depth guard is for a zip that is being CHECKED rather than trusted.
    """
    rows = {r.name: r for r in zip_.rows}

    def resolve(name: str, depth: int = 0) -> str:
        row = rows.get(name)
        if row is None or depth > 8:
            return "?"
        if row.kind == "content":
            return signature(row)
        if row.kind == "join":
            halves = " | ".join(resolve(n, depth + 1) for n in row.operands)
            return f"({row.operator.value} {halves})"
        # A PREFIX row's key is the key of what it SCOPES — the row it is about. Resolving its own
        # name instead gave every prefix row the same key, `?`, and the first widening's run paired
        # quantifiers that had nothing to do with one another and called them a disagreement.
        return resolve(row.scopes, depth + 1)

    return {name: resolve(name) for name in rows}


def says_what(row) -> dict[str, str]:
    """What a prefix row SAYS, field by field, as strings both zips can produce.

    One dict per kind, holding only what is COMPARABLE across two independently-built zips: an enum
    value, a box's filler, or a slot's STATE. **No magnitude is ever compared** — `strength` is
    reported as stated/unstated exactly as `truth_state` reports the truth slot, because a value is
    curation and the gate is not the curator. It is the difference between «the station says nothing
    about how strongly this wants» and «the station says 0.85 where the table says 0.9»: the first is
    a defect, the second is a migration.
    """
    if row.kind == "attitude":
        return {
            "verb": str(row.verb),
            "holder": filler(row.holder),
            "addressee": "(nobody)" if row.addressee is None else filler(row.addressee),
            "strength": "unstated" if row.strength is None else "stated",
        }
    if row.kind == "modality":
        return {"modality": row.modality.value}
    if row.kind == "domain":
        return {"domain": filler(row.domain)}
    if row.kind == "quantifier":
        return {"quantity": row.quantity.value, "restriction": filler(row.restriction)}
    return {}                                     # a negation says only that it is there


def about(row) -> str:
    """What a prefix row IS, inside its kind — the half of it that pairs rather than compares.

    The gate's standing doctrine, applied a third time: a content row pairs on its PREDICATE and is
    compared on its boxes; a box pairs on its FILLER and is compared on its role. So an attitude
    pairs on its VERB and is compared on who holds it, whom it addresses and how strongly. Pairing
    two attitudes over one row by document order instead read «Marie said "John told me…"» as the
    station getting Marie's saying wrong, when what it had actually done was get John's telling
    exactly right and miss the outer saying — a MISSING dressed as a defect.

    A quantifier pairs on its restriction («all CATS») and a domain on its domain, for the same
    reason: those are what the row is about, and the station producing a different one is a row the
    drill does not have, not a disagreement about this one.
    """
    if row.kind == "attitude":
        return str(row.verb)
    if row.kind == "quantifier":
        return filler(row.restriction)
    if row.kind == "domain":
        return filler(row.domain)
    return ""


def _comparable(mine: str, theirs: str) -> bool:
    """The same abstention the box pass makes: a VARIABLE, or an OPEN nobody described, is nobody's
    disagreement.

    **A DESCRIBED OPEN IS COMPARABLE** *(schema v4)*: «he» against «she» is two different claims
    about who, and a gate that called them equal was reporting agreement it had not measured. One
    side undescribed still abstains — «I do not know» contradicts nothing.
    """
    if not mine or not theirs:
        return False
    if any(v.startswith("var:") for v in (mine, theirs)):
        return False
    return not any(v == "open" for v in (mine, theirs))


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
    #: The prefix and the joins are counted APART from the content rows and their roles. Folding
    #: them in would move both figures on the day the gate widened and make the history unreadable.
    prefix_paired: int = 0
    said: int = 0
    missing_prefix: list = field(default_factory=list)
    joins_paired: int = 0
    missing_joins: list = field(default_factory=list)
    unparsed: str = ""

    @property
    def verdict(self) -> str:
        if self.conflicts:
            return DISAGREED
        return AGREED if (self.agreed or self.said) else MISSING


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

    _prefix_pass(produced, expected, reading)
    _join_pass(produced, expected, reading)
    return reading


def _prefix_pass(produced, expected, reading) -> None:
    """**THE FOURTH BLINDNESS, closed 2026-09-19.** The gate read `kind="content"` and nothing else,
    so the whole PREFIX was uncompared: every attitude's holder, verb, addressee and strength, every
    negation, modality and domain row. `aw-21`'s POV(me · want) — the imperative, built the day
    before — was measured by an instrument that could not see it, and so were the quotation holders
    the person axis exists for.

    **Pairing is by (kind, the row scoped, what the row is ABOUT)** — see `about`. No name is
    compared: the target is resolved through `target_keys`, so «the want over close.v» is a thing
    both zips can say.

    **AND THE LEFTOVERS ARE READ, because absence and substitution are different facts.** When the
    drill has a prefix row nothing paired with, the gate asks whether the station has an unpaired row
    OF THE SAME KIND OVER THE SAME ROW. If it does, that is a SUBSTITUTION and a defect: the station
    said something ELSE about that row. If it does not, it is MISSING and no defect — most of the
    prefix is E3 unfinished. An extra station row over a row the drill left bare is passed over in
    silence, exactly as an extra content row is: the drill is a floor, not a ceiling.

    *The substitution branch is a GUARD and fires nowhere in the drill today.* The case it is written
    for is `aw-20` — «Suppose the cat is hungry» read as a WANT where the drill holds a SUPPOSE — and
    that one does not reach it, because the station's want scopes the `suppose.v` row it builds and
    the drill's supposition scopes the cat's. Named as a guard so a later reader does not take its
    silence for evidence.
    """
    mine_keys, their_keys = target_keys(produced), target_keys(expected)

    pool: dict[tuple, list] = {}
    for row in expected.rows:
        if row.kind in PREFIX_KINDS:
            pool.setdefault((row.kind, their_keys[row.name], about(row)), []).append(row)

    spare: dict[tuple, list] = {}
    for row in produced.rows:
        if row.kind not in PREFIX_KINDS:
            continue
        waiting = pool.get((row.kind, mine_keys[row.name], about(row)))
        if not waiting:
            spare.setdefault((row.kind, mine_keys[row.name]), []).append(row)
            continue
        other = waiting.pop(0)
        reading.prefix_paired += 1
        mine_says, their_says = says_what(row), says_what(other)
        if not mine_says:                             # a negation: being there IS the agreement
            reading.said += 1
        for slot, value in mine_says.items():
            theirs = their_says.get(slot, "")
            if not _comparable(value, theirs):
                continue
            if value == theirs:
                reading.said += 1
            else:
                reading.conflicts.append(
                    f"{row.kind} over {mine_keys[row.name]}: {slot} — the station says {value}, "
                    f"the drill says {theirs}")

    for (kind, target, what), waiting in pool.items():
        label = f"{kind} {what} over {target}" if what else f"{kind} over {target}"
        for _ in waiting:
            instead = spare.get((kind, target))
            # **AN ABSTENTION IS NOT A SUBSTITUTION** *(2026-09-20, found by the 1st Officier)*. This
            # was the one branch in the gate that did not ask `_comparable()` before calling a
            # difference a conflict — so a station quantifier whose restriction is an undescribed
            # OPEN, sitting over the same row as a drill quantifier over `glitterer.n`, was reported
            # as «the station says something ELSE about that row». It did not: it said «I do not know
            # what this ranges over», which the docstrings two functions above call nobody's
            # disagreement. The defect was mine, introduced the same morning the box passes were
            # widened to read a described OPEN, and it cost `aw-13` and `aw-14` two false reds.
            #
            # `not what` keeps today's behaviour for the kinds whose `about` is empty by construction
            # — negation, modality — so no existing substitution guard is weakened.
            if instead and (not what or _comparable(about(instead[0]), what)):
                row = instead.pop(0)
                reading.conflicts.append(
                    f"{kind} over {target}: the station says {about(row)}, the drill says {what}")
            else:
                reading.missing_prefix.append(label)


def _join_pass(produced, expected, reading) -> None:
    """The joins were uncompared too, and `db/0017` and free choice both turned on their TRUTH.

    A join's key already says everything it is — its operator over its operands' keys — so it pairs
    on that, and what is compared is the same thing a content row's is: the STATE of the truth slot.
    «A or B» claiming its halves was the defect of 2026-09-18; a gate blind to the join could not
    have reported it.
    """
    mine_keys, their_keys = target_keys(produced), target_keys(expected)

    pool: dict[str, list] = {}
    for row in rows_of(expected, "join"):
        pool.setdefault(their_keys[row.name], []).append(row)

    for row in rows_of(produced, "join"):
        waiting = pool.get(mine_keys[row.name])
        if not waiting:
            continue
        other = waiting.pop(0)
        reading.joins_paired += 1
        mine_state, their_state = truth_state(row), truth_state(other)
        if mine_state != their_state:
            reading.conflicts.append(
                f"truth of {mine_keys[row.name]}: the station says {mine_state}, "
                f"the drill says {their_state}")

    for target, waiting in pool.items():
        reading.missing_joins.extend(target for _ in waiting)


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
    prefix_paired = sum(r.prefix_paired for r in readings)
    prefix_total = prefix_paired + sum(len(r.missing_prefix) for r in readings)
    said = sum(r.said for r in readings)
    joins_paired = sum(r.joins_paired for r in readings)
    joins_total = joins_paired + sum(len(r.missing_joins) for r in readings)

    print(f"  ROWS PAIRED    {paired} of {rows_total} the drill hand-compiled")
    print(f"  ROLES AGREED   {roles_agreed} of {roles_total} on the rows that paired")
    print(f"  PREFIX PAIRED  {prefix_paired} of {prefix_total} — attitude · negation · modality · "
          f"domain · quantifier, and {said} of their slots agree")
    print(f"  JOINS PAIRED   {joins_paired} of {joins_total}, compared on the truth slot")
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
            "prefix_paired": r.prefix_paired, "said": r.said,
            "missing_prefix": r.missing_prefix,
            "joins_paired": r.joins_paired, "missing_joins": r.missing_joins,
            "note": r.unparsed,
        } for r in readings], indent=2))
        print(f"\n  written to {args.json}")

    return 1 if conflicts else 0


if __name__ == "__main__":
    raise SystemExit(run())
