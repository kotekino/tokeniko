"""0029 — closed classes v15: **a quantifier's voice depends on the NUMBER of the noun**.

**«All human beings are animals» came back «Every human beings are animals.»** The zip was right —
universal, over a plural restriction — and schema v6's compiler half had just made it right for the
first time. What was wrong is that `db/0021`'s flag answers *«this MEANING has several forms — which
one do we say?»* with **one** form per meaning, and English does not have one form here:

    every cat  ·  every human being          the universal over a SINGULAR noun
    all cats   ·  all human beings           the universal over a PLURAL noun

Same quantity, same sort, two words, and the noun's number is what picks between them. A flag keyed
without the number had to choose one and it chose «every», so every plural universal came out
ungrammatical.

**THIS IS THE THIRD TIME IN TWO DAYS THAT THE KEY WAS COARSER THAN THE MEANING** — after the
described unknown (schema v4) and the fused quantifier (`db/0028`, this morning, whose lesson was
that *the check and the lookup must ask the same question*). The shape is identical and so is the
fix: the thing that distinguishes two words goes **into the key**, on both sides.

---

**MEASURED, NOT ASSERTED.** `Box.number` is a fact about English and the standing law says a fact
about a language is curation, not code — so the witness is tk1's own stored journeys, 547 distinct
sentences of the Captain's real writing, parsed and counted by the noun each determiner modifies
(`det` / `det:predet` onto a `NOUN` or `PROPN`):

    det        Sing  Plur   observed
    all           0    24   «all minds»
    some          9    10   «some software» · «some softwares»
    no           10     0   «no value»
    every         7     0   «every cat»
    each          0     3   «each others»          <- «each other», not a determiner. DISCARDED
    both          0     3   «both minds»

**Only three rows earn a number from this**, and the rest earn none:

    every  ->  sg     7 against 0, and it is the half the defect was about
    all    ->  pl    24 against 0, and it is the other half
    both   ->  pl     3 against 0

`some` is attested BOTH ways in the same corpus, which is the evidence that it does not distinguish.
`no` is 10–0 here and «no cats» is plainly English, so the corpus under-witnesses it rather than
restricting it. `each` has three hits and all three are «each other» read as determiner + noun — an
artefact of the parse, not a fact about English, and it is discarded rather than believed.

**AN ABSENT `number` IS A MEANING AND NOT A GAP**: it says *this word does not distinguish*, exactly
as `either` does on a pronoun's case, and the decompiler answers such a row whichever number it is
asked for. So the honest reading of this migration is «three rows are restricted, everything else
was measured or left alone», and nothing was written on nobody's evidence.

**`both` takes the number and NOT the flag.** It is the DUAL — «the two of them» — which is more
than a bare universal states, and a word that says more than the zip does is the sin in this
direction too (req 8), the same reason `_fused` refuses `often` and `once`.

**Written by the QM on 2026-09-21, on the Captain's ruling «agree with your lean on the spoken flag,
go for the migration».**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, ClosedClassDoc
from tk2.migrations import ensure_collections

VERSION = 15

#: `(role, form, position) -> the features to merge in`, as `db/0023`'s and `db/0026`'s.
#: The number of the noun this determiner was OBSERVED to take. See the table in the docstring.
#:
#: **`takes_number` AND NOT `number`, AND THE DRILL GATE IS WHY.** A pronoun's `number` is ITS OWN —
#: «she» is singular — and `Compiler._unknown()` copies it into the `Open` a described unknown
#: carries (schema v4). A determiner's is the number of the NOUN IT TAKES, which is a different
#: fact about a different word, and writing it into the same column made «All that glitters is not
#: gold» compile its bare `all` to `Open(number='pl')` — a restriction the sentence never stated.
#: `aw-13` and `aw-14` went DISAGREED at the gate the moment it was tried, while the fixpoint stayed
#: flat: one column with two meanings is the defect this whole day has been about, in a third place.
TAKES_NUMBER = {
    ("quantificational", "every", 14): {"takes_number": "sg"},
    ("quantificational", "all", 13): {"takes_number": "pl"},
    ("quantificational", "both", 16): {"takes_number": "pl"},
}

#: `(role, form)` — v14's seventeen, plus «all», which is now the universal's PLURAL voice.
#: «every» keeps the singular one, and they no longer share a slot.
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
        if row.get("version") != 14:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = VERSION
        extra = TAKES_NUMBER.get((row["role"], row["form"], row.get("position")))
        if extra:
            new["features"] = {**(row.get("features") or {}), **extra}
        new["spoken"] = (new["role"], new["form"]) in SPOKEN
        out.append(new)
    return out


def _previous_rows():
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 28), None)
    if found is None:
        raise RuntimeError("0028 is gone — it holds the version this one extends")
    return found.load().CLOSED_CLASS_ROWS


CLOSED_CLASS_ROWS = build_rows(_previous_rows())

#: Unchanged, and checked — this migration adds a feature and sets a flag; it moves no spelling.
CLOSED_CLASS_FORMS = tuple(
    sorted({row["form"] for row in CLOSED_CLASS_ROWS if " " not in row["form"]})
)


def _meaning(row: dict) -> tuple:
    """A row's VOICE. **THIS IS `Decompiler._key()` AND IT MUST STAY THAT WAY.**

    A quantifier's voice is its quantity, the SORT it ranges over (`db/0028`) and now the NUMBER of
    the noun it takes. `db/0028` was written with `sort` here and without it in the index, and five
    flags were absorbed in silence; the rule that came out of it is that the check and the lookup
    ask the same question or the check is describing a different table.
    """
    import json

    features = row.get("features") or {}
    compiled = json.dumps(row.get("compiled") or {}, sort_keys=True)
    return (row["role"], compiled, features.get("sort"), features.get("takes_number"))


def _check() -> None:
    before = _previous_rows()
    if {r["form"] for r in before if " " not in r["form"]} != set(CLOSED_CLASS_FORMS):
        raise ValueError("THE EXCLUSION SET MOVED — D's vocabulary filter would change with it")
    if len(before) != len(CLOSED_CLASS_ROWS):
        raise ValueError("a row was added or lost — this migration sets a feature and a flag")
    if any(row.get("compiled") != was.get("compiled") or row.get("role") != was.get("role")
           for row, was in zip(CLOSED_CLASS_ROWS, before)):
        raise ValueError("a meaning or a role moved — this migration touches `features` and `spoken`")

    placed = {(row["role"], row["form"], row.get("position")) for row in CLOSED_CLASS_ROWS}
    missing = [key for key in TAKES_NUMBER if key not in placed]
    if missing:
        raise ValueError(f"{missing} name no row")

    touched = [row["form"] for row, was in zip(CLOSED_CLASS_ROWS, before)
               if row.get("features") != was.get("features")]
    if sorted(touched) != sorted(form for _, form, _ in TAKES_NUMBER):
        raise ValueError(f"{touched} gained a feature and the measurement names "
                         f"{[f for _, f, _ in TAKES_NUMBER]}")

    spoken = [r for r in CLOSED_CLASS_ROWS if r["spoken"]]
    if len(spoken) != len(SPOKEN):
        raise ValueError(f"{len(SPOKEN)} chosen and {len(spoken)} carry the flag")

    # **THE THING THIS MIGRATION EXISTS FOR**: the universal has two voices and they are told apart
    # by the number, so neither can silently take the other's slot.
    universal = {(r["features"] or {}).get("takes_number"): r["form"] for r in spoken
                 if (r.get("compiled") or {}).get("quantity") == "universal"
                 and r["role"] == "quantificational"}
    if universal != {"sg": "every", "pl": "all"}:
        raise ValueError(f"the universal speaks {universal} and it must speak every/sg and all/pl")

    # **ONE VOICE PER MEANING**, on the key the decompiler actually asks with — across roles too,
    # which is the widening `db/0023` made after «and» and «although» both claimed the same join.
    for scope in ("role", "meaning"):
        seen: dict[tuple, str] = {}
        for row in spoken:
            key = _meaning(row) if scope == "role" else _meaning(row)[1:]
            if key in seen:
                raise ValueError(f"{row['form']!r} and {seen[key]!r} both claim to speak the same "
                                 f"{scope} — the decompiler would have to choose, and it must not")
            seen[key] = row["form"]

    # **AND THE ARITHMETIC THAT WAS NOT BEING READ** (`db/0028`'s lesson): a flag sharing a key with
    # another flag is absorbed in silence, so the only honest test is that the index is as big as
    # the flag count.
    if len({_meaning(row) for row in spoken}) != len(spoken):
        raise ValueError("two flagged rows share a key — one of them would never be spoken")


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(ClosedClassDoc, CLOSED_CLASS_ROWS)
