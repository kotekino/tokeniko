"""UD's own examples, transcribed with their published annotations — the station's gate.

**WHY THESE AND NOT MORE OF OUR OWN SENTENCES** (the Captain, 2026-09-15): our fixtures encode OUR
habits. UD's examples are strangers' sentences, written by people documenting a standard and not by
anyone trying to make tokeniko pass. And both ends of the mapping are CLOSED — 37 relations in, 18
tkzip roles and 10 operators and the five-element prefix out — so the table can be complete rather
than merely large.

**TRANSCRIBED, NOT INVENTED.** Every sentence here is from `universaldependencies.org/u/dep/<rel>`,
and where the page prints the annotation (`case(Chair-2, 's-3)`) the head and label are that page's,
converted from its 1-indexed head-0-is-root convention to ours. Where a page prints a sentence
without a full parse, the missing columns are stanza's, and the entry says so in `annotated`. An
origin that cannot be checked is not evidence — the rule that produced `CLAUDE.md`.

**WHAT AN ENTRY CLAIMS.** `relation` is what UD calls the marked edge. `expect` is what the STATION
should make of it, and it is the claim under test: a tkzip role for the boxes, an operator for the
joins, `None` where the relation carries no compiled meaning of its own. `expect` is the 37 → 18
mapping, one line at a time, and where it is still unknown the entry says `OPEN` rather than
guessing — an abstention is a measurement and a guess is not.
"""

from dataclasses import dataclass, field

from tk2.language.skeleton import Skeleton, skeleton_from_conllu

#: What the station should produce for the marked edge, when it is not a role.
JOIN = "join"
PREFIX = "prefix"
ENTITY = "entity"
STRUCTURE = "structure"
OPEN = "OPEN"          # not yet ruled — the honest state, and it is COUNTED


@dataclass(frozen=True, slots=True)
class Case:
    """One UD example, and what the station owes it."""

    relation: str
    text: str
    rows: tuple[tuple[str, ...], ...]
    #: index of the token whose reading is under test (the marker, or the dependent)
    at: int
    #: what the station should make of it — a tkzip role, one of the constants above, or OPEN
    expect: str
    note: str = ""
    annotated: bool = True

    @property
    def skeleton(self) -> Skeleton:
        return skeleton_from_conllu(self.text, self.rows)


def _c(relation, text, rows, at, expect, note="", annotated=True):
    return Case(relation=relation, text=text, rows=tuple(rows), at=at, expect=expect,
                note=note, annotated=annotated)


CASES: tuple[Case, ...] = (
    # ── case ─────────────────────────────────────────────────────────────────────────────────────
    _c("case", "the Chair 's office", [
        ("1", "the", "the", "DET", "2", "det"),
        ("2", "Chair", "chair", "NOUN", "4", "nmod"),
        ("3", "'s", "'s", "PART", "2", "case"),
        ("4", "office", "office", "NOUN", "0", "root"),
    ], at=2, expect="relation",
       note="THE POSSESSIVE IS A `case` TOO. tkzip has no possessor ROLE — the possessor lives "
            "INSIDE the record, as Box.relation (req 26). So `'s` fills a field, not a box."),

    _c("case", "the office of the Chair", [
        ("1", "the", "the", "DET", "2", "det"),
        ("2", "office", "office", "NOUN", "0", "root"),
        ("3", "of", "of", "ADP", "5", "case"),
        ("4", "the", "the", "DET", "5", "det"),
        ("5", "Chair", "chair", "NOUN", "2", "nmod"),
    ], at=2, expect="relation",
       note="UD's own pairing: this is the SAME relation as «the Chair's office», so it must reach "
            "the same place. `of` under `nmod` is the possessor, not the COMPLEMENT reading."),

    _c("case", "Sue left after the rehearsal", [
        ("1", "Sue", "sue", "PROPN", "2", "nsubj"),
        ("2", "left", "leave", "VERB", "0", "root"),
        ("3", "after", "after", "ADP", "5", "case"),
        ("4", "the", "the", "DET", "5", "det"),
        ("5", "rehearsal", "rehearsal", "NOUN", "2", "obl"),
    ], at=2, expect="time"),

    _c("case", "Sue is in shape", [
        ("1", "Sue", "sue", "PROPN", "4", "nsubj"),
        ("2", "is", "be", "AUX", "4", "cop"),
        ("3", "in", "in", "ADP", "4", "case"),
        ("4", "shape", "shape", "NOUN", "0", "root"),
    ], at=2, expect=OPEN,
       note="A PREDICATIVE `case`: «in shape» is not a location, it is what Sue IS. The marker is "
            "doing copular work and the box it fills is the complement — but `in` is one of the "
            "thirteen ambiguous markers and nothing here selects for it yet."),

    _c("case", "The cafe up beside the lookout", [
        ("1", "The", "the", "DET", "2", "det"),
        ("2", "cafe", "cafe", "NOUN", "0", "root"),
        ("3", "up", "up", "ADP", "6", "case"),
        ("4", "beside", "beside", "ADP", "6", "case"),
        ("5", "the", "the", "DET", "6", "det"),
        ("6", "lookout", "lookout", "NOUN", "2", "nmod"),
    ], at=3, expect="location",
       note="TWO `case` MARKERS ON ONE NOMINAL, not frozen — UD's own contrast with `fixed`. The "
            "station must not merge them into one form the way it merges «because of»."),

    # ── obl, and the agent subtype ───────────────────────────────────────────────────────────────
    _c("obl", "I talked to my friend in the park", [
        ("1", "I", "i", "PRON", "2", "nsubj"),
        ("2", "talked", "talk", "VERB", "0", "root"),
        ("3", "to", "to", "ADP", "5", "case"),
        ("4", "my", "my", "PRON", "5", "nmod:poss"),
        ("5", "friend", "friend", "NOUN", "2", "obl"),
        ("6", "in", "in", "ADP", "8", "case"),
        ("7", "the", "the", "DET", "8", "det"),
        ("8", "park", "park", "NOUN", "2", "obl"),
    ], at=2, expect="recipient",
       note="`to` under obl with a communication verb is the RECIPIENT, not a destination — and "
            "nothing in the table can tell those apart. This is the head-verb geometry case.",
       annotated=False),

    _c("obl:agent", "the cat was chased by the dog", [
        ("1", "the", "the", "DET", "2", "det"),
        ("2", "cat", "cat", "NOUN", "4", "nsubj:pass"),
        ("3", "was", "be", "AUX", "4", "aux:pass"),
        ("4", "chased", "chase", "VERB", "0", "root"),
        ("5", "by", "by", "ADP", "7", "case"),
        ("6", "the", "the", "DET", "7", "det"),
        ("7", "dog", "dog", "NOUN", "4", "obl:agent"),
    ], at=4, expect="agent",
       note="**THE SUBTYPE DOES THE DISAMBIGUATION FOR FREE.** `by` is instrument/agent/path/time "
            "in the table, and `obl:agent` says which — one of the thirteen, solved by UD itself."),

    _c("obl", "Last night , I swam in the pool", [
        ("1", "Last", "last", "ADJ", "2", "amod"),
        ("2", "night", "night", "NOUN", "5", "obl:tmod"),
        ("3", ",", ",", "PUNCT", "5", "punct"),
        ("4", "I", "i", "PRON", "5", "nsubj"),
        ("5", "swam", "swim", "VERB", "0", "root"),
        ("6", "in", "in", "ADP", "8", "case"),
        ("7", "the", "the", "DET", "8", "det"),
        ("8", "pool", "pool", "NOUN", "5", "obl"),
    ], at=5, expect="location",
       note="An UNMARKED time («last night», obl:tmod) beside a marked location. The time box is "
            "filled by a bare nominal here — no marker at all.", annotated=False),

    # ── the core arguments: marked by POSITION, and by no preposition ─────────────────────────────
    _c("nsubj", "the cat chased the dog", [
        ("1", "the", "the", "DET", "2", "det"),
        ("2", "cat", "cat", "NOUN", "3", "nsubj"),
        ("3", "chased", "chase", "VERB", "0", "root"),
        ("4", "the", "the", "DET", "5", "det"),
        ("5", "dog", "dog", "NOUN", "3", "obj"),
    ], at=1, expect="agent",
       note="No marker exists for agent or patient, which is why they are the two roles with no "
            "row in the marker table. UD marks them by RELATION.", annotated=False),

    _c("obj", "the cat chased the dog", [
        ("1", "the", "the", "DET", "2", "det"),
        ("2", "cat", "cat", "NOUN", "3", "nsubj"),
        ("3", "chased", "chase", "VERB", "0", "root"),
        ("4", "the", "the", "DET", "5", "det"),
        ("5", "dog", "dog", "NOUN", "3", "obj"),
    ], at=4, expect="patient", annotated=False),

    _c("iobj", "she gave me a raise", [
        ("1", "she", "she", "PRON", "2", "nsubj"),
        ("2", "gave", "give", "VERB", "0", "root"),
        ("3", "me", "me", "PRON", "2", "iobj"),
        ("4", "a", "a", "DET", "5", "det"),
        ("5", "raise", "raise", "NOUN", "2", "obj"),
    ], at=2, expect=ENTITY,
       note="THE DOUBLE-OBJECT RECIPIENT, with no preposition at all — «she gave me a raise». The "
            "ROLE is `recipient` and it comes from the RELATION (`iobj`), not from any marker, "
            "exactly as agent and patient do. What the closed-class table owes here is only «this "
            "pronoun resolves to an entity»; filling the recipient box is the compile core's job. "
            "Expecting `recipient` of the TABLE was asking it a question it cannot hold — the same "
            "mistake as expecting `time` from a wh-word."),

    # ── the joins ────────────────────────────────────────────────────────────────────────────────
    _c("mark", "he says that you like to swim", [
        ("1", "he", "he", "PRON", "2", "nsubj"),
        ("2", "says", "say", "VERB", "0", "root"),
        ("3", "that", "that", "SCONJ", "5", "mark"),
        ("4", "you", "you", "PRON", "5", "nsubj"),
        ("5", "like", "like", "VERB", "2", "ccomp"),
        ("6", "to", "to", "PART", "7", "mark"),
        ("7", "swim", "swim", "VERB", "5", "xcomp"),
    ], at=2, expect=OPEN,
       note="«that» under a REPORTING verb opens a POV, not a join — E2 ruled attitude a prefix "
            "element with its own holder. The station owes a rule here and has none yet."),

    _c("cc", "she was reading or writing", [
        ("1", "she", "she", "PRON", "3", "nsubj"),
        ("2", "was", "be", "AUX", "3", "aux"),
        ("3", "reading", "read", "VERB", "0", "root"),
        ("4", "or", "or", "CCONJ", "5", "cc"),
        ("5", "writing", "write", "VERB", "3", "conj"),
    ], at=3, expect="or",
       note="A coordinator IS an operator — one of the ten, by name."),

    _c("advcl", "if you know who did it , tell me", [
        ("1", "if", "if", "SCONJ", "3", "mark"),
        ("2", "you", "you", "PRON", "3", "nsubj"),
        ("3", "know", "know", "VERB", "9", "advcl"),
        ("4", "who", "who", "PRON", "5", "nsubj"),
        ("5", "did", "do", "VERB", "3", "ccomp"),
        ("6", "it", "it", "PRON", "5", "obj"),
        ("7", ",", ",", "PUNCT", "9", "punct"),
        ("8", "tell", "tell", "VERB", "0", "root"),
        ("9", "me", "me", "PRON", "8", "obj"),
    ], at=0, expect="imply",
       note="«if» is IMPLY with the join CLAIMED and both halves EMPTY — E2's own distinction "
            "between «if» and «because», carried by the truth slot and not by a relation."),

    # ── the prefix elements ──────────────────────────────────────────────────────────────────────
    _c("aux", "he can swim", [
        ("1", "he", "he", "PRON", "3", "nsubj"),
        ("2", "can", "can", "AUX", "3", "aux"),
        ("3", "swim", "swim", "VERB", "0", "root"),
    ], at=1, expect=PREFIX,
       note="A modal is a PREFIX element scoping a matrix (req 35), never a field on the row."),

    _c("advmod", "he does n't swim", [
        ("1", "he", "he", "PRON", "4", "nsubj"),
        ("2", "does", "do", "AUX", "4", "aux"),
        ("3", "n't", "not", "PART", "4", "advmod"),
        ("4", "swim", "swim", "VERB", "0", "root"),
    ], at=2, expect=PREFIX,
       note="Negation is a prefix element too, and «not all» vs «all not» is exactly why it scopes "
            "rather than sitting on the row.", annotated=False),

    _c("det", "every cat sleeps", [
        ("1", "every", "every", "DET", "2", "det"),
        ("2", "cat", "cat", "NOUN", "3", "nsubj"),
        ("3", "sleeps", "sleep", "VERB", "0", "root"),
    ], at=0, expect=PREFIX,
       note="A quantifier BINDS — it is a prefix row with a variable, not a field on the box.",
       annotated=False),

    _c("det", "the cat sleeps", [
        ("1", "the", "the", "DET", "2", "det"),
        ("2", "cat", "cat", "NOUN", "3", "nsubj"),
        ("3", "sleeps", "sleep", "VERB", "0", "root"),
    ], at=0, expect="determination",
       note="AND THE ARTICLE IS NOT ONE — db/0008's re-typing, read off a real dependency: same "
            "`det` relation, different compiled meaning, and only the ROW can tell them apart.",
       annotated=False),

    # ── things that compile to nothing ───────────────────────────────────────────────────────────
    _c("cop", "Sue is a teacher", [
        ("1", "Sue", "sue", "PROPN", "4", "nsubj"),
        ("2", "is", "be", "AUX", "4", "cop"),
        ("3", "a", "a", "DET", "4", "det"),
        ("4", "teacher", "teacher", "NOUN", "0", "root"),
    ], at=1, expect=STRUCTURE,
       note="Plain copular `be` compiles to STRUCTURE and earns no dimension (req 31): «the cat is "
            "cute» comes out as cat + cute, no verb.", annotated=False),

    _c("punct", "the cat sleeps .", [
        ("1", "the", "the", "DET", "2", "det"),
        ("2", "cat", "cat", "NOUN", "3", "nsubj"),
        ("3", "sleeps", "sleep", "VERB", "0", "root"),
        ("4", ".", ".", "PUNCT", "3", "punct"),
    ], at=3, expect=STRUCTURE, annotated=False),

    _c("compound:prt", "he looked up", [
        ("1", "he", "he", "PRON", "2", "nsubj"),
        ("2", "looked", "look", "VERB", "0", "root"),
        ("3", "up", "up", "ADP", "2", "compound:prt"),
    ], at=2, expect=STRUCTURE,
       note="THE PARTICLE OF A PHRASAL VERB — it marks no role and takes no object. The live parse "
            "that found the selector bug: the tag says ADP and only the relation says otherwise.",
       annotated=False),

    _c("fixed", "out of the box", [
        ("1", "out", "out", "ADP", "4", "case"),
        ("2", "of", "of", "ADP", "1", "fixed"),
        ("3", "the", "the", "DET", "4", "det"),
        ("4", "box", "box", "NOUN", "0", "root"),
    ], at=0, expect="source",
       note="UD's `fixed` marks the frozen multiword — and the table already holds «out of» as ONE "
            "form. The two agree, which is what makes longest-first matching safe here."),

    # ── the pronouns and the open slots ──────────────────────────────────────────────────────────
    _c("nsubj", "I sleep", [
        ("1", "I", "i", "PRON", "2", "nsubj"),
        ("2", "sleep", "sleep", "VERB", "0", "root"),
    ], at=0, expect=ENTITY,
       note="A pronoun is INDEXICAL — resolved to an entity before the dictionary is consulted "
            "(the second standing law). It never earns a dimension.", annotated=False),

    _c("advmod", "when do you sleep ?", [
        ("1", "when", "when", "ADV", "4", "advmod"),
        ("2", "do", "do", "AUX", "4", "aux"),
        ("3", "you", "you", "PRON", "4", "nsubj"),
        ("4", "sleep", "sleep", "VERB", "0", "root"),
        ("5", "?", "?", "PUNCT", "4", "punct"),
    ], at=0, expect="open",
       note="A wh-word OPENS a slot — «there is no mood field»: a question IS something open. WHICH "
            "box it opens (here, time) is the compile core's answer and not the table's: the row "
            "can only say «this leaves something open», which is exactly what it says. My first "
            "transcription expected `time` and was asking the table a question it cannot hold.",
       annotated=False),

    _c("acl:relcl", "the cat that sleeps", [
        ("1", "the", "the", "DET", "2", "det"),
        ("2", "cat", "cat", "NOUN", "0", "root"),
        ("3", "that", "that", "PRON", "4", "nsubj"),
        ("4", "sleeps", "sleep", "VERB", "2", "acl:relcl"),
    ], at=2, expect=OPEN,
       note="A RELATIVE binds its antecedent — a variable shared between two rows. The format has "
            "`Var` for exactly this and the station has no rule that emits one yet.",
       annotated=False),
)


#: WHAT THE RELATION ITSELF SETTLES, with no marker in sight — the other half of the 37 → 18 table.
#: These are the CORE arguments, and the reason `patient` and `experiencer` have no marker row: UD
#: marks them by position and by relation, never by a preposition. Not yet implemented — the compile
#: core (E3 task 2) is what will read these — but transcribed here so the mapping is one document.
RELATION_FILLS_ROLE: dict[str, str] = {
    "nsubj": "agent",          # «the cat chased the dog» — and experiencer for perception verbs,
                               # which is a head-verb question the geometry answers, not a label
    "nsubj:pass": "patient",   # the passive subject IS the patient — «the cat was chased»
    "obj": "patient",
    "iobj": "recipient",       # the double-object recipient: «she gave ME a raise»
    "obl:agent": "agent",      # already settled in code, and listed here so the table is one place
    "obl:tmod": "time",
    "obl:lmod": "location",
}


def by_relation() -> dict[str, list[Case]]:
    out: dict[str, list[Case]] = {}
    for case in CASES:
        out.setdefault(case.relation, []).append(case)
    return out


#: The relations this corpus reaches, bared of subtypes — the gate's coverage of UD's 37.
def covered() -> set[str]:
    return {case.relation.split(":")[0] for case in CASES}
