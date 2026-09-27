# parser/compiler — THE ADVERBIAL QUANTIFIERS, 2026-09-27 14:00

*Roadmap: `E3.3.11.2.9` · `E3.3.11.2.9.1` … `E3.3.11.2.9.12`*

*1st Officier: measure and design first, build only what needs no new ruling. Found by the
attitude measurement (`202609261600_…`): «He never sleeps» compiled as «He sleeps» — the reverse, in
silence. Scratch `$CLAUDE_JOB_DIR/tmp/advq/`.*

## The cause, and what the format already holds

`_compile_closed` counted a quantifier word as placed and trusted a binder to be built — which only
happened for a nominal relation. An adverbial «never» was placed and vanished. **The format needed
nothing new**: a binder over a TIME or LOCATION variable is a `QuantifierRow` whose restriction is
`Open(sort=time|place)` — the shape «nobody» already uses — its variable in the content row's `time`
or `location` box. Four quantities exist: ∀ · ∃ · ¬∃ · ¬∀. Nothing for few / many / most.

## Built (not committed; `db/0043` written, NOT applied)

- **knowledge** — `db/0043` (closed classes v23): the 13 adverbial fused rows name the box their
  variable fills (`compiled.roles`), the repair `db/0014` made for «here» and «now»
- **the root cause** — a quantifier is counted placed only where its binder is built; one nobody
  binds stays unplaced, and an unplaced operator withholds its clause (`E3.12.5.2`). This applies to
  every quantifier, not only the adverbs
- `_bare_quantifier` takes fused quantifiers under any relation, the box from the row; it refuses a
  row whose force differs from its quantity or that carries a count, and a quantifier word modified by
  anything but «not» («almost never», «almost everyone» — withheld, where HEAD claimed ∀)
- scope read literally, in word order (`E3.12.5` (6), `E3.3.11.2.16` (1)); the decompiler says a
  quantified time mid-clause where the compiler reads its scope, and refuses an order it would not
  read back

| sentence | at HEAD | now |
|---|---|---|
| He never sleeps · He always / sometimes sleeps | «He sleeps» | ¬∃t · ∀t · ∃t, round-trips |
| He sleeps nowhere / everywhere / somewhere | «He sleeps» | the binder in the location box |
| He doesn't always sleep · He never doesn't sleep | «He does not sleep» (wrong) | ¬∀t · ¬∃t¬ |
| He was never late | «He was no late» | ¬∃t late |
| I think that he never sleeps | «I think that he sleeps» | ATT · ¬∃t |
| I never thought that he slept | claimed «I thought he slept» | withheld (ruling 2) |
| Never give up! · Everyone always sleeps · Does he never sleep? | «never» lost | right |
| He can / must / need never … | «He can sleep» (wrong) | withheld (`E3.3.11.2.9.5`) |
| He seldom / often sleeps · How often do you work? | «He sleeps» · «How do you work?» | withheld (`E3.3.11.2.9.2`) |
| Do you ever sleep? · Nobody ever sleeps | «ever» dropped | withheld (`E3.3.11.2.9.3`) |
| He sleeps once · I work twice a week | «I work a week» | withheld (`E3.3.11.2.9.4`) |

**Gates**: fixpoint 74 · 9 · 0 + W4 (63/69) → **72 · 9 · 0 + W6 (61/67)** · drill 63 · 4 · 20 →
**60 · 6 · 21** · UD 30 · 0 · 15, identical. Moves: `nha-1` «He never works», `nha-2` «A calculator
never thinks» now said right (FIXED at the fixpoint) but DISAGREED at the drill on SPELLING only
(`E3.3.11.2.9.1`) — **the drill-gate ratchet test is red**; `freq-1` «I work twice a week», `freq-4`
«How often do you work?» → WITHHELD (they were a wrong sentence and a different question). Gate:
spine 7 · station 596 · evidence 141 + the red · migrations 8. Self-verification on 58 unscripted
variants: three defects of the change found and fixed; none left.

## For the Captain — with ids

- `E3.3.11.2.9.1` **how «never» is spelled** *(built past, the ratchet red)* — the rows and the
  «nobody» precedent give ONE NEGATIVE binder over `Open(sort=time)`; tkzip reqs 32 / 72 and the drill's
  `nha-1`, `nha-2` spell ∀t (restricted to `time.n`) with a negation. The same claim, two spellings
- `E3.3.11.2.9.2` **proportions** — seldom · rarely · often · usually · «how often»: the format
  cannot hold them; «seldom»'s row says `negative`, which is wrong knowledge
- `E3.3.11.2.9.3` **«ever»** — its row says universal while its own `force` says existential
- `E3.3.11.2.9.4` **once · twice** — `freq-1` puts a count on the binder; «once» also means «formerly»
- `E3.3.11.2.9.5` **an adverbial binder after a modal auxiliary** — «can never», «must never»
- `E3.3.11.2.9.6` **frame or knowledge** — the decompiler's «a quantified TIME is said mid-clause» is
  keyed on `Role.TIME` in code
- `E3.3.11.2.9.7` **polarity at the mouth** — «Nobody sleeps anywhere» → «Nobody sleeps somewhere»;
  «He doesn't sleep anywhere» → «He sleeps not somewhere» (with the older «He eats not something»)
- `E3.3.11.2.9.12` **the ratchets** — fixpoint FIXED 74 → 72, read-whole 63/69 → 61/67, drill agreed
  63 → 60, all by honesty

## Found, with ids

- `E3.3.11.2.9.8` a time phrase narrowing the binder («never at night») is not composed — withheld
- `E3.3.11.2.9.9` «Sometimes everyone sleeps» — the zip right, the mouth cannot front the adverb
- `E3.3.11.2.9.10` a determiner with a modifier («almost all cats») — not checked
- `E3.3.11.2.9.11` «Nobody in the room sleeps» → «Nobody sleeps in the room» (pre-existing)

## RULED *(the Captain, 2026-09-27: «Agreed on all your leans. Go»)*

1. `E3.3.11.2.9.1` **«never» is ONE NEGATIVE binder over `Open(sort=time)`** — one spelling for nobody,
   nothing, nowhere, never; tkzip reqs 32 / 72 amended; the drill's `nha-1`, `nha-2` amended now
2. `E3.3.11.2.9.2` proportions withheld; later a fuzzy proportion on the binder, its values as rows;
   «seldom»'s row corrected now (it is not `negative`)
3. `E3.3.11.2.9.3` «ever» is ∃ with a polarity feature, as «any» has
4. `E3.3.11.2.9.4` the count built for «twice»; «once» withheld (two readings)
5. `E3.3.11.2.9.5` a negative adverbial binder after a modal follows the modal row's
   `following_negation` (`db/0036`): «can never» ¬◇ · «must never» □¬ · «need never» ¬□ · «may never»
   withheld; a positive one withheld until a row states it
6. `E3.3.11.2.9.6` the decompiler's mid-clause rule for a quantified time is FRAME (word order)
7. `E3.3.11.2.9.7` a polarity feature on the «any-» rows; the decompiler says the «any-» form under a
   negation or a negative binder
8. `E3.3.11.2.9.12` the ratchets re-based to the honest numbers

## The rulings built *(1st Officier, 2026-09-27)* — eight of eight, the gate green

`nha-1`, `nha-2` amended to one NEGATIVE binder (bar doc AMENDMENTS) · «seldom» no quantity (`force: few`);
«rarely», «usually» got rows in the adverb kinds (v6) — without them they fell to manner and CLAIMED
the event; a cut adverb-kinds operator now withholds its clause · «ever» ∃ with `polarity:
negative-context` («Nobody ever sleeps» round-trips) · «twice» a `count=2` on the binder; «once»
`ambiguous`, withheld; «I work twice a week» withheld (the week needs `E3.3.11.2.9.8`) · after a modal
by its `following_negation`: «can never» ¬∃t◇, «must never» □¬∃t, «need never» ¬∃t□, «may never»
withheld · the mid-clause rule marked FRAME · the «any-» rows and «ever» carry the polarity; the
decompiler says «He does not sleep anywhere», «Nobody saw anyone». `db/0043` = closed classes v23 +
adverb kinds v6, NOT applied.

**Gates**: fixpoint **72 · 9 · 0 + W6, 61/67** · drill **62 · 4 · 21**, prefix 33/85 → 35/83, the
disagreements back to the named four · UD 30 · 0 · 15 identical. Spine 7 · station 626 · evidence 142
green · migrations 8. The test ratchets did not move; **the exit's floors are re-based in `plan.md`**:
drill agreed ≥ 62 · fixpoint FIXED ≥ 72 · read-whole ≥ 61 of 67 · UD answered ≥ 30. Self-verification
on 28 unscripted variants: one defect caused («might never» refused by the mouth), fixed.

**Found, with ids:**
- `E3.3.11.2.9.13` «cannot ever», «must not ever», «needn't ever» — withheld (no rule orders ∃ against a
  negation in the modal's slot)
- `E3.3.11.2.9.14` **free-choice «any» read as ∃** — «He sleeps anywhere» → «He sleeps somewhere»
- `E3.3.11.2.9.15` «ever» in a question is said back «sometimes» (round-trips)
- `E3.3.11.2.9.16` other frequency adverbs («frequently», «occasionally», «generally») have no rows and
  fall to manner, CLAIMING the event — each enters on its own witness
- `E3.3.11.2.9.17` «He did not sleep twice» → «He slept not twice» — the scope right, the English odd
