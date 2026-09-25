"""0038 — UD readings v3: **the gap a zero relative leaves** — a fifth question (G5, the Captain's
ruling of 2026-09-25).

**THE QUESTION.** «the fish the cat ate» and «the day I slept» are one tree — `acl:relcl`, a subject,
no object, no pronoun, no stranded marker — and the antecedent is the OBJECT in one and an
ADVERBIAL in the other. G5 withheld every such clause (`docs/parser-compiler/
202609241130_the-fixpoints-eleven.md`, «STOPPED»), and `tools/relative_gap_bench.py` measured the
knowledge that could tell them apart: 113 hand-labelled zero relatives, 107 in the withheld shape.

**THE RULING, IN HIS TERMS** *(the Captain, 09-25 — «agreement, plus two»)*:

    1. the gap's role is written only when the verb frames and the antecedent's supersense AGREE;
       any disagreement withholds, as today
    2. a PASSIVE relative never has an object gap — tree shape, frame
    3. two curation rows for the blind spots, `time` → time and `way` → manner — knowledge (the
       `db/0019` `happy` precedent)

The agreement is code (`Compiler._zero_gap`): the verb's primary sense has an object frame and the
antecedent names no circumstance → the object; it has none and the antecedent names one → that
circumstance's box; anything else withholds. **What the antecedent names is THIS row** — the
supersense half of the agreement, which the bench held as a fixed map in its own source.

**WHY A READING OF `acl:relcl` AND NOT A TABLE OF ITS OWN.** The rules answer one question only the
relative clause asks — nothing else in the station wants to know whether «day» names a time *as a
gap* (a marked phrase already has its marker's rules, `db/0012`) — and this table is where the
station keeps what it reads on top of a UD label, with a default for a miss. A new collection would
be a model, a reader and a loader for five rules; the subject-role table would be the wrong name for
them. The rules are written in `MarkerSelector`'s vocabulary and RUN by it, so the adverbial gap is
settled by the same machinery that settles «at noon» against «at the door».

**THE RULES** — first match wins, and there is **NO DEFAULT**, on purpose:

    lemma     time    -> time        WordNet files «time» `noun.event`   (the ruling's row)
    lemma     way     -> manner      WordNet has no class for manner      (the ruling's row)
    nominal   noun.time      -> time
    nominal   noun.location  -> location
    nominal   noun.motive    -> reason      — heard, and it names no box

*No default* because silence is half of the agreement: «the fish the cat ate» is an object gap
exactly because «fish» names no circumstance. A default would make every antecedent a
circumstance and every object relative a disagreement.

**`noun.motive` NAMES NO BOX, AND IS HERE ANYWAY.** tkzip has no reason box — a reason is a JOIN
(«because», `db/0008`'s causal markers), and a join cannot be said of a variable. So «the reason he
left» withholds. But the rule must still be HEARD: without it, «the reason I asked» — `ask` has an
object frame, and «reason» would be silent — would compile to `ask(patient = reason)`, a wrong
complete zip (the bench's `p26`). A kind the station hears and cannot place is a withholding; a kind
it never hears is an object.

**THE COST, STATED BY THE CAPTAIN, AND KEPT BESIDE THE ROWS**: *rows for exactly the bench's two
wrongs is tuning on the test.* So they are trusted only if a held-out set written AFTER them holds —
the `held-out` group of `tools/relative_gap_bench.py`, ~20 fresh zero relatives on time · way ·
moment · reason · place heads, never seen when these rows were written.

**Written by the 1st Officier on 2026-09-25, on the Captain's ruling of the same day. Nothing is
applied until the Captain says so.**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, UdReadingDoc
from tk2.migrations import ensure_collections

VERSION = 3

#: The ruling every rule below rests on, verbatim enough to be read without this file.
_RULING = ("the Captain, 2026-09-25 («agreement, plus two»): the gap's role is written only when the "
           "verb frames and the antecedent's supersense AGREE, any disagreement withholds; a passive "
           "relative never has an object gap; `time` → time and `way` → manner are curation rows for "
           "the resource's two blind spots — trusted only if a held-out set written after them holds")

#: The bench the supersense half was measured on, and its fixed map.
_BENCH = ("tools/relative_gap_bench.py, 2026-09-25 — 107 zero relatives in the withheld shape; the "
          "supersense candidate's map, stated before measuring, was the classes WordNet names for "
          "circumstances: noun.time → time, noun.location → place, noun.motive → reason")

#: The two curation rows, each with the question it answers and what the resource says instead.
#: `resource_says` is WordNet's primary-sense class for the lemma, as read on 2026-09-25 — recorded
#: so the check below can ask the lookup's own question without loading WordNet at import.
CURATED = [
    {"lemma": "time", "then": "time", "resource_says": "noun.event",
     "why": "«the time we laughed» is WHEN we laughed. WordNet files the primary «time» "
            "(`time.n.01`, an instance or single occasion) under noun.event, so the resource's "
            "class misses the everyday temporal head; the bench's `p04` («I miss the time we ate "
            "together») came out an object for it"},
    {"lemma": "way", "then": "manner", "resource_says": "noun.attribute",
     "why": "«the way she laughs» is HOW she laughs. WordNet has no lexicographer file for manner "
            "at all, and files the primary «way» under noun.attribute; the bench's `p28` («The way "
            "you sing is sad») came out an object for it"},
]

#: The supersense rules — the bench's fixed map, the one the Captain's ruling was measured with,
#: written in the tkzip box each kind names.
SUPERSENSE = [
    ("noun.time", "time", "a stretch or point of time: «the day I slept», «the night she died»"),
    ("noun.location", "location", "a place: «the place we sleep» — tkzip's box for a place is "
                                  "`location`"),
    ("noun.motive", "reason", "a reason: «the reason he left» — HEARD so it disagrees with an object "
                              "frame, and it names no box: tkzip says a reason with a join"),
]

#: Kinds a rule may name that are NOT a tkzip box, and why each is still a rule. A kind outside
#: this and outside the circumstance boxes is a typo the station would silently drop.
NAMES_NO_BOX = {"reason": "tkzip has no reason box — a reason is a JOIN (`db/0008`'s causal "
                          "markers) — and it must still be heard, or `p26` compiles wrong"}

#: The circumstance boxes an adverbial gap may fill — tkzip's own names (`Role`), and the only ones
#: the ruling's four kinds (time · place · manner · reason) can reach.
CIRCUMSTANCE_BOXES = ("location", "manner", "time")

ADVERBIAL_GAP = {"selector": [
    *({"reads": "lemma", "is": [row["lemma"]], "then": row["then"]} for row in CURATED),
    *({"reads": "nominal", "is": [supersense], "then": then} for supersense, then, _ in SUPERSENSE),
]}

LABEL = "acl:relcl"


def build_rows(previous: list[dict]) -> list[dict]:
    """v2's rows carried forward at v3, and the fifth question written onto `acl:relcl` — a new
    row, since nobody read that label before."""
    out = []
    for row in previous:
        if row.get("version") != 2:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = VERSION
        new["reads"] = dict(new.get("reads") or {})
        out.append(new)
    out.append({
        "version": VERSION,
        "inventory": "relation",
        "label": LABEL,
        "reads": {"adverbial_gap": ADVERBIAL_GAP},
        "source": f"{_RULING}; {_BENCH}",
        "note": "which circumstance a zero relative's antecedent names, where the tree leaves the "
                "gap unnamed — «the day I slept» · «the way she laughs» — and silence where it "
                "names none, which is half of what makes «the fish the cat ate» an object gap. "
                + " · ".join(f"{row['lemma']} → {row['then']}: {row['why']}" for row in CURATED)
                + " · " + " · ".join(f"{s} → {t}: {why}" for s, t, why in SUPERSENSE),
        "position": max((r["position"] for r in out), default=-1) + 1,
    })
    return out


def _previous_rows():
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 34), None)
    if found is None:
        raise RuntimeError("0034 is gone — it holds the version this one extends")
    return found.load().UD_READING_ROWS


UD_READING_ROWS = build_rows(_previous_rows())


def _check() -> None:
    from tk2.language.markers import MarkerSelector

    before = _previous_rows()
    seen = set()
    for row in UD_READING_ROWS:
        key = (row["inventory"], row["label"])
        if key in seen:
            raise ValueError(f"{key} is read twice — the index refuses it and so does sense")
        seen.add(key)
        if not row["reads"] or not row["source"]:
            raise ValueError(f"{row['label']!r} states no reading or no source")

    # **NOTHING v2 SAID MOVED.** A fifth question; no old one re-answered.
    now = {(r["inventory"], r["label"]): r["reads"] for r in UD_READING_ROWS}
    for row in before:
        if now[(row["inventory"], row["label"])] != row["reads"]:
            raise ValueError(f"{row['label']!r}'s reading moved — this migration only ADDS")
    if len(UD_READING_ROWS) != len(before) + 1:
        raise ValueError("one row added, on `acl:relcl`, and no other")

    # **EVERY ROW MUST DIFFER FROM THE DEFAULT** — `db/0013`'s discipline, with the fifth default.
    defaults = {"compiles_to_content": True, "opens_clause": True, "states_number": False,
                "admits_roles": None, "adverbial_gap": None}
    for row in UD_READING_ROWS:
        for question, answer in row["reads"].items():
            if question not in defaults:
                raise ValueError(f"{question!r} has no default")
            if answer == defaults[question]:
                raise ValueError(f"{row['label']!r} says {question}={answer}, which IS the default")

    rules = ADVERBIAL_GAP["selector"]
    # **NO DEFAULT.** Silence is the object half of the agreement; a default would make every
    # antecedent name a circumstance, and every object relative a disagreement.
    if any(rule["reads"] == "default" for rule in rules):
        raise ValueError("the adverbial gap's rules must not end in a default — silence is an answer")
    # **THE ORDER IS THE RULE** (`db/0025`'s check): a lemma rule behind a supersense rule is never
    # reached for a word the supersense also classifies.
    first_nominal = next(at for at, rule in enumerate(rules) if rule["reads"] == "nominal")
    if any(rule["reads"] == "lemma" for rule in rules[first_nominal:]):
        raise ValueError("a lemma rule sits behind a supersense rule and may never be reached")
    for rule in rules:
        if rule["reads"] not in ("lemma", "nominal"):
            raise ValueError(f"the antecedent is read by its lemma or its class, not {rule['reads']!r}")
        if rule["then"] not in CIRCUMSTANCE_BOXES and rule["then"] not in NAMES_NO_BOX:
            raise ValueError(f"{rule['then']!r} is neither a circumstance box nor a kind heard on "
                             f"purpose — the station would drop it in silence")

    # **THE CHECK ASKS THE LOOKUP'S OWN QUESTION**, through the station's own runner, with the
    # resource answering what it answered when these rows were written. Each curated row must be
    # NEEDED — the supersense rules alone miss the word — and must WIN once it is there.
    said = {row["lemma"]: row["resource_says"] for row in CURATED}
    selector = MarkerSelector(supersense=lambda lemma, _upos: said.get(lemma))
    alone = {"selector": [r for r in rules if r["reads"] == "nominal"]}
    for row in CURATED:
        ask = {"nominal_lemma": row["lemma"], "nominal_upos": "NOUN",
               "head_lemma": row["lemma"], "head_upos": "NOUN"}
        if selector.settle(alone, **ask) is not None:
            raise ValueError(f"{row['lemma']!r}: the resource's own class already names a kind — "
                             f"the row is noise")
        settled = selector.settle(ADVERBIAL_GAP, **ask)
        if settled is None or settled.role != row["then"]:
            raise ValueError(f"{row['lemma']!r} should read {row['then']!r} and reads "
                             f"{settled and settled.role!r}")


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(UdReadingDoc, UD_READING_ROWS)
