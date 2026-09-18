"""THE SELECTOR FOR THE THIRTEEN — which role an ambiguous marker actually fills, here.

**WHAT THIS FILE IS AND WHAT IT IS NOT.** `db/0008` kept every candidate a marker can mark, ordered
best-first, and refused to pick: *«a row that named ONE would be a lie the compiler could not
detect»*. `db/0012` says WHAT SETTLES each one — an ordered list of rules ending in a default. This
file knows how to RUN a rule and nothing else. **That seam is the standing law's first clause**: the
mapping is curation and lives in rows, the selector is frame and lives in code, and a new
preposition is a migration while a new kind of probe is a code change.

**THE THREE PROBES, IN THE ORDER THEY COST.**

1. `head_pos` — UD's own tag on the word the phrase hangs off. No dictionary, no lookup. It is what
   settles `of` outright: «the office OF the Chair» hangs off a noun and is the complement, «made OF
   titanium» hangs off a verb and is the material.
2. `nominal` — the SUPERSENSE of the marked noun. «at noon» against «at the door» is the whole
   problem, and `noun.time` against `noun.artifact` is the whole answer.
3. `verb` — the supersense of the head verb, which is the case `db/0008` predicted: give-like
   against go-like for «to».

**A DEFAULT IS AN ANSWER, AND IT SAYS SO.** The compile core abstained on these markers because
picking `roles[0]` would be the *silently*-complete nearest fit req 8 forbids. A default that the
zip's bookkeeping records as a default is not silent — and it is measured, which `roles[0]` never
was. `Settled.ground` is what keeps the two apart, and req 4's confidence scalar is the caller
entitled to the difference.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from tk2.dictionary.supersense import derived_supersense, supersense_for

#: What a rule may read. Frame — `db/0012` writes these strings and this file runs them.
NOMINAL, VERB, HEAD_POS, DEFAULT = "nominal", "verb", "head_pos", "default"
#: Two probes added for the subject's role (req 22, `db/0018`): the head's own LEMMA — an
#: exception row, «disagree» — and the supersense of the noun an adjectival head is DERIVED with.
LEMMA, DERIVED = "lemma", "derived"

#: How a role was reached. `settled` = a rule fired on evidence in the sentence; `default` = nothing
#: did, and the curation's best-first answer stands.
SETTLED, GROUND_DEFAULT = "settled", "default"


@dataclass(frozen=True, slots=True)
class Settled:
    """One marker's role, and the standing of the answer."""

    role: str
    ground: str
    #: what actually decided — `nominal:noun.time`, `head_pos:VERB`, `default` — for the record and
    #: for the bench, which is worth nothing if it cannot say WHY a case went the way it did
    why: str

    @property
    def is_default(self) -> bool:
        return self.ground == GROUND_DEFAULT


class MarkerSelector:
    """Runs a row's `selector` rules against one marked phrase.

    The supersense reader is an ARGUMENT so a test can state what the resource says instead of
    depending on which WordNet is installed — the same seam `ClosedClasses` uses for its rows.
    """

    def __init__(self, supersense: Callable[[str, str], str | None] = supersense_for,
                 derived: Callable[[str], str | None] = derived_supersense) -> None:
        self._supersense = supersense
        self._derived = derived

    def settle(self, compiled: dict, nominal_lemma: str = "", nominal_upos: str = "",
               head_lemma: str = "", head_upos: str = "") -> Settled | None:
        """The role this marker fills, or None when the row declares no selector.

        None means «this is not one of the thirteen» — a marker with a single candidate needs no
        selector and never gets one, and a caller must not read the absence as an abstention.
        """
        rules = (compiled or {}).get("selector") or ()
        if not rules:
            return None
        for rule in rules:
            reads = rule.get("reads")
            if reads == DEFAULT:
                return Settled(rule["then"], GROUND_DEFAULT, DEFAULT)
            wanted = rule.get("is") or ()
            if reads == HEAD_POS:
                if (head_upos or "").upper() in wanted:
                    return Settled(rule["then"], SETTLED, f"{HEAD_POS}:{head_upos}")
                continue
            if reads == LEMMA:
                if (head_lemma or "").lower() in wanted:
                    return Settled(rule["then"], SETTLED, f"{LEMMA}:{head_lemma}")
                continue
            if reads == NOMINAL:
                found = self._supersense(nominal_lemma, nominal_upos)
            elif reads == VERB:
                found = self._supersense(head_lemma, head_upos)
            elif reads == DERIVED:
                found = self._derived(head_lemma)
            else:
                # A probe this frame does not implement. Skipped rather than raised: a row written
                # by a later migration must not stop an older station, and the default still stands.
                continue
            if found is not None and found in wanted:
                return Settled(rule["then"], SETTLED, f"{reads}:{found}")
        # Unreachable while `db/0012`'s own check holds — every selector ends in a default — and
        # kept because a row is data and a station that trusted data to be well-formed would be
        # trusting the wrong thing.
        return None
