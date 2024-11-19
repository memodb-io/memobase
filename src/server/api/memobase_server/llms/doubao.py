from .utils import get_doubao_async_client_instance
from ..env import CONFIG


async def doubao_complete(
    model, prompt, system_prompt=None, history_messages=[], **kwargs
) -> str:
    doubao_async_client = get_doubao_async_client_instance()
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})

    response = await doubao_async_client.chat.completions.create(
        model=model, messages=messages, **kwargs
    )
    return response.choices[0].message.content
