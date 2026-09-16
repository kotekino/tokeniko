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
ROW = "row"            # it must open a CONTENT ROW of its own — ruled by tkzip, not built by E3 yet

#: Relations that DO NOT ARISE IN ENGLISH, so an empty corpus for them is COMPLETE rather than
#: missing. `clf` is the classifier — UD's page has no English example because English has none, and
#: its first example is Mandarin; `dislocated` likewise prints none. Reported apart from «not yet
#: reached», because the two are different states and averaging them would make the coverage number
#: a lie in the flattering direction.
NOT_IN_ENGLISH = ("clf", "dislocated")

#: The relations the corpus gained on 2026-09-16, when it went from 16 relations to all 37. They are
#: the HARD ones by construction — everything easy had already been transcribed — so a coverage
#: number over the whole corpus is not comparable with one from before.
#:
#: **Kept so the floor can be stated in two halves and neither can hide the other**: the cases that
#: existed before must not REGRESS (a ratchet), and these are the FRONTIER, where the number is
#: expected to be low and to climb. One averaged figure would let a real regression on the old cases
#: be paid for by a lucky gain on the new ones.
FRONTIER = ("amod", "appos", "ccomp", "conj", "csubj", "discourse", "expl", "flat", "goeswith",
            "list", "nmod", "nummod", "orphan", "parataxis", "reparandum", "root", "vocative",
            "xcomp")
#: A relation may gain a case AFTER the split — the frontier grows, the ratchet never does. «Sam
#: spent forty dollars» arrived on 2026-09-16 to MEASURE a limit rather than to claim a feature.


def ratchet() -> tuple:
    """The cases that existed before 2026-09-16 — the half that may never get worse."""
    return tuple(c for c in CASES if c.relation not in FRONTIER)


def frontier() -> tuple:
    """The cases added when the corpus reached all 37 relations — the half that is meant to climb."""
    return tuple(c for c in CASES if c.relation in FRONTIER)


#: UD's OWN abstention: `dep` means «we could not decide which relation this is». There is nothing
#: for the station to owe, and a case asserting otherwise would be testing our reading of a shrug.
UD_ABSTAINS = ("dep",)


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

    # ══ THE TWENTY-ONE RELATIONS THE GATE HAD NOT REACHED, added 2026-09-16 ═══════════════════
    # Transcribed from each relation's own page, then parsed by stanza and CHECKED against the
    # published edge. **Stanza produces 15 of the 18; the three it does not — `goeswith`,
    # `orphan`, `reparandum` — are named on their own cases and are all ONE FAMILY: a typo, a
    # gapping, a self-correction. The station will never meet them labelled from this provider.**

    # ── amod ──
    _c("amod", "Sam eats large hot dogs", [
        ("1", "Sam", "sam", "PROPN", "2", "nsubj"),
        ("2", "eats", "eat", "VERB", "0", "root"),
        ("3", "large", "large", "ADJ", "5", "amod"),
        ("4", "hot", "hot", "ADJ", "5", "amod"),
        ("5", "dogs", "dog", "NOUN", "2", "obj"),
    ], at=2, expect=ROW,
       note="**REQ 70 ALREADY RULES THIS: attributive adjectives are SECOND ROWS, not a field** — «a human body» is EXISTS B (body(B) AND human(B)), the same machinery as the depictive «he ate the fish raw». The station does not build it yet, and «Last night» leaving `Last` unplaced is the same hole seen from the other side."),

    # ── appos ──
    _c("appos", "Sam , my brother , arrived", [
        ("1", "Sam", "sam", "PROPN", "6", "nsubj"),
        ("2", ",", ",", "PUNCT", "1", "punct"),
        ("3", "my", "my", "PRON", "4", "nmod:poss"),
        ("4", "brother", "brother", "NOUN", "1", "appos"),
        ("5", ",", ",", "PUNCT", "1", "punct"),
        ("6", "arrived", "arrive", "VERB", "0", "root"),
    ], at=3, expect=OPEN,
       note="«Sam, my brother» is ONE individual under two descriptions. Whether that is an identity row, a second row, or the record's own `relation` field is not ruled — and it leans on E3b, because the descriptions are usually names."),

    # ── ccomp ──
    _c("ccomp", "He said that he knew the muffin man .", [
        ("1", "He", "he", "PRON", "2", "nsubj"),
        ("2", "said", "say", "VERB", "0", "root"),
        ("3", "that", "that", "SCONJ", "5", "mark"),
        ("4", "he", "he", "PRON", "5", "nsubj"),
        ("5", "knew", "know", "VERB", "2", "ccomp"),
        ("6", "the", "the", "DET", "8", "det"),
        ("7", "muffin", "muffin", "NOUN", "8", "compound"),
        ("8", "man", "man", "NOUN", "5", "obj"),
        ("9", ".", ".", "PUNCT", "2", "punct"),
    ], at=4, expect="predicate",
       note="A complement CLAUSE opens a row of its own. What relates it to the matrix is the other half — E2 made attitude a PREFIX element, so a reporting verb should raise a POV rather than a join, and that is still on E3's list."),

    # ── conj ──
    _c("conj", "Bill is big and honest", [
        ("1", "Bill", "bill", "PROPN", "3", "nsubj"),
        ("2", "is", "be", "AUX", "3", "cop"),
        ("3", "big", "big", "ADJ", "0", "root"),
        ("4", "and", "and", "CCONJ", "5", "cc"),
        ("5", "honest", "honest", "ADJ", "3", "conj"),
    ], at=4, expect="complement",
       note="«Bill is big and honest» — two copular predications sharing a subject. The second is a row, and `and` is the join. The shared subject is the part that has to be a VARIABLE rather than a repeated box."),

    # ── csubj ──
    _c("csubj", "That he lied surprised me .", [
        ("1", "That", "that", "SCONJ", "3", "mark"),
        ("2", "he", "he", "PRON", "3", "nsubj"),
        ("3", "lied", "lie", "VERB", "4", "csubj"),
        ("4", "surprised", "surprise", "VERB", "0", "root"),
        ("5", "me", "i", "PRON", "4", "obj"),
        ("6", ".", ".", "PUNCT", "4", "punct"),
    ], at=2, expect="predicate",
       note="A whole clause in the SUBJECT slot: «that he lied» is what surprised me. It is a row, and the matrix's agent slot should hold its NAME (req 33: nesting is naming)."),

    # ── discourse ──
    _c("discourse", "Iguazu is in Argentina :)", [
        ("1", "Iguazu", "iguazu", "PROPN", "4", "nsubj"),
        ("2", "is", "be", "AUX", "4", "cop"),
        ("3", "in", "in", "ADP", "4", "case"),
        ("4", "Argentina", "argentina", "PROPN", "0", "root"),
        ("5", ":)", ":)", "SYM", "4", "discourse"),
    ], at=4, expect=OPEN,
       note="An emoticon carries AFFECT and no proposition. That is the heart's business, not the zip's — and «what a smiley does to a zip» is unruled on purpose."),

    # ── expl ──
    _c("expl", "There is a ghost in the room", [
        ("1", "There", "there", "PRON", "2", "expl"),
        ("2", "is", "be", "VERB", "0", "root"),
        ("3", "a", "a", "DET", "4", "det"),
        ("4", "ghost", "ghost", "NOUN", "2", "nsubj"),
        ("5", "in", "in", "ADP", "7", "case"),
        ("6", "the", "the", "DET", "7", "det"),
        ("7", "room", "room", "NOUN", "2", "obl"),
    ], at=0, expect="structure",
       note="**THE EXPLETIVE CONTRIBUTES NOTHING TO THE PROPOSITION.** «There is a ghost in the room» claims a ghost is in the room; `there` is scaffolding. It is also the sentence req 31 names as the exception that keeps existential `be` CONTENT while copular `be` is glue — and the expletive is what separates them."),

    # ── flat ──
    _c("flat", "Hillary Rodham Clinton", [
        ("1", "Hillary", "hillary", "PROPN", "0", "root"),
        ("2", "Rodham", "rodham", "PROPN", "1", "flat"),
        ("3", "Clinton", "clinton", "PROPN", "1", "flat"),
    ], at=1, expect=OPEN,
       note="«Hillary Rodham Clinton» is ONE name across three tokens. This is E3b's first task by another route, and the station must not mint three individuals."),

    # ── goeswith ──
    _c("goeswith", "They come here with out legal permission", [
        ("1", "They", "they", "PRON", "2", "nsubj"),
        ("2", "come", "come", "VERB", "0", "root"),
        ("3", "here", "here", "ADV", "2", "advmod"),
        ("4", "with", "with", "ADP", "7", "case"),
        ("5", "out", "out", "ADP", "7", "case"),
        ("6", "legal", "legal", "ADJ", "7", "amod"),
        ("7", "permission", "permission", "NOUN", "2", "obl"),
    ], at=4, expect=OPEN,
       note="**STANZA DOES NOT PRODUCE THIS RELATION HERE.** UD publishes `goeswith(with-4, out-5)` — «with out» is a typo for «without» — and stanza reads `out` as a SECOND `case` marker instead. So the station never meets `goeswith` from this provider, and what it meets is the «up beside» shape: two markers on one nominal.",
       annotated=False),

    # ── list ──
    _c("list", "Steve Jones sj@abc.xyz University of Arizona", [
        ("1", "Steve", "steve", "PROPN", "0", "root"),
        ("2", "Jones", "jones", "PROPN", "1", "flat"),
        ("3", "sj@abc.xyz", "sj@abc.xyz", "PROPN", "1", "list"),
        ("4", "University", "university", "PROPN", "1", "list"),
        ("5", "of", "of", "ADP", "6", "case"),
        ("6", "Arizona", "arizona", "PROPN", "4", "nmod"),
    ], at=2, expect=OPEN,
       note="A contact block is not a sentence. UD says so by having a relation for it; what a zip does with it is unruled."),

    # ── nmod ──
    _c("nmod", "a room in the hotel", [
        ("1", "a", "a", "DET", "2", "det"),
        ("2", "room", "room", "NOUN", "0", "root"),
        ("3", "in", "in", "ADP", "5", "case"),
        ("4", "the", "the", "DET", "5", "det"),
        ("5", "hotel", "hotel", "NOUN", "2", "nmod"),
    ], at=2, expect="location",
       note="A nominal modifying a NOUN, with a case marker — and the marker decides, exactly as it does under `obl`. This is the case that proved `nmod` + noun head is not enough to call something a possessor."),

    # ── nummod ──
    _c("nummod", "Sam ate 3 sheep", [
        ("1", "Sam", "sam", "PROPN", "2", "nsubj"),
        ("2", "ate", "eat", "VERB", "0", "root"),
        ("3", "3", "3", "NUM", "4", "nummod"),
        ("4", "sheep", "sheep", "NOUN", "2", "obj"),
    ], at=2, expect="count",
       note="**THE BOX HAS A `count` FIELD AND THIS IS WHAT FILLS IT** (req 26: every nominal box is quantifier · relation · noun, per phrase). A numeral is not a quantifier and not a determination — it is a count, and the station does not read it yet."),

    # ── orphan ──
    _c("orphan", "Marie won gold and Peter bronze", [
        ("1", "Marie", "marie", "PROPN", "2", "nsubj"),
        ("2", "won", "win", "VERB", "0", "root"),
        ("3", "gold", "gold", "NOUN", "2", "obj"),
        ("4", "and", "and", "CCONJ", "5", "cc"),
        ("5", "Peter", "peter", "PROPN", "3", "conj"),
        ("6", "bronze", "bronze", "NOUN", "5", "compound"),
    ], at=5, expect=OPEN,
       note="**STANZA DOES NOT PRODUCE THIS RELATION.** UD publishes `orphan(Peter, bronze)` for the gapped «and Peter bronze»; stanza reads `compound`. Gapping is a real hole and the station will not meet it labelled.",
       annotated=False),

    # ── parataxis ──
    _c("parataxis", "The guy , John said , left early in the morning", [
        ("1", "The", "the", "DET", "2", "det"),
        ("2", "guy", "guy", "NOUN", "7", "nsubj"),
        ("3", ",", ",", "PUNCT", "2", "punct"),
        ("4", "John", "john", "PROPN", "5", "nsubj"),
        ("5", "said", "say", "VERB", "7", "parataxis"),
        ("6", ",", ",", "PUNCT", "2", "punct"),
        ("7", "left", "leave", "VERB", "0", "root"),
        ("8", "early", "early", "ADV", "7", "advmod"),
        ("9", "in", "in", "ADP", "11", "case"),
        ("10", "the", "the", "DET", "11", "det"),
        ("11", "morning", "morning", "NOUN", "7", "obl"),
    ], at=4, expect="predicate",
       note="«The guy, John said, left early» — the report is a row of its own and the matrix is NOT its complement. Same shape as `ccomp` and a different route to it."),

    # ── reparandum ──
    _c("reparandum", "Go to the righ- to the left .", [
        ("1", "Go", "go", "VERB", "0", "root"),
        ("2", "to", "to", "ADP", "4", "case"),
        ("3", "the", "the", "DET", "4", "det"),
        ("4", "righ-", "righ-", "NOUN", "1", "obl"),
        ("5", "to", "to", "ADP", "7", "case"),
        ("6", "the", "the", "DET", "7", "det"),
        ("7", "left", "left", "NOUN", "4", "nmod"),
        ("8", ".", ".", "PUNCT", "1", "punct"),
    ], at=3, expect=OPEN,
       note="**STANZA DOES NOT PRODUCE THIS RELATION.** UD publishes `reparandum(left-7, righ--4)` for the self-correction «the righ- to the left»; stanza reads `nmod`. A disfluency must never become content — `original` keeps it verbatim (req 3) — but the station cannot act on a label it never receives.",
       annotated=False),

    # ── nummod, the WORD form ──
    # UD's second nummod example. It arrived ABSTAINING — the station read digits and not words —
    # and the abstention is what got the dependency admitted the same day. A case that measures a
    # gap is worth as much as one that confirms a feature, and this one did both within the hour.
    _c("nummod", "Sam spent forty dollars", [
        ("1", "Sam", "sam", "PROPN", "2", "nsubj"),
        ("2", "spent", "spend", "VERB", "0", "root"),
        ("3", "forty", "forty", "NUM", "4", "nummod"),
        ("4", "dollars", "dollar", "NOUN", "2", "obj"),
    ], at=2, expect="count",
       note="**THE CASE THAT MEASURED A LIMIT AND THEN CLOSED IT.** It was added abstaining, with "
            "`expect=OPEN`, because converting «forty» needs a roster of atoms plus composition "
            "rules and `word2number` was not a declared dependency. The Captain admitted it the "
            "same day, on `nltk`'s terms — one door — so the case now answers. *It is kept because "
            "a corpus that only holds what already works is a corpus that cannot report a gap.*"),

    # ── root ──
    _c("root", "the cat sleeps", [
        ("1", "the", "the", "DET", "2", "det"),
        ("2", "cat", "cat", "NOUN", "3", "nsubj"),
        ("3", "sleeps", "sleep", "VERB", "0", "root"),
    ], at=2, expect="predicate",
       note="The relation every sentence has, and the one the corpus had reached twenty times without ever NAMING — so the coverage report called it unreached."),

    # ── vocative ──
    _c("vocative", "Guys , take it easy !", [
        ("1", "Guys", "guy", "NOUN", "3", "vocative"),
        ("2", ",", ",", "PUNCT", "3", "punct"),
        ("3", "take", "take", "VERB", "0", "root"),
        ("4", "it", "it", "PRON", "3", "obj"),
        ("5", "easy", "easy", "ADJ", "3", "xcomp"),
        ("6", "!", "!", "PUNCT", "3", "punct"),
    ], at=0, expect="structure",
       note="**E2 RULED THIS IN THE DRILL**: «the vocative is addressing, not content». «Guys, take it easy» is an instruction to a room; the room is not a participant in it."),

    # ── xcomp ──
    _c("xcomp", "We expect them to change their minds", [
        ("1", "We", "we", "PRON", "2", "nsubj"),
        ("2", "expect", "expect", "VERB", "0", "root"),
        ("3", "them", "they", "PRON", "2", "obj"),
        ("4", "to", "to", "PART", "5", "mark"),
        ("5", "change", "change", "VERB", "2", "xcomp"),
        ("6", "their", "their", "PRON", "7", "nmod:poss"),
        ("7", "minds", "mind", "NOUN", "5", "obj"),
    ], at=4, expect=OPEN,
       note="**THE NAMED GAP.** `xcomp` is deliberately absent from `CLAUSE_DEPS`: «you like TO SWIM» is one predication with a controlled subject, and nobody asserts that you swim. So it is not a row — and WHAT it is instead has not been ruled. The zip says so by leaving the verb unplaced."),

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
