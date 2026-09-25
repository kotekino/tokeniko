# parser/compiler — THE COURSE CHECK, 2026-09-26 09:00

*Roadmap: `E3.2.1.4` · `E3.2.1.5` · `E3.2.7.1` · `E3.2.17` · `E3.1.1` · `E3.3.4.1` · `E3.8.3` ·
`E3.10` · `E3.11` · `E3.12` · `E3.13` · `E2.3.1` · `E3.7` → `E4.3.1` · `E4.8` · `E1e.8.1 – .3` ·
`E1e.9` · `E1e.10` · `E3b.3.2`*

*An outside reading. The Captain asked a cloud Claude session, with no access to our conversations,
to check the code of `tokeniko-tk2/` at `68403e8` against the plan, the requirements, the READMEs
and the vision: «has the code produced until now consistently respected the plan? do you see any
weakness or misunderstanding?» Its report is the artifact «tk2 Course Check» (claude.ai, private to
the Captain). It had no stanza and no MongoDB, so it re-measured none of the gates; its probes used
hand-written skeletons in the shapes this plan documents.*

## How it was taken

**Every claim was re-verified here before anything was adopted** — the grep, the line, the
diff of ids between `roadmap.md` and `plan.md`. None was refuted. The Captain then ruled the
method: *fix here, in one pass, mechanically — no intermediate tests or decisions; test at the end;
commit; and the cloud session only QA-reviews that commit.* So what is BUILT below is only what
needed no ruling, or what followed a ruling already standing; every item marked *for the Captain*
waits.

## The verdict it gave, and ours

- **The discipline holds** — the guard, frame/knowledge, abstention, rows as a ledger, determinism
  (43 UD cases × 2 contexts × 6 hash seeds, byte-identical zips).
- **Two truth errors no corpus contained** — both reproduced, both fixed today.
- **One safety breach** — a tool reading tk1 around the guard. Disabled today.
- **The largest gap is in the PLAN, not the code** — limit B has no owner. *Agreed, and it is the
  finding most worth its cost: seven schema versions pulled by the round trip, none measured against
  comparison, which is half of why tk2 exists (tkzip req 1).*
- **E3 has no exit bar.** *Agreed, and it is the other steering question: each fix now surfaces
  2–5 findings.*
- **The trio drifted from the nested-id rule on the day it was written** — 58 roadmap ids absent
  from `plan.md`, `G1–G10` still in the plan. *Reconciled today.*

## The findings, with their ids and what happened

| id | finding | status 09-26 |
|---|---|---|
| `E3.2.1.4` | quote rotation keyed on 9 verbs — «John exclaimed to Marie "You are late"» made the listener late | **built** — `_contexts` asks `_relate`'s question |
| `E3.2.1.5` | «She lives here/there/now/then» → an `Open` → «Where does she live?» | **built, minimum** — schema v10, `Open.deixis`/`distance`, said never asked; context-vs-field *for the Captain* |
| `E1e.9` | `tools/journey_ledger_build.py` opens tk1's `tokeniko_mem` with a raw client | **disabled**; the door is `E3b.3.2` |
| `E4.8` | limit B: no task builds role vectors, compound or derived points; req 11 flagged since 09-14 | *for the Captain* |
| `E3.12` | E3's «Done when» stale; no numeric exit | *for the Captain* |
| reconcile | 58 ids, G-labels, `E3.7` without status, stale numbers, 9 notes without headers, ~15 unnumbered findings | **done** — see below |
| `E3.10` | a zip records nothing about the station, knowledge or provider that made it (data-modeling req 7) | open — *where it lives is the Captain's*; QM weighs it P2: nothing is stored before PS1 |
| `E3.2.7.1` | nltk's «one door» is three | **built** — the door; the `lexname` rebuild still owed |
| `E3.11` | knowledge read from migration FILES, never the body | open — QM weighs it P3: sandbox-era by design |
| `E3.8.3` | the audit stale: ten constants after it, and its `SAYING_VERBS` row false | open — at E3's real close; the row is annotated |
| `E3.3.4.1` | the schema enforces less than the ratchets test | *for the Captain* |
| `E2.3.1` | `Pov` and `AttitudeRow`, two spellings of one attitude | *for the Captain* |
| `E1e.6.1` | the drill-gate section gate is knowingly red | **unchanged, by ruling** — the review proposed amending now; the Captain ruled E1e (tests follow decisions, 09-25) |
| `E3b.3.2` | E3b is planned on tk1 rows the guard forbids | *for the Captain* — one ruling with `E1e.9` |
| `E3.13` | ten carried-in features placed in no epic | open |
| `E3.1.1` | stanza · spacy-stanza · torch undeclared, unpinned | **built** — a `station` optional group |
| `E1e.10` | exception rows justified by the cases that score them; only `db/0038` held out | *for the Captain* — a standing rule |
| `E1e.8.1` | the spine reaches WordNet | **built** — stubs injected |
| `E1e.8.2` | 16 stanza tests unmarked | **built** — marked `skeleton` |
| `E1e.8.3` | `test_migrations` ~40 min in a section gate | open |
| `E3.2.17` | `compile.py`, one class of ~2,650 lines mutating shared rows; comments drifted | comments corrected; the refactor at E3's close |

**`E3.7` → `E4.3.1`.** The unplaced sense had a plan entry and no status. Which sense a word has is
not the station's (req 11: the sense slot is emitted OPEN); it is met where senses are bound.

## The reconciliation

- every roadmap id now appears in `plan.md` — inline where the plan's prose already told the story
  (`E3.2.4` … `E3.2.16.2`, `E3.2.1.1 – .3`, `E3.5.1.1 – .3`, `E3.6.1`), and as a one-line index under
  `E3.3` where the reasoning lives only in the notes;
- the `G`-labels are gone from the plan; the note that used them keeps its label → id table;
- the ~15 findings `202609241130_…` listed without ids are numbered under their sources there
  (`E3.3.2.12 – .13`, `E3.3.2.1.2`, `E3.3.2.7.1`, `E3.3.2.5.1.1 – .3`, `E3.3.2.10.3 – .7`,
  `E1e.6.2`, `E1e.8.3`). Those found while building `E3.3.2.10.1` sit one level up, as siblings of
  `E3.3.2.10.2`, with the origin written — the rule's allowance for deep nesting;
- ten E3 notes gained their `*Roadmap:*` header;
- stale text corrected: `E3.3`'s numbers, `E3.3.2`'s «open» list, `E3.3.1`'s missing DONE, `E3.4`'s
  deferral, `E3.8`'s second «Done when», the roadmap's `E3.3` line.

*Not done, and named*: E0–E2's tasks have no dotted ids. They are landed, and the rule's own
«immutable» means a closed epic is not renumbered for the sake of form; an item found under one
(`E2.3.1`) takes its id from the task number the plan gives it.
