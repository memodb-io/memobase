from typing import Optional
from ....models.utils import Promise
from ....env import ProfileConfig, CONFIG
from ....prompts.utils import (
    parse_string_into_subtopics,
    attribute_unify,
)
from ....prompts.profile_init_utils import read_out_event_tags
from ....llms import llm_complete

from ....prompts import event_tagging as event_tagging_prompt


async def tag_event(
    project_id: str, config: ProfileConfig, event_summary: str
) -> Promise[Optional[list]]:
    event_tags = read_out_event_tags(config)
    available_event_tags = set([et.name for et in event_tags])
    if len(event_tags) == 0:
        return Promise.resolve(None)
    event_tags_str = "\n".join([f"- {et.name}({et.description})" for et in event_tags])
    r = await llm_complete(
        project_id,
        event_summary,
        system_prompt=event_tagging_prompt.get_prompt(event_tags_str),
        temperature=0.2,
        model=CONFIG.best_llm_model,
        **event_tagging_prompt.get_kwargs(),
    )
    if not r.ok():
        return r
    parsed_event_tags = parse_string_into_subtopics(r.data())
    parsed_event_tags = [
        {"tag": attribute_unify(et["sub_topic"]), "value": et["memo"]}
        for et in parsed_event_tags
    ]
    strict_parsed_event_tags = [
        et for et in parsed_event_tags if et["tag"] in available_event_tags
    ]
    return Promise.resolve(strict_parsed_event_tags)
