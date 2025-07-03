import json
import socket
import threading
import time
from queue import Queue

from pydantic import ValidationError

from common.config import MAX_BUFFER_SIZE_IN_BYTES
from common.logger.log_types import LogType
from common.logger.logger import log
from common.protocol.dto.client_files_info_message import ClientFilesInfoMessage
from common.protocol.enums.server_status_types import ServerStatus
from common.utils.repo_dir_finder import get_client_directory_path
from server.config import REPO_BASE_PATH
from server.repo_utils.repo_synchronizer import synchronize_server_repo
from server.sync_handlers.next_sync_info_sender import send_next_sync_info_message
from server.sync_handlers.server_status_sender import send_server_status_message
from server.sync_handlers.task_sender import prepare_tasks_for_client, send_tasks_to_client

MODULE_NAME = "TCP_SESSION_HANDLER"


def handle_tcp_session(conn, client_address, sync_interval: int, active_client_ref, client_queue: Queue, lock) -> None:
    from server.core.client_queue_handler import resume_next_client

    log(
        LogType.INFO,
        f"[{MODULE_NAME}] Starting session for client at {client_address}"
    )

    try:
        process_client_sync(conn, client_address, sync_interval)
    except Exception as e:
        log(
            LogType.ERROR,
            f"[{MODULE_NAME}] Error: {e}"
        )
    finally:
        log(
            LogType.INFO,
            f"[{MODULE_NAME}] Closing connection with {client_address}"
        )

        try:
            conn.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

        conn.close()

        with lock:
            active_client_ref[0] = None
            resume_next_client(
                sync_interval,
                active_client_ref,
                client_queue,
                lock
            )


def process_client_sync(conn, client_address, sync_interval: int) -> None:
    start_time = time.perf_counter()

    try:
        received_data = conn.recv(MAX_BUFFER_SIZE_IN_BYTES)
        decoded_json = json.loads(received_data.decode())
        client_files_info = ClientFilesInfoMessage.model_validate(decoded_json)
    except (json.JSONDecodeError, UnicodeDecodeError, ValidationError) as e:
        log(
            LogType.ERROR,
            f"[{MODULE_NAME}] Invalid data from client {client_address}: {e}"
        )
        return

    log(
        LogType.INFO,
        f"[{MODULE_NAME}] Handling client {client_files_info.client_id} from {client_address}"
    )

    client_ip, client_port = client_address
    client_repo_path = get_client_directory_path(
        REPO_BASE_PATH,
        client_files_info.client_id,
        client_ip
    )

    tasks = prepare_tasks_for_client(client_files_info.files, client_repo_path)
    send_tasks_to_client(
        conn,
        tasks,
        client_files_info.client_id
    )

    received_files, deleted_files = synchronize_server_repo(
        conn,
        len(tasks.files_to_send),
        client_files_info.files,
        client_repo_path
    )

    send_next_sync_info_message(conn, sync_interval)

    end_time = time.perf_counter()
    duration_ms = int((end_time - start_time) * 1_000)

    log(
        LogType.SUCCESS,
        f"[{MODULE_NAME}] Sync completed in {duration_ms} ms | "f"received: {received_files} | deleted: {deleted_files}"
    )


def start_tcp_session(conn: socket.socket, client_address: tuple[str, int], sync_interval: int,
                      active_client_ref, client_queue: Queue, lock: threading.Lock) -> None:
    send_server_status_message(conn, ServerStatus.READY)
    active_client_ref[0] = conn

    threading.Thread(
        target=handle_tcp_session,
        args=(
            conn,
            client_address,
            sync_interval,
            active_client_ref,
            client_queue,
            lock
        ),
        daemon=True
    ).start()
