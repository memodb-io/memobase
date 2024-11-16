import json
import asyncio
from typing import Callable, Optional, List, Dict, Any, Awaitable
from ..utils import get_encoded_tokens
from ..env import CONFIG, LOG
from ..models.utils import Promise
from ..models.response import CODE
from .openai import openai_complete
from ..dashboard.capture_key import capture_int_key


# TODO: add TPM/Rate limiter
async def llm_complete(
    prompt, system_prompt=None, history_messages=[], json_mode=False, **kwargs
) -> Promise[str | dict]:
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    try:
        results = await openai_complete(
            CONFIG.best_llm_model,
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            **kwargs,
        )
    except Exception as e:
        LOG.error(f"Error in llm_complete: {e}")
        return Promise.reject(CODE.SERVICE_UNAVAILABLE, f"Error in llm_complete: {e}")

    in_tokens = len(
        get_encoded_tokens(
            prompt + system_prompt + "\n".join([m["content"] for m in history_messages])
        )
    )
    out_tokens = len(get_encoded_tokens(results))

    capture_int_key("openai_llm_input_tokens", in_tokens)
    capture_int_key("openai_llm_output_tokens", out_tokens)

    if not json_mode:
        return Promise.resolve(results)
    return Promise.resolve(json.loads(results))


# TODO: llm abstraction
# LLMFunc = Callable[
#     [
#         str,  # model
#         str,  # prompt
#         Optional[str],  # system_prompt
#         List[Dict[str, str]],  # history_messages
#         Any,  # **kwargs
#     ],
#     Awaitable[str],
# ]

# _llm_api_style_registries: dict[str, LLMFunc] = {
#     "openai": openai_complete,
# }


# @dataclass
# class LLMFactory:
#     api_style: str = "openai"
#     model: str = "gpt-4o"

#     def __call__(self, *args, **kwargs):
#         return _llm_api_style_registries[self.api_style](*args, **kwargs)
