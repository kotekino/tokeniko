"""THE CLOSED CLASSES — English's finite grammatical vocabulary, as typed rows.

The standing law of 2026-08-25 put this table here twice over. Test 2 of the FRAME test says a
closed grammatical class «feels like law and is not: it is a contingent fact about one language,
dialect-varying and revisable» — so it is knowledge, and knowledge lives in rows. And the second law
of the same day says what the rows are FOR: **content is defined, structure is compiled**. A content
word earns a dimension in the dictionary; a function word becomes structure in the zip — a role, a
quantifier, a mood, a binding — and never needs a vector at all.

ONE TABLE, TWO CONSUMERS, and it is born in E1 because the first consumer arrived first:

  - E1 EXCLUDES with it. A function word never asks the dictionary a question, so the head of the
    definition digraph's in-degree ranking (`in` at 14,408 in-edges, meaning *inch*; `at` at #19,
    meaning the Lao kip) is out of the seed proposal by PRINCIPLE rather than by a filter that would
    have to keep guessing. `tools/propose_seeds.py` reads these rows.
  - E3 COMPILES with it. It replaces tk1's four hand lists (`_ANAPHORIC_PRONOUNS`,
    `_QUANTIFIER_*`, `_WH_*`, `_RELATIVE_PRONOUNS`) — «a list copied across as written is a rebuild
    that inherited the defect». `compiled` is the column that work fills; it is empty here on
    purpose, because what a form compiles TO is a tkzip question and tkzip is E2.

A CLASS IS NOT A JOB, which is why there are two columns and not one. «Pronoun» is three different
operations — `they` resolves to an ENTITY from context, `everyone` is a QUANTIFIER and refers to
nothing, `who` opens an unbound VARIABLE and a question mood — and a compiler that reads only the
class has to re-derive the job from the form, which is the hand list returning through a side door.
So `word_class` is the traditional class (what a grammar calls it) and `role` is what the compiler
does with it (what the zip gets). One form may hold several rows when it genuinely holds several
jobs: `that` is a demonstrative determiner, a relative pronoun and a complementizer, and collapsing
those three would lose the distinction the parser needs most.

WHAT IS DELIBERATELY NOT HERE, each for a stated reason:

  - NUMERALS. `two`, `seventeen`, `three hundred and four` — productive and infinite, so not a
    closed class at all however finite the words below ten look.
  - INTERJECTIONS (`oh`, `ouch`, `hey`). An open class in practice, and none of them is structure.
  - DERIVED ADVERBS OF FREQUENCY AND DEGREE (`usually`, `normally`, `generally`, `typically`,
    `occasionally`, `rarely`, `slightly`, `very`, `quite`). They behave quantificationally and tk1
    read some of them as quantifiers, but they are formed productively from open-class adjectives —
    `-ly` is a rule, not a roster. The NON-derived quantificational adverbs (`always`, `never`,
    `ever`, `sometimes`, `often`, `seldom`) ARE here, because those are genuinely a closed set.
    This boundary is the one place the table's edge is a judgment call, and it is stated rather
    than hidden so the Captain can move it.
  - PROPER NAMES of any kind — a different problem, already answered in the dictionary by the name
    refusal (`wordnet.is_name_only`).

A FORM IS NOT A READING, and this is the table's live hazard. `like`, `save`, `need`, `must`,
`will`, `can`, `down` and `round` are closed-class forms that ALSO spell open-class words: to like
somebody, a person's will, an empty can. A row here says the FORM has a structural job, never that
the spelling has no content reading — so this table may be used to exclude a form from the seed
PROPOSAL (a starting point, correctable) and must never be used to refuse a word's MEMBERSHIP in
the base (a dimension, not correctable once absent). The refusal that operates on membership is the
name refusal, which is about readings and asks the resource.
"""

from typing import Annotated, Any

from bunnet import Indexed
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from tk2.core.documents import LogicDocument
from tk2.core.mixins import Timestamped


class ClosedClassDoc(LogicDocument, Timestamped):
    """logic (r) — one form, in one of its structural jobs.

    Versioned as a whole, for `DictionaryPolicyDoc`'s reason: a build (or a parse) that read these
    rows must stay able to say WHICH set it read, and a set edited in place makes every earlier
    record a description of something that no longer exists. A change is a new version written
    whole; the old version stays readable beside it.
    """

    #: The version these rows belong to. A reader reads exactly one.
    version: Annotated[int, Indexed()] = Field(ge=1)

    #: The surface form, lower case. Multi-word forms keep their spaces (`each other`, `as long as`,
    #: `in front of`): a complex preposition is one role marker, and splitting it into words would
    #: hand the compiler three role markers that mean nothing apart.
    form: str = Field(min_length=1)

    #: What a grammar calls it: pronoun · determiner · preposition · conjunction · auxiliary ·
    #: modal · particle · clitic · adverb. A string rather than an enum for `reward_source`'s
    #: reason — the roster is a description of a language, and a class that needed a code change to
    #: exist would put the table back in code.
    word_class: str = Field(min_length=1)

    #: THE JOB — what the compiler does with the form, which is the column the zip is built from:
    #: `referential` (resolve to an entity from context) · `quantificational` (a quantifier, not a
    #: referent) · `interrogative` / `relative` (an unbound variable, plus a question mood for the
    #: first) · `role_marker` · `coordinator` / `subordinator` / `complementizer` · `demonstrative`
    #: · `possessive` · `reflexive` / `reciprocal` · `tense_aspect` · `modality` · `negation` ·
    #: `infinitive_marker` · `existential` · `expletive`.
    role: str = Field(min_length=1)

    #: The grammatical features the resolver needs and cannot recover from the spelling: person,
    #: number, gender, case for the referential pronouns; polarity and force for the quantifiers.
    #: A map rather than columns because they are per-class — a preposition has no person — and a
    #: column per feature would be a schema change every time a class arrives that has its own.
    features: dict[str, Any] = Field(default_factory=dict)

    #: E3's column, and empty by construction here. What this form COMPILES to in tkzip — the role
    #: name, the quantifier corner, the mood, the binding. It is a map with no fixed shape yet
    #: because tkzip v2 is E2, and writing a guess into it now would be exactly the load-bearing
    #: knowledge-in-code this table exists to end, merely relocated.
    compiled: dict[str, Any] = Field(default_factory=dict)

    #: Where the row came from — the reference the form was established against, so «is this list
    #: complete?» is answerable by re-walking the source rather than by re-remembering.
    source: str = Field(min_length=1)

    #: Why this row is here, or what is odd about it: the archaic forms, the forms that also spell
    #: open-class words, the judgment calls at the class's edge.
    note: str = ""

    #: Declared order within (version, word_class), so the rows read back grouped as they were
    #: written down — the inventory is an argument about a language and its grouping is part of it.
    position: int = Field(ge=0)

    class Settings:
        name = "closed_classes"
        indexes = [
            # One row per job per form per version, where a job is (class, role): `his` is a
            # possessive determiner AND a possessive pronoun, `that` a demonstrative determiner AND
            # a relative pronoun. Two rows for ONE job would make «what does `that` do here»
            # ambiguous, which is the one thing this table exists to answer.
            IndexModel(
                [
                    ("version", ASCENDING),
                    ("form", ASCENDING),
                    ("word_class", ASCENDING),
                    ("role", ASCENDING),
                ],
                unique=True,
            ),
            IndexModel([("version", ASCENDING), ("role", ASCENDING)]),
        ]
