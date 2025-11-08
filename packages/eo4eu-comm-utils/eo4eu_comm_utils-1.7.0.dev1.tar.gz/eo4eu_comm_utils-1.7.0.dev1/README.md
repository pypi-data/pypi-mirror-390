# Communication utilities for EO4EU

This package provides classes and functions that help with common tasks involving:

- Communicating with Kafka topics
- Logging, and in particular combining various loggers

## Installation

`eo4eu-comm-utils` is published on [PyPI](https://pypi.org/project/eo4eu-comm-utils/) and can be installed with `pip` anywhere. You can look for the latest version and pin that in your `requirements.txt` or what-have-you.

The package has now reached version `1.0` and the API should be stable. You can thus write something to the effect of  `eo4eu-comm-utils~=1.x`, where `x` the latest version when you first installed it.

**IMPORTANT**: The base package does not include support for kafka and prometheus! For the former, install `eo4eu-comm-utils[kafka]~=1.x`. For the latter, install `eo4eu-comm-utils[prometheus]~=1.x`. For both, install `eo4eu-comm-utils[full]~=1.x`.

## Usage

For example usage of this package, you may refer to [post-pro](https://git.apps.eo4eu.eu/eo4eu/eo4eu-provision-handler/post-pro), [jupyter-openfaas](https://git.apps.eo4eu.eu/eo4eu/eo4eu-openfaas-operations/jupyter-openfaas) or [jupyter-proxy](https://git.apps.eo4eu.eu/eo4eu/eo4eu-openfaas-operations/jupyter-proxy).

### Kafka consumers and producers

The interface for the `KafkaConsumer` and `KafkaProducer` classes is almost the same as before. For consumers:

```py
from eo4eu_comm_utils.kafka import KafkaConsumer

execution = ...

consumer = KafkaConsumer(
    topics = [config.topics.in_topic],
    config = config.kafka,
    handler = execution,
    logger = ...  # optional user-specified logger
)
consumer.consume()
```

And for producers:

```py
from eo4eu_comm_utils.kafka import KafkaProducer

producer = KafkaProducer(
    topic = config.topics.out_topic,
    config = config.kafka,
    logger = ...  # optional user-specified logger
)

# old way
producer.set_topic("relevant.topic")
producer.send_message(
    key = "component_name",
    msg = "something happened"
)

# new way
producer.send_message(
    key = "component_name",
    msg = "something happened",
    topic = "relevant.topic"
)
```

### Logging and messaging

Oftentimes you have multiple output streams to send messages to: Local component logs, downstream components, other Kafka topics, etc... This package provides the `Dispatcher` class that can handle multiple loggers/messengers at once and also group them up. For example:

```py
from eo4eu_comm_utils.kafka import KafkaProducer
from eo4eu_comm_utils.comms import Dispatcher, LogComm, MonitoringComm TopicComm
from .config import config
import logging

logging.basicConfig()

producer = KafkaProducer(topic = "system.dsl", config = config.kafka.to_dict())

dispatcher = Dispatcher(
    comms = {
        "local": LogComm(logger = logger.getLogger(__name__)),
        "monitor": MonitoringComm(
            producer = producer,
            namespace = config.eo4eu.namespace,
            source = "component_name",
            prefix = "ComponentName"
        ),
        "out_topic_0": TopicComm(
            producer = producer,
            topic = "out_topic_0",
            key = "component_name",
        ),
        "out_topic_1": TopicComm(
            producer = producer,
            topic = "out_topic_1",
            key = "component_name",
        ),
    },
    groups = {
        "all_logs": ["local", "monitor"],
        "all_out_topics": ["out_topic_0", "out_topic_1"],
    }
)
```

The `Dispatcher` class supports all the common logging methods, such as `info`, `warning`, `error` etc, as well as `success` and a `send` method for simply sending messages:

```py
dispatcher.local.info("Started processing")
dispatcher.local.error("Something bad happened")

# this will send the same message to "local" and "monitor",
# as those make up the group "all_logs"
dispatcher.all_logs.success("We did it")

dispatcher.out_topic_0.send("hi")
dispatcher.out_topic_1.send("hello")

# this will send the same message to "out_topic_0" and "out_topic_1",
# as those make up the group "all_out_topics"
dispatcher.all_out_topics.send("some info")
```

### Different Comms

The dispatcher can work with any class following the very simple `Comm` interface:

```py
class Comm(ABC):
    @abstractmethod
    def send(*args, **kwargs):
        pass
```

Comms are not very useful on their own and it's best to always wrap them in a `Dispatcher`, which is what provides the regular logging `info`, `error`, etc functions. If you only want to use one comm, you can do:

```py
from eo4eu_comm_utils.comms import Dispatcher, ...

some_comm = ...

dispatcher = Dispatcher.one(some_comm)
```

Which then allows you to use all the known functions with that comm only.

`eo4eu_comm_utils` provides a number of predefined comms:

### LogComm

It is basically a regular python `logging.Logger`, but with the extra debug option to print the entire stack trace upon error:

```py
from eo4eu_comm_utils.comms import LogComm
import logging

log_comm = LogComm(
    logger = logging.getLogger(__name__),
    print_traceback = True  # default is False
)
```

### TopicComm

Requires a `KafkaProducer`, and will send messages to a single topic.

```py
from eo4eu_comm_utils.kafka import KafkaProducer
from eo4eu_comm_utils.comms import LogComm

producer = KafkaProducer(
    topic = "doesnt.matter",
    config = KAFKA_CONFIG
)

topic_comm = TopicComm(
    producer = producer,
    topic = "topic.name",
    key = "key_name"
)
```

With topic comms wrapped in a dispatcher, it only makes sense to use `Dispatcher.send` and not logging functions like `info` or `debug`.

### MonitoringComm

Configured out of the box to send messages to the `monitoring.notify` component. You can refer to [NOTIFIER.md](https://git.apps.eo4eu.eu/eo4eu/eo4eu-provision-handler/eo4eu-comm-utils/-/blob/main/NOTIFIER.md) for more information.

### PrometheusComm

Is a wrapper around a set of prometheus counters or gauges that represent some metrics. To use it, you should first define an enum for all the possible metrics. Note that you need `eo4eu-comm-utils[prometheus]` or `eo4eu-comm-utils[full]` to use the prometheus submodule.

```py
from enum import Enum
from eo4eu_comm_utils.comms import Dispatcher
from eo4eu_comm_utils.comms.prometheus import (
    Gauge,
    Counter,
    PrometheusComm
)


class Metric(Enum):
    UPLOAD_FAILURE
    DOWNLOAD_FAILURE
    ACTIVE_WORKFLOWS
    # etc

prom_comm = PrometheusComm({
    Metric.UPLOAD_FAILURE: Counter(
        "component_upload_failure",
        "failed to upload"
    ),
    Metric.DOWNLOAD_FAILURE: Counter(
        "component_download_failure",
        "failed to download"
    ),
    Metric.ACTIVE_WORKFLOWS: Gauge(
        "active_workflows",
        "the number of active workflows"
    )
    # ...
})

# wrap it in a dispatcher
dispatcher = Dispatcher.one(prom_comm)

# increment the upload failure counter
dispatcher.add(Metric.UPLOAD_FAILURE)
# many times, if you want
dispatcher.add(Metric.DOWNLOAD_FAILURE, value = 5)
# or multiple metrics at the same time
dispatcher.add(Metric.UPLOAD_FAILURE, Metric.DOWNLOAD_FAILURE)

# you can use send for gauges as well. The following calls
# the Gauge.set method with the value 3
dispatcher.send(Metric.ACTIVE_WORKFLOWS, value = 3)
```
