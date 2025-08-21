import asyncio
from ....models.utils import Promise, CODE
from ....env import CONFIG, TRACE_LOG
from ....utils import get_blob_str, get_encoded_tokens, truncate_string
from ....llms import llm_complete
from ....prompts import (
    summary_profile,
)
from .types import UpdateProfile, AddProfile


async def re_summary(
    user_id: str,
    project_id: str,
    add_profile: list[AddProfile],
    update_profile: list[UpdateProfile],
) -> Promise[None]:
    add_tasks = [summary_memo(user_id, project_id, ap) for ap in add_profile]
    await asyncio.gather(*add_tasks)
    update_tasks = [summary_memo(user_id, project_id, up) for up in update_profile]
    ps = await asyncio.gather(*update_tasks)
    if not all([p.ok() for p in ps]):
        return Promise.reject(
            CODE.INTERNAL_SERVER_ERROR, "Failed to re-summary profiles"
        )
    return Promise.resolve(None)


async def summary_memo(
    user_id: str, project_id: str, content_pack: dict
) -> Promise[None]:
    content = content_pack["content"]
    if len(get_encoded_tokens(content)) <= CONFIG.max_pre_profile_token_size:
        return Promise.resolve(None)
    r = await llm_complete(
        project_id,
        content_pack["content"],
        system_prompt=summary_profile.get_prompt(),
        temperature=0.2,  # precise
        model=CONFIG.summary_llm_model,
        **summary_profile.get_kwargs(),
    )
    if not r.ok():
        TRACE_LOG.error(
            project_id,
            user_id,
            f"Failed to summary memo: {r.msg()}",
        )
        return r
    content_pack["content"] = truncate_string(
        r.data(), CONFIG.max_pre_profile_token_size // 2
    )
    return Promise.resolve(None)
