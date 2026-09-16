"""THE AMBIGUOUS MARKERS' BENCH — every case the selector has to get right, with its gold.

**WHY A BENCH AND NOT MORE GATE CASES.** The UD gate measures the PARSE: a skeleton in, and did the
station read the relation UD says is there. This measures the SELECTOR, whose input is not a
sentence but a tuple — *which marker, on which nominal, under which verb* — and putting a parser in
front of it would make a wrong number unattributable between the two. So the cases here are stated
at exactly the selector's own signature, and the gate keeps its job.

**THE CASES COME FROM THREE PLACES, AND THEY ARE NOT WORTH THE SAME.**

- `drill` — E2's seventy-eight hand-compiled sentences, ruled by the Captain and committed before
  any of this existed. **Independent evidence**: nobody writing them was thinking about a selector.
- `ud` — the two UD examples whose marker the gate already abstains on.
- `curation` — the worked examples written into `db/0008`'s own comments («at the door / at noon /
  at speed»). **These are the claim, not a test of it**: a selector that reproduces them has agreed
  with the curation and discovered nothing. They are here because the curation's coverage is what
  the thirteen rows promise, and a selector that could not even hold its own examples would be
  refuted — but they are scored APART and never averaged in.

**PROPER NAMES ARE MARKED AND SCORED APART.** «Anna», «Genoa», «Osaka» are named individuals, and
tk2 has a standing refusal about them: `wordnet.is_name_only` keeps them out of the base, and what
replaces them (a type-centroid vector plus a context-scoped identity) is not built. WordNet reads
`anna` as a coin and `genoa` as a triangular sail. Averaging those into one number would hide a
known, parked hole behind a selector's score.
"""

from dataclasses import dataclass

DRILL, UD, CURATION = "drill", "ud", "curation"


@dataclass(frozen=True, slots=True)
class MarkerCase:
    """One ambiguous marker, in the company that is supposed to settle it."""

    #: the marker's surface form — one of the thirteen (and their cousins) `db/0008` lists
    marker: str
    #: the nominal it marks: lemma, and UD's POS for it
    nominal: str
    nominal_upos: str
    #: the word the marked phrase hangs off — a verb's lemma, or the noun for a possessor phrase
    head: str
    head_upos: str
    #: UD's relation between that head and the nominal — `obl`, `nmod`, `advmod`, …
    dep: str
    #: the tkzip role this must compile to — or `relation`, the one FIELD a marker can name, which
    #: is what a possessor phrase is (req 26: the possessor lives inside the record, not in a box)
    expect: str
    #: where the gold came from: `drill`, `ud` or `curation` — they are NOT worth the same
    source: str
    phrase: str = ""
    #: a named individual: the base refuses it and the identity layer is not built
    name: bool = False


def _m(marker, nominal, nominal_upos, head, head_upos, dep, expect, source, phrase, name=False):
    return MarkerCase(marker=marker, nominal=nominal, nominal_upos=nominal_upos, head=head,
                      head_upos=head_upos, dep=dep, expect=expect, source=source, phrase=phrase,
                      name=name)


CASES: tuple[MarkerCase, ...] = (
    # ── from E2's drill: hand-compiled, ruled, and committed before this task existed ────────────
    _m("at", "home", "NOUN", "stay", "VERB", "obl", "location", DRILL, "I stay at home"),
    _m("to", "station", "NOUN", "walk", "VERB", "obl", "destination", DRILL, "I walk to the station"),
    _m("in", "garden", "NOUN", "cat", "NOUN", "obl", "location", DRILL, "a cat is in the garden"),
    _m("to", "cub", "NOUN", "feed", "VERB", "obl", "recipient", DRILL, "it feeds milk to its cubs"),
    _m("with", "hammer", "NOUN", "build", "VERB", "obl", "instrument", DRILL,
       "I build my contraption with my hammer"),
    _m("of", "titanium", "NOUN", "make", "VERB", "obl", "source", DRILL,
       "the hammer is made of titanium"),
    _m("for", "family", "NOUN", "work", "VERB", "obl", "beneficiary", DRILL,
       "she works for her family"),
    _m("with", "fork", "NOUN", "eat", "VERB", "obl", "instrument", DRILL, "I ate with a fork"),
    _m("with", "anna", "PROPN", "eat", "VERB", "obl", "comitative", DRILL, "I ate with Anna",
       name=True),
    _m("of", "city", "NOUN", "name", "NOUN", "nmod", "relation", DRILL,
       "the name of a big city"),
    _m("in", "asia", "PROPN", "live", "VERB", "obl", "location", DRILL, "I live in Asia", name=True),
    _m("in", "osaka", "PROPN", "live", "VERB", "obl", "location", DRILL, "Osaka is where you live",
       name=True),
    _m("to", "genoa", "PROPN", "go", "VERB", "obl", "destination", DRILL, "I went to Genoa",
       name=True),
    _m("in", "france", "PROPN", "drive", "VERB", "obl", "location", DRILL,
       "you may drive in France", name=True),

    # ── from the UD gate: the two abstentions the corpus names ───────────────────────────────────
    _m("to", "friend", "NOUN", "talk", "VERB", "obl", "recipient", UD,
       "I talked to my friend in the park"),
    _m("in", "pool", "NOUN", "swim", "VERB", "obl", "location", UD,
       "Last night , I swam in the pool"),

    # ── the curation's own worked examples — the CLAIM, scored apart ──────────────────────────────
    _m("at", "door", "NOUN", "stand", "VERB", "obl", "location", CURATION, "at the door"),
    _m("at", "noon", "NOUN", "leave", "VERB", "obl", "time", CURATION, "at noon"),
    _m("at", "speed", "NOUN", "drive", "VERB", "obl", "manner", CURATION, "at speed"),
    _m("in", "paris", "PROPN", "live", "VERB", "obl", "location", CURATION, "in Paris", name=True),
    _m("in", "may", "NOUN", "leave", "VERB", "obl", "time", CURATION, "in May"),
    _m("in", "ink", "NOUN", "write", "VERB", "obl", "instrument", CURATION, "written in ink"),
    _m("on", "table", "NOUN", "lie", "VERB", "obl", "location", CURATION, "on the table"),
    _m("on", "monday", "NOUN", "leave", "VERB", "obl", "time", CURATION, "on Monday"),
    _m("on", "physics", "NOUN", "lecture", "VERB", "obl", "topic", CURATION, "a lecture on physics"),
    _m("by", "train", "NOUN", "travel", "VERB", "obl", "instrument", CURATION, "by train"),
    _m("by", "river", "NOUN", "walk", "VERB", "obl", "path", CURATION, "by the river"),
    _m("by", "noon", "NOUN", "arrive", "VERB", "obl", "time", CURATION, "by noon"),
    _m("to", "paris", "PROPN", "go", "VERB", "obl", "destination", CURATION, "go to Paris",
       name=True),
    _m("to", "anna", "PROPN", "give", "VERB", "obl", "recipient", CURATION, "give to Anna",
       name=True),
    _m("of", "sister", "NOUN", "cat", "NOUN", "nmod", "relation", CURATION, "the cat of my sister"),
    _m("of", "wood", "NOUN", "make", "VERB", "obl", "source", CURATION, "made of wood"),
    _m("with", "knife", "NOUN", "cut", "VERB", "obl", "instrument", CURATION, "cut with a knife"),
    _m("with", "anna", "PROPN", "go", "VERB", "obl", "comitative", CURATION, "went with Anna",
       name=True),
    _m("for", "anna", "PROPN", "buy", "VERB", "obl", "beneficiary", CURATION, "for Anna", name=True),
    _m("for", "paris", "PROPN", "leave", "VERB", "obl", "destination", CURATION, "left for Paris",
       name=True),
    _m("for", "hour", "NOUN", "wait", "VERB", "obl", "duration", CURATION, "for an hour"),
    _m("over", "table", "NOUN", "hang", "VERB", "obl", "location", CURATION, "over the table"),
    _m("over", "bridge", "NOUN", "walk", "VERB", "obl", "path", CURATION, "over the bridge"),
    _m("over", "week", "NOUN", "spread", "VERB", "obl", "duration", CURATION, "over a week"),
    _m("up", "hill", "NOUN", "walk", "VERB", "obl", "location", CURATION, "up the hill"),
    _m("as", "doctor", "NOUN", "work", "VERB", "obl", "manner", CURATION, "works as a doctor"),

    # ── a few more where the discriminator is plain, to keep the bench from being all `in` ────────
    _m("in", "room", "NOUN", "sit", "VERB", "obl", "location", CURATION, "sat in the room"),
    _m("at", "night", "NOUN", "work", "VERB", "obl", "time", CURATION, "at night"),
    _m("for", "week", "NOUN", "stay", "VERB", "obl", "duration", CURATION, "for a week"),
    _m("with", "friend", "NOUN", "travel", "VERB", "obl", "comitative", CURATION,
       "travelled with a friend"),
    _m("to", "teacher", "NOUN", "speak", "VERB", "obl", "recipient", CURATION,
       "spoke to the teacher"),
    _m("by", "car", "NOUN", "travel", "VERB", "obl", "instrument", CURATION, "by car"),
    _m("in", "winter", "NOUN", "ski", "VERB", "obl", "time", CURATION, "in winter"),
    _m("over", "year", "NOUN", "grow", "VERB", "obl", "duration", CURATION, "over a year"),
    _m("to", "school", "NOUN", "go", "VERB", "obl", "destination", CURATION, "go to school"),
    _m("in", "bottle", "NOUN", "keep", "VERB", "obl", "location", CURATION, "kept in a bottle"),
)


def independent() -> tuple[MarkerCase, ...]:
    """The cases nobody wrote with a selector in mind — the ones a score may be claimed on."""
    return tuple(c for c in CASES if c.source in (DRILL, UD))


def named() -> tuple[MarkerCase, ...]:
    """The cases resting on a named individual — a known, parked hole, scored apart."""
    return tuple(c for c in CASES if c.name)


def markers() -> tuple[str, ...]:
    return tuple(sorted({c.marker for c in CASES}))
