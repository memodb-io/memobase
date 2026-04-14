import numpy as np
from typing import Literal
from .utils import get_openai_async_client_instance
from ...env import LOG


EMBEDDING_BATCH_SIZE = 10  # DashScope 等供应商限制单次最多 10 条


async def openai_embedding(
    model: str, texts: list[str], phase: Literal["query", "document"] = "document"
) -> np.ndarray:
    openai_async_client = get_openai_async_client_instance()

    all_embeddings = []
    total_prompt_tokens = 0
    total_total_tokens = 0

    for i in range(0, len(texts), EMBEDDING_BATCH_SIZE):
        batch = texts[i : i + EMBEDDING_BATCH_SIZE]
        response = await openai_async_client.embeddings.create(
            model=model, input=batch, encoding_format="float"
        )
        all_embeddings.extend([dp.embedding for dp in response.data])
        total_prompt_tokens += getattr(response.usage, "prompt_tokens", 0) or 0
        total_total_tokens += getattr(response.usage, "total_tokens", 0) or 0

    LOG.info(f"OpenAI embedding, {model}, {phase}, {total_prompt_tokens}/{total_total_tokens}, batches={-(-len(texts) // EMBEDDING_BATCH_SIZE)}")
    return np.array(all_embeddings)
