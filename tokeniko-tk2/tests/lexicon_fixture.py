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
