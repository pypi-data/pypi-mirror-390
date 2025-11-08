import logging
from abc import ABC, abstractmethod
from enum import Enum


class LogLevel(Enum):
    """An Enum wrapper around default Python log levels. Values:

    LogLevel.DEBUG

    LogLevel.INFO

    LogLevel.WARNING

    LogLevel.ERROR

    LogLevel.CRITICAL

    LogLevel.START

    LogLevel.SUCCESS
    """
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    START = 0
    SUCCESS = 1

    def to_logging_level(self) -> int:
        """Converts the LogLevel to a regular integer

        LogLevel.DEBUG -> logging.DEBUG

        LogLevel.INFO -> logging.INFO

        LogLevel.WARNING -> logging.WARNING

        LogLevel.ERROR -> logging.ERROR

        LogLevel.CRITICAL -> logging.CRITICAL

        LogLevel.START -> logging.INFO

        LogLevel.SUCCESS -> logging.INFO
        """
        if self in {LogLevel.START, LogLevel.SUCCESS}:
            return logging.INFO

        return self.value


class Comm(ABC):
    """Simple interface meant to wrap classes
    which send messages somewhere"""

    @abstractmethod
    def send(self, *args, **kwargs):
        """To be defined by the implementation"""
        pass
