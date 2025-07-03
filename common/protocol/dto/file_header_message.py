from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from common.protocol.enums.message_types import MessageType


class FileHeaderMessage(BaseModel):
    type: Literal[MessageType.FILE_HEADER] = MessageType.FILE_HEADER
    name: str
    path: str
    size: int
    last_mod: datetime
