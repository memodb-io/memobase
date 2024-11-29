import json
import asyncio
from typing import Callable, Optional, List, Dict, Any, Awaitable
from ..prompts.utils import convert_response_to_json
from ..utils import get_encoded_tokens
from ..env import CONFIG, LOG
from ..models.utils import Promise
from ..models.response import CODE
from .openai import openai_complete
from ..dashboard.capture_key import capture_int_key


FACTORIES = {"openai": openai_complete}
assert CONFIG.llm_style in FACTORIES, f"Unsupported LLM style: {CONFIG.llm_style}"


# TODO: add TPM/Rate limiter
async def llm_complete(
    prompt, system_prompt=None, history_messages=[], json_mode=False, **kwargs
) -> Promise[str | dict]:
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    try:
        results = await FACTORIES[CONFIG.llm_style](
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

    await capture_int_key(f"{CONFIG.llm_style}_llm_input_tokens", in_tokens)
    await capture_int_key(f"{CONFIG.llm_style}_llm_output_tokens", out_tokens)

    if not json_mode:
        return Promise.resolve(results)
    parse_dict = convert_response_to_json(results)
    if parse_dict is not None:
        return Promise.resolve(parse_dict)
    else:
        return Promise.reject(
            CODE.UNPROCESSABLE_ENTITY, "Failed to parse JSON response"
        )


if __name__ == "__main__":
    import asyncio

    print(
        asyncio.run(
            llm_complete(
                "你好",
                '回复{"response": 我是MemoBase}如果用户向你说你好',
                json_mode=True,
            )
        ).data()
    )

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
