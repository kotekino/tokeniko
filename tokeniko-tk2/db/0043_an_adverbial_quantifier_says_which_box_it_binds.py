"""0043 — closed classes v23 · adverb kinds v6: **an adverbial quantifier says which box it binds, and
what it cannot say it says it cannot** (parser-compiler, `E3.3.11.2.9` — the Captain's rulings
`E3.3.11.2.9.1` … `E3.3.11.2.9.12` of 2026-09-27).

**THE RULINGS, AS THE QM RECORDED THEM** *(the Captain, 2026-09-27: «Agreed on all your leans. Go»;
`docs/E3-parser-compiler/202609271400_the-adverbial-quantifiers.md`)*:

    1. E3.3.11.2.9.1 «never» is ONE NEGATIVE binder over Open(sort=time) — one spelling for nobody,
       nothing, nowhere, never; tkzip reqs 32 / 72 amended; the drill's nha-1, nha-2 amended now
    2. E3.3.11.2.9.2 proportions withheld; later a fuzzy proportion on the binder, its values as
       rows; «seldom»'s row corrected now (it is not `negative`)
    3. E3.3.11.2.9.3 «ever» is ∃ with a polarity feature, as «any» has
    4. E3.3.11.2.9.4 the count built for «twice»; «once» withheld (two readings)
    5. E3.3.11.2.9.5 a negative adverbial binder after a modal follows the modal row's
       following_negation (db/0036): «can never» ¬◇ · «must never» □¬ · «need never» ¬□ · «may
       never» withheld; a positive one withheld until a row states it
    6. E3.3.11.2.9.6 the decompiler's mid-clause rule for a quantified time is FRAME (word order)
    7. E3.3.11.2.9.7 a polarity feature on the «any-» rows; the decompiler says the «any-» form
       under a negation or a negative binder
    8. E3.3.11.2.9.12 the ratchets re-based to the honest numbers

Rulings 1, 5, 6 and 8 are the compiler's, the decompiler's and the tests'. **This file holds the
knowledge of 2, 3, 4 and 7, and the box every adverbial quantifier binds.**

---

**ONE — THE BOX.** «He never sleeps» came back «He sleeps»: the reverse, in silence. «never» is ¬∃t —
the binder «nobody» raises, its variable in the TIME box — and no relation names that box (`advmod`
is not a nominal one), so the ROW does, in `compiled.roles`, exactly as `db/0014` did it for «here»
and «now». All thirteen adverbial fused quantifiers, the withheld ones too — which box «often» ranges
over is true of it whatever its force means:

    always · never · ever · sometimes · often · seldom · once · twice    ->  time
    everywhere · somewhere · anywhere · nowhere                          ->  location
    somehow                                                              ->  manner

*Why a row and not the sort: `sort: place` and the role `location` do not share a spelling, and a
map from the one vocabulary to the other would be a list in code relating two sets of db words — the
thing `db/0034` moved out of `UD_DEP_TO_ROLE`.*

**TWO — «seldom» IS NOT `negative`** (ruling 2). Its row compiled ¬∃ beside its own `force: few`:
bound, «he seldom sleeps» would have said «he never sleeps». The format has no quantity for «few»,
so the corrected row states NONE — a quantifier over times whose quantity the format does not hold
— and keeps its force, which is what it means. The compiler leaves such a word unplaced and
withholds its clause. *«often» keeps its `existential` beside `force: many`: ∃ is weaker than what
it says and not false of it, and the ruling names «seldom» alone.*

**AND «rarely», «usually» GET ROWS — BECAUSE WITHOUT ONE THEY CLAIM.** Neither is in the closed
classes, so both fell to the manner default: «he rarely sleeps» compiled to sleep(he) in a
«rarely» manner, CLAIMED — a clause the sentence does not entail. A row is what makes the station
see an operator and withhold. They go to the ADVERB KINDS, not here: the closed-class forms filter
D's vocabulary and the Captain ruled new adverbs out of it (2026-09-16, `db/0013`). `circumstantial`,
because req 23 sends a circumstantial adverb to «a box or the quantifier»; compiled as a quantifier
over the time box with no quantity — `seldom`'s corrected shape exactly. The adverb kinds hold no
`features` column, so their force (few · most) is in the note, where the fuzzy proportion of ruling 2
will find it. *Only these two: they are the witnesses the measurement met. «frequently»,
«occasionally», «generally» enter on a witness of their own (the standing law of 2026-09-18).*

**THREE — «ever» IS ∃, AND IT IS A POLARITY ITEM** (ruling 3). Its row compiled `universal` while its
own `force` said `existential`; the force was right. It takes `polarity: negative-context` — `any`'s
own feature and value, since v1 — so the decompiler speaks it only where a negation stands over it.

**FOUR — «once» HAS TWO READINGS** (ruling 4). One time, or formerly («I once lived in Rome»). The row
says so in the table's own vocabulary for a form the tree cannot settle — `kind: ambiguous` with its
candidates, `'d`'s shape — and the station withholds it. «twice» keeps its `count: 2` feature, and
the compiler now builds it onto the binder's `count`, as the drill's `freq-1` has.

**SEVEN — THE «any-» ROWS SAY THEIR POLARITY** (ruling 7). `anyone` · `anybody` · `anything` ·
`anywhere` carried none, so `db/0028` had nothing to key a choice on and wrote: *«the day a zip needs
"anyone" it will be because polarity reached the format»*. It reached the ROWS instead, which is
where it lives — «anybody» is at home under a negation and not in a plain statement. And «anyone»
is `spoken` among the two persons, `db/0028`'s choice of «someone» mirrored. **The voice key gains
the polarity** (`Decompiler._key`): without it «anyone» and «someone» would be one meaning, and two
flags on one key is the silent overwrite `db/0028` paid five sentences to learn.

---

**NOTHING ELSE MOVES**, and the check refuses anything that does: no form arrives in the closed classes
(D's exclusion set is untouched), no row is added or lost there, and every row outside the ones named
above is v22's.

**Written by the 1st Officier on 2026-09-27 — first for the box alone, then, before it was ever
applied, folded with the Captain's rulings of the same day. Nothing is applied until the Captain
says so.**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, AdverbKindDoc, ClosedClassDoc
from tk2.migrations import ensure_collections

CLOSED_VERSION = 23
ADVERB_VERSION = 6

_RULING = ("the Captain, 2026-09-27 (E3.3.11.2.9.1 … E3.3.11.2.9.12, «Agreed on all your leans. "
           "Go»)")

#: The role of a quantifier that IS its own phrase (`db/0028`) — a name of the table's vocabulary.
FUSED = "fused_quantifier"
#: `any`'s own feature and value since v1 — a name, not a roster.
POLARITY, NEGATIVE_CONTEXT = "polarity", "negative-context"

#: form -> the box the variable it binds fills. The thirteen adverbial fused quantifiers, and no
#: other row: a fused PRONOUN takes its box from its relation, as every nominal does.
BINDS_IN = {
    "always": "time",
    "never": "time",
    "ever": "time",
    "sometimes": "time",
    "often": "time",
    "seldom": "time",
    "once": "time",
    "twice": "time",
    "everywhere": "location",
    "somewhere": "location",
    "anywhere": "location",
    "nowhere": "location",
    "somehow": "manner",
}

#: form -> (the meaning it compiles to, why) — the four rows whose MEANING the rulings move.
MEANING = {
    "seldom": ({"kind": "quantifier", "roles": ["time"]},
               "v23 (E3.3.11.2.9.2): NOT `negative` — «seldom» is few, which no quantity of the "
               "format holds; the row states none, and its force says what it means"),
    "ever": ({"kind": "quantifier", "quantity": "existential", "roles": ["time"]},
             "v23 (E3.3.11.2.9.3): ∃, as its own force always said — `universal` was the row "
             "contradicting itself; a polarity item, as «any» is"),
    "once": ({"kind": "ambiguous", "candidates": [
                 {"kind": "quantifier", "quantity": "existential", "roles": ["time"], "count": 1},
                 {"kind": "quantifier", "quantity": "existential", "roles": ["time"],
                  "tense": "past"}]},
             "v23 (E3.3.11.2.9.4): two readings — ONE time, or FORMERLY («I once lived in Rome») — "
             "and nothing in the tree chooses; withheld"),
}

#: form -> the polarity it gains (ruling 3 and ruling 7). Each already carries the meaning; only
#: WHERE it is said is new.
POLAR = ("ever", "anyone", "anybody", "anything", "anywhere")

#: `(role, form)` gaining the `spoken` flag: of the two negative-context persons, the one said.
VOICED = {(FUSED, "anyone"): "the person under a negation — «nobody saw ANYONE»; «anybody» is the "
                             "same meaning, and «someone» is the plain context's (`db/0028`)"}

#: The adverb kinds' two new rows: a quantifier over times whose quantity the format does not hold.
QUANTIFIER_OVER_TIME = {"kind": "quantifier", "roles": ["time"]}
UNHELD = {
    "rarely": "force few — «he rarely sleeps» is not «he sleeps»; the manner default claimed it",
    "usually": "force most — «he usually sleeps» is not «he sleeps»; the manner default claimed it",
}


def _adverbial(row: dict) -> bool:
    """A fused quantifier that is an ADVERB — **the word class decides**, as it did for `db/0028`."""
    return row.get("role") == FUSED and row.get("word_class") == "adverb"


def _note(row: dict, said: str) -> str:
    note = row.get("note") or ""
    return (f"{note} — " if note else "") + said


def build_closed(previous: list[dict]) -> list[dict]:
    out = []
    for row in previous:
        if row.get("version") != CLOSED_VERSION - 1:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = CLOSED_VERSION
        said = []
        if _adverbial(row) and row["form"] in BINDS_IN:
            role = BINDS_IN[row["form"]]
            if row["form"] in MEANING:
                compiled, why = MEANING[row["form"]]
                new["compiled"] = {**compiled}
                said.append(why)
            else:
                new["compiled"] = {**row["compiled"], "roles": [role]}
            said.append(f"v23: its variable fills the {role} box — an adverb has no relation that "
                        f"names one (E3.3.11.2.9, `db/0014`'s repair one role over)")
        if row.get("role") == FUSED and row["form"] in POLAR:
            new["features"] = {**(row.get("features") or {}), POLARITY: NEGATIVE_CONTEXT}
            said.append("v23 (E3.3.11.2.9.7): said only where a negation or a negative binder "
                        "stands over it")
        if (row.get("role"), row["form"]) in VOICED:
            new["spoken"] = True
            said.append(f"v23: {VOICED[(row['role'], row['form'])]}")
        if said:
            new["note"] = _note(row, " · ".join(said) + f" ({_RULING})")
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
    for form, why in UNHELD.items():
        out.append({
            "version": ADVERB_VERSION,
            "form": form,
            "kind": "circumstantial",
            "compiled": dict(QUANTIFIER_OVER_TIME),
            "source": f"E3.3.11.2.9.2 — {_RULING}: proportions withheld",
            "note": f"{why}. A quantifier over the time box with NO quantity — the format holds none "
                    f"for it — so the station leaves it unplaced and withholds the clause",
            "position": position,
            "spoken": False,
        })
        position += 1
    return out


def _previous(number: int, attribute: str):
    # **BY NUMBER**, never through `newest_migration_declaring` — see `db/0041`.
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == number), None)
    if found is None:
        raise RuntimeError(f"{number:04d} is gone — it holds the version this one extends")
    return getattr(found.load(), attribute)


CLOSED_CLASS_ROWS = build_closed(_previous(41, "CLOSED_CLASS_ROWS"))
ADVERB_KIND_ROWS = build_adverbs(_previous(40, "ADVERB_KIND_ROWS"))

#: **UNCHANGED** — meanings, features and flags move on named rows, and no form arrives.
CLOSED_CLASS_FORMS = tuple(
    sorted({row["form"] for row in CLOSED_CLASS_ROWS if " " not in row["form"]})
)


def _meaning(row: dict) -> tuple:
    """A row's VOICE. **THIS IS `Decompiler._key()` AND IT MUST STAY THAT WAY** — see `db/0029`.
    Since v23 it carries the POLARITY a row states, and only where it states one."""
    features = row.get("features") or {}
    key = (row["role"], tuple(sorted((k, str(v)) for k, v in (row.get("compiled") or {}).items())),
           features.get("sort"), features.get("takes_number"))
    return key if features.get(POLARITY) is None else (*key, features[POLARITY])


def _check() -> None:
    from tk2.tkzip.schema import Quantity, Role

    before = [r for r in _previous(41, "CLOSED_CLASS_ROWS") if r.get("version") == CLOSED_VERSION - 1]
    if set(CLOSED_CLASS_FORMS) != {r["form"] for r in before if " " not in r["form"]}:
        raise ValueError("THE EXCLUSION SET MOVED — D's vocabulary filter would change with it")
    if len(CLOSED_CLASS_ROWS) != len(before):
        raise ValueError("a closed-class row was added or lost — this migration adds none")

    # **THE ROWS NAMED ARE EXACTLY THE ONES THE WORD CLASS NAMES** — every adverbial fused
    # quantifier, and no pronoun: the table draws the line, not this file.
    adverbial = sorted(r["form"] for r in before if _adverbial(r))
    if adverbial != sorted(BINDS_IN):
        raise ValueError(f"{sorted(set(adverbial) ^ set(BINDS_IN))}: named here and not an "
                         f"adverbial fused quantifier, or one and not named")

    moved = {"box": [], "meaning": [], "polarity": [], "voice": []}
    for row, was in zip(CLOSED_CLASS_ROWS, before):
        if (row["form"], row.get("role"), row.get("word_class"), row.get("source")) != (
                was["form"], was.get("role"), was.get("word_class"), was.get("source")):
            raise ValueError(f"{was['form']!r}: a form, a role or a class moved")
        form = row["form"]
        if row.get("compiled") != was.get("compiled"):
            if form in MEANING:
                if row["compiled"] != MEANING[form][0]:
                    raise ValueError(f"{form!r}: its meaning is not the one the ruling names")
                moved["meaning"].append(form)
            elif {k: v for k, v in row["compiled"].items() if k != "roles"} != was.get("compiled"):
                # **ONE KEY ARRIVES AND NOTHING ELSE MOVES** on a row whose meaning no ruling names.
                raise ValueError(f"{form!r}: its meaning moved beyond the box it binds")
            else:
                moved["box"].append(form)
            roles = [c.get("roles") for c in row["compiled"].get("candidates", [row["compiled"]])]
            if any(r is None or len(r) != 1 or r[0] not in {x.value for x in Role} for r in roles):
                raise ValueError(f"{form!r}: {roles} is not ONE box of the format")
        if row.get("features") != was.get("features"):
            if {k: v for k, v in row["features"].items() if k != POLARITY} != (was.get("features")
                                                                                 or {}) \
                    or row["features"][POLARITY] != NEGATIVE_CONTEXT:
                raise ValueError(f"{form!r}: a feature moved beyond its polarity")
            moved["polarity"].append(form)
        if bool(row.get("spoken")) != bool(was.get("spoken")):
            moved["voice"].append((row.get("role"), form))
        if row.get("note") != was.get("note") and form not in {
                *BINDS_IN, *POLAR, *(f for _, f in VOICED)}:
            raise ValueError(f"{form!r}: a note moved on a row nothing here names")
    if sorted(moved["box"] + moved["meaning"]) != sorted(BINDS_IN):
        raise ValueError(f"the rows whose meaning moved are {moved}, not the thirteen named")
    if sorted(moved["meaning"]) != sorted(MEANING):
        raise ValueError(f"the meanings moved are {moved['meaning']}, not the rulings' {sorted(MEANING)}")
    if sorted(moved["polarity"]) != sorted(POLAR) or sorted(moved["voice"]) != sorted(VOICED):
        raise ValueError(f"polarity or voice moved on {moved}, not on the rows the rulings name")

    # **WHAT THE RULINGS SAY, CHECKED ON THE ROWS** — not on this file's own constants.
    by_form = {r["form"]: r for r in CLOSED_CLASS_ROWS if r.get("role") == FUSED}
    if by_form["seldom"]["compiled"].get("quantity") is not None:
        raise ValueError("«seldom» still states a quantity — ruling 2 says the format holds none")
    ever = by_form["ever"]
    if ever["compiled"].get("quantity") != Quantity.EXISTENTIAL.value \
            or ever["features"].get("force") != Quantity.EXISTENTIAL.value:
        raise ValueError("«ever» is ∃ by ruling 3, and its row and its force must say so together")
    if by_form["twice"]["features"].get("count") != 2 or by_form["twice"]["compiled"] != {
            **was_compiled(before, "twice"), "roles": ["time"]}:
        raise ValueError("«twice» keeps its count and its meaning; only its box arrives")

    # **ONE SORT, ONE BOX** — two rows of one sort naming two boxes would be a curation error.
    boxes: dict[str, set] = {}
    for row in CLOSED_CLASS_ROWS:
        if _adverbial(row):
            for candidate in row["compiled"].get("candidates", [row["compiled"]]):
                boxes.setdefault(row["features"].get("sort"), set()).update(candidate["roles"])
    split = {sort: sorted(named) for sort, named in boxes.items() if len(named) > 1}
    if split:
        raise ValueError(f"one sort names several boxes: {split}")

    # **THE TABLE'S LAW, RE-RUN IN FULL** (`db/0015`) — one voice per meaning, on the key the
    # decompiler asks with, polarity included; and a voice is a choice between two forms or more.
    voices: dict[tuple, str] = {}
    carriers: dict[tuple, int] = {}
    for row in CLOSED_CLASS_ROWS:
        carriers[_meaning(row)] = carriers.get(_meaning(row), 0) + 1
        if not row.get("spoken"):
            continue
        if _meaning(row) in voices:
            raise ValueError(f"{row['form']!r} and {voices[_meaning(row)]!r} both speak one meaning")
        voices[_meaning(row)] = row["form"]
    for role, form in VOICED:
        row = next(r for r in CLOSED_CLASS_ROWS if (r.get("role"), r["form"]) == (role, form))
        if carriers[_meaning(row)] < 2:
            raise ValueError(f"{form!r} is the only form with its meaning — it needs no flag")

    # **THE ADVERB KINDS: TWO ROWS ARRIVE AND NONE MOVES**, and the second roster's laws hold.
    earlier = [r for r in _previous(40, "ADVERB_KIND_ROWS")
               if r.get("version") == ADVERB_VERSION - 1]
    if len(ADVERB_KIND_ROWS) != len(earlier) + len(UNHELD):
        raise ValueError(f"the adverb kinds gain exactly {sorted(UNHELD)}")
    if any({k: v for k, v in row.items() if k != "version"} !=
           {k: v for k, v in was.items() if k not in ("version", "_id")}
           for row, was in zip(ADVERB_KIND_ROWS, earlier)):
        raise ValueError("an existing adverb row moved — this migration only adds there")
    added = ADVERB_KIND_ROWS[len(earlier):]
    if {r["form"] for r in added} != set(UNHELD) or any(
            r["compiled"] != QUANTIFIER_OVER_TIME or r["spoken"] for r in added):
        raise ValueError("the adverb rows added are not the two proportions, unheld and mute")
    clash = sorted({r["form"] for r in ADVERB_KIND_ROWS} & {r["form"] for r in CLOSED_CLASS_ROWS})
    if clash:
        raise ValueError(f"{clash} are in BOTH rosters and a reader could not tell which answers")
    if len({r["position"] for r in ADVERB_KIND_ROWS}) != len(ADVERB_KIND_ROWS):
        raise ValueError("two adverb rows share a position")


def was_compiled(rows: list[dict], form: str) -> dict:
    return next(r["compiled"] for r in rows if r["form"] == form and r.get("role") == FUSED)


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(ClosedClassDoc, CLOSED_CLASS_ROWS)
    writer.insert_many(AdverbKindDoc, ADVERB_KIND_ROWS)
