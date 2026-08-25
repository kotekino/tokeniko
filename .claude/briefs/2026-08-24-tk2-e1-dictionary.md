# Work order: tk2 E1 — THE DICTIONARY AT SCALE

*QM brief, 2026-08-24. Second epic (`tokeniko-tk2/docs/plan.md` § E1). Same cadence as E0: ONE task
at a time, STOP and report; QM validates, the Captain green-lights each commit; you never commit.*

## Standing condition — UPDATED 2026-08-25: the body is reachable

The Captain is home; mongo is available. **T5 is no longer home-gated.** Partial gates only from the
workshop (full gate = deploy condition, never routine).

**T1 IS DONE, COMMITTED AND PUSHED** (`34e43c8`) — `tk2/dictionary/` exists: `keys.py` (POS-split
keys as law, word-anchored sense keys `left.v.01` with the WordNet synset name kept as provenance),
`config.py` (`ClosurePolicy` + `STANDING` + `fingerprint()` sha256), `glosses.py` (tokenise · stop
· land on lexicon), `closure.py` (digraph over WORDS · SCC · seed closure · depth cut · `stopped`
reason), `wordnet.py` (the only nltk-touching module). 327 checks green. Measured at full scale
under depth-2: 83,082 lemmas → 1,135 words → 1,863 keys; zero multi-word closed sets; the
`right`-ring reproduces as a named regression. You are CONTINUING that engine, not restarting it.

## Captain's rulings, 2026-08-25 (binding for the rest of E1)

- **`nltk` is ADMITTED** to the closed dependency list (pure python + data, isolated behind the
  provider seam in `wordnet.py`). Declare it in `pyproject.toml` if not already.
- **Stop list — lexicon membership WINS (option a).** A word that is in the lexicon is NEVER
  dropped as a stop word; the stop list applies only to tokens that are not lexicon members. This
  is what lets the Captain's own example (me → not → you → negation) form at all. It CHANGES the
  measured numbers (the 1,135/1,863 figures above were measured under the old absolute stop list) —
  **re-measure and report the new figures**; the old ones are superseded, not a regression.
  This belongs in the mining layer (`glosses.py`) and the change must be visible in the policy
  fingerprint if it is a policy knob.

## Standing law added 2026-08-25 — where a closed set may live

`plan.md` now carries it before the epics (read it there); it binds this epic immediately.
**FRAME** → code: the shape in which anything can be stated (the key grammar, the write classes, the
guard, the logic floor), moved only by migration. It must pass both tests — does a change alter the
SHAPE of rows/keys/operations rather than their content, and could evidence revise it? Anything
empirical is knowledge however certain we are. **CURATION** → db rows, grown generated-then-curated,
recorded in the build manifest: the seeds, the closure cuts, **the acceptance bar**, and **the
relation weights you write in T3 — they land as rows from the start, never as a table in
`config.py`**. **OPEN** → geometry with a nearest-anchor fallback, never a list at all.

Two tasks join this epic from that ruling:

- **T2b — the proper-noun/abbreviation refusal** (option C; dispatched 2026-08-25). A reading whose
  senses are all proper nouns/instances/abbreviations is refused at BOTH membership and mining, by a
  semantic criterion and never a typed exclusion list.
- **T4b — the policy becomes rows.** Seeds, closure cuts, the bar and the relation weights leave
  `config.py` for a `dictionary_policy` logic collection through the migration door, fingerprinted
  into the manifest. Seeds grown by proposal + simulation + the Captain's approval; **`max_size`
  ruled in the same breath** (400 was arbitrary — the base overshoots it to 1,357 because a ring
  lands whole); `POS_ORDER` travels with them (it is WordNet's answer, not the key grammar). The bar
  rows are epoch-stamped and append-mostly, each build recording the bar version + fingerprint it was
  measured against, and the offline suite reads a snapshot pinned by that fingerprint so acceptance
  tests still run without the body. Not to be touched before its own dispatch.

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
