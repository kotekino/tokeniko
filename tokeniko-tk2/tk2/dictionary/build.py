"""THE BASE, ASSEMBLED — closure to dimensions to matrices, in one call with one policy.

Three steps that were three commands in the prototype (`tk2_subset` -> `tk2_matrix` -> `tk2_build2`,
each reading a config file and writing a sandbox collection the next one read back). They are one
function here for the reason the manifest exists: a base is ONE measurement under ONE declared
policy, and three commands that could each be run under a different config are three chances for a
build to be assembled out of parts nobody measured together.

Pure. The resource arrives as a provider — which is also what lets the whole assembly be tested on
the handcrafted worlds — and nothing here opens a database or writes a row. Storing the result is
`tools/build_dictionary.py`'s act, and it goes through the migration door.

D LANDED HERE AT T4, beside R and over the SAME dimensions — which is the whole reason the key
space is computed once and passed to both. It is built when the policy declares a gloss walk and
skipped when it does not (v1–v5 declare none), and that absence is REPORTED rather than defaulted:
re-running the base T3 measured must stay possible, and a D built under parameters nobody declared
would be the standing law arriving by omission.
"""

from dataclasses import dataclass, field

from tk2.dictionary import closure, distribution, glosses, relations
from tk2.dictionary.closure import Digraph, SeedClosure
from tk2.dictionary.config import DictionaryConfig
from tk2.dictionary.matrix import Matrix


class PolicyIncomplete(ValueError):
    """The policy cannot build what it was asked to build.

    A policy version older than v3 declares no relation weights, and R without weights is not a
    smaller R — it is no matrix at all. Raised rather than defaulted, because a default here would
    be R's weights back in code with extra steps.
    """


class MiningLawMismatch(ValueError):
    """The resource is reading itself one way and the policy declares another.

    The single failure this guard exists for: a provider built under one lemma scope while the rows
    say the other produces a base that is perfectly well-formed, measurably different, and recorded
    under a fingerprint describing the reading it did NOT obey. Nothing downstream could ever notice.
    """


@dataclass(frozen=True, slots=True)
class BaseBuild:
    """One base: the words the closure admitted, the dimensions they occupy, and the matrices."""

    words: tuple[str, ...]
    dimensions: tuple[str, ...]
    relational: Matrix
    #: D over the same dimensions, or `None` when the policy declares no gloss walk.
    distributional: Matrix | None = None
    #: The closure's own account of itself — where it stopped, what it could not find, and what
    #: sits one ring past the cut. Carried because a build's manifest is not only its counts.
    closure: SeedClosure = None
    graph_stats: dict = field(default_factory=dict)
    one_ring_past: tuple[str, ...] = ()

    def counts(self) -> dict[str, int]:
        """What the manifest records. `DictionaryBuildDoc.counts` is a free dict for exactly this
        reason: D's numbers join R's without a migration against the shape."""
        stats = self.relational.stats()
        counted = {
            "lexicon": self.graph_stats.get("nodes", 0),
            "closure_words": len(self.words),
            "keys": len(self.dimensions),
            "r_cells": stats["nonzero"],
            "r_negative": stats["negative"],
            "r_silent_rows": stats["silent_rows"],
            "one_ring_past": len(self.one_ring_past),
        }
        if self.distributional is not None:
            d_stats = self.distributional.stats()
            counted |= {
                "d_cells": d_stats["nonzero"],
                "d_silent_rows": d_stats["silent_rows"],
            }
        return counted


def build_base(
    config: DictionaryConfig,
    provider,
    progress=None,
    antonym_symmetry: str | None = None,
    closed_forms=None,
) -> BaseBuild:
    """THE build: the definition digraph, the seed closure, the dimensions, and R over them.

    `provider` answers both protocols — the gloss seam the closure reads through and the relation
    seam R is filled from. One object because it is one resource, and two objects would be two
    chances for the membership and the geometry to be measured against different WordNets.

    `closed_forms` is the `closed_classes` table (migration 0004), injected because the dictionary
    package is pure and those are KB rows. D needs it whenever the policy reads structure as
    `compiled`; the refusal for a missing one lives in `distribution.vocabulary_of`, which is the
    only place that can tell whether it was needed.
    """
    if config.relations is None:
        raise PolicyIncomplete(
            "the policy declares no relation weights, so there is no R to build. Policy v3 "
            "(db/0006) is what declares them; a build against an older version is a build of a "
            "matrix nobody weighted."
        )

    # The provider is the resource; the scope is the POLICY telling it how to read itself. Asked of
    # a provider that can answer (`getattr`, because a fixture resource has no scope to have), and
    # refused when the two disagree — see `MiningLawMismatch`.
    declared = config.relations.lemma_scope
    reading = getattr(provider, "lemma_scope", None)
    if declared is not None and reading is not None and declared != reading:
        raise MiningLawMismatch(
            f"the policy declares lemma_scope {declared!r} and the provider is reading the resource "
            f"as {reading!r}. The base would be measured under one law and fingerprinted under the "
            f"other."
        )

    _step(progress, "digraph")
    graph: Digraph = closure.build_digraph(provider, config.closure)
    graph_stats = closure.digraph_stats(graph)

    _step(progress, "closure")
    result = closure.seed_closure(graph, config.seeds, config.closure)
    dimensions = tuple(glosses.dimensions_of(result.words, provider))

    _step(progress, "relations")
    # `antonym_symmetry` is the RUN's argument against the standing declaration, and `None` defers
    # to the policy — which is where the reading lives since v5 (`relations.resolve_symmetry`). A
    # run that names one is reproducing a non-standing reading and may not be STORED; the tool
    # refuses that at its own door.
    relational = relations.build(
        dimensions, provider, config.relations, antonym_symmetry=antonym_symmetry
    )

    # D over the SAME `dimensions` tuple — not a second key space computed the same way, the same
    # object — so the two matrices can be read cell for cell and the store's registry describes
    # both. A policy with no gloss walk builds no D rather than a default one; the tool says so.
    distributional = None
    if config.distribution is not None:
        _step(progress, "distribution")
        distributional = distribution.build(
            dimensions, provider, config.distribution, closed=closed_forms
        )

    return BaseBuild(
        words=result.words,
        dimensions=dimensions,
        relational=relational,
        distributional=distributional,
        closure=result,
        graph_stats=graph_stats,
        one_ring_past=result.one_ring_past(graph),
    )


def _step(progress, name: str) -> None:
    if progress is not None:
        progress(name)
