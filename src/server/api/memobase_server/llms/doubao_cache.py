from .utils import (
    get_doubao_async_client_instance,
    exclude_special_kwargs,
    get_doubao_client_instance,
)


async def doubao_cache_complete(
    model, prompt, system_prompt=None, history_messages=[], **kwargs
) -> str:
    sp_args, kwargs = exclude_special_kwargs(kwargs)
    context_id = sp_args.get("context_id", None)

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
        print(response.usage)
        return response.choices[0].message.content


def doubao_cache_create_context(model, system_prompt) -> str:
    doubao_client = get_doubao_client_instance()
    response = doubao_client.context.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            }
        ],
        mode="common_prefix",
    )
    return response.id
