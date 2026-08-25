"""THE CLOSED CLASSES — the shape of the table, and the three cross-checks that make «exhaustive»
a checkable word rather than a claim.

An incomplete closed class is the failure mode the Captain named at dispatch: the table exists so a
function word is never asked what it means, and one that is missing from it is asked. Completeness
cannot be proven — no enumeration of a language can be — so what is tested here is the next best
thing, three independent sources that must all be covered:

  1. TK1's four hand lists, which this table retires. If a form tk1 needed is missing, the rebuild
     inherited a defect instead of ending one.
  2. NLTK's English stop list, which is a different tradition's answer to nearly the same question.
     Everything it holds is covered but for a residue that is DECLARED here, word by word, with the
     reason each one is not a closed-class row.
  3. The dictionary's own declared seeds — where an overlap is not a failure but a RULING, so the
     test pins the overlap that exists and fails the day another appears unannounced.

Offline throughout: the rows are read from the migration that will write them (`tests/seed.py`'s
argument — what is tested is the seed that will really create the world, not a copy of it), and the
stop list is nltk's, which the dictionary tests already require.
"""

import pytest

from tests.seed import closed_class_rows, closed_class_forms, policy_rows
from tk2.dictionary import policy


@pytest.fixture(scope="module")
def rows():
    return closed_class_rows()


@pytest.fixture(scope="module")
def by_form(rows):
    """Every job each form holds, which is the question every consumer asks."""
    index: dict[str, set[str]] = {}
    for row in rows:
        index.setdefault(row["form"], set()).add(row["role"])
    return index


# ------------------------------------------------------------------------------------------------
# the shape
# ------------------------------------------------------------------------------------------------


def test_every_row_validates_against_the_model(rows):
    """The migration writer will validate these; failing here is failing early and by name."""
    from tk2.core.models import ClosedClassDoc
    from tk2.datatier.migration_writer import shape_of

    shape = shape_of(ClosedClassDoc)
    for row in rows:
        shape.model_validate(row)


def test_one_row_per_job(rows):
    """(form, class, role) is unique — the table's whole promise is that «what does `that` do here»
    has one answer per job, and two rows for one job would be two answers."""
    seen = set()
    for row in rows:
        job = (row["form"], row["word_class"], row["role"])
        assert job not in seen, f"{job} declared twice"
        seen.add(job)


def test_a_pronoun_is_three_jobs(by_form):
    """The reason the table is typed at all. Each of these is a different operation on the zip, and
    a compiler that read only the class would have to re-derive the job from the form."""
    assert "referential" in by_form["they"]
    assert "quantificational" in by_form["everyone"]
    assert "interrogative" in by_form["who"]
    assert "relative" in by_form["who"]
    # `that` is the extreme case: a demonstrative, a relative pronoun and a complementizer.
    assert by_form["that"] == {"demonstrative", "relative", "subordinator"}


def test_the_forms_are_lower_case_and_stripped(rows):
    for row in rows:
        assert row["form"] == row["form"].lower().strip(), row["form"]


def test_every_row_names_where_it_came_from(rows):
    """«Is this complete?» is answered by re-walking a named source, never by re-remembering."""
    for row in rows:
        assert row["source"].strip(), row


def test_the_compiled_meaning_is_left_for_E3(rows):
    """E1 needs the roster; what a form compiles TO is a tkzip question and tkzip is E2. A guess
    written here now would be the hand list this table retires, merely relocated."""
    assert all(row["compiled"] == {} for row in rows)


def test_the_referential_pronouns_carry_what_a_resolver_needs(rows):
    """`them` resolves to an entity, and person/number are how the resolver picks which."""
    referential = [r for r in rows if r["role"] == "referential" and r["word_class"] == "pronoun"]
    assert referential
    for row in referential:
        assert "person" in row["features"], row["form"]
        assert "number" in row["features"], row["form"]


def test_the_multiword_forms_are_not_in_the_exclusion_set(rows):
    """`FORMS` is what E1 excludes with, and the digraph's nodes are WORDS. A multi-word row is for
    E3 and can never match a node, so it must not silently look like one."""
    forms = set(closed_class_forms())
    assert all(" " not in form for form in forms)
    assert "each other" not in forms
    assert {r["form"] for r in rows} - forms == {r["form"] for r in rows if " " in r["form"]}


# ------------------------------------------------------------------------------------------------
# cross-check 1 — tk1's hand lists, which this table retires
# ------------------------------------------------------------------------------------------------

#: Read off `tokeniko-tk1/lib/llc/constants.py` (2026-08-25). Copied INTO the test rather than
#: imported, because tk1 is another package with another environment — and because the point is
#: that this table can replace them, which stays true whatever tk1 does next.
TK1_LISTS = {
    "_RELATIVE_PRONOUNS": ("who", "whom", "which", "that", "whose"),
    "_ANAPHORIC_PRONOUNS": ("he", "she", "it", "they", "him", "her", "them"),
    "_REFLEXIVE_PRONOUNS": ("itself", "himself", "herself", "themselves", "themself", "oneself"),
    "_PRONOUNS_BASE_ANCHORS": ("i", "me", "my", "mine", "myself", "you", "your", "yours",
                               "yourself", "yourselves"),
    "_QUANTIFIER_UNIVERSAL": ("all", "every", "each", "everything", "everyone", "everybody"),
    "_QUANTIFIER_EXISTENTIAL": ("some", "any", "several", "something", "someone", "somebody"),
    "_QUANTIFIER_INDEFINITE": ("a", "an"),
    "_QUANTIFIER_NEGATIVE": ("no", "none", "neither", "nothing", "nobody"),
    "_QUANTIFIER_DEFINITE": ("the", "this", "that", "these", "those"),
    "_NEGATIVE_QUANTIFIERS": ("nobody", "no one", "nothing", "none"),
    "_WH": ("who", "whom", "which", "whose", "what", "where", "when", "how", "why"),
    "_NEGATION_MARKERS": ("not", "no", "never", "n't", "nor", "neither"),
    "_ADV_QUANTIFIERS": ("always", "sometimes", "never"),
}


@pytest.mark.parametrize("name,forms", sorted(TK1_LISTS.items()))
def test_tk1s_hand_list_is_covered(name, forms, by_form):
    """E3 may not port a list as written; it may only find every form of it here."""
    missing = [form for form in forms if form not in by_form]
    assert not missing, f"{name} is not covered: {missing}"


def test_tk1s_dialect_spellings_are_the_parsers_problem_not_the_tables(by_form):
    """`no-one` and `noone` are spellings of `no one`, and normalisation is a parser's job. The
    table holds the FORM, once — a roster that also carried every misspelling would be a roster
    nobody could ever call complete."""
    assert "no one" in by_form
    assert "no-one" not in by_form


# ------------------------------------------------------------------------------------------------
# cross-check 2 — nltk's English stop list, and the declared residue
# ------------------------------------------------------------------------------------------------

#: What nltk's stop list holds that this table does not, each with its reason. Written out rather
#: than computed, because every entry is a JUDGMENT and a computed exemption would let a real hole
#: hide inside a pattern.
#:
#: Two kinds, and neither is a closed class:
#:   - FRAGMENTS. nltk's list is de-apostrophised, so it carries `aren`, `didn`, `won`, `ma` and the
#:     bare letters `d ll m o re s t ve y`. They are halves of contractions, and the halves that
#:     ARE structure (`n't`, `'s`, `'re`, `'ve`, `'ll`, `'d`, `'m`) are rows already.
#:   - CONTENT AND DEGREE WORDS. `again`, `further`, `just`, `only`, `too`, `very` are focus and
#:     degree adverbs — the declared edge of the table (see the model's docstring: `-ly` and the
#:     degree adverbs are out because they are productive, not because they are unimportant).
#:     `own` and `same` are adjectives with meanings, and `same` is a DICTIONARY SEED — the
#:     Captain's identity family names it. That one is the sharpest illustration the cross-check
#:     produces: a stop list is a statement about frequency in text, never about what is a word.
STOPWORD_RESIDUE = {
    "fragments": (
        "ain", "aren", "couldn", "d", "didn", "doesn", "don", "hadn", "hasn", "haven", "isn",
        "ll", "m", "ma", "mightn", "mustn", "needn", "o", "re", "s", "shan", "shouldn", "t",
        "ve", "wasn", "weren", "won", "wouldn", "y",
    ),
    "content and degree": ("again", "further", "just", "only", "own", "same", "too", "very"),
}


def test_the_stop_list_is_covered_but_for_a_declared_residue(by_form):
    """A second tradition's answer to nearly this question, walked whole.

    Contractions spelled with an apostrophe (`aren't`, `you've`) are skipped: they are an auxiliary
    plus a clitic, both of which are rows, and a table that also listed every contraction would be
    listing the parser's work.
    """
    from nltk.corpus import stopwords

    declared = {word for group in STOPWORD_RESIDUE.values() for word in group}
    uncovered = sorted(
        word
        for word in stopwords.words("english")
        if "'" not in word and word not in by_form and word not in declared
    )
    assert not uncovered, (
        f"nltk knows these as function words and the table does not: {uncovered}. "
        f"Either they are rows, or they belong in STOPWORD_RESIDUE with a reason."
    )


def test_the_residue_is_really_absent(by_form):
    """The other direction, so the residue cannot quietly become a list of rows that also exist —
    which would make the exemption above vacuous and the coverage claim meaningless."""
    for reason, words in STOPWORD_RESIDUE.items():
        for word in words:
            assert word not in by_form, f"{word} is a row; it should leave the {reason!r} residue"


# ------------------------------------------------------------------------------------------------
# cross-check 3 — the overlap with the dictionary's seeds, which is a ruling and not a bug
# ------------------------------------------------------------------------------------------------

#: The forms that are BOTH a closed-class row and a declared dictionary seed, as the policy stands
#: at version 1. `me`, `you`, `not` and `be` are the four the second standing law removes — they are
#: structure, and the seed proposal drops them. `must` and `need` are the two that REMAIN, and they
#: are the open question this table surfaced: a modal auxiliary whose spelling is also a volitional
#: verb the requirement 8 families name on purpose.
#:
#: Pinned so that a policy version 2 which adds a new overlap has to say so here, in the diff,
#: instead of arriving silently.
KNOWN_OVERLAP = {"be", "me", "must", "need", "not", "you"}


def test_the_overlap_with_the_declared_seeds_is_the_known_one():
    seeds = set(policy.seeds_from_rows(policy_rows()))
    assert seeds & set(closed_class_forms()) == KNOWN_OVERLAP


def test_the_bar_names_one_closed_class_form_and_it_is_need():
    """Requirement 12 makes every bar word a seed, so a bar word that is also a function word is a
    third witness to the same open question — and here it is `need` again, from the pair
    `want.v ~ need.v NEAR`. The bar means the VERB; the table means the semi-modal («he need not
    go»). One spelling, two readings, and nothing here rules on it."""
    from tk2.dictionary.config import bar_words

    assert set(bar_words(policy.snapshot_bar())) & set(closed_class_forms()) == {"need"}
