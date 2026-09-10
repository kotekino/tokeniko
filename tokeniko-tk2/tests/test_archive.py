"""The archived migrations: readable forever, runnable never.

E1b squashed thirteen migrations into one baseline and moved the originals to `db/archive/`. They
are kept rather than deleted for one reason — a reader who finds nine policy versions in the
database will want to know where they came from, and «git log» is a worse answer than a directory.

But an archived migration that the runner could still find would be a second, older world trying to
apply itself over the baseline's. The two properties below are what keep «archive» a real word.
"""

from pathlib import Path

from tk2 import migrations


def test_the_runner_does_not_descend_into_the_archive():
    """`discover()` does not walk subdirectories, so the archive is invisible to it. The chain since
    E1b starts at the baseline and grows normally — 0002 re-ruled the NEAR floor hours later — so
    what is held here is that no ARCHIVED number ever reappears in the live chain."""
    found = migrations.discover()
    labels = [m.label for m in found]

    assert labels[0] == "0001_the_world_and_everything_declared"
    assert [m.number for m in found] == sorted(m.number for m in found)
    archived = {p.name for p in (Path(migrations.DEFAULT_DIRECTORY) / "archive").glob("0*.py")}
    assert not {label + ".py" for label in labels} & archived


def test_the_archive_is_still_there_and_still_thirteen():
    """Kept, not deleted. If this ever fails because somebody tidied the directory away, the nine
    policy versions in the database lose the only readable account of where they came from."""
    archive = Path(migrations.DEFAULT_DIRECTORY) / "archive"

    files = sorted(p.name for p in archive.glob("0*.py"))
    assert len(files) == 13
    assert files[0] == "0001_create_the_world.py"
    assert files[-1] == "0013_the_verdict_gets_its_two_edges.py"


def test_the_baseline_carries_every_version_the_chain_declared():
    """The load-bearing claim of the squash, checked rather than trusted: nine policy versions and
    two bar versions, which is exactly what the thirteen wrote."""
    baseline = migrations.discover()[0].load()

    assert {row["version"] for row in baseline.POLICY_ROWS} == {1, 2, 3, 4, 5, 6, 7, 8, 9}
    assert {row["version"] for row in baseline.BAR_ROWS} == {1, 2}


def test_every_carried_policy_row_still_explains_itself():
    """The notes ARE the ledger — nine rulings with the measurements that produced them. A squash
    that dropped one would lose the reasoning while keeping the value, which is the worse half."""
    baseline = migrations.discover()[0].load()

    mute = [r for r in baseline.POLICY_ROWS if not r.get("note")]
    assert mute == []
