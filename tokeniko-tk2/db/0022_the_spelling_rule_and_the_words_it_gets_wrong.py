"""0022 — inflections v1: **the present tense is one rule and twenty-one exceptions** (req 9).

**WHY THE DECOMPILER NEEDS THIS AT ALL, measured rather than assumed.** A zip holds lemmas. Rendered
as lemmas, «A calculator never thinks» becomes «Think.» — and the station reads that back as an
IMPERATIVE, correctly, by its own `Mood=Imp` rule. **26 of the round trip's 32 failures were that one
artefact.** Inflection carries mood; a sentence without it says something else.

**THE RULE IS FRAME, THE EXCEPTIONS ARE ROWS.** `-ies` after a consonant-plus-`y`, `-es` after a
sibilant, `-s` otherwise: that is orthography, and orthography is frame for the same reason
punctuation is — the compiler reads it as structure, never as vocabulary. WHICH WORDS the rule gets
wrong is a revisable fact about English and lives here.

**GENERATED OFFLINE, THEN CURATED — and the curation was not a formality.** `lemminflect` was run over
all **20,364 verb lemmas WordNet holds**; the rule disagrees with it on 43. Of those 43, **22 are
defects in the instrument** rather than facts about English:

    ghostwrite -> «ghost-writes»     a hyphen inserted
    overshoot  -> «over shoots»      a SPACE inserted: not one word any more
    proofread  -> «proof reads»      the same
    jell       -> «gels»             a different word's inflection
    impanel    -> «empanels»         the same
    okay       -> «o.k.'s»           an apostrophe and two full stops
    torpedo    -> «torpedo»          no inflection at all, and plainly wrong
    distil / fulfil / instal         the AMERICAN spelling's inflection of a BRITISH lemma
    rendezvous -> «rendezvous»       uncertain, and left to the rule

*The library never ships. It is used the way WordNet is used to build the base — offline, as an
instrument — and its errors are caught by curation, which is what curation is for.* `torpedo` is in
the roster with the form the QM judged correct against the instrument's own answer, and is flagged
here so that judgement can be argued with.

**WHAT THE 21 ARE:** two true irregulars (`be`, `have`), the `-o`-after-a-consonant verbs that take
`-es` where most take `-s` (`go`, `do`, `echo`, `veto` and nine more — the rule takes the majority
side and these are the minority), three consonant-doublings (`quiz`, `whir`, `whiz`), and `stomach`,
whose `ch` is a /k/.

**ONLY `VBZ`.** The decompiler renders the present because it does not read the theatre yet. `VBD`
and `VBN` are their own generation and their own curation, on the day a slice needs them — and that
day the instrument's ~200 irregular pasts will need the same eye.

**Written by the QM on 2026-09-19, on the Captain's ruling that lemminflect be used as an OFFLINE
INSTRUMENT rather than admitted to the closed dependency list — because importing it loads spacy and
torch, which are deliberately not on that list (the provider lives behind the skeleton adapter).**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, InflectionDoc
from tk2.migrations import ensure_collections

VERSION = 1

TAG_PRESENT = "VBZ"

SOURCE = ("lemminflect 0.2.3 over all 20,364 verb lemmas in WordNet, 2026-09-19, curated by the QM "
          "against the spelling rule in `tk2.language.inflect`")

#: `(lemma, the form, what the rule would have said)`. The third column is kept so a later change to
#: the rule can be checked against every exception that claims to need it.
PRESENT_TENSE = (
    ("be", "is", "bes"),
    ("dado", "dadoes", "dados"),
    ("do", "does", "dos"),
    ("echo", "echoes", "echos"),
    ("embargo", "embargoes", "embargos"),
    ("forgo", "forgoes", "forgos"),
    ("go", "goes", "gos"),
    ("have", "has", "haves"),
    ("lasso", "lassoes", "lassos"),
    ("outdo", "outdoes", "outdos"),
    ("outgo", "outgoes", "outgos"),
    ("overdo", "overdoes", "overdos"),
    ("quiz", "quizzes", "quizes"),
    ("stomach", "stomachs", "stomaches"),
    ("torpedo", "torpedoes", "torpedos"),
    ("undergo", "undergoes", "undergos"),
    ("undo", "undoes", "undos"),
    ("veto", "vetoes", "vetos"),
    ("whir", "whirrs", "whirs"),
    ("whiz", "whizzes", "whizes"),
    ("zero", "zeroes", "zeros"),
)

NOTES = {
    "be": "the one true irregular, and the copula the decompiler speaks a predication with",
    "have": "the other true irregular",
    "torpedo": "THE INSTRUMENT SAID «torpedo», unchanged, which is wrong; this form is the QM's",
    "stomach": "the `ch` is a /k/, so the sibilant rule does not apply",
}

INFLECTION_ROWS = [
    {
        "version": VERSION,
        "lemma": lemma,
        "tag": TAG_PRESENT,
        "form": form,
        "instead_of": rule_says,
        "source": SOURCE,
        "note": NOTES.get(lemma, ""),
        "position": position,
    }
    for position, (lemma, form, rule_says) in enumerate(PRESENT_TENSE)
]


def _check() -> None:
    from tk2.language.inflect import present_tense_rule

    seen = set()
    for row in INFLECTION_ROWS:
        key = (row["lemma"], row["tag"])
        if key in seen:
            raise ValueError(f"{key} appears twice — one form per lemma per tag")
        seen.add(key)
        if row["form"] == row["instead_of"]:
            raise ValueError(f"{row['lemma']}: the rule already produces {row['form']!r}, so this "
                             f"row is not an exception to anything")
        # The row must disagree with the rule AS THE CODE STATES IT, not as this file remembers it.
        if present_tense_rule(row["lemma"]) != row["instead_of"]:
            raise ValueError(
                f"{row['lemma']}: the rule now says {present_tense_rule(row['lemma'])!r} and this "
                f"row was written against {row['instead_of']!r} — the rule moved under the roster")


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(InflectionDoc, INFLECTION_ROWS)
