import socket
from pathlib import Path

from common.logger.log_types import LogType
from common.logger.logger import log
from common.protocol.dto.client_files_info_message import ClientFilesInfoMessage
from common.utils.repo_scanner import list_repo_files

MODULE_NAME = "FILE_INFO_SENDER"


def send_files_info(sock: socket, client_files_info_message) -> None:
    sock.sendall(client_files_info_message.model_dump_json().encode())

    log(
        LogType.SUCCESS,
        f"[{MODULE_NAME}] Sent CLIENT_FILES_INFO with {len(client_files_info_message.files)} files."
    )


def create_client_files_info_message(repo_path: Path, client_id: str) -> ClientFilesInfoMessage:
    files = list_repo_files(repo_path)

    return ClientFilesInfoMessage(
        client_id=client_id,
        files=files
    )
