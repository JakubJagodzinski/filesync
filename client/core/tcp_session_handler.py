import time
from datetime import datetime
from socket import socket

from client.config import REPO_BASE_PATH
from client.core.tcp_connector import establish_tcp_connection
from client.sync_handlers.file_info_sender import send_files_info, create_client_files_info_message
from client.sync_handlers.file_sender import send_files_to_server
from client.sync_handlers.next_sync_info_receiver import receive_next_sync_info_message
from client.sync_handlers.task_receiver import receive_tasks_from_server
from common.logger.log_types import LogType
from common.logger.logger import log
from common.protocol.enums.server_status_types import ServerStatus
from common.utils.repo_dir_finder import get_client_directory_path

MODULE_NAME = "TCP_SESSION_HANDLER"


def handle_tcp_session(sock: socket, client_id: str | None) -> None:
    log(
        LogType.INFO,
        f"[{MODULE_NAME}] Starting client session"
    )

    client_ip = sock.getpeername()[0]

    repo_path = get_client_directory_path(REPO_BASE_PATH, client_id, client_ip)

    client_files_info_message = create_client_files_info_message(repo_path, client_id)
    send_files_info(sock, client_files_info_message)

    tasks = receive_tasks_from_server(sock)
    if tasks is None:
        return

    send_files_to_server(
        sock,
        tasks,
        repo_path,
        client_files_info_message
    )

    next_sync_time = receive_next_sync_info_message(sock)
    if next_sync_time:
        sleep_until_next_sync(next_sync_time)


def sleep_until_next_sync(next_sync_time: datetime) -> None:
    delta = (next_sync_time - datetime.now()).total_seconds()
    sleep_time = max(0.0, delta)
    log(
        LogType.INFO,
        f"[{MODULE_NAME}] Sleeping for {sleep_time:.2f} seconds until next sync..."
    )
    time.sleep(sleep_time)


def start_tcp_session(server_ip, server_port, client_id: str | None) -> bool:
    sock, status = establish_tcp_connection(server_ip, server_port)

    if not sock or not status:
        return False

    with sock:
        log(
            LogType.INFO,
            f"[{MODULE_NAME}] Server status: {status}"
        )

        if status == ServerStatus.READY:
            handle_tcp_session(sock, client_id)
            return True
        else:
            return False
