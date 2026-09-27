# datatier — TK1 IS READ, NEVER WRITTEN, 2026-09-27 19:00

*Roadmap: `E3b.3.2` · `E3b.3.2.1` · `E1e.9` — amends datatier req 4*

## The ruling *(the Captain, 2026-09-27)*

> *«Remove the guard as it is and replace it with this: reading is ALWAYS allowed on tk1. Writing, in
> the context tk2, is NEVER allowed.»*

The question it answers (`E3b.3.2`, from the course check): the places table, the names list, the
stakeholders and the journeys live in tk1's databases, which the guard refused even for a read. The
two candidates were a snapshot exported once from tk1's side, or a read-only door. **Neither: tk1 is
read in place, whenever tk2 needs it.** «Read lazily, never materialized» (`places.py`, the places
table's own ruling) is now satisfied literally — nothing is copied into `tokeniko_tk2`.

## What changes, and what does not

- **was:** tk1's databases (`TK1_BODY_DBS`) refused FIRST, by name, for any handle — read or write
- **now:** a tk1 database may be opened for READING, always; no tk2 path may WRITE to it, ever
- **unchanged:** tk2's own writes go to the sandbox whitelist only; the biography is never wiped or
  edited; what crosses into tk2 as tk2's own rows still crosses by migration (E9)
- `E1e.9`'s tool (`tools/journey_ledger_build.py`, disabled 09-26) may come back through the read door
  once it exists — it read, it never wrote

## Built — `E3b.3.2.1` *(2026-09-27)*

The Captain, on the QM's proposal of a read-only facade plus a read-only Mongo user: *«We shouldn't
overcomplicate the things. We just don't write tk1, simple as that. […] When we need to read from tk1,
we just do it.»* So the build is the smallest one:

- `tk1_database(name)` (`tk2/datatier/client.py`) — a handle on tk1's server (`TK1_MONGO_URI`, default
  `tokeniko.local:27018`), for reading. Nothing in tk2 writes through it
- `database()` keeps refusing tk1's names as a tk2 database — the handle tk2 writes through
- `tools/journey_ledger_build.py` re-enabled through it (`E1e.9`); a read of `tkzipdebug` gives 583 rows
