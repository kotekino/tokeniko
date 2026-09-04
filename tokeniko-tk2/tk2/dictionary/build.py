"""THE BASE, ASSEMBLED — closure to dimensions to matrices, in one call with one policy.

Three steps that were three commands in the prototype (`tk2_subset` -> `tk2_matrix` -> `tk2_build2`,
each reading a config file and writing a sandbox collection the next one read back). They are one
function here for the reason the manifest exists: a base is ONE measurement under ONE declared
policy, and three commands that could each be run under a different config are three chances for a
build to be assembled out of parts nobody measured together.

Pure. The resource arrives as a provider — which is also what lets the whole assembly be tested on
the handcrafted worlds — and nothing here opens a database or writes a row. Storing the result is
`tools/build_dictionary.py`'s act, and it goes through the migration door.

D IS T4's, and it lands here: `build_base` will return it beside R, over the SAME dimensions, which
is the whole reason the key space is computed once and passed to both.
"""

from dataclasses import dataclass, field

from tk2.dictionary import closure, glosses, relations
from tk2.dictionary.closure import Digraph, SeedClosure
from tk2.dictionary.config import DictionaryConfig
from tk2.dictionary.matrix import Matrix


class PolicyIncomplete(ValueError):
    """The policy cannot build what it was asked to build.

    A policy version older than v3 declares no relation weights, and R without weights is not a
    smaller R — it is no matrix at all. Raised rather than defaulted, because a default here would
    be R's weights back in code with extra steps.
    """


@dataclass(frozen=True, slots=True)
class BaseBuild:
    """One base: the words the closure admitted, the dimensions they occupy, and the matrices."""

    words: tuple[str, ...]
    dimensions: tuple[str, ...]
    relational: Matrix
    #: The closure's own account of itself — where it stopped, what it could not find, and what
    #: sits one ring past the cut. Carried because a build's manifest is not only its counts.
    closure: SeedClosure = None
    graph_stats: dict = field(default_factory=dict)
    one_ring_past: tuple[str, ...] = ()

    def counts(self) -> dict[str, int]:
        """What the manifest records. Names chosen to stay meaningful when D joins them."""
        stats = self.relational.stats()
        return {
            "lexicon": self.graph_stats.get("nodes", 0),
            "closure_words": len(self.words),
            "keys": len(self.dimensions),
            "r_cells": stats["nonzero"],
            "r_negative": stats["negative"],
            "r_silent_rows": stats["silent_rows"],
            "one_ring_past": len(self.one_ring_past),
        }


def build_base(config: DictionaryConfig, provider, progress=None) -> BaseBuild:
    """THE build: the definition digraph, the seed closure, the dimensions, and R over them.

    `provider` answers both protocols — the gloss seam the closure reads through and the relation
    seam R is filled from. One object because it is one resource, and two objects would be two
    chances for the membership and the geometry to be measured against different WordNets.
    """
    if config.relations is None:
        raise PolicyIncomplete(
            "the policy declares no relation weights, so there is no R to build. Policy v3 "
            "(db/0006) is what declares them; a build against an older version is a build of a "
            "matrix nobody weighted."
        )

    _step(progress, "digraph")
    graph: Digraph = closure.build_digraph(provider, config.closure)
    graph_stats = closure.digraph_stats(graph)

    _step(progress, "closure")
    result = closure.seed_closure(graph, config.seeds, config.closure)
    dimensions = tuple(glosses.dimensions_of(result.words, provider))

    _step(progress, "relations")
    relational = relations.build(dimensions, provider, config.relations)

    return BaseBuild(
        words=result.words,
        dimensions=dimensions,
        relational=relational,
        closure=result,
        graph_stats=graph_stats,
        one_ring_past=result.one_ring_past(graph),
    )


def _step(progress, name: str) -> None:
    if progress is not None:
        progress(name)
