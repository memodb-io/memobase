import asyncio
from ....env import CONFIG, LOG
from ....models.utils import Promise
from ....models.response import ProfileData
from ....env import ProfileConfig, ContanstTable
from ....llms import llm_complete
from ....prompts.utils import (
    parse_string_into_merge_action,
)
from ....prompts.profile_init_utils import UserProfileTopic
from .types import UpdateResponse, PROMPTS, AddProfile, UpdateProfile, MergeAddResult


async def merge_or_add_new_memos(
    project_id: str,
    fact_contents: list[str],
    fact_attributes: list[dict],
    profiles: list[ProfileData],
    config: ProfileConfig,
    total_profiles: list[UserProfileTopic],
) -> Promise[MergeAddResult]:
    assert len(fact_contents) == len(
        fact_attributes
    ), "Length of fact_contents and fact_attributes must be equal"
    USE_LANGUAGE = config.language or CONFIG.language
    TOPIC_SUBTOPIC_DESCRIPTIONS = {
        (p.topic, sp.name): {
            "description": sp.description,
            "update_description": sp.update_description,
        }
        for p in total_profiles
        for sp in p.sub_topics
    }

    profile_option_results = {
        "add": [],
        "update": [],
        "before_profiles": profiles,
        "delete": [],
    }
    if not len(profiles):
        profile_option_results["add"].extend(
            [
                {
                    "content": f_c,
                    "attributes": f_a,
                }
                for f_c, f_a in zip(fact_contents, fact_attributes)
            ]
        )
        return Promise.resolve(profile_option_results)

    # new_facts_to_add = []
    facts_to_update = []
    for f_c, f_a in zip(fact_contents, fact_attributes):
        new_p = {"content": f_c, "attributes": f_a}
        same_topic_p = [
            p
            for p in profiles
            if (
                p.attributes[ContanstTable.topic] == f_a[ContanstTable.topic]
                and p.attributes[ContanstTable.sub_topic]
                == f_a[ContanstTable.sub_topic]
            )
        ]
        # 1 if not same topics exist, directly add this
        if not len(same_topic_p):
            profile_option_results["add"].append(new_p)
            continue
        same_topic_p = same_topic_p[0]
        # 2 if exist, continue to merge/replace
        facts_to_update.append(
            {
                "old_profile": same_topic_p,
                "new_profile": new_p,
            }
        )
    merge_tasks = []
    for dp in facts_to_update:
        old_p: ProfileData = dp["old_profile"]
        slot_description = TOPIC_SUBTOPIC_DESCRIPTIONS.get(
            (
                old_p.attributes[ContanstTable.topic],
                old_p.attributes[ContanstTable.sub_topic],
            ),
            {"description": None, "update_description": None},
        )
        task = llm_complete(
            project_id,
            PROMPTS[USE_LANGUAGE]["merge"].get_input(
                old_p.attributes[ContanstTable.topic],
                old_p.attributes[ContanstTable.sub_topic],
                old_p.content,
                dp["new_profile"]["content"],
                update_instruction=slot_description["update_description"],
                topic_description=slot_description["description"],
            ),
            system_prompt=PROMPTS[USE_LANGUAGE]["merge"].get_prompt(),
            temperature=0.2,  # precise
            **PROMPTS[USE_LANGUAGE]["merge"].get_kwargs(),
        )
        merge_tasks.append(task)

    merge_results: list[Promise] = await asyncio.gather(*merge_tasks)
    for p, old_new_profile in zip(merge_results, facts_to_update):
        if not p.ok():
            LOG.warning(f"Failed to merge profiles: {p.msg()}")
            continue
        old_p: ProfileData = old_new_profile["old_profile"]
        update_response: UpdateResponse = parse_string_into_merge_action(p.data())
        if update_response is None:
            LOG.warning(f"Failed to parse merge action: {p.data()}")
            continue
        if update_response["action"] == "UPDATE":
            if ContanstTable.update_hits not in old_p.attributes:
                old_p.attributes[ContanstTable.update_hits] = 1
            else:
                old_p.attributes[ContanstTable.update_hits] += 1
            profile_option_results["update"].append(
                {
                    "profile_id": old_p.id,
                    "content": update_response["memo"],
                    "attributes": old_p.attributes,
                    "action": "UPDATE",
                }
            )
        else:
            LOG.warning(f"Invalid action: {update_response['action']}")
            continue
        old_new_profile["new_profile"]["attributes"][ContanstTable.update_hits] = (
            old_p.attributes[ContanstTable.update_hits]
        )
    return Promise.resolve(profile_option_results)
