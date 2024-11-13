import numpy as np
from dataclasses import dataclass
from ..env import CONFIG
from .utils import get_openai_async_client_instance, get_openai_retry_decorator


@dataclass
class EmbeddingFunc:
    embedding_dim: int
    max_token_size: int
    func: callable

    async def __call__(self, *args, **kwargs) -> np.ndarray:
        return await self.func(*args, **kwargs)


def wrap_embedding_func_with_attrs(**kwargs):
    """Wrap a function with attributes"""

    def final_decro(func) -> EmbeddingFunc:
        new_func = EmbeddingFunc(**kwargs, func=func)
        return new_func

    return final_decro


@wrap_embedding_func_with_attrs(
    embedding_dim=CONFIG.embedding_dim, max_token_size=CONFIG.embedding_max_token_size
)
@get_openai_retry_decorator()
async def get_embedding(texts: list[str]) -> np.ndarray:
    openai_async_client = get_openai_async_client_instance()
    response = await openai_async_client.embeddings.create(
        model=CONFIG.embedding_model, input=texts, encoding_format="float"
    )
    return np.array([dp.embedding for dp in response.data])
