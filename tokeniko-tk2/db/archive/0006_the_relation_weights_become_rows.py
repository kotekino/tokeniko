"""0006 — policy version 3: R's weights become rows, and the alphabet travels with them.

The standing law of 2026-08-25 named this one in advance: «the relation weights you write in T3 —
they land as rows from the start, never as a table in `config.py`». They are curation by both tests
— changing a weight changes what the rows SAY and not the shape of anything, and evidence revises
them the first time the bar disagrees — so `tk2/dictionary/config.py` holds `RelationPolicy`, which
is a shape with no values in it, and this file holds the values.

**VERSION 3 IS A NEW SET OF ROWS.** v1 and v2 stay exactly where they are: `dictionary_policy` is a
LEDGER, and a manifest row recording either must keep naming something a later reader can still
read. Nothing below edits, retires or deletes an older row.

WHAT IS IN IT, and what argued for each:

  1. **THE MINED WEIGHTS** — nineteen relations, carried VERBATIM from the prototype's `WEIGHTS`
     (`scripts/tk2/tk2_config.py`), signs included, in the order its cell walk evaluated them. The
     order is now load-bearing rather than incidental: `position` is the PRECEDENCE two equally
     strong relations are resolved by, so a rebuild cannot flip a cell's provenance by iteration
     luck. Two of the prototype's twenty-one entries are NOT here: `gloss_overlap`, which is
     co-occurrence and therefore D's whole job (T4 declares it), and `wup` — dropped from BOTH
     matrices, because it is not a named edge (it fails R's provenance criterion: `wup` names a
     SCORE OVER the taxonomy, not a relation between two words) and it is not co-occurrence (it
     fails D's). Recoverable later as its own graded-taxonomy layer if a question needs it.
  2. **THE CURATED VOCABULARY** — the six relations a DEFINITION can state, and the reciprocal
     weight of 0.60, from the Captain's ruling of 2026-08-12 (requirement 20). A separate `kind`
     from the mined weights because `entails` is in both: the same claim from two provenances, which
     is the prototype's own choice and must not collapse into one row.
  3. **THE MINER'S GUESS** — the cue words and the POS-pair fallback that pick WHICH curated
     relation a gloss looks like it is stating. Rows because they are a list, and the standing law
     is unambiguous about lists. **Reported at dispatch as a question rather than a settlement:** a
     cue-word table is arguably category THREE («right for the words someone thought of and silently
     wrong for every other»), and the honest long-run answer is geometry deciding what a gloss
     states. It is carried across verbatim so that nothing is invented while it waits for that
     ruling, and every proposal it produces is pending until the Captain relabels or rejects it.
  4. **THE ALPHABET** — `POS_ORDER`, ruled by the Captain on 2026-08-25 to travel with the policy
     rows: it is WordNet's answer about English rather than the key grammar, and what stays in code
     is that a key IS word-plus-POS. It was ruled before v2 shipped and v2 shipped without it, so it
     folds in here rather than costing a migration of its own for one line.

**WHAT DID NOT MOVE.** The seeds, the closure cuts and the bar. The seed and closure rows below are
`db/0005`'s own — read off that file's declaration and re-stamped at version 3, notes and all —
because a policy version must be a WHOLE policy (a build reads one version) and re-typing 224 seeds
to carry them forward is how a transcription error enters a ledger.

**THE CONFIG FINGERPRINT MOVES, and that is the mechanism working.** v3 declares strictly more than
v2 did, so it is a different policy and hashes differently. v1's and v2's own fingerprints are
untouched — `DictionaryConfig.as_dict` writes nothing about relations or the alphabet when a policy
declared neither, precisely so that an older manifest row keeps meaning what it meant.

**NOT APPLIED BY THE OFFICER.** This file is written and reported; the apply is the Captain's hand.
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, DictionaryPolicyDoc
from tk2.dictionary import keys, policy
from tk2.dictionary.config import DictionaryConfig, RelationPolicy
from tk2.migrations import ensure_collections

POLICY_VERSION = 3


def _version_2():
    """`db/0005`, loaded as the runner loads it — the seeds and the cuts read off the file that
    declared them rather than copied beside it. Same move 0005 made on 0004's closed classes."""
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 5), None)
    if found is None:
        raise RuntimeError("migration 0005 is gone — it holds the seeds version 3 carries forward")
    return found.load()


V2 = _version_2()


# ------------------------------------------------------------------------------------------------
# 1 — the mined weights: every named WordNet relation R fills a cell with
# ------------------------------------------------------------------------------------------------

#: `(relation, weight, family)`, in the order the cell walk evaluates them — which is what
#: `position` records and what a tie is resolved by. Signs are the prototype's: the ONE negative
#: weight is antonymy, and the sign is the antonym column-read primitive (`row[X][index(W)] < 0`)
#: rather than a convention about badness.
MINED_WEIGHTS = (
    ("identity", 1.0, "axis"),
    ("synonym", 1.0, "lexical"),
    ("antonym", -1.0, "lexical"),
    ("derivational", 0.9, "lexical"),
    ("entails", 0.8, "verb"),
    ("causes", 0.85, "verb"),
    ("troponym", 0.7, "verb"),
    ("hyponym_1", 0.7, "taxonomy"),
    ("hypernym_1", 0.7, "taxonomy"),
    ("hypernym_2", 0.5, "taxonomy"),
    ("verb_group", 0.75, "verb"),
    ("similar_to", 0.8, "adjective"),
    ("attribute", 0.7, "adjective"),
    ("also_see", 0.5, "adjective"),
    ("meronym", 0.6, "part"),
    ("holonym", 0.6, "part"),
    ("entailed_by", 0.6, "verb"),
    ("caused_by", 0.6, "verb"),
    ("troponym_of", 0.7, "verb"),
)

#: The prototype's own comment on each, kept as the row's reason. A curated value with no reason
#: attached is a value nobody can later argue with (`ParamDoc.note`'s argument).
MINED_NOTES = {
    "identity": "X is X — the diagonal. A matrix whose diagonal is zero has no self-similarity and "
                "its cosines stop meaning what they look like",
    "synonym": "a shared synset: the same sense speaks for both dimensions",
    "antonym": "lemma antonym — THE negative weight, and the sign IS the antonym column-read "
               "primitive. Answered before every relation but synonymy, so a pair that is also "
               "taxonomically close still reads as opposed",
    "derivational": "able -> ability. Cross-POS by nature, which is half of why the base splits by "
                    "part of speech at all",
    "entails": "eat -> chew, swallow (verb). One of the relations the Jurassic build could never "
               "produce — the point of the whole review",
    "causes": "kill -> die (verb). The strongest claim in the table after identity and synonymy",
    "troponym": "eat -> devour, slurp. A verb's hyponym is a MANNER-OF, which is a different "
                "relation from a noun's hyponym and gets its own name and weight",
    "hyponym_1": "the taxonomy downward, one step: dog -> puppy",
    "hypernym_1": "the taxonomy upward, one step. `instance_hypernyms` are folded in — the "
                  "distinction they draw is about NAMES, which the base does not contain (option C)",
    "hypernym_2": "two steps up, and weaker for it: a grandparent is a real relation and a vaguer one",
    "verb_group": "eat.v.01 <-> eat.v.02 — WordNet's own statement that two readings of a verb "
                  "belong together",
    "similar_to": "hungry -> peckish, famished (adjective satellite)",
    "attribute": "hot <-> temperature (adjective <-> noun). Cross-POS by nature, like `derivational`",
    "also_see": "the weakest named edge WordNet states, and it says so: see also",
    "meronym": "part / member / substance — the three read as one relation, because the difference "
               "between them is a claim R is not making yet",
    "holonym": "the whole, read from the part",
    "entailed_by": "the reverse read of `entails`. The relation is DIRECTIONAL, so «Y entails X» is "
                   "its own, weaker cell rather than a mirror of the forward one",
    "caused_by": "the reverse read of `causes`, on the same argument",
    "troponym_of": "the reverse read of `troponym` — and equal to it, because «X is a manner of Y» "
                   "and «Y has X as a manner» are the same strength of claim in opposite directions",
}


# ------------------------------------------------------------------------------------------------
# 2 — the curated vocabulary: what a DEFINITION may state (requirement 20)
# ------------------------------------------------------------------------------------------------

#: THE CLOSED SET of curated relation names, with the weight each proposal carries. Closed on
#: purpose: a curator who may invent a relation name per edge is writing prose, not a matrix. Every
#: one of these is a relation a definition can state; none of them is a similarity score.
CURATED_WEIGHTS = (
    ("used_for", 0.80),
    ("site_of", 0.70),
    ("involves", 0.75),
    ("entails", 0.80),
    ("causes", 0.85),
    ("state_of", 0.80),
)

CURATED_NOTES = {
    "used_for": "X's gloss states X's PURPOSE is Y — bed -> sleep, «a piece of furniture that "
                "provides a place to sleep»",
    "site_of": "X's gloss states X is the PLACE where Y happens",
    "involves": "X's gloss names Y as a PARTICIPANT of X — eat -> food. The weakest claim and the "
                "miner's fallback: it says only «the definition names it», which is the one thing "
                "the miner actually observed",
    "entails": "X's gloss states Y necessarily happens when X does. Deliberately the same name as "
               "the WordNet edge: same claim, different provenance — and the cell says which",
    "causes": "X's gloss states X brings Y about",
    "state_of": "X's gloss states X is the CONDITION attached to Y — hungry -> eat",
}

#: THE RECIPROCAL CELL — the Captain's ruling of 2026-08-12: «agree on the reciprocal 0.60, approve
#: both edges».
RECIPROCAL_WEIGHT = 0.60

RECIPROCAL_NOTE = (
    "the back-reference a curated edge writes. Measured BEFORE the ruling: written one way only, "
    "sleep.v~bed.n reaches 0.217 and eat.v~hungry.a 0.193 — both under the 0.30 NEAR floor, so the "
    "stated-relation read passes while the cosine read still misses. At 0.60 they reach 0.353 and "
    "0.329 and both reads close. The value is not invented: it is R's own existing convention "
    "(entails 0.80 / entailed_by 0.60, causes 0.85 / caused_by 0.60), so a curated edge is shaped "
    "like the edges it sits beside"
)

# ------------------------------------------------------------------------------------------------
# 3 — the miner's guess, and why it is rows rather than code
# ------------------------------------------------------------------------------------------------

#: How the miner GUESSES which of the six a gloss is stating. Cues are tried IN THIS ORDER, so a
#: gloss that is both purposive and locative («provides a place to sleep») reads as purpose — which
#: is how the Captain himself quoted it («a piece of furniture ... for sleeping»).
CURATION_CUES = (
    ("causes", ("cause", "causes", "make", "makes", "bring", "brings", "result", "results", "produce")),
    ("used_for", ("for", "used", "use", "provides", "provide", "designed", "intended", "serves", "so")),
    ("site_of", ("place", "where", "area", "surface", "room", "space", "site", "location")),
)

#: ...and when no cue fires, the POS pair decides. `(source POS, target POS, relation)`.
CURATION_DEFAULTS = (
    ("a", "v", "state_of"),   # an adjective's gloss naming an act names the condition around it
    ("a", "n", "state_of"),
    ("v", "v", "entails"),    # a verb defined through another verb states what the act consists of
    ("n", "v", "used_for"),
    ("v", "n", "involves"),
    ("n", "n", "involves"),
)

GUESS_NOTE = (
    "the miner's GUESS at which curated relation a gloss states, carried verbatim from the "
    "prototype. A guess and never a claim: every proposal is pending until the Captain relabels or "
    "rejects it. Surfaced at T3 as an open question rather than a settlement — a cue-word list is "
    "arguably a category-3 set (right for the words someone thought of, silently wrong for every "
    "other), and the long-run answer is the geometry deciding what a definition states"
)


# ------------------------------------------------------------------------------------------------
# 4 — the alphabet: which parts of speech exist
# ------------------------------------------------------------------------------------------------

#: WordNet's own four, in WordNet's own order — which is also the order a multi-POS word's keys are
#: listed in, so the dimension order stays a function of the word set alone. The satellite adjective
#: `s` is an ALIAS of `a`: a separate `s` dimension would split `hungry` from `famished` on a
#: distinction the lexicographer made about the synset rather than about the word.
#:
#: Typed out here rather than read off `keys.GRAMMAR_ALPHABET`, because this file is the
#: DECLARATION and reading the code would make the code the declaration again. The two are checked
#: against each other at `policy.config_from_rows` (`keys.assert_compiled`), so a future alphabet
#: that the key convention cannot honour stops a build instead of quietly minting keys nobody ruled.
ALPHABET = keys.Alphabet(
    order=("n", "v", "a", "r"),
    names=(("n", "noun"), ("v", "verb"), ("a", "adjective"), ("r", "adverb")),
    aliases=(("s", "a"),),
)

ALPHABET_NOTES = {
    "n": "noun — WordNet's first, and the dimension order's first",
    "v": "verb",
    "a": "adjective. WordNet's satellite `s` folds in here (see the `s` alias)",
    "r": "adverb",
    "s": "WordNet's satellite adjective. It is an ADJECTIVE — a separate `s` dimension would split "
         "`hungry` from `famished` on a distinction the lexicographer made about the synset, not "
         "about the word",
}


# ------------------------------------------------------------------------------------------------
# the rows
# ------------------------------------------------------------------------------------------------

RELATIONS = RelationPolicy(
    weights=tuple((name, weight) for name, weight, _family in MINED_WEIGHTS),
    curated=CURATED_WEIGHTS,
    reciprocal_weight=RECIPROCAL_WEIGHT,
    cues=CURATION_CUES,
    defaults=CURATION_DEFAULTS,
)

#: The whole policy v3, as the engine will receive it — assembled as an OBJECT and written out as
#: rows, for the reason 0003 and 0005 both gave: it is the one way to carry a set across a medium
#: without a transcription error, and it means `DECLARED.fingerprint()` is the fingerprint a build
#: will really record. The seeds, the cuts and the bar are v2's, unread and unedited.
DECLARED = DictionaryConfig(
    closure=V2.DECLARED.closure,
    declared_seeds=V2.DECLARED.declared_seeds,
    bar=policy.snapshot_bar(),
    relations=RELATIONS,
    alphabet=ALPHABET,
)

RELATION_FAMILY = {name: family for name, _weight, family in MINED_WEIGHTS}

# A relation named like a seed would take the seed's family and lose its own. It cannot happen with
# these two sets and it is asserted rather than hoped, because the day it does happen the row would
# still be written and would simply say the wrong thing.
_COLLISION = sorted(set(V2.FAMILY_OF) & set(RELATION_FAMILY))
if _COLLISION:
    raise RuntimeError(f"a relation and a seed share a name: {_COLLISION}. One of them would lose its family.")

FAMILY_OF = {**V2.FAMILY_OF, **RELATION_FAMILY}

POLICY_ROWS = policy.policy_rows_of(DECLARED, POLICY_VERSION, FAMILY_OF)

#: v2's reasons, carried with v2's values. A row that arrived at version 3 with its note dropped
#: would be a curated decision that lost the argument for itself on the way across.
_CARRIED_NOTES = {(row["kind"], row["name"]): row["note"] for row in V2.POLICY_ROWS}

_NEW_NOTES = {
    **{(policy.KIND_RELATION_WEIGHT, name): note for name, note in MINED_NOTES.items()},
    **{(policy.KIND_CURATED_RELATION, name): note for name, note in CURATED_NOTES.items()},
    (policy.KIND_CURATION, "reciprocal_weight"): RECIPROCAL_NOTE,
    **{(policy.KIND_CURATION_CUE, name): GUESS_NOTE for name, _cues in CURATION_CUES},
    **{
        (policy.KIND_CURATION_DEFAULT, f"{source}{policy.POS_PAIR_SEPARATOR}{target}"): GUESS_NOTE
        for source, target, _relation in CURATION_DEFAULTS
    },
    **{(policy.KIND_POS, letter): ALPHABET_NOTES[letter] for letter in ALPHABET.order},
    **{(policy.KIND_POS_ALIAS, spelling): ALPHABET_NOTES[spelling] for spelling, _l in ALPHABET.aliases},
}

for _row in POLICY_ROWS:
    _key = (_row["kind"], _row["name"])
    # A KeyError here is the point: every row of a curated policy explains itself, and a new kind
    # that arrived without a reason should fail at import rather than reach the database mute.
    _row["note"] = _CARRIED_NOTES[_key] if _key in _CARRIED_NOTES else _NEW_NOTES[_key]


# ------------------------------------------------------------------------------------------------
# what 0005 knew, still readable from the newest policy file
# ------------------------------------------------------------------------------------------------
#
# `tools/propose_seeds.py` finds the migration declaring the NEWEST policy version and asks it to
# re-derive its structural seeds. That file is now this one, and the derivation has not moved — so
# it is re-exported rather than re-implemented. A second copy of a derivation is how two answers to
# one question get born.

STRUCTURAL_K = V2.STRUCTURAL_K
STRUCTURAL_SEEDS = V2.STRUCTURAL_SEEDS
derive_structural_seeds = V2.derive_structural_seeds


def up(writer, db) -> None:
    # The base's own collections are created here, empty: `tools/build_dictionary.py --apply` fills
    # them, and a build that had to create its own tables would be a build doing a deploy's job.
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(DictionaryPolicyDoc, POLICY_ROWS)
