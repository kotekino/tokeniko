"""THE FORM A WORD TAKES — the spelling rule, and the roster of words it gets wrong (req 9).

**THE SPLIT IS THE POINT, AND IT IS THE SAME ONE THE STATION DRAWS EVERYWHERE.** Adding `-s`, `-es`
after a sibilant and `-ies` after a consonant-plus-`y` is ORTHOGRAPHY — frame, for the same reason
punctuation is frame: the compiler reads it as structure and never as vocabulary, so the decompiler
writes it the same way. WHICH WORDS the rule gets wrong is a revisable fact about English, so the
exceptions are ROWS (`db/0022`, `language_inflections`) and this file only runs them.

**MEASURED, not assumed**: over all 20,364 verb lemmas WordNet holds the rule is right for every one
but 21 (2026-09-19). A rule with a 0.1% exception roster is a rule; a rule needing a thousand rows
would have been a lookup table wearing a rule's clothes, and the measurement is what tells them
apart.

**NO LIBRARY SHIPS.** `lemminflect` generated the roster offline — the way WordNet builds the base —
and stayed out of the closed dependency list, because importing it loads spacy and torch and those
live behind the skeleton adapter by design.
"""

from __future__ import annotations

from dataclasses import dataclass

#: The third person singular present. The only tag the decompiler needs while it renders the present
#: — the theatre is not read yet, and a past tense it cannot place is a tense it must not speak.
PRESENT = "VBZ"

SIBILANTS = ("s", "x", "z", "ch", "sh")
VOWELS = "aeiou"


def present_tense_rule(lemma: str) -> str:
    """The regular third person singular: the orthography, and nothing else.

    `-o` takes `-s` here, which is the majority side of a genuinely split class — *demos*, *discos*,
    *solos*, *tangos* against *goes*, *does*, *echoes*. The minority is in the roster, and putting
    the split this way round makes the roster fourteen rows instead of several hundred.
    """
    word = (lemma or "").strip().lower()
    if not word:
        return ""
    if word.endswith("y") and word[-2:-1] not in VOWELS:
        return word[:-1] + "ies"
    if word.endswith(SIBILANTS):
        return word + "es"
    return word + "s"


@dataclass(frozen=True, slots=True)
class Inflections:
    """The roster as it stands: `(lemma, tag) -> the form`, and the rule for everything else."""

    forms: dict
    source: str = "(unnamed)"

    @classmethod
    def from_rows(cls, rows, source: str = "(unnamed)") -> "Inflections":
        rows = list(rows)
        if rows:
            newest = max(r.get("version", 1) for r in rows)
            rows = [r for r in rows if r.get("version", 1) == newest]
        return cls({(r["lemma"], r["tag"]): r["form"] for r in rows}, source)

    def of(self, lemma: str, tag: str = PRESENT) -> str:
        """The word in that form — the roster where it speaks, the rule where it does not.

        There is no abstention here and there should not be: a verb the roster has never heard of is
        not an unknown, it is a REGULAR verb, and that is what the measurement over twenty thousand
        lemmas establishes. The place that abstains is the decompiler, and it abstains about
        MEANINGS, not about spellings.
        """
        word = (lemma or "").strip().lower()
        found = self.forms.get((word, tag))
        if found is not None:
            return found
        return present_tense_rule(word) if tag == PRESENT else word


def standing_inflections(db_name: str | None = None) -> Inflections:
    """The roster AS IT STANDS — live rows if a database is named, else the newest migration's.

    `standing_closed_classes`'s shape and reason: a measurement must be reproducible with no body.
    """
    if db_name:
        from tk2.core.models import InflectionDoc
        from tk2.datatier.client import database

        rows = list(database(db_name)[InflectionDoc.Settings.name].find({}, {"_id": 0}))
        if rows:
            return Inflections.from_rows(rows, f"{db_name}.{InflectionDoc.Settings.name}")

    from tk2.datatier.policy_source import newest_migration_declaring

    found, module = newest_migration_declaring("INFLECTION_ROWS")
    return Inflections.from_rows(module.INFLECTION_ROWS, f"db/{found.label} (not applied)")
