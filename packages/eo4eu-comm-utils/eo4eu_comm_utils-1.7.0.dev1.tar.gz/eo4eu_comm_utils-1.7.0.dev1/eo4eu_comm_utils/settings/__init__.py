import logging


logger = logging.getLogger("eo4eu.comm")
logger.setLevel(logging.INFO)


class Settings:
    """Holds library-wide settings"""

    LOGGER = logger
    """The logger used by the library. By default, it's \"eo4eu.comm\""""

    DEFAULT_KAFKA_DECODER = lambda msg: msg.value().decode("utf-8")
    """The default way to extract data from kafka messages"""

    DEFAULT_KAFKA_CONSUMER_CALLBACK_FMT = lambda msg, dec_msg: f"[Topic {msg.topic()}] Message received: {dec_msg}"
    """The default log message sent whenever a message is consumed"""

    DEFAULT_KAFKA_ASYNC_TIMEOUT = 3600
    """The default timeout for kafka coroutines"""
