"""0042 — open priors v1: **a tag question expects its answer** (tkzip req 50 — the Captain's ruling
on `E3.3.11.2.21`, 2026-09-27).

**THE RULING, AS THE QM RELAYED IT** *(«all your ruling, go»)*:

    7. A tag question (E3.3.11.2.21): req 50 — the host OPEN with a high PRIOR, the prior's value
       knowledge with a counted default (as `strength`, req 23) — or the 09-18 reading, claimed and
       then asked. QM's lean: req 50. A claim and a question about that same claim contradict each
       other; the prior holds exactly what the speaker does — expects, and asks. One rule then
       covers every host, coordinated or conditional, and every tag.

    RULED: … a tag question is req 50's: the host OPEN with a high prior, the prior knowledge with
    a counted default (the 09-18 note's «claim then ask» superseded).

**WHAT THE STATION DID, MEASURED BEFORE THIS WAS WRITTEN** (`202609261600_the-attitude-takes-its-
matrix-place.md`, round 3): «She slept, didn't she?» was withheld whole — the tag's verb is elided,
and the host went with it because req 50's prior «is not built»; «He is tired, isn't he?» claimed
the tiredness and asked a copula with no complement, and said back nothing at all; «If it rains, she
stays, doesn't she?» claimed the conditional. Three answers to one question, and the first was the
only honest one.

**IT IS A ROW BECAUSE IT IS A FACT ABOUT ENGLISH, NOT ABOUT LOGIC** — `db/0020`'s argument, word for
word, one slot over. How much «isn't it?» expects is the baseline that intonation, «surely» and «…,
right?» move away from; a constant in the compiler would make each of those a code change. What the
TREE says is only the shape: a tag hangs off its host by `parataxis`, heads itself with the host's
auxiliary, and carries its own polarity — and the polarity against the host's is the whole of what
tells the two shapes apart.

**ONE ROW, AND THE SECOND SHAPE IS NAMED AND NOT WRITTEN.** A tag of the host's OWN polarity — «So
she slept, did she?» — is a different act: it infers, or doubts, or mocks, and nothing in the corpora
witnesses how much it expects. It has a name in the reader (`CONSTANT_TAG`) so the station can say
what it met, and no row, so the station withholds it: *a class enters on a witness, not on a
principle* (the standing law of 2026-09-18). Req 50's «It's cold, isn't it?» is this row's witness.

**THE NUMBER IS 0.8, AND IT IS A CURATION, NOT A MEASUREMENT.** Req 50 says «high» and gives no
figure, and no drill case hand-compiles one. It is set below the bare imperative's 0.9 (`db/0020`)
on purpose: a tag asks because the speaker is NOT sure, where a command is as sure as a want gets.
The gates compare the SLOT — stated against unstated — never the magnitude, so re-curating it is a
migration and not a red gate.

**Written by the 1st Officier on 2026-09-27, on the Captain's ruling of the same day. Nothing is
applied until the Captain says so.**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, OpenPriorDoc
from tk2.migrations import ensure_collections

VERSION = 1

_RULING = ("the Captain, 2026-09-27 (E3.3.11.2.21, «all your ruling, go»): a tag question is req "
           "50's — the host OPEN with a high prior, the prior knowledge with a counted default; the "
           "09-18 note's «claim then ask» superseded")

OPEN_PRIOR_ROWS = [
    {
        "version": VERSION,
        "shape": "reversed_tag",
        "compiled": {"prior": 0.8},
        "source": f"tkzip req 50's own witness, «It's cold, isn't it?» — {_RULING}",
        "note": ("a tag of the polarity OPPOSITE to its host's: «isn't it?» after «it is», «is it?» "
                 "after «it isn't». The same-polarity tag («did she?» after «she slept») has no row "
                 "and is withheld"),
        "position": 0,
    },
]


def _check() -> None:
    from tk2.language.prior import CONSTANT_TAG, REVERSED_TAG

    shapes = [r["shape"] for r in OPEN_PRIOR_ROWS]
    if sorted(shapes) != sorted(set(shapes)):
        raise ValueError(f"one row per shape of asking — got {shapes}")
    # A row the reader cannot ask for is a note in the wrong place (`db/0020`'s law).
    unknown = set(shapes) - {REVERSED_TAG, CONSTANT_TAG}
    if unknown:
        raise ValueError(f"{sorted(unknown)}: no shape the station recognises")
    if CONSTANT_TAG in shapes:
        raise ValueError("the same-polarity tag has no witness, and so no row (2026-09-18's law)")
    for row in OPEN_PRIOR_ROWS:
        prior = row["compiled"].get("prior")
        if not isinstance(prior, (int, float)) or not 0.0 <= prior <= 1.0:
            raise ValueError(f"{row['shape']}: {prior!r} is not a prior in [0, 1]")
        # **HIGH, BY THE RULING** — a prior of *yes* at or below one half expects nothing, or the
        # opposite, and the decompiler would say a tag the zip does not hold.
        if prior <= 0.5:
            raise ValueError(f"{row['shape']}: {prior} does not expect its answer — req 50 says high")


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(OpenPriorDoc, OPEN_PRIOR_ROWS)
