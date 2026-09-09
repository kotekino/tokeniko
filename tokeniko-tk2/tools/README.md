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
  dimensions, and BOTH matrices over them — R (named relations, signed) and, since T4, D (gloss
  overlap, unsigned) — with the shape of what was built and the bar READ, never scored: the absolute
  floors are T5's and the Captain's. The bar is printed under R alone, D alone and the two
  CONCATENATED — nothing is ever averaged — at the mix THE ROWS DECLARE (policy v7: 0.5, the
  Captain's ruling of 2026-09-09) and at a sweep around it; `--mix` reproduces another blend, and
  there is no fallback if a policy declares none. `--apply --db … --authorized …` is the Captain's
  hand and the only part that writes, through the migration door, leaving a manifest row behind.
  `--compare-lemma-scope` is the A/B of 2026-08-26 the Captain ruled on: R built twice over ONE key
  space, changing only whether a synset's other lemmas may state antonymy and derivation for a
  dimension (he ruled `word` — policy v4). `--compare-antonym-symmetry` is the measurement ordered
  beside it, now three readings of a one-sided antonymy: `stated` (the resource's own), `overwrite`
  (state the reverse always — it destroys four stated cells) and `add_only` (complete a pair only
  where R is silent, as its own relation `antonym_inferred` with its own weight row, which is the
  shape a standing ruling would have to take).
  `--lemma-scope` reproduces a reading the rows do not declare. Three more measurements arrived with
  D at T4, and all three have since been ruled on: `--compare-derivational` builds R once per
  candidate weight over ONE key space (the E1 open item — `land.n~land.v` is FAR and
  `cause.n~cause.v` is NEAR, and R gave them the same cell; the Captain halved the weight to 0.45 on
  its sweep); `--compare-weighting` builds D twice, one word one vote against an idf-shaped
  down-weight on its gloss dimensions (measured, `idf` not adopted); `--compare-senses` builds the
  WHOLE BASE twice, under `primary` and under `all`, and is the only one of the family that moves
  membership — two bases, not two readings of one (measured, `all` rejected). `--senses` and
  `--walk NAME=VALUE` reproduce a closure cut and a gloss walk the rows do not declare. None of these variants may be
  STORED: a base in the database has to be the one its config fingerprint describes.
- `curate_dictionary.py` — the definitional edges (requirement 20): `propose` mines both sides of a
  pair and prints the evidence verbatim, `simulate` moves an in-memory copy of R and re-reads the
  bar, `approve` is refused without `--i-am-the-captain` and `--authorized`. The default worklist is
  DERIVED — the bar's NEAR pairs R leaves mute — rather than a list that would go stale.
