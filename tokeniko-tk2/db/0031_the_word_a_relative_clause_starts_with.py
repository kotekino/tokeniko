"""0031 — closed classes v17: **the word a relative clause starts with** (parser-compiler req 36).

**«Every cat that sleeps is happy» was decompiling to «Every cat is happy.»** — which is not a
shorter way of saying it, it is a STRONGER claim than the zip holds. The restriction says WHICH cats
are meant; dropping it asserts the predicate of all of them. Saying more than the zip does is the
sin req 8 names, and losing a restriction is how it happens without a word looking wrong.

The station has always compiled these clauses. It could not say them back because **no relative
pronoun is spoken**: all nine `relative` rows carry the identical `compiled`

    {'kind': 'open', 'binds': 'antecedent'}

so the decompiler's inverse index finds nine forms for one meaning, which is a CHOICE, which is
curation and does not live in code. It abstained, correctly, and the clause went unsaid.

**`that`, AND ONLY `that`.** The nine differ by `features.sort` — the axis `db/0028` put in the key
— and the sort is what English picks by:

    who · whom   person        which   thing        where   place
    whose        possessor     that    —            when    time        why   cause

**Choosing `who` over `which` needs the ANTECEDENT's animacy, and the zip does not record it.** That
is not an oversight here: it is the same hole as the pinned gate failure `q-6`, it is named in req 9
as E3b's, and inventing it from a dictionary key would be the station guessing at content. `that`
is the relative English uses when it does not commit — «the cat that sleeps», «the man that ate the
fish», both restrictive and both grammatical — and it is the one row whose sort is empty, so it
answers the question the decompiler can actually ask.

*`as` is the other sortless row («such a cat AS sleeps») and is the competitor this flag settles. The
sorted rows stay unflagged on purpose: the day the zip carries animacy, `who` and `which` are one
migration away and the key already has the axis to hold them apart.*

**AND THE ROUND TRIP CLOSES ANYWAY**, which is the test that matters: `who` and `that` compile to
the same thing, so «I know the man who ate the fish» coming back as «the man that ate the fish» is
a different WORD and the same zip. A decompiler is faithful to the zip, not to the original
sentence (req 9).

**Written by the QM on 2026-09-21, building the decompiler half of the relative clause.**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, ClosedClassDoc
from tk2.migrations import ensure_collections

VERSION = 17

#: `(role, form)` — v16's eighteen, plus the relative pronoun.
SPOKEN = (
    ("negation", "not"),
    ("quantificational", "every"),
    ("quantificational", "all"),
    ("quantificational", "some"),
    ("quantificational", "no"),
    ("fused_quantifier", "everyone"),
    ("fused_quantifier", "someone"),
    ("fused_quantifier", "nobody"),
    ("fused_quantifier", "something"),
    ("fused_quantifier", "somewhere"),
    ("relative", "that"),
    ("coordinator", "and"),
    ("subordinator", "because"),
    ("subordinator", "if"),
    ("subordinator", "when"),
    ("determination", "a"),
    ("modality", "can"),
    ("modality", "must"),
    ("tense_aspect", "will"),
)


def build_rows(previous: list[dict]) -> list[dict]:
    out = []
    for row in previous:
        if row.get("version") != 16:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = VERSION
        new["spoken"] = (new["role"], new["form"]) in SPOKEN
        out.append(new)
    return out


def _previous_rows():
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 30), None)
    if found is None:
        raise RuntimeError("0030 is gone — it holds the version this one extends")
    return found.load().CLOSED_CLASS_ROWS


CLOSED_CLASS_ROWS = build_rows(_previous_rows())

#: Unchanged, and checked — this migration sets one flag.
CLOSED_CLASS_FORMS = tuple(
    sorted({row["form"] for row in CLOSED_CLASS_ROWS if " " not in row["form"]})
)


def _meaning(row: dict) -> tuple:
    """A row's VOICE. **THIS IS `Decompiler._key()` AND IT MUST STAY THAT WAY** — see `db/0029`."""
    import json

    features = row.get("features") or {}
    compiled = json.dumps(row.get("compiled") or {}, sort_keys=True)
    return (row["role"], compiled, features.get("sort"), features.get("takes_number"))


def _check() -> None:
    before = _previous_rows()
    if {r["form"] for r in before if " " not in r["form"]} != set(CLOSED_CLASS_FORMS):
        raise ValueError("THE EXCLUSION SET MOVED — D's vocabulary filter would change with it")
    if len(before) != len(CLOSED_CLASS_ROWS):
        raise ValueError("a row was added or lost — this migration sets a flag")
    if any(row.get("compiled") != was.get("compiled") or row.get("features") != was.get("features")
           or row.get("role") != was.get("role")
           for row, was in zip(CLOSED_CLASS_ROWS, before)):
        raise ValueError("a meaning, a feature or a role moved — this migration only sets `spoken`")

    spoken = [r for r in CLOSED_CLASS_ROWS if r["spoken"]]
    if len(spoken) != len(SPOKEN):
        raise ValueError(f"{len(SPOKEN)} chosen and {len(spoken)} carry the flag")

    # **THE THING THIS MIGRATION EXISTS FOR**: exactly one relative speaks, and it is the one whose
    # sort is empty — the only question the decompiler can ask without animacy it does not have.
    relatives = [r["form"] for r in spoken if r["role"] == "relative"]
    if relatives != ["that"]:
        raise ValueError(f"{relatives} speak the relative and it must be «that» alone")
    if (next(r for r in CLOSED_CLASS_ROWS
             if r["role"] == "relative" and r["form"] == "that")["features"] or {}).get("sort"):
        raise ValueError("«that» has a sort — then it is not the answer for an unknown antecedent")

    # **ONE VOICE PER MEANING**, on the key the decompiler actually asks with.
    for scope in ("role", "meaning"):
        seen: dict[tuple, str] = {}
        for row in spoken:
            key = _meaning(row) if scope == "role" else _meaning(row)[1:]
            if key in seen:
                raise ValueError(f"{row['form']!r} and {seen[key]!r} both claim to speak the same "
                                 f"{scope} — the decompiler would have to choose, and it must not")
            seen[key] = row["form"]

    # **AND THE ARITHMETIC** (`db/0028`'s lesson): a flag sharing a key with another is absorbed.
    if len({_meaning(row) for row in spoken}) != len(spoken):
        raise ValueError("two flagged rows share a key — one of them would never be spoken")


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(ClosedClassDoc, CLOSED_CLASS_ROWS)
