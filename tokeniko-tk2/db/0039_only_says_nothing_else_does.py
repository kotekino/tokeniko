"""0039 — adverb kinds v4 and closed classes v21: **«only» says that nothing else does**, and **«as
long as» claims neither half** (parser-compiler, `E3.12.5.9` — the Captain's rulings `E3.12.5.9.12`
of 2026-09-26).

**THE RULINGS, AS HE GAVE THEM** *(«accepted all your leans»)*, the ones this file writes:

    4. Where the words live: «exclusive» (only · just · solely · merely) and «identifying» (exactly ·
       precisely) are per-word KNOWLEDGE, rows; «the associate goes to the consequent» is LOGIC,
       frame.
    6. «as long as» claims neither half, as «if» does.

and the ones the compiler reads them by, which are logic and live there (`Compiler._compose`,
`Compiler._focus`):

    1. «only X P» on a NOUN keeps P(X) claimed — a presupposition, kept as the definite's relative
       clause is (`E3.3.13`); on a CONDITION it does not — «only if» does not claim «if», which is
       what makes «if and only if» compose.
    2. Joins are truth-functional — the format's law. What is not («only because», a generic
       «when») is RECORDED as lost until it has a home, never dropped in silence.
    3. Normal form: «only if» → `CONV`, sentence order kept (row order carries scope); «if and only
       if» → `EQ`.

**WHAT THE STATION DID, MEASURED BEFORE THIS WAS WRITTEN** (`202609261500_only-and-the-conditionals
.md`): no row for any of the six, in either roster, so each fell to the MANNER default — «it rains in
an only manner» — and the «if» beside it kept its sufficient direction. **Every «only if» compiled
the reverse claim**, a wrong claim by `E3.12.5` (4), and the only trace was `defaulted`, outside the
zip.

**ONE MEANING PER WORD, AND IT IS NOT AN OPERATOR.** «only» does not ADD the converse to «if», it
REPLACES the direction: «I stay home only if it rains» is S → R and does not entail R → S. So the
row does not say «conv» — «only cats eat fish» has no join in it for a converse to reverse. It says
what the word MEANS wherever it stands — *nothing but its associate satisfies the frame* — and the
compiler, which reads the tree, decides what that does to the clause or the phrase the particle
hangs off. The two meanings, as `compiled`:

    {"kind": "focus", "focus": "exclusive"}      only · just · solely · merely   — the associate is
                                                 NECESSARY: nothing else does
    {"kind": "focus", "focus": "identifying"}    exactly · precisely             — necessary AND
                                                 sufficient: the associate and nothing else

**WHICH ROSTER: THE ADVERB KINDS, AND THE REASON IS `db/0013`'s.** The closed-class forms are a
STRUCTURE FILTER on D's vocabulary (`distribution.vocabulary` drops them), and the sealed base was
built against the set as it stands: six new single-word forms there would move the exclusion set
and change what D is built from — which is exactly the cost the Captain ruled the second table to
avoid (2026-09-16). The adverb kinds are the table the station ALREADY reads for an `ADV` under
`advmod`, which is how stanza tags every one of the six in every tree the bench saw, and its
`compiled` is the closed classes' own vocabulary — the two rosters stay one format. *Checked below:
none of the six is a closed-class form.*

**A FIFTH KIND, `focus`, BESIDE REQUIREMENT 23's FOUR.** None of the four says it: `epistemic` and
`evaluative` are prefix elements over a clause, `discourse` relates two rows the tree gives, and
`circumstantial` fills a box. A focus particle does none of these — it restricts which thing
satisfies the frame, and WHICH thing is the tree's to say (its associate). The name is the one the
chapter note already uses for the class («the focus particles have no row»). `manner` stays the
default and stays forbidden as a row.

**THE VOICES** — four forms for one meaning is a CHOICE, which is curation (`db/0035`'s shape):
«only» speaks the exclusive, the word the drill and the traffic attest (`only-2` … `only-6`,
`t-dc-4`); «exactly» speaks the identifying.

**NOT HERE, ON PURPOSE.** `strictly` and `even` — the bench's two other particles. The ruling named
six forms and no more; «strictly» is marginal English as a condition («strictly if», and stanza hangs
it off the MATRIX), and «even» is scalar, not exclusive. They stay where the manner default puts
them, which is `E3.12.5.9.3`'s remaining question and ruling 5's, not this file's.

**«AS LONG AS» CLAIMS NEITHER HALF.** v20 had it `asserts: both` since v4 (`db/0010`) — «I stay home
as long as it rains» claimed that it rains AND that I stay home. Its reading is the conditional one
(R → S, or ∀t R(t) → S(t)), which claims neither, as «if» does. The row's `relation: condition` has
said so all along; only `asserts` moves.

**Written by the 1st Officier on 2026-09-26, on the Captain's rulings of the same day. Nothing is
applied until the Captain says so.**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, AdverbKindDoc, ClosedClassDoc
from tk2.migrations import ensure_collections

CLOSED_VERSION = 21
ADVERB_VERSION = 4

#: The fifth adverb kind and its two meanings. NAMES and their vocabulary, not a roster: which words
#: carry them is the rows' business below.
FOCUS = "focus"
EXCLUSIVE = "exclusive"
IDENTIFYING = "identifying"

_RULING = ("the Captain, 2026-09-26 (E3.12.5.9.12, «accepted all your leans»): «exclusive» (only · "
           "just · solely · merely) and «identifying» (exactly · precisely) are per-word KNOWLEDGE, "
           "rows; «the associate goes to the consequent» is LOGIC, frame")

#: form -> (meaning, spoken, note). The six the ruling names, and no seventh.
FOCUS_ROWS = {
    "only": (EXCLUSIVE, True,
             "«only if it rains» — the condition is necessary; «only cats eat fish» — nothing but "
             "cats does. The voice of the exclusive: the word the drill and the traffic attest"),
    "just": (EXCLUSIVE, False,
             "«just if» — the exclusive as the ruling lists it. Its temporal reading («I JUST "
             "arrived») hangs off the verb, where the associate is not given and the station "
             "abstains"),
    "solely": (EXCLUSIVE, False, "«solely because», «solely by him»"),
    "merely": (EXCLUSIVE, False, "«merely a cat» — the exclusive, with a scale the zip does not keep"),
    "exactly": (IDENTIFYING, True,
                "«exactly when it rains» — necessary AND sufficient. The voice of the identifying"),
    "precisely": (IDENTIFYING, False, "«precisely when», «precisely if»"),
}

#: The one closed-class row this migration corrects: form -> why.
CORRECTED = {
    "as long as": "the conditional reading claims neither half, as «if» does (ruling 6). v20 claimed "
                  "both — «I stay home as long as it rains» asserted the rain",
}


def build_closed(previous: list[dict]) -> list[dict]:
    out = []
    for row in previous:
        if row.get("version") != CLOSED_VERSION - 1:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = CLOSED_VERSION
        if row["form"] in CORRECTED and row.get("role") == "subordinator":
            new["compiled"] = {**row["compiled"], "asserts": "neither"}
            note = row.get("note") or ""
            new["note"] = (f"{note} — " if note else "") + f"v21: {CORRECTED[row['form']]}"
        out.append(new)
    return out


def build_adverbs(previous: list[dict]) -> list[dict]:
    out = []
    for row in previous:
        if row.get("version") != ADVERB_VERSION - 1:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = ADVERB_VERSION
        out.append(new)
    position = 1 + max(r["position"] for r in out)
    for form, (meaning, spoken, note) in FOCUS_ROWS.items():
        out.append({
            "version": ADVERB_VERSION,
            "form": form,
            "kind": FOCUS,
            "compiled": {"kind": FOCUS, FOCUS: meaning},
            "source": _RULING,
            "note": note,
            "position": position,
            "spoken": spoken,
        })
        position += 1
    return out


def _previous(number: int, attribute: str):
    # **BY NUMBER**, never through `newest_migration_declaring` — that walks and loads every file in
    # `db/`, this one included, and `db/0013`'s first draft recursed until the stack died.
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == number), None)
    if found is None:
        raise RuntimeError(f"{number:04d} is gone — it holds the version this one extends")
    return getattr(found.load(), attribute)


CLOSED_CLASS_ROWS = build_closed(_previous(37, "CLOSED_CLASS_ROWS"))
ADVERB_KIND_ROWS = build_adverbs(_previous(35, "ADVERB_KIND_ROWS"))

#: **UNCHANGED** — the six focus particles went to the adverb kinds so that this would not move.
CLOSED_CLASS_FORMS = tuple(
    sorted({row["form"] for row in CLOSED_CLASS_ROWS if " " not in row["form"]})
)


def _meaning(row: dict) -> tuple:
    """An adverb row's VOICE. **THIS IS `Decompiler._key(None, compiled)` AND IT MUST STAY THAT
    WAY** — `db/0035`'s key, for `db/0029`'s reason."""
    compiled = row.get("compiled") or {}
    return (None, tuple(sorted((k, str(v)) for k, v in compiled.items())), None, None)


def _check() -> None:
    # ── the closed classes: one meaning moves, and nothing else ─────────────────────────────────
    before = [r for r in _previous(37, "CLOSED_CLASS_ROWS") if r.get("version") == CLOSED_VERSION - 1]
    if set(CLOSED_CLASS_FORMS) != {r["form"] for r in before if " " not in r["form"]}:
        raise ValueError("THE EXCLUSION SET MOVED — D's vocabulary filter would change with it")
    if len(CLOSED_CLASS_ROWS) != len(before):
        raise ValueError("a closed-class row was added or lost — this migration corrects one")
    for row, was in zip(CLOSED_CLASS_ROWS, before):
        if (row["form"], row.get("role"), row.get("word_class"), row.get("features"),
                row.get("spoken")) != (was["form"], was.get("role"), was.get("word_class"),
                                       was.get("features"), was.get("spoken")):
            raise ValueError(f"{was['form']!r}: a form, a role, a feature or a voice moved")
        corrected = was["form"] in CORRECTED and was.get("role") == "subordinator"
        if corrected:
            if row["compiled"] != {**was["compiled"], "asserts": "neither"}:
                raise ValueError(f"{was['form']!r}: only `asserts` may move, and only to neither")
        elif row.get("compiled") != was.get("compiled"):
            raise ValueError(f"{was['form']!r}: a meaning this migration does not name moved")
    if sorted(r["form"] for r, w in zip(CLOSED_CLASS_ROWS, before)
              if r["compiled"] != w["compiled"]) != sorted(CORRECTED):
        raise ValueError("the corrected rows are not the ones this migration names")

    # ── the adverb kinds: six rows added, and every earlier row as it was ───────────────────────
    earlier = [r for r in _previous(35, "ADVERB_KIND_ROWS") if r.get("version") == ADVERB_VERSION - 1]
    if len(ADVERB_KIND_ROWS) != len(earlier) + len(FOCUS_ROWS):
        raise ValueError(f"this migration adds exactly the {len(FOCUS_ROWS)} focus particles")
    if any({k: v for k, v in row.items() if k != "version"} !=
           {k: v for k, v in was.items() if k not in ("version", "_id")}
           for row, was in zip(ADVERB_KIND_ROWS, earlier)):
        raise ValueError("an existing adverb row moved — this migration only adds")
    added = ADVERB_KIND_ROWS[len(earlier):]
    if {r["form"] for r in added} != set(FOCUS_ROWS) or any(r["kind"] != FOCUS for r in added):
        raise ValueError("the rows added are not the six focus particles the ruling names")
    if len({r["position"] for r in ADVERB_KIND_ROWS}) != len(ADVERB_KIND_ROWS):
        raise ValueError("two adverb rows share a position")

    # **THE TABLE'S LAWS, RE-RUN IN FULL** (`db/0015`: a check travels with the data it guards).
    closed = {row["form"] for row in CLOSED_CLASS_ROWS}
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

    # **ONE VOICE PER MEANING**, on the key the decompiler actually asks with — and each of the two
    # focus meanings HAS one, because the decompiler composes «only if» from it.
    spoken = [r for r in ADVERB_KIND_ROWS if r.get("spoken")]
    if len({_meaning(row) for row in spoken}) != len(spoken):
        raise ValueError("two flagged adverbs share a meaning — one of them would never be spoken")
    for meaning, voice in ((EXCLUSIVE, "only"), (IDENTIFYING, "exactly")):
        said = [r["form"] for r in spoken if r["compiled"] == {"kind": FOCUS, FOCUS: meaning}]
        if said != [voice]:
            raise ValueError(f"the {meaning} is voiced by {said}, not by «{voice}» alone")


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(ClosedClassDoc, CLOSED_CLASS_ROWS)
    writer.insert_many(AdverbKindDoc, ADVERB_KIND_ROWS)
