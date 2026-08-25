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
    ):
        self._lexicon = tuple(lexicon)
        self._glosses = dict(GLOSSES if glosses is None else glosses)
        self._glosses_all = dict(GLOSSES_ALL if glosses_all is None else glosses_all)
        self._lemmas = dict(LEMMA_EXCEPTIONS if lemmas is None else lemmas)
        self._stopwords = frozenset(stopwords)
        self._pos = dict(PARTS_OF_SPEECH if parts_of_speech is None else parts_of_speech)

    def lexicon(self):
        return self._lexicon

    def gloss(self, word, senses="primary"):
        if senses == "all" and word in self._glosses_all:
            return self._glosses_all[word]
        return self._glosses.get(word, "")

    def parts_of_speech(self, word):
        return self._pos.get(word, ())

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
