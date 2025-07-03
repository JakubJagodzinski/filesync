import socket
import threading
from queue import Queue

from common.logger.log_types import LogType
from common.logger.logger import log
from common.protocol.enums.server_status_types import ServerStatus
from server.core.tcp_session_handler import start_tcp_session
from server.sync_handlers.server_status_sender import send_server_status_message

MODULE_NAME = "CLIENT_QUEUE_HANDLER"


def handle_client_queue(conn: socket.socket, client_address: (str, int), sync_interval: int) -> None:
    client_queue = Queue()
    active_client_lock = threading.Lock()
    active_client: list[socket.socket | None] = [None]

    with active_client_lock:
        if active_client[0] is None:
            start_tcp_session(
                conn,
                client_address,
                sync_interval,
                active_client,
                client_queue,
                active_client_lock
            )
        else:
            send_server_status_message(conn, ServerStatus.BUSY)

            client_queue.put((conn, client_address))
            log(
                LogType.INFO,
                f"[{MODULE_NAME}] Client queued: {client_address}"
            )


def resume_next_client(sync_interval, active_client_ref, client_queue: Queue, lock):
    if not client_queue.empty():
        next_conn, next_addr = client_queue.get()
        try:
            start_tcp_session(
                next_conn,
                next_addr,
                sync_interval,
                active_client_ref,
                client_queue,
                lock
            )
        except Exception as e:
            log(
                LogType.ERROR,
                f"[{MODULE_NAME}] Error while resuming next client: {e}"
            )

            try:
                next_conn.close()
            except Exception as e:
                log(
                    LogType.ERROR,
                    f"[{MODULE_NAME}] Unexpected error: {e}"
                )
