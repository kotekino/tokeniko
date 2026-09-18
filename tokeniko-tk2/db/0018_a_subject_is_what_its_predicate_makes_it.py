"""0018 — subject roles v1: **a subject is what its predicate makes it** (parser-compiler req 22).

**TEN OF THE DRILL GATE'S TWELVE DISAGREEMENTS WERE ONE QUESTION.** `nsubj` was always `agent`
(`RELATION_FILLS_ROLE`, whose own comment deferred the question), and a copular subject always
`patient`. The drill says otherwise, and E2 said why (`tkzip/202609111051_notes.md`, ruling 2): *«I
kicked the dog (I act) vs I fear the dog (it happens to me)»*.

**THE BENCH, on every subject the drill holds (49):**

    copular + adjective   the related noun's supersense      noun.state -> experiencer   4/4
                                                             noun.attribute -> patient   6/6
    copular + noun        always a patient                                               3/3
    verb                  the verb's supersense: THREE CONTRADICTIONS in the drill itself
                          VerbNet's subject role: worse — motion verbs are `Theme`, not agents

**THE CONTRADICTIONS WERE ASKED, NOT RESOLVED BY WHICH SIDE THE GATE PREFERRED.** The QM, who
compiled the rows with the Captain acknowledging, judged each against ruling 2 and the Captain
acknowledged the verdicts: `exist` → patient STANDS (one shape with «there is»); `disagree` →
experiencer STANDS (a position held — WordNet files it `communication`, so it is this table's one
exception); **`think` and `live` were errors**, and so was the drill's split on `learn` and
perception. Twelve rows amended, dated, in the bar doc.

**THE RULE** — `MarkerSelector`'s vocabulary, first match wins, ending in a default:

    verb      disagree -> experiencer (the exception)
              verb.emotion · verb.cognition · verb.perception -> experiencer
              verb.stative -> patient
              otherwise -> agent
    copular   a NOUN complement -> patient
              an adjective whose noun is noun.state -> experiencer
              otherwise -> patient

**`noun.feeling` IS NOT IN, and was for one draft**: ruling 2's words («feeling and thinking»)
suggested it, it has no drill witness, and it made «Be QUIET!» an experiencer — WordNet relates
*quiet* to a feeling. A class enters on a witness, not on a principle alone. `verb.perception` is
in on the Captain's ruling — «look», «watch», «listen» are acts and will want exception rows when a
witness arrives. **Known limit**: stimulus-subject psych verbs («the
dog FRIGHTENS me» is `verb.emotion`, and the dog is no experiencer). **Known miss**: `develop`, whose
role follows the SENSE, which the station never picks (req 11).

**Written by the QM on 2026-09-18, on the Captain's «amend the drill and build the rule».**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, SubjectRoleDoc
from tk2.migrations import ensure_collections

VERSION = 1

SOURCE = ("the subject-role bench, 2026-09-18 — every drill subject; E2 ruling 2 "
          "(tkzip/202609111051_notes.md); the Captain's acknowledged verdicts")

SUBJECT_ROLE_ROWS = [
    {
        "version": VERSION,
        "predicate": "verb",
        "compiled": {"selector": [
            {"reads": "lemma", "is": ["disagree"], "then": "experiencer"},
            {"reads": "verb", "is": ["verb.emotion", "verb.cognition", "verb.perception"],
             "then": "experiencer"},
            {"reads": "verb", "is": ["verb.stative"], "then": "patient"},
            {"reads": "default", "then": "agent"},
        ]},
        "source": SOURCE,
        "note": "«disagree» is filed verb.communication and means a held position — the one exception",
        "position": 0,
    },
    {
        "version": VERSION,
        "predicate": "copular",
        "compiled": {"selector": [
            {"reads": "head_pos", "is": ["NOUN", "PROPN", "PRON", "NUM"], "then": "patient"},
            {"reads": "derived", "is": ["noun.state"], "then": "experiencer"},
            {"reads": "default", "then": "patient"},
        ]},
        "source": SOURCE,
        "note": "an adjective is read through its related noun: WordNet files almost all of them adj.all",
        "position": 1,
    },
]

#: The roles a rule may produce — the subject's candidates in tkzip's inventory, and no others.
SUBJECT_ROLES = ("agent", "experiencer", "patient")


def _check() -> None:
    kinds = [r["predicate"] for r in SUBJECT_ROLE_ROWS]
    if sorted(kinds) != ["copular", "verb"]:
        raise ValueError(f"one rule per kind of predicate, and exactly two kinds — got {kinds}")
    for row in SUBJECT_ROLE_ROWS:
        rules = row["compiled"]["selector"]
        if rules[-1]["reads"] != "default":
            raise ValueError(f"{row['predicate']}: the selector does not end in a default")
        for rule in rules:
            if rule["then"] not in SUBJECT_ROLES:
                raise ValueError(f"{row['predicate']}: {rule['then']!r} is not a subject's role")


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(SubjectRoleDoc, SUBJECT_ROLE_ROWS)
