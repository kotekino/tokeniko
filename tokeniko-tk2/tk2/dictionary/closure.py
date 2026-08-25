"""THE CLOSURE ENGINE — the definition digraph, its closed sets, and the seed closure's two cuts.

A set S is CLOSED when defs(S) is a subset of S: every word S's definitions name is already in S.
The minimal closed sets are the SINK components of the definition digraph, and this module finds
them (Tarjan, iterative — the full lexicon is not a place to spend the recursion limit).

Beside that it runs the closure from the sensitive seeds, because requirement 8 puts the volitional
and motion verbs in scope BY CONSTRUCTION and closure alone would happily return a clique of
function words. The two are computed separately and reported separately so the fight between
«closed» and «sensitive» is MEASURED rather than assumed.

Everything here is a pure function over a graph or over an injected `GlossProvider`. No resource, no
database, no policy of its own — the policy arrives as a `ClosurePolicy`, and since T4b it arrives
REQUIRED. It used to be optional with a default-constructed fallback, which was a policy of its own
wearing a keyword argument's clothes: a run that forgot to pass one measured under numbers nobody
declared and the manifest could not have known.

THE DEPTH CUT AND ITS RING. `seed_closure` expands `max_depth` times, so the LAST layer it admits is
never itself expanded. That is what the review's `right` was: `left` entered on the last layer, and
`right` — named only by `left` — sat one ring outside a subset that already contained the word that
names it. An honest boundary, but an invisible one. So the result carries `unexpanded` (the layer
whose namers were never followed) and `one_ring_past` (exactly what they name and the subset does
not have), which turns the cut into something the Captain can look at and rule on.
"""

from dataclasses import dataclass

from tk2.dictionary.config import ClosurePolicy
from tk2.dictionary.glosses import GlossProvider, definition_in_lexicon

Digraph = dict[str, set[str]]


# ------------------------------------------------------------------------------------------------
# the definition digraph:  word --> the lexicon words its definition is written with
# ------------------------------------------------------------------------------------------------


def build_digraph(
    provider: GlossProvider,
    policy: ClosurePolicy,
    progress=None,
) -> Digraph:
    """One node per lexicon word, edges to the lexicon words its definition names.

    Built over WORDS, not over POS-split keys, and the distinction is load-bearing: the closure
    decides MEMBERSHIP (which words the base is made of), while the POS split decides DIMENSIONS
    (how many axes each member occupies). A word is in or out as a word; `key_space` then expands
    the survivors. Reducing a gloss per-POS would ask a question the gloss does not answer — a
    definition names words, and which sense of them it means is precisely what the geometry is being
    built to decide.
    """
    words = tuple(provider.lexicon())
    lexicon = frozenset(words)
    stops = provider.stopwords()
    graph: Digraph = {}
    for i, word in enumerate(words, 1):
        graph[word] = definition_in_lexicon(word, lexicon, provider, policy.senses, stops)
        if progress is not None:
            progress(i, len(words))
    return graph


def digraph_stats(graph: Digraph) -> dict:
    """The three numbers that say whether a reduction worked at all. `silent` is the honest one: a
    definition that names NO lexicon word can never belong to a closed set, and a lexicon where that
    count is large is a lexicon whose definitions are written in some other vocabulary."""
    sizes = [len(v) for v in graph.values()]
    return {
        "nodes": len(graph),
        "edges": sum(sizes),
        "mean_out_degree": (sum(sizes) / len(sizes)) if sizes else 0.0,
        "silent": sum(1 for v in graph.values() if not v),
    }


# ------------------------------------------------------------------------------------------------
# sink SCCs = the minimal closed sets
# ------------------------------------------------------------------------------------------------


def strongly_connected_components(graph: Digraph) -> list[list[str]]:
    """Tarjan, iterative and deterministic: neighbours are walked in sorted order, so the same graph
    always yields the same components in the same order. Recursion would be shorter and would blow
    the stack somewhere past the tenth thousand definition."""
    index_of: dict[str, int] = {}
    low: dict[str, int] = {}
    on_stack: dict[str, bool] = {}
    stack: list[str] = []
    result: list[list[str]] = []
    counter = 0

    for root in graph:
        if root in index_of:
            continue
        work = [(root, iter(sorted(graph.get(root, ()))))]
        index_of[root] = low[root] = counter
        counter += 1
        stack.append(root)
        on_stack[root] = True

        while work:
            node, it = work[-1]
            advanced = False
            for nxt in it:
                if nxt not in graph:
                    continue
                if nxt not in index_of:
                    index_of[nxt] = low[nxt] = counter
                    counter += 1
                    stack.append(nxt)
                    on_stack[nxt] = True
                    work.append((nxt, iter(sorted(graph.get(nxt, ())))))
                    advanced = True
                    break
                if on_stack.get(nxt):
                    low[node] = min(low[node], index_of[nxt])
            if advanced:
                continue

            work.pop()
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[node])
            if low[node] == index_of[node]:
                comp = []
                while True:
                    m = stack.pop()
                    on_stack[m] = False
                    comp.append(m)
                    if m == node:
                        break
                result.append(sorted(comp))
    return result


def is_closed(graph: Digraph, words) -> bool:
    """defs(S) subset-of S — the Captain's definition, asked of any set at all.

    Words the graph does not know are not edges and cannot break closure; a word outside the lexicon
    was never a node to leave to.
    """
    inside = set(words)
    return all(target in inside for w in inside for target in graph.get(w, ()) if target in graph)


def closed_sets(graph: Digraph) -> list[list[str]]:
    """The MINIMAL closed sets: components no edge leaves — sinks in the condensation.

    Note what this returns and what it does not. The Captain's example set {me, not, you, negation}
    is closed, but it is not minimal: `me` and `you` reach `not` without `not` reaching back, so the
    minimal closed set inside it is {not, negation}. Both facts are true and the difference matters
    when choosing a subset — ask `is_closed` about a set you propose, ask this for the floor.
    """
    comps = strongly_connected_components(graph)
    return sorted((comp for comp in comps if is_closed(graph, comp)), key=lambda c: (len(c), c))


# ------------------------------------------------------------------------------------------------
# the seed closure — how far does «eat» reach before it swallows the dictionary?
# ------------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SeedClosure:
    """What a closure run produced, including where it stopped and why."""

    words: tuple[str, ...]
    # One entry per ring: layer 0 is the seeds themselves. The last entry was ADMITTED and never
    # EXPANDED — see `unexpanded`.
    layers: tuple[tuple[str, ...], ...] = ()
    # Seeds the lexicon does not contain. Reported, never silently dropped: requirement 15 says
    # membership is a defect too, and a seed that is not a word is the first place to look.
    missing: tuple[str, ...] = ()
    # Why the walk stopped: "exhausted" (nothing new to add — the closure is genuinely closed),
    # "depth" (the ring cut), or "size" (the cap).
    stopped: str = "exhausted"

    @property
    def unexpanded(self) -> tuple[str, ...]:
        """The last admitted layer — in the subset, but their own definitions were never followed.
        Empty when the walk exhausted itself, because then there was nothing left to follow."""
        if self.stopped == "exhausted" or not self.layers:
            return ()
        return self.layers[-1]

    def one_ring_past(self, graph: Digraph) -> tuple[str, ...]:
        """THE `right` INVENTORY: what the unexpanded layer names that the subset does not have.

        This is the cut made visible. Every word here is one definition away from a word that is
        already in — the review found `right` sitting exactly here while `left` was inside, and
        nobody would have seen it without looking at the picture afterwards.
        """
        inside = set(self.words)
        out: set[str] = set()
        for word in self.unexpanded:
            out |= {t for t in graph.get(word, ()) if t not in inside}
        return tuple(sorted(out))


def seed_closure(graph: Digraph, seeds, policy: ClosurePolicy) -> SeedClosure:
    """Expand the seeds through the definition digraph, `max_depth` rings, capped at `max_size`.

    The size cap admits a whole ring or none of it. Trimming a ring alphabetically would make
    membership depend on spelling, which is the kind of arbitrary nobody can defend later; a run
    that hits the cap says so (`stopped == "size"`) and the answer is a different policy, not a
    smaller alphabet.
    """
    seeds = list(dict.fromkeys(seeds))
    frontier = {s for s in seeds if s in graph}
    missing = tuple(s for s in seeds if s not in graph)
    seen = set(frontier)
    layers: list[tuple[str, ...]] = [tuple(sorted(frontier))]
    stopped = "exhausted"

    for _ in range(policy.max_depth):
        nxt: set[str] = set()
        for word in frontier:
            nxt |= graph.get(word, set())
        nxt -= seen
        if not nxt:
            stopped = "exhausted"
            break
        seen |= nxt
        layers.append(tuple(sorted(nxt)))
        frontier = nxt
        if len(seen) > policy.max_size:
            stopped = "size"
            break
    else:
        # The rings ran out first. Whether that CUT anything is a separate question — a policy that
        # happens to be deep enough is not a policy that stopped short, and `unexpanded` must not
        # accuse it of one. (`max_depth == 0` lands here too, with the seeds as the frontier.)
        stopped = "depth" if _has_unfollowed_edges(graph, frontier, seen) else "exhausted"

    return SeedClosure(
        words=tuple(sorted(seen)),
        layers=tuple(layers),
        missing=missing,
        stopped=stopped,
    )


def _has_unfollowed_edges(graph: Digraph, frontier, seen) -> bool:
    """Would one more ring have added anything? The difference between «we stopped» and «there was
    nothing left», which `stopped` must not blur."""
    return any(t not in seen for w in frontier for t in graph.get(w, ()))


def per_seed_cost(graph: Digraph, seeds, policy: ClosurePolicy) -> list[tuple[str, int | None]]:
    """The QM's counter, quantified per seed: function words close cheaply, `eat` pulls in the world.

    `None` means the seed is not a lexicon word at all — a membership question, not a cost one.
    """
    uncapped = ClosurePolicy(max_depth=policy.max_depth, max_size=10_000, senses=policy.senses)
    rows: list[tuple[str, int | None]] = []
    for seed in seeds:
        if seed not in graph:
            rows.append((seed, None))
            continue
        rows.append((seed, len(seed_closure(graph, [seed], uncapped).words)))
    return rows
