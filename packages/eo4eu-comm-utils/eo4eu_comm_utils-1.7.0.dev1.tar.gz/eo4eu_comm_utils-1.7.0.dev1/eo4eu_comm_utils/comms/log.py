import traceback
import logging
from .interface import Comm, LogLevel


class LogComm(Comm):
    """A comm wrapping a regular Python logger

    :param logger: The logger to be wrapped
    :type logger: logging.Logger
    """

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def send(self, level: LogLevel, msg: str = "", *args, **kwargs):
        """Converts the `level` param to a regular python logging level
        and calls the `logging.Logger.log` method with that level
        and the `msg` parameter

        :param level: The LogLevel of the message
        :type level: LogLevel
        :param msg: The message to be logged
        :type msg: str
        :param args: Ignored
        :param kwargs: Ignored
        """
        self.logger.log(level.to_logging_level(), msg)
