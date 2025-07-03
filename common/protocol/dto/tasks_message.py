from typing import List, Literal

from pydantic import BaseModel

from common.protocol.enums.message_types import MessageType


class TasksMessage(BaseModel):
    type: Literal[MessageType.TASKS] = MessageType.TASKS
    files_to_send: List[str]
