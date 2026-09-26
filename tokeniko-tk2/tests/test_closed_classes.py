"""The closed classes learn what they compile to — `db/0008`, version 2.

The column was empty by construction until tkzip froze. What this file holds is that it is now full
AND that everything in it is a value the frozen format actually has: a `compiled` map naming a role,
an operator, a quantity or a modality that `tk2.tkzip.schema` does not define would be knowledge
about a format nobody implements.
"""

from collections import Counter

import pytest

from tk2.migrations import discover
from tk2.tkzip.schema import Determination, Modality, Operator, Quantity, Role


def migration(number: int):
    found = next((m for m in discover() if m.number == number), None)
    if found is None:
        pytest.skip(f"migration {number} is not present")
    return found.load()


@pytest.fixture(scope="module")
def rows():
    """THE NEWEST version — v3 (`db/0009`). The gate corrected three mappings the afternoon v2
    landed, and a suite pinned to v2 would hold the station to the older table for ever."""
    return migration(9).CLOSED_CLASS_ROWS


@pytest.fixture(scope="module")
def v2():
    return migration(8).CLOSED_CLASS_ROWS


@pytest.fixture(scope="module")
def v1():
    return migration(1).CLOSED_CLASS_ROWS


# ------------------------------------------------------------------------------------------------
# the column is full, and full of values the format has
# ------------------------------------------------------------------------------------------------


def test_every_row_compiles_to_something(rows):
    """«Empty» was the v1 state and the whole point of v2. A row with nothing in `compiled` is a
    form the station would meet and have no instruction for."""
    empty = [r["form"] for r in rows if not r["compiled"]]

    assert empty == [], f"{len(empty)} rows still compile to nothing: {empty[:12]}"
    assert len(rows) == 383, "v2 carries every v1 row forward, no more and no fewer"


def test_no_compiled_map_hides_a_None(rows):
    """A key present with a `None` value is worse than an absent key: it reads as «answered» to
    anything that checks for the key. The three articles and three clitics were exactly this."""
    optional = {"binds", "aspect", "tense"}
    holes = [(r["form"], r["compiled"]) for r in rows
             if any(v is None for k, v in r["compiled"].items() if k not in optional)]

    assert holes == [], f"{len(holes)} compiled maps carry a None: {holes[:6]}"


@pytest.mark.parametrize("key, enum", [
    ("operator", Operator), ("quantity", Quantity),
    ("modality", Modality), ("determination", Determination),
])
def test_named_values_exist_in_the_frozen_schema(rows, key, enum):
    allowed = {member.value for member in enum}
    wrong = [(r["form"], r["compiled"][key]) for r in rows
             if r["compiled"].get(key) is not None and r["compiled"][key] not in allowed]

    assert wrong == [], f"{key} values the format does not define: {wrong}"


def test_every_marked_role_is_one_of_the_eighteen(rows):
    allowed = {member.value for member in Role}
    wrong = [(r["form"], r["compiled"]["roles"]) for r in rows
             if r["compiled"].get("kind") == "box" and set(r["compiled"]["roles"]) - allowed]

    assert wrong == [], f"boxes naming a role tkzip has not got: {wrong}"


# ------------------------------------------------------------------------------------------------
# the re-typings — each one a defect v1 could not have avoided, and each one named
# ------------------------------------------------------------------------------------------------


def test_the_causal_markers_became_a_JOIN_not_a_box(rows):
    """E2's collapse, arriving where it was predicted: there is no CAUSE relation, because a cause
    is what implies its effect. «because of» marks no box — it joins two rows."""
    because = next(r for r in rows if r["form"] == "because of")

    assert because["role"] == "causal_marker"
    assert because["compiled"]["kind"] == "join"
    assert because["compiled"]["operator"] == Operator.IMPLY.value
    assert because["compiled"]["antecedent"] == "marked"
    assert because["compiled"]["was"] == "role_marker", "the row says what it used to be"


def test_the_concessive_loss_is_RECORDED_rather_than_hidden(rows):
    """«Despite the rain I went out» is truth-functionally «rain AND went out» — the defeated
    expectation is not truth-functional and `JoinRow` has no marker field to carry it. Compiling to
    AND is a LOSS, and the row must say so or the figurative layer will never find its own cases."""
    despite = next(r for r in rows if r["form"] == "despite")

    assert despite["compiled"]["operator"] == Operator.AND.value
    assert despite["compiled"]["pragmatic"] == "concessive"
    assert despite["compiled"]["lossy"] is True


def test_the_possessive_marks_a_POSSESSOR_and_not_glue(rows):
    """CORRECTED AT v3 by the UD gate. UD analyses «the Chair 's office» as case + nmod and pairs it
    explicitly with «the office OF the Chair» — the same relation in two spellings. v2 compiled `'s`
    to structure, so one of those spellings threw the possessor away. tkzip keeps the possessor
    INSIDE the record as Box.relation (req 26)."""
    clitic = next(r for r in rows if r["form"] == "'s" and r["role"] == "genitive")

    assert clitic["compiled"]["kind"] == "field"
    assert clitic["compiled"]["field"] == "relation"
    assert clitic["compiled"]["was"] == "structure", "the row says what it used to be"


def test_plain_copular_be_is_STRUCTURE_and_the_row_names_what_chooses(rows):
    """Req 31 and the Captain's first draft verbatim: «the cat is cute» is cat + cute, NO VERB. v2
    typed every form of `be` as theatre. One row cannot tell copular from auxiliary from existential
    `be` — the dependency can, so the row carries both readings and names the relation that picks."""
    is_ = next(r for r in rows if r["form"] == "is")

    assert is_["compiled"]["kind"] == "structure"
    assert is_["compiled"]["when"] == "cop", "and it says WHICH dependency makes it glue"
    assert is_["compiled"]["otherwise"] == "theatre"
    assert all(next(r for r in rows if r["form"] == f)["compiled"]["when"] == "cop"
               for f in ("be", "am", "are", "was", "were", "been", "being"))


def test_v3_changes_ELEVEN_rows_and_moves_no_form(rows, v2):
    """The migration's whole claim, checked: three mappings corrected, nothing else touched, and —
    load-bearing — the single-word FORMS are identical. That set is the dictionary's gloss-word
    exclusion: if it moved, D would change and the sealed base with it, under a policy nobody
    re-ruled."""
    before = {(r["form"], r["word_class"], r["position"]): r for r in v2}
    after = {(r["form"], r["word_class"], r["position"]): r for r in rows}

    assert set(before) == set(after)
    changed = {k[0] for k in after if before[k]["compiled"] != after[k]["compiled"]}
    assert changed == {"'s", "'m", "'re", "be", "is", "am", "are", "was", "were", "been", "being"}
    assert not [k for k in after if before[k]["role"] != after[k]["role"]], "no row was re-typed"

    forms = lambda rs: sorted({r["form"] for r in rs if " " not in r["form"]})
    assert forms(v2) == forms(rows), "the exclusion set must not move"


def test_the_articles_are_DETERMINATION_and_not_quantity(rows):
    """v1's own features said «force: definite / indefinite» and the row was still typed
    quantificational. tkzip keeps determination as its own field beside quantity — «the cat» and
    «a cat» differ in determination and are both singular."""
    the, a = (next(r for r in rows if r["form"] == f) for f in ("the", "a"))

    assert the["role"] == a["role"] == "determination"
    assert the["compiled"]["determination"] == Determination.DEFINITE.value
    assert a["compiled"]["determination"] == Determination.INDEFINITE.value
    assert all(r["form"] not in ("a", "an", "the")
               for r in rows if r["compiled"].get("kind") == "quantifier")


def test_the_future_is_a_THEATRE_and_never_a_modality(rows):
    """tkzip's Modality is necessity / possibility, frozen — E2 ruled a forecast is a future
    THEATRE. v1 typed `will` and `'ll` as modality with «modality: future», which is a modal
    operator the format does not have."""
    will, ll = (next(r for r in rows if r["form"] == f) for f in ("will", "'ll"))

    assert will["compiled"]["kind"] == "theatre" and will["role"] == "tense_aspect"
    assert ll["compiled"]["kind"] == "theatre"
    assert all(r["compiled"].get("modality") in (m.value for m in Modality)
               for r in rows if r["compiled"].get("kind") == "prefix"
               and r["compiled"].get("element") == "modality")


def test_a_form_v1_called_ambiguous_keeps_BOTH_readings(rows):
    """v1's own note on `'d`: «contracted would or had — genuinely ambiguous». A row that picked one
    would be a lie the compiler could not detect."""
    d = next(r for r in rows if r["form"] == "'d")

    assert d["compiled"]["kind"] == "ambiguous"
    kinds = {c["kind"] for c in d["compiled"]["candidates"]}
    assert kinds == {"prefix", "theatre"}


# ------------------------------------------------------------------------------------------------
# the ambiguous markers, which are the reason `roles` is a list
# ------------------------------------------------------------------------------------------------


def test_an_ambiguous_marker_keeps_every_candidate_best_first(rows):
    by = next(r for r in rows if r["form"] == "by" and r["role"] == "role_marker")
    to = next(r for r in rows if r["form"] == "to" and r["role"] == "role_marker")

    assert by["compiled"]["roles"] == ["instrument", "agent", "path", "time"]
    assert to["compiled"]["roles"] == ["destination", "recipient"]


def test_patient_and_experiencer_are_marked_by_NOTHING(rows):
    """The sanity check that says the mapping is sane rather than merely complete: those two are
    core arguments, marked by POSITION. UD marks them nsubj/obj/iobj and never `case`. A preposition
    claiming to mark a patient would mean the mapping had been filled in by vibes."""
    marked = {role for r in rows if r["compiled"].get("kind") == "box"
              for role in r["compiled"]["roles"]}

    assert "patient" not in marked and "experiencer" not in marked
    assert len(marked) == 16, "the other sixteen all have at least one marker"


def test_without_negates_the_box_it_fills(rows):
    """«without a knife» is the instrument NEGATED — it fills a box and raises the negation prefix,
    which no other marker does."""
    without = next(r for r in rows if r["form"] == "without")

    assert without["compiled"]["roles"] == ["instrument", "comitative"]
    assert without["compiled"]["negates"] is True


# ------------------------------------------------------------------------------------------------
# version 2 is version 1 plus a decision — never minus a row
# ------------------------------------------------------------------------------------------------


def test_the_newest_version_carries_every_v1_form_and_invents_none(rows, v1):
    before = Counter((r["form"], r["word_class"]) for r in v1 if r.get("version") == 1)
    after = Counter((r["form"], r["word_class"]) for r in rows)

    assert after == before, "a form was added or lost between versions"


def test_the_newest_version_changes_only_compiled_role_and_note(rows, v1):
    """The forms, features and sources are v1's and must not drift: this migration is the author of
    the MAPPING and of nothing else."""
    old = {(r["form"], r["word_class"], r["position"]): r for r in v1 if r.get("version") == 1}
    for row in rows:
        was = old[(row["form"], row["word_class"], row["position"])]
        assert row["features"] == was["features"]
        assert row["source"] == was["source"]
        assert row["version"] == 3

    moved = [r["form"] for r in rows
             if r["role"] != old[(r["form"], r["word_class"], r["position"])]["role"]]
    assert len(moved) == 41, f"41 rows were re-typed, not {len(moved)}"


# ------------------------------------------------------------------------------------------------
# `db/0036` — where a «not» after a modal scopes, on every modal row
# ------------------------------------------------------------------------------------------------


def test_EVERY_modality_row_says_where_a_following_not_scopes():
    """The compiler reads it and never defaults it, so a modal row without it — or with a value
    outside the three — must be the migration's failure, not the station's guess."""
    module = migration(36)
    modal = [r for r in module.CLOSED_CLASS_ROWS if r["role"] == "modality"]
    v18 = {r["form"] for r in migration(33).CLOSED_CLASS_ROWS if r["role"] == "modality"}

    assert {r["form"] for r in modal} == v18 | {"cannot"}
    assert all(r["features"].get(module.FOLLOWING_NEGATION) in module.VALUES for r in modal)
    assert {r["form"]: r["features"][module.FOLLOWING_NEGATION] for r in modal
            if r["form"] in ("must", "need", "can", "may")} == \
        {"must": "inside", "need": "outside", "can": "outside", "may": "ambiguous"}


def test_the_check_REFUSES_a_modal_row_that_lost_its_scope(monkeypatch):
    """«A row with the field missing is a migration check failure, not a fallback» — shown, not
    trusted: the check is run against a table with one answer taken away."""
    module = migration(36)
    rows = [dict(r, features=dict(r["features"])) for r in module.CLOSED_CLASS_ROWS]
    next(r for r in rows if r["form"] == "need")["features"].pop(module.FOLLOWING_NEGATION)
    monkeypatch.setattr(module, "CLOSED_CLASS_ROWS", rows)

    with pytest.raises(ValueError, match="need"):
        module._check()                                                     # noqa: SLF001


def test_cannot_is_the_one_row_added_and_the_exclusion_set_moves_by_it_alone():
    """«cannot» is one token to stanza and was no row at all. It is single-word, so D's exclusion set
    moves — by a form WordNet has no lemma for, which neither vocabulary reading of D can hold."""
    module = migration(36)
    before = migration(33)
    cannot = module.CLOSED_CLASS_ROWS[-1]

    assert set(module.CLOSED_CLASS_FORMS) ^ set(before.CLOSED_CLASS_FORMS) == {"cannot"}
    assert cannot["form"] == "cannot" and cannot["spoken"] is True
    assert cannot["compiled"] == {"kind": "prefix", "element": "modality",
                                  "modality": Modality.POSSIBILITY.value, "negation": "outside"}


def test_the_0036_check_asks_the_question_the_LOOKUP_asks():
    """`db/0029`'s lesson: the migration's `_meaning()` is the decompiler's key, on every row, and
    the voice it proves exists for «X not» is the one the decompiler finds."""
    from tk2.language.closed import ClosedClasses
    from tk2.language.decompile import Decompiler

    module = migration(36)
    for row in module.CLOSED_CLASS_ROWS:
        features = row.get("features") or {}
        assert module._meaning(row) == Decompiler._key(                     # noqa: SLF001
            row["role"], row.get("compiled") or {}, features.get("sort"),
            features.get("takes_number")), row["form"]

    reader = Decompiler(ClosedClasses(module.CLOSED_CLASS_ROWS, "db/0036 (test)"))
    modality = {"kind": "prefix", "element": "modality"}
    assert reader.the_modal("inside", **modality, modality="necessity") == "must"
    assert reader.the_modal("inside", **modality, modality="possibility") == "might"


# ------------------------------------------------------------------------------------------------
# `db/0037` — a purpose claims the act and not the end (the Captain, 2026-09-25)
# ------------------------------------------------------------------------------------------------


def test_every_PURPOSE_row_claims_its_antecedent_and_names_the_matrix_as_it():
    """«to», «in order to», «so that» — one meaning. v19 compiled the two subordinators imply/both
    with the introduced clause first: the end claimed and the arrow reversed."""
    module = migration(37)
    purpose = {r["form"]: r for r in module.CLOSED_CLASS_ROWS
               if r["compiled"].get("asserts") == module.ANTECEDENT}

    assert set(purpose) == {"to", "in order to", "so that"}
    assert all(r["compiled"] == module.PURPOSE for r in purpose.values())
    assert purpose["to"]["features"]["introduces"] == "advcl"
    assert [f for f, r in purpose.items() if r.get("spoken")] == ["to"], "the voice is «to»"


def test_0037_adds_ONE_row_moves_no_form_and_touches_no_other_meaning():
    module, before = migration(37), migration(36)

    assert set(module.CLOSED_CLASS_FORMS) == set(before.CLOSED_CLASS_FORMS)
    assert len(module.CLOSED_CLASS_ROWS) == len(before.CLOSED_CLASS_ROWS) + 1
    moved = [was["form"] for row, was in zip(module.CLOSED_CLASS_ROWS, before.CLOSED_CLASS_ROWS)
             if row["compiled"] != was["compiled"]]
    assert sorted(moved) == ["in order to", "so that"]


def test_the_0037_check_REFUSES_a_purpose_that_does_not_say_which_clause_leads(monkeypatch):
    module = migration(37)
    rows = [dict(r, compiled=dict(r["compiled"])) for r in module.CLOSED_CLASS_ROWS]
    next(r for r in rows if r["form"] == "in order to")["compiled"].pop(module.ANTECEDENT)
    monkeypatch.setattr(module, "CLOSED_CLASS_ROWS", rows)

    with pytest.raises(ValueError, match="in order to"):
        module._check()                                                     # noqa: SLF001


def test_the_0037_check_asks_the_question_the_LOOKUP_asks():
    """The decompiler asks the three joining roles for the purpose meaning, keyed on the same tuple
    as the migration's `_meaning()` — and finds «to», said as the infinitive."""
    from tk2.language.closed import ClosedClasses
    from tk2.language.decompile import Decompiler

    module = migration(37)
    for row in module.CLOSED_CLASS_ROWS:
        features = row.get("features") or {}
        assert module._meaning(row) == Decompiler._key(                     # noqa: SLF001
            row["role"], row.get("compiled") or {}, features.get("sort"),
            features.get("takes_number")), row["form"]
    from tk2.language.decompile import JOINING_ROLES
    assert module.JOINING_ROLES == JOINING_ROLES, "the check asks the roles the decompiler asks"

    reader = Decompiler(ClosedClasses(module.CLOSED_CLASS_ROWS, "db/0037 (test)"))
    assert reader._connective("imply", "antecedent") == ("to", "subordinator")  # noqa: SLF001


# ------------------------------------------------------------------------------------------------
# `db/0039` — «only» says that nothing else does; «as long as» claims neither half (`E3.12.5.9.12`)
# ------------------------------------------------------------------------------------------------


def test_0039_moves_ONE_closed_class_meaning_and_no_form():
    """Ruling 6: «as long as» claims neither half, as «if» does. The six focus particles went to the
    adverb kinds, so the exclusion set — D's vocabulary filter — does not move."""
    module, before = migration(39), migration(37)
    was = [r for r in before.CLOSED_CLASS_ROWS if r["version"] == 20]

    assert set(module.CLOSED_CLASS_FORMS) == set(before.CLOSED_CLASS_FORMS)
    assert len(module.CLOSED_CLASS_ROWS) == len(was)
    moved = [(row["form"], row["compiled"]) for row, old in zip(module.CLOSED_CLASS_ROWS, was)
             if row["compiled"] != old["compiled"]]
    assert moved == [("as long as", {"kind": "join", "operator": "imply", "asserts": "neither"})]


def test_0039_gives_the_six_particles_the_two_meanings_the_ruling_names():
    """Ruling 4: «exclusive» (only · just · solely · merely), «identifying» (exactly · precisely) —
    per-word knowledge, one voice each."""
    module = migration(39)
    focus = {r["form"]: r for r in module.ADVERB_KIND_ROWS if r["kind"] == module.FOCUS}

    assert {f for f, r in focus.items() if r["compiled"]["focus"] == module.EXCLUSIVE} == \
        {"only", "just", "solely", "merely"}
    assert {f for f, r in focus.items() if r["compiled"]["focus"] == module.IDENTIFYING} == \
        {"exactly", "precisely"}
    assert sorted(f for f, r in focus.items() if r["spoken"]) == ["exactly", "only"]
    assert not set(focus) & {r["form"] for r in module.CLOSED_CLASS_ROWS}, "never in both rosters"


def test_the_0039_check_REFUSES_a_particle_in_both_rosters(monkeypatch):
    module = migration(39)
    rows = [*module.CLOSED_CLASS_ROWS, {**module.CLOSED_CLASS_ROWS[0], "form": "only"}]
    monkeypatch.setattr(module, "CLOSED_CLASS_ROWS", rows)

    with pytest.raises(ValueError):
        module._check()                                                     # noqa: SLF001


def test_the_0039_check_asks_the_question_the_LOOKUP_asks():
    """The decompiler composes «only if» from the exclusive's voice — keyed as the migration keys it."""
    from tk2.language.adverbs import AdverbKinds
    from tk2.language.decompile import Decompiler

    module = migration(39)
    for row in module.ADVERB_KIND_ROWS:
        assert module._meaning(row) == Decompiler._key(None, row["compiled"]), row["form"]  # noqa: SLF001
    reader = Decompiler(adverbs=AdverbKinds(module.ADVERB_KIND_ROWS, "db/0039 (test)"))
    assert reader.the_adverb(kind="focus", focus="exclusive") == "only"
    assert reader.the_adverb(kind="focus", focus="identifying") == "exactly"
