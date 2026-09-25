"""0037 — closed classes v20: **a purpose claims the act and not the end** (parser-compiler req 9,
the fixpoint's G1 — the Captain's rulings of 2026-09-25).

**THE RULING, IN HIS WORDS.** *«I eat to prevent my death. But maybe I die even if I eat. The
purpose is an implication, the implication can fail. […] this is my evaluation, which can be false
or imprecise […] in the case of sleeping my purpose and the implication at time t-1 is true. Not at
time t, because maybe there is a dog barking and I can't sleep.»* And the principle above it: *«We
should NEVER make exceptions of the rule: semantics in a fixed grid (roles) glued with operators.»*

So a purpose is `imply(act, end)`: the act is claimed, the end is not — the speaker says he goes,
not that he sleeps — and the join between them is his claim that the one leads to the other,
fallible like every claim.

**WHAT THE TABLE SAID, AND WHY EVERY PURPOSE ROW WAS WRONG** — measured before writing this:

    I go to sleep                 `to` is structure; the clause is ANDed on: «I go and it sleeps»,
                                  the sleep CLAIMED
    I work in order to earn money imply/both, and the compiler puts the introduced clause FIRST —
                                  imply(earn, work): «Because money earns, I work», the end claimed
                                  AND the arrow reversed
    I work so that I earn money   the same row, the same two errors

**TWO FACTS, AND BOTH ARE ABOUT THE WORD** — so both are columns of `compiled`, which is the row's
MEANING and the decompiler's key:

    asserts: antecedent    the join claims its ANTECEDENT and not its consequent. A fourth value
                           beside `both` · `neither` · `matrix` (`db/0010`), because none of those
                           says it: `matrix` is positional and does say «the main clause is
                           claimed», but it has meant «this opens a POINT OF VIEW, not a join»
                           since v4, and the compiler routes it to an attitude. Reusing it would
                           make a purpose an attitude
    antecedent: matrix     WHICH clause is the antecedent. The column is `db/0008`'s — the causal
                           prepositions have carried `antecedent: marked` since v2 («because OF
                           the rain»: the marked phrase leads) — and every subordinator left it
                           unwritten, because every one took the INTRODUCED clause: «because Y, X»
                           is Y → X, and the compiler assumed it. A purpose runs the other way, the
                           act is the main clause, so `matrix` is the column's second value.
                           Absent means what it always meant, so no other row moves

**«TO» IS A ROW OF ITS OWN, AND IT IS SELECTED BY THE CLAUSE IT INTRODUCES.** The same `to`, tagged
`PART` under `mark`, opens «I want TO sleep» (`xcomp` — a complement, which opens no row: `db/0032`)
and «I go TO sleep» (`advcl` — purpose). There it does a SUBORDINATOR's job — it joins its clause to
the matrix, as «in order to» and «so that» do — so that is its role: one row per (form, class, role)
is the table's own index, and the infinitive marker's job stays the structure row's. *«Recognised by SHAPE: stanza gives purpose as `advcl` +
«to» and a complement as `xcomp` — no list»* (the ruling). The shape is frame; that `to` means
purpose THERE is a fact about the word, so it is this row's `features.introduces`, and
`tk2.language.closed` admits a row that names a clause only under that clause. The old `to` stays
exactly as it was — structure, for every other clause — and a reader holding no tree never sees the
new one.

**«TO» IS THE VOICE.** Three subordinators now carry the meaning — `to`, `in order to`, `so that` —
and the decompiler says a purpose as «V₁ to V₂». `spoken` on `to`, and on nothing else carrying it;
that its clause is then said BARE is read off the table too, since `to` is also the infinitive
marker's form.

*«SO THAT» HAS A SECOND READING* — result, «it rained all night, so that the river flooded», where
the end IS claimed. The row has been curated `relation: purpose` since v1, and the purpose reading is
the everyday one; read as purpose, a result sentence claims LESS than it said (the flood goes
unclaimed) — half-said, which is legal. Read as it was, every purpose sentence claimed its end AND
the reversed arrow — a wrong claim, which is not.

**NOT HERE, ON PURPOSE:** «promise». *«I promised her to go to the beach»* means WE go, not I (the
Captain, 2026-09-25), so it is not the plain subject control an exception row would have recorded —
it is knowledge for the micro-nns, later. The controlled subject is the one rule, with no per-verb
row: no complement → the matrix subject; an `obj` or `iobj` → that complement.

**AND TIME IS NOT WRITTEN, BECAUSE THE FORMAT CANNOT SAY IT.** The act is at t-1 and the end at t —
relative to EACH OTHER. `Theatre` is relative to the UTTERANCE, and the infinitive carries no tense
of its own, so the end keeps no theatre and the order lives in the IMPLY's operands: antecedent
first, read with the arrow of time (tkzip req 37). A partner-relative time axis is what is missing.

**THE EXCLUSION SET DOES NOT MOVE** — `to`, `in order to` and `so that` were all forms already.

**Written by the 1st Officier on 2026-09-25, on the Captain's rulings of the same day. Nothing is
applied until the Captain says so.**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, ClosedClassDoc
from tk2.migrations import ensure_collections

VERSION = 20

#: The fourth `asserts` value, and the column that says which clause is the antecedent. A NAME and
#: its vocabulary, not a roster: which words carry them is the rows' business below.
ANTECEDENT = "antecedent"
MATRIX = "matrix"

#: The clause a row is the reading for — `tk2.language.closed` spells the same key.
INTRODUCES = "introduces"

#: The purpose meaning, as the decompiler keys it.
PURPOSE = {"kind": "join", "operator": "imply", "asserts": ANTECEDENT, ANTECEDENT: MATRIX}

_RULING = ("the Captain, 2026-09-25: «purpose is an implication, the implication can fail» — "
           "imply(act, end), the act claimed and the end not; recognised by shape, advcl + «to»")

#: The rows that already mean purpose, corrected in place: form -> why.
CORRECTED = {
    "in order to": "unambiguously purpose. v19 compiled it imply/both with the introduced clause "
                   "first — imply(earn, work) for «I work in order to earn money»: the end claimed "
                   "and the arrow reversed",
    "so that": "curated `relation: purpose` since v1, and v19 made the same two errors as «in order "
               "to». Its result reading («so that the river flooded») now claims less than it said "
               "— half-said, where the old row said the wrong thing",
}

#: **THE ONE ROW THIS MIGRATION ADDS** — `to` as the purpose it marks under an adverbial clause.
PURPOSE_TO = {
    "version": VERSION,
    "form": "to",
    "role": "subordinator",
    "word_class": "particle",
    "compiled": dict(PURPOSE),
    "features": {"relation": "purpose", INTRODUCES: "advcl"},
    "source": _RULING,
    "note": "«I go TO sleep» — the infinitive of purpose, doing a subordinator's job. The same `to` "
            "under `xcomp` («I want to sleep») is the infinitive marker's structure row, and this "
            "row is admitted only where the clause it introduces is an `advcl`. `spoken`: the voice "
            "of purpose, «V₁ to V₂»",
    "position": 137,
    "spoken": True,
}


def build_rows(previous: list[dict]) -> list[dict]:
    out = []
    for row in previous:
        if row.get("version") != 19:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = VERSION
        if row["form"] in CORRECTED and row.get("role") == "subordinator":
            new["compiled"] = dict(PURPOSE)
            note = row.get("note") or ""
            new["note"] = (f"{note} — " if note else "") + \
                f"v20: a purpose claims the act and not the end: {CORRECTED[row['form']]}"
        out.append(new)
    out.append(dict(PURPOSE_TO))
    return out


def _previous_rows():
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 36), None)
    if found is None:
        raise RuntimeError("0036 is gone — it holds the version this one extends")
    return found.load().CLOSED_CLASS_ROWS


CLOSED_CLASS_ROWS = build_rows(_previous_rows())

#: **UNCHANGED** — every form this version touches was a form already.
CLOSED_CLASS_FORMS = tuple(
    sorted({row["form"] for row in CLOSED_CLASS_ROWS if " " not in row["form"]})
)


def _meaning(row: dict) -> tuple:
    """A row's VOICE. **THIS IS `Decompiler._key()` AND IT MUST STAY THAT WAY** — see `db/0029`."""
    features = row.get("features") or {}
    return (row["role"], tuple(sorted((k, str(v)) for k, v in (row.get("compiled") or {}).items())),
            features.get("sort"), features.get("takes_number"))


#: The roles a joining word is said in — the decompiler asks the same two, in `_connective`.
JOINING_ROLES = ("coordinator", "subordinator")


def _check() -> None:
    before = _previous_rows()
    if set(CLOSED_CLASS_FORMS) != {r["form"] for r in before if " " not in r["form"]}:
        raise ValueError("THE EXCLUSION SET MOVED — this migration adds no form")
    if len(CLOSED_CLASS_ROWS) != len(before) + 1 or CLOSED_CLASS_ROWS[-1] != PURPOSE_TO:
        raise ValueError("this migration adds exactly one row, the purpose «to»")
    for row, was in zip(CLOSED_CLASS_ROWS, before):
        if row["form"] != was["form"] or row.get("role") != was.get("role") \
                or row.get("features") != was.get("features") \
                or row.get("spoken") != was.get("spoken"):
            raise ValueError(f"{was['form']!r}: a form, a role, a feature or a voice moved")
        corrected = was["form"] in CORRECTED and was.get("role") == "subordinator"
        if corrected and row["compiled"] != PURPOSE:
            raise ValueError(f"{was['form']!r} is not the purpose meaning")
        if not corrected and row.get("compiled") != was.get("compiled"):
            raise ValueError(f"{was['form']!r}: a meaning this migration does not name moved")
    if PURPOSE_TO["position"] in {r.get("position") for r in before}:
        raise ValueError("the purpose «to»'s position collides with an existing row")

    # **EVERY ROW CARRYING `asserts: antecedent` SAYS WHICH CLAUSE IS THE ANTECEDENT.** The compiler
    # orders the operands by it and never defaults it for this value — a claim about «the
    # antecedent» that does not say which one is not a claim.
    for row in CLOSED_CLASS_ROWS:
        compiled = row.get("compiled") or {}
        if compiled.get("asserts") == ANTECEDENT and compiled.get(ANTECEDENT) != MATRIX:
            raise ValueError(f"{row['form']!r} asserts its antecedent and does not say which it is")
        if compiled.get(ANTECEDENT) == MATRIX and compiled.get("asserts") != ANTECEDENT:
            raise ValueError(f"{row['form']!r}: `antecedent: matrix` is written only on a purpose "
                             f"— every other implication keeps the clause it marks")

    # **A ROW THAT NAMES A CLAUSE IS THE READING FOR THAT CLAUSE, AND ONLY FOR IT** — so the form must
    # keep a row of the same class naming none, or every other clause would lose the form entirely.
    for row in CLOSED_CLASS_ROWS:
        clause = (row.get("features") or {}).get(INTRODUCES)
        if clause is None:
            continue
        rest = [r for r in CLOSED_CLASS_ROWS if r["form"] == row["form"] and r is not row
                and r["word_class"] == row["word_class"]
                and not (r.get("features") or {}).get(INTRODUCES)]
        if not rest:
            raise ValueError(f"{row['form']!r} under «{clause}» is the form's only "
                             f"{row['word_class']} row — every other clause would lose it")
    # **AND ONE ROW PER JOB PER FORM**, the collection's own unique index — asked here so a clash is
    # this check's failure and not a write error at apply time.
    jobs = [(r["form"], r["word_class"], r["role"]) for r in CLOSED_CLASS_ROWS]
    if len(jobs) != len(set(jobs)):
        raise ValueError("two rows share (form, class, role) — the index refuses it")

    # **ONE VOICE PER MEANING**, on the key the decompiler asks with (`db/0028`'s arithmetic)…
    spoken = [r for r in CLOSED_CLASS_ROWS if r.get("spoken")]
    if len({_meaning(r) for r in spoken}) != len(spoken):
        raise ValueError("two flagged rows share a key — one of them would never be spoken")

    # **…AND THE LOOKUP THE DECOMPILER MAKES FOR A PURPOSE, ASKED HERE THE SAME WAY.** It asks the
    # joining roles for this meaning: exactly one flagged form across them is the voice; two would
    # be curation contradicting itself, none would leave a purpose unsayable. And the voice is said
    # with a BARE clause only because the same form is the infinitive marker — shown to hold.
    voiced = [r["form"] for r in CLOSED_CLASS_ROWS
              if r.get("role") in JOINING_ROLES and r.get("spoken")
              and _meaning(r) == _meaning({"role": r["role"], "compiled": PURPOSE})]
    if voiced != ["to"]:
        raise ValueError(f"the purpose is voiced by {voiced}, not by «to» alone")
    if not any(r["form"] == "to" and r["role"] == "infinitive_marker" for r in CLOSED_CLASS_ROWS):
        raise ValueError("the voice of purpose is not the infinitive marker's form")


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(ClosedClassDoc, CLOSED_CLASS_ROWS)
