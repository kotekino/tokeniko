"""0012 — closed classes version 6: the thirteen ambiguous markers learn WHAT SETTLES THEM.

**THE HOLE THIS CLOSES IS `db/0008`'s OWN.** That migration kept every candidate rather than
picking one — *«a row that named ONE would be a lie the compiler could not detect»* — and said where
the answer would come from: *«the selection is the compiler's — from the UD dependency label and,
where that is not enough, nearest-anchor geometry on the head verb»*. The dependency half landed
with the compile core. This is the other half, **and the geometry turned out to be the wrong
instrument.**

**WHAT IT IS INSTEAD: THE RESOURCE'S OWN SUPERSENSE.** WordNet files every synset in a lexicographer
file whose name is a broad semantic class — `noun.time`, `noun.person`, `noun.location`,
`verb.motion`, `verb.communication` — **26 for nouns and 15 for verbs, published and closed.** That
is the same property that made Universal Dependencies the station's gate: both ends of the mapping
are finite, so a table from a supersense to a tkzip role can be COMPLETE rather than merely large.

**WHY NOT THE GEOMETRY, MEASURED AND NOT ASSUMED.** «Is a pool a place?» is a question about the
TAXONOMY, and the dictionary chapter's standing ruling is that cosine does not answer taxonomy —
*«dictionary cosine is co-occurrence, not hypernymy; true cross-abstraction edges read FAR»*. Benched
on 52 cases with their gold:

    selector                       independent        the curation's own        named individuals
    first candidate (the baseline)  8 ok  3 wrong      11 ok  19 wrong           7 ok   4 wrong
    nearest-anchor geometry         6 ok  3 wrong      14 ok   2 wrong 14 mute   4 ok   0 wrong 7 mute
    THE SUPERSENSE                 11 ok  0 wrong      29 ok   1 wrong           9 ok   2 wrong

The geometry is mute on 14 of 30 — most everyday nouns are not among the base's 4,555 dimensions,
and the sense projection that reaches them shares no column with any anchor. Where it does speak it
is no better. Adding it BEHIND the supersense made the independent bucket **worse**, because it
overrode a default that was right. Record:
`docs/parser-compiler/202609161010_the-ambiguous-markers.md`.

**THE PRIMARY SENSE, AND NOT THE BEST OF ALL OF THEM** — `db/0006`'s rule, and here it is not a
preference. Reading every sense and taking the strongest was tried first and returns `pool` as a
TIME, `table` as a TIME and `dog` as an INSTRUMENT: a word's eighth reading is a different word.

**WHAT A ROW NOW CARRIES.** `compiled.selector` — an ORDERED list, first match wins, ending in a
`default` that is the curation's own best-first answer:

    {"reads": "nominal",  "is": ["noun.time"],  "then": "time"}     # «at noon»
    {"reads": "verb",     "is": ["verb.motion"], "then": "destination"}  # «walk to the station»
    {"reads": "head_pos", "is": ["VERB"],       "then": "source"}   # «made OF titanium»
    {"reads": "default",  "then": "location"}

**A `default` IS AN ANSWER AND IT IS NAMED AS ONE.** The compile core abstained on these markers
because *«picking the first candidate would be exactly the silently-complete nearest fit
requirement 8 forbids»* — and the operative word was SILENTLY. A default that the zip's bookkeeping
records as a default is not silent, and abstaining on «in the pool» loses a location any reader
would call obvious. The compiler keeps them apart: a rule that fires is settled, a default is
counted in `Compiled.defaulted`, and req 4's confidence scalar is entitled to the difference.

**THREE ERRORS SURVIVE AND ARE NOT HIDDEN.** «at speed» reads TIME because WordNet files
`speed.n.01` under `noun.time` (a distance per unit time — the resource is right and the rule is
coarse). «I ate with Anna» and «went with Anna» read INSTRUMENT because WordNet holds `anna` only as
an Indian coin. **Both Anna cases are the named-individual hole**, which is parked and has its own
answer waiting (a type-centroid vector plus a context-scoped identity) — not something a better
marker rule should paper over.

**Nothing else moves**: no form arrives or leaves, no role is re-typed, and the single-word FORMS
are identical — that set is the dictionary's gloss-word exclusion set, and a migration that moved it
would move D and the sealed base with it.

**Written by the QM on 2026-09-16, on the Captain's «go with the ambiguous markers».**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, ClosedClassDoc
from tk2.migrations import ensure_collections

VERSION = 6

# ── the probes a rule may run ────────────────────────────────────────────────────────────────────
# FRAME lives in `tk2/language/markers.py`, which knows how to RUN these; the rules are here because
# «which supersense means which role for THIS preposition» is a contingent fact about English.
NOMINAL = "nominal"    # the supersense of the marked nominal's primary sense
VERB = "verb"          # the supersense of the head verb's primary sense
HEAD_POS = "head_pos"  # UD's POS for the word the phrase hangs off — no dictionary needed
DEFAULT = "default"    # nothing chose; the curation's best-first answer, recorded as a default

#: The one answer that is a FIELD of the record rather than a box of the clause (req 26). Named so
#: the check below can admit it without admitting anything else.
FIELD_RELATION = "relation"

#: The supersense groups the rules quantify over, named so a change is one edit and not seventeen.
TIME = ["noun.time"]
ANIMATE = ["noun.person", "noun.animal"]
PLACE = ["noun.location"]
THING = ["noun.artifact"]
STUFF = ["noun.substance"]
TERRAIN = ["noun.object", "noun.location"]
IDEA = ["noun.cognition", "noun.communication"]
MOTION = ["verb.motion"]
TRANSFER = ["verb.communication", "verb.possession"]


def _rule(reads, then, is_=None):
    rule = {"reads": reads, "then": then}
    if is_ is not None:
        rule["is"] = list(is_)
    return rule


#: form -> the ordered rules that settle it. First match wins; the last rule is always a default.
SELECTORS: dict[str, list[dict]] = {
    # «at noon» is a time, «at the door» a place. `manner` («at speed») is real and is not reachable
    # from a supersense: WordNet files speed itself under `noun.time`.
    "at": [_rule(NOMINAL, "time", TIME), _rule(DEFAULT, "location")],

    # «in May» · «written in ink» · «in Paris». The substance rule is what makes ink an instrument.
    "in": [_rule(NOMINAL, "time", TIME), _rule(NOMINAL, "instrument", STUFF),
           _rule(DEFAULT, "location")],

    # «on Monday» · «a lecture on physics» · «on the table».
    "on": [_rule(NOMINAL, "time", TIME), _rule(NOMINAL, "topic", IDEA),
           _rule(DEFAULT, "location")],
    "upon": [_rule(NOMINAL, "time", TIME), _rule(NOMINAL, "topic", IDEA),
             _rule(DEFAULT, "location")],

    # «by noon» · «by Anna» · «by the river» · «by train». The AGENT reading is usually settled
    # before this runs — UD's own `obl:agent` names it — so this is the case where it is not.
    "by": [_rule(NOMINAL, "time", TIME), _rule(NOMINAL, "agent", ANIMATE),
           _rule(NOMINAL, "path", TERRAIN), _rule(DEFAULT, "instrument")],

    # THE ONE `db/0008` NAMED: give-like against go-like. The nominal is asked FIRST, because a
    # person is a recipient under any verb; the verb decides for everything that is not a person.
    # («go to school» is why: WordNet files a school as a `noun.group`, and a nominal-only rule that
    # reached for institutions made the destination a recipient.)
    "to": [_rule(NOMINAL, "recipient", ANIMATE), _rule(VERB, "destination", MOTION),
           _rule(VERB, "recipient", TRANSFER), _rule(DEFAULT, "destination")],

    # «I ate with Anna» against «I ate with a fork» — animacy, and nothing else.
    "with": [_rule(NOMINAL, "comitative", ANIMATE), _rule(DEFAULT, "instrument")],
    "without": [_rule(NOMINAL, "comitative", ANIMATE), _rule(DEFAULT, "instrument")],

    # «for an hour» · «for Anna» · «left for Paris».
    "for": [_rule(NOMINAL, "duration", TIME), _rule(NOMINAL, "beneficiary", ANIMATE),
            _rule(NOMINAL, "destination", PLACE), _rule(DEFAULT, "beneficiary")],

    # «over a week» · «walked over the bridge» · «over the table».
    "over": [_rule(NOMINAL, "duration", TIME), _rule(VERB, "path", MOTION),
             _rule(DEFAULT, "location")],

    # **NO DICTIONARY IS NEEDED FOR `of`, AND ASKING ONE WOULD BE A MISTAKE.** «made OF titanium»
    # hangs off a VERB and is the material; «the office OF the Chair» hangs off a NOUN and is the
    # POSSESSOR — which tkzip keeps inside the record as a field (req 26) and not as a box of the
    # clause at all. UD already says which, so this rule reads the tree and stops.
    #
    # `relation` is a FIELD and not one of the eighteen roles, which is why the check below admits
    # it by name. The precedent is `UD_DEP_SETTLES_ROLE` in `tk2/language/closed.py`: `nmod:poss`
    # settles to `relation` there for the same reason and with the same exception.
    "of": [_rule(HEAD_POS, "source", ["VERB"]),
           _rule(HEAD_POS, "relation", ["NOUN", "PROPN"]),
           _rule(DEFAULT, "complement")],

    # A marked nominal puts these in a place; the bare directional reading has no nominal to mark
    # and never reaches this selector at all.
    "up": [_rule(DEFAULT, "location")],
    "down": [_rule(DEFAULT, "location")],
    "off": [_rule(DEFAULT, "source")],
    "under": [_rule(DEFAULT, "location")],
    "underneath": [_rule(DEFAULT, "location")],

    # «works as a doctor» is a manner; «as tall as» is a measure and marks an ADJECTIVE, not a noun.
    "as": [_rule(NOMINAL, "manner", ANIMATE), _rule(DEFAULT, "measure")],
}


def build_rows(previous: list[dict]) -> list[dict]:
    """Version 6 = version 5 with `selector` on the ambiguous box markers. Nothing else changes."""
    out = []
    for row in previous:
        if row.get("version") != 5:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = VERSION
        compiled = new.get("compiled") or {}
        rules = SELECTORS.get(row["form"])
        if rules and compiled.get("kind") == "box" and len(compiled.get("roles", ())) > 1:
            new["compiled"] = {**compiled, "selector": [dict(r) for r in rules]}
        out.append(new)
    return out


def _previous_rows():
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 11), None)
    if found is None:
        raise RuntimeError("0011 is gone — it holds the version this one extends")
    return found.load().CLOSED_CLASS_ROWS


CLOSED_CLASS_ROWS = build_rows(_previous_rows())

#: Unchanged by this version — and checked, because it is the dictionary's exclusion set.
CLOSED_CLASS_FORMS = tuple(
    sorted({row["form"] for row in CLOSED_CLASS_ROWS if " " not in row["form"]})
)


def _check() -> None:
    """A rule may never name a role the row itself does not offer — that would be the migration
    inventing a role rather than choosing among the ones the curation declared."""
    for row in CLOSED_CLASS_ROWS:
        compiled = row.get("compiled") or {}
        for rule in compiled.get("selector", ()):
            if rule["then"] not in compiled["roles"] and rule["then"] != FIELD_RELATION:
                raise ValueError(
                    f"{row['form']!r}: the selector names {rule['then']!r}, which is not one of "
                    f"its candidates {tuple(compiled['roles'])}"
                )
        if compiled.get("selector") and compiled["selector"][-1]["reads"] != DEFAULT:
            raise ValueError(f"{row['form']!r}: the selector does not end in a default")


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(ClosedClassDoc, CLOSED_CLASS_ROWS)
