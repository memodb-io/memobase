import time
from typing import Literal
import numpy as np
from ...env import CONFIG, LOG
from ...models.utils import Promise
from ...models.response import CODE
from .jina_embedding import jina_embedding
from .openai_embedding import openai_embedding
from ...telemetry import telemetry_manager, HistogramMetricName

FACTORIES = {"openai": openai_embedding, "jina": jina_embedding}
assert (
    CONFIG.embedding_provider in FACTORIES
), f"Unsupported embedding provider: {CONFIG.embedding_provider}"


async def check_embedding_sanity():
    r = await get_embedding("test", ["Hello, world!"])
    if not r.ok():
        raise ValueError(
            "Embedding API check failed! Make sure the embedding API key is valid."
        )
    d = r.data()
    embedding_dim = d.shape[-1]
    if embedding_dim != CONFIG.embedding_dim:
        raise ValueError(
            f"Embedding dimension mismatch! Expected {CONFIG.embedding_dim}, got {embedding_dim}."
        )


async def get_embedding(
    project_id: str,
    texts: list[str],
    phase: Literal["query", "document"] = "document",
    model: str = None,
) -> Promise[np.ndarray]:
    model = model or CONFIG.embedding_model
    try:
        start_time = time.time()
        results = await FACTORIES[CONFIG.embedding_provider](model, texts, phase)
        latency_ms = (time.time() - start_time) * 1000
    except Exception as e:
        LOG.error(f"Error in get_embedding: {e}")
        return Promise.reject(CODE.SERVICE_UNAVAILABLE, f"Error in get_embedding: {e}")
    telemetry_manager.record_histogram_metric(
        HistogramMetricName.EMBEDDING_LATENCY_MS,
        latency_ms,
        {"project_id": project_id},
    )
    return Promise.resolve(results)
