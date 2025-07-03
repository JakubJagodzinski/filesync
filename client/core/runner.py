from client.core.tcp_session_handler import start_tcp_session
from client.sync_handlers.discoverer import Discoverer
from common.config import MULTICAST_GROUP, MULTICAST_PORT

MODULE_NAME = "RUNNER"


def run_client_with_discovery(client_id: str | None) -> None:
    discovery = Discoverer(MULTICAST_GROUP, MULTICAST_PORT)
    discovery.start()

    while True:
        server_address = discovery.get_server_address()

        if server_address:
            server_ip, server_port = server_address
            discovery.stop()

            while True:
                if not start_tcp_session(server_ip, server_port, client_id):
                    discovery.start()
                    break


def run_client(server_ip: str, server_port: int, client_id: str | None) -> None:
    if server_ip and server_port:
        start_tcp_session(
            server_ip,
            server_port,
            client_id,
        )
    else:
        run_client_with_discovery(client_id)
