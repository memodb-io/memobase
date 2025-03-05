from opentelemetry.semconv._incubating.metrics import gen_ai_metrics
from opentelemetry.metrics import Histogram, Meter, Counter


_GEN_AI_CLIENT_OPERATION_DURATION_BUCKETS = [
    0.01,
    0.02,
    0.04,
    0.08,
    0.16,
    0.32,
    0.64,
    1.28,
    2.56,
    5.12,
    10.24,
    20.48,
    40.96,
    81.92,
]

_GEN_AI_CLIENT_TOKEN_USAGE_BUCKETS = [
    1,
    4,
    16,
    64,
    256,
    1024,
    4096,
    16384,
    65536,
    262144,
    1048576,
    4194304,
    16777216,
    67108864,
]

class Instruments:
    def __init__(self, meter: Meter):
        # OTel Semconv
        self.client_operation_duration_histogram: Histogram = meter.create_histogram(
            name=gen_ai_metrics.GEN_AI_CLIENT_OPERATION_DURATION,
            description="GenAI operation duration",
            unit="s",
            explicit_bucket_boundaries_advisory=_GEN_AI_CLIENT_OPERATION_DURATION_BUCKETS,
        )
        self.client_token_usage_histogram: Histogram = meter.create_histogram(
            name=gen_ai_metrics.GEN_AI_CLIENT_TOKEN_USAGE,
            description="Measures number of input and output tokens used",
            unit="{token}",
            explicit_bucket_boundaries_advisory=_GEN_AI_CLIENT_TOKEN_USAGE_BUCKETS,
        )

        # Extra 
        self.requests: Counter = meter.create_counter(
            name="gen_ai.total.requests",
            description="Total number of requests to OpenAI",
            unit="1",
        )
        self.input_tokens: Counter = meter.create_counter(
            name="gen_ai.usage.input_tokens",
            description="Number of prompt tokens processed.",
            unit="1",
        )
        self.output_tokens: Counter = meter.create_counter(
            name="gen_ai.usage.output_tokens",
            description="Number of completion tokens processed.",
            unit="1",
        )

        # TODO: add cost histogram

