# tkzip — REQUIREMENTS

*What the format must respect. One line each. Evidence lives in the dated `_notes.md` beside this.*

1. **Fixed size.** Comparability in O(1) by the DUAL READ — cosine + stated cell, both O(1) — is the thesis; variable size trades it for graph matching. *(Amended 2026-08-12: cosine alone cannot state opposition — antonyms sit CLOSE in the topical geometry; see dictionary req. 19 and the map.)*
2. **Every slot carries a BINDING STATE.** Unbound ≠ 0. Unknown is a variable, never a falsehood.
3. **One shape, three readings** — all bound = assertion · one unbound = question · unresolved = equation.
4. **Storable with variables still open.** An unfinished thought is a first-class memory.
5. **An equation asserted true is supposition** — scenario reasoning must not require believing.
6. **Scope rides inside** (who · in what context), so a contextual defeat is never relearned.
7. **No act type.** A zip is *consumed* by a hardwired category; only the dispatcher is semantic.
8. **Slots must cover what v1 dropped**: coordination · restriction («only») · modality · complement subordination.
9. **Verb senses are load-bearing** — a wrong verb sense is a wrong action, not a wrong word.
10. **Sense selection should be derived, not ordered.** No hardcoded ladder: the sense that keeps the KB consistent wins.
11. **A role stores the D-side geometry and consults R through its sense key** (ruling 2026-08-12): retrieval is topical cosine over cached vectors; stated relations — sign, entailment, cause — are read from R at evaluation via the sense the role already carries. The sense-bridge survives intact.
12. **The compound's point is a TRANSFORMED COMPOSITION, never a centroid** — the roles' D-vectors composed through the operators; negation and binding MOVE the point («land on the runway» ≠ «land on the opposite»).
13. **The derived layer is the figurative sphere** — analogy, metaphor, rhetoric: a separate, context-shaped, deliberately DYNAMIC layer above the fixed base.
14. **A micro-nn shapes the figurative layer** — experience and jargon keep it moving; it PROPOSES the reading, the evaluator admits it (the instinct fence holds here too).
15. **Stable figures CRYSTALLIZE into KB rows** — a dead metaphor becomes vocabulary; instinct is the dynamic front, settled figures become inspectable knowledge.
16. **Derived points are stored EPOCH-STAMPED beside the zip** — cosine finds over the stored index, the found few are recomputed at use; the sleep phase re-derives stale points lazily, never a full recompute.
17. **The dual read recurs at the compound floor** — derived-cosine plays D, KB rows play R: geometry proposes, stated knowledge gates — one law at both floors.

---

*Added 2026-09-11 at E2 task 1 — the role inventory. Evidence: `202609111051_notes.md`; the
Captain's own first draft: `origin-the-excel-draft.md`.*

18. **The role inventory is FRAME** — fixed in code, exhaustive at freeze. Language *structure* is stable where *vocabulary* is not; a forgotten slot is a bug to be found by the instruments and fixed by redesigning the frame, **never a migration**.
19. **Roles are NAMED and verb-independent** — box N means the same thing in every zip. PropBank's numbered args (`ARG2` = recipient for *give*, substance for *fill*) break comparability and are unusable. *Settles OQ2: passive normalizes to deep roles.*
20. **The slot is frame, the marker words are KB rows** — `destination` is the shape; *to · toward · into · onto* are `language_closed_classes` rows and grow.
21. **No catch-all slot, ever** — a typed `other` is the db option by the back door. Unplaced material is a **diagnostic outside the geometry**, never compared, read only by the debug tooling.
22. **Every zip carries the SCHEMA VERSION it was compiled against** — E9's translation night must know what it is translating.
23. **Adverbs split four ways by scope** — manner → a box · epistemic/evaluative → clause properties · circumstantial → a box or the quantifier · discourse → between-row operators. *(never · hardly · almost are structure, not description.)*
24. **Manner is a box; the ROTATION lives in the derived layer** — the zip stores the parts, the derived point composes them (reqs 12, 16), and the sign that separates antonymous manners comes from **R**, since D reads *relentless ≈ lazy* (antonyms sit close: love/hate 0.86). The transform is **bounded**, so a shared verb keeps two sentences comparable.
25. **The theatre is DERIVED** — spacetime is a numeric projection of the fillers, never a replacement for them: *Genoa is a city you can reason about, not a coordinate.*
26. **Every nominal box is a RECORD of five fields** — `quantity` (universal · negated_universal · existential · negative) · `count` (the number, or none) · `determination` (definite · indefinite · generic) · `relation` (the possessor) · `noun`. The record is **per noun phrase**, not one per clause read off the subject (v1's limit; «all cats eat some fish» needs two), and quantity is split from determination because they are orthogonal: «**the three** cats» is definite AND counted, «**not all the** cats» is negated_universal AND definite — v1's single seven-valued field can say only one at a time. `count` is also where «twice a week» puts its number (req 32). *OQ7 answered.*
27. **Topicality survives as one non-geometric marker** — roles normalize so they compare, and the zip still records that the speaker foregrounded the patient, so the renderer speaks it back in the voice it was heard (req 9).
28. **Purpose and cause are OPERATORS BETWEEN ROWS, never boxes** — one encoding per meaning, so «for money» and «to save money» are the same zip. *OQ3 answered; the IMPLY form stays withdrawn as unsound.*
29. **Secondary predication is a SECOND ROW** — depictive co-asserted (`AND`), resultative joined by `IMPLY` with the theatre giving the order. *OQ5 answered. **Rewritten the same day at task 2**: the first form named an explicit `RESULT` operator; `RESULT` dissolved with `CAUSE` (req 37). OQ5's condition — an explicit link, since temporal succession is not causation — is met better, because implication is the link and bare succession still derives nothing.*
30. **Cause-as-participant merges into `agent`** — «the storm broke the window»: volition is readable from the filler, and a separate box would restate what the filler already says.
31. **Plain copular `be` compiles to structure** and never fills the predicate; the `complement` box holds the property, so `become` / `seem` / `remain` keep a home and «the cat is cute» is still *cat + cute, no verb*. *(Existential `be` is content.)*
32. **Frequency is QUANTIFICATION over the time variable**, not a box — *always* universal, *never* negation + universal, *twice a week* a count.

**THE INVENTORY (closed 2026-09-11) — seventeen boxes plus the predicate.**
*Participants:* `agent` · `patient` · `experiencer` · `recipient` · `beneficiary` · `instrument` · `source` · `destination` · `complement` · `topic` · `measure`
*Circumstances:* `location` · `time` · `manner` · `duration` · `path` · `comitative`

*Added 2026-09-11 at E2 task 2 — named rows, operators and scope. Evidence: `202609111511_notes.md`.*

33. **A zip is a FLAT LIST of rows; nesting is naming** — the Tseitin convention. Arbitrary depth, constant shape. *OQ8 answered.*
34. **A box may hold a ROW NAME**, and its vector is that row's **derived point** (reqs 12, 16) — so embedded thoughts compare as thoughts, while the rows survive for the binding machinery.
35. **ROW ORDER = SCOPE ORDER**, and the prefix carries **five** scope-bearing elements: `quantifier · negation · modality · attitude · domain`. That set is FRAME and must stay exhaustive. Row order is therefore **not free** — it can never be used to encode anything else. *OQ6 answered.*
36. **Quantification uses BINDER ROWS** — a box holds a variable, a row binds it. One binding mechanism for quantification, questions, equations and naming (req 2 · evaluator req 5), at the cost of an indirection on every quantified comparison.
37. **There is no CAUSE relation** — a cause is `IMPLY` read with the theatre's arrow of time. Premise, stated so it is not assumed silently: *in a deterministic world, a cause is what implies its effect.* A bonus falls out: when implication direction and time direction **disagree**, the «because» is evidential, not causal.
38. **Assertion status distinguishes «because» from «if»** — same `IMPLY`, rows asserted or not. Binding state (req 2) therefore carries truth-conditional weight and is not bookkeeping.
39. **«only» converts `IMPLY` into `EQ`**, uniformly across the family (*if/iff · because/only because · causes/only causes*). It is a marker, not an operator; the marker words are `language_closed_classes` rows. *Same seam as the role markers.*
40. **Purpose is POV(want) + `IMPLY`** — the intended outcome sits inside the attitude and is never asserted. *OQ3 answered; nothing survives as a purpose box or a purpose relation.*
41. **The operator set is the TEN non-degenerate binary truth functions** — `AND · NAND · OR · NOR · XOR · EQ · IMPLY · NIMPLY · CONV · NCONV` — frame, closed by mathematics, **never trimmed to what English marks**. Trimming would restrict what tokeniko can THINK to what English can SAY. The six English marks are KB rows.
42. **`CONV` is not `IMPLY` with the rows swapped** — row order carries scope (req 35), so it cannot also carry direction.
43. **Truth is cheap for all ten; COMPOSITION is not** — folding two derived points has a natural reading for `AND`/`OR`/`NOT` and none obvious for `XOR`/`NAND`. Declare all ten, implement all ten in truth, and let the derived layer **abstain visibly** where it cannot define the composition.
44. **Normalization is a comparison-time step, not a trim** — `A NIMPLY B` and `A AND ¬B` compare as one thought and still render as «regardless» and «and not».
45. **The attitude takes a prefix position** — de re / de dicto must be expressible. A flat-only POV does not abstain, it **silently forces de re** and would assert existence the speaker never claimed («he thinks a unicorn is in the garden»). The flat POV field survives as shorthand for one fixed prefix position.
46. **`domain` is the fifth prefix element** — «legally» · «in chess» · «as a doctor» · «in Italy» (a jurisdiction, provably not the `location` box: «in Italy you may drive in France…»). No type column — nothing reasons differently across kinds. **Requirement 6 needs no new machinery**, and «as a doctor I disagree; as a father I understand» stops being a KB contradiction.
