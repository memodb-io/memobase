import numpy as np
from typing import Literal
from ...errors import ExternalAPIError
from ...env import CONFIG, LOG
from .utils import get_lmstudio_async_client_instance

LMSTUDIO_TASK = {
    "query": "retrieval.query",
    "document": "retrieval.passage",
}

async def lmstudio_embedding(
    model: str, texts: list[str], phase: Literal["query", "document"] = "document"
) -> np.ndarray:
    lmstudio_async_client = get_lmstudio_async_client_instance()
    response = await lmstudio_async_client.post(
        "/embeddings",
        json={
            "model": model,
            "input": texts,
            "task": LMSTUDIO_TASK[phase],
            "truncate": True,
            "dimensions": CONFIG.embedding_dim,
        },
        timeout=20,
    )
    if response.status_code != 200:
        raise ExternalAPIError(f"Failed to embed texts: {response.text}")
    data = response.json()
    LOG.info(
        f"lmstudio embedding, {model}, {phase}, {data['usage']['prompt_tokens']}/{data['usage']['total_tokens']}"
    )
    return np.array([dp["embedding"] for dp in data["data"]])
