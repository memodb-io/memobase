from enum import Enum, auto
from typing import Dict

from prometheus_client import start_http_server
from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics._internal.instrument import Counter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource


class CounterMetricName(Enum):
    """Enum for all available metrics."""
    REQUEST = "requests_total"
    HEALTHCHECK = "healthcheck_total"

    def get_description(self) -> str:
        """Get the description for this metric."""
        descriptions = {
            CounterMetricName.REQUEST: "Total number of requests to the memobase server",
            CounterMetricName.HEALTHCHECK: "Total number of healthcheck requests to the memobase server",
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
        self.metrics: Dict[CounterMetricName, Counter] = {}
        self._meter = None
        
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
        """Initialize all metrics counters."""
        if not self._meter:
            raise RuntimeError("Call setup_telemetry() before setup_metrics()")
            
        # Create all metrics defined in MetricCounterName enum
        for metric in CounterMetricName:
            self.metrics[metric] = self._meter.create_counter(
                metric.get_metric_name(),
                unit="1",
                description=metric.get_description(),
            )
    
    def increment_counter_metric(self, metric: CounterMetricName, value: int = 1, attributes: Dict[str, str] = None) -> None:
        """Increment a metric by the specified value."""
        if metric not in self.metrics:
            raise KeyError(f"Metric {metric} not initialized")
        self.metrics[metric].add(value, attributes)
    
    def get_counter_metric(self, metric: CounterMetricName) -> Counter:
        """Get a metric by name."""
        if metric not in self.metrics:
            raise KeyError(f"Metric {metric} not initialized")
        return self.metrics[metric]


# Create a global instance
telemetry_manager = TelemetryManager()
telemetry_manager.setup_telemetry()
telemetry_manager.setup_metrics()

