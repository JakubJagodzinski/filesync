from pathlib import Path


def get_client_directory_path(repo_base_path: Path, client_id: str | None, client_ip: str) -> Path:
    if client_id:
        client_dir = f"client_{client_id}"
    else:
        client_dir = f"client_{client_ip.replace('.', '_')}"

    return repo_base_path / client_dir
