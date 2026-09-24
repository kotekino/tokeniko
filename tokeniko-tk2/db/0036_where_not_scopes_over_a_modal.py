"""0036 — closed classes v19: **where «not» scopes over a modal is a fact about each modal**
(parser-compiler req 9, the fixpoint's G10 findings).

**THE STATION ASSUMED «NOT» ALWAYS SITS INSIDE THE MODAL**, because the auxiliary stands before it
and the prefix order is the scope order. For «must» that is right and for half the table it is the
opposite claim, with no warning:

    A calculator must not think       □¬   compiled □¬   right
    A calculator need not think       ¬□   compiled □¬   WRONG — a prohibition for an exemption
    A calculator can not think        ¬◇   compiled ◇¬   WRONG — «perhaps it doesn't» for «it is unable»
    A calculator could not think      ¬◇   compiled ◇¬   WRONG, the same way
    A calculator may not think        ?    compiled ◇¬   a coin toss: permission ¬◇ or epistemic ◇¬
    A calculator cannot think         ¬◇   a bare `think`, «cannot» unplaced — the claim that it DOES

**English does not decide this by position** — every one of these auxiliaries stands before its «not».
It decides it by the WORD: «must not» forbids, «need not» exempts. A fact about each word is
knowledge (the Captain, 2026-09-24), so it is a row, and the compiler reads it.

**WHERE IT LIVES: `features.following_negation`, AND NOT IN `compiled`.** `compiled` is the row's
MEANING and it is the decompiler's key (`db/0028`, `db/0029`): «must» and «need» both compile to □,
and unnegated they ARE one meaning with one voice. Writing the scope into `compiled` would split □
into two meanings the language does not have — «must think» and «need think» would stop being the same
claim, and a second `spoken` flag would become legal for a meaning that already has its voice. What
differs between them is how the FORM combines with a «not» after it, which is exactly what
`features` holds (`db/0023`: «the features a form is CHOSEN by») — per class, a map, no schema
change. The adverb rows carry nothing: for an adverb the scope is WORD ORDER, «necessarily does not»
against «does not necessarily», and word order is frame (the Captain, 2026-09-18).

    inside      «X not» is □¬ / ◇¬ — the negation under the modal
    outside     «X not» is ¬□ / ¬◇ — the modal under the negation
    ambiguous   both are English, and nothing in the clause says which: the compiler ABSTAINS

**«CANNOT» IS A ROW, AND THE CAUSE WAS THE TABLE.** stanza keeps «cannot» one token — form `cannot`,
lemma `cannot`, `AUX` — and the table had no such form, so the walk met nothing. A reader that split
it would be code deciding spelling, and the spelling IS the fact: «cannot» is «can» and «not» in one
word. Its `compiled` carries the negation it holds, `negation: outside` — that one IS meaning (¬◇,
not ◇), so it belongs in the key and gives ¬◇ a meaning of its own. And it is flagged `spoken`: the
voice of ¬◇, the written standard where «can not» is the variant.

**THE EXCLUSION SET MOVES BY ONE FORM, AND THE MOVE IS INERT.** `cannot` is single-word, so it joins
`CLOSED_CLASS_FORMS`, which filters D's vocabulary (`db/0013`). Measured before writing it: WordNet
has NO lemma `cannot` (`wn.synsets('cannot') == []`), so neither vocabulary reading of D can hold it —
`lexicon` is WordNet's lemmas and `base` is keys of them. The filter removes a word D never had. The
check below refuses any other movement.

*`'d` carries the field on its ROW although its `compiled` is `ambiguous` between a possibility and
a perfect: in both readings a following «not» is on the verb — «I'd not go» (would not) · «I'd not
gone» (had not) — so the answer is one, whichever reading wins.*

**Written by the 1st Officier on 2026-09-24, on the QM's work order. The values are curation, listed
here so they can be argued with; nothing is applied until the Captain says so.**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, ClosedClassDoc
from tk2.migrations import ensure_collections

VERSION = 19

#: The feature, and its three values. A NAME and its vocabulary, not a roster: which modal takes
#: which value is the rows' business below. `tk2.language.closed` spells the same four strings.
FOLLOWING_NEGATION = "following_negation"
INSIDE, OUTSIDE, AMBIGUOUS = "inside", "outside", "ambiguous"
VALUES = (INSIDE, OUTSIDE, AMBIGUOUS)

#: form -> (where a following «not» scopes, why). Every `modality` row of v18, and `cannot`.
#: **The reason is written onto the row's `note`** — the ledger keeps the justification verbatim.
SCOPE = {
    "can": (OUTSIDE, "«cannot» / «can not think» is ¬◇ — it is not able, or not allowed. The ◇¬ "
                     "reading («you can NOT go, if you like») lives only in contrastive stress, "
                     "which text does not carry"),
    "could": (OUTSIDE, "the past and the conditional of «can», and it negates the same way: «he "
                       "could not swim» (unable) · «it could not be true» (impossible) — ¬◇. The ◇¬ "
                       "suggestion «you could NOT go» is stress again"),
    "may": (AMBIGUOUS, "permission «you may not smoke» is ¬◇, epistemic «it may not rain» is ◇¬, "
                       "and both are everyday English with the same words in the same order"),
    "might": (INSIDE, "«it might not rain» — ◇¬, possibly not. «might» as permission is archaic and "
                      "its negation («might not» = not allowed) is not current"),
    "must": (INSIDE, "«you must not smoke» — □¬, a prohibition; epistemic «it must not be him» is "
                     "□¬ as well"),
    "should": (INSIDE, "«you should not smoke» — □¬, the obligation is NOT to; not «it is not "
                       "required that you smoke»"),
    "ought": (INSIDE, "«you ought not to smoke» — □¬, as «should»"),
    "need": (OUTSIDE, "«you need not go» — ¬□, no necessity: going is allowed. The polarity-bound "
                      "semi-modal exists almost only for this"),
    "dare": (OUTSIDE, "«he dare not go» — he does NOT dare to go: the daring is what is denied, so "
                      "the negation is over the modal"),
    "'d": (INSIDE, "«I'd not go» (would not) and «I'd not gone» (had not) both put «not» on the "
                   "verb under the auxiliary — one answer for both readings of the clitic"),
    "cannot": (INSIDE, "a SECOND «not» after the fused one is under it: «I cannot not think» is "
                       "¬◇¬, it is impossible that I do not think"),
}

#: **THE ONE ROW THIS MIGRATION ADDS** — «can» and «not» spelled as one word, compiled as one word:
#: a possibility carrying its own negation OUTSIDE it.
CANNOT = {
    "version": VERSION,
    "form": "cannot",
    "role": "modality",
    "word_class": "modal",
    "compiled": {"kind": "prefix", "element": "modality", "modality": "possibility",
                 "negation": OUTSIDE},
    "features": {"modality": "possibility", FOLLOWING_NEGATION: INSIDE},
    "source": "the fixpoint's G10 findings (2026-09-24): «A calculator cannot think» compiled to a "
              "bare `think` because stanza keeps «cannot» one token and the table had no such form",
    "note": "«can» + «not» fused, and the fusion is written in the spelling: ¬◇. `spoken` — the voice "
            "of ¬◇, the written standard where «can not» is the variant — v19: a following «not» "
            "scopes INSIDE: " + SCOPE["cannot"][1],
    "position": 136,
    "spoken": True,
}


def build_rows(previous: list[dict]) -> list[dict]:
    out = []
    for row in previous:
        if row.get("version") != 18:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = VERSION
        if row.get("role") == "modality":
            value, why = SCOPE[row["form"]]
            new["features"] = {**(row.get("features") or {}), FOLLOWING_NEGATION: value}
            note = row.get("note") or ""
            new["note"] = (f"{note} — " if note else "") + \
                f"v19: a following «not» scopes {value.upper()}: {why}"
        out.append(new)
    out.append(dict(CANNOT))
    return out


def _previous_rows():
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 33), None)
    if found is None:
        raise RuntimeError("0033 is gone — it holds the version this one extends")
    return found.load().CLOSED_CLASS_ROWS


CLOSED_CLASS_ROWS = build_rows(_previous_rows())

#: **MOVED BY EXACTLY `cannot`**, which WordNet has no lemma for — see the docstring.
CLOSED_CLASS_FORMS = tuple(
    sorted({row["form"] for row in CLOSED_CLASS_ROWS if " " not in row["form"]})
)


def _meaning(row: dict) -> tuple:
    """A row's VOICE. **THIS IS `Decompiler._key()` AND IT MUST STAY THAT WAY** — see `db/0029`."""
    features = row.get("features") or {}
    return (row["role"], tuple(sorted((k, str(v)) for k, v in (row.get("compiled") or {}).items())),
            features.get("sort"), features.get("takes_number"))


def _is_modality(compiled: dict) -> bool:
    return compiled.get("kind") == "prefix" and compiled.get("element") == "modality"


def _check() -> None:
    before = _previous_rows()
    moved = {r["form"] for r in CLOSED_CLASS_ROWS if " " not in r["form"]} \
        ^ {r["form"] for r in before if " " not in r["form"]}
    if moved != {"cannot"}:
        raise ValueError(f"THE EXCLUSION SET MOVED BY {sorted(moved)} — only «cannot» may, and only "
                         f"because D cannot hold it")
    if set(CLOSED_CLASS_FORMS) != {r["form"] for r in before if " " not in r["form"]} | {"cannot"}:
        raise ValueError("CLOSED_CLASS_FORMS is not v18's set plus «cannot»")
    if len(CLOSED_CLASS_ROWS) != len(before) + 1 or CLOSED_CLASS_ROWS[-1]["form"] != "cannot":
        raise ValueError("this migration adds exactly one row, «cannot»")
    for row, was in zip(CLOSED_CLASS_ROWS, before):
        if row.get("compiled") != was.get("compiled") or row.get("role") != was.get("role") \
                or row.get("spoken") != was.get("spoken") or row["form"] != was["form"]:
            raise ValueError(f"{was['form']!r}: a meaning, a role or a voice moved — this migration "
                             f"writes one feature and adds one row")
        features = dict(row.get("features") or {})
        if row.get("role") == "modality":
            features.pop(FOLLOWING_NEGATION, None)
        if features != (was.get("features") or {}):
            raise ValueError(f"{was['form']!r}: a feature other than `{FOLLOWING_NEGATION}` moved")
    if CANNOT["position"] in {r.get("position") for r in before}:
        raise ValueError("«cannot»'s position collides with an existing row")

    # **EVERY MODALITY ROW CARRIES THE FIELD, AND ONLY FROM THE ALLOWED SET.** A row without it is a
    # failure HERE, never a default in the compiler — a scope nobody wrote down is not a scope.
    modal_rows = [r for r in CLOSED_CLASS_ROWS if r.get("role") == "modality"]
    if {r["form"] for r in modal_rows} != set(SCOPE):
        raise ValueError(f"the modality rows {sorted(r['form'] for r in modal_rows)} and the "
                         f"curated forms {sorted(SCOPE)} are not the same set")
    for row in modal_rows:
        value = (row.get("features") or {}).get(FOLLOWING_NEGATION)
        if value not in VALUES:
            raise ValueError(f"{row['form']!r}: `{FOLLOWING_NEGATION}` is {value!r}, not one of {VALUES}")
    # A row compiling to a modality under ANOTHER role would escape the loop above — and the compiler
    # would meet a modal with no answer. None exists; this says so rather than assuming it.
    stray = [r["form"] for r in CLOSED_CLASS_ROWS
             if r.get("role") != "modality" and _is_modality(r.get("compiled") or {})]
    if stray:
        raise ValueError(f"{stray} compile to a modality outside the `modality` role")
    for row in modal_rows:
        own = (row.get("compiled") or {}).get("negation")
        if own is not None and own not in VALUES:
            raise ValueError(f"{row['form']!r}: its own negation is {own!r}, not one of {VALUES}")

    # **ONE VOICE PER MEANING**, on the key the decompiler asks with (`db/0028`'s arithmetic): a
    # flag sharing a key with another is absorbed in silence.
    spoken = [r for r in CLOSED_CLASS_ROWS if r.get("spoken")]
    if len({_meaning(r) for r in spoken}) != len(spoken):
        raise ValueError("two flagged rows share a key — one of them would never be spoken")
    if [r["form"] for r in spoken if (r.get("compiled") or {}).get("negation")] != ["cannot"]:
        raise ValueError("«cannot» must be the one voice of a modality carrying its own negation")

    # **THE LOOKUP THE DECOMPILER MAKES FOR «X not», ASKED HERE THE SAME WAY.** A negation inside a
    # modality is said with an auxiliary whose following «not» scopes INSIDE — the flagged one if it
    # qualifies, else the only one, else nothing. «can» is the voice of ◇ and scopes OUTSIDE, so ◇¬
    # must find another word, and this is where it is shown to exist.
    for meaning in {_meaning(r) for r in modal_rows if _is_modality(r.get("compiled") or {})
                    and not (r.get("compiled") or {}).get("negation")}:
        fits = [r for r in modal_rows if _meaning(r) == meaning
                and (r.get("features") or {}).get(FOLLOWING_NEGATION) == INSIDE]
        voiced = [r["form"] for r in fits if r.get("spoken")] or \
            ([fits[0]["form"]] if len(fits) == 1 else [])
        if not voiced:
            raise ValueError(f"{meaning}: no auxiliary says this modality with a negation inside it")


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(ClosedClassDoc, CLOSED_CLASS_ROWS)
