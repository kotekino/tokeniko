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

#: The three PTB tags the decompiler speaks. `VBZ` is the third singular present — everywhere else
#: the present IS the lemma, which is a fact about English rather than a gap in the data. `VBD` and
#: `VBN` arrived on 2026-09-20 with the theatre and the passive: a sentence that was heard in the
#: past and spoken back in the present is not the same sentence.
PRESENT = "VBZ"
PAST = "VBD"
PARTICIPLE = "VBN"

SIBILANTS = ("s", "x", "z", "ch", "sh")
VOWELS = "aeiou"
#: For COUNTING syllables `y` is sometimes a vowel — «cypher» and «hyphen» are two syllables and
#: neither doubles its final consonant — and sometimes not: «crayon» and «kayak» are two syllables
#: BECAUSE the `y` between their vowels is a consonant. `_syllables` decides it per letter. It is
#: kept out of `VOWELS` because the `-ies` and `-ied` rules ask a different question about `y`.
#: A final consonant doubles before a vowel suffix in a one-syllable CVC word — «stop» → «stopped».
#: `w`, `x` and `y` never double, because they are not consonants in that position.
NEVER_DOUBLE = "wxy"


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


def _syllables(word: str) -> int:
    """Vowel GROUPS, which is as close to a syllable as spelling gets — and close enough: the rule
    below only asks whether a word is one syllable, and no English one-syllable word has two."""
    groups, inside, previous = 0, False, ""
    for letter in word:
        # `y` is a vowel after a consonant («cypher», «gym») and a CONSONANT between vowels, which
        # is what splits «cray|on» and «kay|ak» into the two syllables they are.
        vowel = letter in VOWELS or (letter == "y" and previous not in VOWELS)
        if vowel:
            groups += 1 if not inside else 0
        inside, previous = vowel, letter
    return max(groups, 1)


def _doubles(word: str) -> bool:
    """Does the final consonant double before `-ed` / `-ing`?

    ONE SYLLABLE, consonant-vowel-consonant — «stop», «beg», «plan». The polysyllables that also
    double do so because their last syllable is STRESSED («prefer», «abet», «occur»), and stress is
    not in the spelling, so those are roster rows rather than a rule that guesses.
    """
    return (len(word) >= 3 and _syllables(word) == 1
            and word[-1] not in VOWELS and word[-1] not in NEVER_DOUBLE
            and word[-2] in VOWELS and word[-3] not in VOWELS)


def past_tense_rule(lemma: str) -> str:
    """The regular past: `-ed`, and the three spellings English puts around it.

    Identical to the past participle for every regular verb, which is why one rule serves both and
    the roster is where they part company — «write» → «wrote» but «written».
    """
    word = (lemma or "").strip().lower()
    if not word:
        return ""
    if word.endswith("e"):
        return word + "d"
    if word.endswith("y") and word[-2:-1] not in VOWELS:
        return word[:-1] + "ied"
    if word.endswith("c") and word[-2:-1] in VOWELS:
        # «panic» → «panicked». The `k` keeps the `c` hard before a front vowel, which is spelling
        # and not an irregularity — «paniced» would be read «panissed». Only after a VOWEL: «sync»
        # and «zinc» have a consonant there and take a plain `-ed`.
        return word + "ked"
    if _doubles(word):
        return word + word[-1] + "ed"
    return word + "ed"


def participle_rule(lemma: str) -> str:
    """The regular past participle — the same word as the past tense, for every REGULAR verb.

    Stated as its own function rather than as an alias because the two are different QUESTIONS that
    happen to share an answer: the roster answers them separately, and «I have written» is exactly
    where that matters.
    """
    return past_tense_rule(lemma)


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
        rule = {PRESENT: present_tense_rule, PAST: past_tense_rule,
                PARTICIPLE: participle_rule}.get(tag)
        return rule(word) if rule is not None else word


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
