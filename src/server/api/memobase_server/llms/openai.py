import numpy as np

from openai import AsyncOpenAI, AsyncAzureOpenAI, APIConnectionError, RateLimitError

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from .utils import wrap_embedding_func_with_attrs
from ..env import CONFIG

_global_openai_async_client = None
_global_azure_openai_async_client = None


def get_openai_async_client_instance():
    global _global_openai_async_client
    if _global_openai_async_client is None:
        _global_openai_async_client = AsyncOpenAI(
            base_url=CONFIG.openai_base_url,
            api_key=CONFIG.openai_api_key,
        )
    return _global_openai_async_client


def get_azure_openai_async_client_instance():
    raise NotImplementedError("Azure OpenAI is not supported yet")
    global _global_azure_openai_async_client
    if _global_azure_openai_async_client is None:
        _global_azure_openai_async_client = AsyncAzureOpenAI(
            base_url=CONFIG.azure_openai_base_url,
            api_key=CONFIG.azure_openai_api_key,
        )
    return _global_azure_openai_async_client


def _get_openai_retry_decorator():
    return retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((RateLimitError, APIConnectionError)),
    )


@_get_openai_retry_decorator()
async def openai_complete_if_cache(
    model, prompt, system_prompt=None, history_messages=[], **kwargs
) -> str:
    openai_async_client = get_openai_async_client_instance()
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})

    response = await openai_async_client.chat.completions.create(
        model=model, messages=messages, **kwargs
    )
    return response.choices[0].message.content


@wrap_embedding_func_with_attrs(embedding_dim=1536, max_token_size=8192)
@_get_openai_retry_decorator()
async def openai_embedding(texts: list[str]) -> np.ndarray:
    openai_async_client = get_openai_async_client_instance()
    response = await openai_async_client.embeddings.create(
        model=CONFIG.embedding_model, input=texts, encoding_format="float"
    )
    return np.array([dp.embedding for dp in response.data])


async def llm_best_complete(
    prompt, system_prompt=None, history_messages=[], **kwargs
) -> str:
    return await openai_complete_if_cache(
        CONFIG.best_llm_model,
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        **kwargs,
    )


async def llm_cheap_complete(
    prompt, system_prompt=None, history_messages=[], **kwargs
) -> str:
    return await openai_complete_if_cache(
        CONFIG.cheap_llm_model,
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        **kwargs,
    )
