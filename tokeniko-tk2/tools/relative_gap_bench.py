"""THE ZERO RELATIVE'S GAP — which knowledge, if any, tells the antecedent's role inside the clause.

    PYTHONPATH=. ../.venv/bin/python tools/relative_gap_bench.py [--cases] [--json PATH]

**THE QUESTION** *(G5, STOPPED; the Captain approved the bench 2026-09-25)*. «the fish the cat ate»
and «the day I slept» are the same stanza tree — `acl:relcl`, `nsubj`, no `obj`, no pronoun — and the
antecedent is the OBJECT in one and an ADVERBIAL in the other. Basic UD carries no gap and the
enhanced graph that would is not produced, so today the station WITHHOLDS the clause. This bench
measures the candidate knowledge against hand-labelled evidence; it proposes nothing.

**THE CASES ARE EVIDENCE** (the third kingdom): each carries its gold and the reason for it, in the
English, because a tag without its reason cannot be argued with. Offline except for stanza; no db.

**WHAT IS SCORED.** Only the cases stanza actually parses into the withheld shape — a zero relative,
subject said, no object, no stranded marker. The others are listed, not scored: the station never
reaches the question for them. Every candidate answers `object`, an adverbial role (`time`,
`place`, `manner`, `reason`), `adverbial` (an adverbial of a kind it cannot name) or None (abstain).
Two scores, never averaged:

- **binary** — object against any adverbial. This is the one req 8 bites on: `sleep(patient=day)`
  is a wrong complete zip.
- **role** — the exact role. An untold `adverbial` is an abstention here, never a right answer.

**THE CANDIDATES, STATED BEFORE MEASURING** (the combinations were fixed before the first run, and
not tuned after it):

- **a — WordNet's verb frames**, read on the Lemma (lemma-specific frames included, which the
  synset's own `frame_ids` omit). A frame is an OBJECT frame when the token after the verb slot in
  its published string is `something`/`somebody` — derived from the resource's strings, not listed.
  The PRIMARY sense is `wn.synsets(lemma, 'v')[0]`, WordNet's own sense order, `db/0006`'s rule.
    a1 primary-permissive  primary sense has an object frame → object, else adverbial
    a2 primary-strict      primary: object frames only → object; none → adverbial; both → abstain
    a3 any-permissive      any sense has an object frame → object, else adverbial
    a4 any-strict          no sense has an object frame → adverbial; no sense lacks one → object;
                           else abstain
- **b — the antecedent's supersense**, through the station's own `supersense_for` (primary sense;
  it does NOT abstain when WordNet is of two minds — it takes the first reading). The map, stated
  in advance, is only the classes WordNet names for circumstances: `noun.time` → time,
  `noun.location` → place, `noun.motive` → reason. There is no manner class.
    b1 strict              one of the three → that role; else abstain
    b2 full                one of the three → that role; else object
- **c — combinations**, each a with b's role naming the adverbial:
    c1 agreement           a1 object ∧ b silent → object; a1 adverbial ∧ b speaks → b's role;
                           else abstain
    c2 a decides, b overrides where a allows intransitive
                           b speaks ∧ primary has a non-object frame → b's role;
                           elif a1 object → object; else b's role or `adverbial`
    c3 a4 decides where decisive, b where a4 is of two minds
                           a4 object → object; a4 adverbial → b's role or `adverbial`;
                           a4 abstains → b1
- **d — stanza beyond the basic tree**
    d1 the antecedent's own matrix dep carries `tmod` → time; else abstain
    d2 the constituency tree: does the relative SBAR carry a WH node or an empty element? (a gap
       marker, if the model were trained with traces) — reported, not a rule

Baselines, for scale: **N** «no object ⇒ object gap» (the rule G5 refused) and **W** withhold (G5).

**AFTER THE RULING** *(the Captain, 2026-09-25 — c1, plus the passive, plus `time`/`way` rows)*:

- **S — the station as built**, end to end: the sentence compiled by the real `Compiler`, and the
  box of the relative's row that holds the antecedent's variable read back (`patient` → object,
  `location` → place). Withheld is an abstention.
- **H — the held-out group**, the ruling's cost clause: fresh zero relatives written after
  `db/0038` existed, scored APART and never pooled with the 107.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nltk.corpus import wordnet as wn  # noqa: E402

from tk2.dictionary.frames import (  # noqa: E402
    canonical_frames, object_frames, verb_senses,
)
from tk2.dictionary.supersense import supersense_for  # noqa: E402
from tk2.language.skeleton import StanzaSkeletons  # noqa: E402

ADVERBIAL = ("time", "place", "manner", "reason", "other")


@dataclass(frozen=True)
class Case:
    key: str
    group: str
    text: str
    antecedent: str   # the surface form of the antecedent, to find the relcl stanza hangs off it
    gold: str         # object | time | place | manner | reason | other
    why: str


# Groups: T transitive verb, object gap · I intransitive verb, adverbial gap · P ambitransitive
# pairs (same verb, both readings) · N a time/place/reason/manner NOUN as the object · M minimal
# pairs with the antecedent as the matrix object (d1) · S stranded
# marker controls (the station already handles these) · E the gap in an embedded clause, and measures.
CASES = (
    # --- T: transitive, object gap -------------------------------------------------------------
    Case("t01", "T", "The man she married is kind.", "man", "object",
         "she married the man"),
    Case("t02", "T", "I lost the key you found.", "key", "object", "you found the key"),
    Case("t03", "T", "The car he bought is red.", "car", "object", "he bought the car"),
    Case("t04", "T", "I have the tools you need.", "tools", "object", "you need the tools"),
    Case("t05", "T", "The people I trust are few.", "people", "object", "I trust the people"),
    Case("t06", "T", "The city they destroyed was old.", "city", "object",
         "they destroyed the city — a location noun, but the thing destroyed"),
    Case("t07", "T", "I met the woman you hired.", "woman", "object", "you hired the woman"),
    Case("t08", "T", "The house we built is small.", "house", "object", "we built the house"),
    Case("t09", "T", "The letter she sent arrived.", "letter", "object", "she sent the letter"),
    Case("t10", "T", "The dog I own is lazy.", "dog", "object", "I own the dog"),
    Case("t11", "T", "I fixed the chair he broke.", "chair", "object", "he broke the chair"),
    Case("t12", "T", "The film we watched was long.", "film", "object", "we watched the film"),
    Case("t13", "T", "I kept the gift you brought.", "gift", "object", "you brought the gift"),
    Case("t14", "T", "The words he used were rude.", "words", "object", "he used the words"),
    Case("t15", "T", "The friend I visited was ill.", "friend", "object", "I visited the friend"),
    Case("t16", "T", "The cake she made was sweet.", "cake", "object", "she made the cake"),
    Case("t17", "T", "The fish the cat ate was red.", "fish", "object",
         "the cat ate the fish — G5's own sentence"),
    Case("t18", "T", "I trust the minds you trust.", "minds", "object",
         "you trust the minds — the doc's «minds you trust»"),

    # --- I: intransitive, adverbial gap -------------------------------------------------------
    Case("i01", "I", "I remember the day I slept.", "day", "time",
         "I slept on that day; nothing is slept — G5's own sentence"),
    Case("i02", "I", "That was the night she died.", "night", "time", "she died on that night"),
    Case("i03", "I", "I recall the year we arrived.", "year", "time", "we arrived in that year"),
    Case("i04", "I", "The moment he fell was awful.", "moment", "time",
         "he fell at that moment"),
    Case("i05", "I", "The day she was born was sunny.", "day", "time",
         "she was born on that day; a PASSIVE of a transitive (bear), its object already the subject"),
    Case("i06", "I", "The week we stayed was cold.", "week", "time", "we stayed that week"),
    Case("i07", "I", "I miss the summer we swam.", "summer", "time", "we swam that summer"),
    Case("i08", "I", "The place I was born is far.", "place", "place",
         "I was born in that place; passive of bear again"),
    Case("i09", "I", "This is the place we sleep.", "place", "place",
         "we sleep in that place (colloquial zero relative with «place»)"),
    Case("i10", "I", "The spot we sat was shady.", "spot", "place",
         "we sat in that spot — marginal English, the stranded «in» usually said"),
    Case("i11", "I", "I like the way she laughs.", "way", "manner", "she laughs in that way"),
    Case("i12", "I", "The way he walks is odd.", "way", "manner", "he walks in that way"),
    Case("i13", "I", "The reason he left is clear.", "reason", "reason",
         "he left for that reason; «leave» is transitive in other uses, nothing is left here"),
    Case("i14", "I", "Nobody knows the reason she cried.", "reason", "reason",
         "she cried for that reason"),
    Case("i15", "I", "I remember the time we laughed.", "time", "time",
         "we laughed at that time"),
    Case("i16", "I", "The hour he woke was early.", "hour", "time", "he woke at that hour"),
    Case("i17", "I", "That was the year it snowed.", "year", "time",
         "it snowed that year; expletive subject"),
    Case("i18", "I", "The minute she arrived, we left.", "minute", "time",
         "she arrived at that minute; the whole NP is itself a matrix temporal"),
    Case("i19", "I", "I know the place he lives.", "place", "place",
         "he lives in that place; «live» has a transitive sense (live a life), not this one"),
    Case("i20", "I", "Spring is the season the river floods.", "season", "time",
         "the river floods in that season; «flood» is also transitive (flood the town)"),
    Case("i21", "I", "The night the baby cried was long.", "night", "time",
         "the baby cried that night"),

    # --- P: ambitransitive, same verb both ways -----------------------------------------------
    Case("p01", "P", "I love the song you sang.", "song", "object", "you sang the song"),
    Case("p02", "P", "I remember the night you sang.", "night", "time", "you sang that night"),
    Case("p03", "P", "The meal we ate was cold.", "meal", "object", "we ate the meal"),
    Case("p04", "P", "I miss the time we ate together.", "time", "time",
         "we ate together at that time; nothing named was eaten"),
    Case("p05", "P", "I liked the story you read.", "story", "object", "you read the story"),
    Case("p06", "P", "I miss the evenings we read.", "evenings", "time",
         "we read in those evenings"),
    Case("p07", "P", "The song she played was loud.", "song", "object", "she played the song"),
    Case("p08", "P", "The night she played was magic.", "night", "time",
         "she played (performed) that night"),
    Case("p09", "P", "The race he ran was hard.", "race", "object",
         "he ran the race — a cognate object"),
    Case("p10", "P", "The way he ran was funny.", "way", "manner", "he ran in that way"),
    Case("p11", "P", "The letters I wrote are lost.", "letters", "object", "I wrote the letters"),
    Case("p12", "P", "The year I wrote was productive.", "year", "time",
         "I wrote (as an activity) that year"),
    Case("p13", "P", "The water we drank was cold.", "water", "object", "we drank the water"),
    Case("p14", "P", "The night we drank was wild.", "night", "time", "we drank that night"),
    Case("p15", "P", "The games we won were easy.", "games", "object", "we won the games"),
    Case("p16", "P", "The day we won was glorious.", "day", "time", "we won on that day"),
    Case("p17", "P", "The soup she cooked was hot.", "soup", "object", "she cooked the soup"),
    Case("p18", "P", "The way she cooks is simple.", "way", "manner", "she cooks in that way"),
    Case("p19", "P", "The tree he climbed is tall.", "tree", "object", "he climbed the tree"),
    Case("p20", "P", "The day he climbed was windy.", "day", "time", "he climbed on that day"),
    Case("p21", "P", "The class she taught was big.", "class", "object", "she taught the class"),
    Case("p22", "P", "The years she taught were happy.", "years", "time",
         "she taught during those years"),
    Case("p23", "P", "The house we left was empty.", "house", "object", "we left the house"),
    Case("p24", "P", "The day we left was rainy.", "day", "time", "we left on that day"),
    Case("p25", "P", "The questions I asked were simple.", "questions", "object",
         "I asked the questions"),
    Case("p26", "P", "The reason I asked is simple.", "reason", "reason",
         "I asked for that reason"),
    Case("p27", "P", "The song you sing is sad.", "song", "object", "you sing the song"),
    Case("p28", "P", "The way you sing is sad.", "way", "manner", "you sing in that way"),

    # --- N: a time/place/reason/manner noun as the OBJECT -------------------------------------
    Case("n01", "N", "The day I remember most is Sunday.", "day", "object",
         "I remember the day — the day is what is remembered"),
    Case("n02", "N", "The place I love is Kyoto.", "place", "object", "I love the place"),
    Case("n03", "N", "The moment I chose was wrong.", "moment", "object", "I chose the moment"),
    Case("n04", "N", "The time I have is short.", "time", "object", "I have the time"),
    Case("n05", "N", "The place I found was quiet.", "place", "object", "I found the place"),
    Case("n06", "N", "The year I spent in Rome was fun.", "year", "object",
         "I spent the year in Rome"),
    Case("n07", "N", "The week I planned was busy.", "week", "object", "I planned the week"),
    Case("n08", "N", "The morning I enjoyed was calm.", "morning", "object",
         "I enjoyed the morning"),
    Case("n09", "N", "The date we set is Monday.", "date", "object", "we set the date"),
    Case("n10", "N", "The city I visited was Paris.", "city", "object", "I visited the city"),
    Case("n11", "N", "The hour I wasted was long.", "hour", "object", "I wasted the hour"),
    Case("n12", "N", "The night I describe was cold.", "night", "object",
         "I describe the night"),
    Case("n13", "N", "The way I chose was hard.", "way", "object",
         "I chose the way (the path) — the manner noun as the thing chosen"),
    Case("n14", "N", "The reason I gave was false.", "reason", "object", "I gave the reason"),
    Case("n15", "N", "The country I love is Italy.", "country", "object", "I love the country"),
    Case("n16", "N", "The day I missed was Friday.", "day", "object", "I missed the day"),
    Case("n17", "N", "The places we saw were beautiful.", "places", "object", "we saw the places"),
    Case("n18", "N", "The spot I picked was shady.", "spot", "object", "I picked the spot"),
    Case("n19", "N", "The summer I remember best was hot.", "summer", "object",
         "I remember the summer"),
    Case("n20", "N", "The room I painted is blue.", "room", "object", "I painted the room"),

    # --- M: minimal pairs with the antecedent as the MATRIX object — d1's own bench. stanza tags
    # «I remember the DAY I slept» day `obl:tmod`, which is wrong for the matrix (the day is what is
    # remembered); these pairs ask whether that wrong tag is nonetheless leaking a right guess
    # about the gap. Same matrix verb, same antecedent, only the relative's verb changes.
    Case("m01", "M", "I remember the day I described.", "day", "object", "I described the day"),
    Case("m02", "M", "I miss the summer I spent.", "summer", "object", "I spent the summer"),
    Case("m03", "M", "I recall the year I wasted.", "year", "object", "I wasted the year"),
    Case("m04", "M", "I love the night we planned.", "night", "object", "we planned the night"),
    Case("m05", "M", "I love the night we danced.", "night", "time", "we danced that night"),
    Case("m06", "M", "I hate the week I chose.", "week", "object", "I chose the week"),
    Case("m07", "M", "I hate the week we stayed.", "week", "time", "we stayed that week"),
    Case("m08", "M", "I remember the moment I chose.", "moment", "object", "I chose the moment"),
    Case("m09", "M", "I remember the moment he fell.", "moment", "time", "he fell at that moment"),
    Case("m10", "M", "I remember the morning I enjoyed.", "morning", "object",
         "I enjoyed the morning"),
    Case("m11", "M", "I remember the morning she left.", "morning", "time",
         "she left that morning — «leave» with its object unsaid, not the morning left"),
    Case("m12", "M", "I miss the time I had.", "time", "object", "I had the time"),
    Case("m13", "M", "I remember the place I found.", "place", "object", "I found the place"),
    Case("m14", "M", "I remember the place we slept.", "place", "place", "we slept in that place"),
    Case("m15", "M", "I remember the way I chose.", "way", "object",
         "I chose the way (the path)"),
    Case("m16", "M", "I remember the way she laughed.", "way", "manner",
         "she laughed in that way"),

    # --- S: stranded marker controls — not the withheld shape; must drop out of the scoring -----
    Case("s01", "S", "The house I live in is old.", "house", "place", "I live in the house"),
    Case("s02", "S", "The girl I talked to is shy.", "girl", "other", "I talked to the girl"),
    Case("s03", "S", "The pen I write with is blue.", "pen", "other", "I write with the pen"),
    Case("s04", "S", "The town I grew up in is small.", "town", "place", "I grew up in the town"),
    Case("s05", "S", "The day I waited for came.", "day", "other", "I waited for the day"),

    # --- E: embedded gaps and measures --------------------------------------------------------
    Case("e01", "E", "The book I want to read is long.", "book", "object",
         "I want to read the book — the gap is the object of the EMBEDDED verb, not of want"),
    Case("e02", "E", "The man I think you met is here.", "man", "object",
         "I think you met the man — the gap is inside the ccomp"),
    Case("e03", "E", "The day I decided to leave was cold.", "day", "time",
         "time, whichever verb it hangs from (deciding or leaving)"),
    Case("e04", "E", "The hours I worked were long.", "hours", "other",
         "I worked for those hours — a DURATION/measure, not an object and not a point in time"),
    Case("e05", "E", "The miles we walked were many.", "miles", "other",
         "we walked those miles — an extent; arguably a cognate object, labelled measure"),
)

# --- H: THE HELD-OUT CHECK — the ruling's cost clause (the Captain, 2026-09-25) ------------------
# «Rows for exactly the bench's two wrongs is tuning on the test», so `db/0038`'s `time`/`way` rows
# are trusted only if THESE hold. Written by the 1st Officier AFTER the rows and the code existed,
# before either was run on them, and nothing was tuned after seeing them. Heads: time · moment ·
# way · reason · place, as adverbial gaps AND as objects. Scored apart, never pooled with the above.
HELD_OUT = (
    # time
    Case("h01", "H", "The time she arrived was late.", "time", "time",
         "she arrived at that time"),
    Case("h02", "H", "I forgot the time the train leaves.", "time", "time",
         "the train leaves at that time; nothing is left"),
    Case("h03", "H", "We talked about the time you fainted.", "time", "time",
         "you fainted at that time"),
    Case("h04", "H", "The time I spent here was good.", "time", "object",
         "I spent the time — the time is what was spent"),
    Case("h05", "H", "I need the time you promised.", "time", "object",
         "you promised the time — the time is what was promised"),
    # moment
    Case("h06", "H", "The moment she smiled, I knew.", "moment", "time",
         "she smiled at that moment; the NP is itself the matrix's temporal"),
    Case("h07", "H", "I remember the moment we met.", "moment", "time",
         "we met at that moment; «meet» with a plural subject and nobody met"),
    Case("h08", "H", "I missed the moment he described.", "moment", "object",
         "he described the moment"),
    Case("h09", "H", "This is the moment I dreaded.", "moment", "object",
         "I dreaded the moment"),
    # way
    Case("h10", "H", "I love the way you think.", "way", "manner", "you think in that way"),
    Case("h11", "H", "The way they talk is strange.", "way", "manner", "they talk in that way"),
    Case("h12", "H", "I hate the way it ends.", "way", "manner", "it ends in that way"),
    Case("h13", "H", "The way we took was long.", "way", "object",
         "we took the way (the route) — the way is what was taken"),
    Case("h14", "H", "The way you suggested is faster.", "way", "object",
         "you suggested the way (the route or the method) — what was suggested"),
    # reason
    Case("h15", "H", "The reason she smiled is a secret.", "reason", "reason",
         "she smiled for that reason"),
    Case("h16", "H", "I understand the reason you worried.", "reason", "reason",
         "you worried for that reason"),
    Case("h17", "H", "The reason he offered was weak.", "reason", "object",
         "he offered the reason"),
    Case("h18", "H", "The reason you stated was false.", "reason", "object",
         "you stated the reason"),
    # place
    Case("h19", "H", "I found the place she hides.", "place", "place",
         "she hides in that place; nothing named is hidden"),
    Case("h20", "H", "The place we met was a cafe.", "place", "place", "we met at that place"),
    Case("h21", "H", "The place you recommended was full.", "place", "object",
         "you recommended the place"),
    Case("h22", "H", "I finally saw the place he described.", "place", "object",
         "he described the place"),
    Case("h23", "H", "The place they work is noisy.", "place", "place",
         "they work in that place"),
)


# ---------------------------------------------------------------------------------------------
# a — the verb frames
# ---------------------------------------------------------------------------------------------

# The readers are the STATION's (`tk2.dictionary.frames`, since the ruling of 2026-09-25 built
# them in): one implementation, so what this bench measured is what the station runs.
FRAMES = canonical_frames()
OBJECT_FRAMES = object_frames()


def a1(verb, _noun):
    senses = verb_senses(verb)
    if not senses:
        return None
    return "object" if senses[0] & OBJECT_FRAMES else "adverbial"


def a2(verb, _noun):
    senses = verb_senses(verb)
    if not senses:
        return None
    has_obj, has_other = bool(senses[0] & OBJECT_FRAMES), bool(senses[0] - OBJECT_FRAMES)
    if has_obj and not has_other:
        return "object"
    if not has_obj:
        return "adverbial"
    return None


def a3(verb, _noun):
    senses = verb_senses(verb)
    if not senses:
        return None
    return "object" if any(s & OBJECT_FRAMES for s in senses) else "adverbial"


def a4(verb, _noun):
    senses = verb_senses(verb)
    if not senses:
        return None
    frames = set().union(*senses)
    if not frames & OBJECT_FRAMES:
        return "adverbial"
    if not frames - OBJECT_FRAMES:
        return "object"
    return None


# ---------------------------------------------------------------------------------------------
# b — the antecedent's supersense (the station's own reader)
# ---------------------------------------------------------------------------------------------

SUPERSENSE_ROLE = {"noun.time": "time", "noun.location": "place", "noun.motive": "reason"}


def b_role(noun):
    return SUPERSENSE_ROLE.get(supersense_for(noun, "NOUN"))


def b1(_verb, noun):
    return b_role(noun)


def b2(_verb, noun):
    return b_role(noun) or "object"


# ---------------------------------------------------------------------------------------------
# c — the three combinations, fixed before the first run
# ---------------------------------------------------------------------------------------------

def c1(verb, noun):
    a, b = a1(verb, noun), b_role(noun)
    if a == "object" and b is None:
        return "object"
    if a == "adverbial" and b is not None:
        return b
    return None


def c2(verb, noun):
    senses, b = verb_senses(verb), b_role(noun)
    if not senses:
        return None
    if b is not None and senses[0] - OBJECT_FRAMES:
        return b
    if senses[0] & OBJECT_FRAMES:
        return "object"
    return b or "adverbial"


def c3(verb, noun):
    a = a4(verb, noun)
    if a == "object":
        return "object"
    if a == "adverbial":
        return b_role(noun) or "adverbial"
    return b1(verb, noun)


# ---------------------------------------------------------------------------------------------
# the parse
# ---------------------------------------------------------------------------------------------

SUBJECTS = ("nsubj", "nsubj:pass", "csubj", "expl")


@dataclass
class Parsed:
    case: Case
    shape: str = ""            # "withheld" when the station would reach the question
    verb: str = ""
    antecedent_lemma: str = ""
    antecedent_dep: str = ""
    verb_children: tuple = ()
    sbar: str = ""
    answers: dict = field(default_factory=dict)
    skeleton: object = None
    #: the station's whole zip for the sentence — complete (nothing unplaced) or not
    complete: bool | None = None


def parse(provider, case: Case) -> Parsed:
    out = Parsed(case)
    skeleton = provider(case.text)[0]
    out.skeleton = skeleton
    relcls = [w for w in skeleton if w.dep == "acl:relcl"
              and skeleton[w.head].text.lower() == case.antecedent.lower()]
    if not relcls:
        found = [(w.text, w.dep, skeleton[w.head].text) for w in skeleton if w.dep != "punct"]
        out.shape = f"no acl:relcl on «{case.antecedent}»: {found}"
        return out
    verb = relcls[0]
    head = skeleton[verb.head]
    children = skeleton.children(verb.index)
    out.verb, out.antecedent_lemma, out.antecedent_dep = verb.lemma, head.lemma, head.dep
    out.verb_children = tuple(c.dep for c in children)
    deps = [c.dep for c in children]
    if any(c.feats.get("PronType") == "Rel" for c in children):
        out.shape = "relative pronoun"
    elif not any(d in SUBJECTS for d in deps):
        out.shape = "no subject"
    elif any(c.upos == "ADP" and c.dep in ("obl", "nmod", "obl:npmod") for c in children):
        out.shape = "stranded marker"
    elif "obj" in deps:
        out.shape = "object said"
    else:
        out.shape = "withheld"
    return out


def sbar_of(snlp, case: Case) -> str:
    """The relative's SBAR as the constituency parser prints it — d2's evidence."""
    tree = snlp(case.text).sentences[0].constituency
    found = []

    def walk(node):
        if node.label == "SBAR":
            found.append(str(node))
        for child in node.children:
            walk(child)
    walk(tree)
    return found[0] if found else ""


def d2_has_gap_marker(sbar: str) -> bool:
    return "-NONE-" in sbar or "(WHNP" in sbar or "*T*" in sbar


def d1(parsed: Parsed):
    return "time" if "tmod" in parsed.antecedent_dep else None


def baseline_n(_verb, _noun):
    return "object"


def baseline_w(_verb, _noun):
    return None


# ---------------------------------------------------------------------------------------------
# S — the station as built (`Compiler._zero_gap`, `db/0038`), end to end
# ---------------------------------------------------------------------------------------------

#: A tkzip box, read back as the bench's gold vocabulary. Anything else is reported by its own name
#: and scores wrong.
BOX_AS_GOLD = {"patient": "object", "time": "time", "location": "place", "manner": "manner"}
STATION = "S the station (built)"


def station_answer(compiler, parsed: Parsed):
    """Compile the sentence and read which box of the relative's row holds the antecedent's
    variable — None when the clause was withheld. Sets `parsed.complete` as a side record."""
    out = compiler.compile(parsed.skeleton)
    parsed.complete = not out.zip.unplaced
    binders = {r.binds: r for r in out.zip.rows if r.kind == "quantifier"}
    for row in out.zip.rows:
        if row.kind != "content" or row.predicate != f"{parsed.verb}.v":
            continue
        for role, box in row.boxes.items():
            name = getattr(box.head, "name", None)
            binder = binders.get(name) if name else None
            if binder is not None and binder.restriction is not None \
                    and binder.restriction.head == f"{parsed.antecedent_lemma}.n":
                return BOX_AS_GOLD.get(role.value, role.value)
    return None


LEXICAL = {"a1 primary-permissive": a1, "a2 primary-strict": a2, "a3 any-permissive": a3,
           "a4 any-strict": a4, "b1 supersense strict": b1, "b2 supersense full": b2,
           "c1 agreement": c1, "c2 a decides, b overrides": c2, "c3 a4 then b1": c3,
           "N no-object=object": baseline_n, "W withhold (today)": baseline_w}


# ---------------------------------------------------------------------------------------------
# scoring
# ---------------------------------------------------------------------------------------------

def binary(label):
    if label is None:
        return None
    return "object" if label == "object" else "adverbial"


def score(rows: list[Parsed], name: str):
    tally = {"binary": Counter(), "role": Counter()}
    wrong = []
    for row in rows:
        answer, gold = row.answers[name], row.case.gold
        if answer is None:
            tally["binary"]["abstain"] += 1
        elif binary(answer) == binary(gold):
            tally["binary"]["right"] += 1
        else:
            tally["binary"]["wrong"] += 1
            wrong.append(row)
        if answer is None or answer == "adverbial":
            tally["role"]["abstain"] += 1
        elif answer == gold:
            tally["role"]["right"] += 1
        else:
            tally["role"]["wrong"] += 1
    return tally, wrong


def fmt(t: Counter, n: int) -> str:
    answered = t["right"] + t["wrong"]
    precision = f"{t['right'] / answered:5.1%}" if answered else "  —  "
    return (f"{t['right']:3d} {t['wrong']:3d} {t['abstain']:3d}  prec {precision}  "
            f"cov {answered / n:5.1%}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", action="store_true", help="print every case with every answer")
    ap.add_argument("--json", help="write the per-case results here")
    args = ap.parse_args()

    from tk2.language import standing_closed_classes
    from tk2.language.compile import Compiler

    provider = StanzaSkeletons()
    compiler = Compiler(standing_closed_classes())
    snlp = provider.pipeline().tokenizer.snlp
    parsed = [parse(provider, case) for case in CASES]
    held = [parse(provider, case) for case in HELD_OUT]
    for row in [*parsed, *held]:
        row.sbar = sbar_of(snlp, row.case)
        if row.verb:
            for name, signal in LEXICAL.items():
                row.answers[name] = signal(row.verb, row.antecedent_lemma)
            row.answers["d1 antecedent tmod"] = d1(row)
            row.answers[STATION] = station_answer(compiler, row)

    print(f"object frames (derived from the strings): {sorted(OBJECT_FRAMES)}")
    print(f"cases: {len(CASES)}  by gold: {dict(Counter(c.gold for c in CASES))}")
    shapes = Counter(r.shape if r.shape in ("withheld", "stranded marker", "object said",
                                            "no subject", "relative pronoun") else "misparse"
                     for r in parsed)
    print(f"stanza shapes: {dict(shapes)}")
    for row in parsed:
        if row.shape != "withheld":
            print(f"  not scored  {row.case.key} [{row.case.group}] {row.case.text!r}: {row.shape}")

    scored = [r for r in parsed if r.shape == "withheld"]
    n = len(scored)
    print(f"\nscored (the withheld shape): {n}   gold binary: "
          f"{dict(Counter(binary(r.case.gold) for r in scored))}")
    print(f"\n{'candidate':30s} | {'BINARY  right wrong abst':38s} | ROLE  right wrong abst")
    wrongs = {}
    for name in [*LEXICAL, "d1 antecedent tmod", STATION]:
        tally, wrong = score(scored, name)
        wrongs[name] = wrong
        print(f"{name:30s} | {fmt(tally['binary'], n):38s} | {fmt(tally['role'], n)}")

    print("\nWRONG (binary) per candidate:")
    for name, rows in wrongs.items():
        if not rows or name.startswith("N "):
            continue
        print(f"  {name}:")
        for r in rows:
            print(f"      {r.case.key} {r.case.text!r:44s} {r.verb}/{r.antecedent_lemma} "
                  f"gold={r.case.gold} said={r.answers[name]}")

    print("\nd1 — the antecedent's matrix dep, by gold:")
    for gold in ("object", "adverbial"):
        print(f"  {gold:9s} {dict(Counter(r.antecedent_dep for r in scored if binary(r.case.gold) == gold))}")
    print("d2 — relative SBARs with a WH node or empty element: "
          f"{sum(d2_has_gap_marker(r.sbar) for r in parsed)} of {len(parsed)}")
    print("relcl children by gold:")
    for gold in ("object", "adverbial"):
        print(f"  {gold:9s} {dict(Counter(d for r in scored if binary(r.case.gold) == gold for d in r.verb_children))}")

    print("\nsupersense of two minds (antecedents whose noun senses span >1 of time/location/motive "
          "or of those and something else):")
    for lemma in sorted({r.antecedent_lemma for r in scored}):
        classes = sorted({s.lexname() for s in wn.synsets(lemma, "n")})
        primary = supersense_for(lemma, "NOUN")
        if set(classes) & set(SUPERSENSE_ROLE) and len(classes) > 1:
            print(f"  {lemma:10s} primary={primary:15s} all={classes}")

    print("\nverb frames of the scored verbs (primary | any):")
    for verb in sorted({r.verb for r in scored}):
        senses = verb_senses(verb)
        primary = sorted(senses[0]) if senses else []
        print(f"  {verb:10s} primary={primary}  a1={a1(verb, '')} a2={a2(verb, '')} "
              f"a3={a3(verb, '')} a4={a4(verb, '')}  senses={len(senses)}")

    report_held_out(held)

    if args.cases:
        print()
        for r in parsed:
            print(f"{r.case.key} {r.case.text!r} gold={r.case.gold} shape={r.shape} "
                  f"verb={r.verb} ante={r.antecedent_lemma}/{r.antecedent_dep} "
                  f"children={r.verb_children}")
            print(f"     {r.answers}")
            print(f"     {r.sbar}")
    if args.json:
        Path(args.json).write_text(json.dumps([
            {"key": r.case.key, "group": r.case.group, "text": r.case.text, "gold": r.case.gold,
             "why": r.case.why, "shape": r.shape, "verb": r.verb, "antecedent": r.antecedent_lemma,
             "antecedent_dep": r.antecedent_dep, "children": r.verb_children, "sbar": r.sbar,
             "answers": r.answers, "complete": r.complete} for r in [*parsed, *held]],
            indent=1))
    return 0


def report_held_out(held: list[Parsed]) -> None:
    """The ruling's cost clause, scored APART: a held-out set is worth nothing pooled."""
    print("\n" + "=" * 96)
    print("THE HELD-OUT CHECK — written after `db/0038` existed, never tuned on (the ruling's cost)")
    print("=" * 96)
    scored = [r for r in held if r.shape == "withheld"]
    for row in held:
        if row.shape != "withheld":
            print(f"  not scored  {row.case.key} {row.case.text!r}: {row.shape}")
    n = len(scored)
    print(f"  scored: {n} of {len(held)}   gold binary: "
          f"{dict(Counter(binary(r.case.gold) for r in scored))}")
    print(f"\n  {'candidate':30s} | {'BINARY  right wrong abst':38s} | ROLE  right wrong abst")
    for name in [*LEXICAL, "d1 antecedent tmod", STATION]:
        tally, _wrong = score(scored, name)
        print(f"  {name:30s} | {fmt(tally['binary'], n):38s} | {fmt(tally['role'], n)}")
    print("\n  per case — the station as built:")
    for r in held:
        said = r.answers.get(STATION)
        verdict = ("withheld" if said is None else "RIGHT" if said == r.case.gold
                   else "WRONG ROLE" if binary(said) == binary(r.case.gold) else "WRONG")
        whole = "" if r.complete is None else ("  zip complete" if r.complete else "  zip partial")
        print(f"    {r.case.key} {r.case.text!r:44s} {r.verb}/{r.antecedent_lemma:7s} "
              f"gold={r.case.gold:7s} said={str(said):8s} {verdict}{whole}")
        print(f"         why: {r.case.why}")


if __name__ == "__main__":
    sys.exit(main())
