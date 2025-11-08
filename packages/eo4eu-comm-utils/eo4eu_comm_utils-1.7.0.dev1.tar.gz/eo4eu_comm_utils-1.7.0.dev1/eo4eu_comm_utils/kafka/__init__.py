from eo4eu_base_utils import OptionalModule


_kafka_module = OptionalModule(
    package = "eo4eu_comm_utils",
    enabled_by = ["kafka", "full"],
    depends_on = ["confluent_kafka"]
)

if _kafka_module.is_enabled():
    from .producer import KafkaProducer
    from .consumer import KafkaConsumer
else:
    KafkaProducer = _kafka_module.broken_class("KafkaProducer")
    KafkaConsumer = _kafka_module.broken_class("KafkaConsumer")
