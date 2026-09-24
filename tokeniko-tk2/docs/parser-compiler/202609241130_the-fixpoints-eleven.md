# The fixpoint's eleven — read one by one, and they are not three causes

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
