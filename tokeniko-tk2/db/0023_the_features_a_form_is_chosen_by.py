"""0023 — closed classes v12: **the features a form is CHOSEN by** (parser-compiler req 9).

**THE SECOND THING THE DECOMPILER ASKED THE ROWS, AND IT IS NOT THE SAME QUESTION AS `db/0021`'S.**
The `spoken` flag answers *«this MEANING has several forms — which one do we say?»*, and it is keyed
on the meaning, because that is what it is about. Three of the choices the second slice ran into are
not about meaning at all:

    «my» or «mine»          same meaning, and the difference is WHERE IT STANDS in the phrase
    «I» or «me» or «my»     same referent, and the difference is the SLOT it occupies
    «am» or «are» or «is»   same verb, and the difference is WHO THE SUBJECT IS

A flag keyed on the meaning cannot separate any of them — all seventeen possessives compile to the
same three words — so the flag was the wrong instrument and a second one is needed. **These are
features of the FORM, and the table already has a `features` column holding exactly this kind of
fact** (`person`, `number`, `gender`, `case` have been there since v1). This migration finishes it
for the cells the decompiler reaches, and nothing here is a new kind of knowledge: it is the
paradigm the rows were always describing, written down where it can be read in both directions.

**WHAT IS ADDED, AND WHY EACH:**

    use: determiner|pronoun   the seventeen possessives. «my cat» and «the cat is mine» are the two
                              positions English has, one word each, and no row said which was which
    elsewhere: true           `are` and `'re`. English's copula has three present cells and one of
                              them is the DEFAULT — not «person 2 and plural» listed out, because
                              that is four rows' worth of feature to say «everything the other two
                              did not take». A paradigm with a default cell is how the language
                              actually works
    person/number on am, is   the two cells that are not the default
    tense: past / finite      `was`, `were`, `be`, `been`, `being` — so that a reader asking for the
                              PRESENT never reaches them by accident
    archaic: true             `thou` · `thee` · `ye` · `thy` · `thine`. They are in the table because
                              the station must READ them; they must never be SPOKEN, and until now
                              nothing said so — which is why «you» had three nominative candidates
    selective: true           the interrogative `which`. A selection question needs a set to select
                              from, and an OPEN box does not give one — so it is not a candidate for
                              a bare question word, and «who» stops being ambiguous with it

**AND TWO CHANGES TO `db/0021`'S TEN:**

    - «although» LOSES THE FLAG. Its meaning is `and` asserting both halves, which is exactly «and»'s
      meaning, and both carried the flag — legal under v11's check, because the check keyed on (role,
      compiled) and they have different roles. The decompiler does not: it asks for a connective by
      OPERATOR, and got two answers, so **the commonest join in the corpus could not be spoken at
      all.** The concession «although» carries is not in the zip; saying it would add content the
      thought does not hold, and `and` is the form that adds nothing. *The check below is widened to
      the key the decompiler actually uses, so this cannot recur.*
    - «will» GAINS IT. English inflects the past and not the future, so the decompiler needs a WORD
      for a thought set after the utterance, and three carry that meaning — `will` · `shall` · `'ll`.
      `shall` is first-person and formal and `'ll` is a clitic, so `will` is the plain one.
    - «can» and «must» GAIN IT. The modals were outside `db/0021` because no decompiled sentence had
      reached a modality row yet; five forms mean possibility and four mean necessity, and the two
      chosen are the plain ones — `may` is also permission, `should` and `ought` are ruled obligation
      by their own features, `need` and `dare` are polarity-bound, `could` and `might` are past.

**Nothing else moves**: no form arrives or leaves, `compiled` is untouched, and D's gloss-word
exclusion set is therefore identical.

**Written by the QM on 2026-09-20. The curation is the QM's and is listed here so it can be argued
with, as `db/0021`'s and `db/0022`'s were.**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, ClosedClassDoc
from tk2.migrations import ensure_collections

VERSION = 12

#: `(role, form)` — the form that SPEAKS each meaning carried by more than one form. `db/0021`'s ten,
#: minus the one that collided with another role's, plus the two modals the second slice reached.
SPOKEN = (
    ("negation", "not"),
    ("quantificational", "every"),
    ("quantificational", "some"),
    ("quantificational", "no"),
    ("coordinator", "and"),
    ("subordinator", "because"),
    ("subordinator", "if"),
    ("subordinator", "when"),
    ("determination", "a"),
    ("modality", "can"),
    ("modality", "must"),
    ("tense_aspect", "will"),
)

#: `(role, form, position) -> the features to merge in`. `position` disambiguates the rows that share
#: a form within one role — `his` and `its` are each written twice, once as a determiner and once as
#: a pronoun, and the table has always told them apart by nothing but their order.
FEATURES = {
    # -- the possessive's two positions ---------------------------------------------------------
    ("possessive", "my", 0): {"use": "determiner"},
    ("possessive", "our", 1): {"use": "determiner"},
    ("possessive", "your", 2): {"use": "determiner"},
    ("possessive", "his", 3): {"use": "determiner"},
    ("possessive", "her", 4): {"use": "determiner"},
    ("possessive", "its", 5): {"use": "determiner"},
    ("possessive", "their", 6): {"use": "determiner"},
    ("possessive", "thy", 7): {"use": "determiner", "archaic": True},
    ("possessive", "whose", 8): {"use": "determiner"},
    ("possessive", "mine", 16): {"use": "pronoun"},
    ("possessive", "ours", 17): {"use": "pronoun"},
    ("possessive", "yours", 18): {"use": "pronoun"},
    ("possessive", "his", 19): {"use": "pronoun"},
    ("possessive", "hers", 20): {"use": "pronoun"},
    ("possessive", "its", 21): {"use": "pronoun"},
    ("possessive", "theirs", 22): {"use": "pronoun"},
    ("possessive", "thine", 23): {"use": "pronoun", "archaic": True},
    # -- the pronouns that must be read and never said -------------------------------------------
    ("referential", "thou", 13): {"archaic": True},
    ("referential", "thee", 14): {"archaic": True},
    ("referential", "ye", 15): {"archaic": True},
    # -- the copula's paradigm, which is the one English verb with three present cells -----------
    ("tense_aspect", "am", 1): {"lemma": "be", "tense": "present", "person": 1, "number": "sg"},
    ("tense_aspect", "is", 2): {"lemma": "be", "tense": "present", "person": 3, "number": "sg"},
    ("tense_aspect", "are", 3): {"lemma": "be", "tense": "present", "elsewhere": True},
    ("tense_aspect", "'m", 6): {"lemma": "be", "tense": "present", "person": 1, "number": "sg",
                                "clitic": True},
    ("tense_aspect", "'re", 2): {"lemma": "be", "tense": "present", "elsewhere": True,
                                 "clitic": True},
    ("tense_aspect", "was", 4): {"lemma": "be", "tense": "past", "person": 3, "number": "sg"},
    ("tense_aspect", "were", 5): {"lemma": "be", "tense": "past", "elsewhere": True},
    ("tense_aspect", "be", 0): {"lemma": "be", "finite": False},
    ("tense_aspect", "been", 6): {"lemma": "be", "finite": False},
    ("tense_aspect", "being", 7): {"lemma": "be", "finite": False},
    # -- the question word that needs a set to choose from ----------------------------------------
    ("interrogative", "which", 53): {"selective": True},
}


def build_rows(previous: list[dict]) -> list[dict]:
    out = []
    for row in previous:
        if row.get("version") != 11:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = VERSION
        new["spoken"] = (row["role"], row["form"]) in SPOKEN
        extra = FEATURES.get((row["role"], row["form"], row.get("position")))
        if extra:
            new["features"] = {**(row.get("features") or {}), **extra}
        out.append(new)
    return out


def _previous_rows():
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 21), None)
    if found is None:
        raise RuntimeError("0021 is gone — it holds the version this one extends")
    return found.load().CLOSED_CLASS_ROWS


CLOSED_CLASS_ROWS = build_rows(_previous_rows())

#: Unchanged, and checked — this migration edits two columns and adds no form.
CLOSED_CLASS_FORMS = tuple(
    sorted({row["form"] for row in CLOSED_CLASS_ROWS if " " not in row["form"]})
)


def _check() -> None:
    import json

    before = _previous_rows()
    if {r["form"] for r in before if " " not in r["form"]} != set(CLOSED_CLASS_FORMS):
        raise ValueError("THE EXCLUSION SET MOVED — D's vocabulary filter would change with it")
    if len(before) != len(CLOSED_CLASS_ROWS):
        raise ValueError("a row was added or lost — this migration only edits columns")
    if any(row.get("compiled") != was.get("compiled")
           for row, was in zip(CLOSED_CLASS_ROWS, before)):
        raise ValueError("a MEANING moved — this migration is about forms, not about meanings")

    spoken = [r for r in CLOSED_CLASS_ROWS if r["spoken"]]
    if len(spoken) != len(SPOKEN):
        raise ValueError(f"{len(SPOKEN)} meanings were chosen and {len(spoken)} rows carry the flag "
                         f"— a (role, form) pair in SPOKEN names no row")

    placed = {(row["role"], row["form"], row.get("position")) for row in CLOSED_CLASS_ROWS}
    missing = [key for key in FEATURES if key not in placed]
    if missing:
        raise ValueError(f"{missing} name no row — a feature written for a form that is not there")

    # **THE INVARIANT `db/0021` STATED, WIDENED TO THE KEY THE DECOMPILER ACTUALLY USES.** v11 asked
    # for one voice per (role, meaning) and got two voices for one MEANING, because a coordinator and
    # a subordinator are two roles saying the same thing. The decompiler chooses a connective by what
    # it means, so that is what must be unique — and the collision cost the corpus its commonest join.
    for scope in ("role", "meaning"):
        seen: dict[tuple, str] = {}
        for row in spoken:
            compiled = json.dumps(row.get("compiled") or {}, sort_keys=True)
            key = (row["role"], compiled) if scope == "role" else (compiled,)
            if key in seen:
                raise ValueError(f"{row['form']!r} and {seen[key]!r} both claim to speak the same "
                                 f"{scope} — the decompiler would have to choose, and it must not")
            seen[key] = row["form"]

    # And a flag on a meaning only ONE form carries would be noise: the table already answers there.
    by_meaning: dict[tuple, int] = {}
    for row in CLOSED_CLASS_ROWS:
        if not (row.get("compiled") or {}):
            continue
        key = (row["role"], json.dumps(row["compiled"], sort_keys=True))
        by_meaning[key] = by_meaning.get(key, 0) + 1
    for row in spoken:
        key = (row["role"], json.dumps(row.get("compiled") or {}, sort_keys=True))
        if by_meaning.get(key, 0) < 2:
            raise ValueError(f"{row['form']!r} is the only form with its meaning — it needs no flag")

    # **ONE DEFAULT CELL PER PARADIGM.** Two `elsewhere` rows in one tense is a paradigm that cannot
    # be read: the reader would be back to choosing, which is the whole thing this file is against.
    defaults: dict[tuple, str] = {}
    for row in CLOSED_CLASS_ROWS:
        features = row.get("features") or {}
        if not features.get("elsewhere"):
            continue
        key = (features.get("lemma"), features.get("tense"), bool(features.get("clitic")))
        if key in defaults:
            raise ValueError(f"{row['form']!r} and {defaults[key]!r} are both the default cell of "
                             f"{key[0]} {key[1]}")
        defaults[key] = row["form"]


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(ClosedClassDoc, CLOSED_CLASS_ROWS)
