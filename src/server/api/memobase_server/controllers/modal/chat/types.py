from typing import TypedDict
from ....prompts import (
    user_profile_topics,
    extract_profile,
    merge_profile,
    merge_profile_yolo,
    organize_profile,
    summary_entry_chats,
    zh_user_profile_topics,
    zh_extract_profile,
    zh_merge_profile,
    zh_summary_entry_chats,
    zh_merge_profile_yolo,
)
from ....models.response import ProfileData

FactResponse = TypedDict("Facts", {"topic": str, "sub_topic": str, "memo": str})
UpdateResponse = TypedDict("Facts", {"action": str, "memo": str})

Attributes = TypedDict("Attributes", {"topic": str, "sub_topic": str})
AddProfile = TypedDict("AddProfile", {"content": str, "attributes": Attributes})
UpdateProfile = TypedDict(
    "UpdateProfile",
    {"profile_id": str, "content": str, "attributes": Attributes},
)

MergeAddResult = TypedDict(
    "MergeAddResult",
    {
        "add": list[AddProfile],
        "update": list[UpdateProfile],
        "delete": list[str],
        "before_profiles": list[ProfileData],
        "update_delta": list[AddProfile],
    },
)

PROMPTS = {
    "en": {
        "entry_summary": summary_entry_chats,
        "profile": user_profile_topics,
        "extract": extract_profile,
        "merge": merge_profile,
        "merge_yolo": merge_profile_yolo,
        "organize": organize_profile,
    },
    "zh": {
        "entry_summary": zh_summary_entry_chats,
        "profile": zh_user_profile_topics,
        "extract": zh_extract_profile,
        "merge": zh_merge_profile,
        "merge_yolo": zh_merge_profile_yolo,
        "organize": organize_profile,
    },
}
