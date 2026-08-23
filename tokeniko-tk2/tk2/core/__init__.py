"""tk2.core — the shape of things.

Pydantic models are the single source of shape (data-modeling req. 6); a dimension change is a
migration, never a cast. What lives here:

  - `constants.py`     — the names the body cannot look up, because it needs them to look anything up.
  - `write_class.py`   — kb (rw) · param (r) · logic (r): the everything-is-rows seam as a schema
                         property, plus the refusal the datatier raises.
  - `documents.py`     — the three document bases. Inheriting one IS the declaration.
  - `mixins.py`        — the field conventions defined once: provenance (parents + producer),
                         the epoch stamp (layer version), the timestamps (int seconds, UTC).
  - `models/`          — the collection register, split by organ. Imported from `tk2.core.models`
                         and NOT re-exported here: the models import `constants` off this package,
                         and pulling them into this file would close that loop.

Nothing in here talks to Mongo. The tier that moves the rows is `tk2.datatier`.
"""

from tk2.core.documents import (
    KbDocument,
    LogicDocument,
    ParamDocument,
    TkDocument,
    assert_writable,
)
from tk2.core.mixins import (
    EpochStamped,
    Parent,
    Provenance,
    Timestamped,
    Updated,
    now_seconds,
)
from tk2.core.write_class import WriteClass, WriteClassViolation

__all__ = [
    "EpochStamped",
    "KbDocument",
    "LogicDocument",
    "Parent",
    "ParamDocument",
    "Provenance",
    "Timestamped",
    "TkDocument",
    "Updated",
    "WriteClass",
    "WriteClassViolation",
    "assert_writable",
    "now_seconds",
]
