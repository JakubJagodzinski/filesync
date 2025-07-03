import socket
from pathlib import Path
from typing import Tuple, List

from common.logger.log_types import LogType
from common.logger.logger import log
from common.protocol.dto.file_info_message import FileInfoMessage
from common.utils.repo_scanner import list_repo_files
from server.sync_handlers.file_receiver import receive_files_from_client

MODULE_NAME = "REPO_SYNCHRONIZER"


def synchronize_server_repo(conn: socket.socket, files_to_receive_count: int,
                            client_files: List[FileInfoMessage], client_repo_path: Path) -> Tuple[int, int]:
    try:
        received_files = receive_files_from_client(conn, files_to_receive_count, client_repo_path)

        client_files_paths = {f.path for f in client_files}
        deleted_files = delete_obsolete_files(client_repo_path, client_files_paths)
        return received_files, deleted_files
    except Exception as e:
        log(
            LogType.ERROR,
            f"[{MODULE_NAME}] Error during repository synchronization: {e}"
        )
        return 0, 0


def delete_obsolete_files(repo_path: Path, client_file_paths: set[str]) -> int:
    server_files = list_repo_files(repo_path)

    deleted_files_counter = 0

    for file_info in server_files:
        if file_info.path not in client_file_paths:
            full_path = repo_path / file_info.path
            try:
                if full_path.exists():
                    full_path.unlink()

                    log(
                        LogType.SUCCESS,
                        f"[{MODULE_NAME}] Removed obsolete file: {file_info.path}"
                    )
                    deleted_files_counter += 1
            except Exception as e:
                log(
                    LogType.ERROR,
                    f"[{MODULE_NAME}] Failed to remove {file_info.path}: {e}"
                )

    return deleted_files_counter
