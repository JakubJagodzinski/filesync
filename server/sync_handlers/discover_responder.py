import json
import socket
import threading
from typing import Tuple

from common.config import MULTICAST_PORT, MULTICAST_GROUP, MAX_BUFFER_SIZE_IN_BYTES
from common.logger.log_types import LogType
from common.logger.logger import log
from common.protocol.dto.offer_message import OfferMessage
from common.protocol.enums.message_types import MessageType

MODULE_NAME = "DISCOVER_RESPONDER"


def udp_discover_listener(server_tcp_port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', MULTICAST_PORT))
        mreq = socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton('0.0.0.0')
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        log(
            LogType.INFO,
            f"[{MODULE_NAME}] Listening for DISCOVER messages..."
        )

        while True:
            try:
                data, client_address = sock.recvfrom(MAX_BUFFER_SIZE_IN_BYTES)

                decoded_data = data.decode()
                message_json = json.loads(decoded_data)

                message_type = message_json.get("type")

                if message_type == MessageType.DISCOVER:
                    log(
                        LogType.SUCCESS,
                        f"[{MODULE_NAME}] DISCOVER received from {client_address}"
                    )
                    send_offer_message(sock, server_tcp_port, client_address)
                else:
                    log(
                        LogType.WARNING,
                        f"[{MODULE_NAME}] Ignoring unknown message type from {client_address}: {message_type}"
                    )
            except json.JSONDecodeError:
                log(
                    LogType.ERROR,
                    f"[{MODULE_NAME}] Failed to decode JSON message from {client_address}"
                )
            except Exception as e:
                log(
                    LogType.ERROR,
                    f"[{MODULE_NAME}] Unexpected error from {client_address}: {e}"
                )


def start_udp_discover_listener(server_tcp_port: int) -> None:
    threading.Thread(
        target=udp_discover_listener,
        args=(server_tcp_port,),
        daemon=True
    ).start()


def send_offer_message(sock: socket.socket, server_tcp_port: int, client_address: Tuple[str, int]) -> None:
    log(
        LogType.INFO,
        f"[{MODULE_NAME}] Sending offer to {client_address}"
    )

    offer_message = OfferMessage(port=server_tcp_port)
    sock.sendto(offer_message.model_dump_json().encode(), client_address)

    log(
        LogType.SUCCESS,
        f"[{MODULE_NAME}] Offer sent to {client_address}"
    )
