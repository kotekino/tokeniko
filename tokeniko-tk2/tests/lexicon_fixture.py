"""A sixteen-word world, handcrafted so the closure engine's every claim can be checked by hand.

It is not a sample of English. It is three shapes, chosen because each one is a thing the engine has
to get right and the real lexicon is far too big to check by eye:

  1. THE CAPTAIN'S EXAMPLE, verbatim: me -> not you | you -> not me | not -> negation |
     negation -> not. The set {me, not, you, negation} defines itself and never leaves. Its MINIMAL
     closed subset is {not, negation}, and the difference between those two facts is the difference
     between `is_closed` and `closed_sets`.

  2. THE `right` RING. Seeded at {sleep, leave} with the standing depth cut of 2, the closure admits
     `left` on the last ring and never expands it — so `right`, which only `left` names, sits exactly
     one ring outside a subset that already contains the word naming it. This is the review's own
     finding (2026-08-12, the Captain found it by looking at the map) turned into a regression: the
     boundary is allowed to be there, it is not allowed to be invisible.

  3. THE COLLISION, requirement 21 — REPAIRED 2026-08-25 (T2). `go`'s definition says «as when one
     has left», and `left` is *leave*'s participle as much as it is the direction. The old reduction
     took the surface form and stopped, so it minted the direction and never saw `leave` at all.
     Now the token names BOTH, because at this layer both are true, and the collision is killed
     where it actually did damage — at the KEY: `left` is not a base form of a verb, so `left.v`
     (which was only ever a second name for `leave.v`) cannot be minted. `USE_USED` below is the
     same disease in its second reported form.

  4. THE NAME REFUSAL, the Captain's option C (2026-08-25, T2b) — `NAME_ONLY` at the foot of this
     file, in its own six-word world for the same reason `USE_USED` has one. WordNet's `or` is
     Oregon's `OR` and its `me` is Maine's `ME`; a lexicon built from the case-folded lemma index
     admits both as if they were function words, and `or` then landed on 57.8% of the real base's
     rows. That world is where the engine has to refuse a reading it was HANDED — its lexicon
     contains `or` and `me` on purpose.

The resource this fixture imitates is DELIBERATELY over-generous about parts of speech, exactly as
WordNet is: `PARTS_OF_SPEECH` lists `left` as a verb because `wn.synsets("left")` does, having
walked back to `leave` on its own. The engine, not the table, is what refuses to mint the dimension.

One divergence from the real adapter, stated out loud because it is a finding and not a convenience:
this fixture's stop list does NOT contain `me`, `you` or `not`, and nltk's English stop list does.
Since the Captain's ruling of 2026-08-25 that lexicon membership outranks the stop list, that
divergence no longer decides whether his closure example can form here — the words are lexicon
members on both sides. What still decides it on the real resource is membership itself: `you` is not
a WordNet lemma at all.
"""

# ------------------------------------------------------------------------------------------------
# the world
# ------------------------------------------------------------------------------------------------

LEXICON = (
    "me",
    "you",
    "not",
    "negation",
    "sleep",
    "leave",
    "go",
    "place",
    "rest",
    "bed",
    "move",
    "left",
    "right",
    "direction",
    "furniture",
    "work",
)

# The primary-sense definitions. Written in the register of a real gloss — a fixture whose glosses
# are word lists would test the graph and never the reduction.
GLOSSES = {
    "me": "not you",
    "you": "not me",
    "not": "a negation",
    "negation": "the act that says not",
    "sleep": "to rest in a bed",
    "leave": "to go away from a place",
    "go": "to move, as when one has left",
    "place": "an area where one may rest",
    "rest": "to stop work for a while",
    "bed": "furniture that provides a place to sleep",
    "move": "to go from one place to another",
    "left": "the direction opposite to right",
    "right": "the direction opposite to left",
    "direction": "the line along which something moves",
    "furniture": "the movable objects in a room",
    "work": "labor at a task",
}

# `senses="all"` adds the further senses. Only one word has one, and that is enough: it proves the
# mode reaches the resource and changes the graph — `work` stops being silent, and stops being a
# closed set of one.
GLOSSES_ALL = {
    "work": "labor at a task ; the place where one labors",
}

# What morphy would answer, PER PART OF SPEECH — the exceptions only. Everything else follows the
# rule morphy itself follows: a word is its own lemma for every POS the resource lists it under
# (see `FixtureGlossProvider.lemma`). Deliberately sparse: only the forms the glosses contain.
LEMMA_EXCEPTIONS = {
    ("says", "v"): "say",
    ("moves", "v"): "move",
    ("provides", "v"): "provide",
    ("objects", "v"): "object",
    ("labors", "v"): "labor",
    ("left", "v"): "leave",     # requirement 21's whole story, in one entry
}

# The fixture's own stop list — see the module head for why it is not nltk's.
STOPWORDS = frozenset(
    {
        "a", "an", "the", "to", "in", "of", "at", "for", "from", "over", "and", "as",
        "when", "where", "which", "that", "who", "one", "has", "have", "may", "is", "was",
    }
)

# Every word's parts of speech AS THE RESOURCE REPORTS THEM — `left` is listed as a verb for the
# same reason WordNet lists it as one, and the engine is what declines to mint `left.v`.
PARTS_OF_SPEECH = {
    "me": ("n",),
    "you": ("n",),
    "not": ("r",),
    "negation": ("n",),
    "sleep": ("n", "v"),
    "leave": ("n", "v"),
    "go": ("n", "v"),
    "place": ("n", "v"),
    "rest": ("n", "v"),
    "bed": ("n",),
    "move": ("n", "v"),
    "left": ("n", "v", "a", "r"),
    "right": ("n", "v", "a", "r"),
    "direction": ("n",),
    "furniture": ("n",),
    "work": ("n", "v"),
}


# ------------------------------------------------------------------------------------------------
# the provider
# ------------------------------------------------------------------------------------------------


class FixtureGlossProvider:
    """The `GlossProvider` protocol over the world above. No nltk, no network, no corpus."""

    def __init__(
        self,
        lexicon=LEXICON,
        glosses=None,
        glosses_all=None,
        lemmas=None,
        stopwords=STOPWORDS,
        parts_of_speech=None,
        name_readings=None,
    ):
        self._lexicon = tuple(lexicon)
        self._glosses = dict(GLOSSES if glosses is None else glosses)
        self._glosses_all = dict(GLOSSES_ALL if glosses_all is None else glosses_all)
        self._lemmas = dict(LEMMA_EXCEPTIONS if lemmas is None else lemmas)
        self._stopwords = frozenset(stopwords)
        self._pos = dict(PARTS_OF_SPEECH if parts_of_speech is None else parts_of_speech)
        self._name_readings = dict(name_readings or {})

    def lexicon(self):
        return self._lexicon

    def gloss(self, word, senses="primary"):
        """A refused reading does not speak. The real adapter gets this for free — its gloss is
        built from the synsets the word is spelled in — and the fixture has to state it, because a
        world whose refused words still had definitions would test the filter and not the seam."""
        if self.is_name_only(word):
            return ""
        if senses == "all" and word in self._glosses_all:
            return self._glosses_all[word]
        return self._glosses.get(word, "")

    def parts_of_speech(self, word):
        """What the resource reports, MINUS the readings that are names. WordNet's `be` is listed as
        a noun because of beryllium; reporting that noun would mint `be.n`, a dimension whose whole
        content is a chemical symbol."""
        names = self._name_readings.get(word, ())
        return tuple(p for p in self._pos.get(word, ()) if p not in names)

    def lemma(self, token, pos):
        """morphy's shape: an exception first, otherwise the token itself if the resource lists it
        under that POS at all. Which is why `left` read as a verb is `leave` and read as a noun is
        `left` — one table, both answers, no ordering deciding anything."""
        exception = self._lemmas.get((token, pos))
        if exception is not None:
            return exception
        return token if pos in self._pos.get(token, ()) else None

    def lemmas(self, token):
        found = []
        for pos in ("n", "v", "a", "r"):
            lemma = self.lemma(token, pos)
            if lemma and lemma not in found:
                found.append(lemma)
        return tuple(found)

    def stopwords(self):
        return self._stopwords

    def senses_of_key(self, key):
        """The senses one DIMENSION speaks for. One per (word, POS) here — enough to prove that
        curation reads a particular definition and quotes it, and few enough to check by eye."""
        word, _, pos = key.rpartition(".")
        return (_fixture_sense(word, pos),) if pos in self.parts_of_speech(word) else ()

    def definition_of_sense(self, sense):
        """One sense's definition. The fixture's senses are `word.pos.01`, so this is the word's
        gloss — which is what makes the sixteen-word world usable as a curation world too."""
        word = sense.rsplit(".", 2)[0]
        return self.gloss(word)

    def is_name_only(self, word):
        """Every reading this world has for the spelling is a name. Declared per POS in
        `name_readings` rather than derived, because the fixture has no synsets to read a capital
        off — it imitates the answer, the adapter measures it."""
        listed = self._pos.get(word, ())
        names = self._name_readings.get(word, ())
        return bool(listed) and all(p in names for p in listed)


# ------------------------------------------------------------------------------------------------
# a second, three-word world: `use` / `used`, requirement 21's other reported collision
# ------------------------------------------------------------------------------------------------

# Kept apart from the sixteen-word world on purpose. It exists to prove ONE thing — that an
# inflection cannot mint a key — and folding it into the main world would cost every hand-checked
# layer and count above their checkability.
#
# The shape, WordNet's own (verified against the corpus, 2026-08-25): `used` is a real adjective
# («of persons; taken advantage of») AND the past tense of `use`. A resource asked for its parts of
# speech answers «adjective, and verb». The verb answer would mint `used.v` — a duplicate dimension
# of `use.v`, naming the same senses through another spelling.
USE_USED_LEXICON = ("use", "used", "tool")
USE_USED_GLOSSES = {
    "use": "to put a tool into service",
    "used": "of persons; taken advantage of",
    "tool": "an implement that is used to do work",
}
USE_USED_POS = {"use": ("n", "v"), "used": ("v", "a"), "tool": ("n", "v")}
USE_USED_LEMMAS = {("used", "v"): "use"}


def use_used_provider():
    return FixtureGlossProvider(
        lexicon=USE_USED_LEXICON,
        glosses=USE_USED_GLOSSES,
        glosses_all={},
        lemmas=USE_USED_LEMMAS,
        parts_of_speech=USE_USED_POS,
    )


# ------------------------------------------------------------------------------------------------
# a third world: the name that is not a word — the Captain's option C (T2b, 2026-08-25)
# ------------------------------------------------------------------------------------------------

# Apart from the sixteen-word world for the same reason `USE_USED` is: it exists to prove two things
# and folding it in would cost every hand-checked layer above its checkability.
#
# The shape is WordNet's own, verified against the corpus 2026-08-25. `or` has two readings and both
# are the spelling `OR` (Oregon, and a hospital's operating room); `me` has one and it is `ME`, the
# state of Maine; `be` has fourteen verb readings that are the English verb and one noun reading
# that is `Be`, beryllium's symbol. Two different outcomes have to follow from that, and this world
# holds both:
#
#   - `or` and `me` cease to be words. Not because a filter deleted them — because the resource has
#     no reading of those spellings that is a word, and the lexicon HERE still contains them, which
#     is the point: membership is the caller's, the refusal is the resource's.
#   - `be` stays a word and loses one dimension. `be.n` was beryllium wearing a copula's spelling.
NAME_ONLY_LEXICON = ("be", "exist", "state", "region", "or", "me")
NAME_ONLY_GLOSSES = {
    "be": "to exist in a state",
    "exist": "to be",
    # The token `or` sits in a real definition, where it always does — the junction that put Oregon
    # on more than half the base's rows.
    "state": "the condition of a region, or a place in the union",
    "region": "an area of a state",
    # Declared and never spoken: the provider returns "" for a word whose every reading is a name.
    # Written down anyway, because a fixture that simply omitted them would prove nothing.
    "or": "a state in the northwestern union",
    "me": "a state in the northeast",
}
NAME_ONLY_POS = {
    "be": ("n", "v"),
    "exist": ("v",),
    "state": ("n", "v"),
    "region": ("n",),
    "or": ("n",),
    "me": ("n",),
}
# Which of those readings are NAMES. The real adapter reads this off the lexicographer's capital;
# the fixture declares it, because a table has no orthography to consult.
NAME_ONLY_NAME_READINGS = {
    "be": ("n",),
    "or": ("n",),
    "me": ("n",),
}


def name_only_provider():
    return FixtureGlossProvider(
        lexicon=NAME_ONLY_LEXICON,
        glosses=NAME_ONLY_GLOSSES,
        glosses_all={},
        lemmas={},
        parts_of_speech=NAME_ONLY_POS,
        name_readings=NAME_ONLY_NAME_READINGS,
    )


# ------------------------------------------------------------------------------------------------
# the senses the sixteen-word world speaks — what curation quotes (T3)
# ------------------------------------------------------------------------------------------------

# Curation is about DEFINITIONS and quotes one of them verbatim, so it needs a resource that can be
# asked about a single sense rather than about a word. This world has exactly one sense per (word,
# POS) — which is all that is needed to prove the miner reads BOTH sides of a pair, mints the edge
# from whichever gloss speaks, and refuses a tautology.


def _fixture_sense(word: str, pos: str) -> str:
    """The sense-key convention, so the fixture's identifiers look like the resource's."""
    return f"{word}.{pos}.01"


# ------------------------------------------------------------------------------------------------
# a fourth world: the RELATIONS (T3) — R's own handcrafted shape
# ------------------------------------------------------------------------------------------------

# Apart from the sixteen-word world for the reason every other world here is: it exists to prove the
# cell walk, and folding it in would cost the layers above their checkability. Eleven dimensions,
# and every claim in it is one a person can verify by reading this table:
#
#   - `eat.v` and `devour.v` SHARE a synset (`eat.v.01`) — that is what synonymy is, and it is the
#     one relation the builder computes rather than asks for.
#   - `eat.v` also states `devour.v.02` as a troponym, so the pair has TWO relations and the cell
#     has to pick one and remember both (`via`). Synonymy answers first.
#   - `hungry.a` is the antonym of `full.a`: the one negative cell, and the sign is the point.
#   - `hot.a` names `temperature.n` as its attribute: a CROSS-POS cell, which is half the reason
#     the base splits by part of speech at all.
#   - `eat.v` entails `swallow.v` and `chew.v`, `kill.v` causes `die.v` — the reverse reads
#     (`entailed_by`, `caused_by`) are the builder's to derive, and weaker.
#   - `eat.v` states a hypernym NOBODY SPEAKS (`consume.v.01` is not a dimension here): a relation
#     pointing outside the base produces no cell, because inventing an axis for it would be
#     membership by side effect.
#   - `food.n` states nothing and nothing states it: a SILENT row, which is a finding rather than a
#     defect (at the real base, 318 dimensions are silent and 141 of them are adverbs).

RELATION_KEYS = (
    "chew.v",
    "devour.v",
    "die.v",
    "eat.v",
    "food.n",
    "full.a",
    "hot.a",
    "hungry.a",
    "kill.v",
    "swallow.v",
    "temperature.n",
)

RELATION_SENSES = {
    "chew.v": ("chew.v.01",),
    "devour.v": ("eat.v.01", "devour.v.02"),
    "die.v": ("die.v.01",),
    "eat.v": ("eat.v.01",),
    "food.n": ("food.n.01",),
    "full.a": ("full.a.01",),
    "hot.a": ("hot.a.01",),
    "hungry.a": ("hungry.a.01",),
    "kill.v": ("kill.v.01",),
    "swallow.v": ("swallow.v.01",),
    "temperature.n": ("temperature.n.01",),
}

RELATION_EDGES = {
    "eat.v": {
        "entails": frozenset({"swallow.v.01", "chew.v.01"}),
        "troponym": frozenset({"devour.v.02"}),
        "hypernym_1": frozenset({"consume.v.01"}),      # spoken by no dimension of this world
    },
    "kill.v": {"causes": frozenset({"die.v.01"})},
    "hungry.a": {"antonym": frozenset({"full.a.01"})},
    "full.a": {"antonym": frozenset({"hungry.a.01"})},
    "hot.a": {"attribute": frozenset({"temperature.n.01"})},
    "temperature.n": {"attribute": frozenset({"hot.a.01"})},
}


class FixtureRelationProvider:
    """The `RelationProvider` protocol over the world above. No nltk, no corpus, no opinions."""

    def __init__(self, senses=None, edges=None, relations=None):
        self._senses = dict(RELATION_SENSES if senses is None else senses)
        self._edges = dict(RELATION_EDGES if edges is None else edges)
        # The resource's whole vocabulary, whether or not this world happens to use every name.
        # A fixture that declared only what it uses would let a weight row for a real WordNet
        # relation look like a policy error.
        self._relations = tuple(WORDNET_RELATION_NAMES if relations is None else relations)

    def senses_of_key(self, key):
        return tuple(self._senses.get(key, ()))

    def relations_of_key(self, key):
        return dict(self._edges.get(key, {}))

    def relations(self):
        return self._relations


#: What `tk2.dictionary.wordnet.RELATIONS` says, restated here so the pure tests need no corpus.
#: A `wordnet`-marked test asserts the two agree — a fixture that had drifted from the resource
#: would be a fixture testing a matrix nobody builds.
WORDNET_RELATION_NAMES = (
    "antonym",
    "derivational",
    "entails",
    "causes",
    "troponym",
    "hyponym_1",
    "hypernym_1",
    "hypernym_2",
    "verb_group",
    "similar_to",
    "attribute",
    "also_see",
    "meronym",
    "holonym",
)
