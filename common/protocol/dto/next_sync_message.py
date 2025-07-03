from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from common.protocol.enums.message_types import MessageType


class NextSyncMessage(BaseModel):
    type: Literal[MessageType.NEXT_SYNC] = MessageType.NEXT_SYNC
    time: datetime
