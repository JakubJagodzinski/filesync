import socket
from datetime import datetime
from pathlib import Path
from typing import Any

from common.config import MAX_BUFFER_SIZE_IN_BYTES
from common.logger.log_types import LogType
from common.logger.logger import log
from common.protocol.dto.file_header_message import FileHeaderMessage

MODULE_NAME = "FILE_SENDER"


def send_file_header(conn: socket, full_path: Path, file_info: Any) -> None:
    header = FileHeaderMessage(
        name=file_info.name,
        path=file_info.path,
        size=full_path.stat().st_size,
        last_mod=datetime.fromtimestamp(full_path.stat().st_mtime),
    )

    conn.sendall((header.model_dump_json() + "\n").encode())


def send_file_binary(conn: socket, full_path: Path) -> None:
    with full_path.open("rb") as f:
        while chunk := f.read(MAX_BUFFER_SIZE_IN_BYTES):
            conn.sendall(chunk)


def send_file(conn: socket, repo_base_path: Path, file_info: Any) -> bool:
    full_path = (repo_base_path / file_info.path).resolve()

    if not full_path.is_file():
        log(
            LogType.ERROR,
            f"[{MODULE_NAME}] File not found: {full_path}"
        )
        return False

    try:
        send_file_header(conn, full_path, file_info)
        send_file_binary(conn, full_path)
        log(
            LogType.SUCCESS,
            f"[{MODULE_NAME}] Sent file {file_info.path}"
        )
        return True
    except Exception as e:
        log(
            LogType.ERROR,
            f"[{MODULE_NAME}] Error sending file {file_info.path}: {e}"
        )
        return False


def send_files_to_server(sock: socket, tasks: Any, repo_path, client_files_info_message) -> None:
    if not tasks.files_to_send:
        log(
            LogType.INFO,
            f"[{MODULE_NAME}] No files to send."
        )
        return

    files_send_counter = 0
    total_requested_files = len(tasks.files_to_send)

    for file_info in client_files_info_message.files:
        if file_info.path in tasks.files_to_send:
            if send_file(sock, repo_path, file_info):
                files_send_counter += 1

    if files_send_counter == total_requested_files:
        log(
            LogType.SUCCESS,
            f"[{MODULE_NAME}] All {files_send_counter} requested files sent."
        )
    else:
        log(
            LogType.SUCCESS,
            f"[{MODULE_NAME}] Sent {files_send_counter} from {total_requested_files} requested files."
        )
