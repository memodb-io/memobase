import time
from contextlib import contextmanager
from opentelemetry import trace
from opentelemetry.trace import StatusCode

from .open_telemetry import telemetry_manager

_tracer = telemetry_manager.get_tracer("memobase.server")


@contextmanager
def memory_span(op_name: str, attributes: dict = None):
    """Context manager that creates a span and records latency."""
    with _tracer.start_as_current_span(op_name) as span:
        if attributes:
            for k, v in attributes.items():
                if v is not None:
                    span.set_attribute(k, str(v))
        t0 = time.monotonic()
        try:
            yield span
        except Exception as e:
            span.set_status(StatusCode.ERROR, str(e))
            raise
        finally:
            elapsed_ms = (time.monotonic() - t0) * 1000
            span.set_attribute("duration_ms", elapsed_ms)
