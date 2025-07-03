import socket

from common.logger.log_types import LogType
from common.logger.logger import log
from common.protocol.dto.server_status_message import ServerStatusMessage
from common.protocol.enums.server_status_types import ServerStatus

MODULE_NAME = "SERVER_STATUS_SENDER"


def send_server_status_message(conn: socket.socket, server_status: ServerStatus) -> None:
    status_message = ServerStatusMessage(status=server_status)
    conn.sendall(status_message.model_dump_json().encode())

    log(
        LogType.SUCCESS,
        f"[{MODULE_NAME}] Sent server status: {server_status}"
    )
