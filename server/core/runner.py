from time import sleep

from common.logger.log_types import LogType
from common.logger.logger import log
from server.cli import get_server_config
from server.core.tcp_connector import start_tcp_listener
from server.sync_handlers.discover_responder import start_udp_discover_listener

MODULE_NAME = "RUNNER"


def run_server() -> None:
    sync_interval, server_tcp_port = get_server_config()

    start_udp_discover_listener(server_tcp_port)
    start_tcp_listener(server_tcp_port, sync_interval)

    log(
        LogType.INFO,
        f"[{MODULE_NAME}] Server is running. Press Ctrl+C to exit."
    )
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        log(
            LogType.INFO,
            f"[{MODULE_NAME}] Server is shutting down..."
        )
