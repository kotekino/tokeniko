"""0001 — CREATE THE WORLD.

The first migration of tokeniko 2. It makes the twelve collections exist, seeds the parameters the
body reads at boot, writes the heart's anatomy, and gives the newborn the rows his first tick will
look for.

What it deliberately does NOT seed: the micro-nn declarations (E5 declares instances when there are
instances to declare), the dictionary (E1), and any knowledge at all. This migration creates a body,
not a mind — an empty one that boots, reads its parameters, and ticks.

The temperament baselines are all 0.0, and that is a placeholder rather than a personality. «The
seed is only t₀» (heart req. 11), and choosing who he starts out as is the Captain's to make in a
later migration — 0.0 means «no inclination recorded yet», not «incapable of calm».
"""

from tk2.core import constants
from tk2.core.models import (
    ALL_MODELS,
    HeartAnatomyDoc,
    HeartLevelDoc,
    HeartMoodDoc,
    HeartTemperamentDoc,
    ParamDoc,
)
from tk2.migrations import ensure_collections

# ------------------------------------------------------------------------------------------------
# THE HEART'S ANATOMY — heart reqs 7 and 8, as rows
# ------------------------------------------------------------------------------------------------

#: (pole, sphere, opposite, targets). Targets read straight off req. 7: love–hate and
#: trust–skepticism target «people, including self»; curiosity–boredom targets ideas and KB regions.
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

ANATOMY_ROWS = [
    {"pole": pole, "sphere": sphere, "opposite": opposite, "targets": targets}
    for pole, sphere, opposite, targets in SPHERE_ROWS
] + [
    {"pole": pole, "sphere": None, "opposite": None, "targets": ["self"], "trigger": trigger}
    for pole, trigger in SPIKE_ROWS
]

SPHERE_POLES = [pole for pole, _s, _o, _t in SPHERE_ROWS]
ALL_POLES = SPHERE_POLES + [pole for pole, _t in SPIKE_ROWS]

# ------------------------------------------------------------------------------------------------
# THE PARAMETERS — keys follow the house convention: component.concern.setting
# ------------------------------------------------------------------------------------------------

PARAM_ROWS = [
    {
        "key": constants.RCACHE_INTERVAL_PARAM,
        "value": constants.RCACHE_INTERVAL_DEFAULT,
        "note": "how often the r-cache re-reads the r-tier; the refresh rate is itself refreshable",
    },
    {
        "key": constants.BODY_TICK_PARAM,
        "value": constants.BODY_TICK_DEFAULT,
        "note": "seconds between ticks; the loop's existence is dna, its cadence is kb",
    },
    {
        "key": constants.DICTIONARY_EPOCH_PARAM,
        "value": 0,
        "note": "the derived layer's version; a derived point stamped below this is stale",
    },
    # Placeholders. E4 sets the real numbers once there is a search to bound — they are seeded now
    # so the rows exist and the body has something to read rather than a None that travels.
    {
        "key": "evaluator.budget.max_depth",
        "value": 0,
        "note": "PLACEHOLDER until E4: 0 means unset, not «no chaining allowed»",
    },
    {
        "key": "evaluator.budget.max_seconds",
        "value": 0,
        "note": "PLACEHOLDER until E4: 0 means unset, not «no time allowed»",
    },
]


def up(writer, db) -> None:
    # The shape first: collections, indexes, and the timeseries configuration, taken from the models
    # themselves so there is one source of truth for the schema.
    ensure_collections(db, ALL_MODELS)

    writer.insert_many(ParamDoc, PARAM_ROWS)
    writer.insert_many(HeartAnatomyDoc, ANATOMY_ROWS)

    # The newborn's heart. Every pole gets a level row because the first tick reads them, and a tick
    # that has to cope with a missing pole is a tick that has to guess what «missing» means.
    writer.insert_many(HeartLevelDoc, [{"pole": pole, "level": 0.0} for pole in ALL_POLES])

    # Mood and temperament integrate the SPHERE poles only: a spike fires and decays inside one
    # tick, so averaging it over a slow window would smear an event into a disposition.
    writer.insert_many(HeartMoodDoc, [{"pole": pole, "value": 0.0} for pole in SPHERE_POLES])
    writer.insert_many(
        HeartTemperamentDoc, [{"pole": pole, "baseline": 0.0} for pole in SPHERE_POLES]
    )
