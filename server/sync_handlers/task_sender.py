from pathlib import Path

from common.logger.log_types import LogType
from common.logger.logger import log
from common.protocol.dto.file_info_message import FileInfoMessage
from common.protocol.dto.tasks_message import TasksMessage
from common.utils.repo_scanner import list_repo_files

MODULE_NAME = "TASK_SENDER"


def prepare_tasks_for_client(client_files: list[FileInfoMessage], client_repo_path: Path) -> TasksMessage:
    server_files = list_repo_files(client_repo_path)
    server_map = {f.path: f for f in server_files}

    files_to_send = []
    for client_file in client_files:
        server_file = server_map.get(client_file.path)
        if not server_file or client_file.last_mod > server_file.last_mod:
            files_to_send.append(client_file.path)

    return TasksMessage(files_to_send=files_to_send)


def send_tasks_to_client(conn, tasks: TasksMessage, client_id: str) -> None:
    conn.sendall(tasks.model_dump_json().encode() + b"\n")

    log(
        LogType.SUCCESS,
        f"[{MODULE_NAME}] Tasks sent to client {client_id}"
    )
