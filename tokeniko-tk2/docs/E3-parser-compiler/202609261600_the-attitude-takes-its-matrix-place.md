# parser/compiler — THE ATTITUDE TAKES ITS MATRIX'S PLACE, 2026-09-26 16:00

*Roadmap: `E3.3.11.1` · `E3.3.11.2` · `E3.3.11.2.1` … `E3.3.11.2.16`*

*A workflow (ultracode): two measurements in parallel — today's behaviour on 59 sentences with the
real stanza station, and the target read from the format, the rulings and the drill's own
hand-compiled shapes — then one design, then a skeptic who tried to break it. The BUILD was stopped
before it touched code: the design itself named decisions «for the Captain before the build».
Artifacts: `$CLAUDE_JOB_DIR/tmp/neg/` (journal results, baselines of the three gates per case).*

## What was measured

**59 sentences — negation × attitude × modal × quantifier × question × quotation × coordination.
Today: 53 WRONG CLAIMS, 1 silent loss, 3 quality, 2 correct.** The two items on the roadmap were two
faces of one defect family, and the family is most of the attitude space.

**ONE ROOT CAUSE.** An attitude is raised LATE and attached as one more prefix row on its
complement (`Compiler._attitude` appends it). It never takes the matrix clause's place in the scope
structure. So:
- it lands INNERMOST, and everything the complement said about itself — ¬, ◇ / □, ∀ / ∃ / ¬∃, a
  domain — stands OUTSIDE the attitude governing it: «I think that he does not sleep» → ¬Bel(p);
  «I think that he can sleep» → ◇Bel(p); «I think that some cat sleeps» asserts the cat exists
- the matrix row survives beside it with its own operators and its place in joins: «I do not think
  that he sleeps» claims ¬think(me) AND «I think that he sleeps»

`_imperative` appends its want the same way («Don't touch it!» → ¬WANT). `_scope` cannot repair
either: it runs before any attitude exists.

## The families, with ids

- `E3.3.11.2.1` **the attitude lands INNERMOST** — every prefix element the complement raised stands
  outside it; de re is forced. `E3.3.11.1` is its negation case; «I hope that he does not come»,
  «I know that he does not sleep», «He said "I am not late"», «I think that he must not sleep»,
  «I think that nobody sleeps», «I think that every cat sleeps» (against the drill's `dere-1`)
- `E3.3.11.2.2` **the matrix row survives beside the attitude** — `E3.3.11.2`'s shape: «He does not
  believe that I lie», «She didn't say that he left», «I do not hope that he comes», «I don't know
  whether he sleeps», `dere-4` «I don't know who ate the fish», «I cannot think that he sleeps», «I
  can think…», and the matrix's operators LOST: «He may not think that she sleeps» → «He thinks
  that she sleeps»; «I can't say» → «I say»; «I no longer think»; «I would think»
- `E3.3.11.2.3` **nested attitudes** — the inner one stands at top level: «Anna thinks that Bob
  believes that he sleeps» claims Bob believes it (`aw-11`); `q-9` «Marie said "John told me 'you
  are late'"» claims John told her
- `E3.3.11.2.4` **an attitude escapes a supposition or a «because»** — «If Anna thinks that he
  sleeps, I leave» claims Anna thinks it
- `E3.3.11.2.5` **a coordinated complement escapes its attitude** — «I think that he sleeps and she
  eats» claims she eats; «I think that an old man sleeps» asserts the man
- `E3.3.11.2.6` **an ASKED attitude stored as a statement** — «Do you think that he sleeps?»,
  «Don't you think that he sleeps?», «Did you say that he does not sleep?»
- `E3.3.11.2.7` **the imperative's want lands innermost** — «Don't touch it!» → ¬WANT(touch); «He
  said: "Don't close the door!"»
- `E3.3.11.2.8` **«It is not true that he sleeps»** — the adjective becomes an attitude verb held by
  the expletive
- `E3.3.11.2.9` **⚑ the ADVERBIAL QUANTIFIERS compile to nothing** — «He never sleeps» → «He
  sleeps», «seldom», «nowhere»: the REVERSE, in silence; «always», «sometimes»: silent losses. Not
  an attitude defect — found here, and the most severe side finding (compile.py `_compile_closed`
  returns `taken` while no binder is built)
- `E3.3.11.2.10` **a passive attitude confuses holder and addressee** — «He was not told that she
  sleeps» says HE did not tell
- `E3.3.11.2.11` **a second participant left on the dissolved matrix** — «He did not persuade Anna
  that she sleeps» loses Anna; «I tried to tell him that…», «He wants me to go» keep boxes that say
  something false
- `E3.3.11.2.12` **the double claim across a sentence boundary** — «John did not say to Marie.
  "You are late."» (stanza splits it), and «Did John say to Marie: "You are late"?»
- `E3.3.11.2.13` **the mouth: «whether» is never said** — an open complement comes back with
  «that», and under «know» that is a factive wrong claim («I know whether he sleeps» → «I know that
  he sleeps»)
- `E3.3.11.2.14` **a pronoun under a quantified holder** — «Nobody thinks that he sleeps»: «he»
  bound or free
- `E3.3.11.2.15` **the elided complement** — «I think that he sleeps and she does not» (three
  readings); and the proforms «I think so», «I don't think so», «I hope not»: ¬hope(me), «so»
  dropped

## The design — «the attitude takes its matrix clause's place»

The format's own law, recursively (tkzip reqs 35 / 68; the drill's `dere-4`, `aw-11`, `q-9`): the
stack on the innermost place is **[what stood over the matrix] · ATTITUDE · [what the complement
raised itself]** · the next attitude …; no matrix content row is left; a join that named the matrix
names the complement's place. Two views of one prefix: RAW (each row scopes the clause that raised
it — what the withholding loop keeps reading) and SEATED (derived once, for assembly). A matrix
hands over its place only if its boxes are the holder's and the addressee's, the speaker claims or
wants it, it is not a restriction, and its operators go to one complement; otherwise the attitude
stands beside a kept matrix — only where that is entailed — or the complement is withheld. The
attitude stands or falls with its matrix. The imperative's want is inserted outermost. The
decompiler says each segment of the stack on its own verb. No kind list: ¬ ◇ □ ∀ ∃ ¬∃, domain, the
want and outer attitudes all obey one rule.

## The skeptic — SOUND WITH AMENDMENTS, four of them blocking

- **seat on the complement's PLACE, not its row** — seated on the row, the matrix's ¬ would land
  under the complement's own ∃, «because», «if» (and the conj / adjective escapes stay open)
- **guard the rename** — «I think, therefore I am» would make a join name itself; bound the walk
- **the dissolution rule literal and voice-aware** — a passive («He was not told») and a second
  participant («persuade Anna») must keep the matrix
- **a kept matrix beside its attitude needs VERIDICAL boxes** — «I almost said», «I nearly
  thought», «I hardly think» deny what a copied attitude would claim
- and: a fronted wh-word through an attitude («What do you think he ate?») is correct today and
  must stay so; carry the law across the sentence boundary without leaning on `SAYING_VERBS`; cut a
  link verb's own boxes with it; a cut inside a definite's restriction withholds

## `E3.3.11.2.16` — what the build needs from the Captain

*Leans are the QM's; the ruling is the Captain's.*

To build now:
1. **One scope rule for every prefix kind** — [matrix's prefix] · ATTITUDE · [complement's prefix];
   a complement's binder read LITERALLY de dicto (the words' own order, the drill's `dere-1`), as
   `E3.12.5` (6) read negation literally. *Lean: yes.*
2. **The format gaps, withheld meanwhile** — an ASKED attitude, a SUPPOSED one, and one with boxes
   of its own («I never thought», «he said quietly», «yesterday he said») have no place in an
   `AttitudeRow` (no truth slot, no boxes): withheld and recorded until the format is ruled, with
   `E2.3.1`. *Lean: yes.*
3. **A negation inside an attitude is a `NegationRow`**, not truth 0.0 (tkzip req 71, the drill):
   one spelling, the only one that also works under a want; req 71 amended, the drill at E1e.
   *Lean: yes.*
4. **The drill follows**: `aw-20` (and any case encoding the old scope) amended in the build.
   *Lean: yes.*
5. **«whether» gets its voice** — a `spoken` flag by migration, so an open complement is not said
   as a factive «that» (`E3.3.11.2.13`). *Lean: yes, in this build.*

Can wait — the interim is literal, or withheld:
6. **Factivity** («know» presupposes its complement, even under ¬): the zip holds «know»; the
   presupposition is derived by the evaluator from per-verb knowledge and logic, never claimed by
   the station. *Lean: yes; not built now.*
7. **The truth of a desired content** («I hope that…», «I want…»): EMPTY, by the 09-17 ruling («he
   WANTS → None»); the drill's `dere-3`, `t-mo-4` amended at E1e. *Lean: yes.*
8. **A pronoun under a quantified holder** (`E3.3.11.2.14`): withhold the bound/free ambiguity, the
   `E3.12.5` (5) precedent. *Lean: yes.*
9. **The elided complement** (`E3.3.11.2.15`): withhold the elided conjunct; the proforms («so»,
   «not» after a verb) become a knowledge feature on their rows. *Lean: yes; the proforms later.*
10. **«It is (not) true that…»** (`E3.3.11.2.8`): clause adjectives collapse into the prefix by
    knowledge rows (true → nothing, false → ¬, possible → ◇), the adverb kinds' epistemic shape;
    withheld meanwhile. *Lean: yes; later.*

**RULED** *(the Captain, 2026-09-26: «accepted all your leans, proceed»)* — all ten as leaned. The
build resumes from the design with the skeptic's amendments and these rulings.

## Built, verified twice, and a third fix running *(2026-09-26 → 27)*

**The build** (1st Officier; the skeptic's blocking amendments taken): RAW for withholding, SEATED
for assembly (`_seat`); a matrix hands over its place only if its boxes are the holder's and the
addressee's, it is claimed or wanted by the speech act, it is not a restriction, its operators go to
one complement, its complement joins nothing outside, and ruling 8 allows; otherwise the complement
is withheld and the matrix judged alone (ruling 2: no attitude beside a kept matrix). The imperative's
want goes outermost. The decompiler cuts the stack at the attitudes and says each level on its own
verb; «whether» is voiced (`db/0041`, written, NOT applied). The same law crosses a sentence
boundary. **Verification round 1**: 16 defects, 13 fixed by a fix round, 2 stopped for the Captain,
1 a report correction. **Round 2**: the build holds; three defects of the change remain — a tag
question the fix round let through when stanza tags «did» as a VERB, a divergent copy of the rule in
`utterance.py`, and the speech act read off `strength` (knowledge) — plus a stale docstring: **a
third fix round is running**.

**Numbers** (HEAD → now): fixpoint 74 · 9 · 0 + WITHHELD 4, 63/69 — unchanged · drill 63 · 4 · 20 —
unchanged, prefix pairs 29/84 → **33/85** (`dere-4`'s ¬, `aw-11`'s thinking, `q-9`'s saying,
`aw-20`'s want now paired) · UD 32 · 0 · 13 → **30 · 0 · 15**, WRONG 0: «if you know who did it, tell
me» (a supposed attitude) and «That he lied surprised me» (a clausal subject holds nothing) now
withheld. Gate: spine 7 · station 537 · evidence 142 · `test_migrations` green (3 known transients).

**Found by the verifiers, pre-existing — with ids:**
- `E3.3.11.2.1.1` «They believe that the man who left was not happy» — the ¬ above the definite,
  against the words' order
- `E3.3.11.2.5.1` a RELATIVE clause inside a complement escapes the attitude — «I think that a man
  who sleeps is tired» claims a man sleeps
- `E3.3.11.2.6.1` «Which man thinks that he sleeps?» — stored as a statement · `E3.3.11.2.6.2`
  «Where do you think he sleeps?» — kept as «where do you think», a different question
- `E3.3.11.2.8.1` «It is true that he sleeps» — the expletive left as a free pronoun, claimed ·
  `E3.3.11.2.8.2` **«I am sure / afraid / aware that…»** — read right at HEAD, now withheld: which
  adjectives hold their subject's attitude is knowledge, the same table as ruling 10's
- `E3.3.11.2.14.1` a pronoun under a quantified ADDRESSEE — «I told every student that he passed»
- `E3.3.11.2.15.1` an elided «does» tagged VERB escapes ruling 9's interim — «…but Bob does»
- `E3.3.11.2.17` the quoted «I» beyond the first level, or under a pronoun holder — «Anna said: "Bob
  thinks that I sleep."» → the speaker; «He said "I am not late"» → «who»
- `E3.3.11.2.18` «almost», «nearly», «hardly» fall to manner and CLAIM the event — «I almost said»
  → «I said»: a veridicality column on the adverb rows (knowledge)
- `E3.3.11.2.19` a cut under an intensional verb judged as a weakening — «He wants me to go» → «He
  wants me»
- `E3.3.11.2.20` the mouth — a passive with a pronoun subject said active («He was told» → «He
  told»); a clause inside and one outside an attitude joined with no boundary; «a old man»

## For the Captain — the build's own questions

1. **Re-base the ratchets** (the build lowered them, marked for his yes): compile ratchet 23 whole /
   93.1% (was 97.1%), frontier 9 / 74.8%, UD answered 30 — all by honest withholding.
2. **Ruling 8 extended to a QUESTIONED holder** («Who thinks that she sleeps?») — the builder's
   deviation: questions and quantifiers are one binding mechanism (req 36).
3. **And to a quantified ADDRESSEE** (`E3.3.11.2.14.1`).
4. **«I am sure that…»** (`E3.3.11.2.8.2`) — withheld until the clause-adjective table (ruling 10's).
5. **Ruling 9's interim cues** — UD's auxiliary-as-head for an elided clause, a «not» after a
   lexical verb — accepted as frame (reading the tree's shape) for the interim.
6. **Apply `db/0041`.**

## Round 3 *(2026-09-27)* — three of four fixed, one stopped, and the verifier refuted on variants

Fixed: the tag whose «did» stanza tags VERB (host withheld with its tag); the divergent copy in
`utterance.py` — the framing sentence is now compiled again with `quotation_withheld` so the
compiler's own rule decides, and a quotation whose frame was withheld goes with it («Anna did not
tell Bob. "You sleep."»); the `_places` docstring. Corpus identical, case for case; frame clean.
**Stopped, rightly**: the speech act's want over an attitude has no structural mark (defect 3).
**Refuted on variants**: a coordinated or conditional host still escapes its tag; and round 3 itself
made a new wrong claim.

**With ids:**
- `E3.3.11.2.21` **⚑ what a TAG QUESTION is — two documents disagree.** tkzip req 50 (the format):
  «It's cold, isn't it?» is OPEN with a high PRIOR. The 09-18 note (`202609180900_…`): «a claim
  followed by a request to confirm it» — resolved there by the QM as a consequence of the Captain's
  «the `?` decides» rule, and pinned by `test_a_TAG_question_claims_and_then_asks`. The do-tag path
  now follows req 50, the copula tag the note; variants (a coordinated or conditional host, «won't»
  / «can't» with no row, a positive VERB-«do» tag) fall between. For the Captain
- `E3.3.11.2.22` **⚑ WRONG CLAIM, caused by round 3 — nested frames across sentences.** «Anna said
  to Bob. "John said to Marie yesterday." "You sleep."» → «Anna said to Bob that John said yesterday
  to Marie», where the same content in one sentence gives «Anna said.»
- `E3.3.11.2.23` over-withholding, caused by round 3 — any withheld saying row is read as a quote
  frame, so «Nobody said to Marie that he sleeps. It rains.» loses «It rains» (`SAYING_VERBS`
  gains a reader — on `E3.8.3`'s list)
- `E3.3.11.2.24` **the speech act's want over an attitude has no structural mark** — «Suppose the
  cat is hungry!» and «I want that you suppose that the cat is hungry» differ only in `strength`
  (knowledge) and an accidental `theatre`. For the Captain
- `E3.3.11.2.25` a conjunct gets no agent — «John said to Marie and left» → «…and it left»
  (pre-existing)
- and two comments that claim more than the code (`_elision`, `compile`'s docstring)

## For the Captain — two more

7. **A tag question (`E3.3.11.2.21`)**: req 50 — the host OPEN with a high prior, the prior's value
   knowledge with a counted default (as `strength`, req 23) — or the 09-18 reading, claimed and then
   asked. *QM's lean: req 50.* A claim and a question about that same claim contradict each other;
   the prior holds exactly what the speaker does — expects, and asks. One rule then covers every
   host, coordinated or conditional, and every tag.
8. **The speech act's mark (`E3.3.11.2.24`)**: req 23 already gives the bare imperative's `strength`
   a counted DEFAULT, so every imperative's want carries one. *QM's lean:* make that an invariant the
   station asserts, and let the decompiler rely on it — no schema change; the truth slot on an
   `AttitudeRow` stays with `E2.3.1`.

**RULED** *(the Captain, 2026-09-27: «all your ruling, go»)* — all eight as leaned: the ratchets
re-based (23 / 93.1% · 9 / 74.8% · UD 30) · ruling 8 covers a questioned holder and a quantified
addressee · «I am sure that…» withheld until the clause-adjective table · ruling 9's interim cues are
frame · `db/0041` APPLIED · **a tag question is req 50's: the host OPEN with a high prior, the prior
knowledge with a counted default** (the 09-18 note's «claim then ask» superseded) · every
imperative's want carries a `strength` (req 23's counted default), an invariant the station asserts.

## Round 4 — the last *(1st Officier, 2026-09-27)* — six of six, the corpus unchanged case for case

- `E3.3.11.2.21` **a tag question is req 50's**: found by the tree's shape (a `parataxis` clause
  headed by an auxiliary, only a pronoun subject, its negation, punctuation); the host's claim opens
  by the same rule the `?` uses, with the prior of the tag's SHAPE — a reversed tag 0.8 (`db/0042`,
  a new table `language_open_priors`, NOT applied; the value is the officer's curation, below the
  imperative's 0.9 because a tag asks for want of certainty); a constant tag has no row and is
  withheld. The host is withheld with its tag when the tree cannot say which clause is asked (a
  coordination), when the tag's pronoun disagrees, or its auxiliary is not the host's. A conditional
  host opens its IMPLY. «Close the door, will you?» keeps the want; the tag is recorded unplaced. The
  decompiler says «It is cold, is it not?». The 09-18 tests amended and renamed
- `E3.3.11.2.24` every imperative's want carries a `strength` — the station refuses a table without
  the bare imperative's row; the decompiler relies on it
- `E3.3.11.2.22` nested frames — quotations compile `quoted`, every position under an attitude: «Anna
  said to Bob. "John said to Marie yesterday." "You sleep."» → «Anna said to Bob.»
- `E3.3.11.2.23` a saying that took its own complement is no frame — «It rains» kept
- the two comments made current; the ratchets marked CONFIRMED

Gate: spine 7 · station 562 · evidence 142 · migrations (the relevant ones) 35. Tools identical to
round 3. Self-verification on 40 unscripted variants: 0 wrong claims, 0 silent losses caused.

**Found, with ids:**
- `E3.3.11.2.26` **⚑ a quoted sentence with no frame is claimed as the speaker's own** — «"You are
  late."» alone, or after a frame that took its own complement
- `E3.3.11.2.27` **⚑ the mouth says an asked conditional as a claim** — «Will you stay if it rains?»
  → «If it rains, you will stay.»
- `E3.3.11.2.28` «we» compiles to `me.n` — its number lost
- `E3.3.11.2.29` the perfect aspect lost — «You have eaten» → «You eat»
- `E3.3.11.2.30` stanza's «wo» / «ca» (from «won't», «can't») have no rows — «She won't come» withheld
- `E3.3.11.2.31` over an attitude, the speech act's only mark is `strength` — a future strength row
  for «would like» over an attitude would read as a command (latent)
