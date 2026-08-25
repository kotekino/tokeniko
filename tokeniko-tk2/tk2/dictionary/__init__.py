"""tk2.dictionary — the two-matrix base, and the logic that builds it.

Pure logic. Nothing here opens a database and nothing here imports a lexical resource: providers are
injected, storage is somebody else's door. The runnable that puts a build into the body is
`tools/build_dictionary.py`, and it writes through the MigrationWriter like every other logic-class
row — the body reads the base, it never writes it.

  - `keys.py`     — THE key convention. Base keys are dimensions (`eat.v`); sense keys ride on them
                    (`eat.v.01`) and are not dimensions. One module, one truth.
  - `config.py`   — the SHAPE of a policy and its fingerprint, hashed into the manifest before it
                    measures anything (tooling req. 4). The VALUES are rows since T4b.
  - `policy.py`   — rows in, a `DictionaryConfig` out: the curation seam, and the bar's offline
                    snapshot. Takes plain mappings, so the package still imports no database.
  - `glosses.py`  — the `GlossProvider` protocol, the reduction of a definition to lexicon words,
                    and the base-form rule that decides which POS may mint a dimension (req. 21).
  - `closure.py`  — the definition digraph, its closed sets, the seed closure and its two cuts.
  - `wordnet.py`  — the real provider. Imports nltk, so it is NOT imported from here: the engine has
                    to stay runnable, and testable, with no corpus on the machine.

The architecture in one line, because forgetting it costs a billion cells: R and D are square over
BASE keys only — thousands, not the ~197k senses. The dictionary rides ON the base (tkzip req. 11).
There is never a senses x senses matrix.
"""

from tk2.dictionary import closure, config, glosses, keys, policy
from tk2.dictionary.closure import (
    SeedClosure,
    build_digraph,
    closed_sets,
    digraph_stats,
    is_closed,
    per_seed_cost,
    seed_closure,
    strongly_connected_components,
)
from tk2.dictionary.config import BarPair, ClosurePolicy, DictionaryConfig
from tk2.dictionary.glosses import (
    GlossProvider,
    definition_in_lexicon,
    dimension_parts_of_speech,
    dimensions_of,
    lexicon_words_in,
)
from tk2.dictionary.keys import InvalidKey, base_of, key_of, key_space, keys_for_word, split_key
from tk2.dictionary.policy import (
    PolicyRowsInvalid,
    bar_fingerprint,
    bar_from_rows,
    bar_snapshot,
    bar_version,
    config_from_rows,
    manifest_row,
    policy_fingerprint,
    policy_version,
    snapshot_bar,
)

__all__ = [
    "BarPair",
    "ClosurePolicy",
    "DictionaryConfig",
    "GlossProvider",
    "InvalidKey",
    "PolicyRowsInvalid",
    "SeedClosure",
    "bar_fingerprint",
    "bar_from_rows",
    "bar_snapshot",
    "bar_version",
    "base_of",
    "build_digraph",
    "closed_sets",
    "closure",
    "config",
    "config_from_rows",
    "definition_in_lexicon",
    "digraph_stats",
    "dimension_parts_of_speech",
    "dimensions_of",
    "glosses",
    "is_closed",
    "key_of",
    "key_space",
    "keys",
    "keys_for_word",
    "lexicon_words_in",
    "manifest_row",
    "per_seed_cost",
    "policy",
    "policy_fingerprint",
    "policy_version",
    "seed_closure",
    "snapshot_bar",
    "split_key",
    "strongly_connected_components",
]
