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

  3. THE COLLISION, requirement 21, staged and not yet fixed. `go`'s definition says «as when one has
     left» — `left` is *leave*'s participle, and the engine mints `left` the DIRECTION from it,
     because the surface form is itself a lexicon word and the surface form is tried first. The
     fixture's lemma table already knows `left -> leave`; nothing consults it yet. When the POS-aware
     repair lands, `left` stops entering here and `right` stops being one ring past anything — the
     tests that pin today's behaviour are named for the defect so they are found and rewritten
     rather than deleted in confusion.

One divergence from the real adapter, stated out loud because it is a finding and not a convenience:
this fixture's stop list does NOT contain `me`, `you` or `not`, and nltk's English stop list does.
On the real resource the Captain's own closure example is therefore unreachable — the function words
that make it work are filtered out before they can be matched.
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

# What morphy would answer. Deliberately sparse: only the forms the glosses actually contain.
LEMMAS = {
    "says": ("say",),
    "moves": ("move",),
    "provides": ("provide",),
    "objects": ("object",),
    "labors": ("labor",),
    "left": ("leave",),      # requirement 21's whole story, in one entry nothing reads yet
}

# The fixture's own stop list — see the module head for why it is not nltk's.
STOPWORDS = frozenset(
    {
        "a", "an", "the", "to", "in", "of", "at", "for", "from", "over", "and", "as",
        "when", "where", "which", "that", "who", "one", "has", "have", "may", "is", "was",
    }
)

# Every word's parts of speech, so the key convention can be exercised without a corpus.
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

    def __init__(self, lexicon=LEXICON, glosses=None, glosses_all=None, lemmas=None, stopwords=STOPWORDS):
        self._lexicon = tuple(lexicon)
        self._glosses = dict(GLOSSES if glosses is None else glosses)
        self._glosses_all = dict(GLOSSES_ALL if glosses_all is None else glosses_all)
        self._lemmas = dict(LEMMAS if lemmas is None else lemmas)
        self._stopwords = frozenset(stopwords)

    def lexicon(self):
        return self._lexicon

    def gloss(self, word, senses="primary"):
        if senses == "all" and word in self._glosses_all:
            return self._glosses_all[word]
        return self._glosses.get(word, "")

    def parts_of_speech(self, word):
        return PARTS_OF_SPEECH.get(word, ())

    def lemmas(self, token):
        return self._lemmas.get(token, ())

    def stopwords(self):
        return self._stopwords
