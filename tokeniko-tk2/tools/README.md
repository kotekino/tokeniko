# tools — the runnable utilities

Things you run at the body, never things the body imports. Each one names its database and refuses
anything not whitelisted — the guard is standard equipment, not a precaution taken when someone
remembers (datatier req. 4).

Nothing that writes the world lives in the body's binary; nothing that reads the world hides in a
tool. The split is the same one everywhere: the body interprets, the tools and migrations deploy.

- `migrate.py` — the migration runner (`--list` · `--db` · `--upto`).
- `export_bar_snapshot.py` — the acceptance bar's rows → its offline snapshot, pinned by fingerprint;
  `--check` is what a gate runs.
- `propose_seeds.py` — the seed proposal, reproducible: the ranking, the two exclusions, the closure
  each candidate set produces. It measures; the Captain rules. `--verify` is the other half: it
  re-derives the standing policy's structural seeds through the migration's own
  `derive_structural_seeds()`, diffs them against the rows, and rebuilds the base from them — what
  makes a materialised seed list a derivation rather than a paste.
- `build_dictionary.py` — the base, built from the standing policy rows: the closure, the
  dimensions, and R over them, with the shape of what was built and the bar READ (not scored — R is
  half the geometry until D lands). `--apply --db … --authorized …` is the Captain's hand and the
  only part that writes, through the migration door, leaving a manifest row behind.
  `--compare-lemma-scope` is the A/B of 2026-08-26 the Captain ruled on: R built twice over ONE key
  space, changing only whether a synset's other lemmas may state antonymy and derivation for a
  dimension (he ruled `word` — policy v4). `--compare-antonym-symmetry` is the measurement ordered
  beside it, now three readings of a one-sided antonymy: `stated` (the resource's own), `overwrite`
  (state the reverse always — it destroys four stated cells) and `add_only` (complete a pair only
  where R is silent, as its own relation `antonym_inferred` with its own weight row, which is the
  shape a standing ruling would have to take).
  `--lemma-scope` reproduces a reading the rows do not declare. None of these variants may be
  STORED: a base in the database has to be the one its config fingerprint describes.
- `curate_dictionary.py` — the definitional edges (requirement 20): `propose` mines both sides of a
  pair and prints the evidence verbatim, `simulate` moves an in-memory copy of R and re-reads the
  bar, `approve` is refused without `--i-am-the-captain` and `--authorized`. The default worklist is
  DERIVED — the bar's NEAR pairs R leaves mute — rather than a list that would go stale.
