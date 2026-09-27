# parser/compiler — THE ATTITUDE FAMILY'S WRONG CLAIMS, AND ONE SPELLING FOR A RESTRICTION, 2026-09-27 21:00

*Roadmap: `E3.3.11.2.5.1` · `E3.3.11.2.1.1` · `E3.3.11.2.6.1` · `E3.3.11.2.8.1` · `E3.3.14` · `E3.3.15` · `E3.3.16` —
found: `E3.3.14.1` · `E3.3.14.2` · `E3.3.14.3` · `E3.3.14.4` · `E3.3.14.5` · `E3.3.14.6` · `E3.3.14.7` · `E3.3.15.1` ·
`E3.3.16.1` · `E3.3.11.2.8.3`*

*1st Officier, on the QM's work order. Measured first (HEAD, the QM's probe `station.py`, a 42-sentence
bench), then built only what needed no new ruling. Artifacts: `$CLAUDE_JOB_DIR/tmp/attf/` (bench and
three variant batches, each run on HEAD — an archive copy in `/tmp` — and on the build).*

## Verdict

**Seven items closed or honestly withheld; the gates did not move** — fixpoint 72 · 9 · 0 + W6, read-whole
61/67 · drill 62 · 4 · 21 · UD 30 · 0 · 15, WRONG 0. One instrument number moved: the drill's prefix pairs
35 → 33 (`aw-15`, below). Six things need the Captain.

## The cause

**ONE ROOT for `E3.3.14`, `E3.3.11.2.5.1` and `E3.3.11.2.1.1`: a restrictive modifier had two spellings.**
An attributive adjective was a row AND-joined to what its binder scoped (req 70); a relative clause was a
row held by the shared variable alone (`_share_variable`), its binder minted LATE, after the clause's own
prefix. So:
- nothing that scoped the matrix scoped the relative clause — «I think that a man who sleeps is tired»
  claimed a man sleeps (`E3.3.11.2.5.1`);
- the late binder was appended after the clause's «not» — «The man who left was not happy» → «Not the
  man that left was happy», at top level too (`E3.3.11.2.1.1`);
- the adjective's join was AND whatever the binder — «Every tired man sleeps» → ∀x (tired ∧ sleep):
  every man is tired; «No tired man sleeps» claimed its halves under ¬∃;
- and the adjective's binder moved out past every row before it — «NOT every tired man sleeps» came out
  ∀¬ (said «Every tired man does not sleep»), «He does NOT see a tired man» claimed the man. *Found here;
  not on the list.*

**The QM's lean — one spelling, AND for ∃ / ¬∃ / definite, IMPLY for ∀ / ¬∀ — VERIFIED**, against:
- the drill: AND for ∃ (`t-dc-1`, `aw-15`), a relative clause AND-joined to its matrix (`t-ws-8`), IMPLY
  with stated halves under ∀ (`t-ws-3`, `only-6`, amended at `E1e.6.4`);
- `_share_variable`'s «a restriction is stated, not claimed» — kept, and refined: stated under ∀ / ¬∀ /
  ¬∃, claimed under ∃ (∃x (R ∧ S) entails ∃x R), claimed under a definite (`E3.3.13.1`'s presupposition);
- `UPWARD_*`: `position()` reads the joins, and IMPLY's antecedent is downward exactly as ∀'s restriction.

**One refinement the lean did not name: the join stands WHERE ITS BINDER STANDS** (req 35) — rows before
the binder scope the join, rows after stay on the clause. Without it the ¬∀ and ∃¬ defects above stay.

## What was built

- **`_box_for` raises the binder for a relative clause** with its phrase, in word order, as for an
  adjective — only where `_gap` places the gap (a filled box is now read on the tree too); a binder whose
  relative clause is withheld later is dropped when the zip is assembled (`vacant`), never mid-compile,
  where a later row would be minted under its name. **The marker stays outside** the binder for both,
  as the drill writes it and `_share_variable` always did.
- **`_modify` is the one builder**: every restriction (`_Restriction`: an adjective's key, or a relative
  clause's row) is joined around what its binder scopes, by `RESTRICTED_BY` (logic: ∀ / ¬∀ → IMPLY, else
  AND); the owner's prefix is walked innermost first, so the join enters the stack at the binder's place.
- **The truths are one shared rule**, `restriction_truths(binder, join truth)`: halves claimed only where
  the binder distributes (∃, no force) and only as much as the join claims (G9 — «If I see a tired man,
  I leave» had claimed the man tired); a definite's restriction claimed whatever the join. `_settle` writes
  it; the decompiler reads it back.
- **The decompiler reads the spelling back** (`_restricted`): a restriction join is said as its clause,
  with the join's prefix and truth; the restriction goes into the phrase (folded adjective, or relative
  clause); nested restrictions («who owns a dog that barks») read inner first; «only» (`_focused`) first.
  `_fold` never folds a tensed row or a restriction join's clause. A relative gap in an attitude's HOLDER
  is the relative pronoun («the man THAT thinks that she sleeps»). A «not» over a noun phrase's binder is
  said on the verb («He does not see a tired man», was «He sees not a…»).
- **An attitude now takes its place INSIDE a restriction** — «The man who thinks that she sleeps is happy»
  compiles whole (was withheld: «an attitude is not a row that restricts»). Under ∀ it cannot (the
  restriction is stated, and an attitude row has no truth slot) and is withheld.
- **`_described_definitely`** looks for the restriction on the first operand of the binder's join, reads
  «definite» off the determiner alone (see `E3.3.14.1`), and now also fires when the attitude in a
  definite's restriction loses its complement to a cut under it («The man who said that [cut] left»).
- **`E3.3.15` — an interrogative is an OPERATOR** (`_is_operator`: a row that `opens` binds, req 36): cut,
  it turned a question into a claim. «Which man sleeps?» is withheld.
- **`E3.3.16` — a question is neither upward nor downward** (`_unentailed`, `ASKING`): a cut from a clause
  that asks — truth open, or a slot its wh-word opened — asks ANOTHER question. «Who thinks that he
  sleeps?», «Do you think that he sleeps?», «Where do you think he sleeps?» (`E3.3.11.2.6.2`) withheld whole.
- **`E3.3.11.2.8.1` — a copula whose subject is the withheld clause** (an expletive standing for it, or a
  `csubj`) goes with it, on ruling 10 of `E3.3.11.2.16` («It is (not) true that…» withheld meanwhile).
  A VERB keeps its row: «[it] surprised me» stands, as the Captain re-based on 09-27.
- **The drill gate reads a restriction join's scope through the join, on both sides** (`claimed_through`):
  «all human beings are animals» is stated under ∀ in the drill and through ∀'s implication here — the
  same claim, which the naive slot compare called DISAGREED (`t-ws-6`).

No migration. No list or table added that is a fact about English: `RESTRICTED_BY` and
`restriction_truths` are logic (restricted quantification, monotonicity) — the charter's one exemption.

## Before → after *(HEAD → the build, real stanza)*

| sentence | HEAD | now |
|---|---|---|
| Every tired man sleeps. | ∀x (tired ∧ sleep), both claimed | ∀x (tired → sleep), halves stated |
| No tired man sleeps. | ¬∃x, halves claimed | ¬∃x (tired ∧ sleep), halves stated |
| Every man who is tired sleeps. | sleep claimed under ∀ | ∀x (tired → sleep) |
| I think that a man who sleeps is tired. | «a man sleeps» claimed outside | ATT · ∃ over the join |
| The man who left was not happy. | «Not the man that left was happy» | «The man that left was not happy» |
| They believe that the man who left was not happy. | ¬ above the definite | the definite, then ¬ |
| Not every tired man sleeps. | ∀¬ — «Every tired man does not sleep» | ¬∀ |
| He does not see a tired man. | ∃x tired man ∧ ¬see (the man claimed) | ¬∃ |
| If I see a tired man, I leave. | «a man is tired» claimed | only the conditional claimed |
| Does a tired man sleep? | mouth: «A tired man sleeps.» | «Does a tired man sleep?» |
| The man who thinks that she sleeps is happy. | withheld | whole |
| The old man who says that he sleeps is happy. | — (kept a moved definite) | withheld |
| Which man sleeps? · Which man thinks that he sleeps? | «Man sleeps.» (claimed) | withheld |
| Who thinks that he sleeps? · Do you think that he sleeps? | «Who thinks?» · «Do you think?» | withheld |
| It is true that he sleeps. · That he sleeps is true. | «True is.» | withheld |

## Gates *(before → after)*

- fixpoint **72 · 9 · 0 + W6 → 72 · 9 · 0 + W6**, read-whole **61/67 → 61/67** — one text changed, `aw-15`
  «…with a foreign licence in france» → «…in france with a foreign licence», FIXED both
- drill **62 · 4 · 21 → 62 · 4 · 21**; prefix pairs **35 → 33** — `aw-15` (`E3.3.14.2`)
- UD **30 · 0 · 15 → 30 · 0 · 15**, WRONG 0
- frontier ratchet 74.8% unchanged (a first cut of the `csubj` rule withheld «[it] surprised me» and
  dropped it to 72.8% — narrowed to copulas, per the Captain's re-base)
- gate (after the QM's blocker): spine **7 passed** · station **613 passed** · evidence **143 passed**

**Self-verification**: 125 unscripted variants in three batches (∀ ∃ ¬∃ the a some / not every · subject
and object gaps · adjectives · under ¬, ◇, □, attitudes, questions, conditionals, imperatives, tags ·
nested and mixed binders), each run on HEAD and on the build. Wrong claims the build caused: two, both
fixed and pinned — a definite with an adjective read as not definite (`E3.3.14.1`), and a definite whose
restriction's attitude lost its complement to a cut, no longer caught by the old RESTRICTION path.
Remaining wrong outputs are stanza's parses (`E3.3.14.3`).

## Tests changed, because they pinned the old reading *(tests follow decisions)*

`…bare_quantifier_binds_ITSELF…` and `…relative_clause_on_a_QUANTIFIED_phrase…` (the latter pinned
«every cat is happy» CLAIMED under ∀) · the ASKED / FRONTED / `?`-after-a-quotation / two TAG tests (the
narrower question no longer stands; the VERB-tag test moved to a host with no complement) · the
relative-clause-holding-an-attitude and DEFINITE-description tests (the attitude now takes its place;
the definite case is pinned on a passive holder) · one decompile test (an AND under ∃ of two rows about
its variable IS the one spelling — now a disjunction) · the utterance frame test (the reason is «joined»).
New: seven compile tests, two decompile, one drill-gate.

## For the Captain

1. **`E3.3.14.1` the minted binder's force** — an adjective mints ∃, a relative clause none (schema v8):
   «A tired man sleeps» and «A man who is tired sleeps» are one join but not one zip. It decides ruling 8
   («The OLD man who says that he sleeps» withheld; «The man who says that he sleeps» not), and it made
   «the tired man» read as not definite (fixed here by reading the determiner alone). *Lean: no force for
   both — `a` is an article, not a quantifier (v2 re-typing), and v8 is the later ruling; amend `t-dc-1`,
   `aw-15` (`some_of`) at E1e.* Cost: the drill's `some_of` rows stop pairing until amended; ∃ reads the
   same downstream (`restriction_truths`, `position` treat both alike).
2. **`E3.3.14.2` `aw-15` — the literal scope over a de re drill** — «In Italy, you may drive … with a
   foreign licence»: the drill has ∃L outside ◇ and the domain; the station now reads the words' order
   (req 35, `E3.12.5` (6)) — domain · ◇ · ∃L. *Lean: amend `aw-15` at E1e to the literal order.* Cost both
   ways: keep de re and the join must jump the binder over rows before it, which is what made «not every»
   ∀¬.
3. **`E3.3.16.1` a question cut is withheld whole** — built, and it reverses the reading the ASKED-attitude
   round left («the narrower question stands», `E3.12.5.1` applied to questions). *Lean: keep — an answer to
   «Do you think?» answers nothing asked.* Cost: every question with any unplaced word is withheld
   («Do you know the muffin man?»); the corpora moved by nothing.
4. **`E3.3.15.1` how «which X» is held** — withheld meanwhile. *Lean: `Box(head=man.n,
   determination=Open(sort="selection"))`* — the schema already allows `determination: Open`, and «which
   ones» is exactly what `Determination` means; the alternative is an `Open` head with the noun lost, or a
   binder with an open force (no such field). A format reading, so yours.
5. **`E3.3.11.2.8.3` the clause adjectives, composed** — «it is true that P» = P · «false» ¬P · «possible»
   ◇P · «necessary» □P · «likely» a truth below 1 · «sure / afraid / aware» the SUBJECT's attitude
   (`E3.3.11.2.8.2`). *Lean: one knowledge table, `language_clause_adjectives` (form · compiles-to: a
   prefix element, a truth, or «holder's attitude» with its verb key), read where the copula's complement is
   the attitude's word; every row by migration.* Withheld meanwhile, as built.
6. **`E3.3.14.4` the gate reads a restriction's scope through its join** (`tools/drill_gate.py`) — an
   instrument change so the one spelling and the drill's lexicalised nouns compare as the same claim.
   *Lean: keep.*

## Found, with ids

- `E3.3.14.1` · `E3.3.14.2` · `E3.3.14.4` — above, for the Captain
- `E3.3.14.3` **stanza's nominal root** — «The student who said that the exam was hard failed», «A student
  who studied passed»: stanza makes the NOUN the root, the station a subjectless row (`E3.12.1.6`'s class);
  with the attitude now able to seat in a restriction, stanza's misattached complement is claimed under
  it («the student said that the exam failed hard»). HEAD withheld it only by the old RESTRICTION reason.
  **CLOSED BY WITHHOLDING** — see «The QM's judgement» below.
- `E3.3.15.1` · `E3.3.16.1` · `E3.3.11.2.8.3` — above, for the Captain
- *seen, pre-existing, not new ids*: a passive relative said active by the mouth — «A man that TOLD is
  happy» for «who was told» (`E3.3.11.2.20`); «A tired man sleeps and snores» — the conjunct gets no
  agent (`E3.3.11.2.25`); «Two tired men» said «Some 2 tired men» (the mouth, `count` beside ∃).

## The QM's judgement *(2026-09-27)* — accepted but for one blocker, and three records

**1. BLOCKER, fixed — `E3.3.14.3` closed by withholding.** The build claimed what HEAD had withheld by
accident: «The man who knew that she lied left.» → «…that she lay left is», «The student who said that
the exam was hard failed.» → «…that the exam failed hard is», and pre-existing on the same shape «A
student who studied passed.» → «A student that studied is.». **The rule, all tree shape (frame):** a
sentence whose root is a NOMINAL (NOUN · PROPN · PRON) with no `cop` and no subject under it, a clause of
its own restricting it (`acl`), and the sentence CLOSED — its last token the root's `punct` — has lost its
predicate: nothing is said OF the phrase, and what the clause holds is the parse's misattachment. The
sentence is withheld (`Compiler._predicate_lost`, E3.12.5 (1)). *The closing condition is what spares the
citation fragment UD's pages print, «the cat that sleeps» (pinned by three tests and a UD case); its cost:
the same misparse typed without a final mark is not caught.* Checked: «My cat is cute» (copula), the
drill's verbless zips (drill gate unchanged), subject and object gaps, attitude inside, definite ·
indefinite · every — only the lost-predicate sentences move, plus «A man who sleeps.», a closed fragment,
now withheld. Gates unchanged. Pinned: `test_a_SENTENCE_whose_root_is_a_noun_phrase_with_a_clause_has_lost_its_predicate`.

**2. RECORD — `E3.3.14.5` ⚑ WRONG CLAIM, proportional determiners read as adjectives under ∃**
(pre-existing). «Most tired men sleep» → ∃x most(x) ∧ tired(x) ∧ sleep(x), «Some most tired men sleep»;
«Few tired men sleep» claims some do; «Most / Many men who sleep are tired» now also said. The rows are
right (`most` · `many` · `few` · `much` · `little`: `kind: quantifier`, a proportional `force`), and
`E3.3.11.2.9.2` would withhold them — but stanza tags them `ADJ amod`, and `ClosedClasses.candidates`
refuses every row to a content-tagged token by the 09-22 ruling («a content word is not a function word
spelled the same»), so the row is never read and the adjective route binds them. **Not built: it needs a
decision on that guard** — admit a `quantificational` row under `ADJ` + `amod` (the label disagreement the
same method forgives for `ADP` against a particle), then the adverbs' ruling applies as it stands. For the
Captain; lean: yes, narrowly.

**3. RECORD — provider misreads (`E3.3.2.8`'s class).** `E3.3.14.6` stanza tags «bit» `Tense=Pres` in «The
dog that bit me sleeps» → said «bites», the tense lost. `E3.3.14.7` «Does a man who sleeps snore?» parses
«snore» as a noun → was said «Is a man that sleeps snore?», another question (withheld now, by the
`E3.3.14.3` rule: a closed sentence with a nominal root).
