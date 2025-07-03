from common.logger.log_types import LogType


class AnsiColor:
    RESET = "\033[0m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    GREEN = "\033[32m"


def get_color(log_type: LogType) -> str:
    return {
        LogType.ERROR: AnsiColor.RED,
        LogType.WARNING: AnsiColor.YELLOW,
        LogType.SUCCESS: AnsiColor.GREEN,
        LogType.INFO: AnsiColor.RESET,
    }.get(log_type, AnsiColor.RESET)
