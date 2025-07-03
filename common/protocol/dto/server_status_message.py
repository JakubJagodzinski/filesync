from typing import Literal

from pydantic import BaseModel

from common.protocol.enums.message_types import MessageType
from common.protocol.enums.server_status_types import ServerStatus


class ServerStatusMessage(BaseModel):
    type: Literal[MessageType.SERVER_STATUS] = MessageType.SERVER_STATUS
    status: ServerStatus
