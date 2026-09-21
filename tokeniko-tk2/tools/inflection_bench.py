"""THE INFLECTION BENCH — how wrong is the spelling rule, and on which words?

    PYTHONPATH=. ../.venv/bin/python tools/inflection_bench.py [--tag VBD] [--show]

**AN OFFLINE INSTRUMENT, LIKE WORDNET IS FOR THE BASE.** `lemminflect` executes a spaCy hook on
import, so importing it loads spacy and torch — deliberately NOT on the closed dependency list,
because the provider lives behind the skeleton adapter. It is therefore run HERE, by hand, and its
answers are curated into a migration; nothing at runtime ever imports it. *(The Captain's ruling,
2026-09-19, after `db/0022`.)*

**AND IT IS NOT TRUSTED ALONE.** `db/0022` measured 22 of its 43 answers to be defects of its own —
«ghost-writes», «over shoots», «torpedo → torpedo». So this bench reads a SECOND resource,
**WordNet's own `verb.exc`**, Princeton's hand-curated list of irregular verb forms, and reports
three states rather than two:

    AGREED      the two resources give the same irregular form  -> a roster row, safe
    DISPUTED    they disagree                                   -> the QM looks at it by hand
    LONE        only lemminflect says so                        -> suspect, and usually its defect

That is `db/0019`'s doctrine applied to a second resource: *where the resources are of two minds, we
do not decide silently.*
"""

import argparse
import sys
import zipfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tk2.language.inflect import (  # noqa: E402
    PARTICIPLE, PAST, PLURAL, PRESENT, participle_rule, past_tense_rule, plural_rule,
    present_tense_rule,
)

RULES = {PRESENT: present_tense_rule, PAST: past_tense_rule, PARTICIPLE: participle_rule,
         PLURAL: plural_rule}
#: Which part of speech each tag inflects, which decides both resources it is measured against.
PART = {PRESENT: "v", PAST: "v", PARTICIPLE: "v", PLURAL: "n"}


def wordnet_exceptions(part: str = "v") -> dict[str, set[str]]:
    """`lemma -> every irregular form Princeton records for it`. Read straight from the corpus zip.

    The file maps INFLECTED -> LEMMA and says nothing about which tag each form carries; that is
    what the second resource is for. What it gives is the one thing that matters here: whether a
    proposed irregular form is a form of English at all.
    """
    import nltk

    found: dict[str, set[str]] = {}
    with zipfile.ZipFile(str(nltk.data.find("corpora/wordnet.zip"))) as archive:
        name = {"v": "verb", "n": "noun"}[part]
        for line in archive.read(f"wordnet/{name}.exc").decode().splitlines():
            parts = line.split()
            if len(parts) < 2:
                continue
            for lemma in parts[1:]:
                found.setdefault(lemma, set()).add(parts[0])
    return found


def lemmas(part: str = "v") -> list[str]:
    from nltk.corpus import wordnet as wn

    return sorted({lemma.name().lower().replace("_", " ")
                   for synset in wn.all_synsets(part) for lemma in synset.lemmas()})


def run(argv=None) -> int:
    parser = argparse.ArgumentParser(description="the spelling rule against two resources")
    parser.add_argument("--tag", default=None, choices=sorted(RULES), help="one tag, not all three")
    parser.add_argument("--show", action="store_true", help="print every disagreement, not a sample")
    args = parser.parse_args(argv)

    from lemminflect import getInflection

    print("=" * 96)
    print("THE INFLECTION BENCH — the rule, lemminflect, and WordNet's own exception list")
    print("=" * 96)

    for tag in ([args.tag] if args.tag else [PRESENT, PAST, PARTICIPLE, PLURAL]):
        rule = RULES[tag]
        # **THE RESOURCES ARE PER PART OF SPEECH**, both of them: WordNet keeps `verb.exc` and
        # `noun.exc` apart, and a plural is asked of `NNS` and a past of `VBD`.
        exceptions = wordnet_exceptions(PART[tag])
        words = [word for word in lemmas(PART[tag]) if " " not in word and "-" not in word]
        print(f"\n  lemmas            {len(words)} single-word {PART[tag]} lemmas in WordNet")
        print(f"  exception list    {len(exceptions)} with an irregular form recorded")
        states = Counter()
        rows, disputed, lone = [], [], []
        for word in words:
            says = getInflection(word, tag=tag)
            said = says[0].lower() if says else ""
            expected = rule(word)
            if not said or said == expected:
                states["the rule is right"] += 1
                continue
            known = {form.lower() for form in exceptions.get(word, ())}
            # WordNet records every irregular form of a verb together and does not say which tag
            # each carries. The PRESENT participle is the one that can be told apart by its spelling,
            # and it is the one tag we are never asking about, so it is removed before comparing.
            candidates = {form for form in known if not form.endswith("ing")}
            if said in candidates:
                states["AGREED — a roster row"] += 1
                rows.append((word, said, expected))
            elif said == word and known and not candidates:
                # **THE ZERO-CHANGE VERBS** — «hit», «put», «cost». WordNet lists only forms that
                # DIFFER from the lemma, so a verb whose past IS its lemma appears there with its
                # `-ing` form alone. That absence is the evidence, and it is evidence rather than
                # silence because the `-ing` form proves the verb was looked at.
                states["AGREED — unchanging, and WordNet's silence is the witness"] += 1
                rows.append((word, said, expected))
            elif said == word + word[-1:] + expected[len(word):]:
                # **THE ONE FACT THE RULE DECLARED OUT OF REACH.** `-ed` after a doubled consonant
                # is the rule's own spelling; what the rule cannot see is the STRESS that decides
                # whether a polysyllable takes it («backlog» does, «visit» does not). So where the
                # instrument's answer differs from the rule by exactly that doubling, it is supplying
                # the missing fact and nothing else — which is a narrower thing to trust than its
                # word choice, and it is the only place it is trusted alone.
                states["AGREED — the instrument supplies the stress the rule cannot see"] += 1
                rows.append((word, said, expected))
            elif candidates:
                states["DISPUTED"] += 1
                disputed.append((word, said, expected, sorted(candidates)))
            else:
                states["LONE — lemminflect only"] += 1
                lone.append((word, said, expected))

        print(f"  --- {tag} " + "-" * (88 - len(tag)))
        for state, count in states.most_common():
            print(f"      {count:6}  {state}")
        for label, found in (("DISPUTED", disputed), ("LONE", lone)):
            if not found:
                continue
            print(f"\n      {label}:")
            for entry in (found if args.show else found[:25]):
                word, said, expected = entry[0], entry[1], entry[2]
                known = f"   wordnet knows {entry[3]}" if len(entry) > 3 else ""
                print(f"        {word:22} lemminflect «{said}»  rule «{expected}»{known}")
            if not args.show and len(found) > 25:
                print(f"        … and {len(found) - 25} more (--show)")
        print(f"\n      ROSTER WOULD BE {len(rows)} rows\n")
        if args.show and rows:
            print("      AGREED rows:")
            for word, said, expected in rows:
                print(f"        ({word!r}, {said!r}, {expected!r}),")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
