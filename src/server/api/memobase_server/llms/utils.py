from openai import AsyncOpenAI
from volcenginesdkarkruntime import AsyncArk
from ..env import CONFIG

_global_openai_async_client = None
_global_doubao_async_client = None


def get_openai_async_client_instance() -> AsyncOpenAI:
    global _global_openai_async_client
    if _global_openai_async_client is None:
        _global_openai_async_client = AsyncOpenAI(
            base_url=CONFIG.llm_base_url,
            api_key=CONFIG.llm_api_key,
            default_query=CONFIG.llm_openai_default_query,
            default_headers=CONFIG.llm_openai_default_header,
        )
    return _global_openai_async_client


def get_doubao_async_client_instance() -> AsyncArk:
    global _global_doubao_async_client

    if _global_doubao_async_client is None:
        _global_doubao_async_client = AsyncArk(api_key=CONFIG.llm_api_key)
    return _global_doubao_async_client


def exclude_special_kwargs(kwargs: dict):
    prompt_id = kwargs.pop("prompt_id", None)
    no_cache = kwargs.pop("no_cache", None)
    return {"prompt_id": prompt_id, "no_cache": no_cache}, kwargs
