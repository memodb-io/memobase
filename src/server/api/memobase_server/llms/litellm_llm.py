from .utils import exclude_special_kwargs
from ..env import LOG, CONFIG


async def litellm_complete(
    model, prompt, system_prompt=None, history_messages=[], **kwargs
) -> str:
    import litellm

    sp_args, kwargs = exclude_special_kwargs(kwargs)
    prompt_id = sp_args.get("prompt_id", None)

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})

    completion_kwargs = {"drop_params": True, **kwargs}
    if CONFIG.llm_api_key:
        completion_kwargs["api_key"] = CONFIG.llm_api_key
    if CONFIG.llm_base_url:
        completion_kwargs["api_base"] = CONFIG.llm_base_url

    response = await litellm.acompletion(
        model=model, messages=messages, timeout=120, **completion_kwargs
    )
    cached_tokens = getattr(
        getattr(response.usage, "prompt_tokens_details", None), "cached_tokens", None
    )
    LOG.info(
        f"LiteLLM {prompt_id} {model} {cached_tokens}/{response.usage.prompt_tokens}"
    )
    return response.choices[0].message.content
