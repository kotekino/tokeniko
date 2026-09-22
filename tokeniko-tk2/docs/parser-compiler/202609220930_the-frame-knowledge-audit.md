# parser/compiler — THE FRAME/KNOWLEDGE AUDIT, E3's CLOSING ACT, 2026-09-22

> *«At the end of E3 we should go through everything we have done and double check if something we
> consider frame should be moved in the knowledge kingdom.»* — the Captain, 2026-09-16

**52 module-level constants across `tk2/language/` and `tk2/tkzip/`.** Each was re-asked the frame
test — *is this LAW, or a revisable fact about a language, a resource or the world?* — and the
sharper form the rule grew on 2026-09-17: **before asking where a list should live, ask why there is
a list.**

**Four should move. Two of the plan's own suspects should not, and both were stale.** The rest are
argued below rather than waved through, because the rule's own lesson is that the answer is not
obvious from inside the decision.

---

## WHAT CHANGED THE PICTURE: THE 2026-09-18 RULING WAS NEVER APPLIED TO THIS LIST

> *«Turning a string into a tree, and reading the tree's SHAPE — its relations, its word order, its
> punctuation — is frame. Anything matched against what was decoded is knowledge.»*

Most of the flagged list is **sets of UD relations**, and they were all flagged with one sentence:
*«this is a set of UD relations living in code»*. That shape argument does not survive the ruling
above — but it also does not clear the whole family, because the sets are not all doing the same
job. They split cleanly once asked what each one DECIDES:

**Sets that read the tree's shape — FRAME.** `SUBJECT_DEPS` · `OBJECT_DEPS` · `NOMINAL_DEPS` ·
`COORDINATE_DEPS` · `EMBEDDING_DEPS` · `RELATIVE_CLAUSE_DEPS` · `COMPLEMENT_CLAUSE_DEPS` ·
`ADVERB_DEPS`. Every member is a relation whose UD definition already names the structural kind —
`nsubj` IS a subject, `acl` IS a clausal modifier of a noun. The reading is transcription, and no
evidence about English revises it.

**Sets that rule what a shape MEANS — KNOWLEDGE.** Two, below.

*That distinction is the audit's main product: the family was flagged as one thing and is two.*

---

## THE FOUR THAT SHOULD MOVE

**1. `SAYING_VERBS` (`utterance.py`) — confirmed, and already correctly flagged.** Nine English verb
keys in a frozenset. It flags itself, names its own replacement — req 55's nearest-anchor geometry
over a small anchor set, *«so the classification never misses the verb nobody thought of»* — and
**E4 owns that geometry**. It is down to **two readers** (`utterance.py:194`, `compile.py:1280`),
the third having gone when the bare-`ccomp` rule stopped consulting it. *Blocked, not undone: moving
it to rows before E4 would be a second closed set in a second place.*

**2. `DEPS_THAT_COMPILE_TO_NOTHING = {"vocative"}` (`compile.py`) — a RULING wearing a set.** It does
not read the tree's shape; it decides that a shape carries no content. *«The vocative is addressing,
not content»* is E2's own ruling, made in the drill — and a ruling is a row. **One element, which is
the tell**: a one-member set is never a set, it is a decision with brackets round it.

**3. `CLAUSE_DEPS`'s `xcomp` EXCLUSION (`compile.py`) — the same, and argued at length in situ.** The
membership is shape-reading and frame; the deliberate ABSENCE is not. *«You like TO SWIM is one
predication with a controlled subject, not two claims: nobody asserts that you swim»* is a semantic
judgement about English complementation. **The set stays, the exclusion becomes a row** — it is the
same fact `db/0010` records about joining words, one relation further out.

**4. `NUMBERED_UPOS = {"NOUN"}` (`compile.py`) — mine, written 2026-09-21, and the audit's own
catch.** It answers *which parts of speech state a number the SPEAKER chose*, and the whole argument
for excluding `PROPN` was that **UD tags every proper noun `Number=Sing` by default morphology
rather than on evidence**. That is a claim about a resource's behaviour, which is the definition of
knowledge. It measured well (fixpoint 65 → 66) and it is still a fact about English and stanza, not
a law.

---

## THE TWO THE PLAN SUSPECTED THAT SHOULD STAY — AND WHY THE LIST WAS STALE

**`CLAIMED = 1.0` — the suspicion rests on a false premise.** The plan reads *«a threshold in code is
the shape `db/0002` and `db/0007` exist to refuse»*. **It is not a threshold.** Every use is an
assignment (`truth=CLAIMED`) or an equality (`row.truth == CLAIMED`); there is no `>=` anywhere.
It is the NAME of the top of a scale the schema defines as `[0, 1]`, exactly as `DENIED = 0.0` names
the bottom. The placement floor was a tuned cut-off and deserved its refusal; this is a coordinate.
**FRAME.**

**`RELATION_FILLS_ROLE` — the judgement it was flagged for has already moved.** The plan reads
*«`nsubj → agent` and not «agent or experiencer» is a JUDGEMENT the station declines to make»*. That
was true when written and is not now: `db/0018`'s rows settle which role a subject takes, by what is
predicated of it («the cat CHASED» · «I LOVE» · «God EXISTS»), and `_subject_role` reads them
(req 22). What is left in code is the structural default, which req 12 rules is the compile core's
half of the 37→18 mapping. **FRAME — and the candidate list should have been updated when `db/0018`
landed.**

---

## ONE I CANNOT SETTLE, AND IT IS A REAL SPLIT

**`UD_DEP_TO_ROLE` (`closed.py`) is TWO THINGS in one literal.**

- **WHICH roles a relation admits** — `nsubj` admits `referential`, `relative`, `interrogative`…
  That is shape-reading. **Frame.**
- **The ORDER, which is BEST-FIRST** — and the map's own comment says so. An ordering is a claim
  about *which reading is commoner in English*, which is a fact about a language and revisable by
  counting. **Knowledge.**

The two are welded together because a Python dict value is a tuple and the tuple carries both. I do
not think this is mine to rule: splitting it means the admissible set stays in code and the
preference becomes rows, and that is a schema for the rows plus a reader. **It wants the Captain.**

*The same welding exists, smaller, in `UD_POS_TO_WORD_CLASS`: the plan flags «UD's `AUX` covers our
auxiliaries AND our modals» as a statement about English. It is — but it is a statement about how
two PUBLISHED tag sets align, revisable only by re-reading either standard, never by evidence about
the world. Frame, with the tension recorded rather than dissolved.*

---

## ARGUED AND CLEARED — the rest, by family

**UD's own published inventories** — `UD_POS` · `UD_DEPS` (`skeleton.py`). Transcription of a
standard. Not even our set.

**Mappings between two published vocabularies** — `UD_POS_TO_WORD_CLASS` · `POS_LETTER` ·
`UD_NUMBER` · `UD_DEP_SETTLES_ROLE`. `closed.py` already rules this family frame, and every entry is
a relation whose UD definition names the thing.

**Word order and orthography, ruled frame on 2026-09-20** — `SUBJECT_ORDER` · `OBJECT_ORDER` ·
`CIRCUMSTANCE_ORDER` · `QUESTION_MARK` · `SIBILANTS` · `VOWELS` · `NEVER_DOUBLE`. *The spelling
RULE is frame and its EXCEPTIONS are rows — `db/0022`, and `db/0024`/`db/0027` after it. That split
is already right and is the model for the others.*

**English words held as KEYS, each already carrying its argument in situ** — `COPULA = "be"` (the
structure of a predication; the word itself comes from the inflection roster) · `DO = "do"`
(do-support is word order) · `NOMINATIVE`/`ACCUSATIVE` (that a subject takes the nominative is
grammar; WHICH FORM spells it is in the rows' `features`) · `IMPERATIVE_VERB = "want.v"` (tkzip
req 48's own ruling — mood is not a field).

**Names, not rosters** — `FUSED_QUANTIFIER` (the roles live in rows; this is one spelling shared by
two readers) · the adverb scopes `EPISTEMIC`/`EVALUATIVE`/`DISCOURSE`/`CIRCUMSTANTIAL`/`MANNER`
(req 23's split; the KINDS are `db/0013`) · the Penn tags `PRESENT`/`PAST`/`PARTICIPLE`/`PLURAL`.

**Internal pipeline** — `ROW_PREFIXES` · `CLOSED_KIND_PLACES` · `LATER_PASS_OWNS` · `SCHEMA_VERSION`
· `THEATRE_EPOCH`. These name our own machinery and no language revises them.

---

## WHAT IT COSTS

Three of the four moves are one migration between them — a `ud_relations` table with a `compiles_to`
column would hold the vocative's ruling and the `xcomp` exclusion, and `NUMBERED_UPOS` is a column
on rows that already exist. **`SAYING_VERBS` is not a migration at all**: it waits for E4, and
writing it into rows now would create the second closed set the move exists to remove.

**Nothing here is moved by this document.** The plan says each one is *discussed, not self-marked*,
and the discussion is what this is.

---

# THE MIGRATION — `db/0032`, AND WHAT IT COST TO DO PROPERLY

*Applied 2026-09-22. Three of the four moves; `SAYING_VERBS` waits for E4 and must.*

    fixpoint    68 of 87 · 18 MOVED · 1 SILENT · 58 of the 70 read whole   UNMOVED
    drill gate  65 agreed · 5 DISAGREED · 17                               UNMOVED

**A relocation that moved a measurement would have been a change in disguise.** Nothing moved,
which is the only result this work was allowed to have.

## `CLAUSE_DEPS` GOT BIGGER, AND THAT IS THE WHOLE POINT

The obvious way to do this was to write a row saying `xcomp` opens no clause and leave the set
excluding it anyway. **That row would have been decoration** — the code would never have consulted
it, because `xcomp` was not in the set to be asked about.

So the set now holds every relation UD NAMES as a clause, `xcomp` among them, because UD is right
to call it an «open clausal complement». The set became pure transcription — and therefore honestly
frame, which it was not before — and `_clause_heads` asks the table which of them earns a row.

**A set whose membership encodes an argument is an argument with brackets round it.** Removing the
brackets is not the fix; moving the argument is, and the set has to be honest afterwards or the
move was cosmetic.

## THE DEFAULT IS NOT A ROW — `db/0013`'s SHAPE, AND WHY IT SCALES

Three defaults live in code as the QUESTIONS the station asks — *does this compile to content · does
this open a clause · does this state a number* — and the rows hold only what differs. A miss is an
ANSWER, so the ordinary reading costs nothing and the table stays small enough to curate. The
migration's own `_check()` refuses a row that merely restates a default, which is what keeps it
that way.

*`UD_NUMBER` stays in code and should: `{"Sing": "sg", "Plur": "pl"}` is two notations for one
fact. What moved is the judgement about WHICH part of speech's Number is evidence at all.*

## ONE TEST HAD TO CHANGE, AND IT IS THE INSTRUCTIVE PART

`test_an_xcomp_stays_inside_its_clause` asserted `"xcomp" not in CLAUSE_DEPS`. **It pinned the
implementation while its name promised the behaviour** — and the implementation is exactly what
this work moved. It now compiles «You like to swim» and asserts ONE content row, with a second test
confirming the ruling is readable from the table.

A test that pins an implementation cannot survive the implementation moving, and the thing worth
protecting was never the set: it was the zip.

## WHAT IS STILL OPEN

- **`SAYING_VERBS`** — nine verb keys, two readers. Req 55 rules the replacement (nearest-anchor
  geometry over a small anchor set) and **E4 owns it**. Rows now would move a closed set rather
  than remove one.
- **`UD_DEP_TO_ROLE`'s welded order** — WHICH roles a relation admits is frame; the BEST-FIRST
  ORDER is a claim about which reading is commoner in English. One tuple carries both, and
  splitting it is the Captain's to rule.
