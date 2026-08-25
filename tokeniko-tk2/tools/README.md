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
