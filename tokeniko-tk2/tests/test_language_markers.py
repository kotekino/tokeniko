"""THE THIRTEEN AMBIGUOUS MARKERS — `db/0012` (v6) and the frame that runs its rules.

Three things are held here, and they are different kinds of claim:

1. **The RULES are well formed** — every ambiguous marker has a selector, every selector ends in a
   default, and no rule names a role its own row does not offer. A migration that invented a role
   would be curation written by nobody.
2. **The FRAME runs them correctly** — with the resource stubbed, so a test says what WordNet
   answers instead of depending on which WordNet is installed.
3. **The BENCH does not regress** — the numbers `db/0012` was ruled on, held as a floor.

And one invariant that outranks all three: **the 268 single-word forms must not move.** That set is
the dictionary's gloss-word exclusion, and a closed-class migration that touched it would move D and
the sealed base with it, under a policy nobody re-ruled.
"""

import pytest

from tests.fixtures.markers import CASES, CURATION, DRILL, UD
from tk2.language.markers import DEFAULT, MarkerSelector, Settled
from tk2.migrations import discover
from tk2.tkzip.schema import Role


def migration(number: int):
    found = next((m for m in discover() if m.number == number), None)
    if found is None:
        pytest.skip(f"migration {number} is not present")
    return found.load()


@pytest.fixture(scope="module")
def v6():
    return migration(12).CLOSED_CLASS_ROWS


@pytest.fixture(scope="module")
def v5():
    return migration(11).CLOSED_CLASS_ROWS


def selectors(rows):
    return {r["form"]: r["compiled"]["selector"] for r in rows
            if (r.get("compiled") or {}).get("selector")}


# ------------------------------------------------------------------------------------------------
# 1 — the rules are well formed
# ------------------------------------------------------------------------------------------------


def test_every_ambiguous_box_marker_now_says_what_settles_it(v6):
    """The hole `db/0008` left open by name: «the selection is the compiler's». Seventeen forms
    carry more than one candidate, and every one of them must now carry its rules."""
    ambiguous = {r["form"] for r in v6
                 if (r.get("compiled") or {}).get("kind") == "box"
                 and len(r["compiled"].get("roles", ())) > 1}

    assert len(ambiguous) == 17, f"{len(ambiguous)} ambiguous box forms, not 17"
    assert ambiguous == set(selectors(v6)), "an ambiguous marker with no rules is the old hole"


def test_a_selector_ends_in_a_default_and_never_falls_off_the_end(v6):
    """A rule list that could run out would leave the caller with None for a marker that IS one of
    the thirteen — an abstention dressed as an absence, which req 8 distinguishes."""
    for form, rules in selectors(v6).items():
        assert rules[-1]["reads"] == DEFAULT, f"{form}: no default"
        assert all(r["reads"] != DEFAULT for r in rules[:-1]), f"{form}: a rule after the default"


def test_no_rule_names_a_role_the_row_does_not_offer(v6):
    """The migration's own check, held from outside it: a selector chooses AMONG the candidates the
    curation declared and may not add one. `relation` is admitted by name — it is the possessor
    FIELD (req 26), which is not a box of the clause at all."""
    for row in v6:
        compiled = row.get("compiled") or {}
        for rule in compiled.get("selector", ()):
            assert rule["then"] in compiled["roles"] or rule["then"] == "relation", \
                f"{row['form']}: {rule['then']} is not a candidate"


def test_every_settled_role_is_one_of_the_eighteen_or_the_possessor_field(v6):
    roles = {r["then"] for rules in selectors(v6).values() for r in rules}
    named = {role.value for role in Role}

    assert roles - named == {"relation"}, "only the possessor field may not be a role"


def test_of_is_settled_by_the_TREE_and_asks_no_dictionary(v6):
    """«made OF titanium» hangs off a verb and is the material; «the office OF the Chair» hangs off
    a noun and is the possessor. UD says which, so a supersense here would be a lookup bought for
    nothing — and the possessor is a FIELD, which is why it is not one of the eighteen."""
    rules = selectors(v6)["of"]

    assert [r["reads"] for r in rules] == ["head_pos", "head_pos", DEFAULT]
    assert [r["then"] for r in rules] == ["source", "relation", "complement"]


def test_v6_moves_no_form_and_changes_only_the_seventeen(v6, v5):
    """The exclusion set is the load-bearing one. Everything else is the migration's own claim:
    seventeen rows gain a selector and nothing else in the table moves."""
    before = {(r["form"], r["word_class"], r["position"]): r for r in v5}
    after = {(r["form"], r["word_class"], r["position"]): r for r in v6}

    assert set(before) == set(after), "a row arrived or left"
    changed = {k[0] for k in after if before[k]["compiled"] != after[k]["compiled"]}
    assert changed == set(selectors(v6)), "something other than a selector moved"
    assert not [k for k in after if before[k]["role"] != after[k]["role"]], "no row was re-typed"

    forms = lambda rs: sorted({r["form"] for r in rs if " " not in r["form"]})
    assert forms(v5) == forms(v6), "THE EXCLUSION SET MOVED — D and the sealed base move with it"
    assert len(forms(v6)) == 268
    assert all(r["version"] == 6 for r in v6)


# ------------------------------------------------------------------------------------------------
# 2 — the frame runs them, with the resource stubbed
# ------------------------------------------------------------------------------------------------


def stub(**said):
    """A supersense reader that answers exactly what a test says and None for everything else."""
    return lambda lemma, upos: said.get(lemma)


def test_the_nominals_supersense_separates_a_time_from_a_place(v6):
    rules = selectors(v6)["at"]
    at_noon = MarkerSelector(stub(noon="noun.time")).settle({"selector": rules}, "noon", "NOUN")
    at_door = MarkerSelector(stub(door="noun.artifact")).settle({"selector": rules}, "door", "NOUN")

    assert at_noon == Settled("time", "settled", "nominal:noun.time")
    assert at_door.role == "location" and at_door.is_default


def test_the_verbs_supersense_separates_give_like_from_go_like(v6):
    """`db/0008` named this case exactly: «give-like → recipient, go-like → destination»."""
    rules = {"selector": selectors(v6)["to"]}
    walk = MarkerSelector(stub(station="noun.artifact", walk="verb.motion"))
    talk = MarkerSelector(stub(friend="noun.person", talk="verb.communication"))

    assert walk.settle(rules, "station", "NOUN", "walk", "VERB").role == "destination"
    assert talk.settle(rules, "friend", "NOUN", "talk", "VERB").role == "recipient"


def test_a_person_is_a_recipient_before_the_verb_is_asked(v6):
    """The nominal is asked first for «to», and «go to school» is why: WordNet files a school under
    `noun.group`, and a nominal rule that reached for institutions made a destination a recipient."""
    rules = {"selector": selectors(v6)["to"]}
    school = MarkerSelector(stub(school="noun.group", go="verb.motion"))

    assert school.settle(rules, "school", "NOUN", "go", "VERB").role == "destination"


def test_a_word_the_resource_does_not_hold_falls_to_the_default(v6):
    """None is an answer. The rules find nothing to fire on, the curation's best-first stands, and
    the caller is told it was a default — which is the whole of req 8 here."""
    settled = MarkerSelector(stub()).settle({"selector": selectors(v6)["in"]}, "zzzq", "NOUN")

    assert settled.role == "location" and settled.is_default and settled.why == DEFAULT


def test_a_marker_with_one_candidate_gets_no_selector_and_that_is_not_an_abstention(v6):
    """«after» marks time and nothing else. `None` here means «not one of the thirteen», and a
    caller that read it as an abstention would be reporting a hole that does not exist."""
    after = next(r for r in v6 if r["form"] == "after" and r["role"] == "role_marker")

    assert "selector" not in after["compiled"]
    assert MarkerSelector(stub()).settle(after["compiled"], "rehearsal", "NOUN") is None


def test_an_unknown_probe_is_skipped_rather_than_raised(v6):
    """A row written by a later migration must not stop an older station: the rule is passed over
    and the default still answers."""
    rules = {"selector": [{"reads": "phase_of_the_moon", "is": ["gibbous"], "then": "time"},
                          {"reads": DEFAULT, "then": "location"}]}

    assert MarkerSelector(stub()).settle(rules, "pool", "NOUN").role == "location"


# ------------------------------------------------------------------------------------------------
# 3 — the bench, held as a floor
# ------------------------------------------------------------------------------------------------


def read(selector, table_rows, case):
    compiled = next((r["compiled"] for r in table_rows
                     if r["form"] == case.marker and (r.get("compiled") or {}).get("kind") == "box"
                     and r["compiled"].get("roles")), {})
    settled = selector.settle(compiled, case.nominal, case.nominal_upos, case.head, case.head_upos)
    return None if settled is None else settled.role


def score(rows, keep):
    selector = MarkerSelector()
    chosen = [c for c in CASES if keep(c)]
    right = sum(read(selector, rows, c) == c.expect for c in chosen)
    return right, len(chosen)


def test_the_bench_holds_on_the_cases_nobody_wrote_for_it(v6):
    """E2's hand-compiled drill and the UD gate's own examples — the number a claim may rest on.
    11 of 11 on 2026-09-16, against 7 of 11 for taking the first candidate."""
    right, total = score(v6, lambda c: c.source in (DRILL, UD) and not c.name)

    assert total == 11
    assert right == total, f"{right} of {total}; all 11 held on 2026-09-16"


def test_the_bench_holds_on_the_curations_own_examples(v6):
    """`db/0008`'s worked examples. This is the curation AGREEING WITH ITSELF and discovers nothing
    — but a selector that could not hold them would be refuted. 29 of 30, «at speed» excepted:
    WordNet files `speed.n.01` under `noun.time`, which is the resource being right about speed."""
    right, total = score(v6, lambda c: c.source == CURATION and not c.name)

    assert total == 30
    assert right >= 29, f"{right} of {total}; 29 held on 2026-09-16"


def test_the_named_individuals_are_where_the_errors_are(v6):
    """9 of 11, and BOTH failures are «with Anna» — WordNet holds `anna` only as an Indian coin.
    That is the named-individual hole, which has its own answer waiting (a type-centroid vector plus
    a context-scoped identity) and must not be papered over with a better marker rule."""
    right, total = score(v6, lambda c: c.name)

    assert total == 11
    assert right >= 9, f"{right} of {total}; 9 held on 2026-09-16"
