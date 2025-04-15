import numpy as np
from typing import Literal
from .utils import get_openai_async_client_instance
from ...env import CONFIG


async def openai_embedding(
    model: str, texts: list[str], phase: Literal["query", "document"] = "document"
) -> np.ndarray:
    openai_async_client = get_openai_async_client_instance()
    response = await openai_async_client.embeddings.create(
        model=model, input=texts, encoding_format="float"
    )
    return np.array([dp.embedding for dp in response.data])
