from .utils import exclude_special_kwargs, get_openai_async_client_instance
from ..env import LOG


async def openai_complete(
    model, prompt, system_prompt=None, history_messages=[], thinking_enable=None, **kwargs
) -> str:
    sp_args, kwargs = exclude_special_kwargs(kwargs)
    prompt_id = sp_args.get("prompt_id", None)

    openai_async_client = get_openai_async_client_instance()
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})

    # thinking 控制：仅当 thinking_enable 显式配置时才注入
    # DashScope/Qwen 使用 extra_body={"enable_thinking": bool}
    # thinking_enable=None 时不干预，让 API 使用默认行为
    if thinking_enable is not None:
        extra_body = kwargs.pop("extra_body", {}) or {}
        extra_body["enable_thinking"] = bool(thinking_enable)
        kwargs["extra_body"] = extra_body

    response = await openai_async_client.chat.completions.create(
        model=model, messages=messages, timeout=120, **kwargs
    )
    cached_tokens = getattr(response.usage.prompt_tokens_details, "cached_tokens", None)
    LOG.info(
        f"Cached {prompt_id} {model} {cached_tokens}/{response.usage.prompt_tokens}"
    )
    return response.choices[0].message.content
