"""THE BROAD-SHORT TEST — one minute, a spine through every module, run at every commit.

**THE GATE PER COMMIT IS THIS FILE PLUS THE FULL TESTS OF THE SECTION BEING COMMITTED** (the
Captain's ruling, 2026-09-22, written in the root `CLAUDE.md`). This half is deliberately shallow and
deliberately WIDE: it does not prove any module correct — that is the section's own suite — it
proves that nothing obviously broke somewhere nobody was looking.

    « Coding should be thorough and no shortcuts, BUT tests must be minimal for the portion of code
      the coding is doing. Regressions in other parts of the app will be caught time by time when
      the full suite will run. »

**THE BUDGET IS THE DESIGN.** One minute, total. So nothing here touches the remote body, loads
stanza (~400 MB and seconds), or reads WordNet: each of those is marked elsewhere and belongs to the
suite that owns it. A test that needs one of them is not a spine test — it is a section test, and it
goes in the section's file.

**AND A CURATED SET DRIFTS**, which is the failure this file has to survive: a new module arrives,
nobody marks it, and the gate silently stops covering it. `test_every_module_has_a_spine` is the
ratchet — it discovers what is under `tk2/` at runtime and fails when something has no test here.
"""

import pathlib

import pytest

pytestmark = pytest.mark.spine

#: The module areas this file covers, each by the name of the test that covers it. Read by the
#: ratchet at the bottom, which compares it against what is actually on disk.
COVERS = {
    "tkzip": "test_the_FORMAT_accepts_a_zip_and_refuses_a_bad_one",
    "language": "test_the_STATION_compiles_a_sentence_and_says_it_back",
    "dictionary": "test_the_DICTIONARY_closes_a_definition_over_the_handcrafted_world",
    "core": "test_CORE_registers_its_collections_and_declares_their_write_class",
    "datatier": "test_the_DATATIER_refuses_tk1s_databases_by_name",
    "migrations": "test_every_MIGRATION_loads_and_the_versions_only_go_up",
}


def test_the_FORMAT_accepts_a_zip_and_refuses_a_bad_one():
    """tkzip — a zip validates, and a value the schema does not admit is refused at the boundary.

    The refusal is the half that matters: schema v7 made `number` a `Literal` precisely because a
    value nobody admitted («dual») reached a zip and nothing could say it back.
    """
    from pydantic import ValidationError

    from tk2.tkzip.schema import SCHEMA_VERSION, Box, ContentRow, Role, Zip

    zip_ = Zip(rows=[ContentRow(name="r0", truth=1.0, predicate="sleep.v",
                                boxes={Role.AGENT: Box(head="cat.n", number="sg")})])
    assert SCHEMA_VERSION >= 8
    assert zip_.rows[0].boxes[Role.AGENT].head == "cat.n"

    with pytest.raises(ValidationError):
        Box(head="cat.n", number="dual")


def test_the_STATION_compiles_a_sentence_and_says_it_back():
    """language — a hand-written skeleton in, a zip out, and a sentence back out of the zip.

    No stanza: the skeleton is written by hand, which is the boundary `skeleton_from_conllu` exists
    for. This is the whole station in one assertion — if compile or decompile is broken anywhere
    structural, the text will not come back.
    """
    from tk2.language import standing_closed_classes
    from tk2.language.compile import Compiler
    from tk2.language.decompile import Decompiler
    from tk2.language.skeleton import skeleton_from_conllu

    skeleton = skeleton_from_conllu("The cat sleeps.", [
        ("1", "The", "the", "DET", "2", "det"),      # the determiner hangs off the NOUN
        ("2", "cat", "cat", "NOUN", "3", "nsubj"),
        ("3", "sleeps", "sleep", "VERB", "0", "root"),
        ("4", ".", ".", "PUNCT", "3", "punct"),
    ])
    table = standing_closed_classes()
    zip_ = Compiler(table).compile(skeleton).zip

    assert zip_.rows and zip_.rows[0].predicate == "sleep.v"
    assert Decompiler(table).decompile(zip_).text == "The cat sleeps."


def test_the_DICTIONARY_closes_a_definition_over_the_handcrafted_world():
    """dictionary — the closure engine on the sixteen-word fixture, which needs no WordNet.

    The real resource is the dictionary suite's business and it is slow. What this asks is only
    that the engine runs and answers with words from the world it was given.
    """
    from tests.lexicon_fixture import FixtureGlossProvider
    from tk2.dictionary import closure
    from tk2.dictionary.config import ClosurePolicy

    policy = ClosurePolicy(max_depth=1, max_size=100, senses="primary")
    graph = closure.build_digraph(FixtureGlossProvider(), policy)
    assert graph, "the definition digraph came out empty"

    reached = closure.seed_closure(graph, ("sleep",), policy)
    assert reached.words, "the closure reached nothing from a seed the fixture defines"


def test_CORE_registers_its_collections_and_declares_their_write_class():
    """core — the register is importable, non-empty, and every model declares where it may be
    written from. A model that forgot is the defect this catches."""
    from tk2.core.models import ALL_MODELS

    assert ALL_MODELS, "the register is empty"
    for model in ALL_MODELS:
        assert getattr(model, "Settings", None) is not None, f"{model.__name__} declares no Settings"


def test_the_DATATIER_refuses_tk1s_databases_by_name():
    """datatier — the guard, which is the one thing in this repository that must never weaken.

    tk1's databases hold the biography. No connection is made here: the refusal is by NAME, which
    is why it can live in a one-minute gate at all.
    """
    from tk2.core import constants
    from tk2.datatier.guard import DatabaseRefused, guard_db_name

    assert guard_db_name(constants.TK2_BODY_TEST_DB) == constants.TK2_BODY_TEST_DB
    for name in constants.TK1_BODY_DBS:
        with pytest.raises(DatabaseRefused):
            guard_db_name(name)


def test_every_MIGRATION_loads_and_the_versions_only_go_up():
    """migrations — every file imports (their module-level `_check()` runs on import, so this
    exercises each one's own guards) and their numbers are unique and ordered.

    No database: discovery and loading are file work, and the `up()` is what needs a body.
    """
    from tk2.migrations import discover

    found = discover()
    assert found, "no migrations were discovered"

    numbers = [m.number for m in found]
    assert numbers == sorted(numbers), "the migrations are out of order"
    assert len(set(numbers)) == len(numbers), "two migrations share a number"
    for migration in found:
        migration.load()


def test_every_module_has_a_spine():
    """**THE RATCHET.** A curated gate drifts: a module arrives, nobody adds a test here, and the
    broad-short test quietly stops being broad. So the set is not trusted — it is checked against
    what is on disk.

    A new package under `tk2/` fails this until someone gives it a spine, which is the intended
    cost: one test, written once, by whoever knew what that module was for.
    """
    root = pathlib.Path(__file__).resolve().parents[1] / "tk2"
    packages = {d.name for d in root.iterdir()
                if d.is_dir() and not d.name.startswith(("_", "."))}
    packages.update(f.stem for f in root.glob("*.py")
                    if f.stem not in ("__init__", "body"))

    missing = sorted(packages - set(COVERS))
    assert not missing, (f"{missing} have no spine test — add one above and name it in COVERS, "
                         f"or the commit gate is not covering them")

    absent = sorted(name for name in COVERS.values() if name not in globals())
    assert not absent, f"COVERS names {absent}, which do not exist in this file"
