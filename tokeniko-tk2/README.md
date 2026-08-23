# tokeniko 2 — the body

The next architecture of tokeniko: one persistent, logic-first thinking entity, embodied on bare
metal beside its own MongoDB. This directory is the **build**; `docs/` is the **blueprint** that the
build answers to.

The two limits tokeniko 2 exists to kill, stated so they can be falsified (`docs/README.md` §1):

- **A — behaviour is hardwired.** Rules become zips: policy in memory, over a vocabulary that is not
  fixed in advance.
- **B — the zip is not computable.** The format becomes fixed-arity: two arbitrary sentences compared
  by uniform numeric operations, with no code that knows their individual shape.

v1 (`../tokeniko/`) is not deprecated and not frozen out of usefulness: it stops growing, and it
keeps witnessing. Its corpora are the no-regression ratchet this build has to clear.

## The map

```
tokeniko-tk2/
  docs/        the blueprint — sixteen requirements files, the plan, the roadmap  (read first)
  tk2/         the installable package: the body's binary
    core/        pydantic models + the constants          — shape
    datatier/    client, guard, r-cache, bunnet wrapping  — movement
  db/          numbered migrations; deploys are migrations (body req. 3)
  tools/       runnable utilities (the migration runner, probes, bars)
```

Where to start reading `docs/`: **`docs/README.md`** (why this project exists and what must survive),
then **`docs/plan.md`** (the epics, their dependencies, and their acceptance contracts), then the
requirements file of whatever you are about to touch. `docs/roadmap.md` is the checkable mirror of
the plan; what finishes moves to `docs/landed.md`.

## The database

The running body uses the sandbox database **`tokeniko_tk2_body`**, on the same local MongoDB as the
rest of the project (`MONGO_URI`, default `mongodb://localhost:27018`).

Two other databases exist on that host, and neither is this one:

- `tokeniko` / `tokeniko_mem` — **tk1's live body: the biography.** Never opened from here. The
  datatier's guard refuses them by name.
- `tokeniko_tk2` — the dictionary-review instruments' sandbox (`../scripts/tk2/`). Its assets cross
  into the body by migration, never by a live read across the fence.

The guard is standard equipment (datatier req. 4): every entry point names its db and refuses one it
was not explicitly given. Go-live (E10) moves that boundary deliberately, with the Captain's hand on
it — a body cannot drift onto the biography by forgetting.

## Running it

From this directory, in the project's virtualenv (`../.venv`):

```
pip install -e .                 # editable install of the `tk2` package
python tools/migrate.py --list   # what is applied, what is pending
python tools/migrate.py          # create the world (and apply anything new)
task body                        # boot, then tick until stopped
task test                        # the unit checks
```

**Migrate before you boot.** The body is an interpreter of the db: with no rows there is nothing to
interpret, and it will say so and keep ticking rather than invent defaults.

`task body` is `python -m tk2.body`. It boots against `tokeniko_tk2_body`, loads the r-tier into the
cache, and ticks until SIGTERM or SIGINT — it finishes the tick it is in and then stops. `--max-ticks
N` bounds a run; `--db NAME` points it elsewhere, subject to the guard.

**The property to watch**: edit a parameter with a migration while the body is running, and it lands
on the next slow tick with no restart (datatier req. 3, body req. 4). That is what makes him fixed at
any moment and grown only through someone else's hands (body req. 5) — and it is the E0 gate:

```
tick 12 — dictionary.layer.epoch=0 · tick every 5s · refresh every 60s
slow tick — r-cache refreshed from the db
tick 13 — dictionary.layer.epoch=1 · tick every 5s · refresh every 60s
```

## Deploys are migrations

Numbered scripts in `db/`, applied by `tools/migrate.py`, recorded in a `migrations` collection.
They are the **only** writer of the `param` and `logic` tiers — the body has no write path to those
at all, at either the datatier or the model. An applied migration is immutable: its checksum is
recorded, and the fix for a wrong one is always a new one.
