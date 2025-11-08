from logging import Logger
from functools import partial
from confluent_kafka import Producer
from eo4eu_base_utils.typing import Self

from ..settings import Settings


def _default_callback(err, msg, logger):
    if err is not None:
        logger.error(
            f"[Topic {msg.topic()}] Failed to deliver message: {str(msg.value())}: {str(err)}"
        )
    else:
        logger.info(
            f"[Topic {msg.topic()}] Message produced: {str(msg.value())}"
        )


class KafkaProducer:
    """Wrapper around confluent_kafka.Producer

    :param topic: The default topic messages will be sent to
    :type topic: str
    :param config: The kafka config to be used for the producer. For reference, see https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html#pythonclient-configuration
    :type config: dict
    :param logger: The standard Python logger to be used
    :type logger: logging.Logger
    :param callback: The callback to be provided to the underlying confluent_kafka.Producer
    :type callabck: Callable
    """

    def __init__(
        self,
        topic: str,
        config: dict,
        logger: Logger|None = None,
        callback = None
    ):
        if logger is None:
            logger = Settings.LOGGER
        if callback is None:
            callback = partial(_default_callback, logger = logger)

        self._topic = topic
        self._logger = logger
        self._producer = Producer(config)
        self._callback = callback

    @classmethod
    def from_config(cls, config: dict, **kwargs) -> Self:
        """Create KafkaProducer without a default topic

        :param config: The kafka config to be used for the producer.
        :type config: dict
        :param kwargs: The keyword arguments passed to KafkaProducer.__init__
        :type kwargs: dict
        :rtype: KafkaProducer
        """
        return KafkaProducer(None, config, **kwargs)

    def set_topic(self, topic: str):
        """Set the default topic to `topic`

        :param topic: The topic to use
        :type topic: str
        """
        self._topic = topic

    def send_message(self, key: str, msg: str, topic: str|None = None, callback = None):
        """Produce a kafka message

        :param key: The key to label the message by
        :type key: str
        :param msg: The message to send
        :type msg: str
        :param topic: The topic to send the message to. If none is provided, the KafkaProducer's default topic will be used
        :type topic: str|None
        :param callback: The callback to be provided to the underlying confluent_kafka.Producer. If none is provided, the KafkaProducer's default callback will be used
        :type callabck: Callable
        """
        if topic is None:
            topic = self._topic
        if callback is None:
            callback = self._callback

        self._producer.produce(topic, key=key, value=msg, callback=callback)
        self._producer.flush()
