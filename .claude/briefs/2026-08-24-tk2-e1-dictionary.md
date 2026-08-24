# Work order: tk2 E1 — THE DICTIONARY AT SCALE

*QM brief, 2026-08-24. Second epic (`tokeniko-tk2/docs/plan.md` § E1). Same cadence as E0: ONE task
at a time, STOP and report; QM validates, the Captain green-lights each commit; you never commit.*

## Standing condition for THIS session: the body is unreachable

The Captain is away from the body — **mongo is NOT available**. Everything until T5 is pure code:
unit tests on fixtures and in-memory builds only. You may WRITE mongo-marked tests, but you cannot
run them; say so in your reports rather than pretending. **T5 (the live build + bar + map — the E1
gate) is HOME-GATED and not yours today.**

## Read first

1. `tokeniko-tk2/docs/plan.md` § E1 — your scope.
2. `tokeniko-tk2/docs/dictionary/requirements.md` — the acceptance contract (all 21 lines + the
   OPEN-at-close list; reqs 10-superseded, 19, 20, 21 are the load-bearing ones).
3. The PoC you are industrializing: `scripts/tk2/` (`tk2_config.py` — seeds/weights/THE BAR ·
   `tk2_subset.py` — digraph/SCC/closure · `tk2_matrix.py` — the cell walk · `tk2_build2.py` — the
   two-matrix write shape · `tk2_curate.py` — propose/simulate/approve). The PoC is the prototype,
   not the law: keep its proven decisions, industrialize its shape.
4. What E0 gives you: `tk2/core` (write-classes, mixins), `tk2/datatier` (guard, traps,
   MigrationWriter, r-cache), the migration runner.

## Architecture guard — read twice, it prevents the billion-cell mistake

The SQUARE matrices R and D exist over **BASE keys only** (the POS-split base lexicon — thousands of
keys, not the ~197k senses). The full dictionary rides ON the base: a sense carries its D-vector
over base dims and consults R through its sense key (tkzip #11). **Never a senses×senses matrix.**

## QM rulings for this epic

- **Code home**: `tk2/dictionary/` = pure logic (closure, mining, matrices, collisions — no mongo
  imports; providers injected). `tools/build_dictionary.py` = the runnable that will do the T5 build.
  `scripts/tk2/` stays untouched — it is the PoC's museum and the instruments' home.
- **Write-classes**: the base collections (`base_r`, `base_d`, key registry) are **logic (r)** —
  the body reads, never writes. Their only writer is the build tool, THROUGH the MigrationWriter
  door, and every build records a manifest row (config hash · date · counts · authorization) in a
  `dictionary_builds` logic collection — the build analog of the migrations ledger. If this shape
  fights the code, STOP and report.
- **Policy before results** (tooling req 4): relation weights, closure depth, bar pairs live in a
  declared config that is hashed into the manifest; never edited after a measuring run.
- **Curated edges**: propose/simulate are code; **approve stays the Captain's hand** — port the
  gate, never weaken it (analytic-only, reciprocal 0.60, evidence recorded verbatim).

## The tasks (one at a time, stop after each)

**T1 — the closure engine.** `tk2/dictionary/`: POS-split key convention (one module, one truth);
the definition digraph + SCC + seed closure + depth cut as pure functions over an injected
gloss-provider; the WordNet adapter (nltk, local) as the real provider. Unit-test the engine on a
small handcrafted fixture AND spot-verify the adapter against known WordNet facts. Carry the PoC's
lesson: the depth cut is a parameter of the config, and the `right`-ring case (one ring past the
cut) is a named regression fixture.

**T2 — the collision fix + membership repair.** Requirement 21: lemma-normalize at gloss-mining
time so an inflection can never mint a key (`left` from «something left over», `use.v`/`used.v`);
POS-aware membership (morphy per-POS). Regression cases by name: left/leave, use/used. These run
inside the T1 engine, not beside it.

**T3 — the R builder + curation port.** All named WordNet relations with weights from the declared
config, sign preserved (synonym→antonym ordering), provenance per cell; the curated-edge machinery
ported (propose/simulate produce the same shapes the PoC proved; approve gated as ruled). Pure core
behind a storage interface — in-memory store for tests, mongo store stubbed for T5.

**T4 — the D builder + the down-weight decision PREPARED.** Gloss-overlap D over POS-split keys
(collision fix active); then, in memory on the PoC's subscale, measure the `derivational`
down-weight candidates against the bar pairs (the land.n~land.v case is the target; the bar must
not regress elsewhere). You do NOT take the decision — you produce the numbers table and report it
for the Captain's ruling.

**T5 — HOME-GATED (not today): the build and the E1 gate.** Full base build into
`tokeniko_tk2_body` via `tools/build_dictionary.py`, bar regression suite green on both reads, map
regenerated. Waits until the body is reachable.

## Law

Never commit/push · partial gates only (and today: no mongo at all) · never touch tk1 dbs ·
secrets unprinted · craft over expedience · STOP on conflicts.
