"""0008 — closed classes version 2: the 383 rows learn WHAT THEY COMPILE TO.

**THE COLUMN WAS LEFT EMPTY ON PURPOSE, AND THE REASON HAS EXPIRED.** `ClosedClassDoc.compiled`
says so in its own docstring: *«E3's column, and empty by construction here … a map with no fixed
shape yet because tkzip v2 is E2, and writing a guess into it now would be exactly the
load-bearing knowledge-in-code this table exists to end, merely relocated.»* **tkzip v2 was frozen
on 2026-09-14.** The shape exists now, so the column can be filled against it rather than against a
guess.

**WHAT E3 FOUND WHEN IT LOOKED.** All 135 prepositions are typed `role_marker` and **not one says
which of the eighteen roles it marks** — which is the question E2's drill parked when it left
`direction`'s marker cluster to this epic. And in the Captain's live v1 traffic, «role marker» is
the phenomenon v1 read WRONG most often: **54% of 184 journeys** (`tools/journey_ledger.html`).
The empty column and the worst failure rate are the same hole.

**AND 37 OF THE 137 MARKERS ARE TYPED WRONG.** They do not mark a box at all. Ruled by the Captain,
2026-09-15, on the measurement below:

    causal      9   «because of» «due to» «owing to» «thanks to» …   -> a JOIN, operator IMPLY
    concessive 10   «despite» «in spite of» «notwithstanding» …      -> a JOIN, operator AND
    exceptive  15   «except» «save» «but for» «other than» …         -> a QUANTIFIER restriction
    comparative 3   «than» «versus» «as»                             -> stay markers, role MEASURE

**THE CAUSAL CASE IS E2'S OWN COLLAPSE, ARRIVING WHERE IT WAS PREDICTED.** There is no CAUSE
relation in tkzip and there never was one: *a cause is what implies its effect* (the Captain's
premise, in a deterministic world). «I stayed home because of the rain» is an IMPLY join with BOTH
halves claimed — which is exactly how the format already distinguishes it from «if it rains I stay
home» (join claimed, halves EMPTY). Nothing new is invented here; a mis-typed row is corrected.

**THE CONCESSIVE CASE IS A LOSS, AND IT IS RECORDED AS ONE RATHER THAN HIDDEN.** «Despite the rain
I went out» is truth-functionally «the rain AND I went out» — the concession is a DEFEATED
EXPECTATION, which is not truth-functional and has nowhere to live: `JoinRow` carries an operator
and two operands and no marker. So these ten forms compile to AND and the flavour is parked, at the
same address E2 sent irony: the figurative layer. **This is named in `compiled` as
`pragmatic: "concessive"`, so the day that layer is built it can find its own cases** rather than
being told the zips were lossless.

**THE EXCEPTIVE CASE NEEDS NO NEW SLOT, WHICH IS WHY IT IS NOT A FRAME BUG.** «Every cat except Tom
sleeps» is «for all x, if x is a cat and x is not Tom, x sleeps» — a quantifier, a restriction and a
negation, all of which the format has. The row records WHICH WAY the restriction runs (`exclude` for
«except», `include` for «including» and «in addition to»), because that is knowledge about the word
and not about the mechanism.

**THE THIRTEEN AMBIGUOUS MARKERS KEEP ALL THEIR CANDIDATES, ORDERED.** `by` is instrument, agent,
path or time; `to` is recipient or destination; `for` is beneficiary, destination or duration. A row
that named ONE would be a lie the compiler could not detect. So `roles` is a LIST, best-first, and
the selection is the compiler's — from the UD dependency label and, where that is not enough,
nearest-anchor geometry on the head verb (`give`-like → recipient, `go`-like → destination). **The
mapping is curation and lives here; the selector is frame and lives in code** — the standing law's
first clause, applied to the case it was written for.

**Applied by the QM on the Captain's explicit ruling, 2026-09-15: «1. agreed 2. confirmed 3. your
reads look right, go».**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, ClosedClassDoc
from tk2.migrations import ensure_collections

VERSION = 2

# ── the compiled vocabulary ──────────────────────────────────────────────────────────────────────
# `kind` says WHERE the form lands in a zip. Everything else is the detail that landing needs.
BOX = "box"                  # fills a role box; `roles` is best-first when the form is ambiguous
JOIN = "join"                # joins two rows; `operator` is one of tkzip's ten
RESTRICTION = "restriction"  # narrows or widens a quantifier's set
ENTITY = "entity"            # resolves to something in the world, from context
QUANTIFIER = "quantifier"    # binds a variable
OPEN = "open"                # leaves a slot OPEN — which is what a question IS (there is no mood)
PREFIX = "prefix"            # a scope-bearing element over a MATRIX
THEATRE = "theatre"          # moves the theatre, not the row
STRUCTURE = "structure"      # compiles to nothing: it was glue
DETERMINATION = "determination"   # sets the box's `determination` field, which is not `quantity`
AMBIGUOUS = "ambiguous"      # two readings the compiler must choose between; `candidates` holds both
FIELD = "field"              # fills a FIELD of the box rather than a box — the possessor


def _box(*roles):
    return {"kind": BOX, "roles": list(roles)}


#: form -> the roles it may mark, BEST-FIRST. Thirteen carry more than one and say so.
MARKERS = {
    # unambiguous circumstantials
    **{f: _box("location") for f in (
        "above", "across", "alongside", "amid", "amidst", "among", "amongst", "astride", "atop",
        "behind", "below", "beneath", "beside", "between", "beyond", "inside", "near", "near to",
        "next to", "opposite", "outside", "outside of", "close to", "far from", "in front of",
        "on top of", "within", "within reach of", "ahead of", "aside", "apart", "against")},
    **{f: _box("time") for f in (
        "after", "before", "since", "ago", "following", "prior to", "subsequent to", "circa",
        "pending", "as from", "as of")},
    **{f: _box("duration") for f in ("during", "throughout", "till", "until")},
    **{f: _box("path") for f in ("along", "around", "round", "past", "via", "through")},
    **{f: _box("direction") for f in ("toward", "towards", "out", "onto", "unto")},
    **{f: _box("destination") for f in ("into", "up to")},
    **{f: _box("source") for f in ("from", "out of", "away from", "apart from")},
    **{f: _box("instrument") for f in ("by means of", "per")},
    **{f: _box("comitative") for f in ("together with", "along with")},
    **{f: _box("beneficiary") for f in ("on behalf of", "in favour of")},
    **{f: _box("topic") for f in (
        "about", "concerning", "regarding", "respecting", "as to", "as for", "in terms of",
        "with regard to", "with respect to")},
    **{f: _box("measure") for f in ("times", "plus", "minus", "less", "than", "versus")},
    **{f: _box("manner") for f in ("like", "unlike", "according to")},

    # ── THE THIRTEEN AMBIGUOUS ONES, every candidate kept, best-first ──────────────────────────
    "at": _box("location", "time", "manner"),            # at the door / at noon / at speed
    "in": _box("location", "time", "instrument", "manner"),   # in Paris / in May / in ink
    "on": _box("location", "time", "topic"),             # on the table / on Monday / on physics
    "upon": _box("location", "time", "topic"),           # `on`, and the rows say so rather than alias
    "by": _box("instrument", "agent", "path", "time"),   # by train / by Anna / by the river / by noon
    "to": _box("destination", "recipient"),              # go to Paris / give to Anna
    "of": _box("complement", "source"),                  # cat of my sister / made of wood
    "with": _box("instrument", "comitative"),            # cut with a knife / went with Anna
    "for": _box("beneficiary", "destination", "duration"),   # for Anna / left for Paris / for an hour
    "over": _box("location", "path", "duration"),        # over the table / over the bridge / over a week
    "under": _box("location", "source"), "underneath": _box("location", "source"),
    "up": _box("direction", "location"),                 # walked up / up the hill
    "down": _box("direction", "location"),
    "off": _box("source", "direction"),
    "as": _box("manner", "measure"),                     # works as a doctor / as tall as
}

#: «without a knife» is the instrument NEGATED — the Captain's read, 2026-09-15. It fills the box and
#: raises the negation prefix over the row, which is why it cannot be a plain `_box`.
MARKERS["without"] = {"kind": BOX, "roles": ["instrument", "comitative"], "negates": True}

#: A cause is what implies its effect. The MARKED phrase is the antecedent.
CAUSAL = ("because of", "due to", "owing to", "thanks to", "on account of", "in case of", "given",
          "considering", "depending on")
#: Truth-functionally AND. The defeated expectation is not truth-functional and is parked, named.
CONCESSIVE = ("despite", "in spite of", "notwithstanding", "regardless of", "irrespective of",
              "contrary to", "instead of", "in lieu of", "in place of", "rather than")
#: Narrows (or widens) the quantifier's set; no new slot — quantifier + restriction + negation.
EXCLUDING = ("except", "except for", "excepting", "excluding", "save", "bar", "barring", "but",
             "but for", "other than", "aside from", "besides")
INCLUDING = ("including", "in addition to")


def _compiled_for(row: dict) -> dict:
    """What ONE v1 row compiles to. Returns `{}` only for a job E3 has not reached yet — and every
    such job is listed in `UNTOUCHED` below, so «empty» never means «forgotten»."""
    form, role = row["form"], row["role"]

    if role == "role_marker":
        if form in CAUSAL:
            return {"kind": JOIN, "operator": "imply", "antecedent": "marked",
                    "was": "role_marker"}
        if form in CONCESSIVE:
            return {"kind": JOIN, "operator": "and", "pragmatic": "concessive",
                    "lossy": True, "was": "role_marker"}
        if form in EXCLUDING:
            return {"kind": RESTRICTION, "polarity": "exclude", "was": "role_marker"}
        if form in INCLUDING:
            return {"kind": RESTRICTION, "polarity": "include", "was": "role_marker"}
        return MARKERS.get(form, {})

    if role in ("referential", "demonstrative"):
        return {"kind": ENTITY, "resolve": "context"}
    if role in ("reflexive", "reciprocal"):
        return {"kind": ENTITY, "resolve": "same_row"}
    if role == "possessive":
        return {"kind": ENTITY, "resolve": "context", "fills": "relation"}
    if role == "quantificational":
        # THE ARTICLES ARE NOT QUANTIFIERS, and v1's own `features` already said so («force»:
        # definite / indefinite). tkzip keeps DETERMINATION as its own field on the box, beside
        # `quantity` — «the cat» and «a cat» differ in determination and are both singular. Typing
        # them quantificational is the same defect as the 33 markers: a traditional grammar label
        # chosen before the format existed.
        force = row.get("features", {}).get("force")
        if force in ("definite", "indefinite"):
            return {"kind": DETERMINATION, "determination": force, "was": "quantificational"}
        return {"kind": QUANTIFIER, "quantity": _QUANTITY.get(form)}
    if role in ("interrogative", "relative", "free_relative"):
        return {"kind": OPEN, "binds": "antecedent" if role != "interrogative" else None}
    if role == "negation":
        return {"kind": PREFIX, "element": "negation"}
    if role == "modality":
        # **TKZIP HAS NO FUTURE MODALITY, AND NO HABITUAL ONE.** `Modality` is `necessity` /
        # `possibility`, frozen — because E2 ruled that a forecast is a FUTURE THEATRE, not a modal
        # operator. v1 typed `will`, `would` and `'ll` as modality with «modality: future», and
        # `used` (to) as «habitual» — all four move the theatre instead.
        feat = row.get("features", {})
        if feat.get("modality") in ("future", "habitual") or form in ("'ll",):
            return {"kind": THEATRE, "tense": feat.get("tense", "future" if form == "'ll" else None)
                    or ("past" if feat.get("modality") == "habitual" else "future"),
                    "aspect": "habitual" if feat.get("modality") == "habitual" else None,
                    "was": "modality"}
        named = _MODALITY.get(form)
        if named is None:
            # `'d` is «would» or «had» and v1's own note says «genuinely ambiguous». It keeps both
            # candidates for the same reason the thirteen markers do: a row that named one would be
            # a lie the compiler could not detect.
            return {"kind": AMBIGUOUS, "candidates": [
                {"kind": PREFIX, "element": "modality", "modality": "possibility"},
                {"kind": THEATRE, "tense": "past", "aspect": "perfect"}]}
        return {"kind": PREFIX, "element": "modality", "modality": named}
    if role == "coordinator":
        return {"kind": JOIN, "operator": _COORDINATOR.get(form, "and")}
    if role == "subordinator":
        return {"kind": JOIN, "operator": _SUBORDINATOR.get(form, "imply")}
    if role == "tense_aspect":
        # **PLAIN COPULAR `be` COMPILES TO STRUCTURE AND EARNS NO DIMENSION** (req 31): «the cat is
        # cute» is *cat + cute, no verb* — the Captain's own first draft, verbatim. It is not a
        # theatre move; `become`, `seem` and `remain` keep a home and `be` does not. Found by the UD
        # gate on «Sue is a teacher», where UD labels it `cop` and the row said «theatre».
        # The COMPILER still has to tell copular `be` from auxiliary `be` («she is running», `aux`)
        # and existential `be` («there is a cat», which IS content) — UD's relation is what says
        # which, and that is the compile core's job, not this row's.
        if row["form"] in _COPULAR_BE:
            return {"kind": STRUCTURE, "when": "cop", "otherwise": THEATRE, "was": THEATRE}
        return {"kind": THEATRE}
    if role == "genitive":
        # **THE POSSESSIVE CLITIC IS NOT GLUE**, found by the UD gate on UD's own example, 2026-09-15.
        # UD analyses «the Chair 's office» as `case('s)` + `nmod(office, Chair)` and pairs it
        # explicitly with «the office OF the Chair» — the same relation, two spellings. tkzip keeps
        # the possessor INSIDE the record as `Box.relation` (req 26), so this fills a FIELD rather
        # than a box. Typing it `structure` threw the possessor away.
        return {"kind": FIELD, "field": "relation", "was": "structure"}
    if role in ("infinitive_marker", "expletive", "existential", "affirmation",
                "verb_particle", "hortative"):
        return {"kind": STRUCTURE}
    return {}


#: The forms of `be`. Copular `be` is glue; the same forms under `aux` move the theatre, and under
#: an existential reading they are content. One row cannot decide that — the dependency can.
_COPULAR_BE = {"be", "is", "am", "are", "was", "were", "been", "being", "'s", "'re", "'m"}

#: Which corner of the square each quantifier word binds. `Quantity` is tkzip's frozen enum.
_QUANTITY = {
    **{f: "universal" for f in ("all", "every", "each", "both", "everybody", "everyone",
                                "everything", "everywhere", "always", "ever")},
    **{f: "negative" for f in ("no", "none", "no one", "nobody", "nothing", "nowhere", "neither",
                               "never", "seldom")},
    # `a`, `an` and `the` are deliberately ABSENT — they are determination, not quantity.
    **{f: "existential" for f in ("some", "any", "somebody", "someone", "something", "somewhere",
                                  "anybody", "anyone", "anything", "anywhere", "several", "either",
                                  "another", "other", "such", "enough", "sometimes", "often",
                                  "once", "twice", "many", "much", "more", "most", "few", "fewer",
                                  "fewest", "little", "less", "least", "somehow", "what")},
}
_MODALITY = {
    **{f: "necessity" for f in ("must", "shall", "should", "ought", "need", "have to", "had to",
                                "has to", "got to")},
    **{f: "possibility" for f in ("can", "could", "may", "might", "would", "will", "dare")},
}
_COORDINATOR = {"and": "and", "or": "or", "nor": "nor", "but": "and", "yet": "and", "so": "imply",
                "plus": "and", "either": "or", "neither": "nor"}
#: Most subordinators are IMPLY; the record keeps the ones that are not, because that is the whole
#: content of E2's collapse — «although» is AND, «unless» is «if not».
_SUBORDINATOR = {"although": "and", "though": "and", "whereas": "and", "while": "and",
                 "unless": "imply", "if": "imply", "because": "imply", "since": "imply",
                 "so that": "imply", "in order that": "imply", "as": "imply", "that": "and"}

#: Jobs E3 has not reached. Listed so an empty `compiled` is a KNOWN gap and never a forgotten one.
UNTOUCHED = ("complementizer",)


def build_rows(previous: list[dict]) -> list[dict]:
    """Version 2 = version 1, with `compiled` filled and the 37 mis-typed markers re-typed.

    Derived from the baseline's own rows rather than re-listed, so the forms, features and sources
    cannot drift from what version 1 established: this migration declares the MAPPING, and the
    mapping is the only thing it is allowed to be the author of.
    """
    out = []
    for row in previous:
        if row.get("version") != 1:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = VERSION
        compiled = _compiled_for(row)
        new["compiled"] = compiled
        kind = compiled.get("kind")
        if kind == DETERMINATION:
            new["role"] = "determination"
            new["note"] = (row.get("note") or "") + (
                " — RE-TYPED at v2: it is an ARTICLE, not a quantifier; it sets determination.")
        elif compiled.get("was") == "modality":
            new["role"] = "tense_aspect"
            new["note"] = (row.get("note") or "") + (
                " — RE-TYPED at v2: tkzip has no future or habitual MODALITY; this moves the theatre.")
        elif row["role"] == "role_marker" and kind in (JOIN, RESTRICTION):
            new["role"] = {JOIN: "causal_marker" if compiled.get("operator") == "imply"
                           else "concessive_marker",
                           RESTRICTION: "exceptive_marker"}[kind]
            new["note"] = (row.get("note") or "") + (
                " — RE-TYPED at v2: it was `role_marker` and it marks no box. "
                f"It compiles to {kind}.")
        out.append(new)
    return out


def _previous_rows():
    from tk2.migrations import discover

    baseline = next((m for m in discover() if m.number == 1), None)
    if baseline is None:
        raise RuntimeError("the baseline is gone — it declares the rows this version carries forward")
    return baseline.load().CLOSED_CLASS_ROWS


#: Declared under the NAME the readers already look for, so `newest_migration_declaring` finds THIS
#: file rather than the baseline and the offline paths see v2 the day it is written. That mechanism
#: exists because a later migration declares only what it CHANGES — and this one changes these rows.
CLOSED_CLASS_ROWS = build_rows(_previous_rows())

#: The single-word forms, rebuilt here for the same reason the baseline builds them: the dictionary's
#: function-word exclusion runs OFFLINE, before anything is applied, and must not read a stale copy.
CLOSED_CLASS_FORMS = tuple(
    sorted({row["form"] for row in CLOSED_CLASS_ROWS if " " not in row["form"]})
)

#: The old name, kept as an alias: this file's own tests and report read `ROWS`.
ROWS = CLOSED_CLASS_ROWS


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(ClosedClassDoc, CLOSED_CLASS_ROWS)
