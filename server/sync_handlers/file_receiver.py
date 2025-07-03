import os
import socket
from pathlib import Path

from common.config import MAX_BUFFER_SIZE_IN_BYTES
from common.logger.log_types import LogType
from common.logger.logger import log
from common.protocol.dto.file_header_message import FileHeaderMessage

MODULE_NAME = "FILE_RECEIVER"


def receive_file_header(conn: socket.socket) -> FileHeaderMessage | None:
    header_data = b''
    while not header_data.endswith(b'\n'):
        chunk = conn.recv(1)

        if not chunk:
            log(
                LogType.ERROR,
                f"[{MODULE_NAME}] Connection closed while reading header"
            )
            return None

        header_data += chunk

    file_header = FileHeaderMessage.model_validate_json(header_data.decode())

    return file_header


def receive_file_binary(conn: socket.socket, destination_path: Path, file_header: FileHeaderMessage) -> bool:
    bytes_remaining = file_header.size
    received_total = 0

    log(
        LogType.INFO,
        f"[{MODULE_NAME}] Receiving file: {file_header.path} ({file_header.size} bytes)"
    )
    with open(destination_path, 'wb') as f:
        while bytes_remaining > 0:
            chunk = conn.recv(min(MAX_BUFFER_SIZE_IN_BYTES, bytes_remaining))
            if not chunk:
                log(
                    LogType.ERROR,
                    f"[{MODULE_NAME}] Connection closed during file transfer. Received {received_total}/{file_header.size} bytes."
                )
                return False

            f.write(chunk)
            bytes_remaining -= len(chunk)
            received_total += len(chunk)

    mod_time = file_header.last_mod.timestamp()
    os.utime(destination_path, (mod_time, mod_time))

    log(
        LogType.SUCCESS,
        f"[{MODULE_NAME}] File saved: {destination_path}"
    )

    return True


def receive_file(conn: socket.socket, client_repo_path: Path) -> bool:
    file_header = receive_file_header(conn)

    if file_header is None:
        log(
            LogType.ERROR,
            f"[{MODULE_NAME}] failed to receive header"
        )
        return False

    destination_path = (client_repo_path / file_header.path).resolve()
    repo_root = client_repo_path

    if not is_path_safe(repo_root, destination_path):
        log(
            LogType.WARNING,
            f"[{MODULE_NAME}] Path traversal attempt: {destination_path}"
        )
        return False

    os.makedirs(destination_path.parent, exist_ok=True)

    success = receive_file_binary(conn, destination_path, file_header)

    return success


def receive_files_from_client(conn: socket.socket, files_to_receive_count: int, client_repo_path: Path) -> int:
    received_files_counter = 0

    for _ in range(files_to_receive_count):
        if receive_file(conn, client_repo_path):
            received_files_counter += 1

    return received_files_counter


def is_path_safe(base: Path, target: Path) -> bool:
    try:
        target.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False
