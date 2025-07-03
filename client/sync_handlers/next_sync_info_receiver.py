import json
import socket
from datetime import datetime
from typing import Optional

from common.config import MAX_BUFFER_SIZE_IN_BYTES
from common.logger.log_types import LogType
from common.logger.logger import log
from common.protocol.dto.next_sync_message import NextSyncMessage
from common.utils.json_parser import safe_parse

MODULE_NAME = "NEXT_SYNC_INFO_RECEIVER"


def receive_next_sync_info_message(sock: socket) -> Optional[datetime]:
    try:
        data = sock.recv(MAX_BUFFER_SIZE_IN_BYTES)

        decoded_data = data.decode()
        next_sync_message_json = json.loads(decoded_data)

        next_sync_message, error = safe_parse(NextSyncMessage, next_sync_message_json)
        if error:
            return None

        log(
            LogType.SUCCESS,
            f"[{MODULE_NAME}] Next sync time received: {next_sync_message.time.isoformat()}"
        )
        return next_sync_message.time

    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        log(
            LogType.ERROR,
            f"[{MODULE_NAME}] Failed to decode NEXT_SYNC message: {e}"
        )
        return None
