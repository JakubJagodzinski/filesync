import json
from typing import Optional

from _socket import SocketType

from common.config import MAX_BUFFER_SIZE_IN_BYTES
from common.logger.log_types import LogType
from common.logger.logger import log
from common.protocol.dto.tasks_message import TasksMessage
from common.utils.json_parser import safe_parse

MODULE_NAME = "TASK_RECEIVER"


def receive_tasks_from_server(sock: SocketType) -> Optional[TasksMessage]:
    try:
        data = sock.recv(MAX_BUFFER_SIZE_IN_BYTES)

        decoded_data = data.decode()
        tasks_message_json = json.loads(decoded_data)

        tasks_message, error = safe_parse(TasksMessage, tasks_message_json)
        if error:
            return None

        log(
            LogType.SUCCESS,
            f"[{MODULE_NAME}] Received TASKS: {len(tasks_message.files_to_send)} files to send."
        )
        return tasks_message
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        log(
            LogType.ERROR,
            f"[{MODULE_NAME}] Failed to decode TASKS message: {e}"
        )
        return None
