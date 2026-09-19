"""0019 — subject roles v2: **where the resource is of two minds, a row settles it** (req 22).

**FOUND BY THE DRILL GATE'S FOURTH WIDENING, 2026-09-19** — though not by what it was widened for.
«Tokeniko, the cat is dead and alive» disagreed on one run and agreed on the next with no code
between them: **NLTK stores a synset's pointers in a `set`**, so `attributes()` returns them in the
process's own string-hash order, and `derived_supersense` took `[0]`. *dead* has two attribute nouns —
`animation.n.01` (`noun.state`, an experiencer) and `animation.n.02` (`noun.attribute`, a patient) —
so the station read one sentence as two different thoughts depending on the process it ran in.

**The reader now abstains when the relation is not of one mind** (`derived_supersense`), because
WordNet publishes no priority among a synset's attributes and any order we imposed would be our
invention wearing the resource's clothes — the provider-defect doctrine at the dictionary's end.

**THAT ABSTENTION COSTS EXACTLY ONE WITNESS, AND THIS MIGRATION BUYS IT BACK.**

    dead     {noun.state, noun.attribute}   abstains -> the copular default, patient   the drill agrees
    alive    {noun.state, noun.attribute}   abstains -> the copular default, patient   the drill agrees
    happy    {noun.state, noun.feeling}     abstains -> the copular default, patient   THE DRILL SAYS EXPERIENCER

`noun.feeling` cannot enter the rule — it was refused on 2026-09-18 with a witness, «Be QUIET!»,
which WordNet relates to a feeling. So *happy* takes a LEMMA row, the shape `disagree` already has:
**where the resource cannot classify a word, E2's ruling 2 does** — *«verbs of feeling and thinking
are the ones tokeniko will use about himself most»* — and a settlement made by a ruling is curation,
which lives here. Witness `t-of-1`, «I am happy because I am thinking and I love you».

*Nothing else moves. The verb rule is untouched, and no probe is added: `lemma` is the copular
selector's first rule now, and it was already the verb selector's.*

**Written by the QM on 2026-09-19, on the Captain's «widen the gate now, then docs first».**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, SubjectRoleDoc
from tk2.migrations import ensure_collections

VERSION = 2

SOURCE = ("the fourth widening of the drill gate, 2026-09-19 — a hash-order defect in "
          "`derived_supersense`, and the one drill witness its repair cost")

#: The adjectives WordNet files under two disagreeing attribute nouns, with the role E2's ruling 2
#: gives them. ONE entry, and it is here rather than in a comment because the next one is a row too.
RULED_ADJECTIVES = {"happy": "experiencer"}


def build_rows(previous: list[dict]) -> list[dict]:
    out = []
    for row in previous:
        if row.get("version") != 1:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = VERSION
        if row["predicate"] == "copular":
            rules = list(row["compiled"]["selector"])
            new["compiled"] = {"selector": [
                {"reads": "lemma", "is": sorted(RULED_ADJECTIVES), "then": "experiencer"},
                *rules,
            ]}
            new["note"] = (row.get("note") or "") + (
                " — v2: «happy» is filed under BOTH noun.state and noun.feeling, so the reader "
                "abstains and this row answers. A ruling settles what the resource cannot.")
        out.append(new)
    return out


def _previous_rows():
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 18), None)
    if found is None:
        raise RuntimeError("0018 is gone — it holds the rule this one amends")
    return found.load().SUBJECT_ROLE_ROWS


SUBJECT_ROLE_ROWS = build_rows(_previous_rows())


def _check() -> None:
    before = _previous_rows()
    if len(before) != len(SUBJECT_ROLE_ROWS):
        raise ValueError("a rule was added or lost — this migration only amends the copular one")

    copular = next(r for r in SUBJECT_ROLE_ROWS if r["predicate"] == "copular")
    first = copular["compiled"]["selector"][0]
    if first["reads"] != "lemma" or first["then"] != "experiencer":
        raise ValueError("the ruled adjectives must be read FIRST — the default would swallow them")
    if sorted(first["is"]) != sorted(RULED_ADJECTIVES):
        raise ValueError("the lemma rule and RULED_ADJECTIVES disagree about which words are ruled")
    if copular["compiled"]["selector"][-1]["reads"] != "default":
        raise ValueError("the copular selector no longer ends in a default")

    verb = next(r for r in SUBJECT_ROLE_ROWS if r["predicate"] == "verb")
    if verb["compiled"] != next(r for r in before if r["predicate"] == "verb")["compiled"]:
        raise ValueError("the VERB rule moved — this migration is about the copular one alone")


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(SubjectRoleDoc, SUBJECT_ROLE_ROWS)
