"""0026 — closed classes v13: **«one» is impersonal, and that is why «it» was unsayable**.

**FOUND BY THE FIXPOINT, on «It will rain tomorrow».** Schema v4 gave an unresolved pronoun its
person, number and gender, so the decompiler can now ask the rows for *the third-person neuter
singular nominative* — and **two rows answer**: `it` and `one`. Two answers is no answer, the
decompiler said nothing rather than choose, and a sentence that had been round-tripping stopped.

**They are not the same word.** `one` is the IMPERSONAL pronoun — «one must be careful», «one never
knows» — a way of saying *anybody, including me*, and never a way of pointing at a specific neuter
thing. Its person, number and gender features are the grammar it AGREES by, not what it refers to,
and nothing in the table said so.

**One feature on one row.** `generic: true`, which the decompiler reads to leave it out of an
anaphor's candidates. It stays exactly as readable as it was: the station has always compiled «one»
by its row, and that row is untouched apart from this column.

*The remaining ambiguities in the paradigm are real ones and stay: a third-person singular whose
GENDER the sentence never gave is genuinely «he» or «she» or «it», and abstaining there is the
decompiler doing its job.*

**Written by the QM on 2026-09-20, fixing a regression the QM introduced the same hour.**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, ClosedClassDoc
from tk2.migrations import ensure_collections

VERSION = 13

#: `(role, form, position) -> the features to merge in`, as `db/0023`'s.
FEATURES = {
    ("referential", "one", 12): {"generic": True},
}


def build_rows(previous: list[dict]) -> list[dict]:
    out = []
    for row in previous:
        if row.get("version") != 12:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = VERSION
        extra = FEATURES.get((row["role"], row["form"], row.get("position")))
        if extra:
            new["features"] = {**(row.get("features") or {}), **extra}
        out.append(new)
    return out


def _previous_rows():
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 23), None)
    if found is None:
        raise RuntimeError("0023 is gone — it holds the version this one extends")
    return found.load().CLOSED_CLASS_ROWS


CLOSED_CLASS_ROWS = build_rows(_previous_rows())

#: Unchanged, and checked — this migration edits one column of one row.
CLOSED_CLASS_FORMS = tuple(
    sorted({row["form"] for row in CLOSED_CLASS_ROWS if " " not in row["form"]})
)


def _check() -> None:
    before = _previous_rows()
    if {r["form"] for r in before if " " not in r["form"]} != set(CLOSED_CLASS_FORMS):
        raise ValueError("THE EXCLUSION SET MOVED — D's vocabulary filter would change with it")
    if len(before) != len(CLOSED_CLASS_ROWS):
        raise ValueError("a row was added or lost — this migration edits one column")

    placed = {(row["role"], row["form"], row.get("position")) for row in CLOSED_CLASS_ROWS}
    missing = [key for key in FEATURES if key not in placed]
    if missing:
        raise ValueError(f"{missing} name no row")

    moved = [row["form"] for row, was in zip(CLOSED_CLASS_ROWS, before)
             if row.get("compiled") != was.get("compiled") or row.get("spoken") != was.get("spoken")]
    if moved:
        raise ValueError(f"{moved} changed meaning — this migration is about ONE feature")

    # **AND THE THING IT EXISTS FOR**: after it, exactly one row is the third-person neuter singular.
    neuter = [row for row in CLOSED_CLASS_ROWS
              if row.get("role") == "referential"
              and (row.get("features") or {}).get("person") == 3
              and (row.get("features") or {}).get("gender") == "n"
              and not (row.get("features") or {}).get("generic")]
    if len(neuter) != 1:
        raise ValueError(f"{[r['form'] for r in neuter]} all claim to be «it» — the decompiler "
                         f"would have to choose, and it must not")


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(ClosedClassDoc, CLOSED_CLASS_ROWS)
