import re
from ....models.utils import Promise, CODE
from ....env import CONFIG, LOG, ProfileConfig
from ....utils import get_encoded_tokens, truncate_string
from ....llms import llm_complete
from ....models.blob import OpenAICompatibleMessage
from ....models.response import UserStatusesData
from .types import PROMPTS, InferPlot


def extract_plot_output(content: str):
    themes = re.search(r"<themes>(.*?)</themes>", content, re.DOTALL)
    overview = re.search(r"<overview>(.*?)</overview>", content, re.DOTALL)
    timeline = re.search(r"<timeline>(.*?)</timeline>", content, re.DOTALL)
    return (
        themes.group(1).strip() if themes else None,
        overview.group(1).strip() if overview else None,
        timeline.group(1).strip() if timeline else None,
    )


async def predict_new_topics(
    project_id: str,
    messages: list[OpenAICompatibleMessage],
    latest_statuses: UserStatusesData,
    user_context: str,
    agent_context: str,
    profile_config: ProfileConfig,
    max_before_old_topics: int = 5,
) -> Promise[InferPlot]:
    USE_LANGUAGE = "zh"
    prompt = PROMPTS[USE_LANGUAGE]["infer_plot"]

    latest_plots = [
        ld.attributes["new_topic"]["overview"]
        for ld in latest_statuses.statuses
        if "new_topic" in ld.attributes
    ][:max_before_old_topics]
    print(
        "THINK",
        prompt.get_input(agent_context, user_context, latest_plots, messages),
    )
    r = await llm_complete(
        project_id,
        prompt.get_input(agent_context, user_context, latest_plots, messages),
        system_prompt=prompt.get_prompt(),
        temperature=0.2,  # precise
        model=CONFIG.thinking_llm_model,
        **prompt.get_kwargs(),
        no_cache=True,
        # thinking_enabled=True,
    )
    if not r.ok():
        return r
    content = r.data()
    print(content)
    themes, overview, timeline = extract_plot_output(content)
    return Promise.resolve(dict(themes=themes, overview=overview, timeline=timeline))
