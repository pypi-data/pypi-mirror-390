from eo4eu_base_utils.typing import Self, Callable

from .monitoring import MonitoringComm
from .interface import Comm, LogLevel
from ..kafka import KafkaProducer
from ..settings import Settings


class Dispatcher:
    """Can combine many instances of :class:`Comm`
    into one, allowing you to select which ones you want
    to send a message to

    :param comms: A dictionary of named :class:`Comm` s
    :type comms: dict[str,Comm]
    :param groups: A dictionary of named groups of :class:`Comm` s. Each key contains a list of names for comms, which must be separately defined in the `comms` dictionary
    :type groups: dict[str,list[str]]
    :param callback: A function to call every time a message is sent. The dispatcher itself is passed as the first argument of the callback
    :type callback: Callable[[Dispatcher,Any],None]
    :param selection: The names of comms to send messages to. This is not meant to be set using this constructor
    :type selection: list[str]
    :param functions: A set of \"functions\" to be called when using this dispatcher as a callable. This is not meant to be set using this constructor
    :type functions: list[tuple[list[str],Callable,tuple]]
    """

    def __init__(
        self,
        comms: dict[str,Comm],
        groups: dict[str,list[str]]|None = None,
        callback = None,
        selection: list[str]|None = None,
        functions: list[str]|None = None
    ):
        if groups is None:
            groups = {}
        if callback is None:
            callback = lambda this, *args, **kwargs: None
        if functions is None:
            functions = []

        self._comms = comms
        self._groups = groups
        self._callback = callback
        self._selection = selection
        self._functions = functions

    @classmethod
    def one(cls, comm: Comm, callback = None) -> Self:
        """Create a dispatcher which wraps a single :class:`Comm`

        :param comm: The :class:`Comm` to be used
        :type comm: Comm
        :param callback: Refer to the `callback` parameter of the constructor
        :type callback: Callable[[Dispatcher,Any],None]
        :rtype: Dispatcher
        """
        return Dispatcher(
            comms = {"default": comm},
            callback = callback
        )

    @classmethod
    def many(cls, **kwargs) -> Self:
        """More convenient method for constructing a dispatcher. 
        Only takes keyword arguments. If an argument is a :class:`Comm` , 
        it is added to the `comms` field of the default constructor. If 
        is is a list, it is added to the `groups` field of the default
        constructor.

        :param kwargs: The comms/groups to initialize the dispatcher with
        :type kwargs: dict[str,Comm|list[str]]
        :rtype: Dispatcher
        """
        comms = {}
        groups = {}
        for name, arg in kwargs.items():
            if isinstance(arg, Comm):
                comms[name] = arg
            elif isinstance(arg, list):
                groups[name] = arg

        return Dispatcher(
            comms = comms,
            groups = groups,
        )

    @classmethod
    def notifier(cls, kafka_config: dict, *args, **kwargs) -> Self:
        """Construct a dispatcher with one :class:`eo4eu_comm_utils.comms.monitoring.MonitoringComm`, 
        for the purposes of sending messages to the Notification Manager

        :param kafka_config: The configuration used for the underlying kafka producer. For reference, see https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html#pythonclient-configuration
        :type kafka_config: dict
        :param args: The positional arguments passed to the :class:`eo4eu_comm_utils.comms.monitoring.MonitoringComm` constructor
        :type args: Tuple[Any]
        :param kwargs: The keyword arguments passed to the :class:`eo4eu_comm_utils.comms.monitoring.MonitoringComm` constructor
        :type kwargs: Dict[str,Any]
        """
        return cls.one(MonitoringComm(
            KafkaProducer(
                topic = "monitoring.notify",
                config = kafka_config,
            ),
            *args,
            **kwargs,
        ))

    def get_comm(self, name: str) -> Comm:
        """Get the comm by the given name

        :param name: The name of the comm
        :type name: str
        :raises: KeyError if the comm does not exist
        :rtype: Comm
        """
        return self._comms[name]

    def add_comm(self, name: str, comm: Comm) -> Self:
        """Sets the given comm into the slot of the given name

        :param name: The name of the new comm
        :type name: str
        :param comm: The new comm
        :type comm: Comm
        :returns: The modified dispatcher (Note that the modification is done inplace!)
        :rtype: Dispatcher
        """
        self._comms[name] = comm
        return self

    def add_group(self, name: str, sub_names: list[str]) -> Self:
        """Sets the given group into the slot of the given name

        :param name: The name of the new group
        :type name: str
        :param sub_names: The new group; note that it may contain the names of other groups
        :type sub_names: list[str]
        :returns: The modified dispatcher (Note that the modification is done inplace!)
        :rtype: Dispatcher
        """
        result = []
        for sub_name in sub_names:
            if sub_name in self._comms:
                result.append(sub_name)
            elif sub_name in self._groups:
                result.extend(self._groups[sub_name])

        self._groups[name] = result
        return self

    def _with_selection(self, selection: list[str]|None) -> Self:
        return Dispatcher(
            comms = self._comms,
            groups = self._groups,
            callback = self._callback,
            selection = selection,
            functions = self._functions
        )

    def __getattr__(self, name: str) -> Self:
        """Returns a new dispatcher which has the given comm 
        or group selected. The current dispatcher is not modified. 
        If the attribute does not exist, a dispatcher with an empty 
        selection is returned.

        :param name: The name of the comm or group to be selected
        :type name: str
        :returns: A new dispatcher with the provided selection
        :rtype: Dispatcher
        """
        if name in self._groups:
            return self._with_selection(self._groups[name])
        if name in self._comms:
            return self._with_selection([name])
        return self._with_selection([])

    def __call__(self, *args, **kwargs):
        """Send messages to the comms selected for by this
        dispatcher's functions. This is only meant to be used
        with :class:`Dispatcher.sendf()` and derivatives.

        :param args: The args to be passed to the function
        :type args: tuple
        :param kwargs: The keyword args to be passed to the function
        :type kwargs: dict
        """
        if len(self._functions) <= 0:
            Settings.LOGGER.warning("Dispatcher has no functions to call")
            return

        for selection, formatter, func_args in self._functions:
            self._with_selection(selection).send(*func_args, formatter(*args, **kwargs))

    def all(self) -> Self:
        """Returns a dispatcher selecting all comms. Does not modify 
        the current dispatcher

        :rtype: Dispatcher
        """
        return self._with_selection(None)

    def len(self) -> int:
        """Returns the number of currently selected comms

        :rtype: int
        """
        if self._selection is None:
            return len(self._comms)

        return len(self._selection)

    def send(self, *args, **kwargs):
        """Sends message to the selected comms

        :param args: The args to be passed to the comm's `send` function
        :type args: tuple
        :param kwargs: The keyword args to be passed to the comm's `send` function
        :type kwargs: dict
        """
        try:
            self._callback(self, *args, **kwargs)
        except Exception as e:
            Settings.LOGGER.warning(f"Callback error: {e}")

        selection = self._comms.keys() if self._selection is None else self._selection

        for name in selection:
            try:
                self._comms[name].send(*args, **kwargs)
            except Exception as e:
                Settings.LOGGER.warning(f"Failed to send message to comm \"{name}\": {e}")

    def add(self, *args, **kwargs):
        """Alias for :class:`Dispatcher.send`"""
        self.send(*args, **kwargs)

    def debug(self, *args, **kwargs):
        """Calls :class:`Dispatcher.send`, adding LogLevel.DEBUG as the first argument"""
        self.send(LogLevel.DEBUG, *args, **kwargs)

    def info(self, *args, **kwargs):
        """Calls :class:`Dispatcher.send`, adding LogLevel.INFO as the first argument"""
        self.send(LogLevel.INFO, *args, **kwargs)

    def warning(self, *args, **kwargs):
        """Calls :class:`Dispatcher.send`, adding LogLevel.WARNING as the first argument"""
        self.send(LogLevel.WARNING, *args, **kwargs)

    def error(self, *args, **kwargs):
        """Calls :class:`Dispatcher.send`, adding LogLevel.ERROR as the first argument"""
        self.send(LogLevel.ERROR, *args, **kwargs)

    def critical(self, *args, **kwargs):
        """Calls :class:`Dispatcher.send`, adding LogLevel.CRITICAL as the first argument"""
        self.send(LogLevel.CRITICAL, *args, **kwargs)

    def start(self, *args, **kwargs):
        """Calls :class:`Dispatcher.send`, adding LogLevel.START as the first argument"""
        self.send(LogLevel.START, *args, **kwargs)

    def success(self, *args, **kwargs):
        """Calls :class:`Dispatcher.send`, adding LogLevel.SUCCESS as the first argument"""
        self.send(LogLevel.SUCCESS, *args, **kwargs)

    def sendf(self, format: str|Callable, *args) -> Self:
        """Populates the dispatcher's functions with the provided
        format and args

        :param format: Either a python format string to be used by `str.format()` or a callable that returns a string. This will determine what will be sent to the currently selected comms if the `__call__` method is called on the resulting dispatcher.
        :type format: str|Callable[[Any],str]
        :param args: The args to be given to each `Comm.send` method *before* the result of the `format` function
        :returns: A new dispatched with the added function tuple. Does not modify the current dispatcher
        :rtype: Dispatcher
        """
        formatter = format
        if isinstance(format, str):
            formatter = lambda *args, **kwargs: format.format(*args)

        return Dispatcher(
            comms = self._comms,
            groups = self._groups,
            callback = self._callback,
            selection = self._selection,
            functions = self._functions + [
                (self._selection, formatter, args)
            ]
        )

    def debugf(self, format: str|Callable) -> Self:
        """Calls Dispatcher.sendf, adding LogLevel.DEBUG as the first argument

        :rtype: Dispatcher
        """
        return self.sendf(format, LogLevel.DEBUG)

    def infof(self, format: str|Callable) -> Self:
        """Calls :class:`Dispatcher.sendf`, adding LogLevel.INFO as the first argument

        :rtype: Dispatcher
        """
        return self.sendf(format, LogLevel.INFO)

    def warningf(self, format: str|Callable) -> Self:
        """Calls :class:`Dispatcher.sendf`, adding LogLevel.WARNING as the first argument

        :rtype: Dispatcher
        """
        return self.sendf(format, LogLevel.WARNING)

    def errorf(self, format: str|Callable) -> Self:
        """Calls :class:`Dispatcher.sendf`, adding LogLevel.ERROR as the first argument

        :rtype: Dispatcher
        """
        return self.sendf(format, LogLevel.ERROR)

    def criticalf(self, format: str|Callable) -> Self:
        """Calls :class:`Dispatcher.sendf`, adding LogLevel.CRITICAL as the first argument

        :rtype: Dispatcher
        """
        return self.sendf(format, LogLevel.CRITICAL)

    def startf(self, format: str|Callable) -> Self:
        """Calls :class:`Dispatcher.sendf`, adding LogLevel.START as the first argument

        :rtype: Dispatcher
        """
        return self.sendf(format, LogLevel.START)

    def successf(self, format: str|Callable) -> Self:
        """Calls :class:`Dispatcher.sendf`, adding LogLevel.SUCCESS as the first argument

        :rtype: Dispatcher
        """
        return self.sendf(format, LogLevel.SUCCESS)

    def clearf(self) -> Self:
        """Returns a dispatcher with the same settings, except all
        function definitions are removed

        :rtype: Dispatcher
        """
        return Dispatcher(
            comms = self._comms,
            groups = self._groups,
            callback = self._callback,
            selection = self._selection,
            functions = []
        )
