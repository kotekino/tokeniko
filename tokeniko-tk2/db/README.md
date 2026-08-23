# db — the migrations

**Deploys are migrations** (body req. 3): development ships as scripts that write the db. Nothing in
this directory is imported by the body — the body *interprets* what these scripts wrote.

- Numbered python scripts, `0001_*.py` upward. The number is the order, and the order is the truth.
- Applied state is recorded in a `migrations` collection; `tools/migrate.py` runs the pending ones.
- A migration is the ONLY writer of the `param` and `logic` collections. Those write-classes have no
  public write path in the datatier — that is the point of declaring them.
- A schema change is a migration, never a cast (data-modeling req. 6).

Empty until T5, which brings the runner and **0001 — creating the world**.
