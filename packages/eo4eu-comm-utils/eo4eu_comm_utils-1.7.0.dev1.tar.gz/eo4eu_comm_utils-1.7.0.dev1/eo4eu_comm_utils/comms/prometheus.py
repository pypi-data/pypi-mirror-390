from enum import Enum
from eo4eu_base_utils import OptionalModule
from eo4eu_base_utils.typing import Any

from .interface import Comm


_prometheus_module = OptionalModule(
    package = "eo4eu_comm_utils",
    enabled_by = ["prometheus", "full"],
    depends_on = ["prometheus_client"]
)

if _prometheus_module.is_enabled():
    from prometheus_client import Counter, Gauge, start_http_server

    Counter.__doc__ = """This is imported from prometheus-client.
        Please refer to https://prometheus.github.io/client_python/instrumenting/counter/
    """
    Gauge.__doc__ = """This is imported from prometheus-client.
        Please refer to https://prometheus.github.io/client_python/instrumenting/counter/
    """

    class CounterComm(Comm):
        """A wrapper around a prometheus Counter. For reference, see
        https://prometheus.github.io/client_python/instrumenting/gauge/. 
        You must install `eo4eu_comm_utils` with the `prometheus` submodule 
        to use this class

        :param counter: The prometheus counter
        :type counter: prometheus_client.Counter
        """
        def __init__(self, counter: Counter):
            self._counter = counter

        def send(self, value: int = 1, **kwargs):
            """Increments the counter by `value`

            :param value: The value to increment the counter by
            :type value: int
            :param kwargs: ignored
            """
            self._counter.inc(value)

        def get(self) -> Counter:
            """Get the underlying :class:`Counter`

            :rtype: Counter"""
            return self._counter


    class GaugeComm(Comm):
        """A wrapper around a prometheus Gauge. For reference, see
        https://prometheus.github.io/client_python/instrumenting/gauge/. 
        You must install `eo4eu_comm_utils` with the `prometheus` submodule 
        to use this class

        :param gauge: The prometheus gauge
        :type gauge: prometheus_client.Gauge
        """
        def __init__(self, gauge: Gauge):
            self._gauge = gauge

        def send(self, value: int = 1, **kwargs):
            """Sets the gauge to `value`

            :param value: The value to set into the gauge
            :type value: int
            :param kwargs: ignored
            """
            self._gauge.set(value)

        def get(self) -> Gauge:
            """Get the underlying :class:`Gauge`

            :rtype: Gauge"""
            return self._gauge


    def _wrap_metric(metric: Counter|Gauge) -> CounterComm|GaugeComm:
        if isinstance(metric, Counter):
            return CounterComm(metric)
        if isinstance(metric, Gauge):
            return GaugeComm(metric)
        raise ValueError(
            f"PrometheusComm expects either CounterComm or GaugeComm, "
            f"not {metric.__class__.__name__}"
        )


    class PrometheusComm(Comm):
        """A comm wrapping several Prometheus counters or gauges. 
        You are supposed to define an enum with the possible metrics 
        and use them as keys in a dictionary when defining this comm. 
        You must install `eo4eu_comm_utils` with the `prometheus` submodule 
        to use this class

        :param input: The dictionary with metrict matched to counters and gauges
        :type input: dict[Enum,prometheus_client.Counter|prometheus_client.Gauge]
        :param port: The port to use for the prometheus server
        :type port: int
        """

        def __init__(self, input: dict[Enum,Counter|Gauge], port: int = 8000):
            start_http_server(port)
            self._metrics = {
                kind: _wrap_metric(metric)
                for kind, metric in input.items()
            }

        def send(self, *kinds: Enum, value: int = 1, **kwargs):
            """Send the value to the selected counters/gauges

            :param kinds: The metric(s) which represent the desired counter(s)/gauge(s)
            :type kinds: Enum
            :param value: The value to increment each counter or set each gauge to
            :type value: int
            :param kwargs: Ignored
            """
            for kind in kinds:
                self._metrics[kind].send(value, **kwargs)

        def get(self, kind: Enum) -> Any:
            """Get the underlying prometheus_client instance of a metric

            :param kind: The metric to get
            :type kind: Enum
            :rtype: Counter|Gauge"""
            return self._metric[kind].get()
else:
    Counter = _prometheus_module.broken_class("Counter")
    Gauge = _prometheus_module.broken_class("Gauge")
    CounterComm = _prometheus_module.broken_class("CounterComm")
    GaugeComm = _prometheus_module.broken_class("GaugeComm")
    PrometheusComm = _prometheus_module.broken_class("PrometheusComm")
