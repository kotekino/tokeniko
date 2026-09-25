# The fixpoint's eleven — read one by one, and they are not three causes

*Roadmap: `E3.3.2` and its tree — and the ids below replace the labels this note was written with.*

> **THE LABELS IN THIS NOTE ARE HISTORY** *(renumbered 2026-09-25 under the nested-id rule)*:
>
> | written as | id | | written as | id |
> |---|---|---|---|---|
> | G1 purpose | `E3.3.2.1` | | G6 names | `E3.3.2.6` → **`E3b.6.1`** |
> | G2 the tree | `E3.3.2.2` | | G7 the understood «to» | `E3.3.2.7` |
> | G3 «of» | `E3.3.2.3` | | G8 provider misreads | `E3.3.2.8` *(open)* |
> | G4 relative clause unseen | `E3.3.2.4` | | G9 a supposed AND | `E3.3.2.9` |
> | G5 the gap overwrote | `E3.3.2.5` | | G10 «not necessarily» | `E3.3.2.10` |
> | `t-ws-1`'s bracketing | `E3.3.2.11` | | «and therefore» | `E3.3.2.2.1` |
> | modal scope | `E3.3.2.10.1` | | the zero relative | `E3.3.2.5.1` |
> | the fixpoint's scope blindness | `E3.3.11` *(open)* | | «I remember the day I slept» | `E3.3.12` *(open)* |
> | two bookkeeping defects | `E3.3.2.4.1` · `.4.2` *(open)* | | «So» lost in silence | `E3.3.2.10.2` *(open)* |
> | «so» claims backwards | `E3.3.2.1.1` *(open)* | | drill amendments | `E1e.6.1` |

*2026-09-24. The 1st Officier's reading of the 11 sentences the compiler reads WHOLE and the round
trip does not bring back (fixpoint 69 · 17 MOVED · 1 SILENT; of 73 read whole, 62 · 10 · 1). No code
changed. The QM's hypothesis was «three or four causes wearing eleven faces»: **refuted — ten
mechanisms in four families, and seven of the eleven have more than one.** Only four flip on a
single fix (`t-of-3`, `t-md-2`, `aw-17`, `q-1`).*

## The groups

| | mechanism | members | side · class | ruling? |
|---|---|---|---|---|
| **G1** | a controlled infinitive («go to SLEEP») is a subjectless row ANDed to its partner; the decompiler has no inverse — it says expletive «it», or promotes the patient to subject | `t-ws-1` `aw-6` (`t-ws-7` by misparse) | decompiler · **format**: control and purpose are not recorded, purpose-«to» collapses to AND | **yes** — is «go to sleep» go(me) ∧ sleep(∅)? is purpose-«to» AND? |
| **G2** | req 70's attributive fold join names a row the clause join also names — a DAG; the decompiler takes the second parent as a second sentence | `t-dc-3` `aw-6` | **compiler** — breaks its own 09-20 rule «a sentence is a tree» | no |
| **G3** | `_dress` says `possessor or determiner` and knows only `'s`: «the result of perception» → «perception's result», which loses `definite` | `t-dc-3` | decompiler; `of` is already knowledge (`db/0012`), read backwards | no |
| **G4** | a relative clause the decompiler does not see — (a) the fused-quantifier branch («something») returns before the restriction and the row vanishes **without entering `unsaid`**, a silently wider claim (req 8); (b) schema v8's quantity-less binder CLAIMS its relative row, and `_read` only recognises truth None | (a) `t-ws-8` · (b) `t-dc-4` | decompiler | no |
| **G5** | the relative GAP's role — `_share_variable` puts the antecedent in the first OPEN box, else AGENT: **«I like the fish that the cat ate» → `eat(agent=fish)`, the cat gone, `unplaced` empty** | `t-ws-8` `t-dc-4` — and blocks G4 | **compiler, FIRST leg — a truth error the fixpoint cannot see** | no |
| **G6** | keys are lowercase, so names come back «marie», «rome», and stanza reads «to marie» as an infinitive | `q-1` (sole cause) · `q-7` `aw-6` (partial) | **format — E3b**: nothing records that a head is a name | **yes** — schema or knowledge |
| **G7** | an addressee with `marker: None` is said with «to» («asked to anna»), which dissolves the attitude | `q-7` (and starred `q-2`) | decompiler over a format ambiguity: in the drill None means «not recorded», in a compiled zip «said bare» (req 65) | **yes** — what None means; a per-verb fact is knowledge |
| **G8** | correct English the provider misreads on the way back — no comma between two full clauses joined by «and» (`t-of-3`, identical to Z1 with the comma); the copular complement before the adverbs makes «married» a passive verb (`aw-17`) | `t-of-3` `aw-17` | provider on the second leg, triggered by our orthography and order (frame) | bench first — both move every «and» and every copula |
| **G9** | an AND inside a supposition keeps truth 1.0 while its halves are unasserted — keyed `asserts: neither`, no form. «If I go and you stay, I am happy» is SILENT (not in the corpus) | `t-ws-7` (also a first-leg misparse) | decompiler + compiler consistency · **format** | **yes** — the truth of a join inside a supposition |
| **G10** | negation outside a modality: «necessarily» IS knowledge (`db/0013`, necessity scope) but the decompiler reads only the closed-class `modality` rows | `t-md-2` | vocabulary — present, not read backwards, not flagged `spoken` | knowledge → a migration |

Plus one, `t-ws-1` only: the xcomp AND attaches to `_outermost` like no `conj` does, so «X because Y»
and «Because Y, X» compile to different bracketings — **compiler**.

**Families:** argument structure (G1 · G5) · zip shape (G2 · G9) · the decompiler's readers (G3 ·
G4 · G10) · surface form the provider misreads (G6 · G7 · G8).

**Entangled:** G4 cannot say an honest sentence until G5 is fixed, and fixing G5 changes the first
zip of `t-ws-8` and `t-dc-4` · G4a exposes the crash below · `aw-6` needs G1 + G2 + G6 · G8 moves
cases that are FIXED today.

## Found outside the brief

1. **A crash** — `decompile.py` reads `.described` on a `Var` when a relative gap sits in AGENT and
   the row has more than one box. «You learn from every mind that you trust.» Reproduced by the QM.
2. **The truth error** of G5 — reproduced by the QM: `r1 eat.v(agent=y2)`, truth 1.0, the cat absent,
   `unplaced: []`; decompiled «I like the fishes. The fishes ate.»
3. The compiler never produces an expletive («It rains» → agent pronoun), so the decompiler's
   expletive branch cannot round-trip anywhere.
4. Minor: relative-clause agreement («fishes that eats»); «every fish» took restriction number pl.

**`t-ng-4`**, which left the population on 09-24: its lost «some is not» is an ELLIPSIS the compiler
left open (noun and predicate both); the decompiler refuses the half correctly. G1's cousin, and
E3b's on the compiler side. «Some software is a mind and some software is not a mind.» is FIXED.

## G5 and the crash — fixed the same day *(1st Officier)*

**The loss was an OVERWRITE.** `_clause` placed `cat.n` in `eat.v`'s AGENT and marked it covered;
`_share_variable` then found no open box and its `for … else` wrote the fish's `Var` over AGENT. So
`unplaced` was empty because the cat HAD been covered — a filled box replaced in silence.

**The gap now takes the role its position gives it, by the machinery every argument uses:**
- an overt relative pronoun (found by its own row, `binds: antecedent`) — its dependency decides,
  through `_role_of` on the pronoun carrying the antecedent's lemma, so the marker selector reads
  «house», not «which»; the gap's box keeps its marker
- a zero relative with no subject — the gap IS the subject (`_subject_role`, `db/0018`)
- a zero relative with one stranded marker («the house I live in») — the same zip as «in which»
- **never an overwrite**: a gap whose role is filled, or cannot be told, WITHHOLDS the clause — its
  words go `unplaced`, the reason to `abstained`, and a `_withhold` pass removes the clause with
  everything that hangs on it (prefix, joins, rows using a variable whose binder went)

**The crash**: the passive «agent nobody described» branch now requires an `Open` head — a gap's
`Var` is a known argument, not an unknown one. And a MARKED gap no longer loses its marker: «every
mind that you learn FROM».

| | before | after |
|---|---|---|
| drill | 67 · 4 · 16 | 67 · 4 · 16 |
| fixpoint | 69 · 17 · 1 · of 73 whole 62 · 10 · 1 | 71 · 15 · 1 · **of 71 whole 62 · 8 · 1** |
| UD gate | 34 · 0 · 11 | identical |

**The FIXED 69 → 71 is not progress**: `t-ws-8` and `t-dc-4` are zero relatives with their subject
said, now withheld, so their shorter zips round-trip. The honest count is the read-whole one — the
eleven are now **nine**, and G4 has lost its two corpus members while remaining a real defect
(«I like the fish that the cat ate» still comes back as two sentences — G4b).

**Moved on purpose:** a subject relative's gap takes `db/0018`'s role like any subject — «All that
glitters» is now EXPERIENCER, as «Gold glitters» is (a test re-pointed); «the cat that sleeps» stays
AGENT. Old silent overwrites now correct or withheld: «in which I live» (was `agent=house`),
«whose», «where», «when», «the fish eaten by the cat».

**⚑ STOPPED — the zero relative with its subject said, for the Captain.** «the fish the cat ate»
and «the day I slept» are the same tree — subject, verb, no object — and the gap is the object in
one and an adverbial in the other. **Only the verb's VALENCY separates them, and the station holds
none.** «No object ⇒ object gap» needs no list but writes `sleep(agent=me, patient=day)`, a wrong
complete zip. Withheld until ruled. Candidate knowledge: WordNet's verb frames · the antecedent's
supersense (`noun.time`). Same question, unbuilt: infinitival relatives («a book to read») and
bare passive participles («the fish eaten»).

## G2 · G3 · G4 — fixed the same day *(1st Officier)*

- **G2 (compiler)** — the outermost fold join takes the owner row's place in every clause join that
  named it; the binders already scope it, so they move with it. **A ratchet**
  (`test_every_compiled_drill_zip_is_a_TREE`): no row is an operand of two joins over every compiled
  drill zip. It caught five on the old code (`t-ws-6` `t-dc-1` `t-dc-3` `t-dc-5` `aw-6`); one stays
  named, below
- **G3 (decompiler)** — a box carrying `relation` AND a determination says «the N of X»; the marker
  is READ FROM THE TABLE (rows whose selector yields `relation`, `db/0012` — today `{of}`). None or
  several → the clitic stays and the loss enters `unsaid`. A pronoun possessor never takes «of»
- **G4b (decompiler)** — a content row sharing the variable of exactly one binder that does not
  scope it, and named by no join, is that binder's relative clause WHATEVER its truth. Truth decides
  how: a quantity-less binder with a claimed row → a relative (it compiles back claimed); with an
  UNCLAIMED row → **refused**, because said as a relative it would come back a claim — *a truth
  error the old code had and nothing measured*; a quantifier's restriction claimed → said, and the
  lost claim recorded
- **G4a (decompiler)** — «something that you do not know» keeps its clause. **The invariant is
  structural**: the reading records which rows reached the text, rolled back when a render fails,
  and every consumed row that never did is named in `unsaid` — a loss cannot hide behind an
  unrelated mention

| | before | after |
|---|---|---|
| drill | 67 · 4 · 16 | byte-identical |
| fixpoint | 71 · 15 · 1 · of 71 whole 62 · 8 · 1 | **73 · 13 · 1 · of 71 whole 63 · 7 · 1** |
| UD gate | 34 · 0 · 11 | identical |

`t-dc-3` FIXED; `t-dc-1` FIXED (a `*` case); `aw-6` loses «The sea sees.» and waits on G1 + G6. The
witnesses — «The cat that sleeps is happy», «I like the fish that the cat ate», «…something that you
do not know…», «…only from minds that you trust» — all come back as said; none did before.

**Found, not fixed:**
1. **`t-dc-5`, a tree violation that wants a design ruling** — `_connect` (discourse adverbs:
   «also», «therefore») joins two rows the coordination already joined. Declining the second join
   loses «A and THEREFORE B»'s implication; keeping both names A twice. The ratchet's one named
   exception, and the list may only shrink
2. **every UNCLAIMED row reports a false loss** — `_clause` logs «held at None and a hedge is not
   built yet» because `None not in (CLAIMED, DENIED)`, so every conditional calls itself not whole
3. **an empty object phrase is dropped quietly** — the reason is recorded, the clause said without it

## G10 — «not necessarily», fixed the same day *(1st Officier)*

The prefix order is the scope order, and the 2×2 was benched before building:

| | necessity | possibility |
|---|---|---|
| **negation inside** (`mod · neg`) | «must not think» — unchanged | «can not think» — unchanged («may not» comes back «can not») |
| **negation outside** (`neg · mod`) | REFUSED → **«does not necessarily think»**, also on the copula and in a question | REFUSED, and stays so — «does not possibly» is not English, so no flag |

**The decompiler reads the adverb table backwards** when a negation sits outside a modality, after
the closed classes and never before them; the adverb rides with the negation, so every verb form
already built takes it. **`db/0035`** flags `necessarily` `spoken` — the word the corpus attests,
and unambiguous for ¬□. Keyed on MEANING (`Decompiler._key`), which the migration's `_meaning()`
equals on every row; position is word order and stays frame. One column added,
`AdverbKindDoc.spoken`, copying `ClosedClassDoc.spoken` — the model had nowhere to carry the flag.
Refused rather than half-said: ¬□¬ · a negated modality beside a second modality · an imperative.

| | before | after |
|---|---|---|
| drill | 67 · 4 · 16 | byte-identical |
| fixpoint | 73 · 13 · 1 · of 71 whole 63 · 7 · 1 | **74 · 13 · 0 · of 71 whole 64 · 7 · 0** |
| UD gate | 34 · 0 · 11 | identical |

**⚑ Found — two compiler errors about modal scope, reproduced by the QM:**
1. **the compiler ignores WORD ORDER for an adverb's scope** — «A calculator necessarily does not
   think» (□¬) compiles to `neg · mod`, ¬□: **a wrong claim with no warning**. Likewise «possibly
   does not» → ¬◇. Which side of «not» the adverb stands on is the tree's shape — frame
2. **where «not» scopes over an AUXILIARY is a fact about each word**, and the code assumes it is
   always inside: «must not» □¬, but «need not» ¬□, «cannot» ¬◇, «may not» ambiguous. «A calculator
   cannot think» compiles to a bare `think` with `cannot` unplaced — the opposite claim, recorded
   only as a word left over. **A per-word fact is knowledge**: rows, for the Captain to rule
3. **«So» with no row before it is lost in silence** — the join is never built and nothing enters
   `unplaced` or `abstained`; the loss G4 closed for relative clauses, in the compiler

## Modal scope — both compiler errors fixed, and a third found *(1st Officier, 09-24)*

**A — frame:** an adverb's scope is its surface order against «not» (`_scope` in `compile.py`; only
negation and modality rows move, anything between them keeps its slot). **B — knowledge
(`db/0036`, closed classes v19):** each modality row carries `features.following_negation` —
where a «not» after it scopes. In `features`, not `compiled`: `compiled` is the decompiler's MEANING
key, and «must» and «need» are one meaning (□) with one voice; how a form combines with a following
«not» is a property of the FORM. A row without the field WITHHOLDS its clause — no default in code.

| form | value | reason |
|---|---|---|
| can · could | outside | «cannot swim», «could not be true» — ¬◇; the ◇¬ reading needs contrastive stress, which text does not carry |
| may | **ambiguous** | permission «you may not smoke» ¬◇ · epistemic «it may not rain» ◇¬ — same words, same order |
| might | inside | «it might not rain» ◇¬; permission «might» is archaic |
| must · should · ought | inside | the obligation is NOT to — □¬ |
| need · dare | outside | «need not go» ¬□ · «dare not go» denies the daring |
| 'd | inside | «I'd not go» / «I'd not gone» both put «not» on the verb |
| **cannot** *(new row)* | inside | stanza keeps it ONE token (AUX); it compiles to ◇ + negation outside, `spoken` as ¬◇'s voice. A second «not» sits under it: «cannot not think» |

**The bench — seven wrong claims before, none after:** «need not» □¬ → ¬□ · «cannot» bare `think` →
¬◇ · **«can not» ◇¬ → ¬◇ (the third error)** · «could not» ◇¬ → ¬◇ · «necessarily does not» ¬□ → □¬
· «possibly does not» ¬◇ → ◇¬ · «may not» a coin toss → **the clause withheld**. Every sentence said
back re-compiles to the same prefix order. Withholding the whole clause is the only truthful answer
for «may not»: dropping the negation leaves ◇ (which permission denies), dropping the modal leaves ¬,
and leaving it unclaimed leaked — «If you may not go, I stay» became «If you go, I stay».

Voices: □¬ «must not» · ◇¬ «might not» · ¬◇ «cannot» · ¬□ stays «does not necessarily» (a split
auxiliary never voices an outside negation, so «need not» cannot take it over).

Drill, fixpoint and UD gate byte-identical but for the table's version line.

**The exclusion set moves by exactly `{cannot}`, and the move is INERT for D** — D's vocabulary is
the base's dimension words or WordNet's lemmas (`distribution.vocabulary_of`), and `cannot` is
neither; the migration's check refuses any other movement. `test_the_closed_classes_read_back_as_
the_exclusion_set` pinned the set to `db/0001`'s where its own docstring says «the forms it would
have read off the migration file» — the newest one.

**Found, not fixed:**
1. **⚑ THE FIXPOINT IS BLIND TO SCOPE** — `tools/roundtrip.canonical` sorts the rows, so □¬ and ¬□
   compare EQUAL. Every scope claim the fixpoint has ever passed is unverified by it; the `t-md-2`
   test and the new ones assert the prefix order separately. An INSTRUMENT defect
2. `policy_source.closed_forms(db)` reads the forms of EVERY version, so a form once added stays in
   the live exclusion set for ever, even after a later version removes it
3. «can't» → «ca» + «n't»; «ca» is not a row, so it compiles to a bare ¬ — weaker than the claim,
   and entailed by it; a «ca» row is NOT inert (WordNet has `ca`: calcium, California). «won't» likely
   the same
4. «could» loses its past — the compiler takes no theatre from a modal
5. `_withhold` leaves some words counted as placed («He thinks» when the attitude row is withheld)
6. an inverted fused question comes back archaic: «Cannot a calculator think?»

## The rulings — 2026-09-25 *(the Captain)*

**G1 — PURPOSE IS AN IMPLICATION, and the controlled subject is read off the complements.**

> *«I eat to prevent my death. But maybe I die even if I eat. The purpose is an implication, the
> implication can fail. […] this is my evaluation, which can be false or imprecise […] in the case of
> sleeping my purpose and the implication at time t-1 is true. Not at time t, because maybe there is
> a dog barking and I can't sleep.»*

The QM proposed an intention (`want`) instead, because a purpose can fail. Refused: **a zip holds
what the speaker CLAIMS, and a purpose is the speaker's claim that the act leads to the end** —
fallible like every claim, and the evaluator judges it. And the governing principle:

> *«We should NEVER make exceptions of the rule: semantics in a fixed grid (roles) glued with
> operators: this grants us computability, on the geometric level.»*

- **purpose = `imply(act, end)`**, the act at t-1 and the end at t; the act is claimed, the end is
  not (the speaker says he goes, not that he sleeps). Recognised by SHAPE: stanza gives purpose as
  `advcl` + «to» («go to sleep», «work to earn money», «go to bed to sleep») and a complement as
  `xcomp` («want to sleep», «told her to go») — no list
- **the controlled subject**: no complement → the matrix subject («I want to sleep», «I go to
  sleep»); a complement → that complement («I forced / persuaded / helped / expect HIM to…»,
  `obj`; «I told / asked HER to go», `iobj` — a bare `iobj` carries the understood «to» of G7).
  **«promise» is NOT an exception row, and not subject control either** *(the Captain, same day)*:
  «I promised her to go to the beach» means WE go — her and me — while «I promised her THAT I'd go»
  is only me. That subtlety is knowledge, **and better, a micro-nn applied to knowledge**: deferred
  to the micro-nns. Until then the rule applies uniformly and «promise» reads as «her»

**G6 → E3b** (names).

**G7 — the understood marker is STORED, and how it was said is kept.** tk1 did it before tk2
existed: a bare indirect object gets the marker «to» and records that it came from a bare `iobj`
(`lib/llc/parser.py:891`; its marker model defaults its origin to «implicit», `lib/core/tk.py:77`).
The meaning is «to Anna»; the bareness is the surface. The decompiler says it as it was said.

**G9 — an AND under a supposition is supposed, like its halves.** The Captain's reading — both
conditions must hold, evaluated as a boolean AND — is exactly the zip's; the defect was only the
AND row carrying `claimed` while its halves carried `supposed`.

**`t-dc-5` — a coordination plus a CAUSAL discourse adverb is the adverb's join, which REPLACES the
«and».** A class, not a word: the adverb table's `discourse` rows already carry the join. «A and
therefore B» claims A, B and A → B; the converse is not claimed, because two things true together is
not an equivalence. Benched on a handful of sentences before building.

**The zero relative — a bench** before any rule. Stanza marks the clause (`acl:relcl`) but not the
antecedent's role inside it; the basic UD it produces has no gap, the enhanced UD that would is not
produced. Candidates: WordNet's verb frames, the antecedent's supersense.

## The zero relative — the bench *(1st Officier, 09-25; `tools/relative_gap_bench.py`)*

113 hand-labelled zero relatives, each with its reason in English (64 object · 28 time · 7 place · 6
manner · 3 reason · 5 other), in seven groups — transitive, intransitive, **the same verb both ways**
(«the song I sang» / «the night I sang»), **time/place nouns as OBJECTS** («the place I love»),
minimal pairs, stranded-marker controls, embedded gaps. 107 reach the withheld shape. Two scores,
never averaged: *binary* (object vs any adverbial — where req 8 bites) and *role*.

| candidate | binary right / wrong / abstain | precision | coverage |
|---|---|---|---|
| primary-sense verb frames, strict | 62 / 13 / 32 | 82.7% | 70% |
| supersense of the antecedent, strict | 35 / 24 / 48 | 59.3% | 55% |
| **frames and supersense must AGREE** | **55 / 2 / 50** | **96.5%** | **53%** |
| any-sense frames | 69 / 38 / 0 | 64.5% | 100% — nearly every verb is transitive in SOME sense |
| stanza's `obl:tmod` on the antecedent | 9 / 2 / 96 | 81.8% | 10% — a misparse's guess |
| «no object ⇒ object gap» | 63 / 44 / 0 | 58.9% | 100% |
| withhold (today) | 0 / 0 / 107 | — | 0% |

**No single signal separates them.** Agreement is the only candidate near trust: its adverbial
answers 16 of 16, its object answers 32 right and 2 wrong — both the same blind spot: «time» is
`noun.event` in WordNet and «way» is `noun.attribute`; **WordNet has no class for manner at all**.
Where agreement abstains is exactly the hard half: the same-verb pairs (14 of 28) and time/place
nouns as objects (15 of 19) stay withheld. Stanza offers nothing more — no gap node in the
constituency tree, no enhanced UD.

**Found:** a PASSIVE relative («the day she was born», `nsubj:pass`) cannot have an object gap —
the object was promoted to subject. That is tree SHAPE, frame, and it removes the «born» errors
from every candidate · WordNet splits valency across senses (`cook.v.01` intransitive, `cook.v.02`
transitive), so any primary-sense rule inherits the resource's sense order · the supersense reader
takes WordNet's first class and does not abstain when it is of two minds.

**For the Captain:** agreement at 96.5% / 53% — or withhold as today. The two known wrongs are both
«the time/way …», which real traffic weights far more heavily than this set does.

**RULED (the Captain, 09-25) — agreement, plus two:**
1. the gap's role is written only when the verb frames and the antecedent's supersense AGREE; any
   disagreement withholds, as today
2. a PASSIVE relative never has an object gap — tree shape, frame
3. two curation rows for the blind spots, `time` → time and `way` → manner — knowledge (the
   `db/0019` `happy` precedent). **Cost stated: rows for exactly the bench's two wrongs is tuning on
   the test**, so ~20 FRESH sentences (time · way · moment · reason · place heads), written after the
   rows exist, are the held-out check — trusted only if they hold

The supersense reader keeps taking WordNet's first class here: abstaining on «two minds» would mute
nearly every time/place noun, and the agreement already guards the first-class guess.

## G1 · G7 · G9 · «and therefore» — built the same day *(1st Officier)*

- **G1** — `advcl` + «to» compiles to `imply(act, end)`: the act claimed, the end unclaimed, the join
  claimed; a row may name the clause relation it introduces (`features.introduces: advcl`) and wins
  there. The purpose join replaces its act in earlier joins like a `conj`, so «X because Y» and
  «Because Y, X» are one tree (`t-ws-1`'s bracketing). Controlled subject: no `obj`/`iobj` → the
  matrix subject; exactly one → it; both → abstain. **Time: the format cannot say «t-1 relative to
  its partner»** — the order lives only in IMPLY's operand order; nothing invented
- **`db/0037`** (closed classes v20): the purpose `to` row (`asserts: antecedent`, a fourth value —
  `matrix` would have made a purpose an attitude), and **two rows that were WRONG CLAIMS corrected**:
  «in order to» and «so that» both claimed the end, with the arrow reversed
- **G7 — schema v9**: one field, `Box.marker_implicit`. A bare `iobj` (an attitude's bare addressee
  too) stores the table's recipient marker and says it back bare. `q-7` now differs only by G6
- **G9** — a join whose outer clause is supposed is supposed; «If I go and you stay, I am happy»
  round-trips. Cost: «If you go to sleep, I stay» is refused (supposed, a purpose and an «if» leave
  the same zip)
- **«and therefore»** — benched on eight sentences, then built: an IMPLY adverb replaces the «and»,
  the same operator is absorbed, a different one abstains. **The tree ratchet's exception list is
  EMPTY** — every compiled drill zip is a tree

| | drill | fixpoint | of 71 whole | UD gate |
|---|---|---|---|---|
| before | 67 · 4 · 16 | 74 · 13 · 0 | 64 · 7 · 0 | 34 · 0 · 11 |
| after | 65 · **6** · 16 | **76 · 11 · 0** | **65 · 6 · 0** | identical |

**The two new DISAGREED are the drill disagreeing with a RULING** — `t-ws-1` hand-compiles «go to
sleep» as the idiom (no «go»), `aw-6` as the refused intention with the arrow reversed. **The
Captain, 09-25: tests follow decisions and never dictate them; both are amended at E1e** — «option
a, but amend the drill at e1e».

**And the costs the QM raised, refused as costs** *(the Captain)*: «To be honest, I left» — *with the
purpose of being honest*; «I woke up to find…» — *my purpose is to find*. Both are purpose, and the
reading is right. *(For the record, the QM's counterexample: «He woke up to find his house on fire».)*

**Found, not fixed:** «so» as a coordinator still claims its consequence with the arrow reversed,
as «in order to» did · «and so»: the adverb «so» matches the coordinator row and is lost in silence ·
«Because I think, I am» comes back think + ccomp (G8's family) · «I asked Anna where she lives»
(reported): Anna unplaced, the attitude lost · «Go to sleep!» — a purpose under an imperative is
refused.

## The zero relative — built *(1st Officier, 09-25)*

**The held-out check HOLDS: 23 fresh cases (time · moment · way · reason · place, 13 adverbial and
10 objects), written after the rows existed, nothing tuned after — 7 right, 0 wrong, 16 withheld.**
Without the rows, plain agreement made one wrong zip there («I love the way you think» →
`think(patient=way)`): the rows prevented a wrong zip in data they had never seen. On the original
107 the station as built answers **54 right, 0 wrong** (50.5% coverage).

- **`db/0038`** (UD readings v3) — one row, `acl:relcl`, answering a fifth question,
  `adverbial_gap`: `lemma time → time` · `lemma way → manner` · `noun.time → time` · `noun.location →
  location` · `noun.motive → reason` (heard, no box — so «the reason I asked» withholds instead of
  writing `ask(patient=reason)`). **No default rule: silence is the object half of the agreement.**
  Run by `MarkerSelector`, the runner that tells «at noon» from «at the door»
- the agreement is the benched one (permissive primary-sense frames — what the Captain ruled on);
  a PASSIVE lets the antecedent's kind decide alone; a clause whose verb has a `ccomp`/`xcomp` is
  withheld (tree shape — «the man I think you met» wrote the gap into `think`)
- the frame readers live in `tk2/dictionary/frames.py`; the bench imports them from there

Fixpoint read-whole **65 of 71 → 66 of 72** («If I tell you something that you do not know, you learn
it» re-enters, FIXED). Drill and UD gate identical.

**⚑ Found — and it is a wrong complete zip, reproduced by the QM.** «I remember the day I slept»
compiles `remember(experiencer=me, time=day)` + `sleep(agent=me, time=day)`, nothing unplaced. The
relative clause is now right; the MATRIX is stanza's `obl:tmod` misparse («remember» at a time,
instead of remembering the day). It was always misread — but the withheld clause used to leave the
zip partial, so it never claimed to be whole. Seven bench cases share it; no held-out case.

**Also found:** a stative subject («I have the tools you need» — `need` is `verb.stative`, so «you»
takes the patient) fills the box the object gap needs, and the clause is withheld · an agentless
passive is said as an active: «The day she was born» → «The day that she bore» (the decompiler, old)
· «I» lowercased inside a relative clause · the drill's «If I tell you something…» row has no
`know.v` (E1e) · `test_migrations` is DB-bound at ~40 minutes.
