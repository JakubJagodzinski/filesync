import json
import socket

from common.config import MAX_BUFFER_SIZE_IN_BYTES
from common.logger.log_types import LogType
from common.logger.logger import log
from common.protocol.dto.server_status_message import ServerStatusMessage
from common.utils.json_parser import safe_parse

MODULE_NAME = "TCP_CONNECTOR"

SERVER_CONNECTION_TIMEOUT = 5


def establish_tcp_connection(server_ip: str, server_port: int) -> tuple[socket.socket | None, str | None]:
    log(
        LogType.INFO,
        f"[{MODULE_NAME}] Connecting to server at {server_ip}:{server_port}"
    )

    try:
        sock = socket.create_connection((server_ip, server_port), timeout=SERVER_CONNECTION_TIMEOUT)

        data = sock.recv(MAX_BUFFER_SIZE_IN_BYTES)

        decoded_data = data.decode()
        server_status_message_json = json.loads(decoded_data)

        server_status_message, error = safe_parse(ServerStatusMessage, server_status_message_json)
        if error:
            sock.close()
            return None, None

        return sock, server_status_message.status
    except (ConnectionRefusedError, TimeoutError) as e:
        log(
            LogType.ERROR,
            f"[{MODULE_NAME}] Server unavailable: {e}"
        )
    except Exception as e:
        log(
            LogType.ERROR,
            f"[{MODULE_NAME}] Failed to connect or communicate with server: {e}"
        )

    return None, None
