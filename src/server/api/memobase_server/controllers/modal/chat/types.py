from typing import TypedDict
from ....prompts import (
    user_profile_topics,
    zh_user_profile_topics,
    extract_profile,
    merge_profile,
    zh_extract_profile,
    zh_merge_profile,
    organize_profile,
)
from ....models.response import ProfileData

FactResponse = TypedDict("Facts", {"topic": str, "sub_topic": str, "memo": str})
UpdateResponse = TypedDict("Facts", {"action": str, "memo": str})

Attributes = TypedDict("Attributes", {"topic": str, "sub_topic": str})
AddProfile = TypedDict("AddProfile", {"content": str, "attributes": Attributes})
UpdateProfile = TypedDict(
    "UpdateProfile",
    {"profile_id": str, "content": str, "attributes": Attributes, "action": str},
)

MergeAddResult = TypedDict(
    "MergeAddResult",
    {
        "add": list[AddProfile],
        "update": list[UpdateProfile],
        "before_profiles": list[ProfileData],
        "delete": list[str],
    },
)

PROMPTS = {
    "en": {
        "profile": user_profile_topics,
        "extract": extract_profile,
        "merge": merge_profile,
        "organize": organize_profile,
    },
    "zh": {
        "profile": zh_user_profile_topics,
        "extract": zh_extract_profile,
        "merge": zh_merge_profile,
        "organize": organize_profile,
    },
}
