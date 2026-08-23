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
pip install -e .     # editable install of the `tk2` package
task body            # boot, tick, exit
```

`task body` is `python -m tk2.body`. Today it boots, ticks once and exits clean — the keel floats
before anything is built on it. The r-tables it will load at boot, and the slow tick that reconciles
them so a parameter edit lands live without a restart (body req. 4), arrive with the datatier and the
first migration.
