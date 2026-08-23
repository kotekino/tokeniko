"""Test-only collection models.

Deliberately NOT the real ones: T4 defines those, and a datatier test that depended on them would
start failing for reasons that have nothing to do with the datatier. These exist to exercise one
write-class each, plus the timeseries case the ODM cannot delete from.
"""

from datetime import datetime
from typing import Any

from bunnet import Granularity, TimeSeriesConfig

from tk2.core import KbDocument, LogicDocument, ParamDocument, Timestamped


class TParam(ParamDocument):
    """A parameter store, shaped the way the r-cache expects one: key and value."""

    key: str
    value: Any = None

    class Settings:
        name = "t_params"


class TLogic(LogicDocument):
    """A hardwired-logic table — read-only, and not a key/value store."""

    name: str
    rule: str

    class Settings:
        name = "t_logic"


class TKb(KbDocument, Timestamped):
    """The writable tier."""

    text: str

    class Settings:
        name = "t_kb"


class TSeries(KbDocument):
    """A timeseries collection — the one the ODM's delete cannot touch."""

    ts: datetime
    value: float

    class Settings:
        name = "t_series"
        timeseries = TimeSeriesConfig(time_field="ts", granularity=Granularity.seconds)


ALL_MODELS = [TParam, TLogic, TKb, TSeries]
