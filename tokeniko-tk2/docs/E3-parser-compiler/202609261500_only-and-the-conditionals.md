# parser/compiler — «ONLY», AND THE CONDITIONALS, 2026-09-26 15:00

*Roadmap: `E3.12.5.9` · `E3.12.5.9.2` … `E3.12.5.9.11`*

*A bench, not a build (1st Officier; real stanza, drill context, closed classes v20; scratch
`$CLAUDE_JOB_DIR/tmp/cond/`). Asked by the Captain after the QM proposed a row «if and only if» → EQ
to make `only-5` pass: «You are asking the wrong question: how can I make the test not fail? […] how
can [the zip] store all the information of that sentence, respecting the goal and the constraints?»*

## The question, and the hypothesis it tested

«If and only if it rains, I stay home» was never compiled as an equivalence: no row, «if» read alone
as a one-way IMPLY, «only» and «and» cut. The QM's hypothesis: the information is COMPOSED — «if» the
sufficient condition, «only» the necessary one (the converse), «and» their conjunction, IMPLY ∧ CONV
= EQ; and «only» is one meaning that also reverses «Only cats eat fish».

## The verdict — PARTLY SUPPORTED, and refuted where it mattered

- **Holds**: «only» has ONE meaning across nouns and clauses — *nothing but its associate satisfies
  the frame*. «if and only if» is «if» ∧ «only if», so AND(IMPLY, CONV) ≡ EQ — logic.
- **Refuted as written**: «only» does not ADD the converse to «if», it REPLACES the direction. «I stay
  home only if it rains» is S → R and does not entail R → S; were «only» additive, it would be EQ,
  which is wrong. [[only]]([[if]]) = CONV alone; «and» then conjoins two complete connectives over
  the same pair of clauses. *(The Captain's own example agrees: «it rains only if I stay home» is the
  same claim as «if it rains, I stay home».)*
- **One schema for both**: the associate goes to the CONSEQUENT — a clause associate reverses the
  join; a noun associate becomes a universal binder whose consequent is «is the associate» (the
  drill's `only-6`, `only-3` shape).

## What the station does today

No row for only · just · strictly · exactly · solely · merely, in either roster. The adverb default
files each as a **`manner` box** — «it rains in an only manner» — and the «if» join keeps its
sufficient direction. So **every «only if» / «only when» compiles the REVERSE claim**, a wrong claim
by `E3.12.5` (4); the only trace is `defaulted`, outside the zip.

| sentence | stanza | today | information | gap |
|---|---|---|---|---|
| If it rains, I stay home · I stay home if it rains | if mark → rains | IMPLY(R,S), unasserted | R → S | none |
| I stay home only if it rains · Only if it rains (do) I stay home | **only advmod → rains** | IMPLY(R,S) + only·manner | S → R | **wrong claim** |
| It rains only if I stay home | only advmod → stay | IMPLY(S,R) + only·manner; «home» lost | R → S | **wrong claim** + silent loss |
| If and only if it rains, I stay home · I stay home if and only if it rains | only conj → if (a mark); and cc → only | antecedent withheld, lone S | R ↔ S | quality, over-withheld |
| I stay home if, and only if, it rains | rains conj → stay (misparse) | IMPLY(R,S) + only·manner | R ↔ S | silent loss (S → R) |
| I stay home just if / strictly if it rains | just → rains · **strictly → stay** | IMPLY(R,S) + manner | S → R or R ↔ S (marginal English) | wrong claim; ambiguity unrecorded |
| I stay home exactly when / only when it rains | when ADV advmod | AND, both asserted | ∀t S(t) ↔ R(t) · ∀t S(t) → R(t) | **wrong claim** |
| Unless it rains, I go out · I go out unless it rains | unless mark → rains | IMPLY(R,G) | ¬R → G | **wrong claim** (polarity dropped) |
| I stay home provided that it rains | provided VERB advcl | an attitude «provide», all asserted | R → S | **wrong claim** |
| I stay home as long as it rains | «as long as» keyed at its first token, missed | AND, both asserted | R → S or ∀t R(t) → S(t) | **wrong claim** |
| I stay home when it rains | when ADV advmod | AND, both asserted | ∀t R(t) → S(t) or episodic | wrong claim (generic) |
| Only cats eat fish · Only John came · Only smoking causes cancer | only → the noun | the claim + only·manner | ∀x (P(x) → x = associate) | «only» lost + a wrong manner box |
| Cats only eat fish · John only came · I only stay home if it rains | only → the VERB, whatever the focus | same | 3+ readings | «only» lost; ambiguity unrecorded |
| I stayed home only because it rained | only → rained | IMPLY(R,S), both asserted + manner | «no other reason» | exclusivity silently lost |

**Operators**: the schema has all ten, including `CONV` and `NCONV` («`CONV` is NOT `IMPLY` with the
operands swapped: row order carries scope»); no closed-class row compiles to eq, conv, nimply, nconv
or xor.

## Findings, with ids

- `E3.12.5.9.2` **⚑ «only» REVERSES the direction and no row says so** — every «only if» / «only
  when» compiles the reverse claim
- `E3.12.5.9.3` **the focus particles have no row** (only · just · exactly · strictly · solely ·
  merely · even · precisely) and fall to the `manner` default, measured on `-ly` adverbs — a wrong
  manner box each time
- `E3.12.5.9.4` **⚑ «unless» / «lest» polarity is never read** — `features.polarity` exists on four
  rows; «Unless it rains, I go out» comes back «If it rains, I go»
- `E3.12.5.9.5` **⚑ «when» never reaches its conjunction row** — stanza tags it `ADV advmod`, never
  `mark`; the default join is AND with both halves asserted
- `E3.12.5.9.6` **a multi-word joiner is keyed at its first token** — «as long as» missed; «provided
  that» parsed as a verb becomes an attitude
- `E3.12.5.9.7` **two manner adverbs collide in one box** — «home» lost while `placement` says both
  were placed: a silent loss
- `E3.12.5.9.8` «if and only if» has two trees, by comma; with commas stanza misreads the clause
- `E3.12.5.9.9` a pre-verbal «only» — the tree does not give the associate (3+ readings)
- `E3.12.5.9.10` the «as long as» row asserts BOTH halves; the conditional reading asserts neither
- `E3.12.5.9.11` «only because» — exclusivity is not truth-functional when both halves are asserted

## What it needs — for the Captain

1. Does «only X P» CLAIM P(X)? The drill (textbook) drops it; English presupposes it for nouns;
   «only if» does not entail «if» — and iff = if ∧ only-if needs the textbook reading for conditionals.
2. Are joins MATERIAL truth functions? With both halves asserted, IMPLY, CONV and EQ are all true —
   «only because», generic «when».
3. The normal form: EQ or AND(IMPLY, CONV); CONV(R,S) or IMPLY(S,R).
4. Where «only» and «exactly» live: the closed classes, or the adverb kinds (no «focus» kind). The
   per-word meaning is knowledge; «the associate goes to the consequent» looks like logic.
5. The manner default for particles outside the population it was measured on: keep, or abstain.
6. «as long as» asserting both.

## `E3.12.5.9.12` — ruled *(the Captain, 2026-09-26: «accepted all your leans»)*

1. **«only X P» on a NOUN keeps P(X) claimed** — a presupposition, kept as the definite's relative
   clause is (`E3.3.13`); **on a CONDITION it does not** — «only if» does not claim «if», which is what
   makes «if and only if» compose.
2. **Joins are truth-functional** — the format's law. What is not («only because», a generic «when»)
   is RECORDED as lost until it has a home, never dropped in silence.
3. **Normal form**: «only if» → `CONV`, sentence order kept (row order carries scope); «if and only
   if» → `EQ`.
4. **Where the words live**: «exclusive» (only · just · solely · merely) and «identifying» (exactly ·
   precisely) are per-word KNOWLEDGE, rows; «the associate goes to the consequent» is LOGIC, frame.
5. **The manner default stays inside the population it was measured on**; a particle outside it
   abstains and is recorded.
6. **«as long as» claims neither half**, as «if» does.

Order: the cheap wrong claims first (`E3.12.5.9.4` «unless», `E3.12.5.9.5` «when»), then the «only»
composition (`E3.12.5.9.2`, `.3`), then the multi-word joiners (`E3.12.5.9.6`, `.10`), then `.7`.

## Built *(1st Officier, 2026-09-26)* — five steps, one STOP

- `E3.12.5.9.4` **«unless»** — the joiner's `polarity: negative` puts a negation over the clause it
  introduces: ¬R → G. No new rows
- `E3.12.5.9.5` **«when»** — a wh-word under `advmod` of an `advcl` takes its subordinator row (the
  clause relation decides, not the word). IMPLY with neither half claimed — entailed by the generic
  AND the episodic reading — and the lost ∀t / episode recorded in `abstained` (ruling 2)
- `E3.12.5.9.2` · `E3.12.5.9.3` **«only»** — `db/0039` (closed classes v21 + adverb kinds v4, NOT
  applied): only · just · solely · merely EXCLUSIVE, exactly · precisely IDENTIFYING, in the ADVERB
  KINDS as a fifth kind `focus` (the closed-class forms filter D's vocabulary, and stanza tags all six
  `ADV advmod`). The logic composes DIRECTIONS: «if» sufficient, «only» necessary, their union both —
  «only if» → CONV, «if and only if» (both of stanza's trees) and «exactly when» → EQ; operands in the
  order «if» gives them, the introduced clause first. A noun associate → ∀x (frame(x) → x is the
  associate), the prejacent kept claimed. Pre-verbal «only» and «only because» left unplaced and
  recorded; «I only stay home if it rains» withheld. The decompiler says all of it back
- `E3.12.5.9.6` · `E3.12.5.9.10` **multi-word joiners** found by their span («as long as»); «provided
  that» read as a VERB is treated as the joiner; «as long as» claims neither half
- `E3.12.5.9.7` a box already taken no longer places a second word — it goes to `unplaced`

**STOP — ruling 5's premise was false.** `db/0013` measured the manner default on ALL 3,767 WordNet
single-word adverbs, and «only» is inside that population; neither fact the resource states isolates
the focus particles («only», «just», «even» have no pertainym; «exactly», «strictly», «simply»,
«solely» do). «strictly if» stays a wrong claim; «even» stays manner.

**Gates**: fixpoint 74 · 9 · 1 + WITHHELD 3, read-whole 64/70 → **63/69** (`only-5` in, FIXED; `only-3`,
`only-4` out, «only» now unplaced) · drill 64 · 4 · 19 → **62 · 6 · 19** · UD 32 · 0 · 13 unchanged.
Red: the frontier coverage ratchet (0.784 → 0.778: «early» in «The guy, John said, left early in the
morning» was counted placed while lost — step 5 made it honest) and the drill-gate pin (`only-6`,
`t-ws-3` DISAGREED: the drill's halves of an implication default to truth 1.0, the station's are
unclaimed — req 38, ruling 1).

**Found, with ids:**
- `E3.12.5.9.13` **the ORPHAN, again** — `t-ws-3` «A person is wrong when he says false»: «false»
  cut in the antecedent withholds it, and «a person is wrong» is left stated, unclaimed, joined to
  nothing: SILENT. The shape `only-5` showed before «if and only if» was built
- `E3.12.5.9.14` «lest» — stanza hangs it `advmod` under a `parataxis`; AND, both claimed: a wrong
  claim, pre-existing
- `E3.12.5.9.15` «I did not swim, nor did I run» → NOR(¬swim, run), a double negation, pre-existing
- `E3.12.5.9.16` «just in case» would compose to CONV if «just» hangs off the clause head
- `E3.12.5.9.17` «the only cat» — «only» tagged ADJ, an attributive row «x is only», pre-existing
- `E3.12.5.9.18` «wherever»'s row asserts both halves — a wrong claim if ever reached
- `E3.12.5.9.19` the decompiler refuses a folded conjunction inside a supposition, pre-existing
- `E1e.6.4` the drill's `c()` claims the halves of a quantified implication (`only-6`, `t-ws-3`), and
  `only-4` encodes «only because» as EQ, which ruling 2 overrides

## Ruled *(the Captain, 2026-09-26: «accepted all your leans, apply 0039»)*

- `E3.12.5.9.3.1` **ruling 5 replaced** — its premise was false (the default was measured on ALL
  adverbs). The manner default STAYS; each focus word met gets its own row, and where its meaning is
  not settled («even», «strictly») the row says ABSTAIN. Knowledge grows word by word
- `E3.12.5.9.13` the orphaned row is withheld with its partner — the sentence is WITHHELD, not SILENT
- CONV's operands in IMPLY's convention (the introduced clause first) — confirmed; the `focus` kind —
  confirmed
- the frontier coverage ratchet re-based (the honest «early»)
- `E1e.6.4` brought forward: the drill amended to rulings 1 and 2
- **`db/0039` APPLIED** to `tokeniko_tk2` — 39 applied, 0 pending. *(`tools/migrate.py` applies on
  sight: it has no dry run.)*

## The rulings built *(1st Officier, 2026-09-26)*

- `E3.12.5.9.3.1` `db/0040` (adverb kinds v5, NOT yet applied): «even», «strictly», «simply» —
  `focus`, meaning `abstain`, no voice. «abstain» is a meaning in the shared vocabulary, so no word
  list: an abstaining row leaves its word unplaced with the reason; over a condition it withholds the
  conditional, whose direction is unsettled. «I stay home strictly if it rains» → WITHHELD (was the
  wrong claim IMPLY); «Even cats eat fish» → «even» unplaced, the claim kept
- `E3.12.5.9.13` `_stranded`: an unclaimed content row named by no join and no prefix, not dissolved
  and binding nothing live, goes with its withheld partner. `t-ws-3` → WITHHELD
- the frontier ratchet re-based: whole 11 → 10, mean 0.78 → 0.77
- `E1e.6.4` the drill amended: `only-6` (halves unclaimed, the prejacent claimed and AND-ed to the
  rule, as ruling 1 says), `t-ws-3` (halves unclaimed), `only-4` (the because-join, «only» unplaced,
  partial); the drill's own bar 82 of 87 (94.3%)

**Gates**: fixpoint **74 · 9 · 0, WITHHELD 4**, read-whole **63 of 69**, SILENT 0 · drill **63 · 4 · 20**,
the disagreements back to the four named families · UD 32 · 0 · 13, WRONG 0.

*Found*: «even if» is a closed-class form of its own and never reaches the «even» row (IMPLY, entailed)
· «simply because» over-withholds as «only because» does (`E3.12.5.11`).
