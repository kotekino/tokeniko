"""THE CANONICAL HEART ANATOMY — heart reqs 7 and 8, expressed as rows.

This is a test asset, not the seed itself: migration 0001 (T5) owns the real seeding. It lives here
so that T4 can prove the requirements' heart is EXPRESSIBLE in the table — six spheres of two
independent poles, three spikes with their triggers, targets as the requirements state them — and so
that T5 has the exact rows to write rather than re-deriving them from prose.

Targets read straight off heart req. 7: love–hate and trust–skepticism target «people, including
self», which is why those poles carry both kinds; curiosity–boredom targets ideas and KB regions.
"""

SPHERE_ROWS = [
    ("joy", "joy-sadness", "sadness", ["self"]),
    ("sadness", "joy-sadness", "joy", ["self"]),
    ("love", "love-hate", "hate", ["self", "person"]),
    ("hate", "love-hate", "love", ["self", "person"]),
    ("anxiety", "anxiety-calm", "calm", ["self"]),
    ("calm", "anxiety-calm", "anxiety", ["self"]),
    ("trust", "trust-skepticism", "skepticism", ["self", "person"]),
    ("skepticism", "trust-skepticism", "trust", ["self", "person"]),
    ("curiosity", "curiosity-boredom", "boredom", ["idea"]),
    ("boredom", "curiosity-boredom", "curiosity", ["idea"]),
    ("pride", "pride-shame", "shame", ["self"]),
    ("shame", "pride-shame", "pride", ["self"]),
]

#: Not spheres — event signals. All target self, all decay on a dna curve (heart req. 8).
SPIKE_ROWS = [
    ("startle", "unexpected raw input"),
    ("disillusion", "a staked expectation breaks"),
    ("serendipity", "an equation closes unsought"),
]


def canonical_anatomy() -> list[dict]:
    """The fifteen rows, as dicts ready for the migration writer."""
    rows = [
        {"pole": pole, "sphere": sphere, "opposite": opposite, "targets": targets}
        for pole, sphere, opposite, targets in SPHERE_ROWS
    ]
    rows += [
        {"pole": pole, "sphere": None, "opposite": None, "targets": ["self"], "trigger": trigger}
        for pole, trigger in SPIKE_ROWS
    ]
    return rows
