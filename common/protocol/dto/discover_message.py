from typing import Literal

from pydantic import BaseModel

from common.protocol.enums.message_types import MessageType


class DiscoverMessage(BaseModel):
    type: Literal[MessageType.DISCOVER] = MessageType.DISCOVER
