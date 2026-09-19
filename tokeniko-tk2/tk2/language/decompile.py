"""THE DECOMPILER — a zip back into a sentence that compiles to that zip. **Requirement 9.**

**THE NAME IS THE DESIGN** (the Captain, 2026-09-19): *«I would call it decompiler, mimicking the
compiler/decompiler of computer languages»*. Decompiled source is never the original source — it is
A source that compiles to the same object — so the acceptance test arrives with the analogy:
**recompile and compare the zips** (`tools/roundtrip.py`, using the drill gate's own comparator).

**IT IS FAITHFUL TO THE ZIP, NOT TO THE SENTENCE.** Where the parse normalised — a passive folded to
active, «you» resolved to an entity, a word left unplaced — the decompilation says what the zip
holds. That gap is not a defect: it is the misparse signal the brain speaks back («so you mean…?»,
req 3) and an input to the confidence scalar (reqs 4, 6).

**TWO CONSUMERS, AND THE SECOND ONE SETS THE BAR.** Internally the round trip feeds the confidence
scalar. Outwardly the senses speak this text, and rag-out only POLISHES it (senses req 4) — with rag
OFF, this is what ships (rag req 5). So the output must be honest English, not a debug readout, and
the LLM can never invent content because it is handed a sentence that already says exactly what the
zip says.

**THE SPINE IS SYMMETRY, AND IT SETTLES THE FRAME/KNOWLEDGE LINE ONCE.** A decompiling decision lives
where the matching COMPILING decision lives:

    word order · punctuation · clause structure · orthography   FRAME, as decoding is frame
    WHICH WORD carries a meaning                                 KNOWLEDGE — the rows, read backwards

So this module holds no vocabulary. A marker comes from `Box.marker`, which records the preposition
actually used (req 65); everything else is looked up in `language_closed_classes` BY MEANING.

**AND WHERE THE ROWS CANNOT ANSWER, IT REFUSES RATHER THAN CHOOSING.** The inverse map is not a
function — 385 rows carry 81 distinct meanings and 47 of those are many-formed (32 prepositions all
mean `location`, 18 subordinators all mean an asserted `imply`). Where a meaning has exactly one
form, that form is the answer. Where it has several, this module says nothing and records what it
could not say. **An omission that changes what the sentence CLAIMS is not an omission but a lie**, so
a row whose negation cannot be spoken is not rendered at all: half-said is legal, wrongly-said is the
sin (req 8), in this direction as in the other.

*Written as E3 task 3's first slice: one content row to one clause. The prefix, the joins and the
questions follow, each measured by the round trip.*
"""

from __future__ import annotations

from dataclasses import dataclass, field

from tk2.dictionary import keys
from tk2.language.closed import ClosedClasses, standing_closed_classes
from tk2.language.inflect import PRESENT, Inflections, standing_inflections
from tk2.tkzip.schema import (
    Box,
    ContentRow,
    Determination,
    Open,
    Quantity,
    Role,
    Var,
    Zip,
)

#: The subject is the first of these the row fills — the inverse of the compile core's own reading:
#: an agent outranks an experiencer («I love the dog»), and a patient is the subject only when
#: nothing else is («God exists», «the cat is hungry»). WORD ORDER, therefore frame.
SUBJECT_ORDER = (Role.AGENT, Role.EXPERIENCER, Role.PATIENT, Role.TOPIC, Role.COMPLEMENT)

#: What follows the verb directly, in order, before any marked circumstance. `recipient` sits here
#: because English says «give Anna a book» with no marker at all.
OBJECT_ORDER = (Role.RECIPIENT, Role.PATIENT, Role.TOPIC, Role.MEASURE, Role.COMPLEMENT)

#: Manner, then place, then time — English's own ordering of circumstances, and frame for the same
#: reason the two above are. A box with a marker carries it; one without is placed by position.
CIRCUMSTANCE_ORDER = (
    Role.MANNER, Role.INSTRUMENT, Role.COMITATIVE, Role.BENEFICIARY,
    Role.SOURCE, Role.PATH, Role.DIRECTION, Role.DESTINATION, Role.LOCATION,
    Role.TIME, Role.DURATION,
)

#: The copula. It is not vocabulary in the sense the rows own: a copular row earns no predicate
#: (req 31) because English's «be» carries no meaning there — it is the structure of a predication,
#: which is frame. Recorded here so the audit sees it rather than having to find it.
COPULA = "be"

CLAIMED = 1.0
DENIED = 0.0


@dataclass
class Decompiled:
    """The sentence, and an honest account of what did not reach it.

    `unsaid` is `Compiled.unplaced`'s mirror and exists for the same reason: the thing that knows it
    failed to say something is this module, and throwing that away means re-deriving it later,
    expensively and imperfectly. `refused` names the rows that could not be said WITHOUT LYING and
    were therefore not said at all.
    """

    text: str = ""
    unsaid: list[str] = field(default_factory=list)
    refused: list[str] = field(default_factory=list)

    @property
    def whole(self) -> bool:
        return not self.unsaid and not self.refused


class Decompiler:
    """Zip → sentence. Pure: it reads the rows it is handed and keeps no state between calls."""

    def __init__(self, table: ClosedClasses | None = None,
                 inflections: Inflections | None = None) -> None:
        self.table = table if table is not None else standing_closed_classes()
        #: The spelling rule and the words it gets wrong (`db/0022`). Without it every clause is a
        #: string of lemmas, and a lemma verb is an IMPERATIVE to the parser — 26 of the round
        #: trip's first 32 failures were that one artefact.
        self.inflections = inflections if inflections is not None else standing_inflections()
        self._by_meaning = self._invert(self.table)
        self._spoken = self._voices(self.table)

    # -- the rows, read backwards -----------------------------------------------------------------

    @staticmethod
    def _invert(table: ClosedClasses) -> dict[tuple, set[str]]:
        """MEANING → the forms that carry it. Built once, like the forward index it mirrors."""
        found: dict[tuple, set[str]] = {}
        for row in table._rows:                       # noqa: SLF001 — the table's own inverse index
            compiled = row.get("compiled") or {}
            if not compiled:
                continue
            key = (row.get("role"), tuple(sorted((k, str(v)) for k, v in compiled.items())))
            found.setdefault(key, set()).add(row["form"])
        return found

    @staticmethod
    def _voices(table: ClosedClasses) -> dict[tuple, str]:
        """MEANING → the one form curation says it is SPOKEN with (`db/0021`'s flag).

        This is where the inverse map stops being a guess. The table's own check holds that at most
        one row per meaning carries it, so a lookup here cannot become a choice made in code.
        """
        found: dict[tuple, str] = {}
        for row in table._rows:                       # noqa: SLF001 — the table's own inverse index
            if not row.get("spoken"):
                continue
            compiled = row.get("compiled") or {}
            key = (row.get("role"), tuple(sorted((k, str(v)) for k, v in compiled.items())))
            found[key] = row["form"]
        return found

    def forms_for(self, role: str, **compiled) -> set[str]:
        """Every form the table gives this meaning — empty when it gives none."""
        key = (role, tuple(sorted((k, str(v)) for k, v in compiled.items())))
        return set(self._by_meaning.get(key, ()))

    def the_form(self, role: str, **compiled) -> str | None:
        """The form, when the table names exactly ONE. None when it names several or none.

        This is the whole of the module's vocabulary discipline: a meaning with one spelling is a
        lookup, and a meaning with several is a CHOICE — which is curation, does not live in code,
        and is not made here. The caller records the silence.
        """
        key = (role, tuple(sorted((k, str(v)) for k, v in compiled.items())))
        spoken = self._spoken.get(key)
        if spoken is not None:
            return spoken
        found = self.forms_for(role, **compiled)
        return next(iter(found)) if len(found) == 1 else None

    # -- the sentence ------------------------------------------------------------------------------

    def decompile(self, zip_: Zip) -> Decompiled:
        """Every content row as a clause, in the order the zip holds them.

        The first slice: content rows only. A zip carrying prefix rows or joins says MORE than this
        text does, and every one of them is recorded as unsaid rather than quietly dropped — which
        is what keeps the round trip's number honest while the rest is built.
        """
        out = Decompiled()
        sentences = []
        for row in zip_.rows:
            if row.kind != "content":
                out.unsaid.append(f"{row.kind} row {row.name}")
                continue
            said = self._clause(row, out)
            if said is None:
                out.refused.append(f"content row {row.name}")
                continue
            sentences.append(said)
        out.text = " ".join(self._finish(s) for s in sentences)
        return out

    @staticmethod
    def _finish(clause: str) -> str:
        """Capital, full stop. Orthography, and orthography is frame — the compiler reads the `?`
        and the `!` as structure and never as vocabulary, so the decompiler writes them the same."""
        clause = clause.strip()
        return (clause[:1].upper() + clause[1:] + ".") if clause else ""

    def _clause(self, row: ContentRow, out: Decompiled) -> str | None:
        """One content row to one clause, or None when it cannot be said without lying."""
        boxes = dict(row.boxes)

        if isinstance(row.truth, Open):
            out.unsaid.append(f"{row.name} is ASKED and the question is not built yet")
            return None
        if row.truth is None:
            out.unsaid.append(f"{row.name} is stated-but-unclaimed and the prefix is not built yet")
            return None

        negated = row.truth == DENIED
        negation = self.the_form("negation", kind="prefix", element="negation")
        if negated and negation is None:
            # The table gives «not» and «no» the same meaning, so nothing here can choose. Saying
            # the clause without its negation would say the OPPOSITE of the zip.
            out.refused.append(f"{row.name}: the negation has no single form in the table")
            return None
        if row.truth not in (CLAIMED, DENIED):
            out.unsaid.append(f"{row.name} is held at {row.truth} and a hedge is not built yet")

        subject_role = next((r for r in SUBJECT_ORDER if r in boxes), None)
        subject = ""
        if subject_role is not None:
            subject = self._phrase(boxes.pop(subject_role), out)

        lemma = keys.word_of(row.predicate) if row.predicate else COPULA
        verb = self.inflections.of(lemma, PRESENT)
        if negated:
            # «does not think», «is not a mind» — the auxiliary carries the inflection and the verb
            # falls back to its lemma, which is English's own rule and therefore frame.
            verb = (f"{self.inflections.of('do', PRESENT)} {negation} {lemma}"
                    if row.predicate else f"{verb} {negation}")

        after = []
        for role in OBJECT_ORDER:
            if role in boxes:
                after.append(self._phrase(boxes.pop(role), out))
        for role in CIRCUMSTANCE_ORDER:
            if role in boxes:
                after.append(self._phrase(boxes.pop(role), out))
        for role in list(boxes):
            out.unsaid.append(f"{row.name}: the {role.value} box has no place in a clause yet")
            boxes.pop(role)

        parts = [part for part in (subject, verb, *after) if part]
        return " ".join(parts) if parts else None

    # -- the noun phrase ---------------------------------------------------------------------------

    def _phrase(self, box: Box, out: Decompiled) -> str:
        """A box as a phrase: its marker, its determiner, its head — in that order, which is frame."""
        head = self._head(box, out)
        if not head:
            return ""

        words = []
        if box.marker:
            words.append(box.marker)                  # req 65: the preposition actually used
        determiner = self._determiner(box, out, head)
        if determiner:
            words.append(determiner)
        if box.relation is not None:
            out.unsaid.append("a possessor: the possessive forms are many and none is preferred")
        if box.count is not None and not isinstance(box.count, (Open, Var)):
            words.append(str(box.count))
        words.append(head)
        return " ".join(words)

    def _head(self, box: Box, out: Decompiled) -> str:
        """The word in the box — a key becomes its word, and an abstention stays an abstention."""
        if isinstance(box.head, Open):
            out.unsaid.append("an OPEN head: the wh-word is not built yet")
            return ""
        if isinstance(box.head, Var):
            out.unsaid.append(f"the variable {box.head.name}: quantifiers are not built yet")
            return ""
        if box.head is None:
            return ""
        return keys.word_of(str(box.head))

    def _determiner(self, box: Box, out: Decompiled, head: str) -> str:
        """«the» / «a» where the table names one form, and silence where it names several.

        `quantity` is where it goes silent: *universal* is «every», «all», «each» and thirty more,
        and choosing among them is curation nobody has done. `determination` is luckier — English has
        ONE definite article — and `indefinite` is «a» or «an», which is not a choice of word but a
        SPELLING of one, so the vowel rule is applied here as orthography.
        """
        if isinstance(box.quantity, Quantity):
            form = self.the_form("quantificational", kind="quantifier", quantity=box.quantity.value)
            if form is None:
                out.unsaid.append(f"a {box.quantity.value} quantity: the table names several forms "
                                  f"and none is preferred")
                return ""
            return form
        if isinstance(box.determination, Determination):
            if box.determination is Determination.GENERIC:
                return ""                              # a generic is bare in English: «cats sleep»
            found = self.forms_for("determination", kind="determination",
                                   determination=box.determination.value, was="quantificational")
            if not found:
                out.unsaid.append(f"a {box.determination.value} determination: no form in the table")
                return ""
            if len(found) == 1:
                return next(iter(found))
            # «a» and «an» are one word in two spellings, and which one is settled by the sound that
            # follows — orthography, and therefore frame. Nothing else in this module chooses.
            vowel = head[:1].lower() in "aeiou"
            return next((f for f in sorted(found) if (f.endswith("n") == vowel)), sorted(found)[0])
        return ""
