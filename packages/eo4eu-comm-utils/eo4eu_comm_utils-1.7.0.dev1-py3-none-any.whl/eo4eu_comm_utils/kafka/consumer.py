import asyncio
from logging import Logger
from confluent_kafka import Consumer, Message
from eo4eu_base_utils.typing import Callable, Any

from ..settings import Settings


class KafkaConsumer:
    """Wrapper around confluent_kafka.Consumer

    :param topics: The kafka topic(s) to listen to
    :type topics: list[str]|str
    :param config: The kafka config to pass to the underlying confluent_kafka.Consumer. For reference, see https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html#pythonclient-configuration
    :type config: dict
    :param handler: A function to pass the UTF-8 decoded value of each message to
    :type handler: Callable[[str],None]|None
    :param logger: Optional Python logger to use for logs
    :type logger: logging.Logger|None
    :param timeout: The poll interval to use when consuming messages
    :type timeout: float
    :param exit_after: If set, the consumer will stop polling after consuming N messages
    :type exit_after: int|None
    :param callback: A function that runs every time a message is received. It takes two parameters: The raw confluent_kafka.Message, and the UTF-8 decoded value of the message
    :type callback: Callable[[confluent_kafka.Message,str],None]|None
    :param decoder: The function that extracts the data requested by the handler from each kafka message. By default, it takes the value and decodes it into a UTF-8 string
    :type decoder: Callable[[confluent_kafka.Message],Any]|None
    :param error_handler: The function that gets called whenever an exception gets raised inside or outside the handler (e.g. thread timeout)
    :type error_handler: Callable[[Exception],None]|None
    :param run_async: If True, each kafka message gets processed asynchronously in its own coroutine. By default, it is False
    :type run_async: bool
    :param async_timeout: The maximum time (in seconds) each coroutine is allowed to run
    :type async_timeout: int
    """

    def __init__(
        self,
        topics: list[str]|str,
        config: dict,
        handler: Callable[[str],None]|None = None,
        logger: Logger|None = None,
        timeout: float = 1.0,
        exit_after: int|None = None,
        callback: Callable[[Message,str],None]|None = None,
        decoder: Callable[[Message],Any]|None = None,
        error_handler: Callable[[Exception],None]|None = None,
        run_async: bool = False,
        async_timeout: int = Settings.DEFAULT_KAFKA_ASYNC_TIMEOUT,
    ):
        if not isinstance(topics, list):
            topics = [topics]
        if logger is None:
            logger = Settings.LOGGER
        if callback is None:
            callback = lambda msg, dec_msg: logger.info(
                Settings.DEFAULT_KAFKA_CONSUMER_CALLBACK_FMT(msg, dec_msg)
            )
        if decoder is None:
            decoder = Settings.DEFAULT_KAFKA_DECODER
        if error_handler is None:
            error_handler = lambda e: logger.error(f"Unhandled error: {e}")
        if async_timeout is None or async_timeout <= 0:
            async_timeout = Settings.DEFAULT_KAFKA_ASYNC_TIMEOUT

        self._consumer = Consumer(config)
        self._topics = topics
        self._handler = handler
        self._logger = logger
        self._timeout = timeout
        self._exit_after = exit_after
        self._callback = callback
        self._decoder = decoder
        self._error_handler = error_handler
        self._run_async = run_async
        self._async_timeout = async_timeout

    def _consume_one(self, handler: Callable[[str],None], task_group = None) -> bool:
        try:
            msg = self._consumer.poll(timeout = self._timeout)
            if msg is None or msg.error():
                return False

            self._callback(msg, msg.value().decode("utf-8"))
            decoded_msg = self._decoder(msg)

            if self._run_async:
                async def _handler_coroutine(*args, **kwargs):
                    handler(*args, **kwargs)

                with asyncio.timeout(self._async_timeout):
                    if task_group is None:
                        asyncio.create_task(_handler_coroutine(decoded_msg))
                    else:
                        task_group.create_task(_handler_coroutine(decoded_msg))
            else:
                handler(decoded_msg)

            return True
        except Exception as e:
            self._error_handler(e)

        return False

    def _consume_unbounded(self, handler: Callable[[str],None]):
        while True:
            self._consume_one(handler)

    def _consume_bounded(self, handler: Callable[[str],None]):
        # Making sure all tasks are complete before exiting
        with asyncio.TaskGroup() as task_group:
            messages_received = 0
            while messages_received < self._exit_after:
                if self._consume_one(handler, task_group = task_group):
                    messages_received += 1

    def consume(self, handler: Callable[[str],None]|None = None):
        """Continuously poll for new messages, either indefinitely 
        or exiting after N messages, depending on whether `exit_after` 
        is None or not

        :param handler: A function to pass the UTF-8 decoded value of each message to. If not given, the KafkaConsumer's default handler will be used
        :type handler: Callable[[str],None]|None
        """
        if handler is None:
            handler = self._handler

        try:
            self._consumer.subscribe(self._topics)

            if self._exit_after is None:
                self._consume_unbounded(handler)
            else:
                self._consume_bounded(handler)
        finally:
            self._consumer.close()
