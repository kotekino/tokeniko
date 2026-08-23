"""THE COLLECTION REGISTER — every model the body knows, in one list.

`boot_datatier(ALL_MODELS)` registers these with the ODM and r-caches the r-class ones. A collection
that is not in this list does not exist as far as the body is concerned, which is the property that
makes the list worth keeping by hand: adding a table is a visible act.

Split by organ rather than gathered into one module, because each organ's tables share a reasoning
that is worth writing once at the top of its file — and because E6/E7 will grow these.

The r-tier holds three kinds of thing, and the difference is worth reading off this list: `params`
are TUNABLES (param), while `heart_anatomy` and `micro_nn_instances` are ARCHITECTURE (logic) — the
shape of the organs, expressed as rows so that changing it is a migration rather than a new binary.
"""

from tk2.core.models.channel import ChannelRegisterDoc
from tk2.core.models.derived import DerivedPointDoc
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
from tk2.core.models.micro_nn import MicroNnInstanceDoc, MicroNnWeightsDoc, OutputKind
from tk2.core.models.params import ParamDoc

#: The tunables. Read at boot, refreshed on the slow tick, written only by migrations.
PARAM_MODELS = [ParamDoc]

#: The architecture, as rows. Same read path as the tunables, different reason for existing: these
#: describe what the organs ARE, and a change to one is body growth (body req. 5).
LOGIC_MODELS = [HeartAnatomyDoc, MicroNnInstanceDoc]

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

#: Everything, in the order a reader should meet it: the tunables, the architecture, then the organs.
ALL_MODELS = R_MODELS + KB_MODELS

__all__ = [
    "ALL_MODELS",
    "KB_MODELS",
    "LOGIC_MODELS",
    "PARAM_MODELS",
    "R_MODELS",
    "AnatomyIncoherent",
    "ChannelRegisterDoc",
    "DerivedPointDoc",
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
