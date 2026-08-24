"""tk2.dictionary — the two-matrix base, and the logic that builds it.

Pure logic. Nothing here opens a database and nothing here imports a lexical resource: providers are
injected, storage is somebody else's door. The runnable that puts a build into the body is
`tools/build_dictionary.py`, and it writes through the MigrationWriter like every other logic-class
row — the body reads the base, it never writes it.

  - `keys.py`     — THE key convention. Base keys are dimensions (`eat.v`); sense keys ride on them
                    (`eat.v.01`) and are not dimensions. One module, one truth.
  - `config.py`   — the declared policy: seeds, the depth cut, the bar. Hashed into the manifest
                    before it measures anything (tooling req. 4).
  - `glosses.py`  — the `GlossProvider` protocol and the reduction of a definition to lexicon words.
  - `closure.py`  — the definition digraph, its closed sets, the seed closure and its two cuts.
  - `wordnet.py`  — the real provider. Imports nltk, so it is NOT imported from here: the engine has
                    to stay runnable, and testable, with no corpus on the machine.

The architecture in one line, because forgetting it costs a billion cells: R and D are square over
BASE keys only — thousands, not the ~197k senses. The dictionary rides ON the base (tkzip req. 11).
There is never a senses x senses matrix.
"""

from tk2.dictionary import closure, config, glosses, keys
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
from tk2.dictionary.config import STANDING, BarPair, ClosurePolicy, DictionaryConfig
from tk2.dictionary.glosses import GlossProvider, definition_in_lexicon, lexicon_words_in
from tk2.dictionary.keys import InvalidKey, base_of, key_of, key_space, keys_for_word, split_key

__all__ = [
    "STANDING",
    "BarPair",
    "ClosurePolicy",
    "DictionaryConfig",
    "GlossProvider",
    "InvalidKey",
    "SeedClosure",
    "base_of",
    "build_digraph",
    "closed_sets",
    "closure",
    "config",
    "definition_in_lexicon",
    "digraph_stats",
    "glosses",
    "is_closed",
    "key_of",
    "key_space",
    "keys",
    "keys_for_word",
    "lexicon_words_in",
    "per_seed_cost",
    "seed_closure",
    "split_key",
    "strongly_connected_components",
]
