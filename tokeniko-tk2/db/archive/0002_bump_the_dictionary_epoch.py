"""0002 — bump the derived layer's epoch from 0 to 1.

The E0 gate's second half. This migration exists to be applied WHILE THE BODY IS RUNNING: it changes
one parameter row, and the proof of the epic is that the living body notices on its next slow tick,
with nobody restarting anything.

The epoch is the right row to move for the demonstration because it is one the body genuinely reads
and reports every tick, so the change is visible in the log rather than inferred from behaviour. In
real use this migration is what a rebuild of the derived layer would ship with — every stored point
below the new number becomes stale, and the sleep phase re-derives them lazily.
"""

from tk2.core import constants
from tk2.core.models import ParamDoc

NEW_EPOCH = 1


def up(writer, db) -> None:
    writer.upsert(
        ParamDoc,
        {"key": constants.DICTIONARY_EPOCH_PARAM},
        {
            "key": constants.DICTIONARY_EPOCH_PARAM,
            "value": NEW_EPOCH,
            "note": "the derived layer's version; a derived point stamped below this is stale",
        },
    )
