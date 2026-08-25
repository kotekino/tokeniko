"""THE COLLECTION REGISTER — every model the body knows, in one list.

`boot_datatier(ALL_MODELS)` registers these with the ODM and r-caches the r-class ones. A collection
that is not in this list does not exist as far as the body is concerned, which is the property that
makes the list worth keeping by hand: adding a table is a visible act.

Split by organ rather than gathered into one module, because each organ's tables share a reasoning
that is worth writing once at the top of its file — and because E6/E7 will grow these.

The r-tier holds three kinds of thing, and the difference is worth reading off this list: `params`
are TUNABLES (param), `heart_anatomy` and `micro_nn_instances` are ARCHITECTURE (logic) — the shape
of the organs, expressed as rows so that changing it is a migration rather than a new binary — and
`dictionary_policy` / `dictionary_bar` / `closed_classes` are CURATION (logic): authorized judgment
about the world, which the standing law of 2026-08-25 puts in rows precisely because it is never
finished.

Beside them, and NOT registered, sit the LEDGERS (`LEDGER_MODELS`, and `MigrationDoc` in its own
module): tables the body is the subject of rather than the reader of.
"""

from tk2.core.models.channel import ChannelRegisterDoc
from tk2.core.models.derived import DerivedPointDoc
from tk2.core.models.dictionary import (
    DictionaryBarDoc,
    DictionaryBuildDoc,
    DictionaryPolicyDoc,
)
from tk2.core.models.forecast import ForecastDoc, StakeStatus
from tk2.core.models.heart import (
    AnatomyIncoherent,
    EmotionalLogDoc,
    HeartAnatomy,
    HeartAnatomyDoc,
    HeartLevelDoc,
    HeartMoodDoc,
    HeartTargetDoc,
    HeartTemperamentDoc,
    UnknownPole,
)
from tk2.core.models.language import ClosedClassDoc
from tk2.core.models.micro_nn import MicroNnInstanceDoc, MicroNnWeightsDoc, OutputKind
from tk2.core.models.params import ParamDoc

#: The tunables. Read at boot, refreshed on the slow tick, written only by migrations.
PARAM_MODELS = [ParamDoc]

#: The architecture, as rows. Same read path as the tunables, different reason for existing: these
#: describe what the organs ARE, and a change to one is body growth (body req. 5). Since E1's T4b
#: the dictionary's CURATION joins them — the seeds, the closure cuts and the acceptance bar are
#: authorized judgment, and the standing law of 2026-08-25 puts authorized judgment in rows. The
#: closed classes join them for the same reason and one test further: a closed grammatical class is
#: a contingent fact about ONE language, so however finite it feels it is knowledge, not frame.
LOGIC_MODELS = [
    HeartAnatomyDoc,
    MicroNnInstanceDoc,
    DictionaryPolicyDoc,
    DictionaryBarDoc,
    ClosedClassDoc,
]

#: Everything the r-cache snapshots at boot.
R_MODELS = PARAM_MODELS + LOGIC_MODELS

#: The body's own state and biography. Written by the body, through the datatier.
KB_MODELS = [
    HeartLevelDoc,
    HeartTargetDoc,
    HeartMoodDoc,
    HeartTemperamentDoc,
    EmotionalLogDoc,
    ForecastDoc,
    DerivedPointDoc,
    MicroNnWeightsDoc,
    ChannelRegisterDoc,
]

#: The ledgers: written by a deploy or a build, never interpreted by the body on a tick. NOT in
#: `ALL_MODELS` for `MigrationDoc`'s reason — registering them would put growing append-only tables
#: into the r-cache, which snapshots every registered r-collection whole on every slow tick. They
#: are models so the migration writer can validate their rows, and `logic` so the write-class seam
#: covers every collection in the database with no exceptions.
LEDGER_MODELS = [DictionaryBuildDoc]

#: Everything, in the order a reader should meet it: the tunables, the architecture, then the organs.
ALL_MODELS = R_MODELS + KB_MODELS

__all__ = [
    "ALL_MODELS",
    "KB_MODELS",
    "LEDGER_MODELS",
    "LOGIC_MODELS",
    "PARAM_MODELS",
    "R_MODELS",
    "AnatomyIncoherent",
    "ChannelRegisterDoc",
    "ClosedClassDoc",
    "DerivedPointDoc",
    "DictionaryBarDoc",
    "DictionaryBuildDoc",
    "DictionaryPolicyDoc",
    "EmotionalLogDoc",
    "ForecastDoc",
    "HeartAnatomy",
    "HeartAnatomyDoc",
    "HeartLevelDoc",
    "HeartMoodDoc",
    "HeartTargetDoc",
    "HeartTemperamentDoc",
    "MicroNnInstanceDoc",
    "MicroNnWeightsDoc",
    "OutputKind",
    "ParamDoc",
    "StakeStatus",
    "UnknownPole",
]
