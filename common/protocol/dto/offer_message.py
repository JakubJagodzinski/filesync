from typing import Literal

from pydantic import BaseModel

from common.protocol.enums.message_types import MessageType


class OfferMessage(BaseModel):
    type: Literal[MessageType.OFFER] = MessageType.OFFER
    port: int
