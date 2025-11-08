from .interface import Comm
from eo4eu_comm_utils.kafka import KafkaProducer


class TopicComm(Comm):
    """Sends messages to a specific kafka topic

    :param producer: The underlying kafka producer
    :type producer: KafkaProducer
    :param topic: The kafka topic to send messages to
    :type topic: str
    :param key: The kafka key to send messages with
    :type key: str
    """

    def __init__(self, producer: KafkaProducer, topic: str, key: str):
        self.producer = producer
        self.topic = topic
        self.key = key

    def send(self, message: str = "", *args, **kwargs):
        """Send `message` to the kafka topic

        :param message: The message to send
        :type message: str
        :param args: Ignored
        :param kwargs: Ignored
        """
        self.producer.send_message(
            key = self.key,
            msg = message,
            topic = self.topic
        )
