import logging
from eo4eu_base_utils.typing import Callable

from .interface import Comm, LogLevel


_logger = logging.getLogger("eo4eu_comm_utils.comms")
_logger.setLevel(logging.WARNING)


class ModifyLogComm(Comm):
    """Wraps another comm, calling a given function on
    the input message before sending. It is expected
    that the underlying comm is a :class:`LogComm`

    :param comm: The comm to be wrapped
    :type comm: Comm
    :param func: The function to modify the input message
    :type func: Callable[[str],str]
    """

    def __init__(self, comm: Comm, func: Callable[[str],str]):
        self._comm = comm
        self._func = func

    def send(self, level: LogLevel, msg: str = "", *args, **kwargs):
        """Send a message to the underlying :class:`Comm`

        :param level: The level of the log message
        :type level: LogLevel
        :param msg: The log message
        :type msg: str
        :param args: Sent to the underlying comm
        :param kwargs: Sent to the underlying comm
        """
        modified_msg = msg
        try:
            modified_msg = self._func(msg)
        except Exception as e:
            _logger.warning(f"Failed to modify message \"{msg}\": {e}")

        self._comm.send(level, modified_msg, *args, **kwargs)
