"""0016 — closed classes v9: **`if` asks too, as `whether` does.**

**FOUND ON E3 TASK 2c's BENCH** (2026-09-18, parser-compiler req 21). The polar question was being
fixed in its root spelling — «Is the cat hungry?» — and the plan took its subordinate spelling as
already working: *«`whether` opens the truth from its marker row»* (req 14, `db/0011`). **It never
had.** `whether` holds two rows, the interrogative (`opens: truth`) and the subordinator (a
conditional JOIN, `asserts: neither`), and a `mark` was always narrowed to the subordinator — so

    «I wonder whether the cat is hungry»   compiled as a CONDITIONAL between the wondering and the cat

**THE TREE SEPARATES THE TWO READINGS, AND NOTHING ELSE DOES.** The word is `mark` in both; what
differs is the clause it marks. A COMPLEMENT (`ccomp`, `csubj`) is asked — «I wonder WHETHER it
rains», «I asked IF it rains» — and an ADVERBIAL (`advcl`) is supposed — «IF it rains, I stay»,
«WHETHER it rains or not, I go». That choice is the station's (frame: reading the tree's shape,
`tk2/language/closed.py`). **What each word CAN do is knowledge, and it lives here.**

**`if` HAD ONLY ONE ROW**, so there was nothing for the tree to choose. It gains the reading `whether`
already has: an interrogative that opens the truth of its clause. English uses the two
interchangeably in exactly this position — «I don't know if he's coming» — and a table that let one
ask and not the other would be a hand list with a hole in it.

**Nothing else moves.** `if` is already a form, so the FORMS are identical and D's gloss-word
exclusion — and the sealed base with it — does not move.

**Written by the QM on 2026-09-18, on the Captain's «whether/if first».**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, ClosedClassDoc
from tk2.migrations import ensure_collections

VERSION = 9

#: The subordinators that ALSO ask — the embedded polar question. `whether` already carries its
#: interrogative row (`db/0011`); `if` gains the same one, so the tree has a reading to choose.
ASKS_TOO = ("if",)


def build_rows(previous: list[dict]) -> list[dict]:
    out = []
    for row in previous:
        if row.get("version") != 8:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = VERSION
        out.append(new)

    # Declared order is within (version, word_class): the new reading goes after its class's last.
    position = 1 + max(r["position"] for r in out if r["word_class"] == "conjunction")
    for form in ASKS_TOO:
        out.append({
            "version": VERSION,
            "form": form,
            "word_class": "conjunction",
            "role": "interrogative",
            "compiled": {"kind": "open", "binds": None, "opens": "truth"},
            "features": {"gap": "polarity"},
            "source": "E3 task 2c's bench, 2026-09-18 — «I asked if the cat is hungry» compiled "
                      "as a conditional (parser-compiler req 21)",
            "position": position,
            "note": "the embedded yes/no question — «I asked IF it rains», as `whether` — v9: "
                    "opens=truth. The clause's dependency chooses: a complement asks, an `advcl` "
                    "supposes (req 21).",
        })
    return out


def _previous_rows():
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 15), None)
    if found is None:
        raise RuntimeError("0015 is gone — it holds the version this one extends")
    return found.load().CLOSED_CLASS_ROWS


CLOSED_CLASS_ROWS = build_rows(_previous_rows())

#: Unchanged, and checked — this migration adds a READING, never a form.
CLOSED_CLASS_FORMS = tuple(
    sorted({row["form"] for row in CLOSED_CLASS_ROWS if " " not in row["form"]})
)


def _check() -> None:
    before = {row["form"] for row in _previous_rows() if " " not in row["form"]}
    if set(CLOSED_CLASS_FORMS) != before:
        raise ValueError("THE EXCLUSION SET MOVED — D's vocabulary filter would change with it")

    # **EVERY WORD THAT ASKS ALSO SUPPOSES, AND BOTH READINGS MUST BE ROWS.** The tree picks between
    # them; a form holding only one leaves the tree nothing to pick, which is exactly how `if` was
    # a conditional in «I asked if it rains».
    for form in ("whether", *ASKS_TOO):
        jobs = [r for r in CLOSED_CLASS_ROWS if r["form"] == form]
        asks = [r for r in jobs if (r.get("compiled") or {}).get("opens") == "truth"]
        supposes = [r for r in jobs if (r.get("compiled") or {}).get("kind") == "join"]
        if len(asks) != 1 or len(supposes) != 1:
            raise ValueError(f"{form!r} must hold exactly one asking and one supposing reading")

    # The collection's unique index, checked before the write rather than discovered by it: one
    # row per (form, word_class, role) — a JOB — per version.
    seen = set()
    for row in CLOSED_CLASS_ROWS:
        key = (row["form"], row["word_class"], row["role"])
        if key in seen:
            raise ValueError(f"{row['form']!r} holds the job {key[1:]} twice")
        seen.add(key)


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(ClosedClassDoc, CLOSED_CLASS_ROWS)
