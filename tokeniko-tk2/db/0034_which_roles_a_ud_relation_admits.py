"""0034 — UD readings v2: **which roles a UD relation admits** — a fourth question (req 9, E3).

**THE CAPTAIN, 2026-09-24: FRAME IS NOT «WHAT GOES IN CODE».** Frame changes only by a fix,
knowledge by learning; the kingdom says HOW a fact changes, not WHERE it lives. `UD_DEP_TO_ROLE` in
`tk2/language/closed.py` answered «which of the closed classes' roles can this relation's dependent
be» — and the roles it named are OUR closed-class roles, which are db rows. A code map whose values
are db vocabulary is a map that can go stale against its own rows, and it did: `db/0028` wrote
`fused_quantifier` and the station would not admit a single one of them until someone edited the
map. Every other fact the station holds about a UD relation already lives here (`db/0032`), so the
admissible sets MOVE HERE, as the fourth question.

**THE RANKING IS DELETED, NOT MOVED.** The map's tuples were «best-first» and `select` broke a tie
by that order. Nothing measured supports it: `tools/dep_order_bench.py` refused every tie the order
decided, and reversed every tuple, and neither moved a single verdict on the drill, the UD gate or
the fixpoint. The one wrong live pick was not even the tuple's: t-ng-4's «No, some software…»,
where `no` is `discourse`/`INTJ`, the POS filter emptied and fell back, and the MIGRATION's first
row — the quantifier — won by row order. So the rows hold SETS, sorted only so a diff is stable, and
**a tie nobody settles abstains**, the emptied-filter fallback included — `select` no longer picks.

    relation       admits_roles                    (default: None — no constraint)
    case           role_marker · causal_marker · concessive_marker · exceptive_marker · genitive
    mark           subordinator · infinitive_marker · complementizer · causal_marker · …
    det            determination · demonstrative · quantificational · possessive · interrogative
    nsubj · obj …  the argument slots: referential · relative · interrogative · …
    advmod         fused_quantifier · quantificational · negation · interrogative · …
    compound:prt   verb_particle — matched as the FULL label, never bared to `compound`

**THE DEFAULT IS «NO CONSTRAINT», AND A MISS IS STILL AN ANSWER.** UD has 37 relations and the
closed classes 27 roles, and most pairs simply do not interact: a relation with no row admits every
role, exactly as a relation absent from the map always did. A subtype with no row of its own reads
its bare label's (`nsubj:pass` → `nsubj`); a subtype that HAS one (`det:poss`, `compound:prt`) is
read as written.

**TRANSCRIBED, NOT RE-RULED.** Each set is the map's tuple as it stood at `db/0033`, member for
member. `mark` still names `complementizer`, which no closed-class row carries — a role nobody holds
admits nothing, so it is inert, and it is carried over rather than silently dropped so this
migration moves the fact and nothing else. Whether it should stay is a curation question.

**Written by the 1st Officier on 2026-09-24, on the Captain's rulings of the same day.**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, UdReadingDoc
from tk2.migrations import ensure_collections

VERSION = 2

#: The ruling every row below rests on, verbatim enough to be read without this file.
_RULING = ("the Captain, 2026-09-24: frame changes only by a fix, knowledge by learning — the "
           "admissible roles name our closed-class roles, which are db rows, so the sets move to "
           "the readings; the ranking is deleted, not moved, because nothing measured supports "
           "it (`tools/dep_order_bench.py`); a tie nobody settles abstains")

#: One row per relation `UD_DEP_TO_ROLE` held at `db/0033`, in its own order, each set as it stood.
#: The note says what the relation's set is FOR, which is what a curator changing it needs to know.
_ADMITS: list[tuple[str, tuple[str, ...], str]] = [
    ("case", ("role_marker", "causal_marker", "concessive_marker", "exceptive_marker",
              "genitive"),
     "the marker relation: where the role markers and their re-typed cousins (`db/0010`) live"),
    ("mark", ("subordinator", "infinitive_marker", "complementizer", "causal_marker",
              "concessive_marker"),
     "the clause marker. `complementizer` is carried over from the map as it stood; no closed-class "
     "row holds it, so it admits nothing"),
    ("cc", ("coordinator",), "a coordinating conjunction is a coordinator and nothing else"),
    ("cc:preconj", ("coordinator",), "«EITHER … or», «BOTH … and» — the first half of a pair"),
    ("det", ("determination", "demonstrative", "quantificational", "possessive", "interrogative"),
     "every job a determiner slot can hold"),
    ("det:poss", ("possessive",), "UD names the possessive determiner outright"),
    ("det:predet", ("quantificational",), "«ALL the cats» — a predeterminer quantifies"),
    ("nmod:poss", ("possessive",), "UD names the possessor outright"),
    ("aux", ("tense_aspect", "modality"), "an auxiliary carries tense or aspect, or a modal force"),
    ("aux:pass", ("tense_aspect",), "the passive auxiliary is structure, never a modal"),
    ("cop", ("tense_aspect",), "the copula carries tense and nothing modal"),
    ("nsubj", ("referential", "relative", "interrogative", "free_relative", "reflexive",
               "reciprocal", "demonstrative", "existential", "fused_quantifier"),
     "a pronoun is whatever its own row says; the relation says only that it FILLS an argument "
     "slot rather than marking one"),
    ("obj", ("referential", "relative", "interrogative", "free_relative", "reflexive",
             "reciprocal", "demonstrative", "fused_quantifier"),
     "as `nsubj`: an argument slot, filled"),
    ("iobj", ("referential", "reflexive", "reciprocal", "demonstrative"),
     "as `nsubj`: an argument slot, filled — the recipient's"),
    ("obl", ("referential", "reflexive", "demonstrative", "fused_quantifier"),
     "an oblique nominal: «I went THERE», «I did it MYSELF», «it is NOWHERE»"),
    ("expl", ("expletive", "existential"), "«IT rains», «THERE is a cat» — no referent"),
    ("advmod", ("fused_quantifier", "quantificational", "negation", "interrogative",
                "free_relative", "referential", "affirmation"),
     "the adverbial slot: «NOWHERE», «NOT», «WHEN», «THERE», «YES»"),
    ("compound:prt", ("verb_particle",),
     "«He looked UP» — the verb's particle; matched as the FULL label, never bared to `compound`"),
    ("fixed", ("role_marker", "subordinator"),
     "the tail of a fixed multi-word expression the closed classes did not match whole"),
]


def build_rows(previous: list[dict]) -> list[dict]:
    """v1's rows carried forward at v2, and the admissible sets merged in — into a row that already
    reads the same label, if there is one, so its other answers survive; else a new row."""
    out = []
    by_key: dict[tuple[str, str], dict] = {}
    for row in previous:
        if row.get("version") != 1:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = VERSION
        new["reads"] = dict(new.get("reads") or {})
        out.append(new)
        by_key[(new["inventory"], new["label"])] = new

    position = max((r["position"] for r in out), default=-1) + 1
    for label, roles, why in _ADMITS:
        admits = sorted(roles)                   # a SET: the sort is for a stable diff, nothing else
        existing = by_key.get(("relation", label))
        if existing is not None:
            existing["reads"]["admits_roles"] = admits
            existing["note"] = f"{existing.get('note', '')} — and it admits: {why}".strip(" —")
            existing["source"] = f"{existing['source']}; admits_roles: {_RULING}"
            continue
        out.append({
            "version": VERSION,
            "inventory": "relation",
            "label": label,
            "reads": {"admits_roles": admits},
            "source": _RULING,
            "note": why,
            "position": position,
        })
        position += 1
    return out


def _previous_rows():
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 32), None)
    if found is None:
        raise RuntimeError("0032 is gone — it holds the version this one extends")
    return found.load().UD_READING_ROWS


UD_READING_ROWS = build_rows(_previous_rows())


def _check() -> None:
    before = _previous_rows()
    seen = set()
    for row in UD_READING_ROWS:
        key = (row["inventory"], row["label"])
        if key in seen:
            raise ValueError(f"{key} is read twice — the index refuses it and so does sense")
        seen.add(key)
        if row["inventory"] not in ("relation", "pos"):
            raise ValueError(f"{row['label']!r} names no UD inventory: {row['inventory']!r}")
        if not row["reads"]:
            raise ValueError(f"{row['label']!r} states no reading — then it is not an exception")
        if not row["source"]:
            raise ValueError(f"{row['label']!r} has no source: a ruling with no origin is a guess")

    # **NOTHING v1 SAID MOVED.** This migration asks a new question; it re-answers no old one.
    now = {(r["inventory"], r["label"]): r["reads"] for r in UD_READING_ROWS}
    for row in before:
        for question, answer in row["reads"].items():
            if now[(row["inventory"], row["label"])].get(question) != answer:
                raise ValueError(f"{row['label']!r}'s {question} moved — this migration only ADDS")

    # **EVERY ROW MUST DIFFER FROM THE DEFAULT** — `db/0013`'s discipline, as `db/0032` runs it,
    # with the fourth question's default beside the three.
    defaults = {"compiles_to_content": True, "opens_clause": True, "states_number": False,
                "admits_roles": None}
    for row in UD_READING_ROWS:
        for question, answer in row["reads"].items():
            if question not in defaults:
                raise ValueError(f"{question!r} has no default — a reader could not know what a "
                                 f"label with no row means")
            if answer == defaults[question]:
                raise ValueError(f"{row['label']!r} says {question}={answer}, which IS the default: "
                                 f"the table holds what differs")

    # **A SET, AND ONLY ABOUT RELATIONS.** Sorted and duplicate-free, so no reader can mistake the
    # storage order for the ranking this migration deletes; non-empty, because a relation admitting
    # NO role would refuse every closed-class form under it, which nobody has ruled.
    for row in UD_READING_ROWS:
        admits = row["reads"].get("admits_roles")
        if admits is None:
            continue
        if row["inventory"] != "relation":
            raise ValueError(f"{row['label']!r} is not a relation — only a relation admits roles")
        if not admits or admits != sorted(set(admits)):
            raise ValueError(f"{row['label']!r}'s admits_roles is not a sorted, non-empty set")
    if sum("admits_roles" in r["reads"] for r in UD_READING_ROWS) != len(_ADMITS):
        raise ValueError("one admissible set per relation the map held — no more, no fewer")


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(UdReadingDoc, UD_READING_ROWS)
