from typing import TypedDict
from ....prompts import (
    extract_profile,
    merge_profile,
    zh_extract_profile,
    zh_merge_profile,
)

FactResponse = TypedDict("Facts", {"topic": str, "sub_topic": str, "memo": str})
UpdateResponse = TypedDict("Facts", {"action": str, "memo": str})

Attributes = TypedDict("Attributes", {"topic": str, "sub_topic": str})
AddProfile = TypedDict("AddProfile", {"content": str, "attributes": Attributes})
UpdateProfile = TypedDict(
    "UpdateProfile",
    {"profile_id": str, "content": str, "attributes": Attributes, "action": str},
)

PROMPTS = {
    "en": {"extract": extract_profile, "merge": merge_profile},
    "zh": {"extract": zh_extract_profile, "merge": zh_merge_profile},
}
