# tkzip — THE FIRST DRAFT (the Captain's own, in excel)

*Transcribed 2026-09-11, at E2's opening, from `doc/notes.xlsx` → tab **TKZIP2**. The original is
undated and **predates the 2026-08-11 conception session** — it is what that session was held
about. The requirements distilled from it; this is the artefact they were distilled FROM.*

> **Why this file exists.** The draft generated `requirements.md` and was then reachable only
> inside a binary spreadsheet — invisible to grep, invisible to every tool a session reaches for
> first. At E2 the QM rebuilt the role inventory from VerbNet, PropBank and FrameNet and
> independently re-derived a box (`with` / comitative) that this draft had on day one. Two routes
> converging is real evidence, but the second route should not have been necessary.
> **The Captain's ruling, 2026-09-11: the chapter documentation is the decision record, and an
> origin that cannot be read is not documentation.**

---

## The shape

```
original │ OP │ POINT OF VIEW │ THEATRE │ SUBJECT │ PREDICATE │ DIRECT │ INDIRECTS
                subject,pred    (stm)     part,      pred, st   part,     material · destination
                                          rel,                  rel,      advantage · how · with
                                          noun                  noun      tool · agent · goal · cause
```

- **`OP`** — the operator joining this row to the previous: `AND`, `IMPLY`.
- **`point of view`** — an attitude wrapper (subject + predicate), e.g. «me / think».
- **`theatre (stm)`** — the clause's spacetime, as four bracketed axis pairs
  `[t_from,t_to][x_from,x_to][y_from,y_to][z_from,z_to]`. Eight values — the same width as v1's
  `TKZip.map`.
- **the noun-phrase record** — every nominal box is three fields: **`part`** (the quantifier:
  all / many / one), **`rel`** (the possessor: «my cat» → `rel=me`), and the noun itself.
  Possessors inside indirect boxes are written inline as `(owner)thing`.
- **`st`** — the predicate's index into the theatre's time axis (`t-1`, `t-2`).
- **the nine indirects** — `material` · `destination` · `advantage` · `how` · `with` · `tool` ·
  `agent` · `goal` · `cause`.

`*` means an empty slot — present, unfilled. **Fixed arity is visible in the draft itself.**

---

## The rows, transcribed verbatim

| original | OP | POV | theatre | subj part·rel·noun | pred · st | direct part·rel·noun | indirects |
|---|---|---|---|---|---|---|---|
| my cat is cute | AND | me / think | * | * · me · cat | cute · * | * | — |
| felines are mammals | AND | * | * | all · * · feline | mammal · * | * | — |
| a wire is ligament made of metal | AND | * | * | all · * · wire | ligament · * | * | — *(gap: «of metal» unfilled)* |
| I gave my sister a book | AND | * | `[t-1,t-1][*,*][*,*][*,*]` | * · * · me | give · t-1 | * *(gap: «a book» unfilled)* | destination = (me)sister |
| I went from Rome to Genoa to see the ligurian sea | AND | * | `[t-2,t-1][r(x),g(x)][r(y),g(y)][r(z),g(z)]` | * · * · me | go · t-2 | * | — |
| ⤷ *(second row)* | **IMPLY** | * | * | * · * · me | see · t-1 | one · liguria · sea | — |
| she works for her family | AND | * | * | * · * · she | work · * | * | advantage = (she)family |
| my cats are orange | AND | * | * | many · me · cat | orange · * | * | — |
| the hammer is made of titanium | AND | * | * | one · * · book *(typo for hammer)* | * | * | material = titanium |
| the mail was written by John | AND | * | `[t-1,t-1][*,*][*,*][*,*]` | one · * · mail | write · * | * | **agent = John** |
| I study for the exam | AND | * | * | * · * · me | study · * | * | **goal = exam** |
| my house was destroyed by the tornado | AND | * | * | one · me · house | destroyed · * | * | **cause = tornado** |
| I build my contraption with my hammer | AND | * | * | * · * · me | build · * | one · me · contraption | — *(gap: «with my hammer» unfilled)* |

*Gaps are transcribed as gaps. It is a draft and the Captain said so; silently completing it would
destroy the evidence of what the draft did and did not reach.*

---

## What the draft decided, and where each landed

| the draft's idea | where it went |
|---|---|
| **fixed arity, `*` for empty** | req 1 — settled, never reopened |
| **the theatre** — spacetime as four axis pairs | v1's `TKZip.map` (8 floats) + per-entity 12 dims. **E2 ruled 2026-09-11: DERIVED, not a replacement for boxes** — «Genoa is a thing you can reason about: it's a city, somebody is born there» |
| **the noun-phrase record** (`part` · `rel` · noun) | **E2 ruled: adopted.** The quantifier is per noun phrase, not one per clause read off the subject (v1's limit). It is also open question 7's home |
| **point of view** as a wrapper | attitudes / nesting — E2 task 2, open question 8 (Tseitin) |
| **`with` as its own box** | **`comitative`.** Not in VerbNet's 29, not in PropBank's adjunct labels. The draft had it before any corpus did |
| `tool` · `how` · `advantage` · `material` | → `instrument` · `manner` · `beneficiary` · `source` |
| **surface `subject` kept beside `agent`** | «the mail was written by John» keeps *what it is about* AND *who did it*. **E2 ruled: roles normalize to deep roles, topicality survives as one non-geometric marker** |
| **`goal` box AND `IMPLY` between rows** | **the draft encodes purpose twice** — which is precisely why open question 3 was opened and why the IMPLY form was withdrawn as unsound (it would derive that an intended outcome occurred). E2 ruled: purpose is an operator between rows, one encoding only |
| `cause` as a box | E2 ruled: cause-as-participant merges into `agent` (volition is readable from the filler); cause-as-circumstance is a row + CAUSE operator |
| copular «cute» / «mammal» **in the predicate slot** | E2 ruled: a `complement` box exists, and plain copular `be` compiles to structure and never fills the predicate — so «the cat is cute» still comes out as *cat + cute, no verb*, while `become` / `seem` / `remain` keep a home |

---

*Source: `doc/notes.xlsx`, tab `TKZIP2`. The workbook also holds `General schema`, `Key Concepts`,
`LL`, `Components`, `Compiler`, `Examples`, `Problems`, `Next step`, `Inconsistencies` — none of
them transcribed yet; read them before reopening a question they might already have answered.*
