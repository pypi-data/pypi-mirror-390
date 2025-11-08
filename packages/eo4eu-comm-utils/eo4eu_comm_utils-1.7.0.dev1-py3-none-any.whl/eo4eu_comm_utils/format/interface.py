from abc import ABC, abstractmethod


class Formatter(ABC):
    """An interface for a class which formats strings"""

    @abstractmethod
    def fmt(self, input: str) -> str:
        """To be defined by the implementation

        :param input: The string to be formatted
        :type input: str
        :rtype: str
        """
        pass
