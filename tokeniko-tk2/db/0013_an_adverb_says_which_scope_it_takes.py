"""0013 — the adverb kinds: which of requirement 23's four scopes an adverb takes.

**REQUIREMENT 23 SPLIT ADVERBS FOUR WAYS AND NOTHING SAID WHICH IS WHICH.** *«Adverbs split four
ways by scope — manner → a box · epistemic/evaluative → clause properties · circumstantial → a box
or the quantifier · discourse → between-row operators.»* The station met the consequence at the UD
gate: `early` in «left early in the morning» and `here` in «they come here» are content words with
no home, and the compiler could only leave them unplaced.

**THE RESOURCE CANNOT ANSWER IT. MEASURED 2026-09-16, BEFORE ANY ROW WAS WRITTEN:**

- **WordNet files every adverb under ONE lexicographer class, `adv.all`.** The supersense that
  settled the thirteen ambiguous markers (`db/0012`) says nothing at all here — 26 noun classes and
  15 verb classes, and one adverb class.
- **Adverbs have NO HYPERNYMS.** Zero, across every probe. So R is structurally thin for them and
  the taxonomy walk that would answer «is this a time adverb or a manner adverb» does not exist.
- What remains is the **pertainym**, the adjective an `-ly` adverb derives from — and it separates
  DERIVED from UNDERIVED, not manner from epistemic: `quickly → quick` and `probably → probable`
  both have one.

So it is curation. The question was only whether the set can be enumerated at all, and it can,
because of the next paragraph.

**MANNER IS THE DEFAULT AND NEEDS NO ROW.** Of WordNet's 3,767 single-word adverbs, **79% end in
`-ly` and 73% carry a pertainym** — derived from an adjective, describing the action. A compiler that
defaults to a manner box is right about the overwhelming majority for free, and this table holds only
the EXCEPTIONS: the epistemic, the evaluative, the discourse connectives and the non-`-ly`
circumstantials. **That is what turns an open class into a curatable one** — not a roster of adverbs,
a roster of the ones that are not what an adverb usually is.

**WHY A SECOND TABLE AND NOT CLOSED CLASSES v7** *(the Captain's ruling, 2026-09-16)*. «however»
compiles to a JOIN exactly as «because» does and «probably» to a MODALITY exactly as «may» does, so
by the second standing law they are structure and the closed-class table is where structure lives.
The obstacle is a cost, not a principle: **the closed-class forms are a STRUCTURE FILTER on D's
vocabulary** (`distribution.vocabulary` drops them — a function word is compiled and never defined),
so sixty new forms would change what D is built from, and the sealed base was built against the set
as it stands. The base is untouched instead.

**The cost the Captain named is that «what does this word compile to» now has two tables.** It is
paid by making only the ROSTER second: `compiled` here holds the identical vocabulary
`ClosedClassDoc.compiled` holds, so a reader asks one, misses, asks the other, and cannot tell which
answered. **If the exclusion set ever stops being load-bearing these rows merge upward and nothing
above notices.** The drift that would have made that merge dangerous was closed the same morning —
`SpaceOrigin` now carries the closed-class version, so a table moving under a sealed base is visible.

**THE CLASH CHECK EARNED ITS PLACE ON THE FIRST RUN, AND WHAT IT FOUND IS A FINDING ABOUT THE
CLOSED CLASSES RATHER THAN ABOUT THIS TABLE.** The first draft held **eleven** forms the closed
classes already hold, and ten of them were already compiled CORRECTLY there:

    so · yet · notwithstanding        already `join` — imply, and, and-concessive
    anywhere · everywhere · nowhere   already `quantifier` — they quantify over PLACES
    somewhere                         likewise
    inside · outside                  already a `box`, roles [location]
    besides                           already an exceptive `restriction`

So the closed-class table is **more complete than this migration assumed**, and the honest move was
to delete eleven rows rather than to argue with it. *A roster written without checking the roster
next to it is how one fact acquires two homes, which is the exact cost this table was ruled to pay
carefully.*

**THE ELEVENTH IS A REAL GAP AND IT IS NAMED RATHER THAN PAPERED OVER.** `however` has ONE
closed-class row — `pronoun / free_relative / open`, which is «however you do it». **Its discourse
reading has no row anywhere**, and it cannot come here because the form is taken. The right home is
a second closed-class ROW, which is what that table already does for the 45 forms holding several
jobs — and, load-bearing: **a second row for an EXISTING form does not move the exclusion set**,
because that set is a set of FORMS. So the fix is available and cheap, and it is a separate ruling.

**ONE FORM MAY HOLD TWO KINDS HERE TOO.** `still` is a TIME adverb in «he is still here» and a
concessive in «still, he left». The unique key is (form, kind), exactly as the closed classes key on
(form, class, role) — collapsing them would lose the distinction a parser needs most.

**THREE FORMS ARE DELIBERATELY ABSENT AND THE REASON IS THE SAME EACH TIME.** `here`, `now` and
`then` already have closed-class rows (`referential` — resolved to an entity from context), and a
second row here would be the two-tables cost turning into an actual contradiction. **A form this
table holds must not be a form the closed classes hold**, and the check below enforces it.

**Written by the QM on 2026-09-16, on the Captain's «a separate adverb-kinds table».**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, AdverbKindDoc
from tk2.migrations import ensure_collections

VERSION = 1

SOURCE = ("requirement 23's four-way split, enumerated against WordNet's adverb inventory "
          "(3,767 single-word adverbs, 79% -ly) — the exceptions to the manner default")

# ── the four kinds ───────────────────────────────────────────────────────────────────────────────
EPISTEMIC = "epistemic"            # a claim ABOUT the claim -> the prefix's modality element
EVALUATIVE = "evaluative"          # the speaker's attitude to it -> the prefix's attitude element
DISCOURSE = "discourse"            # it relates two ROWS -> a join
CIRCUMSTANTIAL = "circumstantial"  # it fills a box -> `roles` says which

#: `manner` is NOT a kind here. It is the default, and a row asserting it would be the roster of an
#: open class that this table exists to avoid writing.

# ── epistemic: a claim about the claim ───────────────────────────────────────────────────────────
# These are the adverbial spelling of the MODALS, and they carry the same two values `db/0001` gave
# `can`/`may` (possibility) and `must` (necessity). «He probably left» asserts possibility, never
# membership — the same maxim the modal rows were written under.
POSSIBILITY = ("probably", "possibly", "perhaps", "maybe", "apparently", "presumably",
               "supposedly", "allegedly", "arguably", "seemingly", "conceivably")
NECESSITY = ("certainly", "obviously", "clearly", "evidently", "undoubtedly", "definitely",
             "surely", "necessarily", "plainly", "manifestly")

# ── evaluative: the speaker's attitude to the claim ──────────────────────────────────────────────
# NOT epistemic: «luckily he left» asserts that he left — the speaker doubts nothing and is telling
# you how to feel about it. That is the prefix's ATTITUDE element, which E2 put there for exactly
# this: an attitude scopes a matrix and does not change its truth.
EVALUATIVE_FORMS = ("luckily", "fortunately", "unfortunately", "sadly", "regrettably", "thankfully",
                    "mercifully", "surprisingly", "oddly", "curiously", "admittedly", "frankly",
                    "honestly", "hopefully", "ideally", "predictably", "inevitably")

# ── discourse: it relates two ROWS, so it is a join ──────────────────────────────────────────────
# The operator is tkzip's own, and the concessive ones take the SAME treatment `db/0008` gave the
# concessive prepositions: truth-functionally AND, with the defeated expectation parked by name in
# `pragmatic` so the figurative layer can find its cases when it is built.
DISCOURSE_IMPLY = ("therefore", "thus", "hence", "consequently", "accordingly")
# `however`, `yet`, `notwithstanding` and `still` are NOT here — the first three are closed-class
# forms already (and `however` only in its free-relative reading, which is the gap named above);
# `still` is here as a TIME adverb and takes its concessive row beside it.
DISCOURSE_CONCESSIVE = ("nevertheless", "nonetheless", "conversely", "anyway", "regardless")
DISCOURSE_AND = ("moreover", "furthermore", "additionally", "also", "similarly", "likewise",
                 "finally")
DISCOURSE_OR = ("otherwise", "alternatively", "instead")

# ── circumstantial: it fills a box, and `roles` says which ───────────────────────────────────────
# The non-`-ly` ones, because the `-ly` ones are manner by default and right to be. `here`, `now` and
# `then` are NOT here — the closed classes already hold them as referential.
TIME_FORMS = ("yesterday", "today", "tomorrow", "tonight", "soon", "early", "late", "already",
              "still",
              "afterwards", "beforehand", "meanwhile", "nowadays", "lately",
              "recently", "previously", "formerly", "thereafter", "presently", "shortly",
              "immediately", "instantly", "henceforth")
LOCATION_FORMS = ("abroad", "upstairs", "downstairs", "indoors", "outdoors", "overseas",
                  "nearby", "elsewhere", "ashore", "aboard", "underground", "overhead",
                  "downtown")
DIRECTION_FORMS = ("backwards", "forwards", "sideways", "upwards", "downwards", "onwards",
                   "homewards", "northwards", "southwards", "eastwards", "westwards")


def _rows():
    out, position = [], 0

    def add(form, kind, compiled, note=""):
        nonlocal position
        out.append({"version": VERSION, "form": form, "kind": kind, "compiled": compiled,
                    "source": SOURCE, "note": note, "position": position})
        position += 1

    for form in POSSIBILITY:
        add(form, EPISTEMIC, {"kind": "prefix", "element": "modality", "modality": "possibility"},
            "the adverbial spelling of `may`/`can` — asserts possibility, never membership")
    for form in NECESSITY:
        add(form, EPISTEMIC, {"kind": "prefix", "element": "modality", "modality": "necessity"},
            "the adverbial spelling of `must` — asserts necessity, not bare assertion")
    for form in EVALUATIVE_FORMS:
        add(form, EVALUATIVE, {"kind": "prefix", "element": "attitude", "attitude": "evaluative"},
            "«luckily he left» ASSERTS that he left; the speaker doubts nothing and says how to "
            "feel about it. An attitude scopes a matrix and does not change its truth")
    for form in DISCOURSE_IMPLY:
        add(form, DISCOURSE, {"kind": "join", "operator": "imply"},
            "relates two ROWS; the marked one is the consequent")
    for form in DISCOURSE_CONCESSIVE:
        add(form, DISCOURSE, {"kind": "join", "operator": "and", "pragmatic": "concessive"},
            "truth-functionally AND — the defeated expectation is not truth-functional and is "
            "parked by name, exactly as db/0008 parked the concessive prepositions")
    for form in DISCOURSE_AND:
        add(form, DISCOURSE, {"kind": "join", "operator": "and"}, "")
    # «still, he left» — the concessive reading beside its TIME row. Same form, two kinds, and the
    # closed classes do exactly this for the 45 forms that hold several jobs.
    add("still", DISCOURSE, {"kind": "join", "operator": "and", "pragmatic": "concessive"},
        "«he is STILL here» is time and «STILL, he left» is concessive; both readings are real and "
        "the dependency is what chooses")
    for form in DISCOURSE_OR:
        add(form, DISCOURSE, {"kind": "join", "operator": "or"},
            "«otherwise» is the alternative branch — an inclusive OR between the rows")
    for form in TIME_FORMS:
        add(form, CIRCUMSTANTIAL, {"kind": "box", "roles": ["time"]}, "")
    for form in LOCATION_FORMS:
        add(form, CIRCUMSTANTIAL, {"kind": "box", "roles": ["location"]}, "")
    for form in DIRECTION_FORMS:
        add(form, CIRCUMSTANTIAL, {"kind": "box", "roles": ["direction"]},
            "req 67's eighteenth role: a direction with no endpoint")
    return out


ADVERB_KIND_ROWS = _rows()


def _check() -> None:
    """**A FORM THIS TABLE HOLDS MUST NOT BE A FORM THE CLOSED CLASSES HOLD.** Two rosters are the
    cost the Captain accepted; two rosters DISAGREEING is the cost turning into a defect, and it is
    the one thing that makes «ask one, then the other» unsafe. `here`, `now`, `then`, `once` and the
    quantificational adverbs are already closed-class rows and are deliberately absent.
    """
    # **READ MIGRATION 12 BY NUMBER, never `standing_closed_classes()`.** That helper asks «which is
    # the NEWEST migration declaring CLOSED_CLASS_ROWS», which walks and LOADS every migration in
    # `db/` — including this one, whose import runs this check, which asks again. The first draft
    # recursed until the stack died. A migration's import-time check may only read migrations that
    # already exist, and by number.
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 12), None)
    if found is None:
        raise RuntimeError("0012 is gone — it holds the closed-class set this table must not clash "
                           "with")
    forms = {row["form"] for row in found.load().CLOSED_CLASS_ROWS}
    clash = sorted({row["form"] for row in ADVERB_KIND_ROWS if row["form"] in forms})
    if clash:
        raise ValueError(
            f"{len(clash)} form(s) are in BOTH rosters and a reader could not tell which answers: "
            f"{clash}. A closed-class form is already compiled; remove it here or move it there."
        )

    # ONE FORM MAY HOLD TWO KINDS, exactly as a closed-class form holds two jobs — «still» is a TIME
    # adverb in «he is still here» and a concessive in «still, he left», and collapsing them would
    # lose the distinction the parser needs most. The unique key is (form, kind), which is what the
    # model's own index says; a repeated PAIR is the error.
    seen = set()
    for row in ADVERB_KIND_ROWS:
        key = (row["form"], row["kind"])
        if key in seen:
            raise ValueError(f"{row['form']!r} appears twice as {row['kind']}")
        seen.add(key)
    if any(row["kind"] == "manner" for row in ADVERB_KIND_ROWS):
        raise ValueError("`manner` is the DEFAULT and may not be a row — that is the roster of the "
                         "open class this table exists to avoid writing")


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(AdverbKindDoc, ADVERB_KIND_ROWS)
