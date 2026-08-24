"""THE DECLARED POLICY — everything tunable, in one place, hashed before it measures anything.

Tooling requirement 4, and the ruling that carries it: policy is declared BEFORE results, hashed
into the build manifest, and never edited after a measuring run. The prototype held the same idea in
module-level globals, which a `--depth 3` flag could quietly override without the manifest ever
seeing it. Here the policy is a VALUE: a run takes a config object, the manifest records that
object's fingerprint, and a variant is a different object rather than a mutated global.

What is declared here today is the CLOSURE policy and THE BAR. The relation weights (R) and the
gloss-overlap parameters (D) join them when their builders land — a build that has more policy has
a different fingerprint, which is the mechanism working, not a problem with it.

Requirement 12 is enforced in code, not by care: the bar's own words are seeds. Run r1 of the
prototype scored only 12 of 18 pairs because `kill`, `water` and `swallow` were never reached by the
seed closure — a subset that cannot score its own bar is not a test.
"""

import hashlib
import json
from dataclasses import asdict, dataclass, field, replace
from typing import Literal

from tk2.dictionary import keys

SenseMode = Literal["primary", "all"]
Verdict = Literal["NEAR", "FAR"]


# ------------------------------------------------------------------------------------------------
# the seeds — requirement 8: the sensitive families are in scope BY CONSTRUCTION, not by luck
# ------------------------------------------------------------------------------------------------

# Closure alone will happily return a clique of function words. These force the verbs that select
# actions into every subset, whatever the definition digraph happens to feel like doing.
SEEDS_VOLITIONAL = ("want", "must", "try", "decide", "choose", "need", "wish", "intend", "refuse")
SEEDS_MOTION = ("go", "come", "walk", "run", "enter", "arrive", "leave", "land", "fall", "move")
SEEDS_EFFECT = ("eat", "food", "hungry", "sleep", "tired", "bed", "drink", "thirsty")
SEEDS_IDENTITY = ("me", "you", "not", "negation", "be", "same", "different")

DECLARED_SEEDS = SEEDS_VOLITIONAL + SEEDS_MOTION + SEEDS_EFFECT + SEEDS_IDENTITY


# ------------------------------------------------------------------------------------------------
# THE BAR — declared before anything is built (requirement 12)
# ------------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class BarPair:
    """One expectation. `a` and `b` are keys or bare words; `why` is the sentence that justified the
    pair when it was declared, kept verbatim because a bar whose reasons are lost is a bar nobody can
    argue with."""

    a: str
    b: str
    verdict: Verdict
    why: str


# Carried from the review's declaration, unedited. Compounds (`land on the runway`) are layer two
# and NOT tested here; what IS tested is whether the single words carry enough to make the compound
# separable later.
BAR_PAIRS = (
    # --- the nearnesses we must NOT lose ---
    BarPair("eat.v", "food.n", "NEAR", "the Captain's line: eat and food are geometrically similar, do not lose it"),
    BarPair("drink.v", "water.n", "NEAR", "same shape, second witness"),
    BarPair("sleep.v", "bed.n", "NEAR", "the «land on your bed» -> sleep chain has to have a hook"),
    # --- the effect axis: what the Jurassic base cannot see ---
    BarPair("eat.v", "hungry.a", "NEAR", "the effect is already NAMEABLE in the 2925 — a wrong-VALUE test, not a missing-axis test"),
    BarPair("sleep.v", "tired.a", "NEAR", "same: effect nameable in base"),
    BarPair("kill.v", "die.v", "NEAR", "pure `causes` edge — unreachable without the unmined relations"),
    BarPair("eat.v", "swallow.v", "NEAR", "pure `entails` edge"),
    # --- POS collapse ---
    BarPair("cause.n", "cause.v", "NEAR", "similar, and the base cannot even ask the question today"),
    BarPair("land.n", "land.v", "FAR", "ground vs. touching down — the collapse that costs us"),
    BarPair("state.n", "state.v", "FAR", "condition vs. to say"),
    # --- the volitional family must be resolvable against each other ---
    BarPair("want.v", "need.v", "NEAR", "action selection reads these"),
    BarPair("want.v", "refuse.v", "FAR", "opposite volitional polarity"),
    # --- motion must not collapse into one blob ---
    BarPair("arrive.v", "leave.v", "FAR", "opposite endpoints of the same motion"),
    BarPair("walk.v", "run.v", "NEAR", "manner siblings"),
    BarPair("enter.v", "leave.v", "FAR", "opposite direction"),
    # --- controls: things that must stay far, or a denser matrix is just noise ---
    BarPair("eat.v", "arrive.v", "FAR", "control — density must not smear everything together"),
    BarPair("bed.n", "cause.n", "FAR", "control"),
    BarPair("tired.a", "runway.n", "FAR", "control"),
)


def bar_words(pairs=BAR_PAIRS) -> tuple[str, ...]:
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
    """

    max_depth: int = 2
    max_size: int = 400
    # Which senses of a word contribute its definition. `primary` = the first synset per POS (what
    # the Jurassic build used); `all` = every sense, denser and noisier.
    senses: SenseMode = "primary"
    # Extra seeds beyond the declared families and the bar's own words — a run's own argument, kept
    # separate from the standing declaration so the standing one stays readable.
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
    """The whole declared policy for one build. Hash it, record the hash, then measure."""

    closure: ClosurePolicy = field(default_factory=ClosurePolicy)
    declared_seeds: tuple[str, ...] = DECLARED_SEEDS
    bar: tuple[BarPair, ...] = BAR_PAIRS

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
            "closure": asdict(self.closure),
            "declared_seeds": list(self.declared_seeds),
            "seeds": list(self.seeds),
            "bar": [asdict(p) for p in self.bar],
        }

    def fingerprint(self) -> str:
        """sha256 over the canonical JSON, sorted keys, no whitespace slack. Two builds with the
        same fingerprint were measured under the same policy; that is the whole claim."""
        blob = json.dumps(self.as_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def with_closure(self, **changes) -> "DictionaryConfig":
        """A variant, for the runs that argue with the standing policy. It is a NEW config with a
        new fingerprint — which is the point: a depth-3 run cannot be mistaken for a depth-2 one."""
        return replace(self, closure=replace(self.closure, **changes))


# The standing policy. Named so a report can say which config it ran, and so a variant is visibly a
# variant of something.
STANDING = DictionaryConfig()
