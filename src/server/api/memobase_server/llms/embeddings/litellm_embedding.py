import numpy as np
from typing import Literal
from ...env import LOG, CONFIG


async def litellm_embedding(
    model: str, texts: list[str], phase: Literal["query", "document"] = "document"
) -> np.ndarray:
    import litellm

    embedding_kwargs = {"drop_params": True}
    if CONFIG.embedding_dim:
        embedding_kwargs["dimensions"] = CONFIG.embedding_dim

    response = await litellm.aembedding(
        model=model,
        input=texts,
        **embedding_kwargs,
    )

    prompt_tokens = getattr(response.usage, "prompt_tokens", None)
    total_tokens = getattr(response.usage, "total_tokens", None)
    LOG.info(f"LiteLLM embedding, {model}, {phase}, {prompt_tokens}/{total_tokens}")
    return np.array([dp["embedding"] for dp in response.data])
