"""POLICY AS ROWS — the mechanism, the ledger, and the one number that says nothing changed.

Three things under test, in the order they matter:

  1. THE MOVE COST NOTHING. Migration 0003's rows rebuild the policy `config.py` used to declare,
     and it fingerprints to `79fdfa9c…` — the hash the base was measured under at `1e7cad3`
     (68,779 lexicon words -> 1,220 closure words -> 1,868 keys). Run offline, with no database and
     no WordNet, because the claim is about VALUES crossing a medium and neither is needed to check
     it.
  2. THE MECHANISM, on rows written here rather than on the standing ones — an incomplete policy is
     refused, an unknown setting is refused, a retired pair leaves the bar and stays in the ledger,
     and both fingerprints move when what they cover moves.
  3. THE SNAPSHOT CANNOT DRIFT. Reading it verifies its own pin offline; a live check asserts it
     against the database's rows whenever a database is reachable.
  7. AN INFERRED OPPOSITION is admitted (policy v5): the reading `add_only` and the relation it
     mints, two rows and one decision.
  6. WHOSE LEMMA MAY SPEAK is a row too (T3 addendum, policy v4) — the Captain's ruling of
     2026-08-26, with the measurement that produced it carried in the row's own reason.
  5. R's WEIGHTS ARE ROWS TOO (T3, policy v3) — the standing law's own worked example, with the
     curated vocabulary, the miner's guess and the alphabet beside them, and the older versions
     hashing exactly as they did.
  4. THE RULING IS IN THE ROWS. Migration 0005's version 2 — purpose ∪ structure, the size cap
     demoted to a rail — with version 1 still reading back as what T2b measured beside it. That the
     200 structural seeds really are the ranking's top 200 needs the whole digraph and is checked
     next door, in `tests/test_dictionary_proposal.py`.
"""

import json

import pytest

from tests.seed import (
    bar_rows,
    closed_class_forms,
    declared_config,
    declared_config_v3,
    declared_config_v4,
    declared_config_v5,
    policy_rows,
    policy_rows_v2,
    policy_rows_v3,
    policy_rows_v4,
    policy_rows_v5,
    ruled_config,
    structural_seeds,
)
from tk2.dictionary import keys as keys_module
from tk2.dictionary import policy
from tk2.dictionary.config import BarPair, ClosurePolicy, DictionaryConfig

#: The policy fingerprint of the base as it stood at `1e7cad3` (E1 T2b), before the values moved
#: into rows. It is written down here and nowhere else: this is the regression the whole task is
#: measured by, and a constant a reader can find is worth more than one derived from the thing under
#: test. If REDUCTION_RULES is ever bumped this number moves WITH it — that is the mechanism
#: working, and updating it is a deliberate act with the reason recorded in the commit.
T2B_FINGERPRINT = "79fdfa9c9f20d8330b7c1ed8c751bd8896fe0efa0b3097324f1c8ccdaa23e526"


# ------------------------------------------------------------------------------------------------
# 1 — the move cost nothing
# ------------------------------------------------------------------------------------------------


def test_the_migrated_rows_rebuild_the_policy_T2b_measured():
    """THE property of T4b, in one assertion. The rows are a different medium for the same values,
    so the hash the engine takes over them must be the same hash — a build after the move and a
    build before it are comparable, which is the only thing the manifest ever claimed."""
    rebuilt = policy.config_from_rows(policy_rows(), bar_rows())
    assert rebuilt.fingerprint() == T2B_FINGERPRINT
    assert rebuilt == declared_config(), "the rows must rebuild the declaration, not merely hash like it"


def test_the_migrated_values_are_the_ones_that_were_declared():
    """Said again as VALUES rather than as a hash, because a hash tells you that something moved and
    never what. These are the numbers the Captain rules on next, and they must reach him unedited."""
    rebuilt = policy.config_from_rows(policy_rows(), bar_rows())
    assert rebuilt.closure == ClosurePolicy(max_depth=2, max_size=400, senses="primary")
    assert len(rebuilt.declared_seeds) == 34
    assert rebuilt.declared_seeds[:3] == ("want", "must", "try")
    assert rebuilt.declared_seeds[-1] == "different"
    assert len(rebuilt.bar) == 18
    assert rebuilt.bar[0] == BarPair(
        "eat.v", "food.n", "NEAR",
        "the Captain's line: eat and food are geometrically similar, do not lose it",
    )
    assert len(rebuilt.seeds) == 41       # the declared 34, plus the bar's own words


def test_every_seed_row_carries_the_family_that_argued_for_it():
    """Requirement 8's families are the REASON those words are seeded. A flat word list would have
    kept the seeds and lost the argument, which is the half a later reader needs."""
    seeds = [r for r in policy_rows() if r["kind"] == policy.KIND_SEED]
    assert {r["family"] for r in seeds} == {"volitional", "motion", "effect", "identity"}
    assert all(r["note"] for r in seeds), "a curated value with no reason is one nobody can argue with"
    by_word = {r["name"]: r for r in seeds}
    assert by_word["want"]["family"] == "volitional"
    assert by_word["land"]["family"] == "motion"
    assert by_word["negation"]["family"] == "identity"


def test_every_closure_row_explains_the_cut_it_sets():
    cuts = {r["name"]: r for r in policy_rows() if r["kind"] == policy.KIND_CLOSURE}
    assert set(cuts) == set(policy.CLOSURE_SETTINGS)
    assert cuts["max_size"]["value"] == 400
    assert all(row["note"].strip() for row in cuts.values())


def test_the_bar_rows_carry_their_reasons_verbatim():
    """`why` is evidence, not a comment: it is what a later reader argues WITH when a pair looks
    wrong, and it is inside the bar's fingerprint for the same reason."""
    rows = bar_rows()
    assert len(rows) == 18
    assert all(row["why"].strip() for row in rows)
    assert rows[8]["why"] == "ground vs. touching down — the collapse that costs us"


# ------------------------------------------------------------------------------------------------
# 2 — the mechanism
# ------------------------------------------------------------------------------------------------


def _policy_row(kind, name, value=None, position=0, family=None, version=1):
    return {
        "version": version, "kind": kind, "name": name, "value": value,
        "family": family, "position": position, "note": "",
    }


def _bar_row(a, b, verdict="NEAR", why="because", position=0, version=1, retired_at=None):
    return {
        "version": version, "a": a, "b": b, "verdict": verdict, "why": why,
        "position": position, "retired_at": retired_at,
    }


def _closure_rows(**settings):
    values = {"max_depth": 2, "max_size": 400, "senses": "primary"} | settings
    return [
        _policy_row(policy.KIND_CLOSURE, name, value, position=i)
        for i, (name, value) in enumerate(values.items())
    ]


def test_rows_from_two_versions_are_refused_rather_than_reconciled():
    """A build reads ONE policy version — that is what makes the manifest's `policy_version` mean
    anything. Two arriving together is a caller bug, and guessing which one was meant would put a
    hash in the manifest describing something nobody declared."""
    rows = [_policy_row(policy.KIND_SEED, "eat"), _policy_row(policy.KIND_SEED, "food", version=2)]
    with pytest.raises(policy.PolicyRowsInvalid):
        policy.policy_version(rows)


def test_an_incomplete_closure_policy_is_refused():
    """A cut that falls back to a default in code is a cut the manifest cannot vouch for."""
    rows = [r for r in _closure_rows() if r["name"] != "max_size"]
    with pytest.raises(policy.PolicyRowsInvalid) as excinfo:
        policy.closure_from_rows(rows)
    assert "max_size" in str(excinfo.value)


def test_an_unknown_closure_setting_is_refused_not_ignored():
    """The silent no-op this project keeps refusing to repeat, in its policy-table form: a curated
    decision that never took effect and never said so."""
    rows = _closure_rows() + [_policy_row(policy.KIND_CLOSURE, "max_width", 7, position=9)]
    with pytest.raises(policy.PolicyRowsInvalid) as excinfo:
        policy.closure_from_rows(rows)
    assert "max_width" in str(excinfo.value)


def test_extra_seeds_can_never_arrive_as_a_row():
    """`extra_seeds` is what a RUN argues against the standing policy. A row that could set it would
    let a stored policy pretend to be the standard one."""
    assert "extra_seeds" not in policy.CLOSURE_SETTINGS
    rows = _closure_rows() + [_policy_row(policy.KIND_CLOSURE, "extra_seeds", ["runway"], position=9)]
    with pytest.raises(policy.PolicyRowsInvalid):
        policy.closure_from_rows(rows)


def test_the_declared_order_survives_the_rows():
    """The seed list is hashed as a LIST, and mongo's natural order is not a promise anyone should
    lean on — so the order is a column."""
    rows = [
        _policy_row(policy.KIND_SEED, "food", position=1),
        _policy_row(policy.KIND_SEED, "want", position=0),
        _policy_row(policy.KIND_SEED, "eat", position=2),
    ]
    assert policy.seeds_from_rows(rows) == ("want", "food", "eat")


def test_a_retired_pair_leaves_the_bar_and_stays_in_the_ledger():
    """Append-mostly, and the «mostly» is a column with a date on it. A bar that could lose a row
    silently is a bar whose history means nothing."""
    rows = [_bar_row("eat.v", "food.n"), _bar_row("bed.n", "cause.n", position=1, retired_at=1700000000)]
    assert len(policy.live_bar_rows(rows)) == 1
    assert policy.bar_from_rows(rows) == (BarPair("eat.v", "food.n", "NEAR", "because"),)
    assert len(rows) == 2, "the retired row is still there — the caller holds the whole ledger"


def test_the_bar_version_is_the_last_time_it_grew():
    """Read ACROSS versions, unlike the policy: version 3 of the bar is versions 1, 2 and 3's live
    rows together, and the number names the newest of them. That is what makes «was this pair
    declared before that run?» answerable from a build's recorded `bar_version` alone."""
    rows = [_bar_row("eat.v", "food.n"), _bar_row("kill.v", "die.v", position=0, version=3)]
    assert policy.bar_version(rows) == 3
    assert len(policy.bar_from_rows(rows)) == 2


def test_an_empty_bar_is_refused():
    with pytest.raises(policy.PolicyRowsInvalid):
        policy.bar_version([_bar_row("eat.v", "food.n", retired_at=1)])


def test_the_row_fingerprints_move_when_the_rows_do():
    """The two hashes the manifest records beside the config's. They cover the ROWS — which rows,
    at which versions — where the config hash covers the values the engine received."""
    seeds = [_policy_row(policy.KIND_SEED, "eat")]
    before = policy.policy_fingerprint(seeds + _closure_rows())
    assert before != policy.policy_fingerprint(seeds + _closure_rows(max_size=401))
    assert before != policy.policy_fingerprint(
        [_policy_row(policy.KIND_SEED, "eat", family="effect")] + _closure_rows()
    )

    bar = [_bar_row("eat.v", "food.n")]
    assert policy.bar_fingerprint(bar) != policy.bar_fingerprint([_bar_row("eat.v", "food.n", verdict="FAR")])
    assert policy.bar_fingerprint(bar) != policy.bar_fingerprint([_bar_row("eat.v", "food.n", why="other")])


def test_the_policy_fingerprint_ignores_when_the_rows_were_written():
    """Two databases that received the same migration at different moments hold the same policy. A
    fingerprint that disagreed with that would be measuring the deploy rather than the declaration."""
    rows = [_policy_row(policy.KIND_SEED, "eat")] + _closure_rows()
    stamped = [row | {"created_at": 1700000000, "_id": "whatever"} for row in rows]
    assert policy.policy_fingerprint(stamped) == policy.policy_fingerprint(rows)


def test_the_row_fingerprints_are_not_the_configs():
    """Three hashes, three claims. The manifest records all of them because «same policy» and «same
    rows» are different statements, and a build that assembled its config from somewhere else would
    agree on the first and disagree on the last two."""
    prows, brows = policy_rows(), bar_rows()
    config = policy.config_from_rows(prows, brows)
    assert len({config.fingerprint(), policy.policy_fingerprint(prows), policy.bar_fingerprint(brows)}) == 3


def test_a_config_written_back_out_as_rows_reads_back_the_same():
    """The round trip the migration uses to carry an existing declaration across unchanged."""
    config = DictionaryConfig(
        closure=ClosurePolicy(max_depth=1, max_size=9, senses="all", extra_seeds=("runway",)),
        declared_seeds=("eat", "food"),
        bar=(BarPair("eat.v", "food.n", "NEAR", "why"),),
    )
    rebuilt = policy.config_from_rows(
        policy.policy_rows_of(config, 1),
        policy.bar_rows_of(config.bar, 1),
        extra_seeds=config.closure.extra_seeds,
    )
    assert rebuilt == config


# ------------------------------------------------------------------------------------------------
# the manifest — what a build has to leave behind
# ------------------------------------------------------------------------------------------------


def test_the_manifest_records_the_rows_the_build_was_measured_against():
    """The ledger fields, and the reason they are assembled from the rows: a tool that copied a
    version number in by hand would be free to copy the wrong one, and the row would then be a
    confident record of a policy nobody ran."""
    prows, brows = policy_rows(), bar_rows()
    config = policy.config_from_rows(prows, brows)

    row = policy.manifest_row(
        config, prows, brows,
        counts={"lexicon": 68779, "words": 1220, "keys": 1868},
        authorization="the Captain, at dispatch",
    )

    assert row["config_fingerprint"] == T2B_FINGERPRINT
    assert row["policy_version"] == 1 and row["policy_fingerprint"] == policy.policy_fingerprint(prows)
    assert row["bar_version"] == 1 and row["bar_fingerprint"] == policy.bar_fingerprint(brows)
    assert row["counts"]["keys"] == 1868
    # The policy itself travels beside its hash: a later reader diffs two builds rather than
    # trusting two hashes to differ for the reason he assumes.
    assert row["policy"]["closure"]["max_size"] == 400
    assert len(row["policy"]["bar"]) == 18


def test_a_manifest_row_is_a_valid_build_document():
    """It has to survive the door it will be written through — the migration writer validates
    against the model, so a shape that only looks right here would fail at the deploy."""
    from tk2.core.models import DictionaryBuildDoc
    from tk2.datatier.migration_writer import shape_of

    prows, brows = policy_rows(), bar_rows()
    row = policy.manifest_row(
        policy.config_from_rows(prows, brows), prows, brows, {"keys": 1868}, "the Captain"
    )
    stored = shape_of(DictionaryBuildDoc).model_validate(row).model_dump()
    assert stored["created_at"] > 0
    assert stored["bar_fingerprint"] == row["bar_fingerprint"]


def test_a_build_must_name_who_authorized_it():
    """A manifest that could not say whose hand ordered the build would be a log, not a ledger."""
    from tk2.core.models import DictionaryBuildDoc
    from tk2.datatier.migration_writer import shape_of

    prows, brows = policy_rows(), bar_rows()
    row = policy.manifest_row(policy.config_from_rows(prows, brows), prows, brows, {}, "")
    with pytest.raises(ValueError):
        shape_of(DictionaryBuildDoc).model_validate(row)


# ------------------------------------------------------------------------------------------------
# 3 — the snapshot cannot drift
# ------------------------------------------------------------------------------------------------


def test_the_snapshot_is_the_migrated_bar():
    """The acceptance suite runs where no body is reachable, so it reads this. It must be the same
    bar the rows hold, pair for pair and reason for reason."""
    document = policy.bar_snapshot()
    assert document["version"] == 1
    assert document["fingerprint"] == policy.bar_fingerprint(bar_rows())
    assert policy.snapshot_bar() == policy.config_from_rows(policy_rows(), bar_rows()).bar


def test_reading_the_snapshot_verifies_its_own_pin(tmp_path):
    """The offline half of «it cannot silently drift»: the file is an EXPORT, and a hand edit that
    does not recompute the hash is refused here, with no database in sight."""
    document = policy.bar_snapshot()
    tampered = json.loads(json.dumps(document))
    tampered["pairs"][8]["verdict"] = "NEAR"          # land.n ~ land.v, quietly conceded
    path = tmp_path / "bar_snapshot.json"
    path.write_text(json.dumps(tampered), encoding="utf-8")

    with pytest.raises(policy.SnapshotStale) as excinfo:
        policy.bar_snapshot(path)
    assert "export" in str(excinfo.value)


def test_the_snapshot_carries_no_clock():
    """It pins CONTENT. `created_at` is the ledger's and lives in the rows — in here it would churn
    on every re-export while pinning nothing extra."""
    for pair in policy.bar_snapshot()["pairs"]:
        assert set(pair) == {"version", "position", "a", "b", "verdict", "why"}


@pytest.mark.mongo
def test_the_snapshot_matches_the_database(clean_db):
    """The live half. Rows that moved without an export are caught the first time anybody runs the
    suite near a body — which is the only thing that makes the offline copy trustworthy."""
    from tk2.core.models import DictionaryBarDoc
    from tk2.datatier.migration_writer import MigrationWriter

    writer = MigrationWriter(clean_db)
    clean_db[DictionaryBarDoc.Settings.name].delete_many({})
    writer.insert_many(DictionaryBarDoc, bar_rows())

    stored = list(clean_db[DictionaryBarDoc.Settings.name].find({}))
    assert policy.bar_fingerprint(stored) == policy.bar_snapshot()["fingerprint"]


# ------------------------------------------------------------------------------------------------
# 4 — policy v2: the Captain's ruling, as rows
# ------------------------------------------------------------------------------------------------
#
# Offline, like section 1 and for the same reason: what is under test is a set of VALUES crossing a
# medium. The one thing NOT checked here is that the 200 structural seeds really are the ranking's
# top 200 — that needs the whole 68,779-word digraph and nltk's corpus, so it is a `wordnet` test
# (`tests/test_dictionary_proposal.py`) and `tools/propose_seeds.py --verify` re-runs it beside the
# base it produces.

#: The fingerprint of policy v2 — purpose ∪ structure(top 200), the cap at 25,000, bar v1 unchanged.
#: Written down here for T2B_FINGERPRINT's reason: it is what a build's manifest will record, and a
#: constant a reader can find is worth more than one derived from the thing under test.
RULED_FINGERPRINT = "90f51226938d29b7b2a46dba40f06b4aa1bf2b50c6959543795536292501a50e"


def test_the_ruled_policy_is_purpose_union_structure():
    """The whole of the 2026-08-25 ruling in one assertion: two sources, one set, 224 rows because
    seven words were argued for twice."""
    config = policy.config_from_rows(policy_rows_v2(), bar_rows())
    assert config == ruled_config()
    assert config.fingerprint() == RULED_FINGERPRINT
    assert len(config.declared_seeds) == 224
    assert len(config.seeds) == 228          # the declared 224, plus the bar's own words
    assert config.closure == ClosurePolicy(max_depth=2, max_size=25_000, senses="primary")


def test_the_identity_family_kept_the_concepts_and_lost_the_function_words():
    """The second standing law, as values. `me` and `you` resolve to an ENTITY before the dictionary
    is consulted; `not` and `be` compile. What stays is what each of them is ABOUT."""
    seeds = {r["name"]: r for r in policy_rows_v2() if r["kind"] == policy.KIND_SEED}
    identity = [r["name"] for r in policy_rows_v2() if r.get("family") == "identity"]
    assert identity == ["negation", "being", "same", "different"]
    for gone in ("me", "you", "not", "be"):
        assert seeds.get(gone) is None or seeds[gone]["family"] != "identity"


def test_every_seed_row_names_the_source_that_argued_for_it():
    """Purpose and structure are approved under different eyes, so a seed that could not say which
    one put it there could not later be retired under either."""
    seeds = [r for r in policy_rows_v2() if r["kind"] == policy.KIND_SEED]
    assert {r["family"] for r in seeds} == {
        "volitional", "motion", "effect", "identity", policy.FAMILY_STRUCTURE
    }
    assert all(r["note"].strip() for r in seeds)

    structural = [r for r in seeds if r["family"] == policy.FAMILY_STRUCTURE]
    assert len(structural) == 193, "200 minus the seven purpose already claimed"
    # The rank and the in-degree travel in the note, because «structure argued for this» means
    # exactly «this many definitions name it» and a rank alone would hide that.
    by_word = {r["name"]: r for r in seeds}
    assert "#1 of the cleaned in-degree ranking, named by 4,044" in by_word["use"]["note"]
    assert "requirement 8" in by_word["want"]["note"]


def test_a_word_both_sources_argued_for_keeps_both_arguments():
    """`land` is a motion seed AND #197 of the ranking. One row — the unique index allows no other
    answer — so the purpose family wins the column and the structural rank goes in the note."""
    by_word = {r["name"]: r for r in policy_rows_v2() if r["kind"] == policy.KIND_SEED}
    assert by_word["land"]["family"] == "motion"
    assert "#197" in by_word["land"]["note"]

    both = [w for w, _rank, _degree in structural_seeds() if by_word[w]["family"] != policy.FAMILY_STRUCTURE]
    assert both == ["leave", "move", "food", "same", "come", "different", "land"]
    names = [r["name"] for r in policy_rows_v2() if r["kind"] == policy.KIND_SEED]
    assert len(names) == len(set(names)), "one form, one row — the unique index would say so louder"


def test_the_structural_seeds_are_a_ranking_and_read_back_as_one():
    """The rows are in rank order and the in-degrees never rise, which is what «top 200» means. A
    list that had been re-sorted, hand-edited or partly re-derived would fail here."""
    seeds = structural_seeds()
    assert len(seeds) == 200
    assert [rank for _word, rank, _degree in seeds] == list(range(1, 201))
    degrees = [degree for _word, _rank, degree in seeds]
    assert degrees == sorted(degrees, reverse=True)
    assert seeds[0] == ("use", 1, 4044)
    assert seeds[-1] == ("sexual", 200, 240)

    declared = policy.seeds_from_rows(policy_rows_v2())
    assert all(word in declared for word, _rank, _degree in seeds)


def test_no_structural_seed_is_a_closed_class_form():
    """The exclusion by PRINCIPLE, checked on the OUTPUT rather than on the intention: `in` heads the
    raw ranking with 14,408 in-edges and means *inch*, and the one thing that must never happen is
    that a function word arrives as a dimension after all."""
    forms = set(closed_class_forms())
    assert not [word for word, _rank, _degree in structural_seeds() if word in forms]


def test_the_size_cap_row_says_it_is_no_longer_a_design_knob():
    """The ruling's reasoning has to survive in the medium the rows have for it, or the next reader
    meets 25,000 with nothing to tell him why it is not a number to tune."""
    cuts = {r["name"]: r for r in policy_rows_v2() if r["kind"] == policy.KIND_CLOSURE}
    assert cuts["max_size"]["value"] == 25_000
    note = cuts["max_size"]["note"]
    assert "NOT A DESIGN KNOB" in note
    assert "588" in note and "50" in note, "the measurement that demoted it travels with it"
    assert "THE POLICY" in cuts["max_depth"]["note"], "the depth cut is what was left in charge"


def test_version_1_is_not_touched_by_version_2():
    """`dictionary_policy` is a LEDGER. v1 still rebuilds the policy T2b measured, with v2 declared
    beside it — which is the only thing that keeps an old manifest row meaningful."""
    assert policy.policy_version(policy_rows()) == 1
    assert policy.policy_version(policy_rows_v2()) == 2
    assert policy.config_from_rows(policy_rows(), bar_rows()).fingerprint() == T2B_FINGERPRINT
    assert policy.policy_fingerprint(policy_rows()) != policy.policy_fingerprint(policy_rows_v2())


def test_the_newest_version_is_selected_explicitly_and_never_guessed():
    """What a tool reading the whole table has to do. `policy_version` refuses a mixed set; choosing
    is a separate, named act, so nothing can drift into measuring a superseded policy by accident."""
    both = policy_rows() + policy_rows_v2()
    with pytest.raises(policy.PolicyRowsInvalid):
        policy.policy_version(both)
    assert policy.policy_version(policy.latest_version(both)) == 2
    assert policy.latest_version(policy_rows()) == policy_rows()
    with pytest.raises(policy.PolicyRowsInvalid):
        policy.latest_version([])


def test_the_bar_did_not_move_with_the_seeds():
    """v2 is measured against the same eighteen pairs. The bar is append-mostly and a policy ruling
    is not an occasion to quietly re-declare the expectation the ruling will be judged by."""
    assert ruled_config().bar == policy.snapshot_bar()
    assert len(ruled_config().bar) == 18


# ------------------------------------------------------------------------------------------------
# 5 — policy v3: R's weights, the curated vocabulary and the alphabet (T3)
# ------------------------------------------------------------------------------------------------
#
# Offline again, and for section 1's reason: what is under test is a set of VALUES crossing a
# medium. The standing law named this one in advance — «the relation weights you write in T3: they
# land as rows from the start, never as a table in config.py» — so the load-bearing assertions here
# are that the rows carry them, that the shape module carries none of them, and that v1 and v2 did
# not move underneath.

#: The fingerprint of policy v3 — v2's seeds and cuts, plus the nineteen relation weights, the six
#: curated relations, the reciprocal, the miner's guess and the alphabet. Written down for
#: T2B_FINGERPRINT's reason: it is what a build's manifest will record.
V3_FINGERPRINT = "4bd99d3dbd57a50a354c888fa84abfc951af166b0d7c48f7bfa9934d7e2e5b67"


def test_the_relation_weights_are_rows():
    """The standing law's own worked example. Nineteen weights, signs included, read back as the
    value object R is filled from."""
    config = policy.config_from_rows(policy_rows_v3(), bar_rows())
    assert config == declared_config_v3()
    assert config.fingerprint() == V3_FINGERPRINT

    weights = dict(config.relations.weights)
    assert len(weights) == 19
    assert weights["identity"] == 1.0 and weights["synonym"] == 1.0
    assert weights["antonym"] == -1.0, "the sign is the antonym column-read primitive"
    assert weights["causes"] == 0.85 and weights["caused_by"] == 0.60
    assert weights["entails"] == 0.80 and weights["entailed_by"] == 0.60


def test_the_declared_order_of_the_weights_is_the_cell_walks_precedence():
    """`position` is not decoration here: two relations of equal absolute weight resolve to the one
    declared first, so a rebuild cannot flip a cell's provenance by iteration luck."""
    relations = policy.config_from_rows(policy_rows_v3(), bar_rows()).relations
    assert relations.relations[:3] == ("identity", "synonym", "antonym")
    assert relations.precedence("troponym") < relations.precedence("hyponym_1")
    assert relations.weight_of("troponym") == relations.weight_of("hyponym_1")


def test_neither_gloss_overlap_nor_wup_is_a_relation_of_r():
    """The two the prototype's single weight table carried and R must not: `gloss_overlap` is
    co-occurrence, which is D's whole job (requirement 10), and `wup` is a score OVER the taxonomy
    rather than a named edge, so it fails R's provenance criterion and D's co-occurrence one alike."""
    relations = policy.config_from_rows(policy_rows_v3(), bar_rows()).relations
    assert "gloss_overlap" not in relations.relations
    assert "wup" not in relations.relations


def test_the_curated_vocabulary_is_closed_and_carries_the_reciprocal():
    """Requirement 20's six, and the back-reference the Captain ruled on 2026-08-12. A separate row
    KIND from the mined weights because `entails` is in both — the same claim from two provenances."""
    relations = policy.config_from_rows(policy_rows_v3(), bar_rows()).relations
    assert [name for name, _weight in relations.curated] == [
        "used_for", "site_of", "involves", "entails", "causes", "state_of"
    ]
    assert relations.curated_weight("used_for") == 0.80
    assert relations.reciprocal_weight == 0.60
    # ...and the two `entails` are two different rows with two different kinds, never one.
    kinds = {(r["kind"], r["name"]) for r in policy_rows_v3()}
    assert (policy.KIND_RELATION_WEIGHT, "entails") in kinds
    assert (policy.KIND_CURATED_RELATION, "entails") in kinds


def test_the_miners_guess_is_rows_too():
    """A cue-word table is a list, and the standing law is unambiguous about lists. Carried verbatim
    from the prototype, in the order the cues are tried."""
    relations = policy.config_from_rows(policy_rows_v3(), bar_rows()).relations
    assert [name for name, _cues in relations.cues] == ["causes", "used_for", "site_of"]
    assert "provides" in dict(relations.cues)["used_for"]
    assert ("a", "v", "state_of") in relations.defaults


def test_the_alphabet_travelled_with_the_policy():
    """`POS_ORDER` — WordNet's answer about English, not the key grammar (the Captain, 2026-08-25).
    It was ruled before v2 shipped and v2 shipped without it, so it folds in here."""
    config = policy.config_from_rows(policy_rows_v3(), bar_rows())
    assert config.alphabet.order == ("n", "v", "a", "r")
    assert dict(config.alphabet.aliases) == {"s": "a"}
    assert [r["name"] for r in policy_rows_v3() if r["kind"] == policy.KIND_POS] == list("nvar")


def test_version_3_carries_version_2_forward_unedited():
    """A build reads ONE version, so v3 has to be a WHOLE policy — and the half of it that did not
    move must be v2's own values, not a re-typing of them."""
    v2 = {(r["kind"], r["name"]): (r["value"], r["family"], r["note"]) for r in policy_rows_v2()}
    v3 = {(r["kind"], r["name"]): (r["value"], r["family"], r["note"]) for r in policy_rows_v3()}
    carried = {key: value for key, value in v3.items() if key[0] in (policy.KIND_SEED, policy.KIND_CLOSURE)}

    assert carried == v2, "the seeds, the cuts, their families and their reasons cross unchanged"
    assert ruled_config().closure == declared_config_v3().closure
    assert ruled_config().declared_seeds == declared_config_v3().declared_seeds
    assert declared_config_v3().bar == policy.snapshot_bar(), "the bar did not move with them either"


def test_every_new_row_still_explains_itself():
    """The rule the older versions are held to, applied to the kinds T3 adds: a curated value with
    no reason attached is a value nobody can later argue with."""
    assert all(row["note"].strip() for row in policy_rows_v3())
    assert all(row["family"] for row in policy_rows_v3() if row["kind"] == policy.KIND_RELATION_WEIGHT)


def test_the_older_versions_hash_exactly_as_they_did():
    """THE regression the optional fields exist for. `as_dict` writes nothing about relations or the
    alphabet when a policy declared neither, so a manifest row recording v1 or v2 keeps meaning what
    it meant — and a v3 build cannot be mistaken for either."""
    assert policy.config_from_rows(policy_rows(), bar_rows()).fingerprint() == T2B_FINGERPRINT
    assert policy.config_from_rows(policy_rows_v2(), bar_rows()).fingerprint() == RULED_FINGERPRINT
    assert V3_FINGERPRINT not in (T2B_FINGERPRINT, RULED_FINGERPRINT)

    v1 = policy.config_from_rows(policy_rows(), bar_rows())
    assert "relations" not in v1.as_dict() and "alphabet" not in v1.as_dict()
    assert v1.relations is None and v1.alphabet is None


# ------------------------------------------------------------------------------------------------
# the mechanism, on rows written here — half a declaration is not a policy
# ------------------------------------------------------------------------------------------------


def _weight_rows(*pairs, version=1):
    return [
        _policy_row(policy.KIND_RELATION_WEIGHT, name, value, position=i, version=version)
        for i, (name, value) in enumerate(pairs)
    ]


def test_a_policy_that_declares_no_relations_says_so_rather_than_inventing_them():
    """`None`, not an empty `RelationPolicy`: v1 and v2 had nothing to say about relations, and a
    config that answered «no weights» would be a config claiming a matrix nobody declared."""
    assert policy.relation_policy_from_rows(_closure_rows()) is None


def test_a_curated_vocabulary_without_weights_is_refused():
    """Half a declaration. A curated edge is shaped like the mined edges it sits beside, so a
    vocabulary with no table beside it describes nothing."""
    rows = [_policy_row(policy.KIND_CURATED_RELATION, "used_for", 0.8)]
    with pytest.raises(policy.PolicyRowsInvalid):
        policy.relation_policy_from_rows(rows)


def test_a_curated_vocabulary_without_a_reciprocal_is_refused():
    """The back-reference is half of what a curated edge writes, and a default in code would be a
    second declaration of a number the Captain ruled."""
    rows = _weight_rows(("identity", 1.0)) + [
        _policy_row(policy.KIND_CURATED_RELATION, "used_for", 0.8)
    ]
    with pytest.raises(policy.PolicyRowsInvalid) as excinfo:
        policy.relation_policy_from_rows(rows)
    assert "reciprocal_weight" in str(excinfo.value)


def test_an_unknown_curation_setting_is_refused_not_ignored():
    rows = _weight_rows(("identity", 1.0)) + [_policy_row(policy.KIND_CURATION, "temperature", 3)]
    with pytest.raises(policy.PolicyRowsInvalid) as excinfo:
        policy.relation_policy_from_rows(rows)
    assert "temperature" in str(excinfo.value)


def test_a_cue_for_a_relation_outside_the_closed_set_is_refused():
    """The vocabulary is closed at the row level too, or a guess could propose something no cell may
    ever carry."""
    rows = _weight_rows(("identity", 1.0)) + [
        _policy_row(policy.KIND_CURATED_RELATION, "used_for", 0.8),
        _policy_row(policy.KIND_CURATION, "reciprocal_weight", 0.6),
        _policy_row(policy.KIND_CURATION_CUE, "smells_like", ["fishy"]),
    ]
    with pytest.raises(policy.PolicyRowsInvalid):
        policy.relation_policy_from_rows(rows)


def test_an_alias_with_no_alphabet_to_point_at_is_refused():
    assert policy.alphabet_from_rows(_closure_rows()) is None
    with pytest.raises(policy.PolicyRowsInvalid):
        policy.alphabet_from_rows([_policy_row(policy.KIND_POS_ALIAS, "s", "a")])


def test_an_alphabet_the_key_convention_cannot_honour_stops_at_the_config():
    """Reading those rows to LOOK at them stays possible; assembling a build's config out of them
    does not. The refusal happens before anything is measured."""
    rows = _closure_rows() + [
        _policy_row(policy.KIND_POS, letter, name, position=i)
        for i, (letter, name) in enumerate((("n", "noun"), ("v", "verb"), ("x", "particle")))
    ]
    assert policy.alphabet_from_rows(rows).order == ("n", "v", "x")
    with pytest.raises(keys_module.AlphabetMismatch):
        policy.config_from_rows(rows, bar_rows())


# ------------------------------------------------------------------------------------------------
# 6 — policy v4: whose lemma may speak (the Captain's ruling, 2026-08-26)
# ------------------------------------------------------------------------------------------------
#
# The value that moved is one row, and the reason it is a row at all is the standing law's two
# tests: changing it changes what the rows SAY and not the shape of anything, and EVIDENCE is
# exactly what revised it — a measured A/B the Captain ruled on. What is checked here is that the
# ruling reached the rows, that its measurement travelled with it, and that the three versions
# before it did not move.

#: The fingerprint of policy v4 — v3's whole declaration plus `lemma_scope = word`.
V4_FINGERPRINT = "00edc2b29a35eb7152523659432a30711c609c20edc6c16b75daf196f7d4f2e5"


def test_the_lemma_scope_is_a_row_and_it_says_word():
    config = policy.config_from_rows(policy_rows_v4(), bar_rows())
    assert config == declared_config_v4()
    assert config.fingerprint() == V4_FINGERPRINT
    assert config.relations.lemma_scope == "word"

    scope_rows = [r for r in policy_rows_v4() if r["kind"] == policy.KIND_RELATION_SETTING]
    assert [(r["name"], r["value"]) for r in scope_rows] == [("lemma_scope", "word")]


def test_the_measurement_that_produced_the_ruling_travels_with_it():
    """A curated value with no reason attached is a value nobody can later argue with — and this one
    was ruled on numbers, so the numbers are the reason. The witness is named because «a wrong
    negative is worse than silence» needs a wrong negative anybody can go and look at."""
    note = next(r["note"] for r in policy_rows_v4() if r["kind"] == policy.KIND_RELATION_SETTING)
    for measured in ("56,599", "49,965", "-6,634", "920 -> 663", "318 -> 353"):
        assert measured in note, f"the note lost {measured}"
    assert "dark.n -> day.n" in note and "night" in note
    assert "3,095 words / 4,445 dimensions" in note, "membership did NOT move, and it must say so"


def test_version_4_carries_version_3_forward_unedited():
    """A build reads ONE version, so v4 is a WHOLE policy — and the 267 rows that did not move must
    be v3's own values and reasons, not a re-typing of them."""
    v3 = {(r["kind"], r["name"]): (r["value"], r["family"], r["note"]) for r in policy_rows_v3()}
    v4 = {(r["kind"], r["name"]): (r["value"], r["family"], r["note"]) for r in policy_rows_v4()}

    assert len(v4) == len(v3) + 1
    assert {k: v for k, v in v4.items() if k in v3} == v3
    assert set(v4) - set(v3) == {(policy.KIND_RELATION_SETTING, "lemma_scope")}
    assert declared_config_v4().bar == policy.snapshot_bar()


def test_the_three_older_versions_still_hash_as_they_did():
    """Every fingerprint moves for v4 and none moves for what came before: `as_dict` writes nothing
    about a scope a policy never declared. An old manifest row keeps meaning what it meant."""
    assert policy.config_from_rows(policy_rows(), bar_rows()).fingerprint() == T2B_FINGERPRINT
    assert policy.config_from_rows(policy_rows_v2(), bar_rows()).fingerprint() == RULED_FINGERPRINT
    assert policy.config_from_rows(policy_rows_v3(), bar_rows()).fingerprint() == V3_FINGERPRINT
    assert len({T2B_FINGERPRINT, RULED_FINGERPRINT, V3_FINGERPRINT, V4_FINGERPRINT}) == 4

    v3 = policy.config_from_rows(policy_rows_v3(), bar_rows())
    assert v3.relations.lemma_scope is None
    assert "lemma_scope" not in v3.relations.as_dict()


def test_the_mining_law_the_code_still_owns_did_not_move_with_it():
    """`RELATION_RULES` names what stays in CODE about the cell walk. The scope left it and became a
    row, so the config fingerprint covers the scope directly — bumping the date would claim the code
    changed its mind about something it no longer decides."""
    from tk2.dictionary.config import RELATION_RULES

    assert policy.config_from_rows(policy_rows_v3(), bar_rows()).relations.as_dict()["rules"] == \
        policy.config_from_rows(policy_rows_v4(), bar_rows()).relations.as_dict()["rules"] == \
        RELATION_RULES


def test_an_unknown_relation_setting_is_refused_not_ignored():
    rows = _weight_rows(("identity", 1.0)) + [_policy_row(policy.KIND_RELATION_SETTING, "senses", "all")]
    with pytest.raises(policy.PolicyRowsInvalid) as excinfo:
        policy.relation_policy_from_rows(rows)
    assert "senses" in str(excinfo.value)


def test_a_scope_row_without_weights_beside_it_is_refused():
    """Half a declaration again: a reading of the resource with no matrix to read it into."""
    with pytest.raises(policy.PolicyRowsInvalid):
        policy.relation_policy_from_rows([_policy_row(policy.KIND_RELATION_SETTING, "lemma_scope", "word")])


# ------------------------------------------------------------------------------------------------
# 7 — policy v5: the inferred opposition admitted (the Captain's ruling, 2026-08-26)
# ------------------------------------------------------------------------------------------------

#: The fingerprint of policy v5 — v4's whole declaration, plus `antonym_symmetry = add_only` and the
#: weight of the relation that reading mints.
V5_FINGERPRINT = "2e19cbb1329be812f1557f7807d99802d76320217ca45dc389189730eab88e79"


def test_the_reading_and_the_relation_it_mints_are_both_rows():
    """Two rows and ONE decision: the mode, and the weight of the cell it writes. Neither is
    meaningful alone, and the engine refuses either without the other."""
    config = policy.config_from_rows(policy_rows_v5(), bar_rows())
    assert config == declared_config_v5()
    assert config.fingerprint() == V5_FINGERPRINT
    assert config.relations.antonym_symmetry == "add_only"
    assert dict(config.relations.weights)["antonym_inferred"] == -1.0
    assert config.relations.lemma_scope == "word", "v4's ruling is carried, not re-argued"


def test_the_inferred_relation_is_believed_last_among_equals():
    """Its PRECEDENCE is the end of the declared order, which costs nothing and says something: an
    inferred opposition can only ever occupy a cell nothing else claimed, so its position never
    decides a winner — and last is the honest place for it."""
    relations = policy.config_from_rows(policy_rows_v5(), bar_rows()).relations
    assert relations.relations[-1] == "antonym_inferred"
    assert relations.precedence("antonym_inferred") > relations.precedence("antonym")


def test_the_evidence_that_produced_the_ruling_travels_with_the_mode():
    """It was ruled on a measurement AND on a principle, and the row has to carry both — the numbers
    because they are the reason, and «the bar reads identically» because that is what says the
    ruling does not rest on the bar."""
    note = next(r["note"] for r in policy_rows_v5()
                if (r["kind"], r["name"]) == (policy.KIND_RELATION_SETTING, "antonym_symmetry"))
    for measured in ("143", "overwrites 0", "663 -> 806", "353 -> 346", "3,095 words / 4,445"):
        assert measured in note, f"the note lost {measured}"
    assert "dark.n -> day.n" in note, "the cell overwrite would have destroyed is named"
    assert "IDENTICALLY UNDER ALL" in note and "PRINCIPLE" in note


def test_the_name_argues_for_itself_in_the_row():
    """Why it is not `antonym`, not `antonym_of`, and carries no `_reciprocal` suffix. A curated
    value with no reason attached is a value nobody can later argue with — and this one is a NAME,
    which is the part a later reader is most likely to want to change."""
    note = next(r["note"] for r in policy_rows_v5()
                if (r["kind"], r["name"]) == (policy.KIND_RELATION_WEIGHT, "antonym_inferred"))
    assert "NOT called `antonym`" in note
    assert "antonym_of" in note and "_reciprocal" in note
    assert "same sign, same strength, different name" in note


def test_version_5_carries_version_4_forward_unedited():
    v4 = {(r["kind"], r["name"]): (r["value"], r["family"], r["note"]) for r in policy_rows_v4()}
    v5 = {(r["kind"], r["name"]): (r["value"], r["family"], r["note"]) for r in policy_rows_v5()}

    assert len(v5) == len(v4) + 2
    assert {k: v for k, v in v5.items() if k in v4} == v4
    assert set(v5) - set(v4) == {
        (policy.KIND_RELATION_WEIGHT, "antonym_inferred"),
        (policy.KIND_RELATION_SETTING, "antonym_symmetry"),
    }
    assert declared_config_v5().bar == policy.snapshot_bar()


def test_the_four_older_versions_still_hash_as_they_did():
    """Every fingerprint moves for v5 and none moves for what came before."""
    assert policy.config_from_rows(policy_rows(), bar_rows()).fingerprint() == T2B_FINGERPRINT
    assert policy.config_from_rows(policy_rows_v2(), bar_rows()).fingerprint() == RULED_FINGERPRINT
    assert policy.config_from_rows(policy_rows_v3(), bar_rows()).fingerprint() == V3_FINGERPRINT
    assert policy.config_from_rows(policy_rows_v4(), bar_rows()).fingerprint() == V4_FINGERPRINT
    assert len({T2B_FINGERPRINT, RULED_FINGERPRINT, V3_FINGERPRINT, V4_FINGERPRINT,
                V5_FINGERPRINT}) == 5

    v4 = policy.config_from_rows(policy_rows_v4(), bar_rows())
    assert v4.relations.antonym_symmetry is None
    assert "antonym_symmetry" not in v4.relations.as_dict()


def test_a_reading_and_its_weight_row_travel_together():
    """The pairing, from both sides, as the engine enforces it — `relations.policy_for` is the one
    place that knows which weight a reading needs, so nothing can strip it by hand and drift."""
    from tk2.dictionary import relations as relation_engine

    standing = policy.config_from_rows(policy_rows_v5(), bar_rows()).relations
    for mode in ("stated", "overwrite"):
        older = relation_engine.policy_for(standing, mode)
        assert "antonym_inferred" not in dict(older.weights)
        assert older.antonym_symmetry == mode
    again = relation_engine.policy_for(standing, "add_only")
    assert dict(again.weights)["antonym_inferred"] == -1.0
    assert again == standing, "the standing policy IS the add-only policy"
