"""THE DECLARED POLICY — its SHAPE, and the fingerprint taken over it before it measures anything.

Tooling requirement 4, and the ruling that carries it: policy is declared BEFORE results, hashed
into the build manifest, and never edited after a measuring run. The prototype held the same idea in
module-level globals, which a `--depth 3` flag could quietly override without the manifest ever
seeing it. Here the policy is a VALUE: a run takes a config object, the manifest records that
object's fingerprint, and a variant is a different object rather than a mutated global.

**WHAT IS NO LONGER HERE, and why (T4b, the standing law of 2026-08-25).** This module used to
DECLARE the seeds, the closure cuts and the eighteen bar pairs. They are CURATION — «authorized
judgment, as complete as we can make it, grown generated-then-curated» — and «a category-2 set
stated in code is a defect even when its contents are correct». They now live in `dictionary_policy`
and `dictionary_bar`, arrive through `tk2.dictionary.policy.config_from_rows`, and are fingerprinted
into the manifest at both levels. What stays here is the SHAPE: what a closure cut IS, what a bar
pair IS, and how a policy is canonicalised and hashed. Shape is frame; content never is.

There is deliberately no `STANDING` any more, and no default for a single declared value. A default
in code is a second declaration of it, and the day the Captain moves `max_size` in a row, a bare
`ClosurePolicy()` elsewhere would still be answering 400 — with nothing to say the two disagree.
Every construction states its policy, or it reads it from the rows.

Requirement 12 is enforced in code, not by care: the bar's own words are seeds (`DictionaryConfig.
seeds`). Run r1 of the prototype scored only 12 of 18 pairs because `kill`, `water` and `swallow`
were never reached by the seed closure — a subset that cannot score its own bar is not a test.
"""

import hashlib
import json
from dataclasses import asdict, dataclass, replace
from typing import Literal

from tk2.dictionary import keys

SenseMode = Literal["primary", "all"]
Verdict = Literal["NEAR", "FAR"]


# ------------------------------------------------------------------------------------------------
# the reduction's law, dated
# ------------------------------------------------------------------------------------------------

# NOT a knob — there is no other setting, and the three decisions behind this date are law: gloss
# mining keeps every POS-aware reading of a token (requirement 21), the stop list yields to lexicon
# membership (the Captain's ruling), and a reading the resource knows only as a NAME is refused at
# membership and at mining alike (option C). It is hashed anyway, because the fingerprint's claim is
# that two builds sharing it were measured under the same policy, and on 2026-08-25 the mining law
# moved underneath a config that could not see it. A build from before and one from after must not
# be able to present the same hash. Bump when the reduction's law moves again.
#
# It stays in CODE while the seeds and the bar leave, and the standing law is what says so: this
# names the shape in which a gloss becomes edges at all, it moves only by changing the mining code,
# and a row could not move it. The seeds are content; this is the grammar the content is read under.
#
# The `.2` is not decoration: the law moved TWICE on the 25th (the stop-list ruling in the morning,
# the name refusal in the afternoon), and a bare date cannot separate two builds a day cannot
# separate either. A same-day amendment takes the next ordinal.
REDUCTION_RULES = "2026-08-25.2"


# ------------------------------------------------------------------------------------------------
# THE BAR — one expectation, declared before anything is built (requirement 12)
# ------------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class BarPair:
    """One expectation. `a` and `b` are keys or bare words; `why` is the sentence that justified the
    pair when it was declared, kept verbatim because a bar whose reasons are lost is a bar nobody can
    argue with.

    The pairs themselves are rows (`dictionary_bar`) since T4b; this is the shape they are read into.
    """

    a: str
    b: str
    verdict: Verdict
    why: str


def bar_words(pairs) -> tuple[str, ...]:
    """The words the bar names, POS suffix stripped, first-mention order preserved."""
    out: list[str] = []
    for pair in pairs:
        for side in (pair.a, pair.b):
            word = keys.word_of(side) if keys.is_base_key(side) else keys.normalize_word(side)
            if word not in out:
                out.append(word)
    return tuple(out)


# ------------------------------------------------------------------------------------------------
# the closure policy
# ------------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ClosurePolicy:
    """How far the seed closure is allowed to run before we call it exploded.

    `max_depth` is THE DEPTH CUT, and it is a parameter rather than a constant because the review
    left a lesson attached to it: at depth 2 the word `right` sat exactly one ring outside the
    subset — its namers entered on the last expanded layer and were never expanded themselves. That
    is an honest boundary, not a bug, but a boundary nobody can see is a boundary nobody can rule
    on, so the closure reports what lies one ring past the cut and this number is the thing the
    Captain moves when he disagrees with it.

    `max_size` is the second cut and answers a different question: the QM's stated counter that
    `closed` and `sensitive` would fight — function words close cheaply, `eat` pulls in the world.

    Both are REQUIRED. Their values are curation and live in rows (`kind: "closure"`); a default
    here would be a second, quieter declaration of a number the Captain moves in the db.
    """

    max_depth: int
    max_size: int
    # Which senses of a word contribute its definition. `primary` = the first synset per POS (what
    # the Jurassic build used); `all` = every sense, denser and noisier.
    senses: SenseMode
    # Extra seeds beyond the declared families and the bar's own words — a run's own argument, and
    # the one field here that is NOT a row: a standing declaration is what the rows hold, and this
    # is what a single run says against it. Empty by default because «no argument» is a real
    # default, not an undeclared value.
    extra_seeds: tuple[str, ...] = ()

    def __post_init__(self):
        if self.max_depth < 0:
            raise ValueError("max_depth is a number of rings, never negative")
        if self.max_size < 1:
            raise ValueError("max_size must leave room for at least one word")
        if self.senses not in ("primary", "all"):
            raise ValueError(f"unknown sense mode {self.senses!r}")


@dataclass(frozen=True, slots=True)
class DictionaryConfig:
    """The whole declared policy for one build. Hash it, record the hash, then measure.

    Assembled from rows by `tk2.dictionary.policy.config_from_rows`. Still a plain value object with
    no database anywhere near it — that is the seam: the rows are somebody else's door, and this is
    what the engine is handed.
    """

    closure: ClosurePolicy
    declared_seeds: tuple[str, ...]
    bar: tuple[BarPair, ...]

    @property
    def seeds(self) -> tuple[str, ...]:
        """The seeds that actually run: the declared families, then the bar's own words, then the
        run's extras — deduplicated, order preserved. Requirement 12 in code (see the module head)."""
        out: list[str] = []
        for word in (*self.declared_seeds, *bar_words(self.bar), *self.closure.extra_seeds):
            w = keys.normalize_word(word)
            if w not in out:
                out.append(w)
        return tuple(out)

    def as_dict(self) -> dict:
        """The canonical form the fingerprint is taken over — and the form the manifest stores, so a
        later reader can diff two builds' policies instead of trusting two hashes to differ."""
        return {
            "reduction_rules": REDUCTION_RULES,
            "closure": asdict(self.closure),
            "declared_seeds": list(self.declared_seeds),
            "seeds": list(self.seeds),
            "bar": [asdict(p) for p in self.bar],
        }

    def fingerprint(self) -> str:
        """sha256 over the canonical JSON, sorted keys, no whitespace slack. Two builds with the
        same fingerprint were measured under the same policy; that is the whole claim.

        NOTE what is deliberately NOT in here: the policy and bar ROW versions. This hashes the
        policy as the engine received it, and it must keep answering the same hash for the same
        values however they were assembled — that is what makes «the move to rows changed nothing»
        a checkable statement rather than a promise. Which rows a build read is recorded beside this
        in the manifest, by `tk2.dictionary.policy`'s own two fingerprints.
        """
        blob = json.dumps(self.as_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def with_closure(self, **changes) -> "DictionaryConfig":
        """A variant, for the runs that argue with the standing policy. It is a NEW config with a
        new fingerprint — which is the point: a depth-3 run cannot be mistaken for a depth-2 one."""
        return replace(self, closure=replace(self.closure, **changes))
