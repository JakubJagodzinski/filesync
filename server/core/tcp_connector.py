import socket
import threading

from common.logger.log_types import LogType
from common.logger.logger import log
from server.core.client_queue_handler import handle_client_queue

MODULE_NAME = "TCP_CONNECTOR"


def start_tcp_listener(tcp_port: int, sync_interval_in_sec: int) -> None:
    threading.Thread(
        target=tcp_listener,
        args=(
            tcp_port,
            sync_interval_in_sec
        ),
        daemon=True
    ).start()


def tcp_listener(tcp_port: int, sync_interval: int) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', tcp_port))
    sock.listen()

    log(
        LogType.INFO,
        f"[{MODULE_NAME}] Server is listening on port {tcp_port}"
    )

    while True:
        conn, client_address = sock.accept()
        log(
            LogType.SUCCESS,
            f"[{MODULE_NAME}] Connection received from {client_address}"
        )

        handle_client_queue(conn, client_address, sync_interval)
