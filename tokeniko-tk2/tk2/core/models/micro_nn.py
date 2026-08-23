"""The instinct middleware — one abstraction, many instances, split across two collections.

The split is the Captain's ruling of 2026-08-23, and it exists because the two halves of an instance
have opposite write-classes:

  - the DECLARATION (name · input schema · output kind · reward source) is architecture. Instances
    differ by declaration, never by stack (micro-nn req. 1), and a new instance arrives by
    deployment — so it is **logic (r)**, written only by migrations.
  - the WEIGHTS are trained online from the reward families (reqs 4, 5): «training moves rows, never
    code». The body writes them continuously — so they are **kb (rw)**.

One collection could not have held both without making the body able to rewrite its own
declarations, and «it just never does» is the remembered rule that the write-class seam exists to
replace with structure.

THE FENCE, structurally: neither table carries `Provenance`. A micro-nn ranks among already-legal
options only — never a verdict, never content, **no provenance ⇒ it can never mint or admit a
belief** (micro-nn req. 7). That is not a comment here, it is the absence of two fields.
"""

from enum import Enum
from typing import Annotated

from bunnet import Indexed
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from tk2.core.documents import KbDocument, LogicDocument
from tk2.core.mixins import EpochStamped, Timestamped, Updated


class OutputKind(str, Enum):
    """One shape: features in → a ranking or a scalar in [0,1] out; nothing else (micro-nn req. 2).

    An enum rather than an anatomy table, because unlike the heart's spheres this is not something a
    migration may extend: a third output kind would be a different middleware, not a bigger one. If
    the Captain reads the everything-is-rows seam as covering this too, it moves the same way the
    heart's anatomy did.
    """

    RANKING = "ranking"
    SCALAR = "scalar"


class MicroNnInstanceDoc(LogicDocument, Timestamped):
    """logic (r) — an instance's declaration is architecture-as-rows: it changes by deployment, never by him.

    `input_schema` is the ORDERED feature names, and the order is load-bearing: the weights row is a
    flat vector aligned to it, so a declaration that reorders its features invalidates every weight
    trained against the old order. That is why a schema change is a new epoch, not an edit.
    """

    name: Annotated[str, Indexed(unique=True)]
    input_schema: Annotated[list[str], Field(min_length=1)]
    output_kind: OutputKind

    #: Which reward family trains it — intellectual (an equation closing) or heart (micro-nn req. 5).
    #: A string rather than an enum because the reward SOURCES are sites, and the site roster grows.
    reward_source: str = Field(min_length=1)

    class Settings:
        name = "micro_nn_instances"


class MicroNnWeightsDoc(KbDocument, EpochStamped, Timestamped, Updated):
    """kb — weights are what training moves, and training is something he does to himself, online.

    One row per (instance, epoch). Keeping the epochs rather than overwriting one row is what makes
    «same features, same epoch, same output» checkable after the fact (micro-nn req. 8) — a claim of
    determinism you cannot reproduce is a claim you cannot test. Pruning old epochs is E5's to
    decide once there is a growth rate to look at.

    THE EPOCH'S SCOPE, per the T4 ruling recorded in `derived.py`: this counter belongs to the
    OWNING INSTANCE and to no other, and `instance` is what says so. There is deliberately no
    `epoch_layer` column — the row already names its scope, and a second naming could disagree.
    """

    #: The declaration's `name`. A name rather than an id: a weights row should stay readable beside
    #: its declaration in a probe, and the declaration's name is unique by index.
    instance: Annotated[str, Indexed()]
    weights: list[float]

    class Settings:
        name = "micro_nn_weights"
        indexes = [
            # One weight vector per instance per epoch — two would make «the weights at epoch N»
            # ambiguous, which is exactly the question req. 8 promises an answer to.
            IndexModel([("instance", ASCENDING), ("epoch", ASCENDING)], unique=True),
        ]
