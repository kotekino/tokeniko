"""0035 — adverb kinds v3: **«not necessarily» is not «must not»** (parser-compiler req 9, the
fixpoint's G10).

**«So a calculator does not necessarily think» was the fixpoint's one SILENT sentence.** Its zip is

    p0  negation   -> r0
    p1  necessity  -> r0
    r0  think.v (experiencer = a calculator)

a negation OUTSIDE a necessity — ¬□, the claim that thinking is not REQUIRED of a calculator. The
compiler reached it through `db/0013`'s `necessarily`; the decompiler could say a modality only with
a closed-class auxiliary, and **an auxiliary stands before «not»**: «must not» puts the negation
INSIDE, □¬, which is the opposite claim — that a calculator is required NOT to think. So it refused
the row, correctly, and the sentence came back as nothing.

**THE FORM EXISTS. IT WAS NEVER READ BACKWARDS.** Ten necessity adverbs carry the identical
`compiled`

    {'kind': 'prefix', 'element': 'modality', 'modality': 'necessity'}

so the inverse is ten forms for one meaning — a CHOICE, which is curation, which is this flag
(`db/0021`'s, `db/0031`'s shape). The position is not: an adverb stands AFTER «not», so «not
necessarily» is the order that says ¬□, and where the adverb sits is word order, which is frame.

**`necessarily`, AND ONLY `necessarily`.** It is the word the corpus attests for this very meaning
(`t-md-2`, traffic), and it is the one of the ten that reads as ¬□ whatever the context:

    not certainly · not surely     marginal English; the natural order is «certainly not», □¬
    not obviously · not clearly    EVIDENTIAL — «it is not obvious that…», a different claim
    not necessarily                the negation of necessity, and nothing else

«need not» and «does not have to» say the same thing and were not chosen: they are closed-class
forms, whose negation scopes over them LEXICALLY (need not ¬□, must not □¬, cannot ¬◇), and that is
a question about the closed classes this migration does not open.

*No possibility adverb is flagged, and ¬◇ stays refused.* «does not possibly think» is not how
English says it — «cannot» is, and that is a closed-class form with the same lexical question.

**KEYED ON THE MEANING, NOT ON THE POSITION.** The question the decompiler asks is «which adverb
voices this `compiled`», and it asks it only where the closed classes cannot answer — outside a
negation. A column saying which scope position a flag is for would record, as knowledge, a fact
the word order already holds.

**Written by the 1st Officier on 2026-09-24, on the QM's work order for G10.**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, AdverbKindDoc
from tk2.migrations import ensure_collections

VERSION = 3

#: `(kind, form)` — the one adverb that speaks a meaning the closed classes cannot say in its place.
SPOKEN = (
    ("epistemic", "necessarily"),
)


def build_rows(previous: list[dict]) -> list[dict]:
    out = []
    for row in previous:
        if row.get("version") != 2:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = VERSION
        new["spoken"] = (new["kind"], new["form"]) in SPOKEN
        out.append(new)
    return out


def _previous(number: int, attribute: str):
    # **BY NUMBER**, never through `newest_migration_declaring` — that walks and loads every file in
    # `db/`, this one included, and `db/0013`'s first draft recursed until the stack died.
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == number), None)
    if found is None:
        raise RuntimeError(f"{number:04d} is gone — it holds the version this one reads")
    return getattr(found.load(), attribute)


ADVERB_KIND_ROWS = build_rows(_previous(15, "ADVERB_KIND_ROWS"))


def _meaning(row: dict) -> tuple:
    """A row's VOICE. **THIS IS `Decompiler._key(None, compiled)` AND IT MUST STAY THAT WAY** —
    `db/0029`'s lesson: a check keyed on anything but the lookup's own key is checking a table that
    does not exist. The adverb rows have no closed-class `role`, sort or number, so the meaning is
    the `compiled` map alone — the vocabulary the two rosters share."""
    compiled = row.get("compiled") or {}
    return (None, tuple(sorted((k, str(v)) for k, v in compiled.items())), None, None)


def _check() -> None:
    before = [r for r in _previous(15, "ADVERB_KIND_ROWS") if r.get("version") == 2]
    if len(before) != len(ADVERB_KIND_ROWS):
        raise ValueError("a row was added or lost — this migration sets a flag")
    if any((row["form"], row["kind"], row.get("compiled")) != (was["form"], was["kind"],
                                                               was.get("compiled"))
           for row, was in zip(ADVERB_KIND_ROWS, before)):
        raise ValueError("a form, a kind or a meaning moved — this migration only sets `spoken`")

    # **THE TABLE'S LAWS, RE-RUN IN FULL** (`db/0015`: a check travels with the data it guards).
    # The closed classes read by number too — v18, the newest that declares them.
    closed = {row["form"] for row in _previous(33, "CLOSED_CLASS_ROWS")}
    clash = sorted({row["form"] for row in ADVERB_KIND_ROWS} & closed)
    if clash:
        raise ValueError(f"{clash} are in BOTH rosters and a reader could not tell which answers")
    seen = set()
    for row in ADVERB_KIND_ROWS:
        key = (row["form"], row["kind"])
        if key in seen:
            raise ValueError(f"{row['form']!r} appears twice as {row['kind']} — the unique index is "
                             f"(version, form, kind) and the write would be refused")
        seen.add(key)
    if any(row["kind"] == "manner" for row in ADVERB_KIND_ROWS):
        raise ValueError("`manner` is the DEFAULT and may not be a row")

    spoken = [r for r in ADVERB_KIND_ROWS if r["spoken"]]
    if len(spoken) != len(SPOKEN):
        raise ValueError(f"{len(SPOKEN)} chosen and {len(spoken)} carry the flag")

    # **THE THING THIS MIGRATION EXISTS FOR**: the voice is a NECESSITY, and it is the one the
    # decompiler asks for outside a negation.
    necessity = {"kind": "prefix", "element": "modality", "modality": "necessity"}
    if [r["form"] for r in spoken if r.get("compiled") == necessity] != ["necessarily"]:
        raise ValueError("«necessarily» must be the one adverb speaking a necessity")

    # **ONE VOICE PER MEANING**, on the key the decompiler actually asks with — and the arithmetic
    # (`db/0028`): a flag sharing a key with another is absorbed in silence.
    if len({_meaning(row) for row in spoken}) != len(spoken):
        raise ValueError("two flagged adverbs share a meaning — the decompiler would have to "
                         "choose, and one of them would never be spoken")


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(AdverbKindDoc, ADVERB_KIND_ROWS)
