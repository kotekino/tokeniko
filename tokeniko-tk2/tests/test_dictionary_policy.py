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
"""

import json

import pytest

from tests.seed import bar_rows, declared_config, policy_rows
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
