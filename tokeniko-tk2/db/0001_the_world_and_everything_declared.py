"""0001 — THE BASELINE. The world, and every curated row nine rulings produced.

**WHY THERE IS A BASELINE AT ALL, and why the thirteen migrations it replaces are in `archive/`.**
E1b renamed every collection whose name was hiding what it held (`base_r` and `base_d` were the
shortest possible names and the least readable) and gave `tokeniko_tk2` to the BODY, the prototype
that used to own it having been superseded whole. Renaming was measured and refused: mongo cannot
rename a TIMESERIES collection at all (`heart_emotional_log` is one, with its `system.buckets`
shadow), and moving a database is a copy in any case. So the honest act was a rebuild.

**WHAT A REBUILD COST, measured before it was chosen: nothing.** Every heart row in the body read
`0.0` with `created_at == updated_at ==` the migration's own timestamp. He had been created and had
never ticked; there was no biography to lose. Everything else in that database came from a migration
or from `tools/build_dictionary.py --apply`, and the base rebuilds from these rows in forty seconds
with a fingerprint that has to match or the rebuild is refused.

**THE LEDGER IS NOT LOST, because the ledger was never the migration files.** It is the
`dictionary_policy` rows, and all NINE versions are written below with their notes verbatim — v1
still fingerprints to what v1 measured, v4 still explains in its own words why only a word's own
lemma may state its antonymy, v9 still says which single pair its NEAR floor is fitted to. What the
squash gives up is the SEQUENCE as replayable steps: that the lemma scope was ruled before the
symmetry, the bar before the mix. That ordering is real information — it is why the rulings are
right — and it survives in git and in the notes, but not as thirteen files anyone can re-run. The
Captain took that price knowingly on 2026-09-10.

**THE ROWS ARE DATA AND ARE READ AS DATA.** `db/data/declared_rows.json` holds them — 2,192 policy
rows across nine versions, 37 bar pairs across two, 383 closed-class forms, the heart's anatomy and
the body's parameters. A file rather than a python literal for two reasons: 2,192 rows of prose
notes inlined would make this migration unreadable, and a diff on a JSON file shows a changed NOTE
as plainly as a changed value, which is the property that makes a curated row auditable.

**WHAT IS NOT HERE.** The base itself — `dictionary_base_keys`, `_relations`, `_distribution` and
their seals. Those are DERIVED, and a migration that shipped a derived artifact would be a migration
doing a build's job: it is `tools/build_dictionary.py --apply`, under the Captain's hand, and the
manifest row it writes is what says which policy it was measured against.
"""

import json
from pathlib import Path

from tk2.core.models import (
    ALL_MODELS,
    BASE_MODELS,
    LEDGER_MODELS,
    ClosedClassDoc,
    DictionaryBarDoc,
    DictionaryPolicyDoc,
    HeartAnatomyDoc,
    HeartLevelDoc,
    HeartMoodDoc,
    HeartTemperamentDoc,
    ParamDoc,
)
from tk2.migrations import ensure_collections

#: Everything nine rulings declared, exported from the thirteen migrations this baseline replaces
#: (`db/archive/`) at the moment they were archived. Every note verbatim; nothing re-typed.
DECLARED = json.loads((Path(__file__).resolve().parent / "data" / "declared_rows.json").read_text())

POLICY_ROWS = DECLARED["policy"]
BAR_ROWS = DECLARED["bar"]
CLOSED_CLASS_ROWS = DECLARED["closed_classes"]
ANATOMY_ROWS = DECLARED["heart_anatomy"]
PARAM_ROWS = DECLARED["params"]

#: Every pole the heart has, and the twelve that are SPHERES. A spike (`startle`, `disillusion`,
#: `serendipity`) has a level like any other pole but no mood and no temperament: it fires and decays
#: inside one tick, so integrating it over a slow window would smear an event into a disposition.
ALL_POLES = tuple(DECLARED["heart_poles"]["all"])
SPHERE_POLES = tuple(DECLARED["heart_poles"]["spheres"])

#: The newest policy version these rows carry — what `config_from_rows` will select by default and
#: what a build measures under.
POLICY_VERSION = max(row["version"] for row in POLICY_ROWS)
BAR_VERSION = max(row["version"] for row in BAR_ROWS)


def _declared():
    """The newest policy version as the value object the engine takes.

    ASSEMBLED FROM THE ROWS, never restated: the rows are the declaration, and a second copy of the
    same values in this file would be the quieter of two declarations — the exact defect the
    standing law of 2026-08-25 exists to prevent. Every archived migration built a `DECLARED` this
    way too; the difference is that this one has nine versions to choose from and says which.
    """
    from tk2.dictionary import policy

    return policy.config_from_rows(
        [row for row in POLICY_ROWS if row["version"] == POLICY_VERSION], BAR_ROWS
    )


#: What a build measures under, unless it is told to read an older version.
DECLARED = _declared()


# ------------------------------------------------------------------------------------------------
# the structural seeds, and the code that re-derives them
# ------------------------------------------------------------------------------------------------
#
# CODE, not data, and that is why it is here rather than in the JSON: `tools/propose_seeds.py
# --verify` re-runs it against the resource and diffs the result against the rows that were written
# down. A seed list nobody can re-derive is a list somebody typed, and the whole ruling of
# 2026-08-25 was that seeds are grown generated-then-curated. Carried unchanged from the archived
# 0005, with two seams re-pointed at this file's own rows.

#: The single-word closed-class forms — the exclusion by PRINCIPLE, read off the rows above rather
#: than off a migration, so the derivation runs before the Captain's hand has applied anything.
CLOSED_CLASS_FORMS = tuple(
    sorted({row["form"] for row in CLOSED_CLASS_ROWS if " " not in row["form"]})
)


def standing_closure():
    """The closure cuts the newest policy version declares, as the value object the walk takes.

    Read from the rows instead of restated, because a second copy of `max_depth` in this file would
    be exactly the quieter-of-two-declarations the standing law forbids.
    """
    from tk2.dictionary import policy

    return policy.closure_from_rows([r for r in POLICY_ROWS if r["version"] == POLICY_VERSION])


STRUCTURAL_K = 200

#: `(word, rank, in_degree)`, in rank order — rank being its position in the CLEANED ranking, which
#: is the table the Captain approved from (the excluded rows are numbered separately and are not in
#: it). The in-degree travels because it is the evidence: it is what «structure argued for this
#: word» actually means, and a rank alone would hide that #200 is named by 241 definitions while #1
#: is named by 4,044.
#:
#: DERIVED, NOT TYPED — see `derive_structural_seeds()` and the head of this file.
STRUCTURAL_SEEDS: tuple[tuple[str, int, int], ...] = (
    ("use", 1, 4044), ("make", 2, 2678), ("relate", 3, 2633),
    ("especially", 4, 2287), ("manner", 5, 2183), ("person", 6, 2162),
    ("small", 7, 1709), ("usually", 8, 1587), ("act", 9, 1469),
    ("form", 10, 1419), ("state", 11, 1398), ("cause", 12, 1302),
    ("plant", 13, 1170), ("quality", 14, 1074), ("body", 15, 1048),
    ("large", 16, 1042), ("flower", 17, 1041), ("part", 18, 986),
    ("resemble", 19, 966), ("consist", 20, 929), ("two", 21, 917),
    ("leave", 22, 848), ("lack", 23, 836), ("time", 24, 836),
    ("give", 25, 824), ("leaf", 26, 823), ("long", 27, 773),
    ("water", 28, 708), ("genus", 29, 700), ("place", 30, 694),
    ("produce", 31, 692), ("characterize", 32, 676), ("contain", 33, 675),
    ("color", 34, 662), ("animal", 35, 637), ("cover", 36, 631),
    ("capable", 37, 626), ("characteristic", 38, 614), ("mark", 39, 609),
    ("number", 40, 608), ("take", 41, 608), ("tree", 42, 608),
    ("property", 43, 599), ("light", 44, 593), ("white", 45, 593),
    ("order", 46, 582), ("unit", 47, 578), ("various", 48, 568),
    ("very", 49, 567), ("sound", 50, 566), ("shape", 51, 563),
    ("move", 52, 560), ("blood", 53, 556), ("group", 54, 553),
    ("woman", 55, 543), ("occur", 56, 535), ("work", 57, 533),
    ("result", 58, 519), ("point", 59, 511), ("people", 60, 509),
    ("surface", 61, 506), ("hold", 62, 502), ("process", 63, 497),
    ("equal", 64, 493), ("name", 65, 490), ("position", 66, 486),
    ("substance", 67, 471), ("feel", 68, 465), ("show", 69, 465),
    ("head", 70, 452), ("action", 71, 449), ("change", 72, 434),
    ("disease", 73, 433), ("food", 74, 433), ("skin", 75, 433),
    ("yellow", 76, 433), ("north", 77, 429), ("cell", 78, 426),
    ("word", 79, 423), ("involve", 80, 420), ("line", 81, 420),
    ("side", 82, 420), ("fruit", 83, 418), ("fish", 84, 417),
    ("provide", 85, 417), ("wear", 86, 416), ("low", 87, 415),
    ("live", 88, 413), ("liquid", 89, 411), ("play", 90, 411),
    ("red", 91, 411), ("force", 92, 409), ("short", 93, 409),
    ("become", 94, 408), ("write", 95, 405), ("branch", 96, 402),
    ("treat", 97, 398), ("good", 98, 397), ("unite", 99, 396),
    ("high", 100, 394), ("term", 101, 391), ("condition", 102, 384),
    ("system", 103, 384), ("material", 104, 382), ("mean", 105, 381),
    ("end", 106, 377), ("power", 107, 374), ("open", 108, 371),
    ("degree", 109, 369), ("grow", 110, 368), ("serve", 111, 368),
    ("money", 112, 366), ("study", 113, 366), ("base", 114, 365),
    ("things", 115, 356), ("tissue", 116, 355), ("activity", 117, 350),
    ("area", 118, 348), ("new", 119, 347), ("express", 120, 341),
    ("common", 121, 340), ("drug", 122, 338), ("trade", 123, 338),
    ("tropical", 124, 338), ("structure", 125, 336), ("remove", 126, 334),
    ("control", 127, 332), ("same", 128, 331), ("follow", 129, 330),
    ("bird", 130, 326), ("instrument", 131, 325), ("life", 132, 321),
    ("particular", 133, 320), ("compound", 134, 319), ("support", 135, 319),
    ("bear", 136, 318), ("hair", 137, 318), ("member", 138, 315),
    ("wood", 139, 312), ("shrub", 140, 310), ("hand", 141, 308),
    ("hard", 142, 306), ("found", 143, 305), ("way", 144, 304),
    ("put", 145, 303), ("great", 146, 302), ("strong", 147, 296),
    ("air", 148, 294), ("human", 149, 294), ("value", 150, 294),
    ("build", 151, 293), ("eye", 152, 292), ("piece", 153, 291),
    ("come", 154, 290), ("certain", 155, 289), ("amount", 156, 287),
    ("physical", 157, 286), ("metal", 158, 281), ("cut", 159, 280),
    ("foot", 160, 280), ("object", 161, 279), ("region", 162, 276),
    ("set", 163, 276), ("carry", 164, 275), ("acid", 165, 270),
    ("only", 166, 270), ("man", 167, 266), ("black", 168, 265),
    ("seed", 169, 264), ("own", 170, 263), ("measure", 171, 262),
    ("thin", 172, 261), ("source", 173, 260), ("perform", 174, 259),
    ("quantity", 175, 259), ("bring", 176, 258), ("event", 177, 256),
    ("soft", 178, 256), ("organism", 179, 255), ("period", 180, 252),
    ("different", 181, 250), ("free", 182, 250), ("design", 183, 249),
    ("direction", 184, 248), ("heat", 185, 248), ("movement", 186, 248),
    ("edible", 187, 247), ("information", 188, 247), ("child", 189, 246),
    ("ground", 190, 246), ("kind", 191, 246), ("face", 192, 244),
    ("effect", 193, 242), ("excessive", 194, 242), ("herb", 195, 242),
    ("game", 196, 241), ("land", 197, 241), ("muscle", 198, 241),
    ("function", 199, 240), ("sexual", 200, 240),
)


# ------------------------------------------------------------------------------------------------
# the rows
# ------------------------------------------------------------------------------------------------


def derive_structural_seeds(k: int = STRUCTURAL_K, progress=None) -> tuple[tuple[str, int, int], ...]:
    """Re-derive `STRUCTURAL_SEEDS` from the resource — THE code path, not a second one.

    nltk and the WordNet corpus are needed and are imported here rather than at module scope: a
    migration that could not be read on a machine without a corpus would be a migration whose values
    nobody can inspect. `progress` is passed straight to `build_digraph` because this takes minutes
    and a silent minute looks like a hang.
    """
    from tk2.dictionary import closure, proposal
    from tk2.dictionary.wordnet import WordNetProvider, wordnet_lexicon

    provider = WordNetProvider(wordnet_lexicon())
    graph = closure.build_digraph(provider, standing_closure(), progress)
    ranking = proposal.structural_ranking(graph, provider, CLOSED_CLASS_FORMS)

    clean = [c for c in ranking if c.is_candidate]
    rank_of = {c.word: (i, c.in_degree) for i, c in enumerate(clean, 1)}
    return tuple((word, *rank_of[word]) for word in proposal.structural_seeds(ranking, k))

def up(writer, db) -> None:
    # The shape first: collections, indexes and the timeseries configuration, taken from the models
    # themselves so there is one source of truth for the schema. BASE_MODELS is included because the
    # build must find its collections already made — a build that created them would be a build
    # doing a deploy's job.
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(ParamDoc, PARAM_ROWS)
    writer.insert_many(HeartAnatomyDoc, ANATOMY_ROWS)
    writer.insert_many(ClosedClassDoc, CLOSED_CLASS_ROWS)

    # The whole policy ledger, all nine versions. Not just the newest: a manifest row recording an
    # older version's fingerprint has to point at something a reader can still read.
    writer.insert_many(DictionaryPolicyDoc, POLICY_ROWS)
    writer.insert_many(DictionaryBarDoc, BAR_ROWS)

    # The newborn's heart. Every pole gets a level row because the first tick reads them, and a tick
    # that has to cope with a missing pole is a tick that has to guess what «missing» means.
    writer.insert_many(HeartLevelDoc, [{"pole": pole, "level": 0.0} for pole in ALL_POLES])
    writer.insert_many(HeartMoodDoc, [{"pole": pole, "value": 0.0} for pole in SPHERE_POLES])
    writer.insert_many(
        HeartTemperamentDoc, [{"pole": pole, "baseline": 0.0} for pole in SPHERE_POLES]
    )
