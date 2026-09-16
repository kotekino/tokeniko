"""THE DRILL, SCORED against the bar declared and committed before it existed (`1a68337`).

  bar:  >= 90% no-abstention  ·  100% no-silent-wrong
  and the COUNT of schema changes the drill forced, reported beside the score — because an
  instrument that can always be satisfied by moving the target measures nothing.
"""

from collections import Counter

import pytest

from tests.fixtures.drill import CASES
from tk2.tkzip.schema import Zip

# The forced-change ledger. Every entry names the sentence that forced it. Adding a row here is the
# admission that the conception missed something; the LENGTH of this list is part of the result.
FORCED_CHANGES = [
    ("direction box", "He looked up. / She turned left.",
     "a direction with no endpoint — not a destination, not a path, not a manner"),
    ("scopes on prefix rows", "Software can be minds and humans must be minds.",
     "◇A ∧ □B — two modalities over two conjuncts; «everything after» could not express it"),
    ("Ref — a box may hold a row name", "Cognition is the psychological result of perception and "
     "learning and reasoning.",
     "req 34 said a box may hold a row name and there was no type for it; the name validated as a "
     "bare dictionary key"),
]

NO_ABSTENTION_BAR = 0.90


@pytest.mark.parametrize("case", CASES, ids=[c.id for c in CASES])
def test_every_case_validates_and_round_trips(case):
    assert Zip.model_validate(case.zip.model_dump()) == case.zip


@pytest.mark.parametrize("case", [c for c in CASES if c.distinct_from],
                         ids=[c.id for c in CASES if c.distinct_from])
def test_readings_that_must_stay_apart_stay_apart(case):
    """Two sentences that mean different things must not produce one zip — the silent-wrong sin."""
    by_id = {c.id: c for c in CASES}
    for other in case.distinct_from:
        assert case.zip != by_id[other].zip, f"{case.id} collapsed into {other}"


def test_quoted_and_reported_speech_converge():
    """Two spellings of one meaning must produce ONE zip — the mirror of `distinct_from`.

    «John said to Marie "You are late"» and «John said to Marie that she was late» differ only in
    the wording John used, and tkzip stores meaning. The two get there by different machinery — a
    rotation against the addressee, and an anaphor resolved to the recipient — which is exactly why
    it is worth asserting that they meet.
    """
    by_id = {c.id: c for c in CASES}
    assert by_id["q-5"].zip == by_id["q-6"].zip


def test_a_partial_is_honestly_marked():
    """PARTIAL is only legal if the zip SAYS it is incomplete — unplaced material, or an open slot,
    or confidence below 1. A silently incomplete zip is a silent-wrong."""
    for case in CASES:
        if case.verdict != "partial":
            continue
        honest = bool(case.zip.unplaced) or (case.zip.parse_confidence or 1.0) < 1.0
        assert honest, f"{case.id} is partial but the zip does not admit it"


def test_no_case_is_a_silent_wrong():
    assert [c.id for c in CASES if c.verdict == "fail"] == []


def test_the_drill_meets_its_declared_bar():
    counts = Counter(c.verdict for c in CASES)
    total = len(CASES)
    coverage = counts["pass"] / total
    assert counts["fail"] == 0, "100% no-silent-wrong is absolute"
    assert coverage >= NO_ABSTENTION_BAR, f"{coverage:.1%} is below the declared {NO_ABSTENTION_BAR:.0%}"


def test_the_allocation_is_what_was_declared():
    """~30 clusters / ~30 traffic / ~15 awkward, and every one of the six clusters present."""
    half = Counter(c.source.split(":")[0] for c in CASES)
    assert half["cluster"] >= 25 and half["traffic"] >= 25 and half["awkward"] >= 15
    clusters = {c.source for c in CASES if c.source.startswith("cluster:")}
    assert len(clusters) == 6, clusters


def test_every_format_failure_category_from_the_traffic_is_represented():
    """The selection rule declared with the bar: cover all seven of v1's format-failure categories."""
    seen = {c.source.split(":", 1)[1] for c in CASES if c.source.startswith("traffic:")}
    assert seen == {"wrong-structure", "dropped-content", "operator-flattening", "missed-mood",
                    "missed-negation", "missed-modality", "missed-quantifier"}


def test_the_report(capsys):
    """Not an assertion — the drill's result, printed where it can be read."""
    counts = Counter(c.verdict for c in CASES)
    total = len(CASES)
    lines = [
        "",
        "=" * 78,
        f"THE DRILL — {total} sentences",
        "=" * 78,
        f"  PASS     {counts['pass']:3d}   {counts['pass']/total:6.1%}",
        f"  PARTIAL  {counts['partial']:3d}   {counts['partial']/total:6.1%}   (counts against the 90%)",
        f"  FAIL     {counts['fail']:3d}   {counts['fail']/total:6.1%}",
        "",
        f"  bar: >= {NO_ABSTENTION_BAR:.0%} no-abstention · 100% no-silent-wrong",
        f"  met: {'YES' if counts['pass']/total >= NO_ABSTENTION_BAR and not counts['fail'] else 'NO'}",
        "",
        f"  SCHEMA CHANGES THE DRILL FORCED: {len(FORCED_CHANGES)}",
    ]
    for name, sentence, why in FORCED_CHANGES:
        lines.append(f"    · {name} — «{sentence}»")
        lines.append(f"      {why}")
    lines.append("")
    by_half = Counter(c.source.split(":")[0] for c in CASES)
    for half, n in sorted(by_half.items()):
        p = sum(1 for c in CASES if c.source.startswith(half) and c.verdict == "pass")
        lines.append(f"  {half:9s} {n:3d} cases · {p} pass")
    lines.append("")
    for case in CASES:
        if case.verdict != "pass":
            lines.append(f"  [{case.verdict.upper()}] {case.id}: {case.sentence}")
    lines.append("=" * 78)
    print("\n".join(lines))
