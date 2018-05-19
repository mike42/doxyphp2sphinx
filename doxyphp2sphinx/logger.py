from enum import IntEnum


class LogLevel(IntEnum):
    """
    Named log levels
    """
    OFF = 0
    ERROR = 1
    WARN = 2
    INFO = 3
    DEBUG = 4
    TRACE = 5
    ALL = 6


class FilteredLogger:
    def __init__(self, loglevel):
        self._loglevel = loglevel

    def log(self, msg, loglevel = LogLevel.INFO):
        if loglevel > self._loglevel:
            return
        print(msg)
