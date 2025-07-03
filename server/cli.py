from typing import Tuple


def get_server_config() -> Tuple[int, int]:
    print("Enter synchronization interval (in minutes):")
    sync_interval = int(input("> "))

    print("Enter TCP listening port: ")
    tcp_port = int(input("> "))

    return sync_interval, tcp_port
