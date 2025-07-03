import json
import socket
import threading
import time
from typing import Optional, Tuple

from common.config import MAX_BUFFER_SIZE_IN_BYTES
from common.logger.log_types import LogType
from common.logger.logger import log
from common.protocol.dto.discover_message import DiscoverMessage
from common.protocol.dto.offer_message import OfferMessage
from common.utils.json_parser import safe_parse

MODULE_NAME = "DISCOVERER"

DISCOVER_INTERVAL = 10
DISCOVER_TIMEOUT = 5


class Discoverer:
    def __init__(self, multicast_group: str, multicast_port: int):
        self._thread: Optional[threading.Thread] = None
        self.multicast_group = multicast_group
        self.multicast_port = multicast_port
        self._stop_event = threading.Event()
        self._server_endpoint: Optional[Tuple[str, int]] = None

    def start(self):
        self._server_endpoint = None
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            daemon=True
        )
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()

    def get_server_address(self) -> Optional[Tuple[str, int]]:
        return self._server_endpoint

    def _run(self):
        while not self._stop_event.is_set():
            log(
                LogType.INFO,
                f"[{MODULE_NAME}] Sending multicast DISCOVER message..."
            )

            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
                    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
                    sock.settimeout(DISCOVER_TIMEOUT)

                    self._send_discover(sock)
                    offer = self._receive_offer(sock)

                    if offer:
                        self._server_endpoint = offer
                        return

            except socket.timeout:
                log(
                    LogType.INFO,
                    f"[{MODULE_NAME}] No OFFER received. Retrying in {DISCOVER_INTERVAL} seconds."
                )
            except Exception as e:
                log(
                    LogType.ERROR,
                    f"[{MODULE_NAME}] Error: {e}"
                )

            time.sleep(DISCOVER_INTERVAL)

    def _send_discover(self, sock: socket.socket) -> None:
        discover = DiscoverMessage()
        sock.sendto(discover.model_dump_json().encode(), (self.multicast_group, self.multicast_port))

    @staticmethod
    def _receive_offer(sock: socket.socket) -> Optional[Tuple[str, int]]:
        try:
            data, server_address = sock.recvfrom(MAX_BUFFER_SIZE_IN_BYTES)
            server_ip = server_address[0]

            decoded_data = data.decode()
            offer_message_json = json.loads(decoded_data)

            offer_message, error = safe_parse(OfferMessage, offer_message_json)
            if error:
                return None

            log(
                LogType.SUCCESS,
                f"[{MODULE_NAME}] Received OFFER from {server_ip}:{offer_message.port}"
            )
            return server_ip, offer_message.port
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            log(
                LogType.ERROR,
                f"[{MODULE_NAME}] Failed to decode JSON OFFER message: {e}"
            )
            return None
