import asyncio
from typing import TypedDict
from ....env import CONFIG, LOG
from ....models.utils import Promise
from ....models.response import ProfileData
from ....llms import llm_complete
from ....prompts.utils import (
    parse_string_into_merge_action,
)
from .types import UpdateResponse, PROMPTS, AddProfile, UpdateProfile

MergeAddResult = TypedDict(
    "MergeAddResult",
    {
        "add": list[AddProfile],
        "update": list[UpdateProfile],
        "before_profiles": list[ProfileData],
    },
)


async def merge_or_add_new_memos(
    fact_contents: list[str],
    fact_attributes: list[dict],
    profiles: list[ProfileData],
) -> Promise[MergeAddResult | None]:
    profile_option_results = {"add": [], "update": [], "before_profiles": profiles}
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
                p.attributes["topic"] == f_a["topic"]
                and p.attributes["sub_topic"] == f_a["sub_topic"]
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
        task = llm_complete(
            PROMPTS[CONFIG.language]["merge"].get_input(
                old_p.attributes["topic"],
                old_p.attributes["sub_topic"],
                old_p.content,
                dp["new_profile"]["content"],
            ),
            system_prompt=PROMPTS[CONFIG.language]["merge"].get_prompt(),
            temperature=0.2,  # precise
        )
        merge_tasks.append(task)

    success_update_profile_count = 0
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
        success_update_profile_count += 1
    LOG.info(
        (
            f"TOTAL {len(fact_contents)} profiles, ADD {len(profile_option_results['add'])} new profiles, "
            f"update {success_update_profile_count}/{len(facts_to_update)} existing profiles"
        )
    )
    return Promise.resolve(profile_option_results)
