"""0021 — closed classes v11: **a meaning has a form it is SPOKEN with** (parser-compiler req 9).

**THE DECOMPILER ASKED THE ROWS A QUESTION THEY COULD NOT ANSWER.** Compiling reads form → meaning
and is many-to-one on purpose: thirty-two prepositions mean `location`, eighteen subordinators mean
an asserted `imply`, three forms mean sentential negation. Decompiling reads meaning → form, and
there the many-to-one becomes a CHOICE — «not» or «n't» or «no» — which the table does not make.

**A decompiler that chose for itself would be the standing law's own failure relocated**: our own set,
hard-coded, wearing a `next(iter(...))` instead of a list literal. So the choice becomes a flag, one
row per meaning, and it is CURATION.

**WHERE IT IS NOT NEEDED, IT IS NOT SET.** A meaning with a single form is already unambiguous — «or»
means the disjunction and nothing else does — and a PARSED zip records the preposition it actually
met (`Box.marker`, req 65), so a marked phrase never asks this table anything. Ten meanings need it
today; the rest enter on a witness, as every roster here does.

**THE TEN, AND WHY EACH:**

    negation          not        «n't» is a clitic and «no» is a determiner — «not» is the
                                 sentential negator, and a clause that cannot say it is REFUSED
                                 rather than spoken as its own opposite
    universal         every      it takes a singular noun, which is what the decompiler renders
    existential       some       the neutral positive-polarity existential; «any» is polarity-bound
    negative          no         the determiner reading: «no cats»
    and / coordinator and        «but», «yet», «for» and «plus» all add something and is the one
                                 that adds nothing
    and / subordinate although   the concessive, where the coordinator's «and» cannot go
    imply asserts both because    the asserted implication, and `db/0010`'s own example
    imply asserts neither if      the supposed one, and `db/0016`'s
    imply ambiguous   when       the station abstains on it anyway (req 13), so this speaks the
                                 abstention rather than inventing a stronger word
    indefinite        a          one word in two spellings; «an» is orthography and stays in code

*«the» needs no flag (English has one definite article) and neither do «or», «nor», «xor» or the
markers — the table already names exactly one form for each of those meanings.*

**Nothing else moves**: no form arrives or leaves, so D's gloss-word exclusion set is untouched, and
`compiled` is not edited — the flag is a new column and the meanings are exactly the meanings v10
had.

**Written by the QM on 2026-09-19, on the Captain's «add the preferred form flag». The ten choices
are the QM's and are listed here so they can be argued with.**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, ClosedClassDoc
from tk2.migrations import ensure_collections

VERSION = 11

#: `(role, form)` — the form that SPEAKS each meaning that has more than one. Keyed by form rather
#: than by the compiled dict so the choice is readable: a reader must be able to see «not, and not
#: n't» without decoding a selector.
SPOKEN = (
    ("negation", "not"),
    ("quantificational", "every"),
    ("quantificational", "some"),
    ("quantificational", "no"),
    ("coordinator", "and"),
    ("subordinator", "although"),
    ("subordinator", "because"),
    ("subordinator", "if"),
    ("subordinator", "when"),
    ("determination", "a"),
)


def build_rows(previous: list[dict]) -> list[dict]:
    out = []
    for row in previous:
        if row.get("version") != 10:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = VERSION
        new["spoken"] = (row["role"], row["form"]) in SPOKEN
        out.append(new)
    return out


def _previous_rows():
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 17), None)
    if found is None:
        raise RuntimeError("0017 is gone — it holds the version this one extends")
    return found.load().CLOSED_CLASS_ROWS


CLOSED_CLASS_ROWS = build_rows(_previous_rows())

#: Unchanged, and checked — this migration adds a column and no form.
CLOSED_CLASS_FORMS = tuple(
    sorted({row["form"] for row in CLOSED_CLASS_ROWS if " " not in row["form"]})
)


def _check() -> None:
    import json

    before = _previous_rows()
    if {r["form"] for r in before if " " not in r["form"]} != set(CLOSED_CLASS_FORMS):
        raise ValueError("THE EXCLUSION SET MOVED — D's vocabulary filter would change with it")
    if len(before) != len(CLOSED_CLASS_ROWS):
        raise ValueError("a row was added or lost — this migration only adds a column")

    spoken = [r for r in CLOSED_CLASS_ROWS if r["spoken"]]
    if len(spoken) != len(SPOKEN):
        raise ValueError(f"{len(SPOKEN)} meanings were chosen and {len(spoken)} rows carry the flag "
                         f"— a (role, form) pair in SPOKEN names no row")

    # **THE INVARIANT THE FLAG EXISTS FOR**: one voice per meaning. Two would put the decompiler
    # back where it started, choosing — and it would do it silently, which is worse.
    seen: dict[tuple, str] = {}
    for row in spoken:
        meaning = (row["role"], json.dumps(row.get("compiled") or {}, sort_keys=True))
        if meaning in seen:
            raise ValueError(f"{row['form']!r} and {seen[meaning]!r} both claim to speak the same "
                             f"meaning ({row['role']})")
        seen[meaning] = row["form"]

    # And a flag on a meaning only ONE form carries would be noise: the table already answers there.
    by_meaning: dict[tuple, int] = {}
    for row in CLOSED_CLASS_ROWS:
        if not (row.get("compiled") or {}):
            continue
        key = (row["role"], json.dumps(row["compiled"], sort_keys=True))
        by_meaning[key] = by_meaning.get(key, 0) + 1
    for meaning, form in seen.items():
        if by_meaning.get(meaning, 0) < 2:
            raise ValueError(f"{form!r} is the only form with its meaning — it needs no flag")


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(ClosedClassDoc, CLOSED_CLASS_ROWS)
