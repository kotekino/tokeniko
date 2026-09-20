"""0025 — subject roles v3: **two verbs the supersense reads wrong** (parser-compiler req 19).

**THEY WERE ALWAYS WRONG AND NOTHING COULD SEE THEM.** «He looked up» and «He almost died» both have
a pronoun subject, and until 2026-09-20 an unresolvable third-person pronoun compiled to OPEN — so
the drill gate, which abstains on an OPEN filler, had nothing to compare and reported no conflict.
The moment the station started keeping the word (`he.n`, which is what the drill writes), both
disagreements appeared. *A defect that only an abstention was hiding is still a defect, and this is
the second time the instruments have found more than the arguments did.*

**WHAT THE SUPERSENSE GETS WRONG, AND WHY IT IS NOT THE SUPERSENSE'S FAULT:**

    look   `verb.perception` -> experiencer,  and the drill says AGENT
    die    no rule at all    -> agent,        and the drill says PATIENT

WordNet's supersense says what a verb is ABOUT, and the subject's role turns on something else:
whether the subject DOES the thing or has it happen to them. *Looking* and *seeing* are both
perception and only one of them is volitional; *dying* is something a body does and nothing anybody
performs. **Volitionality is not in the resource** — there is no column for it in WordNet and no
reliable way to derive it — so the honest form is a lemma rule, which is what `db/0019` already
established for `disagree` and for the adjective `happy`.

**ONE ROW MOVES**, the `verb` predicate's selector, and it gains two lemma rules ahead of the
supersense ones. The order is the point: a lemma rule that came after `verb.perception` would never
be reached for `look`.

*Written by the QM on 2026-09-20. The two readings are the drill's own, not the QM's.*
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, SubjectRoleDoc
from tk2.migrations import ensure_collections

VERSION = 3

#: `lemma -> the role its subject takes`, ahead of every supersense rule. Each one is a verb whose
#: supersense is right about the SUBJECT MATTER and wrong about who is doing it.
RULED_VERBS = {
    "look": "agent",      # volitional perception; «see» is the involuntary one and keeps the rule
    "die": "patient",     # nobody performs dying — `verb.body` says what it is about, not who acts
}


def build_rows(previous: list[dict]) -> list[dict]:
    out = []
    for row in previous:
        if row.get("version") != 2:
            continue
        new = dict(row)
        new.pop("_id", None)
        new["version"] = VERSION
        if row["predicate"] == "verb":
            compiled = {**(row.get("compiled") or {})}
            selector = list(compiled.get("selector") or ())
            # After the lemma rules that are already there, and BEFORE every supersense rule —
            # `look` is `verb.perception` and would never be reached otherwise.
            at = sum(1 for rule in selector if rule.get("reads") == "lemma")
            fresh = [{"reads": "lemma", "is": [lemma], "then": role}
                     for lemma, role in sorted(RULED_VERBS.items())]
            compiled["selector"] = [*selector[:at], *fresh, *selector[at:]]
            new["compiled"] = compiled
        out.append(new)
    return out


def _previous_rows():
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 19), None)
    if found is None:
        raise RuntimeError("0019 is gone — it holds the version this one extends")
    return found.load().SUBJECT_ROLE_ROWS


SUBJECT_ROLE_ROWS = build_rows(_previous_rows())


def _check() -> None:
    before = _previous_rows()
    if len(before) != len(SUBJECT_ROLE_ROWS):
        raise ValueError("a row was added or lost — this migration edits one selector")

    verb = next(r for r in SUBJECT_ROLE_ROWS if r["predicate"] == "verb")
    selector = verb["compiled"]["selector"]
    lemma_rules = [rule for rule in selector if rule.get("reads") == "lemma"]
    ruled = {lemma: rule["then"] for rule in lemma_rules for lemma in rule["is"]}
    for lemma, role in RULED_VERBS.items():
        if ruled.get(lemma) != role:
            raise ValueError(f"{lemma!r} should be {role!r} and the selector says {ruled.get(lemma)!r}")

    # **THE ORDER IS THE RULE.** A lemma rule that sits behind a supersense rule is a rule that never
    # fires, and `look` is `verb.perception` — so this is not a tidiness check.
    first_supersense = next((at for at, rule in enumerate(selector)
                             if rule.get("reads") == "verb"), len(selector))
    if any(at > first_supersense for at, rule in enumerate(selector)
           if rule.get("reads") == "lemma"):
        raise ValueError("a lemma rule sits behind a supersense rule and would never be reached")
    if selector[-1]["reads"] != "default":
        raise ValueError("the selector must still end in a default, or a verb can reach no role")

    copular = next(r for r in SUBJECT_ROLE_ROWS if r["predicate"] == "copular")
    if copular["compiled"] != next(r for r in before if r["predicate"] == "copular")["compiled"]:
        raise ValueError("the copular rule moved — this migration is about verbs")


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(SubjectRoleDoc, SUBJECT_ROLE_ROWS)
