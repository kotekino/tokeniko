"""0005 — the dictionary's policy at version 2: the seeds ruled, the size cap demoted to a rail.

0003 moved the policy into rows WITHOUT touching a value, so that the Captain could rule on the
values themselves against a measurement rather than against a memory. He ruled on 2026-08-25, on the
numbers `tools/propose_seeds.py` measured, and this is that ruling written down.

**VERSION 2 IS A NEW SET OF ROWS.** Version 1 stays exactly where it is: `dictionary_policy` is a
LEDGER, and a manifest row recording policy v1 must keep naming something a later reader can still
read. Nothing below edits, retires or deletes a v1 row.

WHAT MOVED, and what argued for it:

  1. THE SEEDS ARE **PURPOSE ∪ STRUCTURE** — two sources, labelled per row, because they are
     approved under different eyes. PURPOSE is requirement 8's declared families (an argument about
     what this being must be able to think about, which no measurement can make and none can
     refute); STRUCTURE is the definitional core by in-degree over the whole definition digraph (the
     resource arguing for itself: the words WordNet writes its definitions with are the words the
     base cannot do without). `family` carries which one, so a seed can later be approved or retired
     under the eyes that put it there.
  2. THE IDENTITY FAMILY LOST ITS FUNCTION WORDS. `me` and `you` are indexical — a pronoun resolves
     to an ENTITY before the dictionary is consulted — and `not` and `be` are pure structure, which
     compiles (the second standing law of 2026-08-25: content is defined, structure is compiled).
     What replaces them is the CONCEPT each of them is not: `negation` (the thing he reasons about,
     where `not` is the thing he says) and `being` («the state or fact of existing»), a real noun
     with its own gloss, admitted as the argued exception to the de-inflection guard.
  3. `max_size` 400 → **25,000, AND IT STOPPED BEING A DESIGN KNOB.** See its note below: the
     measurement showed a cap does not trim a base, it deletes a whole ring of one — so the depth
     cut is the policy and the cap is a runaway guard.

**WHAT DID NOT MOVE.** The depth cut (2), the sense mode (`primary`) and the bar. The bar is a
separate table and is APPEND-mostly; version 2 of the policy is measured against bar v1 exactly as
version 1 was, and the eighteen pairs are read here (via the offline snapshot) rather than restated,
so `DECLARED` below is the whole policy a build will run and not a fragment of it.

**NOT APPLIED BY THE OFFICER.** This file is written and reported; the apply is the Captain's hand.

------------------------------------------------------------------------------------------------
HOW THE 200 STRUCTURAL SEEDS WERE DERIVED — reproducible, and re-runnable from this repo
------------------------------------------------------------------------------------------------

`STRUCTURAL_SEEDS` below is a materialised list, and a materialised list that cannot be regenerated
is a paste. `derive_structural_seeds()` in this file IS the derivation — the same functions
`tools/propose_seeds.py` calls, in the same order. Two things run it: the GATE
(`tests/test_dictionary_proposal.py`, marked `wordnet`, ~7s for the whole 68,779-word digraph) and
`tools/propose_seeds.py --verify`, which re-derives, diffs, and then rebuilds the base so the
numbers the ruling was made on can be reproduced in one command. If the list and the derivation ever
disagree, they disagree out loud.

The derivation, stated so it can be argued with:

  - THE GRAPH: `closure.build_digraph` over `wordnet_lexicon()` — every single-word WordNet lemma of
    two characters or more that is not a name-only spelling (option C) — under THESE closure cuts,
    i.e. `senses="primary"`. Measured 2026-08-25: 68,779 nodes · 469,620 edges · 11 silent.
  - THE RANKING NUMBER: in-degree. How many of the lexicon's definitions name the word.
  - THE ORDER: `Counter.most_common`, whose ties fall back to insertion order, over a lexicon that
    is sorted — so words with equal in-degree rank alphabetically. It matters at the boundary: the
    200th seed sits among a run of words all named by 240-odd definitions.
  - THE TWO EXCLUSIONS: the closed classes (migration 0004's single-word forms — by PRINCIPLE, a
    function word never asks the dictionary a question) and the de-inflection guard
    (`proposal.inflection_of` — `used`, `are`, `made`, `lacking`, `marked`, `being` rank on grammar
    somebody else earned). Excluded words are labelled in the ranking, never dropped silently.
  - THE CUT: `proposal.structural_seeds(ranking, k)` with **k = 200**, the Captain's ruling. `k`
    counts CANDIDATES, so this is 200 seeds and not 200 rows of which half were function words.

SEVEN WORDS ARE IN BOTH SOURCES — `leave` (#22), `move` (#52), `food` (#74), `same` (#128), `come`
(#154), `different` (#181), `land` (#197) — which is the two arguments agreeing and is worth seeing.
A form cannot hold two rows in one version (the unique index says so, and rightly), so the purpose
row wins and its note records the structural rank as well: the word keeps both arguments, and the
seed SET is the union either way. That is why there are 224 seed rows and not 231.
"""

from tk2.core.models import ALL_MODELS, LEDGER_MODELS, DictionaryPolicyDoc
from tk2.dictionary import policy
from tk2.dictionary.config import ClosurePolicy, DictionaryConfig
from tk2.migrations import ensure_collections

POLICY_VERSION = 2

# ------------------------------------------------------------------------------------------------
# SOURCE 1 — PURPOSE: requirement 8's families, as the Captain ruled them on 2026-08-25
# ------------------------------------------------------------------------------------------------

# Closure alone will happily return a clique of function words. These force the verbs that select
# actions into every subset, whatever the definition digraph happens to feel like doing.
#
# `volitional`, `motion` and `effect` are v1's, word for word. `identity` is the one that moved: it
# was `me you not negation be same different` and it is now the four words of it that are DICTIONARY
# business — see the head of this file.
PURPOSE_FAMILIES = {
    "volitional": ("want", "must", "try", "decide", "choose", "need", "wish", "intend", "refuse"),
    "motion": ("go", "come", "walk", "run", "enter", "arrive", "leave", "land", "fall", "move"),
    "effect": ("eat", "food", "hungry", "sleep", "tired", "bed", "drink", "thirsty"),
    "identity": ("negation", "being", "same", "different"),
}

PURPOSE_SEEDS = tuple(word for family in PURPOSE_FAMILIES.values() for word in family)

PURPOSE_FAMILY_OF = {word: family for family, words in PURPOSE_FAMILIES.items() for word in words}

# ------------------------------------------------------------------------------------------------
# SOURCE 2 — STRUCTURE: the definitional core, by in-degree
# ------------------------------------------------------------------------------------------------

#: The family name a structural seed carries. It is not one of requirement 8's four and must not
#: pretend to be: those say WHAT this being must be able to think about, this one says the resource
#: cannot define anything without the word.
STRUCTURE = "structure"

#: The Captain's cut, 2026-08-25. At 200 the base lands at 3,095 words / 4,445 keys with the bar
#: 23/23 inside it; at 100 it was 2,389 and at 400 it was 3,855, so this is a chosen point on a
#: smooth curve and not the edge of a cliff.
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
# THE CLOSURE CUTS
# ------------------------------------------------------------------------------------------------

CLOSURE = ClosurePolicy(max_depth=2, max_size=25_000, senses="primary")

# ------------------------------------------------------------------------------------------------
# the rows
# ------------------------------------------------------------------------------------------------

#: The union, purpose first. A word both sources argued for appears ONCE — see the head of the file.
DECLARED_SEEDS = PURPOSE_SEEDS + tuple(
    word for word, _rank, _degree in STRUCTURAL_SEEDS if word not in PURPOSE_SEEDS
)

FAMILY_OF = {
    **{word: STRUCTURE for word, _rank, _degree in STRUCTURAL_SEEDS},
    # Second, so it wins: a word both sources argued for keeps the family that says WHY it is
    # wanted, and its structural rank is recorded in the note instead of overwriting the reason.
    **PURPOSE_FAMILY_OF,
}

STRUCTURAL_RANK = {word: (rank, degree) for word, rank, degree in STRUCTURAL_SEEDS}

#: The whole policy v2, as the engine will receive it. Assembled as an OBJECT and written out as
#: rows, rather than the rows being typed beside it, for the reason 0003 gave: it is the one way to
#: carry a set across a medium without a transcription error, and it means `DECLARED.fingerprint()`
#: is the fingerprint a build will really record.
#:
#: The bar is READ (from its pinned snapshot: v1, the eighteen pairs) and not restated. A second
#: copy of the pairs here would be a second declaration of them, and a `BAR_VERSION = 1` beside it
#: would be a third — a number in this file that the day the bar grows could only be wrong. What
#: `up()` writes does not depend on the bar at all; this object does, because a build's config
#: fingerprint covers policy AND bar together, and that is the number it must agree with.
DECLARED = DictionaryConfig(
    closure=CLOSURE,
    declared_seeds=DECLARED_SEEDS,
    bar=policy.snapshot_bar(),
)

POLICY_ROWS = policy.policy_rows_of(DECLARED, POLICY_VERSION, FAMILY_OF)

#: The notes are the reasons the rows exist, in the medium the rows have for them. A curated value
#: with no reason attached is a value nobody can later argue with (`ParamDoc.note`'s argument).
CLOSURE_NOTES = {
    "max_depth": "THE POLICY. How many rings the seed closure expands, and the number that decides "
                 "how big the base is. At 2 the word `right` sits exactly one ring outside the "
                 "subset — see SeedClosure.one_ring_past",
    "max_size": "A RUNAWAY GUARD, NOT A DESIGN KNOB (the Captain, 2026-08-25). A ring is admitted "
                "whole or not at all, so a cap does not trim a base — it deletes the last ring of "
                "one. Measured: under the old cap of 400, seeding the top 50 structural words gave "
                "588 words, SMALLER than the 1,208 that seeding nothing structural at all gave, "
                "because the extra seeds made the last ring too big to admit. A number that makes "
                "a base shrink when you add seeds to it is not a design knob. Set far above any "
                "intended base (3,095 words), so it can only ever catch a runaway",
    "senses": "which senses of a word contribute its definition — `primary` (first synset per POS, "
              "what the Jurassic build used) or `all` (denser, noisier)",
}

for _row in POLICY_ROWS:
    if _row["kind"] == policy.KIND_CLOSURE:
        _row["note"] = CLOSURE_NOTES[_row["name"]]
    elif _row["family"] == STRUCTURE:
        _rank, _degree = STRUCTURAL_RANK[_row["name"]]
        _row["note"] = (
            f"seed, structural — #{_rank} of the cleaned in-degree ranking, named by {_degree:,} "
            f"of the lexicon's definitions"
        )
    else:
        _row["note"] = f"seed, {_row['family']} family — requirement 8: in scope by construction"
        if _row["name"] in STRUCTURAL_RANK:
            _rank, _degree = STRUCTURAL_RANK[_row["name"]]
            _row["note"] += (
                f" · structure argued for it too: #{_rank} of the cleaned ranking, {_degree:,} "
                f"definitions name it"
            )


# ------------------------------------------------------------------------------------------------
# the derivation, re-runnable
# ------------------------------------------------------------------------------------------------


def _closed_class_forms() -> tuple[str, ...]:
    """Migration 0004's single-word forms — the exclusion by PRINCIPLE, read off the file that
    writes them so the derivation can be re-run before the Captain's hand has applied it."""
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 4), None)
    if found is None:
        raise RuntimeError("migration 0004 is gone — the closed classes are half of the derivation")
    return tuple(found.load().FORMS)


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
    graph = closure.build_digraph(provider, CLOSURE, progress)
    ranking = proposal.structural_ranking(graph, provider, _closed_class_forms())

    clean = [c for c in ranking if c.is_candidate]
    rank_of = {c.word: (i, c.in_degree) for i, c in enumerate(clean, 1)}
    return tuple((word, *rank_of[word]) for word in proposal.structural_seeds(ranking, k))


def up(writer, db) -> None:
    # 0003 made these tables; a database that somehow reaches 0005 without them is a database whose
    # next line would fail more confusingly than this one.
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS])

    writer.insert_many(DictionaryPolicyDoc, POLICY_ROWS)
