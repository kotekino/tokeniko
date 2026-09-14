"""0003 — policy version 11: R and D are READ APART. The reader stops blending them.

**REQUIREMENT 10 SAID SO FROM THE FIRST DAY, AND THE READER DID NOT.** The dictionary chapter's
ruling of 2026-08-12: two matrices over one key space, *«consulted separately, every answer naming
its source, **never blended into one float**»*. `distribution.py`'s own docstring repeats it —
*«neither is folded into the other, here or anywhere downstream»*. And `space.py` returned
`cos(R + 0.15·D)`: one float. The contradiction was inside the codebase, visible, for a month.

Found by the E1 audit of 2026-09-14. **The Captain's ruling:** *«separate — that was a mistake. We
chose two arrays because the use case of inspecting one or another was clear. Blending is for sure
something that can have benefit, but it is against what we thought and we did for a reason.»*

**THE PROCEDURE, AND IT IS MEASURED RATHER THAN PREFERRED.**

  1. **R is asked first.** Where R speaks — a stated cell, or any cosine at all — **R decides**, and
     the answer names R as its source. Measured: R alone decides **15 of the 18** bar pairs it
     speaks on, and its only failure mode is the `derivational` edge, which is requirement 16 and
     already open.
  2. **Where R is silent, the verdict is ABSTAIN**, and D's reading comes back beside it as a
     PROPOSAL. Measured, and this is the number that settles it: with R silent, D cannot separate a
     declared NEAR from a declared FAR. `eat.v~hungry.a` (declared NEAR) reads D cosine **0.338**;
     `bed.n~cause.n` (declared FAR) reads **0.326** — on identical cells of 0.500. Across every
     R-silent pair, **7 of 8 declared NEARs sit at or below the highest declared FAR.**

**SO THE BLEND WAS AVERAGING A DECIDER WITH A PROPOSER**, and that is why twenty-four of thirty-seven
came back undecided: R's clean signal was being diluted by a matrix that provably cannot decide.

**THE FLOOR DOES NOT MOVE, AND THAT IS THE INTERESTING PART.** Swept for R alone: the best zero-wrong
floor is **+0.28** — the same number the blend was fitted to, which says the floor was never an
artefact of blending. Dropping to +0.20 would buy three more decisions (`walk~run` +0.208,
`cause.n~cause.v` +0.222, `eat.v~swallow.v` +0.226, all correctly NEAR) and cost `compass.n~compass.v`
(+0.273). **No floor separates those**, because it is an ORDERING INVERSION: the declared-FAR pair
sits ABOVE a declared-NEAR one, both carried by `derivational`, which says «same root» and not «same
meaning». That is requirement 16 wearing its third disguise, and it belongs to E1d T3.

**THE BAR SCORE IS UNCHANGED — 13 decided, 0 wrong, 24 abstain.** The gain is off the bar:
`thick.a~thin.a` reads R −0.049 → **FAR** where the blend read +0.011 → ABSTAIN, and `push.v~pull.v`
likewise. **Two of the eight measurable opposition pairs recover their sign**, which is exactly the
failure requirement 14 predicted and which nothing was watching because they are not declared.

And the abstentions become legible: «ABSTAIN» stops meaning *a number landed between two floors* and
starts meaning **«R is silent on this pair»** — a diagnosis rather than a shrug, and it points
straight at what T3 has to mine.

**WHAT DOES NOT MOVE.** The FAR ceiling stays 0.0 and is now a CLEANER theorem than before: under the
blend it held because D is unsigned; under separate reads it holds because only R is read at all, so
the sign below zero is the resource's own statement.

**`mix` IS CARRIED, NOT DELETED.** It is a ledger: v7 ruled it, v8, v9 and v10 carried it, and those
four fingerprints must keep hashing to what they measured. Under `separate` no verdict consults it —
but D still has to be scaled when it is asked to PROPOSE, and the mix is what says how loudly.

**NOT APPLIED BY THE QM.** Written and reported; the apply is the Captain's hand.
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, DictionaryPolicyDoc
from tk2.dictionary import policy
from tk2.dictionary.config import READING_SEPARATE, DictionaryConfig, ReadingPolicy
from tk2.migrations import ensure_collections

POLICY_VERSION = 11


def _previous():
    """Version 10 — the near-floor ruling, which carries the whole ledger forward from the baseline."""
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 2), None)
    if found is None:
        raise RuntimeError("0002 is gone — it holds the version this one carries forward")
    return found.load()


PREVIOUS = _previous()

READING = ReadingPolicy(
    mix=PREVIOUS.DECLARED.reading.mix,
    near_floor=PREVIOUS.DECLARED.reading.near_floor,
    far_ceiling=PREVIOUS.DECLARED.reading.far_ceiling,
    mode=READING_SEPARATE,
)

MODE_NOTE = (
    "HOW the two matrices are read. RULED `separate` on 2026-09-14 by the Captain, after the E1 "
    "audit found the reader contradicting requirement 10 — which has said since 2026-08-12 that R "
    "and D are 'consulted separately, every answer naming its source, never blended into one "
    "float', while `space.py` returned cos(R + 0.15*D). His words: 'separate, that was a mistake; "
    "we chose two arrays because the use case of inspecting one or another was clear'. THE "
    "PROCEDURE: R is asked first and where it speaks it DECIDES, naming itself as the source; where "
    "R is SILENT the verdict is ABSTAIN and D comes back beside it as a PROPOSAL, never a verdict. "
    "MEASURED, not preferred: R alone decides 15 of the 18 bar pairs it speaks on, and where R is "
    "silent D cannot separate a declared NEAR from a declared FAR — eat.v~hungry.a (NEAR) reads D "
    "0.338 against bed.n~cause.n (FAR) at 0.326, on identical cells of 0.500, and 7 of 8 declared "
    "NEARs sit at or below the highest declared FAR. So the blend was averaging a DECIDER with a "
    "PROPOSER, which is why 24 of 37 came back undecided. The bar score is unchanged (13 decided, 0 "
    "wrong); the gain is off the bar — thick.a~thin.a recovers FAR at R -0.049 where the blend read "
    "+0.011 and abstained, and so does push.v~pull.v: 2 of the 8 measurable opposition pairs get "
    "their sign back, which is the failure requirement 14 predicted and nothing was watching. The "
    "NEAR floor was re-swept for R alone and does NOT move: +0.28 is still the best zero-wrong "
    "floor, so it was never an artefact of blending. +0.20 would decide three more and get "
    "compass.n~compass.v wrong, and no floor fixes that because it is an ORDERING INVERSION — the "
    "declared-FAR pair sits above a declared-NEAR one, both carried by `derivational`, which states "
    "'same root' and not 'same meaning'. That is requirement 16 and it belongs to T3"
)

DECLARED = DictionaryConfig(
    closure=PREVIOUS.DECLARED.closure,
    declared_seeds=PREVIOUS.DECLARED.declared_seeds,
    bar=PREVIOUS.DECLARED.bar,
    relations=PREVIOUS.DECLARED.relations,
    alphabet=PREVIOUS.DECLARED.alphabet,
    distribution=PREVIOUS.DECLARED.distribution,
    reading=READING,
)

FAMILY_OF = {row["name"]: row["family"]
             for row in PREVIOUS.POLICY_ROWS
             if row["version"] == PREVIOUS.POLICY_VERSION and row["kind"] == policy.KIND_SEED}

POLICY_ROWS = policy.policy_rows_of(DECLARED, POLICY_VERSION, FAMILY_OF)

_CARRIED = {(row["kind"], row["name"]): row["note"]
            for row in PREVIOUS.POLICY_ROWS if row["version"] == PREVIOUS.POLICY_VERSION}

for _row in POLICY_ROWS:
    _key = (_row["kind"], _row["name"])
    _row["note"] = MODE_NOTE if _key == (policy.KIND_READING, "mode") else _CARRIED[_key]


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(DictionaryPolicyDoc, POLICY_ROWS)
