from datetime import datetime, timedelta

from common.logger.log_types import LogType
from common.logger.logger import log
from common.protocol.dto.next_sync_message import NextSyncMessage

MODULE_NAME = "NEXT_SYNC_INFO_SENDER"


def send_next_sync_info_message(conn, sync_interval: int) -> None:
    next_sync_time = datetime.now() + timedelta(minutes=sync_interval)
    next_sync_message = NextSyncMessage(time=next_sync_time)

    try:
        conn.sendall(next_sync_message.model_dump_json().encode())
    except OSError as e:
        log(
            LogType.ERROR,
            f"[{MODULE_NAME}] Failed to send next sync info: {e}"
        )

    log(
        LogType.SUCCESS,
        f"[{MODULE_NAME}] Sent next sync time: {next_sync_time}"
    )
