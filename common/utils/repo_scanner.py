from datetime import datetime
from pathlib import Path
from typing import List

from common.protocol.dto.file_info_message import FileInfoMessage


def list_repo_files(directory_path: Path) -> List[FileInfoMessage]:
    files = []

    for path in directory_path.rglob("*"):
        if path.is_file():
            try:
                stat = path.stat()
                rel_path = path.relative_to(directory_path).as_posix()
                files.append(FileInfoMessage(
                    name=path.name,
                    path=rel_path,
                    last_mod=datetime.fromtimestamp(stat.st_mtime)
                ))
            except FileNotFoundError:
                continue

    return files
