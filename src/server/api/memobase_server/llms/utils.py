from openai import APIConnectionError, RateLimitError, AsyncOpenAI
from volcenginesdkarkruntime import AsyncArk, Ark

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from ..env import CONFIG

_global_openai_async_client = None
_global_doubao_async_client = None
_global_doubao_client = None


def get_openai_retry_decorator():
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((RateLimitError, APIConnectionError)),
    )


def get_openai_async_client_instance() -> AsyncOpenAI:
    global _global_openai_async_client
    if _global_openai_async_client is None:
        _global_openai_async_client = AsyncOpenAI(
            base_url=CONFIG.llm_base_url,
            api_key=CONFIG.llm_api_key,
        )
    return _global_openai_async_client


def get_doubao_async_client_instance() -> AsyncArk:
    global _global_doubao_async_client

    if _global_doubao_async_client is None:
        _global_doubao_async_client = AsyncArk(api_key=CONFIG.llm_api_key)
    return _global_doubao_async_client


def get_doubao_client_instance() -> Ark:
    global _global_doubao_client
    if _global_doubao_client is None:
        _global_doubao_client = Ark(api_key=CONFIG.llm_api_key)
    return _global_doubao_client


def exclude_special_kwargs(kwargs: dict):
    prompt_id = kwargs.pop("prompt_id", None)
    return {"prompt_id": prompt_id}, kwargs
