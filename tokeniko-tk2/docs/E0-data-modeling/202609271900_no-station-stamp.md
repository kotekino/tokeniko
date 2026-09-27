# data-modeling — NO STATION STAMP ON A ZIP, 2026-09-27 19:00

*Roadmap: `E3.10` · `E3.10.1` — amends data-modeling req 7*

## The ruling *(the Captain, 2026-09-27)*

> *«I think we don't need any of this. Station change, implies check and (eventual) recompile of the
> involved zips.»*

The question (`E3.10`, from the course check): req 7 asked `derived_by` to carry the STATION VERSION
so a station later found buggy has its zips findable; `Compiled` and `Zip` carry `schema_version`
alone. Where should the stamp live — the zip, or the document around it (tkzip req 59)?

**Neither. No stamp.** A change to the station is itself the trigger: after it, the stored zips are
checked and those that change are recompiled. Nothing has to be found by version, because every zip
is a candidate.

## Why it holds

- a zip is the thought; the same thought compiled by two stations stays the same zip, so comparison
  (limit B, `E4.8`) never sees a version difference that is not a meaning difference
- the check needs only what is already kept: every stored zip's document carries `original` verbatim
  (tkzip req 59, data-modeling req 1) — recompile it and compare
- «the station» includes its knowledge: a migration that changes the closed classes, the adverb kinds
  or the UD readings is a station change too

## What it asks for — `E3.10.1`, before the first zip is stored (PS1 / E6)

The check itself: after a station change, recompile each stored zip's `original`, compare, and list
the zips that differ. **One cost, stated:** a recompiled zip that differs is a belief that changes —
«retreat, not override» says it goes through the mind's own machinery (as E9's translation night
does, additive), not a replacement in place. How is `E3.10.1`'s to design.
