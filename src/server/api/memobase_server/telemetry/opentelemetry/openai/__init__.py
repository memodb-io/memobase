from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from typing import Collection
from opentelemetry.semconv.schemas import Schemas
from opentelemetry.metrics import get_meter
from opentelemetry.instrumentation.utils import unwrap
from wrapt import wrap_function_wrapper
from .instruments import Instruments
from .patch import chat_completions, async_chat_completions
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource, DEPLOYMENT_ENVIRONMENT
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry import metrics
from opentelemetry.sdk.environment_variables import (
    OTEL_EXPORTER_OTLP_ENDPOINT,
)
import os
import logging

LOG = logging.getLogger(__name__)

def init(
        deployment_environment: str = "default",
        otlp_endpoint: str = None,
        service_name: str = "memobase"
    ):

    resource = Resource(attributes={
        SERVICE_NAME: service_name,
        DEPLOYMENT_ENVIRONMENT: deployment_environment
    })
    if otlp_endpoint is not None:
        os.environ[OTEL_EXPORTER_OTLP_ENDPOINT] = otlp_endpoint

    if os.getenv(OTEL_EXPORTER_OTLP_ENDPOINT):
        metric_exporter = OTLPMetricExporter()
    else:
        metric_exporter = ConsoleMetricExporter()

    # metric_reader = PeriodicExportingMetricReader(metric_exporter)
    # meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    # # set global meter provider
    # metrics.set_meter_provider(meter_provider)

    OpenAIInstrumentor().instrument(
        deployment_environment=deployment_environment
    )
    LOG.info("OpenAI telemetry initialized")


_instruments = ("openai >= 1.26.0",)

class OpenAIInstrumentor(BaseInstrumentor):
    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments
    
    def _instrument(self, **kwargs):
        # get global meter
        self._meter = get_meter(__name__)

        instrument = Instruments(self._meter)
        deployment_environment = kwargs.get("deployment_environment")

        wrap_function_wrapper(
            module="openai.resources.chat.completions",
            name="Completions.create",
            wrapper=chat_completions(
               instrument, deployment_environment
            ),
        )

        wrap_function_wrapper(
            module="openai.resources.chat.completions",
            name="AsyncCompletions.create",
            wrapper=async_chat_completions(
                instrument, deployment_environment
            ),
        )

    @staticmethod
    def _uninstrument(self, **kwargs):
        import openai 

        unwrap(openai.resources.chat.completions.Completions, "create")
        unwrap(openai.resources.chat.completions.AsyncCompletions, "create")