from ....env import CONFIG, TRACE_LOG
from ....models.utils import Promise, CODE
from ....models.response import ProfileData
from ....env import ProfileConfig, ContanstTable
from ....llms import llm_complete
from ....prompts.utils import (
    parse_string_into_merge_yolo_action,
)
from ....prompts.profile_init_utils import UserProfileTopic
from ....types import SubTopic
from .types import UpdateResponse, PROMPTS, AddProfile, UpdateProfile, MergeAddResult


async def merge_or_valid_new_memos(
    user_id: str,
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
    DEFINE_MAPS = {
        (p.topic, sp.name): sp for p in total_profiles for sp in p.sub_topics
    }
    RUNTIME_MAPS = {
        (p.attributes[ContanstTable.topic], p.attributes[ContanstTable.sub_topic]): p
        for p in profiles
    }
    USE_LANGUAGE = config.language or CONFIG.language
    PROFILE_VALIDATE_MODE = (
        config.profile_validate_mode
        if config.profile_validate_mode is not None
        else CONFIG.profile_validate_mode
    )

    profile_session_results: MergeAddResult = {
        "add": [],
        "update": [],
        "delete": [],
        "update_delta": [],
        "before_profiles": profiles,
    }
    tasks = []
    new_memos = []
    for f_c, f_a in zip(fact_contents, fact_attributes):
        KEY = (
            f_a[ContanstTable.topic],
            f_a[ContanstTable.sub_topic],
        )
        runtime_profile = RUNTIME_MAPS.get(KEY, None)
        define_sub_topic = DEFINE_MAPS.get(KEY, SubTopic(name=""))
        if (
            not PROFILE_VALIDATE_MODE
            and not define_sub_topic.validate_value
            and runtime_profile is None
        ):
            TRACE_LOG.info(
                project_id,
                user_id,
                f"Skip validation: {KEY}",
            )
            profile_session_results["add"].append(
                {
                    "content": f_c,
                    "attributes": f_a,
                }
            )
            continue
        new_memos.append(
            (
                {
                    "new_info": f_c,
                    "current_memo": runtime_profile.content if runtime_profile else "",
                    "topic": KEY[0],
                    "subtopic": KEY[1],
                    "topic_description": define_sub_topic.description,
                    "update_instruction": define_sub_topic.update_description,
                },
                f_c,
                f_a,
            )
        )
    new_memos_input = [{"memo_id": i + 1, **m[0]} for i, m in enumerate(new_memos)]
    r = await llm_complete(
        project_id,
        PROMPTS[USE_LANGUAGE]["merge_yolo"].get_input(new_memos_input),
        system_prompt=PROMPTS[USE_LANGUAGE]["merge_yolo"].get_prompt(),
        temperature=0.2,  # precise
        **PROMPTS[USE_LANGUAGE]["merge_yolo"].get_kwargs(),
    )
    oneline_response = r.data().replace("\n", "<br/>")
    if not r.ok():
        TRACE_LOG.warning(
            project_id,
            user_id,
            f"Failed to merge profiles: {r.msg()}",
        )
        return r
    memo_actions = parse_string_into_merge_yolo_action(r.data())

    abort_infos = []
    for i, m in enumerate(new_memos):
        update_response = memo_actions.get(i + 1, None)
        if update_response is None:
            TRACE_LOG.warning(
                project_id,
                user_id,
                f"No Corresponding Merge Action: {new_memos_input[i]}, <raw_response> {oneline_response} </raw_response>",
            )
            continue
        f_c, f_a = m[1], m[2]
        KEY = (f_a[ContanstTable.topic], f_a[ContanstTable.sub_topic])
        runtime_profile = RUNTIME_MAPS.get(KEY, None)
        if update_response["action"] == "UPDATE":
            if runtime_profile is None:
                profile_session_results["add"].append(
                    {
                        "content": update_response["memo"],
                        "attributes": f_a,
                    }
                )
            else:
                if ContanstTable.update_hits not in runtime_profile.attributes:
                    runtime_profile.attributes[ContanstTable.update_hits] = 1
                else:
                    runtime_profile.attributes[ContanstTable.update_hits] += 1
                profile_session_results["update"].append(
                    {
                        "profile_id": runtime_profile.id,
                        "content": update_response["memo"],
                        "attributes": runtime_profile.attributes,
                    }
                )
                profile_session_results["update_delta"].append(
                    {
                        "content": f_c,
                        "attributes": f_a,
                    }
                )
        elif update_response["action"] == "APPEND":
            if runtime_profile is None:
                profile_session_results["add"].append(
                    {
                        "content": f_c,
                        "attributes": f_a,
                    }
                )
            else:
                if ContanstTable.update_hits not in runtime_profile.attributes:
                    runtime_profile.attributes[ContanstTable.update_hits] = 1
                else:
                    runtime_profile.attributes[ContanstTable.update_hits] += 1
                profile_session_results["update"].append(
                    {
                        "profile_id": runtime_profile.id,
                        "content": f"{runtime_profile.content};{f_c}",
                        "attributes": runtime_profile.attributes,
                    }
                )
                profile_session_results["update_delta"].append(
                    {
                        "content": f_c,
                        "attributes": f_a,
                    }
                )
        elif update_response["action"] == "ABORT":
            abort_infos.append(new_memos_input[i])
        else:
            TRACE_LOG.warning(
                project_id,
                user_id,
                f"Unkown merge action: {update_response['action']}",
            )
            continue

    if len(abort_infos):
        TRACE_LOG.info(
            project_id,
            user_id,
            f"Invalid merge: {abort_infos}. <raw_response> {oneline_response} </raw_response>",
        )
    return Promise.resolve(profile_session_results)
