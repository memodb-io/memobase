from ....models.utils import Promise, CODE
from ....env import CONFIG, LOG, ProfileConfig
from ....utils import get_encoded_tokens, truncate_string
from ....llms import llm_complete
from ....models.blob import OpenAICompatibleMessage
from .types import PROMPTS, ChatInterest
from ..utils import try_json_loads


async def detect_chat_interest(
    project_id: str,
    messages: list[OpenAICompatibleMessage],
    profile_config: ProfileConfig,
) -> Promise[ChatInterest]:
    USE_LANGUAGE = "zh"
    prompt = PROMPTS[USE_LANGUAGE]["detect_interest"]

    r = await llm_complete(
        project_id,
        prompt.get_input(messages),
        system_prompt=prompt.get_prompt(),
        temperature=0.2,  # precise
        model=CONFIG.best_llm_model,
        **prompt.get_kwargs(),
    )
    if not r.ok():
        return r
    content = r.data()
    data = try_json_loads(content)
    print(data)
    if data is None:
        return Promise.reject(
            CODE.INTERNAL_SERVER_ERROR, "Unable to parse the LLM json response"
        )
    return Promise.resolve(data)
