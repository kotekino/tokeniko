"""The runner: discovery, the ledger, immutability — and 0001 actually creating the world."""

from pathlib import Path

import pytest

from tk2 import migrations
from tk2.core import constants
from tk2.core.models import (
    ALL_MODELS,
    HeartAnatomy,
    HeartAnatomyDoc,
    HeartLevelDoc,
    HeartMoodDoc,
    HeartTemperamentDoc,
    ParamDoc,
)
from tk2.core.models.migrations import MigrationDoc
from tk2.datatier import traps
from tests.seed import (
    all_poles,
    bar_rows,
    closed_class_forms,
    closed_class_rows,
    param_rows,
    policy_rows,
    policy_rows_v2,
    policy_rows_v3,
    policy_rows_v4,
    policy_rows_v5,
    policy_rows_v6,
    policy_rows_v7,
    sphere_poles,
)


# ------------------------------------------------------------------------------------------------
# discovery — pure
# ------------------------------------------------------------------------------------------------


def _write(directory: Path, filename: str, body: str = "def up(writer, db):\n    pass\n") -> Path:
    path = directory / filename
    path.write_text(body)
    return path


def test_migrations_are_found_in_number_order(tmp_path):
    _write(tmp_path, "0003_c.py")
    _write(tmp_path, "0001_a.py")
    _write(tmp_path, "0002_b.py")
    assert [m.number for m in migrations.discover(tmp_path)] == [1, 2, 3]


def test_files_that_are_not_migrations_are_ignored(tmp_path):
    _write(tmp_path, "0001_a.py")
    _write(tmp_path, "README.md", "not python")
    _write(tmp_path, "helper.py")
    _write(tmp_path, "1_short.py")
    assert [m.label for m in migrations.discover(tmp_path)] == ["0001_a"]


def test_two_migrations_with_one_number_are_refused(tmp_path):
    """The number IS the order; two files cannot hold one position."""
    _write(tmp_path, "0001_a.py")
    _write(tmp_path, "0001_b.py")
    with pytest.raises(migrations.MigrationError) as excinfo:
        migrations.discover(tmp_path)
    assert "0001" in str(excinfo.value)


def test_a_missing_directory_is_an_error(tmp_path):
    with pytest.raises(migrations.MigrationError):
        migrations.discover(tmp_path / "nowhere")


def test_a_migration_without_up_is_refused(tmp_path):
    _write(tmp_path, "0001_empty.py", "X = 1\n")
    with pytest.raises(migrations.MigrationError) as excinfo:
        migrations.discover(tmp_path)[0].load()
    assert "up(writer, db)" in str(excinfo.value)


def test_the_checksum_follows_the_file(tmp_path):
    path = _write(tmp_path, "0001_a.py")
    before = migrations.discover(tmp_path)[0].checksum()
    path.write_text("def up(writer, db):\n    return 1\n")
    assert migrations.discover(tmp_path)[0].checksum() != before


def test_the_real_directory_is_found_by_default():
    """The package finds `db/` beside itself, so the runner works from any working directory."""
    found = migrations.discover()
    assert [m.label for m in found][:4] == [
        "0001_create_the_world",
        "0002_bump_the_dictionary_epoch",
        "0003_the_dictionary_policy_becomes_rows",
        "0004_the_closed_classes_become_rows",
    ]


# ------------------------------------------------------------------------------------------------
# the ledger — live
# ------------------------------------------------------------------------------------------------

live = pytest.mark.mongo


@pytest.fixture
def empty_db(test_db):
    """A database with nothing in it, including no migration history.

    `system.*` is skipped deliberately: mongo refuses to drop `system.views` while a timeseries
    collection is present, and those are its bookkeeping anyway — dropping the timeseries collection
    itself takes its buckets with it.
    """
    for name in test_db.list_collection_names():
        if name.startswith("system."):
            continue
        test_db.drop_collection(name)

    yield test_db

    # Put the session's collections back. The drops above took out the TIMESERIES collections too,
    # and a later test that merely inserts would get a plain collection auto-created in their place
    # — passing while testing something else entirely. Re-registering rebuilds them with their real
    # configuration.
    from bunnet import init_bunnet

    from tests.models import ALL_MODELS as TEST_MODELS

    init_bunnet(database=test_db, document_models=[*ALL_MODELS, *TEST_MODELS])


@live
def test_everything_is_pending_on_a_fresh_database(empty_db, tmp_path):
    _write(tmp_path, "0001_a.py")
    _write(tmp_path, "0002_b.py")
    assert [m.number for m in migrations.pending(empty_db, tmp_path)] == [1, 2]


@live
def test_applying_records_the_ledger_row(empty_db, tmp_path):
    _write(tmp_path, "0001_a.py")
    migration = migrations.discover(tmp_path)[0]

    migrations.apply(empty_db, migration)

    row = empty_db[MigrationDoc.Settings.name].find_one({"number": 1})
    assert row["name"] == "a"
    assert row["checksum"] == migration.checksum()
    assert row["applied_at"] > 0


@live
def test_an_applied_migration_is_not_pending_again(empty_db, tmp_path):
    _write(tmp_path, "0001_a.py")
    migrations.migrate(empty_db, tmp_path)
    assert migrations.pending(empty_db, tmp_path) == []


@live
def test_migrate_is_idempotent(empty_db, tmp_path):
    _write(tmp_path, "0001_a.py", "def up(writer, db):\n    db['probe'].insert_one({'n': 1})\n")

    assert len(migrations.migrate(empty_db, tmp_path)) == 1
    assert len(migrations.migrate(empty_db, tmp_path)) == 0

    assert empty_db["probe"].count_documents({}) == 1


@live
def test_migrations_run_in_order(empty_db, tmp_path):
    body = "def up(writer, db):\n    db['probe'].insert_one({{'n': {n}}})\n"
    _write(tmp_path, "0002_b.py", body.format(n=2))
    _write(tmp_path, "0001_a.py", body.format(n=1))

    migrations.migrate(empty_db, tmp_path)

    assert [d["n"] for d in empty_db["probe"].find({})] == [1, 2]


@live
def test_a_failing_migration_is_not_recorded(empty_db, tmp_path):
    """A half-applied migration that claimed to be finished is the worst state to leave a database
    in; re-running is at least something a person can reason about."""
    _write(tmp_path, "0001_boom.py", "def up(writer, db):\n    raise RuntimeError('boom')\n")

    with pytest.raises(RuntimeError):
        migrations.migrate(empty_db, tmp_path)

    assert empty_db[MigrationDoc.Settings.name].count_documents({}) == 0
    assert len(migrations.pending(empty_db, tmp_path)) == 1


@live
def test_editing_an_applied_migration_is_refused(empty_db, tmp_path):
    """An applied migration is IMMUTABLE: the database already holds what the old file did."""
    path = _write(tmp_path, "0001_a.py")
    migrations.migrate(empty_db, tmp_path)

    path.write_text("def up(writer, db):\n    db['probe'].insert_one({'oops': 1})\n")

    with pytest.raises(migrations.MigrationError) as excinfo:
        migrations.pending(empty_db, tmp_path)
    assert "immutable" in str(excinfo.value)
    assert "NEW migration" in str(excinfo.value)


@live
def test_the_body_cannot_write_the_ledger(empty_db):
    """A deploy is something that happens TO him."""
    from tk2.core.write_class import WriteClassViolation

    with pytest.raises(WriteClassViolation):
        MigrationDoc.insert_one({"number": 1})


# ------------------------------------------------------------------------------------------------
# 0001 creates the world
# ------------------------------------------------------------------------------------------------


@pytest.fixture
def created(empty_db):
    """The world, as migration 0001 leaves it."""
    migrations.migrate(empty_db)
    return empty_db


@live
def test_0001_creates_every_collection(created):
    names = set(created.list_collection_names())
    for model in ALL_MODELS:
        assert model.Settings.name in names, f"{model.Settings.name} was not created"


@live
def test_0001_seeds_the_parameters(created):
    stored = {r["key"]: r["value"] for r in created["params"].find({})}
    assert stored[constants.RCACHE_INTERVAL_PARAM] == constants.RCACHE_INTERVAL_DEFAULT
    assert stored[constants.BODY_TICK_PARAM] == constants.BODY_TICK_DEFAULT
    assert constants.DICTIONARY_EPOCH_PARAM in stored
    assert "evaluator.budget.max_depth" in stored


@live
def test_every_seeded_param_key_follows_the_house_convention(created):
    """`component.concern.setting` — dotted, most general first."""
    for row in created["params"].find({}):
        assert len(row["key"].split(".")) >= 3, row["key"]
        assert row["key"] == row["key"].lower()


@live
def test_every_seeded_param_explains_itself(created):
    """These rows are read by human probes; a number with no note is a mystery."""
    for row in created["params"].find({}):
        assert row["note"].strip(), row["key"]


@live
def test_0001_seeds_a_coherent_anatomy(created):
    rows = traps.find_all(HeartAnatomyDoc)
    heart = HeartAnatomy(rows)

    heart.check_coherent()
    assert len(rows) == 15
    assert len(heart.spheres()) == 6
    assert len(heart.spikes()) == 3


@live
def test_0001_gives_the_newborn_his_levels(created):
    """The first tick reads them; a tick that has to cope with a missing pole has to guess what
    «missing» means."""
    levels = {row.pole: row.level for row in traps.find_all(HeartLevelDoc)}
    assert set(levels) == set(all_poles())
    assert all(v == 0.0 for v in levels.values())


@live
def test_mood_and_temperament_cover_the_spheres_only(created):
    """A spike fires and decays inside one tick; averaging it over a slow window would smear an
    event into a disposition."""
    assert {r.pole for r in traps.find_all(HeartMoodDoc)} == set(sphere_poles())
    assert {r.pole for r in traps.find_all(HeartTemperamentDoc)} == set(sphere_poles())


@live
def test_0001_seeds_no_knowledge(created):
    """It creates a body, not a mind: no dictionary, no beliefs, no micro-nn instances."""
    assert created["micro_nn_instances"].count_documents({}) == 0
    assert created["forecasts"].count_documents({}) == 0
    assert created["derived_points"].count_documents({}) == 0


@live
def test_0002_moves_the_epoch(created):
    """Both migrations run in `created`; 0002 is what the gate applies to a LIVE body."""
    row = created["params"].find_one({"key": constants.DICTIONARY_EPOCH_PARAM})
    assert row["value"] == 1


@live
def test_the_seeded_params_are_exactly_what_the_migration_declares(created):
    assert {r["key"] for r in created["params"].find({})} == {r["key"] for r in param_rows()}


@live
def test_the_body_still_cannot_write_what_the_migration_wrote(created):
    from tk2.core.write_class import WriteClassViolation

    with pytest.raises(WriteClassViolation):
        traps.insert(ParamDoc(key="body.sneaks.in", value=1))
    with pytest.raises(WriteClassViolation):
        traps.insert(HeartAnatomyDoc(pole="smugness", targets=["self"]))


# ------------------------------------------------------------------------------------------------
# 0003 puts the dictionary's policy in rows
# ------------------------------------------------------------------------------------------------


@live
def test_0003_creates_the_dictionary_tables_including_the_ledger(created):
    """The ledger is created here even though it is not in `ALL_MODELS`: a table the body does not
    read still has to exist before the first build writes its manifest row."""
    names = set(created.list_collection_names())
    for name in ("dictionary_policy", "dictionary_bar", "dictionary_builds"):
        assert name in names, f"{name} was not created"


@live
def test_0003_writes_the_policy_and_the_bar_as_declared(created):
    """VERSION-EXPLICIT since 0005, and that is the table working rather than the test bending: the
    collection holds v1 AND v2, a v1 manifest row still has to point at something readable, and a
    query that named no version would be asking «the policy» of a ledger that holds two."""
    stored_policy = [r for r in created["dictionary_policy"].find({}) if r["version"] == 1]
    stored_bar = list(created["dictionary_bar"].find({}))

    assert {(r["kind"], r["name"]) for r in stored_policy} == {
        (r["kind"], r["name"]) for r in policy_rows()
    }
    assert {(r["a"], r["b"], r["verdict"]) for r in stored_bar} == {
        (r["a"], r["b"], r["verdict"]) for r in bar_rows()
    }
    assert {r["version"] for r in stored_policy} == {1}
    assert {r["version"] for r in stored_bar} == {1}
    # Epoch-stamped, and live: the two ledger properties that justified moving the bar out of code.
    assert all(r["created_at"] > 0 for r in stored_bar)
    assert all(r["retired_at"] is None for r in stored_bar)


@live
def test_the_policy_read_back_from_the_database_is_the_one_that_was_declared(created):
    """The seam end to end: rows out of mongo, through the pure reader, into the value object the
    engine takes as an argument — and version 1 still fingerprints to what T2b measured, with 0005
    applied on top of it. THAT is the ledger's promise: a recorded hash keeps naming the policy the
    build that recorded it really ran."""
    from tests.test_dictionary_policy import T2B_FINGERPRINT
    from tk2.dictionary import policy

    stored_policy = [r for r in created["dictionary_policy"].find({}) if r["version"] == 1]
    stored_bar = list(created["dictionary_bar"].find({}))
    config = policy.config_from_rows(stored_policy, stored_bar)

    assert config.fingerprint() == T2B_FINGERPRINT
    assert policy.policy_version(stored_policy) == 1
    assert policy.bar_version(stored_bar) == 1
    assert policy.bar_fingerprint(stored_bar) == policy.bar_snapshot()["fingerprint"]


@live
def test_reading_the_policy_without_naming_a_version_is_refused(created):
    """The other half of the same lesson, as behaviour rather than as care: the whole table read at
    once is not a policy, and `policy_version` says so instead of picking one."""
    from tk2.dictionary import policy

    stored = list(created["dictionary_policy"].find({}))
    with pytest.raises(policy.PolicyRowsInvalid):
        policy.policy_version(stored)
    # The NEWEST, whichever it is: this test is about the refusal and the explicit selection, and a
    # version number in it would have to be edited every time the Captain rules.
    assert policy.policy_version(policy.latest_version(stored)) == max(r["version"] for r in stored)


# ------------------------------------------------------------------------------------------------
# 0004 puts English's closed classes in rows
# ------------------------------------------------------------------------------------------------


@live
def test_0004_writes_the_closed_classes_as_declared(created):
    """One table replacing tk1's four hand lists, and E1's exclusion set at the same time."""
    stored = list(created["closed_classes"].find({}))
    declared = closed_class_rows()

    assert {(r["form"], r["word_class"], r["role"]) for r in stored} == {
        (r["form"], r["word_class"], r["role"]) for r in declared
    }
    assert {r["version"] for r in stored} == {1}
    # E3's column is empty by construction — what a form compiles TO is a tkzip question.
    assert all(r["compiled"] == {} for r in stored)


@live
def test_the_closed_classes_read_back_as_the_exclusion_set(created):
    """What `tools/propose_seeds.py` reads when a body is reachable: the same forms it would have
    read off the migration file, so a proposal measured before the apply and one measured after are
    the same measurement."""
    stored = list(created["closed_classes"].find({}))
    assert {r["form"] for r in stored if " " not in r["form"]} == set(closed_class_forms())


@live
def test_the_body_cannot_write_the_closed_classes(created):
    """A contingent fact about one language, and still not his to edit: it arrives by migration."""
    from tk2.core.models import ClosedClassDoc
    from tk2.core.write_class import WriteClassViolation

    with pytest.raises(WriteClassViolation):
        ClosedClassDoc.insert_one({"form": "sneak"})


@live
def test_the_body_cannot_write_the_dictionarys_policy(created):
    """Curation is authorized judgment, and the authorization is not his. Every one of these tables
    is `logic`: the migration door writes them, the body reads them."""
    from tk2.core.models import DictionaryBarDoc, DictionaryBuildDoc, DictionaryPolicyDoc
    from tk2.core.write_class import WriteClassViolation

    for model in (DictionaryPolicyDoc, DictionaryBarDoc, DictionaryBuildDoc):
        with pytest.raises(WriteClassViolation):
            model.insert_one({"whatever": 1})


# ------------------------------------------------------------------------------------------------
# 0005 rules the seeds and demotes the size cap
# ------------------------------------------------------------------------------------------------


@live
def test_0005_writes_policy_version_2_beside_version_1_and_not_over_it(created):
    """A ledger, not an edit. Both versions are in the table afterwards, and v1 is untouched — the
    one property that makes an old manifest row mean anything at all."""
    stored = list(created["dictionary_policy"].find({}))
    v1 = [r for r in stored if r["version"] == 1]
    v2 = [r for r in stored if r["version"] == 2]

    assert {1, 2} <= {r["version"] for r in stored}, "both versions are in the table afterwards"
    assert len(v1) == len(policy_rows())
    assert len(v2) == len(policy_rows_v2())
    assert {(r["kind"], r["name"]) for r in v2} == {(r["kind"], r["name"]) for r in policy_rows_v2()}
    # The bar did not move with it: it is a separate, append-mostly table and v2 is measured against
    # the same eighteen pairs.
    assert {r["version"] for r in created["dictionary_bar"].find({})} == {1}


@live
def test_the_ruled_policy_reads_back_as_the_one_the_captain_ruled(created):
    """The seam again, at version 2: rows out of mongo, through the pure reader, and the closure
    cuts and seed count are the ones the ruling names.

    VERSION-EXPLICIT since 0006 wrote v3 on top. The table is a ledger and now holds three, so
    «the ruled policy» is a version somebody names — which is exactly what a manifest row does.
    """
    from tests.test_dictionary_policy import RULED_FINGERPRINT
    from tk2.dictionary import policy

    stored = [r for r in created["dictionary_policy"].find({}) if r["version"] == 2]
    stored_bar = list(created["dictionary_bar"].find({}))
    config = policy.config_from_rows(stored, stored_bar)

    assert policy.policy_version(stored) == 2
    assert config.closure.max_size == 25_000
    assert config.closure.max_depth == 2
    assert config.fingerprint() == RULED_FINGERPRINT


@live
def test_a_seed_cannot_hold_two_rows_in_one_version(created):
    """The unique index, on the case that would really have hit it: `land` is a purpose seed AND
    #197 of the structural ranking, and a union that wrote it twice would have failed here."""
    from pymongo.errors import DuplicateKeyError

    with pytest.raises(DuplicateKeyError):
        created["dictionary_policy"].insert_one(
            {"version": 2, "kind": "seed", "name": "land", "value": None,
             "family": "structure", "position": 999, "note": "", "created_at": 1}
        )


# ------------------------------------------------------------------------------------------------
# 0006 puts R's weights, the curated vocabulary and the alphabet in rows
# ------------------------------------------------------------------------------------------------


@live
def test_0006_writes_policy_version_3_beside_the_two_before_it(created):
    """A ledger, three deep. v1 and v2 are untouched — the property that keeps an old manifest row
    meaningful, checked again because it is the property most easily lost."""
    stored = list(created["dictionary_policy"].find({}))
    by_version = {v: [r for r in stored if r["version"] == v] for v in (1, 2, 3)}

    assert {1, 2, 3} <= {r["version"] for r in stored}
    assert len(by_version[1]) == len(policy_rows())
    assert len(by_version[2]) == len(policy_rows_v2())
    assert len(by_version[3]) == len(policy_rows_v3())
    assert {(r["kind"], r["name"]) for r in by_version[3]} == {
        (r["kind"], r["name"]) for r in policy_rows_v3()
    }
    # The bar still has not moved: it is a separate, append-mostly table, and a policy ruling is not
    # an occasion to re-declare the expectation the ruling will be judged by.
    assert {r["version"] for r in created["dictionary_bar"].find({})} == {1}


@live
def test_the_relation_weights_read_back_as_the_matrix_they_describe(created):
    """The seam, at version 3: rows out of mongo, through the pure reader, into the value object R
    is filled from — signs, precedence, curated vocabulary and alphabet included.

    VERSION-EXPLICIT since 0007 wrote v4 on top, for the reason 0006 made v2's test explicit."""
    from tests.test_dictionary_policy import V3_FINGERPRINT
    from tk2.dictionary import policy

    stored = [r for r in created["dictionary_policy"].find({}) if r["version"] == 3]
    config = policy.config_from_rows(stored, list(created["dictionary_bar"].find({})))

    assert policy.policy_version(stored) == 3
    assert config.fingerprint() == V3_FINGERPRINT
    assert dict(config.relations.weights)["antonym"] == -1.0
    assert config.relations.reciprocal_weight == 0.60
    assert config.alphabet.order == ("n", "v", "a", "r")


@live
def test_0006_creates_the_bases_own_collections_empty(created):
    """`base_keys` and `base_r` are made by the DEPLOY and filled by the BUILD. A build that had to
    create its own tables would be a build doing a deploy's job — and the collections have to exist
    before the first one runs."""
    from tk2.core.models import BaseKeyDoc, BaseRelationDoc

    names = set(created.list_collection_names())
    for model in (BaseKeyDoc, BaseRelationDoc):
        assert model.Settings.name in names, f"{model.Settings.name} was not created"
        assert created[model.Settings.name].count_documents({}) == 0


@live
def test_the_body_cannot_write_the_base(created):
    """The base is `logic`: the build writes it through the migration door, the body reads it. The
    ODM path is closed at the MODEL, so a caller holding one cannot save its way past the datatier."""
    from tk2.core.models import BaseKeyDoc, BaseRelationDoc
    from tk2.core.write_class import WriteClassViolation

    for model in (BaseKeyDoc, BaseRelationDoc):
        with pytest.raises(WriteClassViolation):
            model.insert_one({"build": "b", "key": "eat.v", "index": 0})


# ------------------------------------------------------------------------------------------------
# 0007 rules whose lemma may speak
# ------------------------------------------------------------------------------------------------


@live
def test_0007_writes_policy_version_4_beside_the_three_before_it(created):
    """Four deep, and the ledger property holds at every level: nothing below v4 is edited, so a
    manifest row naming any of them still points at something a reader can read."""
    stored = list(created["dictionary_policy"].find({}))
    assert {1, 2, 3, 4} <= {r["version"] for r in stored}
    assert len([r for r in stored if r["version"] == 4]) == len(policy_rows_v4())
    assert len([r for r in stored if r["version"] == 3]) == len(policy_rows_v3())


@live
def test_the_ruled_lemma_scope_reads_back_from_the_database(created):
    """The seam at version 4, and the value the Captain ruled: rows out of mongo, through the pure
    reader, into the thing that decides whether `eat` carries `corrode`'s derivations.

    VERSION-EXPLICIT since 0008 wrote v5 on top — the table is four rulings deep now."""
    from tests.test_dictionary_policy import V4_FINGERPRINT
    from tk2.dictionary import policy

    stored = [r for r in created["dictionary_policy"].find({}) if r["version"] == 4]
    config = policy.config_from_rows(stored, list(created["dictionary_bar"].find({})))

    assert policy.policy_version(stored) == 4
    assert config.relations.lemma_scope == "word"
    assert config.fingerprint() == V4_FINGERPRINT
    # ...and everything v3 declared is still declared, unedited.
    assert dict(config.relations.weights)["antonym"] == -1.0
    assert config.alphabet.order == ("n", "v", "a", "r")
    assert len(config.declared_seeds) == 224


# ------------------------------------------------------------------------------------------------
# 0008 admits the inferred opposition
# ------------------------------------------------------------------------------------------------


@live
def test_0008_writes_policy_version_5_beside_the_four_before_it(created):
    stored = list(created["dictionary_policy"].find({}))
    assert {1, 2, 3, 4, 5} <= {r["version"] for r in stored}
    assert len([r for r in stored if r["version"] == 5]) == len(policy_rows_v5())
    assert {r["version"] for r in created["dictionary_bar"].find({})} == {1}


@live
def test_version_5_is_the_policy_a_build_can_run_R_from(created):
    """v5's whole declaration, live: the cuts, the weights, the alphabet, whose lemma speaks and how
    a one-sided antonymy is read — with nothing left for a default in code to answer.

    VERSION-EXPLICIT since 0009 wrote v6 on top, for the reason 0006 made v2's test explicit."""
    from tests.test_dictionary_policy import V5_FINGERPRINT
    from tk2.dictionary import policy, relations

    stored = [r for r in created["dictionary_policy"].find({}) if r["version"] == 5]
    config = policy.config_from_rows(stored, list(created["dictionary_bar"].find({})))

    assert policy.policy_version(stored) == 5
    assert config.fingerprint() == V5_FINGERPRINT
    assert config.relations.antonym_symmetry == relations.SYMMETRY_ADD_ONLY
    assert config.relations.lemma_scope == "word"
    assert config.alphabet is not None and config.closure.max_depth == 2
    assert relations.resolve_symmetry(config.relations, None) == relations.SYMMETRY_ADD_ONLY


# ------------------------------------------------------------------------------------------------
# 0009 declares D's gloss walk
# ------------------------------------------------------------------------------------------------


@live
def test_0009_writes_policy_version_6_beside_the_five_before_it(created):
    stored = list(created["dictionary_policy"].find({}))
    assert {1, 2, 3, 4, 5, 6} <= {r["version"] for r in stored}
    assert len([r for r in stored if r["version"] == 6]) == len(policy_rows_v6())
    assert len([r for r in stored if r["version"] == 5]) == len(policy_rows_v5())
    # The bar still has not moved: a policy ruling is not an occasion to re-declare the expectation
    # the ruling will be judged by.
    assert {r["version"] for r in created["dictionary_bar"].find({})} == {1}


@live
def test_0009_creates_D_own_collection_empty(created):
    """`base_d` is made by the DEPLOY and filled by the BUILD, exactly as `base_r` was at 0006: a
    build that had to create its own table would be a build doing a deploy's job."""
    from tk2.core.models import BaseDistributionDoc

    assert BaseDistributionDoc.Settings.name in set(created.list_collection_names())
    assert created[BaseDistributionDoc.Settings.name].count_documents({}) == 0


@live
def test_the_body_cannot_write_D_either(created):
    from tk2.core.models import BaseDistributionDoc
    from tk2.core.write_class import WriteClassViolation

    with pytest.raises(WriteClassViolation):
        BaseDistributionDoc.insert_one({"build": "b", "key": "eat.v", "index": 0})


@live
def test_version_6_can_build_both_matrices(created):
    """v6 read back as a policy that names every value BOTH geometries need — R's weights and
    readings, and D's nine parameters — with nothing left for a default in code to answer.

    VERSION-EXPLICIT since 0010 wrote v7 on top, for the reason 0006 made v2's test explicit. It is
    also where v6's deliberate SILENCE is checked: it declares D and says nothing about how loudly
    to hear it, because the mix was still a measurement on the day these rows were written."""
    from tests.test_dictionary_policy import V6_FINGERPRINT
    from tk2.dictionary import policy

    stored = [r for r in created["dictionary_policy"].find({}) if r["version"] == 6]
    config = policy.config_from_rows(stored, list(created["dictionary_bar"].find({})))

    assert policy.policy_version(stored) == 6
    assert config.fingerprint() == V6_FINGERPRINT
    assert config.relations is not None and config.distribution is not None
    assert config.distribution.measure == "jaccard" and config.distribution.min_shared == 2
    assert config.reading is None


# ------------------------------------------------------------------------------------------------
# 0010 rules the dual read, and moves two numbers with it
# ------------------------------------------------------------------------------------------------


@live
def test_0010_writes_policy_version_7_beside_the_six_before_it(created):
    stored = list(created["dictionary_policy"].find({}))
    assert {r["version"] for r in stored} == {1, 2, 3, 4, 5, 6, 7}
    assert len([r for r in stored if r["version"] == 7]) == len(policy_rows_v7())
    assert len([r for r in stored if r["version"] == 6]) == len(policy_rows_v6())
    # The bar still has not moved, three rulings deep now: a policy ruling is not an occasion to
    # re-declare the expectation the ruling will be judged by.
    assert {r["version"] for r in created["dictionary_bar"].find({})} == {1}


@live
def test_the_standing_policy_declares_how_the_two_geometries_are_read_together(created):
    """The end of the chain, live: the newest rows name every value both matrices need AND the one
    value that says how to read them as one number — with nothing left for a default in code."""
    from tests.test_dictionary_policy import V7_FINGERPRINT
    from tk2.dictionary import policy

    stored = policy.latest_version(list(created["dictionary_policy"].find({})))
    config = policy.config_from_rows(stored, list(created["dictionary_bar"].find({})))

    assert policy.policy_version(stored) == 7
    assert config.fingerprint() == V7_FINGERPRINT
    assert config.reading is not None and config.reading.mix == 0.5
    assert config.distribution.min_shared == 1
    assert dict(config.relations.weights)["derivational"] == 0.45
