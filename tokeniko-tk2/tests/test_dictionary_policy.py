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
  9. THE DUAL READ IS RULED (policy v7): the mix gets a home of its own, and two numbers move on
     the sweeps that measured them.
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
    baseline,
    migration,
    bar_rows_v2,
    closed_class_forms,
    declared_config,
    declared_config_v3,
    declared_config_v4,
    declared_config_v5,
    declared_config_v6,
    declared_config_v7,
    declared_config_v8,
    declared_config_v9,
    declared_config_v10,
    declared_config_v11,
    declared_config_v12,
    policy_rows,
    policy_rows_v2,
    policy_rows_v3,
    policy_rows_v4,
    policy_rows_v5,
    policy_rows_v6,
    policy_rows_v7,
    policy_rows_v8,
    policy_rows_v9,
    policy_rows_v10,
    policy_rows_v11,
    policy_rows_v12,
    ruled_config,
    structural_seeds,
)
from tk2.dictionary import keys as keys_module
from tk2.dictionary import policy
from tk2.dictionary.config import BarPair, ClosurePolicy, DictionaryConfig, ReadingPolicy

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
    assert document["version"] == 2
    assert document["fingerprint"] == policy.bar_fingerprint(bar_rows() + bar_rows_v2())
    # The snapshot is the LIVE bar — v1's eighteen plus v2's nineteen since 0011 — so it is read
    # against the live rows, not against v1's alone.
    assert policy.snapshot_bar() == policy.config_from_rows(
        policy_rows(), bar_rows() + bar_rows_v2()
    ).bar


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
    # BOTH versions: the snapshot pins the LIVE bar, and since 0011 that is v1 plus v2. Writing
    # only v1 here would prove the snapshot matches a bar nobody runs.
    writer.insert_many(DictionaryBarDoc, bar_rows() + bar_rows_v2())

    stored = list(clean_db[DictionaryBarDoc.Settings.name].find({}))
    assert policy.bar_version(stored) == 2
    assert len(policy.bar_from_rows(stored)) == 37
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
    assert ruled_config().bar == policy.bar_from_rows(bar_rows())
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
    # «The bar did not move with them» — said against the LEDGER since E1b squashed the chain:
    # policy v3 declares no bar pairs of its own, and the bar's own versions are 1 and 2.
    assert {row["version"] for row in baseline().BAR_ROWS} == {1, 2}
    assert declared_config_v3().bar == policy.bar_from_rows(bar_rows())


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
    # «The bar did not move with them» — said against the LEDGER since E1b squashed the chain:
    # policy v4 declares no bar pairs of its own, and the bar's own versions are 1 and 2.
    assert {row["version"] for row in baseline().BAR_ROWS} == {1, 2}
    assert declared_config_v4().bar == policy.bar_from_rows(bar_rows())


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
    # «The bar did not move with them» — said against the LEDGER since E1b squashed the chain:
    # policy v5 declares no bar pairs of its own, and the bar's own versions are 1 and 2.
    assert {row["version"] for row in baseline().BAR_ROWS} == {1, 2}
    assert declared_config_v5().bar == policy.bar_from_rows(bar_rows())


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


# ------------------------------------------------------------------------------------------------
# 8 — policy v6: D's gloss walk, declared before it measured anything (T4, 2026-09-09)
# ------------------------------------------------------------------------------------------------
#
# The standing law's own worked example, applied to the second matrix on its first day: «a
# category-2 set stated in code is a defect even when its contents are correct». D's nine parameters
# are curation, so they arrive as rows rather than being moved into rows later — and they arrive as
# the PROTOTYPE's values, because a value edited on the way in would corrupt the comparison the
# measurement is about to make.

#: The fingerprint of policy v6 — v5's whole declaration, plus the gloss walk.
V6_FINGERPRINT = "29b95942c0840b7ee107bcf66034e9e373a185c6f9539940be833d60c21321a8"


def test_the_gloss_walk_is_rows_from_its_first_day():
    config = policy.config_from_rows(policy_rows_v6(), bar_rows())
    assert config == declared_config_v6()
    assert config.fingerprint() == V6_FINGERPRINT
    assert config.distribution is not None
    assert config.relations.antonym_symmetry == "add_only", "v5's ruling is carried, not re-argued"


def test_the_walk_is_the_prototypes_own_values():
    """T4b-i's rule, kept: «today's values migrate across VERBATIM». Every one of these is in
    `scripts/tk2/tk2_config.py` or in `tk2_matrix.cell`, and the comparison the Captain is about to
    rule on is only honest if the starting point is the thing that was measured before."""
    walk = policy.config_from_rows(policy_rows_v6(), bar_rows()).distribution
    assert (walk.measure, walk.weighting, walk.vocabulary) == ("jaccard", "uniform", "base")
    assert (walk.min_shared, walk.scale, walk.cap, walk.floor) == (2, 5.0, 0.5, 0.1)
    assert walk.identity == 1.0
    assert walk.senses == "primary"


def test_every_parameter_of_the_walk_explains_itself_and_what_it_measures():
    """A curated value with no reason attached is one nobody can later argue with. Three of these do
    not survive the change of scale intact, and the rows have to say so in numbers."""
    notes = {r["name"]: r["note"] for r in policy_rows_v6()
             if r["kind"] == policy.KIND_DISTRIBUTION}
    assert set(notes) == set(policy.DISTRIBUTION_SETTINGS)
    assert all(len(note) > 80 for note in notes.values())
    assert "835,145" in notes["vocabulary"], "the base/lexicon measurement travels with the row"
    assert "76,915" in notes["min_shared"], "what the floor actually sizes"
    assert "BINARY" in notes["cap"], "the saturation finding is not left to a reader to discover"
    assert "log(1 + N/df)" in notes["weighting"] and "smoothing" in notes["weighting"]


def test_a_policy_that_declares_no_walk_says_so_rather_than_inventing_one():
    """`None`, not a default walk: v1-v5 had nothing to say about D, and the base T3 measured must
    stay readable exactly as it was measured."""
    assert policy.distribution_from_rows(_closure_rows()) is None
    v5 = policy.config_from_rows(policy_rows_v5(), bar_rows())
    assert v5.distribution is None and "distribution" not in v5.as_dict()


def test_half_a_walk_is_refused_rather_than_completed():
    """A D missing its floor is not a laxer D — it is a matrix whose size nobody declared."""
    rows = [_policy_row(policy.KIND_DISTRIBUTION, "measure", "jaccard"),
            _policy_row(policy.KIND_DISTRIBUTION, "senses", "primary")]
    with pytest.raises(policy.PolicyRowsInvalid) as excinfo:
        policy.distribution_from_rows(rows)
    assert "min_shared" in str(excinfo.value)


def test_an_unknown_walk_setting_is_refused_not_ignored():
    rows = [_policy_row(policy.KIND_DISTRIBUTION, name, value)
            for name, value in (("senses", "primary"), ("vocabulary", "base"),
                                ("measure", "jaccard"), ("weighting", "uniform"),
                                ("min_shared", 2), ("scale", 5.0), ("cap", 0.5),
                                ("floor", 0.1), ("identity", 1.0), ("temperature", 3))]
    with pytest.raises(policy.PolicyRowsInvalid) as excinfo:
        policy.distribution_from_rows(rows)
    assert "temperature" in str(excinfo.value)


def test_a_walk_whose_floor_is_above_its_cap_is_refused_at_the_row():
    """Every cell D could write would be refused: a policy that declares an empty matrix by accident
    rather than on purpose."""
    rows = [_policy_row(policy.KIND_DISTRIBUTION, name, value)
            for name, value in (("senses", "primary"), ("vocabulary", "base"),
                                ("measure", "jaccard"), ("weighting", "uniform"),
                                ("min_shared", 2), ("scale", 5.0), ("cap", 0.1),
                                ("floor", 0.5), ("identity", 1.0))]
    with pytest.raises(policy.PolicyRowsInvalid):
        policy.distribution_from_rows(rows)


def test_version_6_carries_version_5_forward_unedited():
    """A build reads ONE version, so v6 is a WHOLE policy — and the rows that did not move must be
    v5's own values and reasons, not a re-typing of them."""
    v5 = {(r["kind"], r["name"]): (r["value"], r["family"], r["note"]) for r in policy_rows_v5()}
    v6 = {(r["kind"], r["name"]): (r["value"], r["family"], r["note"]) for r in policy_rows_v6()}

    assert len(v6) == len(v5) + len(policy.DISTRIBUTION_SETTINGS)
    assert {k: v for k, v in v6.items() if k in v5} == v5
    assert {name for kind, name in set(v6) - set(v5)} == set(policy.DISTRIBUTION_SETTINGS)


def test_the_five_older_versions_still_hash_as_they_did():
    """`as_dict` writes nothing about a walk a policy never declared, so every manifest row naming
    v1-v5 keeps meaning what it meant — and a v6 build cannot be mistaken for any of them."""
    from tests.seed import policy_rows_v4

    assert policy.config_from_rows(policy_rows(), bar_rows()).fingerprint() == T2B_FINGERPRINT
    assert policy.config_from_rows(policy_rows_v2(), bar_rows()).fingerprint() == RULED_FINGERPRINT
    assert policy.config_from_rows(policy_rows_v3(), bar_rows()).fingerprint() == V3_FINGERPRINT
    assert policy.config_from_rows(policy_rows_v4(), bar_rows()).fingerprint() == V4_FINGERPRINT
    assert policy.config_from_rows(policy_rows_v5(), bar_rows()).fingerprint() == V5_FINGERPRINT
    assert len({T2B_FINGERPRINT, RULED_FINGERPRINT, V3_FINGERPRINT, V4_FINGERPRINT,
                V5_FINGERPRINT, V6_FINGERPRINT}) == 6


def test_a_walk_written_back_out_as_rows_reads_back_the_same():
    """The round trip, for the ninth kind of row: what `policy_rows_of` writes is what
    `config_from_rows` reads, or the migration that first writes a policy is writing something else."""
    config = declared_config_v6()
    written = policy.policy_rows_of(config, version=6)
    assert policy.config_from_rows(written, policy.bar_rows_of(config.bar, 1)) == config


# ------------------------------------------------------------------------------------------------
# 9 — policy v7: the dual read gets a home, and two numbers move (T4, 2026-09-09)
# ------------------------------------------------------------------------------------------------
#
# The mix was deliberately kept OUT of v6 — «measured at T4 and ruled by the Captain before it can
# be a row at all» — and this is the ruling: 0.5, beside `min_shared` 1 and `derivational` 0.45.
# What is held to account here is that the three moved and nothing else did, that the mix has no
# default anywhere to fall back on, and that six older versions still hash as they always did.

#: The fingerprint of policy v7 — v6's declaration with two values moved, plus the dual read.
V7_FINGERPRINT = "3940735d6b1892e8da0b07f876a0f1a933952769f9d3040ff13c38445447638e"


def test_the_dual_read_is_a_row_and_the_ruling_is_the_three_values():
    config = policy.config_from_rows(policy_rows_v7(), bar_rows())
    assert config == declared_config_v7()
    assert config.fingerprint() == V7_FINGERPRINT
    assert config.reading == ReadingPolicy(mix=0.5)
    assert config.distribution.min_shared == 1
    assert dict(config.relations.weights)["derivational"] == 0.45


#: THE STANDING POLICY'S HASH — policy v12 against the live thirty-seven-pair bar.
STANDING_FINGERPRINT = "b400f6c8aa236f605eb826642f918d2c9a22ad0d4b422edb6b72e97eb807cc2e"

#: v11's own hash — the two matrices ruled apart, before gloss references were mined into R. A
#: build read apart must not be able to present the hash of one read blended, and one mining
#: references must not present the hash of one that never did.
V11_FINGERPRINT = "25a3cd7e425e2a48afbdaa5b11d8637bccbe671cfcc7506c079352d9cb094ca3"

#: v10's own hash — the re-fitted NEAR floor, and what the reader ran under while it was still
#: blending. Kept because the build that is sealed on the body was read through it.
V10_FINGERPRINT = "685af0388d3abd25656f6ba507e2c31fef3bf33ed6f004b9edbd84d304718641"

#: v9's own hash — the verdict function as it was FIRST ruled, before the floor was re-fitted hours
#: later. Kept because the correction is the interesting part: this is the number the base was built
#: and sealed under, and `dictionary_builds` still records it.
V9_FINGERPRINT = "9824ef465c86f0f689d4a5220b4d6a0d46d2a6ff8ba7e9d4630539472f16bd71"

#: v8's own hash — the walk ruling without the verdict function. Kept so the floors' arrival is
#: visible as a number of its own, the way `V7_AGAINST_BAR_V2` keeps the bar's growth visible.
V8_FINGERPRINT = "cac116244d11f45b0ef9e086a752f87de3a16e3a61cf31d9ea3a7895b5321a30"

#: What policy v7 hashes to against the GROWN bar — the standing reading between 0011 and 0012, and
#: kept because it is the only place the bar's growth is visible as a number on its own: same policy
#: rows as `V7_FINGERPRINT`, eighteen pairs against thirty-seven.
V7_AGAINST_BAR_V2 = "ef0a3a4702255bf0b2189cde8043a326007f0b01d2afd557f398ac1f35e7c6db"


def test_the_standing_reading_is_policy_v7_against_the_grown_bar():
    """The two constants side by side, so the ONLY thing that separates them is legible: same
    policy rows, two different bars. If a later ruling moves a policy value, this test and
    `V7_FINGERPRINT` move together; if a later bar grows, only this one moves."""
    grown = policy.config_from_rows(policy_rows_v7(), bar_rows() + bar_rows_v2())
    v1 = policy.config_from_rows(policy_rows_v7(), bar_rows())

    assert len(grown.bar) == 37
    assert len(v1.bar) == 18
    assert grown.fingerprint() == V7_AGAINST_BAR_V2
    assert v1.fingerprint() == V7_FINGERPRINT
    assert grown.fingerprint() != v1.fingerprint()
    # Nothing but the bar moved: the policy half of both configs is the same object.
    assert grown.closure == v1.closure
    assert grown.relations == v1.relations
    assert grown.distribution == v1.distribution
    assert grown.reading == v1.reading


def test_the_grown_bar_keeps_every_pair_version_one_declared():
    """Append-mostly, measured: v2 ADDS, it never edits or drops. A bar that could rewrite its own
    history would make «declared before the run» unprovable."""
    v1 = {(p.a, p.b, p.verdict, p.why) for p in policy.bar_from_rows(bar_rows())}
    grown = {(p.a, p.b, p.verdict, p.why) for p in policy.bar_from_rows(bar_rows() + bar_rows_v2())}

    assert v1 < grown
    assert len(grown - v1) == 19


def test_the_grown_bar_can_see_an_opposition_outside_the_verbs():
    """The defect that made the bar grow: at the ruled mix, 167 of the 405 oppositions R states
    read at or above zero — and not one was on the bar, because v1's only two opposition pairs are
    verbs. v2 states one in each of the other three parts of speech."""
    added = list(policy.bar_from_rows(bar_rows_v2()))
    far = [p for p in added if p.verdict == "FAR"]
    pos = {p.a.rsplit(".", 1)[1] for p in far} | {p.b.rsplit(".", 1)[1] for p in far}

    assert {"n", "a", "r"} <= pos
    assert ("employee.n", "employer.n") in {(p.a, p.b) for p in far}
    assert ("mental.a", "physical.a") in {(p.a, p.b) for p in far}
    assert ("externally.r", "internally.r") in {(p.a, p.b) for p in far}


def test_policy_v8_is_the_structure_ruling_and_the_re_ruled_mix():
    """The Captain's ruling of 2026-09-10, in rows: a function word stops being evidence, and D is
    turned down from 0.5 to 0.15. Both were re-measured against the grown bar — neither could have
    been decided against the eighteen, which is why 0011 came first."""
    config = policy.config_from_rows(policy_rows_v8(), bar_rows() + bar_rows_v2())

    assert config == declared_config_v8()
    assert config.fingerprint() == V8_FINGERPRINT
    assert config.distribution.structure == "compiled"
    assert config.reading == ReadingPolicy(mix=0.15)
    assert len(config.bar) == 37


def test_v8_moved_two_values_and_nothing_else():
    """Every other row crosses with its value, its family AND its reason: a ruling is not an
    occasion to quietly re-type the policy around it."""
    v7 = {(r["kind"], r["name"]): (r["value"], r["family"], r["note"]) for r in policy_rows_v7()}
    v8 = {(r["kind"], r["name"]): (r["value"], r["family"], r["note"]) for r in policy_rows_v8()}

    moved = {key for key in v7 if v7[key][0] != v8.get(key, (None,))[0]}
    added = set(v8) - set(v7)

    assert moved == {(policy.KIND_READING, "mix")}
    assert added == {(policy.KIND_DISTRIBUTION, "structure")}
    assert {key: v8[key] for key in v8 if key not in moved | added} == {
        key: v7[key] for key in v7 if key not in moved | added
    }


def test_an_older_policy_is_undeclared_about_structure_and_not_admitted():
    """The distinction the ruling turns on: v6 and v7 never faced the question, so they read `None`
    — and `None` is not the same statement as `admitted`, which is a version that considered it and
    said no. It is also what keeps their recorded fingerprints naming what was measured."""
    v7 = policy.config_from_rows(policy_rows_v7(), bar_rows())
    v8 = policy.config_from_rows(policy_rows_v8(), bar_rows() + bar_rows_v2())

    assert v7.distribution.structure is None
    assert v8.distribution.structure == "compiled"
    assert "structure" not in v7.distribution.as_dict()
    assert v7.distribution.as_dict()["rules"] == v8.distribution.as_dict()["rules"]


def test_policy_v9_turns_a_cosine_into_a_verdict():
    """The last ruling of E1: NEAR at or above +0.27, FAR below zero, ABSTAIN between. Held back
    all epic on purpose — every earlier reading was threshold-free, because a number fitted to a bar
    that cannot see the space is worse than no number."""
    config = policy.config_from_rows(policy_rows_v9(), bar_rows() + bar_rows_v2())

    assert config == declared_config_v9()
    assert config.fingerprint() == V9_FINGERPRINT
    assert config.reading == ReadingPolicy(mix=0.15, near_floor=0.27, far_ceiling=0.0)
    assert config.reading.verdict(0.30) == "NEAR"
    assert config.reading.verdict(0.10) == "ABSTAIN"
    assert config.reading.verdict(-0.05) == "FAR"


def test_policy_v10_refits_the_near_floor_to_the_base_that_was_actually_applied():
    """The correction, and the coupling behind it. `compass.n~compass.v` is a declared FAR that read
    +0.2721 on the APPLIED base against a floor of +0.27, so the policy called it NEAR — and the
    floor had been fitted to that same pair reading +0.2668 on a 4,445-dimension base that no longer
    existed. Requirement 12 makes every bar word a seed, bar v2 added nineteen pairs, and the base
    grew to 4,555: THE BAR AND THE FLOORS ARE COUPLED, and growing one moves the other.

    0.28 sits in the gap between the wall (+0.2721) and the lowest declared NEAR (+0.2843) rather
    than on either endpoint — a floor sitting exactly on the lowest NEAR fails when that pair moves
    by a thousandth, which is precisely how the first one failed.
    """
    config = policy.config_from_rows(policy_rows_v10(), bar_rows() + bar_rows_v2())

    assert config == declared_config_v10()
    assert config.fingerprint() == V10_FINGERPRINT
    assert config.reading.near_floor == 0.28
    assert config.reading.verdict(0.2721) == "ABSTAIN", "the wall no longer reads NEAR"
    assert config.reading.verdict(0.2843) == "NEAR", "the lowest declared NEAR still decides"
    # Only the fitted half moved. The theorem did not, and the walk did not.
    assert config.reading.far_ceiling == 0.0
    assert config.distribution == declared_config_v9().distribution
    assert config.reading.mix == declared_config_v9().reading.mix


def test_v10_moved_one_value_and_the_notes_carry_the_reason():
    v9 = {(r["kind"], r["name"]): (r["value"], r["note"]) for r in policy_rows_v9()}
    v10 = {(r["kind"], r["name"]): (r["value"], r["note"]) for r in policy_rows_v10()}

    moved = {key for key in v9 if v9[key][0] != v10[key][0]}
    assert moved == {(policy.KIND_READING, "near_floor")}
    assert set(v10) == set(v9), "nothing arrived and nothing left"
    # The note has to say WHY, or the ledger records a number nobody can argue with.
    reason = v10[(policy.KIND_READING, "near_floor")][1]
    assert "compass" in reason and "4,555" in reason and "COUPLED" in reason


def test_the_far_edge_is_zero_because_D_cannot_reach_below_it():
    """Not a calibration: D is unsigned, so a negative dual read IS R's sign. The row is written
    anyway — a later ruling may want a margin, and a threshold in code is the defect the standing
    law exists to prevent."""
    config = policy.config_from_rows(policy_rows_v9(), bar_rows() + bar_rows_v2())

    assert config.reading.far_ceiling == 0.0
    assert config.reading.verdict(-1e-9) == "FAR"
    assert config.reading.verdict(0.0) == "ABSTAIN"


def test_a_policy_that_never_ruled_the_floors_refuses_to_judge():
    """v7 and v8 read the bar threshold-free and have no verdict to give. Refusing is the point:
    inventing one here would put an acceptance threshold in code."""
    v8 = policy.config_from_rows(policy_rows_v8(), bar_rows() + bar_rows_v2())

    assert not v8.reading.decides
    assert "near_floor" not in v8.reading.as_dict()
    with pytest.raises(ValueError, match="no acceptance floors"):
        v8.reading.verdict(0.5)


def test_the_two_edges_are_declared_together_or_not_at_all():
    """One without the other is a verdict function with a side it cannot answer on — and a crossed
    pair would make some reading both NEAR and FAR."""
    with pytest.raises(ValueError, match="together or not at all"):
        ReadingPolicy(mix=0.15, near_floor=0.27)
    with pytest.raises(ValueError, match="must sit ABOVE"):
        ReadingPolicy(mix=0.15, near_floor=-0.1, far_ceiling=0.0)


def test_v9_moved_nothing_and_only_added_the_two_edges():
    v8 = {(r["kind"], r["name"]): (r["value"], r["family"], r["note"]) for r in policy_rows_v8()}
    v9 = {(r["kind"], r["name"]): (r["value"], r["family"], r["note"]) for r in policy_rows_v9()}

    assert set(v9) - set(v8) == {
        (policy.KIND_READING, "near_floor"),
        (policy.KIND_READING, "far_ceiling"),
    }
    assert {k: v9[k] for k in v8} == v8


def test_the_mix_is_its_own_kind_and_not_a_setting_of_D():
    """A row filed under `distribution` would say that D owns how loudly it is heard. It is a
    property of reading the two matrices at once, and neither matrix's."""
    v7 = {(r["kind"], r["name"]) for r in policy_rows_v7()}
    assert (policy.KIND_READING, "mix") in v7
    assert (policy.KIND_DISTRIBUTION, "mix") not in v7
    assert [r["family"] for r in policy_rows_v7() if r["kind"] == policy.KIND_READING] == ["dual"]


def test_an_undeclared_mix_is_a_refusal_and_never_a_silent_default():
    """The law the lemma scope and the antonym reading carry, applied to the third parameter that
    earned it: `None` from the rows, nothing invented, and a config that says so in `as_dict`."""
    assert policy.reading_from_rows(_closure_rows()) is None
    v6 = policy.config_from_rows(policy_rows_v6(), bar_rows())
    assert v6.reading is None and "reading" not in v6.as_dict()
    with pytest.raises(ValueError):
        v6.with_reading(mix=0.5)


def test_an_unknown_reading_setting_is_refused_not_ignored():
    rows = [_policy_row(policy.KIND_READING, "mix", 0.5),
            _policy_row(policy.KIND_READING, "floor", 0.30)]
    with pytest.raises(policy.PolicyRowsInvalid) as excinfo:
        policy.reading_from_rows(rows)
    assert "floor" in str(excinfo.value), "the acceptance floors are T5's, and they are not this row"


def test_a_negative_mix_is_refused_at_the_row():
    """It would flip every D cell's sign, and D is unsigned by construction — the sign is R's alone
    and it is the antonym column-read primitive."""
    with pytest.raises(policy.PolicyRowsInvalid):
        policy.reading_from_rows([_policy_row(policy.KIND_READING, "mix", -0.5)])
    with pytest.raises(ValueError):
        ReadingPolicy(mix=-1.0)


def test_a_mix_of_zero_is_a_declaration_and_not_an_absence():
    """«The dual read is R alone» is a thing a policy may say, and it must not read as «unset»."""
    reading = policy.reading_from_rows([_policy_row(policy.KIND_READING, "mix", 0.0)])
    assert reading == ReadingPolicy(mix=0.0)


def test_a_dual_read_declared_over_no_D_is_refused():
    """The mix says how loudly the SECOND geometry speaks; without one it describes a reading of a
    matrix nobody was asked to build. Refused where rows become a thing a build measures under —
    `reading_from_rows` next door still reads them, because looking at a policy must stay possible."""
    rows = _closure_rows() + [_policy_row(policy.KIND_READING, "mix", 0.5)]
    assert policy.reading_from_rows(rows) == ReadingPolicy(mix=0.5)
    with pytest.raises(policy.PolicyRowsInvalid) as excinfo:
        policy.config_from_rows(rows, bar_rows())
    assert "no gloss walk" in str(excinfo.value)


def test_every_value_that_moved_says_in_numbers_what_moved_it():
    """A ruled value whose reason is «the Captain said so» is one nobody can argue with later. Each
    of the three carries the sweep that produced it, and the four measured-and-standing rows carry
    what was measured about them — so no reader re-litigates a closed question blind."""
    notes = {(r["kind"], r["name"]): r["note"] for r in policy_rows_v7()}

    moved = notes[(policy.KIND_DISTRIBUTION, "min_shared")]
    assert "1,670,286" in moved and "153,830" in moved and "19,524" in moved
    assert "47 of 80" in moved and "26 of 80" in moved

    halved = notes[(policy.KIND_RELATION_WEIGHT, "derivational")]
    assert "PEAK" in halved and "0.45 -> 67" in halved and "0.30 -> 66" in halved

    mix = notes[(policy.KIND_READING, "mix")]
    assert "+0.063" in mix and "-0.059" in mix and "58/80 -> 67/80" in mix
    assert "NO DEFAULT" in mix.upper()
    # The sweep's four numbers were taken at the PRE-ruling derivational, and the note says so and
    # says what they become under the whole ruling — a number whose conditions are lost is a number
    # the next reader cannot reproduce.
    assert "derivational` 0.90" in mix and "+0.065" in mix and "-0.062" in mix

    # The two parked questions, closed by rejection — with their numbers, not their verdicts alone.
    assert "12,925" in notes[(policy.KIND_DISTRIBUTION, "senses")]
    assert "+0.759" in notes[(policy.KIND_CLOSURE, "senses")]
    assert "35.7%" in notes[(policy.KIND_DISTRIBUTION, "weighting")]
    assert "10.4%" in notes[(policy.KIND_DISTRIBUTION, "weighting")]
    # And the two that could not be seen at all behind the old gate.
    for name in ("measure", "vocabulary"):
        assert "UNOBSERVABLE" in notes[(policy.KIND_DISTRIBUTION, name)].upper()


def test_version_7_carries_version_6_forward_except_the_two_it_moved():
    """A build reads ONE version, so v7 is a WHOLE policy — and every row that did not move must be
    v6's own value AND v6's own reason, not a re-typing of either."""
    v6 = {(r["kind"], r["name"]): (r["value"], r["family"], r["note"]) for r in policy_rows_v6()}
    v7 = {(r["kind"], r["name"]): (r["value"], r["family"], r["note"]) for r in policy_rows_v7()}

    assert set(v7) - set(v6) == {(policy.KIND_READING, "mix")}
    moved_value = {key for key in v6 if key in v7 and v7[key][0] != v6[key][0]}
    assert moved_value == {(policy.KIND_DISTRIBUTION, "min_shared"),
                           (policy.KIND_RELATION_WEIGHT, "derivational")}

    # The rows whose NOTE moved without their value: the four measured-and-standing, and they only
    # ever GAIN text — v6's argument for the value is what a later reader still needs.
    moved_note = {key for key in v6 if key in v7 and v7[key][2] != v6[key][2]} - moved_value
    assert moved_note == {(policy.KIND_DISTRIBUTION, "measure"),
                          (policy.KIND_DISTRIBUTION, "vocabulary"),
                          (policy.KIND_DISTRIBUTION, "senses"),
                          (policy.KIND_DISTRIBUTION, "weighting"),
                          (policy.KIND_DISTRIBUTION, "cap"),
                          (policy.KIND_CLOSURE, "senses")}
    for key in moved_note:
        assert v7[key][2].startswith(v6[key][2]), "a reason is extended, never replaced"

    unmoved = set(v6) - moved_value - moved_note
    assert {k: v6[k] for k in unmoved} == {k: v7[k] for k in unmoved}


def test_the_relation_order_survives_the_reweighting():
    """The declared order IS the cell walk's precedence, so rebuilding the weight tuple to change
    one number must not reorder it — that would be a second, silent ruling riding along."""
    v6 = policy.config_from_rows(policy_rows_v6(), bar_rows()).relations
    v7 = policy.config_from_rows(policy_rows_v7(), bar_rows()).relations
    assert v7.relations == v6.relations
    assert {name: w for name, w in v7.weights if w != dict(v6.weights)[name]} == {
        "derivational": 0.45
    }


def test_the_six_older_versions_still_hash_as_they_did():
    """`as_dict` writes nothing about a dual read a policy never declared, so every manifest row
    naming v1-v6 keeps meaning what it meant — and a v7 build cannot be mistaken for any of them."""
    assert policy.config_from_rows(policy_rows(), bar_rows()).fingerprint() == T2B_FINGERPRINT
    assert policy.config_from_rows(policy_rows_v2(), bar_rows()).fingerprint() == RULED_FINGERPRINT
    assert policy.config_from_rows(policy_rows_v3(), bar_rows()).fingerprint() == V3_FINGERPRINT
    assert policy.config_from_rows(policy_rows_v4(), bar_rows()).fingerprint() == V4_FINGERPRINT
    assert policy.config_from_rows(policy_rows_v5(), bar_rows()).fingerprint() == V5_FINGERPRINT
    assert policy.config_from_rows(policy_rows_v6(), bar_rows()).fingerprint() == V6_FINGERPRINT
    assert len({T2B_FINGERPRINT, RULED_FINGERPRINT, V3_FINGERPRINT, V4_FINGERPRINT,
                V5_FINGERPRINT, V6_FINGERPRINT, V7_FINGERPRINT}) == 7


def test_a_dual_read_written_back_out_as_rows_reads_back_the_same():
    """The round trip, for the tenth kind of row."""
    config = declared_config_v7()
    written = policy.policy_rows_of(config, version=7)
    assert policy.config_from_rows(written, policy.bar_rows_of(config.bar, 1)) == config


# ------------------------------------------------------------------------------------------------
# v11 — the two matrices are read APART
# ------------------------------------------------------------------------------------------------


def test_policy_v11_rules_the_reading_mode_and_moves_nothing_else():
    """E1d T2. Requirement 10 has said since 2026-08-12 that R and D are «consulted separately,
    every answer naming its source, never blended into one float» — and the reader returned
    `cos(R + 0.15*D)` for a month. The E1 audit found it; the Captain ruled `separate`.

    ONE VALUE ARRIVES AND NOTHING ELSE MOVES: the mix, both floors, the walks and the seeds are all
    v10's. What changes is what a VERDICT MEANS, which is exactly why it is a row.
    """
    from tk2.dictionary.config import READING_SEPARATE

    config = policy.config_from_rows(policy_rows_v11(), bar_rows() + bar_rows_v2())

    assert config == declared_config_v11()
    assert config.reading.mode == READING_SEPARATE
    assert config.reading.reads_separately
    assert config.fingerprint() == V11_FINGERPRINT

    # the ledger's promise: v10 still hashes to what v10 measured
    assert declared_config_v10().fingerprint() == V10_FINGERPRINT
    assert config.fingerprint() != V10_FINGERPRINT, "a mode change is a different reading"


def test_v11_carries_every_v10_value_untouched():
    v10 = {(r["kind"], r["name"]): r["value"] for r in policy_rows_v10()}
    v11 = {(r["kind"], r["name"]): r["value"] for r in policy_rows_v11()}

    arrived = set(v11) - set(v10)
    assert arrived == {(policy.KIND_READING, "mode")}, "one row arrives and none leaves"
    assert not {k for k in v10 if v10[k] != v11[k]}, "no v10 value moved"


def test_v11s_note_carries_the_measurement_that_settled_it():
    """A ruling without the number that produced it is an opinion with a version attached."""
    note = next(r["note"] for r in policy_rows_v11()
                if (r["kind"], r["name"]) == (policy.KIND_READING, "mode"))

    assert "never blended into one float" in note, "the requirement it repairs"
    assert "0.338" in note and "0.326" in note, "the pair that proves D cannot decide"
    assert "15 of the 18" in note, "what R alone decides"
    assert "thick.a~thin.a" in note, "the sign the blend was drowning"


def test_the_earlier_versions_never_declared_a_mode_and_must_keep_saying_nothing():
    """UNDECLARED is not «blended». v7-v10 ruled the mix and never faced this question, and a
    default here would be a reading the manifest cannot vouch for."""
    for rows in (policy_rows_v7(), policy_rows_v8(), policy_rows_v9(), policy_rows_v10()):
        reading = policy.reading_from_rows(rows)
        assert reading.mode is None
        assert not reading.reads_separately
        assert "mode" not in reading.as_dict()


# ------------------------------------------------------------------------------------------------
# v12 — a definition that names a word is stating something
# ------------------------------------------------------------------------------------------------


def test_policy_v12_mines_gloss_references_and_lets_a_stated_cell_decide():
    """E1d T3. Requirement 2 was REFUTED at scale — `eat.v~food.n` reads D cosine +0.0484 and D
    direct cell 0.0000, because their definitions share nothing. The relation is that eat's
    definition NAMES food, which is R's kind of claim and was never mined."""
    from tk2.dictionary import references

    config = policy.config_from_rows(policy_rows_v12(), bar_rows() + bar_rows_v2())
    weights = dict(config.relations.weights)

    assert config == declared_config_v12()
    assert weights[references.GLOSS_REFERENCE] == 0.9
    assert weights[references.GLOSS_REFERENCE_RECIPROCAL] == 0.54
    assert config.reading.cell_decides is True
    assert config.fingerprint() == STANDING_FINGERPRINT


def test_v12_says_which_relations_may_not_decide_and_which_stay_out_of_the_cosine():
    from tk2.dictionary import references

    reading = policy.config_from_rows(policy_rows_v12(), bar_rows()).reading

    # `derivational` states «same root», not «same meaning» — req 16, and the reason land.n~land.v,
    # compass.n~compass.v and play.n~play.v are declared FAR and read positive.
    assert not reading.decides_by_cell("derivational")
    assert not reading.decides_by_cell(references.GLOSS_REFERENCE_AMBIGUOUS)
    assert reading.decides_by_cell(references.GLOSS_REFERENCE)
    assert reading.decides_by_cell("hypernym_1")

    # Reference cells are claims about a PAIR. Measured: with them in the cosine and the reciprocal
    # on, land.n~land.v, state.n~state.v and play.n~play.v all flip to a wrong NEAR.
    assert not reading.enters_the_cosine(references.GLOSS_REFERENCE)
    assert not reading.enters_the_cosine(references.GLOSS_REFERENCE_RECIPROCAL)
    assert reading.enters_the_cosine("derivational"), "structural, but still a profile statement"
    assert reading.enters_the_cosine("antonym")


def test_v12_adds_rows_and_takes_none_away():
    """A first draft of `db/0004` rebuilt `RelationPolicy` field by field and DROPPED `defaults`,
    which silently un-declared six `curation_default` rows. Caught by counting kinds, not by reading
    the code — so the count is held here from now on."""
    from collections import Counter

    before = Counter(r["kind"] for r in policy_rows_v11())
    after = Counter(r["kind"] for r in policy_rows_v12())

    assert all(after[kind] >= before[kind] for kind in before), "a version may not un-declare"
    assert after["relation_weight"] - before["relation_weight"] == 3
    assert after["reading"] - before["reading"] == 3


def test_the_relation_sets_travel_as_readable_rows():
    """One name, one value: a nested document would not be greppable in the collection."""
    rows = {(r["kind"], r["name"]): r["value"] for r in policy_rows_v12()}

    assert rows[(policy.KIND_READING, "structural_relations")] == \
        "derivational,gloss_reference_ambiguous"
    assert "gloss_reference_reciprocal" in rows[(policy.KIND_READING, "reference_relations")]


def test_every_version_before_twelve_keeps_saying_nothing_about_the_cell_rule():
    for rows in (policy_rows_v9(), policy_rows_v10(), policy_rows_v11()):
        reading = policy.reading_from_rows(rows)
        assert reading.cell_decides is None
        assert reading.structural_relations is None
        assert not reading.decides_by_cell("hypernym_1"), "undeclared means the cell cannot decide"
        assert reading.enters_the_cosine("anything"), "and nothing is held out of the cosine"


def test_the_closed_classes_are_found_even_when_the_newest_migration_never_declares_them():
    """A LATENT BUG, live from the day `db/0002` landed and found by E1d T3 on 2026-09-14.

    `closed_forms(None)` asked the NEWEST POLICY migration for the closed-class rows — but a later
    version declares only what it CHANGES, and only the baseline declares those. It raised
    `AttributeError` for four days and nothing noticed, because the offline path is the one that
    runs BEFORE a migration is applied, which is exactly the path that must not assume.
    """
    from tk2.datatier.policy_source import closed_forms, newest_migration_declaring

    forms, source = closed_forms(None)

    assert len(forms) > 200 and "the" in forms
    assert "0001" in source, "the baseline is what declares them"

    found, module = newest_migration_declaring("POLICY_ROWS")
    assert found.number >= 4, "and the newest POLICY is still found the other way"
