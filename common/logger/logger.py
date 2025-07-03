import threading
from datetime import datetime

from common.logger.log_colors import AnsiColor, get_color
from common.logger.log_types import LogType

_log_lock = threading.Lock()


def log(msg_type: LogType, message: str) -> None:
    with _log_lock:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        color = get_color(msg_type)
        print(f"{color}[{timestamp}] [{msg_type}] {message}{AnsiColor.RESET}")
