"""0028 — closed classes v14: **the quantifier that is its own noun** (parser-compiler req 9).

**«Nobody knows the answer» was decompiling to «The answer is known.»** — the truth inverted, which
is the sin req 8 names, and not a word dropped. The 1st Officier's `aw-13` work made the station
compile a bare quantifier properly for the first time: it now raises a binder whose restriction says
only what the PHRASE said — `Open(sort='person')`, schema v4's described unknown — and the
decompiler had no way to turn a quantity plus a sort back into a word, so the subject came out empty
and the clause passivised around the hole.

**THE ROWS ALREADY KNEW.** Every fused form in the table carries its `sort` and its `force`:

    everyone · everybody   universal   person        nothing      negative     thing
    someone  · somebody    existential person        everywhere   universal    place
    no one   · nobody      negative    person        nowhere      negative     place
    everything             universal   thing         never        negative     time
    something              existential thing         always       universal    time

So this migration adds no knowledge at all. What it does is say, in the column that decides, a
thing the table has always recorded in a column nobody keyed on.

---

**«no» IS A DETERMINER AND «nobody» IS A NOUN PHRASE, AND THE ROLE NOW SAYS SO.**

The first version of this migration only set `spoken` on the five fused forms English has two words
for, and it **cost the fixpoint five sentences**: «There is nobody cat», «I work everyone day»,
«not everyone cloud produces rain», «Everyone teacher gave somewhere student a book», «Somewhere
software is mind». The decompiler's spoken index is keyed on `(role, compiled)` — and `no` and
`nobody` have **identical** `compiled`, `{'kind': 'quantifier', 'quantity': 'negative'}`. Five flags
landed on three occupied slots and overwrote them in silence:

    universal     ['every', 'everyone']                         ->  said 'everyone'
    existential   ['some', 'someone', 'something', 'somewhere']  ->  said 'somewhere'
    negative      ['no', 'nobody']                              ->  said 'nobody'

**The count was the tell and nothing was reading it**: seventeen rows carried the flag and the index
held twelve keys, before and after, so five flags were absorbed without a word. This migration now
checks that too, because a check that cannot see its own arithmetic is decoration.

The fix is not to teach the index to tolerate two words in one slot. It is that they are **not the
same kind of word**: `no` takes a noun and `nobody` IS one, which is a difference of JOB and `role`
is the column for the job. The table has always known it — `word_class` is `determiner` on one and
`pronoun` on the other — and only `role` failed to say so. So every quantificational row whose
word class is not `determiner` moves to **`fused_quantifier`**, and the collision cannot occur: the
determiners keep the plain quantifier slots and the fused forms have their own.

*The split is exact and the table drew it, not this file: all 25 rows carrying a `sort` are pronouns
or adverbs, every determiner is sortless, and the one sortless pronoun — `none` — is fused too
(«none of the cats» is its own phrase), which is why the criterion is the word class and not the
sort.*

**AND THE CHECK IS KEYED ON WHAT THE LOOKUP IS KEYED ON**, which is the lesson the five sentences
paid for: the first version widened `_meaning()` to include `sort` and left `Decompiler._voices()`
keyed on `(role, compiled)`, so `no` and `nobody` were two meanings to the check and one meaning to
the index. **The check and the lookup must ask the same question or the check is asking about a
different table.** Both now key on `(role, compiled, sort)` — a quantifier's voice is its quantity
AND the sort it ranges over — and each of the two places says so with the other one named.

---

**WHICH FORM SPEAKS**, for the five pairs English has two words for — `db/0021`'s flag doing
`db/0021`'s job, now inside the fused role where the meaning is `(quantity, sort)`:

    universal   + person   ->  everyone     («everybody» is the same meaning in a warmer register)
    existential + person   ->  someone      («somebody» likewise)
    negative    + person   ->  nobody       («no one» is the same word with a space in it)
    existential + thing    ->  something    against «anything»
    existential + place    ->  somewhere    against «anywhere»

**The `any-` series is the same meaning under a different POLARITY** — «anybody» is at home in a
question and a negation and not in a plain statement — and only `any` itself carries the
`polarity: negative-context` feature that says so. Rather than write that feature onto four more
rows on no witness, the flag settles it: a plain statement says «someone», and the day a zip needs
«anyone» it will be because polarity reached the format, which it has not.

*Every other (quantity, sort) pair already has exactly one plain form — «everywhere», «nowhere»,
«nothing», «always», «never» — and needs no flag, which is the rule `db/0021` set and this keeps.*

**Written by the QM on 2026-09-20, on a defect the 1st Officier's work exposed in the QM's file.
Rewritten on 2026-09-21 — it had never been applied — after the fixpoint measured its cost.**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, ClosedClassDoc
from tk2.migrations import ensure_collections

VERSION = 14

#: The job of a quantifier that IS its own noun phrase, against the `quantificational` determiner
#: that takes one. A string, like every other role — `ClosedClassDoc.role`'s own note says the
#: roster is a description of a language and a role that needed a code change to exist would put
#: the table back in code.
FUSED = "fused_quantifier"

#: `(role, form)` — the five fused forms whose meaning has a twin. The determiners `every` · `some`
#: · `no` keep theirs from v12 and no longer share a slot with these.
SPOKEN = (
    ("negation", "not"),
    ("quantificational", "every"),
    ("quantificational", "some"),
    ("quantificational", "no"),
    (FUSED, "everyone"),
    (FUSED, "someone"),
    (FUSED, "nobody"),
    (FUSED, "something"),
    (FUSED, "somewhere"),
    ("coordinator", "and"),
    ("subordinator", "because"),
    ("subordinator", "if"),
    ("subordinator", "when"),
    ("determination", "a"),
    ("modality", "can"),
    ("modality", "must"),
    ("tense_aspect", "will"),
)


def _fused_row(row: dict) -> bool:
    """Is this a quantifier that is its own phrase? **The word class decides, and it always knew.**"""
    return row.get("role") == "quantificational" and row.get("word_class") != "determiner"


def build_rows(previous: list[dict]) -> list[dict]:
    out = []
    for row in previous:
        if row.get("version") != 13:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = VERSION
        if _fused_row(row):
            new["role"] = FUSED
        new["spoken"] = (new["role"], new["form"]) in SPOKEN
        out.append(new)
    return out


def _previous_rows():
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 26), None)
    if found is None:
        raise RuntimeError("0026 is gone — it holds the version this one extends")
    return found.load().CLOSED_CLASS_ROWS


CLOSED_CLASS_ROWS = build_rows(_previous_rows())

#: Unchanged, and checked — this migration moves a role and sets a flag, and touches no spelling.
CLOSED_CLASS_FORMS = tuple(
    sorted({row["form"] for row in CLOSED_CLASS_ROWS if " " not in row["form"]})
)


def _meaning(row: dict) -> tuple:
    """A row's VOICE — and for a quantifier the SORT is part of it.

    **THIS IS `Decompiler._voices()`'s KEY AND IT MUST STAY THAT WAY.** The decompiler builds
    MEANING → the one form that speaks it, and a check keyed on anything else is checking a
    different table: the first version of this migration keyed on `sort` here and left the index
    keyed without it, so `no` and `nobody` were two meanings to the check and one slot to the index,
    and the index kept whichever row came last.
    """
    import json

    compiled = json.dumps(row.get("compiled") or {}, sort_keys=True)
    return (row["role"], compiled, (row.get("features") or {}).get("sort"))


def _check() -> None:
    before = _previous_rows()
    if {r["form"] for r in before if " " not in r["form"]} != set(CLOSED_CLASS_FORMS):
        raise ValueError("THE EXCLUSION SET MOVED — D's vocabulary filter would change with it")
    if len(before) != len(CLOSED_CLASS_ROWS):
        raise ValueError("a row was added or lost — this migration moves a role and sets a flag")
    if any(row.get("compiled") != was.get("compiled") or row.get("features") != was.get("features")
           for row, was in zip(CLOSED_CLASS_ROWS, before)):
        raise ValueError("a meaning or a feature moved — this migration touches `role` and `spoken`")

    # **THE ROLE MOVED FOR EXACTLY THE ROWS THE WORD CLASS NAMES**, and for no others.
    moved = [row["form"] for row, was in zip(CLOSED_CLASS_ROWS, before)
             if row["role"] != was["role"]]
    should = [row["form"] for row in before if _fused_row(row)]
    if moved != should:
        raise ValueError(f"{sorted(set(moved) ^ set(should))} moved role and should not have, "
                         f"or should have and did not")
    # **THE SPLIT IS THE TABLE'S, NOT THIS FILE'S**: after the move, no row left in the plain
    # quantifier role carries a sort, and every row that does is fused. *(An interrogative carries
    # a sort too — «who» ranges over persons — and it is a different role and not in question.)*
    if any(row["role"] == "quantificational" and (row.get("features") or {}).get("sort")
           for row in CLOSED_CLASS_ROWS):
        raise ValueError("a DETERMINER carries a sort — the split this migration draws is wrong")

    spoken = [r for r in CLOSED_CLASS_ROWS if r["spoken"]]
    if len(spoken) != len(SPOKEN):
        raise ValueError(f"{len(SPOKEN)} chosen and {len(spoken)} carry the flag")

    # **ONE VOICE PER MEANING**, on the key the decompiler actually asks with — including across
    # roles, which is the widening `db/0023` made after «and» and «although» both claimed to speak
    # the same join.
    for scope in ("role", "meaning"):
        seen: dict[tuple, str] = {}
        for row in spoken:
            key = _meaning(row) if scope == "role" else _meaning(row)[1:]
            if key in seen:
                raise ValueError(f"{row['form']!r} and {seen[key]!r} both claim to speak the same "
                                 f"{scope} — the decompiler would have to choose, and it must not")
            seen[key] = row["form"]

    # **AND THE ARITHMETIC THAT WAS NOT BEING READ.** A flag that shares a key with another flag is
    # absorbed in silence, so the only honest test is that the index is as big as the flag count.
    if len({_meaning(row) for row in spoken}) != len(spoken):
        raise ValueError("two flagged rows share a key — one of them would never be spoken")

    # A flag on a meaning only ONE form carries would be noise: the table already answers there.
    counts: dict[tuple, int] = {}
    for row in CLOSED_CLASS_ROWS:
        if row.get("compiled"):
            counts[_meaning(row)] = counts.get(_meaning(row), 0) + 1
    for row in spoken:
        if counts.get(_meaning(row), 0) < 2:
            raise ValueError(f"{row['form']!r} is the only form with its meaning — it needs no flag")


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(ClosedClassDoc, CLOSED_CLASS_ROWS)
