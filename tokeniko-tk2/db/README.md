# db — the migrations

**Deploys are migrations** (body req. 3): development ships as scripts that write the db. Nothing in
this directory is imported by the body — the body *interprets* what these scripts wrote.

- Numbered python scripts, `0001_*.py` upward. The number is the order, and the order is the truth.
- Applied state is recorded in a `migrations` collection; `tools/migrate.py` runs the pending ones.
- A migration is the ONLY writer of the `param` and `logic` collections. Those write-classes have no
  public write path in the datatier — that is the point of declaring them.
- A schema change is a migration, never a cast (data-modeling req. 6).

## What is here since E1b (2026-09-10)

- **`0001_the_world_and_everything_declared.py`** — the baseline. Creates every collection and
  writes every curated row nine rulings produced: the whole policy ledger, the acceptance bar, the
  closed classes, the heart's anatomy and the body's parameters.
- **`data/declared_rows.json`** — those rows, as data. A file rather than a python literal because
  2,192 rows of prose notes inlined would make the migration unreadable, and because a diff shows a
  changed NOTE as plainly as a changed value — which is the property that makes a curated row
  auditable.
- **`archive/`** — the thirteen migrations that built E1, kept and never run. `discover()` does not
  descend into subdirectories, and `tests/test_archive.py` holds both halves of that: the runner
  sees only the baseline, and the archive is still there.

**Why a baseline at all.** E1b renamed every collection whose name hid what it held, and mongo
cannot rename a timeseries collection — so the honest act was a rebuild. Nothing was lost: the body
had been created and had never ticked. The ledger survived because the ledger was never these files
— it is the `dictionary_policy` rows, and all nine versions are written above with their notes
verbatim.

**What is NOT here: the base itself.** `dictionary_base_keys`, `_relations`, `_distribution` and
their seals are DERIVED. A migration that shipped a derived artifact would be a migration doing a
build's job: that is `tools/build_dictionary.py --apply`, under the Captain's hand.
