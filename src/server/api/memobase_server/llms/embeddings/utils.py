from openai import AsyncOpenAI
from httpx import AsyncClient
from ...env import CONFIG

_global_openai_async_client = None
_global_jina_async_client = None
_global_lmstudio_async_client = None
_global_ollama_async_client = None


def get_openai_async_client_instance() -> AsyncOpenAI:
    global _global_openai_async_client
    if _global_openai_async_client is None:
        _global_openai_async_client = AsyncOpenAI(
            base_url=CONFIG.embedding_base_url,
            api_key=CONFIG.embedding_api_key,
        )
    return _global_openai_async_client


def get_jina_async_client_instance() -> AsyncClient:
    global _global_jina_async_client
    if _global_jina_async_client is None:
        _global_jina_async_client = AsyncClient(
            base_url=CONFIG.embedding_base_url,
            headers={"Authorization": f"Bearer {CONFIG.embedding_api_key}"},
        )
    return _global_jina_async_client

def get_lmstudio_async_client_instance() -> AsyncClient:
    global _global_lmstudio_async_client
    if _global_lmstudio_async_client is None:
        _global_lmstudio_async_client = AsyncClient(
            base_url=CONFIG.embedding_base_url,
            headers={"Authorization": f"Bearer {CONFIG.embedding_api_key}"},
        )
    return _global_lmstudio_async_client

def get_ollama_async_client_instance() -> AsyncClient:
    global _global_ollama_async_client
    if _global_ollama_async_client is None:
        _global_ollama_async_client = AsyncClient(
            base_url=CONFIG.embedding_base_url,
            headers={"Authorization": f"Bearer {CONFIG.embedding_api_key}"},
        )
    return _global_ollama_async_client

