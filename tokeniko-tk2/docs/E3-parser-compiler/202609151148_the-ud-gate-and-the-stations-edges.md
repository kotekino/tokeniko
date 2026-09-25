# parser/compiler — THE UD GATE, AND WHERE THE STATION ENDS, 2026-09-15 11:48

*Roadmap: `E3` scope · `E3.5.1`*

*E3's opening session. Three rulings by the Captain, each of which moves something the conception
notes of 2026-08-23 had left in a weaker shape. Requirements 2 and 3 are amended by this note.*

---

## 1. THE STATION'S SCOPE, stated so it can be defended

> *«Take natural language, pass through spacy and stanza, collapse in tkzip using dictionary. This
> is the scope.»* — the Captain

**IN:** surface → skeleton (tokens, POS, dependencies) → **tkzip**. Mechanical. Roles filled,
structure compiled, the zip emitted with its confidence scalar.

**OUT:** what the zip MEANS. *«How tokeniko will interpret the result of the parser into a zip is
definitely a matter of evaluator and the mind.»* That is not a new boundary — it is evaluator req 5
already written down: **«One algorithm, no WSD stage — sense slots, wh-gaps and unbound roles are
the same problem: try bindings, keep the one whose grounding survives the KB.»**

**THE PRECISION THAT KEEPS «using dictionary» FROM MEANING TWO THINGS** *(the QM's caveat, accepted
by the Captain in the same breath as the scope)*: the station consults the dictionary for **SHAPE,
never for MEANING**.

- **Shape — yes.** The content lists that must not be ported as written (`_SUBJECT_CONTROL_VERBS`,
  `_IMPLICATION_VERBS`, `_COMPARISON_AFFIRMATIVE`, `_ROOM_WORDS`) become **geometry with a
  nearest-anchor fallback** — «is this verb an implication verb?» is answered by the base, not by a
  list. That is the standing law's third category and it is the station's legitimate use of R.
- **Meaning — no.** The station emits the lemma with **the sense slot OPEN**, an unbound variable
  like any other. It never picks a sense. A station that resolved senses would be doing the
  evaluator's one algorithm, worse and earlier, with no KB to check itself against.

---

## 2. THE GATE IS UNIVERSAL DEPENDENCIES — not our own sentences

> *«We should go much further than that: take all the examples from `universaldependencies.org/u/dep/`
> and `/u/pos/` and make our combo work good and consistently.»* — the Captain

**UD APPEARS NOWHERE IN THE tk2 DOCS BEFORE THIS NOTE.** What it publishes:

- **37 main dependency relations** (+30 documented subtypes, 67 with a global page), each carrying
  its own examples;
- **17 universal POS tags** — 6 open class, 8 closed, 3 other.

**WHY THIS IS THE RIGHT GATE, and not merely a bigger one.**

1. **It is a CLOSED, EXTERNAL, PUBLISHED enumeration.** The 37 relations are the frame the station
   maps FROM; tkzip's 18 roles, 10 operators and five-element prefix are what it maps TO. **That
   mapping table is E3's real deliverable** — and it can be complete, because both ends are closed.
2. **`case` is the empty field we already found.** `language_closed_classes` holds 135 prepositions
   all typed `role_marker` and **not one says which of the 18 roles it marks**. UD's `case` relation
   and its examples are exactly the evidence that fills it — the question E2's drill parked when it
   left `direction`'s marker cluster here («does *toward* entail arrival?»).
3. **It is not our own habits.** Our fixtures encode how the Captain and the QM write. UD's examples
   are strangers' sentences — the only kind that finds what our own corpus structurally cannot.

---

## 3. SHIELD (1) IS DEAD, AND NOW FOR THE RIGHT REASON — requirement 2 amended

The conception notes wrote shield (1) — *disagreement between skeletons* — and immediately called it
weak: *«spaCy and stanza are not consistently comparable in tk1 — their POS/dep vocabularies
differ»*. **The QM proposed at this session that UD would REPAIR that shield**, since both tools can
emit UD, making two independent readers comparable at last. **The Captain refuted it, and the reason
is the part worth keeping:**

> *«We are using stanza through spacy, using spacy-stanza. And sometimes only spacy: that's the real
> point where the two tools are not comparable, because **stanza tries to be as much close to UD2
> standard while spacy is, let's say, more "creative"**. Sometimes I used it for convenience in tk1,
> even though the real parsing/compiling was done through stanza.»*

So the vocabularies do not differ arbitrarily — **one conforms to a standard and the other does
not**. Two readers where only one is trying to be correct is not a disagreement signal; it is one
reader plus noise. Standardising on UD cannot fix that, because spaCy's non-conformance is the whole
problem and UD is the thing it does not conform to.

**THE RULING:** *«Take stanza as close enough and check against UD2 standard and its examples.»*

- **stanza is THE skeleton provider** (requirement 2 already says so — this only says why, sharply).
  `spacy-stanza` may remain the API surface; **spaCy's own models are not a second opinion and are
  not a fallback.**
- **THE SECOND READER IS UD2 ITSELF.** Not another parser — the published standard and its examples.
  «Close enough» is not an assumption to carry: it is a MEASUREMENT E3 owes, relation by relation.
- Shields (2) and (3) are untouched and remain the real protection: the evaluator's incoherence
  flags parse-suspicion, and below the floor the brain asks by rendering the reading back.

---

## 4. THE JOURNEYS BELONG TO E9, NOT HERE — and that was the Captain's catch

The QM proposed the Captain's 583 stored `tkzipdebug` journeys as E3's derivation corpus, and built
`tools/journey_ledger.html` to choose from them. **The Captain refused the framing:**

> *«The journey may be helpful to improve the parser-compiler, but it's definitely NOT related to
> parser-compiler BL. Everything that belongs to tk2 memory (inherited from tk1 memory) should
> belong to a further point called "migration".»*

**That epic already exists: E9 — the translation night.** Its task 3 is *«the no-regression ratchet —
v1's corpora and test-feedback log replayed: everything v1 answered correctly, v2 must»*, and
`tkzipdebug` **is** v1's test-feedback log. So the journeys are named there rather than gaining an
epic of their own. *(The Captain, on being shown this: «ah right, my fault.»)*

**They may still help the parsing work — he said so explicitly — but as EVIDENCE, never as the
gate.** What the ledger measured, and what makes them worth keeping in view:

| | |
|---|---|
| journeys recorded | 583 |
| distinct sentences | 546 |
| clean (never spent on E2's drill) | **529** |
| **v1 read them WRONG** | **209 — 40%** |

By phenomenon, with v1's own failure rate — **the two worst are exactly what E3 owes**:

    role marker  184  54% wrong     negation      99  56% wrong
    subordinate  165  49%           coordination 151  50%
    quantified   135  47%           modal         41  54%

**«Role marker» failing 54% of the time in the live engine is the same 135 prepositions whose
`compiled` field is empty.** That is not a coincidence and it is the strongest single argument that
E3's task 0 is the right first task.

**17 sentences stay fenced** — they were spent on E2's drill, which is E3's acceptance gate, and
deriving from them would grade the station on what it learned from. Same rule as *a pair proposed
after seeing a result is not a bar pair*. The ledger shows them struck and excludes them from every
count.

*The instrument is `tools/journey_ledger.html` — local, read-only over `tokeniko_mem.tkzipdebug`,
grouped by phenomenon using our own 383 `language_closed_classes` rows as the classifier.*
