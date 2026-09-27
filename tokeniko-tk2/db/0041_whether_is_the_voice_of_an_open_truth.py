"""0041 — closed classes v22: **«whether» is the voice of an open truth** (parser-compiler,
`E3.3.11.2.13` — the Captain's ruling `E3.3.11.2.16` (5) of 2026-09-26).

**THE RULING, AS THE QM RELAYED IT** *(«accepted all your leans, proceed»)*:

    5. «whether» gets its voice — a `spoken` flag by migration, so an open complement is not said
       as a factive «that» (E3.3.11.2.13).

**WHAT THE STATION DID, MEASURED BEFORE THIS WAS WRITTEN** (`202609261600_the-attitude-takes-its-
matrix-place.md`): «I wonder whether he sleeps» compiles to ATT(me, wonder) over sleep(he) with its
truth OPEN — the holder's question, read off «whether»'s own row (`opens: truth`). Said back, the
complementizer was always «that», because the decompiler asked for the voice of an asserted
complement and for nothing else: «I wonder THAT he sleeps», and under «know» the reverse of what
was said — «I know whether he sleeps» came back «I know that he sleeps», a factive claim the
speaker never made.

**WHY A FLAG AND NOT A LOOKUP.** Two rows carry the meaning `{kind: open, binds: None, opens: truth}`
in the interrogative role — «whether» and «if» («I asked IF the cat is hungry») — so the inverse map
names two forms and the decompiler, rightly, chose neither. Which one English speaks by default is a
CHOICE, and a choice is curation (`db/0021`'s law): «whether» is the one that is never also a
conditional, so a sentence said with it cannot be read back as supposing.

**ONE ROW MOVES, AND ONLY ITS FLAG.** Every other row is v21's, with its version; no form is added or
lost, so the exclusion set — D's vocabulary filter — does not move.

**Written by the 1st Officier on 2026-09-26, on the Captain's ruling of the same day. Nothing is
applied until the Captain says so.**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, ClosedClassDoc
from tk2.migrations import ensure_collections

CLOSED_VERSION = 22

_RULING = ("the Captain, 2026-09-26 (E3.3.11.2.16 (5), «accepted all your leans, proceed»): "
           "«whether» gets its voice — a `spoken` flag by migration, so an open complement is not "
           "said as a factive «that» (E3.3.11.2.13)")

#: THE MEANING that gains a voice — an open truth, in the interrogative role. A name of the table's
#: own vocabulary, not a roster.
OPEN_TRUTH = {"kind": "open", "binds": None, "opens": "truth"}
ROLE = "interrogative"

#: (role, form) -> why it is the voice. The one the ruling names, and no second.
VOICED = {
    (ROLE, "whether"): "an open truth — «I wonder WHETHER he sleeps», «I know WHETHER he sleeps». "
                       "Of the two forms that carry it, the one that is never also a conditional",
}


def build_closed(previous: list[dict]) -> list[dict]:
    out = []
    for row in previous:
        if row.get("version") != CLOSED_VERSION - 1:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = CLOSED_VERSION
        if (row.get("role"), row["form"]) in VOICED and row.get("compiled") == OPEN_TRUTH:
            new["spoken"] = True
            note = row.get("note") or ""
            new["note"] = (f"{note} — " if note else "") + \
                f"v22: {VOICED[(row['role'], row['form'])]} ({_RULING})"
        out.append(new)
    return out


def _previous(number: int, attribute: str):
    # **BY NUMBER**, never through `newest_migration_declaring` — that walks and loads every file in
    # `db/`, this one included, and `db/0013`'s first draft recursed until the stack died.
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == number), None)
    if found is None:
        raise RuntimeError(f"{number:04d} is gone — it holds the version this one extends")
    return getattr(found.load(), attribute)


CLOSED_CLASS_ROWS = build_closed(_previous(39, "CLOSED_CLASS_ROWS"))

#: **UNCHANGED** — a flag moves, and no form.
CLOSED_CLASS_FORMS = tuple(
    sorted({row["form"] for row in CLOSED_CLASS_ROWS if " " not in row["form"]})
)


def _meaning(row: dict) -> tuple:
    """A row's VOICE. **THIS IS `Decompiler._key()` AND IT MUST STAY THAT WAY** — see `db/0029`."""
    features = row.get("features") or {}
    return (row["role"], tuple(sorted((k, str(v)) for k, v in (row.get("compiled") or {}).items())),
            features.get("sort"), features.get("takes_number"))


def _check() -> None:
    before = [r for r in _previous(39, "CLOSED_CLASS_ROWS") if r.get("version") == CLOSED_VERSION - 1]
    if set(CLOSED_CLASS_FORMS) != {r["form"] for r in before if " " not in r["form"]}:
        raise ValueError("THE EXCLUSION SET MOVED — D's vocabulary filter would change with it")
    if len(CLOSED_CLASS_ROWS) != len(before):
        raise ValueError("a closed-class row was added or lost — this migration moves one flag")

    # **ONE ROW MOVES, AND ONLY ITS FLAG** — form, role, class, meaning and features stay v21's.
    moved = []
    for row, was in zip(CLOSED_CLASS_ROWS, before):
        if (row["form"], row.get("role"), row.get("word_class"), row.get("compiled"),
                row.get("features"), row.get("source")) != (
                was["form"], was.get("role"), was.get("word_class"), was.get("compiled"),
                was.get("features"), was.get("source")):
            raise ValueError(f"{was['form']!r}: a form, a role, a meaning or a feature moved")
        if bool(row.get("spoken")) != bool(was.get("spoken")):
            moved.append((row.get("role"), row["form"]))
        elif row.get("note") != was.get("note"):
            raise ValueError(f"{was['form']!r}: a note moved on a row whose voice did not")
    if sorted(moved) != sorted(VOICED):
        raise ValueError(f"the rows whose voice moved are {moved}, not the ones the ruling names")
    if not all(row.get("spoken") for row in CLOSED_CLASS_ROWS
               if (row.get("role"), row["form"]) in VOICED):
        raise ValueError("a flag this migration names was taken away rather than given")

    # **THE TABLE'S LAW, RE-RUN IN FULL** (`db/0015`: a check travels with the data it guards) —
    # one voice per meaning, on the key the decompiler actually asks with; and a voice is only ever
    # a choice between two forms or more.
    spoken = [r for r in CLOSED_CLASS_ROWS if r.get("spoken")]
    voices: dict[tuple, str] = {}
    for row in spoken:
        meaning = _meaning(row)
        if meaning in voices:
            raise ValueError(f"{row['form']!r} and {voices[meaning]!r} both speak one meaning")
        voices[meaning] = row["form"]
    carriers: dict[tuple, int] = {}
    for row in CLOSED_CLASS_ROWS:
        carriers[_meaning(row)] = carriers.get(_meaning(row), 0) + 1
    for role, form in VOICED:
        row = next(r for r in CLOSED_CLASS_ROWS if (r.get("role"), r["form"]) == (role, form))
        if carriers[_meaning(row)] < 2:
            raise ValueError(f"{form!r} is the only form with its meaning — it needs no flag")


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(ClosedClassDoc, CLOSED_CLASS_ROWS)
