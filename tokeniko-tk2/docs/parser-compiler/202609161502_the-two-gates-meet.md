# parser/compiler — THE TWO GATES MEET, AND WHAT THAT COST ON THE FIRST RUN, 2026-09-16 15:02

*Requirement 18, written yesterday afternoon after a wrong role sat in every copular sentence for a
day with no test going red. **The control found six disagreements on its first run, and crashed the
compiler before it got that far.***

**Six DISAGREED → four, and all four remaining are open questions the project has NAMED.**

---

## WHAT IT COMPARES, AND WHY NOT EQUALITY

The drill is the FORMAT's gate: 78 sentences hand-compiled with no parser, proving tkzip can hold the
world. The UD gate is the STATION's: it compiles strangers' sentences and never looks at the drill.
**Nothing compared what the station PRODUCES with what the Captain hand-COMPILED.**

Most of the drill needs features E3 has not built — attitudes, domains, most quantifier scoping — so
a zip-equality check would fail all 78 and teach nothing. What is asked instead is **agreement where
both speak**:

    AGREED      the station produced a row or a role and the drill has the same one
    DISAGREED   both name the same filler and give it DIFFERENT roles — the only failure that counts
    MISSING     the drill has it and the station does not. Expected, counted, never averaged in

**The matching is by CONTENT.** Rows pair on their predicate key — and, for copular rows which have
no predicate by req 31, on their complement's head. Boxes pair on their HEAD key. That is what makes
a disagreement mean something: `patient: sue.n` against `topic: sue.n` is one filler under two names,
which is precisely the defect the requirement was written for.

**A VARIABLE IS NEVER A CONFLICT.** The station and the drill number their variables independently,
so `x0` against `P` is a disagreement about nothing — and comparing them would make the gate cry wolf
on every quantified sentence, which is most of the drill.

## IT CRASHED THE COMPILER BEFORE IT COULD SCORE ANYTHING

**SIX OF THE CAPTAIN'S OWN SENTENCES STOPPED THE STATION DEAD**, and both causes are things UD's tidy
corpus cannot contain:

**1 — A TOKEN UD DOES NOT DEFINE.** His annotations («He thinks a cat is in the garden. **[de
dicto]**») leave trailing whitespace, which stanza tags **`SPACE`** — not one of UD's seventeen. Its
lemma normalises to nothing, `key_of` raised `InvalidKey`, and the compiler stopped. *A station that
stops is neither half-understood nor wrongly-understood: it produced no zip at all, which req 8 does
not even contemplate.* A token the station cannot read is now unplaced, and unplaced is a state the
format has.

**2 — TWO ROWS CALLED `m0`.** «In Italy, you MAY drive in France with a FOREIGN licence» raises a
modality prefix and an attributive-modifier row, and both were minted `m{len(...)}` from different
counters. The schema requires names unique within a zip and refused it. **No sentence in UD's corpus
carries both a modal and an attributive adjective**, so neither existing gate could have found it.
The prefixes are now gathered in one place with a comment saying why.

## THE SIX DISAGREEMENTS, AND WHAT THEY WERE

**TWO WERE CURATION ERRORS, AND THEY ARE ONE ERROR SEEN FROM BOTH ENDS** (`db/0015`):

**«I walk TOWARD the station» compiled a DIRECTION; the drill says DESTINATION.** The drill is
explicit across three rows — «to», «toward», «as far as» all fill one destination box and differ
only by marker — and dir-2's own note says why: *«the marker row is where "no arrival entailed"
lives»*. **Requirement 65 exists so that these share a box**, and typing `toward` as a direction put
the entailment in the ROLE, which is the one place req 65 says it must not be.

*The principle is sharper than the three witnesses.* Req 67 defines `direction` as **a direction with
NO ENDPOINT**. A marked phrase HAS one: **the nominal IS the endpoint.** So a `role_marker` can never
produce `direction` — the role exists for the case where there is no nominal to mark. Five rows
corrected on the principle, and the migration now REFUSES to apply if any marker offers `direction`
alone.

**«She turned LEFT» compiled a MANNER — and it is the sentence req 67 was written for.** `db/0013`'s
direction list held `backwards`, `sideways`, `upwards`… and not `left`, `right` or any compass point,
so the manner default answered. *The very words that forced the eighteenth role into the format were
missing from the table that routes them to it.*

**THE OTHER FOUR ARE OPEN QUESTIONS, NOT DEFECTS, AND THEY ARE NOW MEASURED:**

- **`exist-3` «God exists»** — the station says `agent`, the drill `patient`. Nobody acts in an
  existence claim.
- **`aw-11`, `aw-20` «the cat is hungry»** — the station says `patient`, the drill `experiencer`.
  A copular subject is a patient when a CATEGORY is predicated («Sue is a teacher») and an
  experiencer when a STATE is («the cat is hungry»).

  **These three are one question**, and it is the one `RELATION_FILLS_ROLE`'s own comment defers:
  *«`nsubj` is deliberately `agent` and not "agent or experiencer": which one it is depends on the
  VERB, that is a head-verb question the geometry answers, and a station that guessed here would be
  doing the compile core's job badly instead of leaving it open.»* **It now has three witnesses and a
  number instead of a prediction.**
- **`aw-19` «I ate with Anna»** — the named-individual hole, E3b, already on the record twice.

## AND A LESSON ABOUT CHECKS, PAID FOR IMMEDIATELY

`db/0015`'s first draft added rows to the adverb table and re-ran only ONE of that table's two laws.
It shipped a duplicate — `northwards` was already a v1 direction adverb — and the unique index
refused the write with a `BulkWriteError` that took **39 tests** down with it.

**A CHECK MUST TRAVEL WITH THE DATA IT GUARDS.** `db/0013` had the duplicate check; `db/0015` wrote
to the same table without it, which is exactly how an invariant that was written once stops holding.
Every migration that touches a table now re-runs that table's laws, and this one says so in its own
code.

## WHERE IT STANDS

    ROWS PAIRED    91 of 126 the drill hand-compiled
    ROLES AGREED   64 of 123 on the rows that paired
    SENTENCES      38 agreed · 4 DISAGREED · 36 reached no common ground
    MULTI-SENTENCE 5 were split by stanza and only the first half read — E3 task 2b, met from the
                   other side

**The four are a RATCHET, held by a test** (`@pytest.mark.skeleton`, the marker the few live-parsing
tests already use): a fifth disagreement is a new defect, and the count may only go down.

*And the 36 that reached no common ground are the honest measure of how much of the drill E3 has not
built. They are counted apart so they can never be averaged into something that looks like
agreement.*
