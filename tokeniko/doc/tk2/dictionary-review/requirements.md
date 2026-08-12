# dictionary review — REQUIREMENTS

*What the geometry must respect. One line each. Evidence lives in the dated `_notes.md` beside this.*

1. **One space, no categories.** Verbs are not a separate object from nouns; «land on the bed» must reach «sleep» without passing through a verb-class partition.
2. **`eat` stays near `food`.** No precision gain may cost an existing correct nearness — precision by *addition*, never by splitting the space.
3. **The lexicon is fixed.** Words live in relation to each other; the KB never moves them.
4. **The movable geometry is derived** — the interpreted space of a zip, not the dictionary. What is learned is the *map* between the two.
5. **Consequence is learned, not looked up.** The dictionary supplies meaning; the KB supplies what follows.
6. **The compound is the atom of the derived space** — the filler selects which region of the verb is live, so the pair is not recoverable from either word alone.
7. **Identity carries no geometry.** «me» contributes whose state is located, never what it means.
8. **Sensitive verbs are in scope by construction** — verbs determine actions, so volitional and motion families are both mandatory in any subset.
9. **The base must split by POS.** A collapsed dimension merges two different relation sets.
10. **~~Density comes from relations, never co-occurrence.~~ REFUTED BY MEASUREMENT, 2026-08-12** — `eat` and `food` have NO WordNet relation, so relations-only scores them 0.000: this line and line 2 cannot both hold in one matrix. Awaiting the Captain's ruling (one blended matrix vs. two layers).
11. **The base is already explicit and hand-editable** — 2925 rows × 2925 columns, a full squared semantic matrix; the *dictionary* is not, because it is defined by reference to the base.
12. **The bar is set before the matrix is built**, and the subset must contain the pairs that must come out far apart («land on the runway» vs «land on the opposite»).
13. **Derived vectors are a cache in the zip**, recomputable — so cosine runs in the DB.
14. **The antonym SIGN must survive the density** — measured: one negative cell reads +0.519 under a dense co-occurrence fill and −0.186 under relations only; `utils_antonyms` depends on the sign.
15. **Membership is a defect too, not only values** — `want`, `swallow`, `chew`, `negation` are not base words, so `eat entails swallow` is inexpressible: the word LIST is under review, not just the matrix.
16. **The POS split is necessary and NOT sufficient** — `land.n`~`land.v` is 1.000 collapsed and still 0.410 split, re-merged by the `derivational` edge.
17. **Doubts are settled by measurement** (the Captain's ruling, 2026-08-12): code, drafts and tests are legitimate instruments for DEFINING requirements — not only for implementing them.
18. **Every cell states which relation produced it** — a matrix that cannot be interrogated cannot be curated by hand.
