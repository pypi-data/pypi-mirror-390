import os
import json
from pathlib import Path
from datetime import datetime, timezone
from eo4eu_base_utils.unify import overlay

from .interface import Comm, LogLevel
from ..kafka import KafkaProducer


_namespace_path = Path("/var/run/secrets/kubernetes.io/serviceaccount/namespace")


class MonitoringComm(Comm):
    """A comm configured out of the box to conform
    to the EO4EU Notification Manager message format. It
    sends kafka messages to monitoring.notify, so it needs
    a kafka producer

    :param producer: The kafka producer used to send the messages. This class tries to conform to different implementations lying around, but :class:`eo4eu_comm_utils.kafka.KafkaProducer` is recommended.
    :type producer: KafkaProducer
    :param component_name: The name of the component sending the messages
    :type component_name: str
    :param workflow_name: The name of the component's workflow. If not given, the instance will attempt to find the kubernetes namespace.
    :type workflow_name: str|None
    :param status_dict: An optional dictionary that translates :class:`LogLevel` to a string for the outgoing message.
    :type status_dict: dict[LogLevel,str]|None
    :param kwargs: Optional arguments that will be added to the output message as keys
    """

    def __init__(
        self,
        producer: KafkaProducer,
        component_name: str = "Component",
        workflow_name: str|None = None,
        status_dict: dict[LogLevel,str]|None = None,
        **kwargs
    ):
        if workflow_name is None:
            try:
                workflow_name = _namespace_path.read_text()
            except Exception:
                workflow_name = "unknown"

        if status_dict is None:
            status_dict = {
                LogLevel.DEBUG:    "INFO",
                LogLevel.INFO:     "INFO",
                LogLevel.WARNING:  "WARNING",
                LogLevel.ERROR:    "ERROR",
                LogLevel.CRITICAL: "CRITICAL",
                LogLevel.START:    "START",
                LogLevel.SUCCESS:  "SUCCESS",
            }

        self._producer = producer
        self._workflow_name = workflow_name
        self._component_name = component_name
        self._status_dict = status_dict
        self._kwargs = kwargs
        try:
            self._pod = os.environ["HOSTNAME"]
        except Exception:
            self._pod = "unknown"

    def send(
        self,
        level: LogLevel,
        description: str,
        *args,
        verbose_description: str|None = None,
        **kwargs
    ):
        """Send a proper message to the notification topic

        :param level: The level of the message
        :type level: LogLevel
        :param description: The message itself
        :type description: str
        :param args: Ignored
        :param verbose_description: An optional verbose description for the status
        :type verbose_description: str|None
        :param kwargs: Optional keyword arguments that will replace keys in the message
        """
        message = overlay(
            {
                "component_name": self._component_name,
                "workflow_name": self._workflow_name,
                "status": self._status_dict.get(level, "INFO"),
                "description": description,
                "verbose_description": verbose_description,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "optional": {
                    "pod": self._pod,
                }
            },
            overlay(self._kwargs, kwargs)
        )

        # trying to be compatible with the different kafka producers
        # floating around
        previous_topic = "monitoring.notify"
        try:
            previous_topic = self._producer._topic
        except Exception:
            pass
        self._producer.set_topic("monitoring.notify")
        self._producer.send_message(
            key = self._component_name,
            msg = json.dumps(message)
        )
        self._producer.set_topic(previous_topic)
