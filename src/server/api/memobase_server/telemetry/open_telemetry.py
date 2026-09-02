from enum import Enum
from typing import Dict
import os
import socket
from prometheus_client import start_http_server
from opentelemetry import metrics, trace
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics._internal.instrument import (
    Counter,
    Histogram,
    Gauge,
)
from opentelemetry.sdk.resources import SERVICE_NAME, Resource, DEPLOYMENT_ENVIRONMENT
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from functools import wraps
from ..env import LOG, CONFIG


def no_raise_exception(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            LOG.error(f"Error in {func.__name__}: {e}")

    return wrapper


class CounterMetricName(Enum):
    """Enum for all available metrics."""

    REQUEST = "requests_total"
    HEALTHCHECK = "healthcheck_total"
    LLM_INVOCATIONS = "llm_invocations_total"
    LLM_TOKENS_INPUT = "llm_input_tokens_total"
    LLM_TOKENS_OUTPUT = "llm_output_tokens_total"
    EMBEDDING_TOKENS = "embedding_tokens_total"
    MEMORY_BLOBS_INSERTED = "memory_blobs_inserted_total"
    MEMORY_BLOBS_DELETED = "memory_blobs_deleted_total"
    MEMORY_PROFILES_UPDATED = "memory_profiles_updated_total"
    MEMORY_USERS_CREATED = "memory_users_created_total"
    MEMORY_USERS_DELETED = "memory_users_deleted_total"

    def get_description(self) -> str:
        """Get the description for this metric."""
        descriptions = {
            CounterMetricName.REQUEST: "Total number of requests to the memobase server",
            CounterMetricName.HEALTHCHECK: "Total number of healthcheck requests to the memobase server",
            CounterMetricName.LLM_INVOCATIONS: "Total number of LLM invocations",
            CounterMetricName.LLM_TOKENS_INPUT: "Total number of input tokens",
            CounterMetricName.LLM_TOKENS_OUTPUT: "Total number of output tokens",
            CounterMetricName.EMBEDDING_TOKENS: "Total number of embedding tokens",
            CounterMetricName.MEMORY_BLOBS_INSERTED: "Total number of memory blobs inserted",
            CounterMetricName.MEMORY_BLOBS_DELETED: "Total number of memory blobs deleted",
            CounterMetricName.MEMORY_PROFILES_UPDATED: "Total number of memory profiles updated",
            CounterMetricName.MEMORY_USERS_CREATED: "Total number of memory users created",
            CounterMetricName.MEMORY_USERS_DELETED: "Total number of memory users deleted",
        }
        return descriptions[self]

    def get_metric_name(self) -> str:
        """Get the full metric name with prefix."""
        return f"memobase_server_{self.value}"


class HistogramMetricName(Enum):
    """Enum for histogram metrics."""

    LLM_LATENCY_MS = "llm_latency"
    EMBEDDING_LATENCY_MS = "embedding_latency"
    REQUEST_LATENCY_MS = "request_latency"
    MEMORY_QUERY_LATENCY_MS = "memory_query_latency"
    MEMORY_INSERT_LATENCY_MS = "memory_insert_latency"
    MEMORY_FLUSH_LATENCY_MS = "memory_flush_latency"
    MEMORY_PROFILE_COUNT = "memory_profile_result_count"

    def get_description(self) -> str:
        """Get the description for this metric."""
        descriptions = {
            HistogramMetricName.LLM_LATENCY_MS: "Latency of the LLM in milliseconds",
            HistogramMetricName.EMBEDDING_LATENCY_MS: "Latency of the embedding in milliseconds",
            HistogramMetricName.REQUEST_LATENCY_MS: "Latency of the request in milliseconds",
            HistogramMetricName.MEMORY_QUERY_LATENCY_MS: "Latency of memory profile queries in milliseconds",
            HistogramMetricName.MEMORY_INSERT_LATENCY_MS: "Latency of memory blob insert operations in milliseconds",
            HistogramMetricName.MEMORY_FLUSH_LATENCY_MS: "Latency of memory buffer flush operations in milliseconds",
            HistogramMetricName.MEMORY_PROFILE_COUNT: "Number of profiles returned per query",
        }
        return descriptions[self]

    def get_unit(self) -> str:
        """Get the unit for this metric."""
        if self == HistogramMetricName.MEMORY_PROFILE_COUNT:
            return "1"
        return "ms"

    def get_metric_name(self) -> str:
        """Get the full metric name with prefix."""
        return f"memobase_server_{self.value}"


class GaugeMetricName(Enum):
    """Enum for gauge metrics."""

    INPUT_TOKEN_COUNT = "input_token_count_per_call"
    OUTPUT_TOKEN_COUNT = "output_token_count_per_call"

    def get_description(self) -> str:
        """Get the description for this metric."""
        descriptions = {
            GaugeMetricName.INPUT_TOKEN_COUNT: "Number of input tokens per call",
            GaugeMetricName.OUTPUT_TOKEN_COUNT: "Number of output tokens per call",
        }
        return descriptions[self]

    def get_metric_name(self) -> str:
        """Get the full metric name with prefix."""
        return f"memobase_server_{self.value}"


class TelemetryManager:
    """Manages telemetry setup and metrics for the memobase server."""

    def __init__(
        self,
        service_name: str = "memobase-server",
        prometheus_port: int = 9464,
        deployment_environment: str = "default",
    ):
        self._service_name = service_name
        self._prometheus_port = prometheus_port
        self._deployment_environment = deployment_environment
        self._metrics: Dict[
            CounterMetricName | HistogramMetricName | GaugeMetricName,
            Counter | Histogram | Gauge,
        ] = None
        self._meter = None
        self._tracer_provider = None

    def setup_telemetry(self) -> None:
        """Initialize OpenTelemetry with Prometheus exporter and optional OTLP tracing."""
        resource = Resource(
            attributes={
                SERVICE_NAME: self._service_name,
                DEPLOYMENT_ENVIRONMENT: self._deployment_environment,
            }
        )
        reader = PrometheusMetricReader()
        provider = MeterProvider(resource=resource, metric_readers=[reader])
        metrics.set_meter_provider(provider)

        # Start Prometheus HTTP server, skip if port is already in use
        try:
            start_http_server(self._prometheus_port)
        except OSError as e:
            if e.errno == 48:  # Address already in use
                LOG.warning(
                    f"Prometheus HTTP server already running on port {self._prometheus_port}"
                )
            else:
                raise e

        # Initialize meter
        self._meter = metrics.get_meter(self._service_name)

        # Setup OTLP tracing if endpoint is configured
        otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "")
        if otlp_endpoint:
            try:
                from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
                tracer_provider = TracerProvider(resource=resource)
                otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
                tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
                trace.set_tracer_provider(tracer_provider)
                self._tracer_provider = tracer_provider
                LOG.info(f"OTLP tracing enabled, exporting to {otlp_endpoint}")
            except Exception as e:
                LOG.warning(f"Failed to setup OTLP tracing: {e}. Tracing will be disabled.")
        else:
            LOG.info("OTEL_EXPORTER_OTLP_ENDPOINT not set, tracing disabled (using NoOp tracer)")

    def _construct_attributes(self, **kwargs) -> Dict[str, str]:

        # if os.environ.get("POD_IP"):
        #     # use k8s downward API to get the pod ip
        #     pod_ip = os.environ.get("POD_IP", None)
        # else:
        #     # use the hostname to get the ip address
        #     hostname = socket.gethostname()
        #     pod_ip = socket.gethostbyname(hostname)
        pod_ip = os.environ.get("POD_IP", None)
        return {
            DEPLOYMENT_ENVIRONMENT: self._deployment_environment,
            "memobase_server_ip": pod_ip,
            **kwargs,
        }

    def setup_metrics(self) -> None:
        """Initialize all metrics."""
        if not self._meter:
            raise RuntimeError("Call setup_telemetry() before setup_metrics()")

        if self._metrics is None:
            self._metrics = {}

        # Create counters
        for metric in CounterMetricName:
            self._metrics[metric] = self._meter.create_counter(
                metric.get_metric_name(),
                unit="1",
                description=metric.get_description(),
            )

        # Create histogram for latency
        for metric in HistogramMetricName:
            self._metrics[metric] = self._meter.create_histogram(
                metric.get_metric_name(),
                unit=metric.get_unit(),
                description=metric.get_description(),
            )

        # Create gauges for token counts
        for metric in GaugeMetricName:
            self._metrics[metric] = self._meter.create_gauge(
                metric.get_metric_name(),
                unit="1",
                description=metric.get_description(),
            )

    @no_raise_exception
    def increment_counter_metric(
        self,
        metric: CounterMetricName,
        value: int = 1,
        attributes: Dict[str, str] = None,
    ) -> None:
        """Increment a counter metric."""
        self._validate_metric(metric)
        complete_attributes = self._construct_attributes(**(attributes or {}))
        self._metrics[metric].add(value, complete_attributes)

    @no_raise_exception
    def record_histogram_metric(
        self,
        metric: HistogramMetricName,
        value: float,
        attributes: Dict[str, str] = None,
    ) -> None:
        """Record a histogram metric value."""
        self._validate_metric(metric)
        complete_attributes = self._construct_attributes(**(attributes or {}))
        self._metrics[metric].record(value, complete_attributes)

    @no_raise_exception
    def set_gauge_metric(
        self,
        metric: GaugeMetricName,
        value: float,
        attributes: Dict[str, str] = None,
    ) -> None:
        """Set a gauge metric."""
        self._validate_metric(metric)
        complete_attributes = self._construct_attributes(**(attributes or {}))
        self._metrics[metric].set(value, complete_attributes)

    def get_tracer(self, name: str):
        """Get a tracer. Returns a NoOp tracer if tracing is not configured."""
        return trace.get_tracer(name)

    def _validate_metric(self, metric) -> None:
        """Validate if the metric is initialized."""
        if metric not in self._metrics:
            raise KeyError(f"Metric {metric} not initialized")


# Create a global instance
telemetry_manager = TelemetryManager(
    deployment_environment=CONFIG.telemetry_deployment_environment
)
telemetry_manager.setup_telemetry()
telemetry_manager.setup_metrics()
