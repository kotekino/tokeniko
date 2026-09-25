# tooling — THE TEST INVENTORY, AND WHY THE SUITE TOOK TWO HOURS, 2026-09-22

*Roadmap: `E1e.8`*

*Written when the Captain asked two questions I had been answering by assertion: «is it absolutely
necessary to run ALL the suite» and «why is it so slow». Both answers turned out to be no and «a
defect», and the second one had been getting worse every day we worked.*

---

## THE ANSWER TO «WHY IS IT SO SLOW»

**`Migration.load()` re-executed the module on every call**, and a migration that EXTENDS another
reads it by loading it. `db/0031._previous_rows()` loaded `db/0030`, whose `_previous_rows()` loaded
`db/0029`, down to `db/0008` — each level re-running everything beneath it, and each execution
running that file's module-level `_check()` over 385 rows.

    standing_closed_classes()          186.7s  ->  0.2s
    discover() + load() all 31           38.9s  ->  ~0s
    the whole suite, file by file      ~2 hours ->  ~34 min

**Every migration we wrote made every station test slower.** The five written on 2026-09-21 each
added a level to the chain. The cost was invisible because it arrived one migration at a time.

Memoising is safe because a migration file is **immutable by policy** — the ledger fingerprints it
and `test_archive` holds it to that — so a loaded module is a fact about the file rather than a
snapshot of it. The key carries mtime and size anyway, so a file edited while it is being written is
re-read rather than remembered wrong.

*The rule this broke had a number in it: the Captain's 2026-09-17 ruling said «the full suite runs
once, at the commit gate» and justified it against a **nine-minute** suite. By the time it was two
hours the premise was gone, and I kept obeying the letter of it for weeks instead of saying so.*

---

## THE INVENTORY — 44 files, 1172 tests, every one green on 2026-09-22

Timed individually, after the fix. **A file's cost is now almost entirely what it must LOAD**:
stanza (~400 MB), WordNet, or the remote body.

### the station — E3, the parser/compiler/decompiler

| file | tests | time | needs |
|---|---:|---:|---|
| `test_language_compile` | 91 | 27.2s | stanza |
| `test_language_utterance` | 22 | 6.8s | stanza |
| `test_language_skeleton` | 12 | 4.8s | stanza |
| `test_language_markers` | 15 | 2.3s | — |
| `test_language_decompile` | 39 | 0.4s | — |
| `test_language_inflect` | 28 | 0.3s | — |
| `test_language_closed` | 15 | 0.3s | — |
| `test_language_adverbs` | 19 | 0.3s | — |
| `test_closed_classes` | 20 | 0.3s | — |

### the station's evidence — the gates that SCORE it, not unit tests

| file | tests | time | needs |
|---|---:|---:|---|
| `test_drill_gate` | 17 | 26.1s | stanza |
| `test_ud_gate` | 9 | 2.3s | — |
| `test_drill` | 107 | 0.3s | — |
| `test_placement_bench` | 7 | 0.3s | — |

### tkzip — E2, the format

| file | tests | time | needs |
|---|---:|---:|---|
| `test_tkzip_schema` | 23 | 0.3s | — |

### the dictionary — E1

| file | tests | time | needs |
|---|---:|---:|---|
| `test_dictionary_senses` | 9 | 25.6s | WordNet |
| `test_dictionary_proposal` | 12 | 7.8s | WordNet |
| `test_dictionary_wordnet` | 35 | 5.4s | WordNet |
| `test_dictionary_supersense` | 24 | 4.5s | WordNet |
| `test_dictionary_policy` | 117 | 1.4s | — |
| `test_dictionary_relations` | 37 | 0.3s | — |
| `test_dictionary_distribution` | 30 | 0.3s | — |
| `test_dictionary_space` | 39 | 0.3s | — |
| `test_dictionary_closure` | 32 | 0.3s | — |
| `test_dictionary_curation` | 18 | 0.3s | — |
| `test_dictionary_keys` | 24 | 0.3s | — |
| `test_dictionary_config` | 14 | 0.3s | — |
| `test_dictionary_build` | 8 | 0.3s | — |
| `test_dictionary_curated_edges` | 12 | 0.2s | — |
| `test_dictionary_references` | 10 | 0.2s | — |

*Eleven of the fifteen run on the sixteen-word handcrafted world in `tests/lexicon_fixture.py` and
need no resource at all. Only four read the real WordNet, and those four are the whole cost.*

### core — models, documents, write classes, field conventions

| file | tests | time | needs |
|---|---:|---:|---|
| `test_models_live` | 22 | 42.4s | **the body** |
| `test_models` | 32 | 0.3s | — |
| `test_readonly_documents` | 57 | 0.2s | — |
| `test_mixins` | 16 | 0.3s | — |
| `test_write_class` | 7 | 0.3s | — |
| `test_documents` | 6 | 0.2s | — |

### the datatier — the door to the body

| file | tests | time | needs |
|---|---:|---:|---|
| `test_migrations` | 54 | **~31 min** | **the body** — it applies all 31, one at a time |
| `test_matrix_store` | 23 | 10.5s | the body |
| `test_traps` | 18 | 2.4s | the body |
| `test_rcache` | 22 | 2.3s | the body |
| `test_migration_writer` | 16 | 1.9s | the body |
| `test_guard` | 21 | 0.3s | — |
| `test_anatomy` | 22 | 0.3s | — |
| `test_archive` | 4 | 0.3s | — |

### and the gate itself

| file | tests | time | needs |
|---|---:|---:|---|
| `test_spine` | 7 | 2.2s | — |

---

## WHAT THIS BOUGHT, AND WHAT IT DID NOT

**The suite is no longer two hours, but it is not five minutes either.** ~31 of the ~34 are
`test_migrations` alone, applying 31 migrations to a real database one at a time — which IS the
test, and which grows with the knowledge. *The sweep that produced this table capped every file at
90 seconds, so the first figure written here said 4.6 minutes; that was the cap, not the cost.*

A cost worth paying at a deploy, and still not the commit gate — the Captain's ruling stands on its
own grounds, not on the clock:

> *«Tests must be minimal for the portion of code the coding is doing. Regressions in other parts of
> the app will be caught time by time when the full suite will run.»*

And the attention argument the clock never touched: *«during a test I obviously lose the
concentration, so I start another task, then I forget to check when I close the lid of the
laptop.»* A gate nobody watches reports nothing — one such run sat nine hours behind a sleeping
laptop and had to be discarded as evidence, which is how this investigation started.

**What is still genuinely slow and always will be:** `test_migrations` (it applies 31 migrations to
a real database — that IS the test), `test_models_live` (the body, by definition), and the four
files that read WordNet. Those are costs, not defects.

**The one improvement left on the table:** four station files each build their own
`StanzaSkeletons`, and the model loads once per process — so running them together in one pytest
invocation pays it once, not four times. The section gate already does that. It is worth knowing
before anyone optimises something that is already amortised.
