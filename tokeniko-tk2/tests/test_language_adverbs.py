"""THE ADVERB KINDS — requirement 23's four-way split, as rows (`db/0013`) and the frame that reads
them (`db/0014` for the two repairs it found).

The claims held here are of three different kinds and are kept apart:

1. **The ROWS are well formed** — no form clashes with the closed classes, `manner` is never a row,
   and every `compiled` map speaks the closed classes' own vocabulary.
2. **The READER is right**, including that a miss is the MANNER DEFAULT and says so.
3. **The 268-form exclusion set did not move**, which is what licensed `db/0014` to exist at all.
"""

import pytest

from tk2.language.adverbs import (
    CIRCUMSTANTIAL, DISCOURSE, EPISTEMIC, EVALUATIVE, MANNER, AdverbKinds,
)
from tk2.migrations import discover
from tk2.tkzip.schema import Modality, Operator, Role


def migration(number: int):
    found = next((m for m in discover() if m.number == number), None)
    if found is None:
        pytest.skip(f"migration {number} is not present")
    return found.load()


@pytest.fixture(scope="module")
def rows():
    return migration(13).ADVERB_KIND_ROWS


@pytest.fixture(scope="module")
def table(rows):
    return AdverbKinds(rows, "db/0013 (test)")


# ------------------------------------------------------------------------------------------------
# 1 — the rows
# ------------------------------------------------------------------------------------------------


def test_MANNER_is_never_a_row(rows):
    """It is the DEFAULT, and 79% of English's adverbs are `-ly` and describe the action. A row
    asserting manner would be the roster of the open class this table exists to avoid writing."""
    assert not [r for r in rows if r["kind"] == MANNER]


def test_no_form_clashes_with_the_closed_classes(rows):
    """**THE COST OF TWO ROSTERS, REFUSED.** A reader asks the closed classes, misses, asks this —
    and if a form were in both it could not tell which answered. The migration's own import-time
    check enforces it; this holds the invariant from outside, where a later edit would meet it.

    It caught eleven forms on the first run, and ten of them were already compiled CORRECTLY in the
    closed classes — `so` and `yet` as joins, `anywhere`/`everywhere`/`nowhere` as quantifiers over
    places, `inside`/`outside` as location boxes. The finding was about this table's assumptions.
    """
    closed = {r["form"] for r in migration(14).CLOSED_CLASS_ROWS}
    clash = sorted({r["form"] for r in rows} & closed)

    assert clash == [], f"{len(clash)} form(s) in both rosters: {clash}"


def test_every_compiled_map_speaks_the_closed_classes_vocabulary(rows):
    """Only the ROSTER is second; the ANSWER must be identical. A caller that could tell which table
    answered would be looking at two formats, which is the defect req 12 names."""
    for row in rows:
        compiled = row["compiled"]
        assert compiled["kind"] in ("box", "prefix", "join"), row["form"]
        if compiled["kind"] == "box":
            assert [Role(r) for r in compiled["roles"]], row["form"]
        if compiled["kind"] == "join":
            assert Operator(compiled["operator"]), row["form"]
        if compiled["kind"] == "prefix" and compiled.get("modality"):
            assert Modality(compiled["modality"]), row["form"]


def test_one_form_may_hold_two_KINDS(rows):
    """«he is STILL here» is time and «STILL, he left» is concessive — both real, and only the
    dependency separates them. The closed classes do exactly this for 45 forms."""
    still = sorted(r["kind"] for r in rows if r["form"] == "still")

    assert still == [CIRCUMSTANTIAL, DISCOURSE]


def test_the_four_kinds_are_all_populated(rows):
    kinds = {r["kind"] for r in rows}
    assert kinds == {EPISTEMIC, EVALUATIVE, DISCOURSE, CIRCUMSTANTIAL}


# ------------------------------------------------------------------------------------------------
# 2 — the reader
# ------------------------------------------------------------------------------------------------


def test_a_miss_is_the_MANNER_DEFAULT_and_says_so(table):
    """A default that cannot be told from a curated answer is the silently-complete nearest fit
    req 8 forbids — the same distinction `db/0012` drew for the ambiguous markers."""
    quickly = table.read("quickly")

    assert quickly.kind == MANNER and quickly.is_default
    assert quickly.role == "manner", "and it still fills a box (req 24)"


def test_a_curated_row_is_not_a_default(table):
    early = table.read("early")

    assert early.kind == CIRCUMSTANTIAL and not early.is_default
    assert early.role == "time"


@pytest.mark.parametrize("form, kind, expected", [
    ("abroad", CIRCUMSTANTIAL, "location"),
    ("backwards", CIRCUMSTANTIAL, "direction"),
    ("probably", EPISTEMIC, "possibility"),
    ("certainly", EPISTEMIC, "necessity"),
    ("luckily", EVALUATIVE, "evaluative"),
    ("therefore", DISCOURSE, "imply"),
    ("nevertheless", DISCOURSE, "and"),
])
def test_the_four_scopes_reach_the_right_slot(table, form, kind, expected):
    reading = table.read(form)
    compiled = reading.compiled

    assert reading.kind == kind
    assert expected in (reading.role, compiled.get("modality"), compiled.get("attitude"),
                        compiled.get("operator"))


def test_the_dependency_chooses_between_a_forms_two_kinds(table):
    """UD's `discourse` relation names the kind outright — the only dependency that does."""
    assert table.read("still", "advmod").kind == CIRCUMSTANTIAL
    assert table.read("still", "discourse").kind == DISCOURSE


def test_an_empty_table_still_answers(table):
    """The default is the MECHANISM's, not the table's: a station with no rows at all still calls
    every adverb a manner adverb, which is right 79% of the time."""
    empty = AdverbKinds([], "(empty)")

    assert empty.read("early").kind == MANNER
    assert len(empty) == 0


# ------------------------------------------------------------------------------------------------
# 3 — what db/0014 was allowed to do, and why
# ------------------------------------------------------------------------------------------------


def test_v7_does_not_move_the_268_form_exclusion_set():
    """**THE MIGRATION'S WHOLE LICENCE TO EXIST.** The exclusion set is a set of FORMS, so editing a
    row's `compiled` column and adding a second row for a form already present both leave it
    untouched. A NEW form would move it, and take D and the sealed base with it — which is exactly
    why `db/0013`'s sixty adverbs are a separate table."""
    v6 = sorted({r["form"] for r in migration(12).CLOSED_CLASS_ROWS if " " not in r["form"]})
    v7 = migration(14).CLOSED_CLASS_FORMS

    assert list(v7) == v6
    assert len(v7) == 268


def test_a_referential_adverb_now_says_which_box_it_fills():
    """«They come HERE» left `here` unplaced: the row said `entity, resolve: context` — right about
    the HEAD and silent about the ROLE — and `advmod` is not a nominal relation, so nothing could
    reach one."""
    rows = {(r["form"], r["role"]): r for r in migration(14).CLOSED_CLASS_ROWS}

    assert rows[("here", "referential")]["compiled"]["roles"] == ["location"]
    assert rows[("now", "referential")]["compiled"]["roles"] == ["time"]
    assert rows[("here", "referential")]["compiled"]["resolve"] == "context", "still indexical"


def test_however_gained_its_discourse_reading_beside_the_free_relative():
    """One form, several jobs, several rows — what this table has done since v1 for 45 forms."""
    however = [r for r in migration(14).CLOSED_CLASS_ROWS if r["form"] == "however"]

    assert len(however) == 2
    kinds = {r["compiled"]["kind"] for r in however}
    assert kinds == {"open", "join"}, "«however you do it» and «however, he left»"


# ------------------------------------------------------------------------------------------------
# 4 — the voice (`db/0035`)
# ------------------------------------------------------------------------------------------------


def test_v3_sets_ONE_flag_and_moves_nothing_else():
    """`necessarily` speaks a necessity outside a negation; every other column of every row is v2's.
    The necessity adverbs are ten forms for one meaning, so the choice is curation — and exactly one
    choice was made."""
    v2 = [r for r in migration(15).ADVERB_KIND_ROWS if r["version"] == 2]
    v3 = migration(35).ADVERB_KIND_ROWS

    assert [{k: v for k, v in r.items() if k not in ("version", "spoken")} for r in v3] == \
        [{k: v for k, v in r.items() if k != "version"} for r in v2]
    assert [(r["kind"], r["form"]) for r in v3 if r["spoken"]] == [(EPISTEMIC, "necessarily")]
    assert next(r for r in v3 if r["spoken"])["compiled"]["modality"] == Modality.NECESSITY.value


def test_the_check_asks_the_question_the_LOOKUP_asks():
    """**THE MIGRATION'S `_meaning()` IS THE DECOMPILER'S KEY** — `db/0029`'s lesson, pinned on every
    row rather than trusted: a check on a coarser or finer key than the lookup's checks a table that
    does not exist, and the loser of a shared key is silent."""
    from tk2.language.decompile import Decompiler

    module = migration(35)
    for row in module.ADVERB_KIND_ROWS:
        assert module._meaning(row) == Decompiler._key(None, row["compiled"]), row["form"]  # noqa: SLF001

    reader = Decompiler(adverbs=AdverbKinds(module.ADVERB_KIND_ROWS, "db/0035 (test)"))
    assert reader.the_adverb(kind="prefix", element="modality",
                             modality="necessity") == "necessarily"
    assert reader.the_adverb(kind="prefix", element="modality", modality="possibility") is None, \
        "eleven possibility adverbs and no flag: a choice, and not one made in code"


# ------------------------------------------------------------------------------------------------
# 5 — a focus word whose meaning is not settled says ABSTAIN (`db/0040`, `E3.12.5.9.3.1`)
# ------------------------------------------------------------------------------------------------


def test_v5_adds_the_three_unsettled_focus_words_and_moves_nothing_else():
    """The Captain's ruling: keep the manner default; each focus word met gets its own row, and
    where the meaning is not settled the row says ABSTAIN — «even», «strictly», «simply»."""
    v4 = [r for r in migration(39).ADVERB_KIND_ROWS if r["version"] == 4]
    module = migration(40)
    v5 = module.ADVERB_KIND_ROWS

    assert [{k: v for k, v in r.items() if k != "version"} for r in v5[:len(v4)]] == \
        [{k: v for k, v in r.items() if k != "version"} for r in v4]
    added = v5[len(v4):]
    assert {r["form"] for r in added} == {"even", "strictly", "simply"}
    assert all(r["kind"] == "focus" and r["compiled"] == {"kind": "abstain"} and not r["spoken"]
               for r in added)


def test_an_ABSTAIN_row_is_read_as_what_it_says():
    """The reader hands the row back as it is — the kind says what the word IS, the meaning what
    the station may do with it — and a miss is still the manner default."""
    kinds = AdverbKinds(migration(40).ADVERB_KIND_ROWS, "db/0040 (test)")

    assert kinds.read("strictly").kind == "focus"
    assert kinds.read("strictly").compiled["kind"] == "abstain"
    assert kinds.read("quickly").is_default


def test_the_0040_check_REFUSES_a_voiced_abstention(monkeypatch):
    module = migration(40)
    rows = [dict(r) for r in module.ADVERB_KIND_ROWS]
    rows[-1]["spoken"] = True
    monkeypatch.setattr(module, "ADVERB_KIND_ROWS", rows)

    with pytest.raises(ValueError):
        module._check()                                                     # noqa: SLF001
