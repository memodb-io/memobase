import time
from typing import Literal
import numpy as np
from traceback import format_exc
from ...env import CONFIG, LOG
from ...models.utils import Promise
from ...models.response import CODE
from ...models.database import DEFAULT_PROJECT_ID
from .jina_embedding import jina_embedding
from .openai_embedding import openai_embedding
from .lmstudio_embedding import lmstudio_embedding
from .ollama_embedding import ollama_embedding
from ...telemetry import telemetry_manager, HistogramMetricName, CounterMetricName
from ...utils import get_encoded_tokens

FACTORIES = {"openai": openai_embedding, "jina": jina_embedding, "lmstudio": lmstudio_embedding, "ollama": ollama_embedding}
assert (
    CONFIG.embedding_provider in FACTORIES
), f"Unsupported embedding provider: {CONFIG.embedding_provider}"


async def check_embedding_sanity():
    if not CONFIG.enable_event_embedding:
        LOG.info("Event embedding is disabled, skipping sanity check.")
        return
    r = await get_embedding(DEFAULT_PROJECT_ID, ["Hello, world!"])
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
    LOG.info(f"Embedding dimension matched: {embedding_dim}")


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
        LOG.error(f"Error in get_embedding: {e} {format_exc()}")
        return Promise.reject(CODE.SERVICE_UNAVAILABLE, f"Error in get_embedding: {e}")
    embedding_tokens = len(get_encoded_tokens("\n".join(texts)))
    telemetry_manager.increment_counter_metric(
        CounterMetricName.EMBEDDING_TOKENS,
        embedding_tokens,
        {"project_id": project_id},
    )
    telemetry_manager.record_histogram_metric(
        HistogramMetricName.EMBEDDING_LATENCY_MS,
        latency_ms,
        {"project_id": project_id},
    )
    return Promise.resolve(results)
