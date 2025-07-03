from typing import List, Literal

from pydantic import BaseModel

from common.protocol.dto.file_info_message import FileInfoMessage
from common.protocol.enums.message_types import MessageType


class ClientFilesInfoMessage(BaseModel):
    type: Literal[MessageType.CLIENT_FILES_INFO] = MessageType.CLIENT_FILES_INFO
    client_id: str | None
    files: List[FileInfoMessage]
