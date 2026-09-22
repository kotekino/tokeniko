"""THE DOMAIN BENCH — what evidence says «in Italy» FRAMES a claim rather than locating an event?

    PYTHONPATH=. ../.venv/bin/python tools/domain_bench.py

**THE BENCH BEFORE THE ANSWER** (the Captain's PRIO 1: *«establish the criteria and the test bench
BEFORE proposing an answer — enumerate the cases a mechanism must handle, then measure candidates
against them; never pick the tidy one and defend it»*).

**THE STATION HAS NEVER BUILT A `DomainRow`.** The schema has held the fifth prefix element since
E2 — *«the context a claim holds in: legally · in chess · as a doctor · in Italy»* — the decompiler
can already say one, the drill hand-compiles three, and rules reqs 6–7 depend on it («as a doctor I
disagree; as a father I understand» must be two positions honestly held, not a KB contradiction).
The compiler has never raised one. `grep DomainRow tk2/language/` is empty.

**THE OBVIOUS RULE IS WRONG, WHICH IS WHY THIS EXISTS.** «A marked nominal before the subject is a
domain» fits all three drill cases and also swallows «In the morning, I go to work» (a TIME) and
«With a knife, he cut the bread» (an INSTRUMENT). Fronting is necessary and nowhere near sufficient.

**AND ONE PAIR MAY BE IRREDUCIBLE** — the question this bench exists to answer honestly:

    « Legally, in Italy, he is still married. »   in Italy  -> DOMAIN
    « In France, I ate well. »                    in France -> LOCATION

Same relation, same marker, same fronting, same comma. If nothing in the parse separates them, then
the station must ABSTAIN there rather than guess — which is the placement floor's answer
(`docs/dictionary/202609191500_the-placement-floor.md`) and the confidence bench's, and it is a
result, not a failure.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tk2.language.skeleton import StanzaSkeletons  # noqa: E402

#: `(sentence, {head word -> what it IS})`. A word absent from the map is not under test.
#: The three `drill` cases are hand-compiled in `tests/fixtures/drill.py` and are the ground truth
#: the Captain approved; the rest are the negatives a rule must not swallow.
CASES = [
    ("In Italy, you may drive in France with a foreign licence.",
     {"Italy": "domain", "France": "location"}, "drill aw-15"),
    ("As a doctor I disagree.", {"doctor": "domain"}, "drill aw-16"),
    ("As a father I understand.", {"father": "domain"}, "drill aw-16"),
    ("Legally, in Italy, he is still married.",
     {"Legally": "domain", "Italy": "domain"}, "drill aw-17"),
    ("In chess, the king moves one square.", {"chess": "domain"}, "the schema's own example"),
    ("In the morning, I go to work.", {"morning": "time"}, "fronted, and NOT a domain"),
    ("With a knife, he cut the bread.", {"knife": "instrument"}, "fronted, and NOT a domain"),
    ("At home, I relax.", {"home": "location"}, "fronted, and NOT a domain"),
    ("Yesterday, I slept badly.", {"Yesterday": "time"}, "UD marks this one `obl:tmod` itself"),
    ("In France, I ate well.", {"France": "location"}, "THE HARD ONE — aw-17's twin"),
]


_STATION = None


def _contested(sentence, word):
    """Did another phrase in this clause want the SAME BOX as this one?

    **ASKED OF THE COMPILER, NOT GUESSED FROM THE RELATION.** Comparing UD deps calls «In the
    morning, I go TO WORK» a clash — two `obl`s — and it is not: the morning is a TIME and the work
    a DESTINATION, which the compiler already works out by running the marker selector over the
    supersense. So the honest question is what it DID:

        « In the morning, I go to work. »   time · destination      unplaced []
        « In Italy, … in France … »         location: italy         unplaced ['France']

    A box taken and a sibling left over is a contest. A clean placement is not.
    """
    global _STATION
    if _STATION is None:
        from tk2.language import standing_closed_classes
        from tk2.language.compile import Compiler

        _STATION = (Compiler(standing_closed_classes()), StanzaSkeletons())
    compiler, provider = _STATION

    from tk2.language.utterance import compile_utterance
    from tools.drill_gate import DRILL_CONTEXT

    zip_ = compile_utterance(compiler, provider(sentence), DRILL_CONTEXT).zip
    return bool(zip_.unplaced)


def facts(skeleton, word, sentence):
    """Everything a rule may look at. Nothing here reads a dictionary directly: that would be a
    different bench, and the point of this one is what the PARSE plus the station's own placement
    can say."""
    subject = next((w.index for w in skeleton.words
                    if w.bare_dep in ("nsubj", "csubj", "expl")), None)
    marker = next((w.text.lower() for w in skeleton.words
                   if w.bare_dep == "case" and w.head == word.index), None)
    comma_after = any(w.text == "," and w.index == word.index + 1 for w in skeleton.words)
    return {
        "fronted": subject is not None and word.index < subject,
        "marker": marker,
        "dep": word.bare_dep,
        "role_also_filled": _contested(sentence, word),
        "comma_after": comma_after,
        "is_adverb": word.upos == "ADV",
    }


#: The candidates. Each takes the facts and answers «is this a domain?». They are deliberately
#: crude: a rule that needs the dictionary is not a rule this bench can score.
CANDIDATES = {
    "fronted alone": lambda f: f["fronted"],
    "fronted + comma": lambda f: f["fronted"] and f["comma_after"],
    "marker is `as`": lambda f: f["marker"] == "as",
    "fronted + role already filled": lambda f: f["fronted"] and f["role_also_filled"],
    "fronted ADVERB": lambda f: f["fronted"] and f["is_adverb"],
    "`as` OR fronted-adverb":
        lambda f: f["marker"] == "as" or (f["fronted"] and f["is_adverb"]),
    "`as` OR fronted-adverb OR fronted-with-its-box-contested":
        lambda f: f["marker"] == "as" or (f["fronted"] and (f["is_adverb"]
                                                            or f["role_also_filled"])),
}


def run() -> int:
    provider = StanzaSkeletons()
    rows = []
    for sentence, expected, note in CASES:
        skeleton = provider(sentence)[0]
        for word in skeleton.words:
            if word.text not in expected:
                continue
            rows.append((sentence, word.text, expected[word.text] == "domain",
                         expected[word.text], facts(skeleton, word, sentence), note))

    print("=" * 100)
    print("THE DOMAIN BENCH — what the PARSE alone can say about «in Italy» vs «in France»")
    print("=" * 100)
    print(f"  {len(rows)} phrases under test · "
          f"{sum(1 for r in rows if r[2])} domains · {sum(1 for r in rows if not r[2])} not\n")

    print(f"  {'phrase':<12} {'truth':<11} {'fronted':<8} {'marker':<8} {'dep':<10} "
          f"{'role2':<6} {'comma':<6} {'adv':<5}")
    print(f"  {'-' * 12} {'-' * 11} {'-' * 8} {'-' * 8} {'-' * 10} {'-' * 6} {'-' * 6} {'-' * 5}")
    for _, text, _, truth, f, _ in rows:
        print(f"  {text:<12} {truth:<11} {str(f['fronted']):<8} {str(f['marker']):<8} "
              f"{f['dep']:<10} {str(f['role_also_filled']):<6} {str(f['comma_after']):<6} "
              f"{str(f['is_adverb']):<5}")

    print("\n" + "=" * 100)
    print("  THE CANDIDATES — a rule is only worth having if it is right in BOTH directions")
    print("=" * 100)
    print(f"  {'rule':<40} {'caught':>8} {'missed':>8} {'FALSE+':>8}   verdict")
    print(f"  {'-' * 40} {'-' * 8} {'-' * 8} {'-' * 8}   {'-' * 24}")
    for name, rule in CANDIDATES.items():
        caught = sum(1 for _, _, is_domain, _, f, _ in rows if is_domain and rule(f))
        missed = sum(1 for _, _, is_domain, _, f, _ in rows if is_domain and not rule(f))
        wrong = sum(1 for _, _, is_domain, _, f, _ in rows if not is_domain and rule(f))
        verdict = ("CLEAN" if not missed and not wrong
                   else f"{wrong} false positive{'s' if wrong != 1 else ''}"
                        + (f", {missed} missed" if missed else ""))
        print(f"  {name:<40} {caught:>8} {missed:>8} {wrong:>8}   {verdict}")

    print("\n  **A FALSE POSITIVE IS THE SIN** (req 8): a domain the speaker did not state indexes a")
    print("  claim to a context it was never held in, and the evaluator would never contradict it.")
    print("  A MISS only leaves the station where it already is.\n")

    hard = [r for r in rows if r[5] == "THE HARD ONE — aw-17's twin"]
    twin = [r for r in rows if "Legally" in r[0] and r[1] == "Italy"]
    if hard and twin:
        print("=" * 100)
        print("  THE PAIR THAT DECIDES WHETHER A RULE CAN EXIST AT ALL")
        print("=" * 100)
        for _, text, _, truth, f, _ in twin + hard:
            print(f"  «{text}» is a {truth:<9} {f}")
        if twin[0][4] == hard[0][4]:
            print("\n  **IDENTICAL ON EVERY FACT THE PARSE GIVES.** No rule over these features can")
            print("  separate them, and one of them is a domain. The station must ABSTAIN on a bare")
            print("  fronted locative — which is a RESULT, not a gap to be filled with a guess.")
        else:
            print("\n  They differ — and the difference is what a rule would have to read.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
