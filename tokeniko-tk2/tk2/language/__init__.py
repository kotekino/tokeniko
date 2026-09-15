"""English's closed classes, as the station reads them.

The table is `language_closed_classes` — KB rows, never a code list (the standing law's first
clause). This package is the MECHANISM that reads them: matching a form in a token stream, and
choosing which JOB a form is doing when it holds more than one.
"""

from tk2.language.skeleton import (
    EMBEDDING_DEPS,
    UD_DEPS,
    UD_POS,
    Skeleton,
    SkeletonProvider,
    StanzaSkeletons,
    Word,
    bare,
    skeleton_from_conllu,
)
from tk2.language.closed import (
    ClosedClasses,
    Match,
    UD_DEP_TO_ROLE,
    UD_POS_TO_WORD_CLASS,
    standing_closed_classes,
)

__all__ = [
    "EMBEDDING_DEPS",
    "Skeleton",
    "SkeletonProvider",
    "StanzaSkeletons",
    "UD_DEPS",
    "UD_POS",
    "Word",
    "bare",
    "skeleton_from_conllu",
    "ClosedClasses",
    "Match",
    "UD_DEP_TO_ROLE",
    "UD_POS_TO_WORD_CLASS",
    "standing_closed_classes",
]
