"""The channel registers — what he has learned about how to speak in each room.

«The channel register is learned kb rows — each channel's etiquette and jargon, fed by its own
traffic, learned via micro-nn; **never config**» (senses req. 3). That last clause is the whole
design: the difference between a register and a settings file is that nobody writes this by hand.
"""

from typing import Annotated, Any

from bunnet import Indexed
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from tk2.core.documents import KbDocument
from tk2.core.mixins import Timestamped, Updated


class ChannelRegisterDoc(KbDocument, Timestamped, Updated):
    """kb — learned from the channel's own traffic, never configured: that is exactly what makes it knowledge rather than settings.

    One row is one learned trait of one channel. `strength` is what makes the row learnABLE: a
    register entry that could only be present or absent could never be reinforced or worn down by
    the traffic that teaches it, and the micro-nn that feeds this table (micro-nn req. 6) emits a
    scalar, not a boolean.

    The register does not decide WHAT he says — a sense is dumb about content (senses req. 2). It
    shapes tone, and it is consulted beside heart deviation when the mouth colours a sentence.
    """

    channel: Annotated[str, Indexed()]
    trait: str
    value: Any = None
    strength: float = Field(ge=0.0, le=1.0)

    class Settings:
        name = "channel_registers"
        indexes = [
            # One value per (channel, trait): two rows for the same trait of the same channel would
            # be two answers where the mouth needs one.
            IndexModel([("channel", ASCENDING), ("trait", ASCENDING)], unique=True),
        ]
