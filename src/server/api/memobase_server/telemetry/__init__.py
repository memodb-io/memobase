from enum import Enum, auto
from typing import Dict

from prometheus_client import start_http_server
from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics._internal.instrument import Counter, Histogram, ObservableGauge
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.metrics import CallbackOptions, Observation


from ..env import LOG


class CounterMetricName(Enum):
    """Enum for all available metrics."""
    REQUEST = "requests_total"
    HEALTHCHECK = "healthcheck_total"
    LLM_INVOCATIONS = "llm_invocations_total"

    def get_description(self) -> str:
        """Get the description for this metric."""
        descriptions = {
            CounterMetricName.REQUEST: "Total number of requests to the memobase server",
            CounterMetricName.HEALTHCHECK: "Total number of healthcheck requests to the memobase server",
            CounterMetricName.LLM_INVOCATIONS: "Total number of LLM invocations",
        }
        return descriptions[self]
    
    def get_metric_name(self) -> str:
        """Get the full metric name with prefix."""
        return f"memobase_server_{self.value}"

class HistogramMetricName(Enum):
    """Enum for histogram metrics."""
    LLM_LATENCY_MS = "llm_latency"

    def get_description(self) -> str:
        """Get the description for this metric."""
        descriptions = {
            HistogramMetricName.LLM_LATENCY_MS: "Latency of the LLM in milliseconds",
        }
        return descriptions[self]
    
    def get_metric_name(self) -> str:
        """Get the full metric name with prefix."""
        return f"memobase_server_{self.value}"

class ObservableGaugeMetricName(Enum):
    """Enum for observable gauge metrics."""
    INPUT_TOKEN_COUNT = "input_token_count"
    OUTPUT_TOKEN_COUNT = "output_token_count"

    def get_description(self) -> str:
        """Get the description for this metric."""
        descriptions = {
            ObservableGaugeMetricName.INPUT_TOKEN_COUNT: "Number of input tokens",
            ObservableGaugeMetricName.OUTPUT_TOKEN_COUNT: "Number of output tokens",
        }
        return descriptions[self]
    
    def get_metric_name(self) -> str:
        """Get the full metric name with prefix."""
        return f"memobase_server_{self.value}"

class TelemetryManager:
    """Manages telemetry setup and metrics for the memobase server."""
    
    def __init__(self, service_name: str = "memobase-server", prometheus_port: int = 9464):
        self.service_name = service_name
        self.prometheus_port = prometheus_port
        self.metrics: Dict[CounterMetricName | HistogramMetricName | ObservableGaugeMetricName,
                            Counter | Histogram | ObservableGauge] = {}
        self._meter = None
        # Store the latest values for observable gauges
        self._gauge_values: Dict[ObservableGaugeMetricName, Dict[str, float]] = {
            metric: {} for metric in ObservableGaugeMetricName
        }
        
    def setup_telemetry(self) -> None:
        """Initialize OpenTelemetry with Prometheus exporter."""
        resource = Resource(attributes={SERVICE_NAME: self.service_name})
        reader = PrometheusMetricReader()
        provider = MeterProvider(resource=resource, metric_readers=[reader])
        metrics.set_meter_provider(provider)
        
        # Start Prometheus HTTP server
        start_http_server(self.prometheus_port)
        
        # Initialize meter
        self._meter = metrics.get_meter(self.service_name)
        
    def setup_metrics(self) -> None:
        """Initialize all metrics."""
        if not self._meter:
            raise RuntimeError("Call setup_telemetry() before setup_metrics()")
            
        # Create counters
        for metric in CounterMetricName:
            self.metrics[metric] = self._meter.create_counter(
                metric.get_metric_name(),
                unit="1",
                description=metric.get_description(),
            )
        
        # Create histogram for latency
        for metric in HistogramMetricName:
            self.metrics[metric] = self._meter.create_histogram(
                metric.get_metric_name(),
                unit="ms",
                description=metric.get_description(),
            )
        
        # Create observable gauges for token counts
        for metric in ObservableGaugeMetricName:
            def make_callback(metric_name):
                def callback(options: CallbackOptions):
                    values = self._gauge_values[metric_name]
                    for value in values.values():
                        yield Observation(value["value"], value["attributes"])
                return callback

            self.metrics[metric] = self._meter.create_observable_gauge(
                metric.get_metric_name(),
                unit="1",
                description=metric.get_description(),
                callbacks=[make_callback(metric)]
            )
    
    def increment_counter_metric(self, metric: CounterMetricName, value: int = 1, attributes: Dict[str, str] = None) -> None:
        """Increment a counter metric."""
        if metric not in self.metrics:
            raise KeyError(f"Metric {metric} not initialized")
        self.metrics[metric].add(value, attributes)
    
    def record_histogram_metric(self, metric: HistogramMetricName, value: float, attributes: Dict[str, str] = None) -> None:
        """Record a histogram metric value."""
        if metric not in self.metrics:
            raise KeyError(f"Metric {metric} not initialized")
        self.metrics[metric].record(value, attributes)
    
    def set_gauge_metric(self, metric: ObservableGaugeMetricName, value: float, attributes: Dict[str, str] = None) -> None:
        """Set an observable gauge metric."""
        if metric not in self.metrics:
            raise KeyError(f"Metric {metric} not initialized")
        
        # Store the value with its attributes
        attr_key = attributes["project_id"]
        self._gauge_values[metric][attr_key] = {
            "value": value,
            "attributes": attributes
        }


# Create a global instance
telemetry_manager = TelemetryManager()
telemetry_manager.setup_telemetry()
telemetry_manager.setup_metrics()

