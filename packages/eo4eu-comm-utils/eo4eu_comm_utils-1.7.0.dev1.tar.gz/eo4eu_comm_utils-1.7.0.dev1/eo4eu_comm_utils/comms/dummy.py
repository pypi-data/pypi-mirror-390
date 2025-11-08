from .interface import Comm

class DummyComm(Comm):
    """Does nothing"""

    def send(self, *args, **kwargs):
        """Does nothing"""
        pass
