import hashlib
from .utils import get_doubao_async_client_instance, exclude_special_kwargs
from ..connectors import get_redis_client
from ..env import LOG

CONTEXT_EXPIRE_TIME = 60 * 60 * 24
BEFORE_EXPIRE_TIME = 10


def compute_prompt_hash(system_prompt: str) -> str:
    return hashlib.md5(system_prompt.encode()).hexdigest()


async def doubao_cache_create_context_and_save(
    model, system_prompt, context_name
) -> str:
    prompt_hash = compute_prompt_hash(system_prompt)
    redis_key = f"memobase::doubao_context_id::{model}::{prompt_hash}"
    async with get_redis_client() as redis_client:
        context_id = await redis_client.get(redis_key)
        if context_id is not None:
            await redis_client.expire(
                redis_key, CONTEXT_EXPIRE_TIME - BEFORE_EXPIRE_TIME
            )
            if isinstance(context_id, bytes):
                return context_id.decode()
            return context_id
    doubao_client = get_doubao_async_client_instance()
    try:
        response = await doubao_client.context.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                }
            ],
            mode="common_prefix",
            ttl=CONTEXT_EXPIRE_TIME,
        )
    except Exception as e:
        LOG.error(f"Error creating context: {e}")
        return None
    async with get_redis_client() as redis_client:
        await redis_client.set(
            redis_key, response.id, ex=CONTEXT_EXPIRE_TIME - BEFORE_EXPIRE_TIME
        )
    LOG.info(f"Created context cache for {context_name}")
    return response.id


async def doubao_cache_complete(
    model, prompt, system_prompt=None, history_messages=[], **kwargs
) -> str:
    sp_args, kwargs = exclude_special_kwargs(kwargs)
    prompt_id = sp_args.get("prompt_id", None)
    assert prompt_id is not None, "prompt_id is required"

    context_id = await doubao_cache_create_context_and_save(
        model, system_prompt, prompt_id
    )

    doubao_async_client = get_doubao_async_client_instance()
    messages = []

    if system_prompt and context_id is None:
        # when context_id is None, we use system prompt to create context
        messages.append({"role": "system", "content": system_prompt})
    messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})

    if context_id is None:
        response = await doubao_async_client.chat.completions.create(
            model=model, messages=messages, timeout=120, **kwargs
        )
        return response.choices[0].message.content
    else:
        response = await doubao_async_client.context.completions.create(
            model=model, messages=messages, context_id=context_id, timeout=120, **kwargs
        )
        LOG.info(
            f"Cached {prompt_id} {model} {response.usage.prompt_tokens_details.cached_tokens}/{response.usage.prompt_tokens}"
        )
        return response.choices[0].message.content
