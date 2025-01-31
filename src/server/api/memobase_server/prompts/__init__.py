from . import (
    extract_profile,
    zh_extract_profile,
    merge_profile,
    zh_merge_profile,
    organize_profile,
    summary_profile,
)

PROMPT_ID_TO_PROMPT = {
    "extract_profile": extract_profile,
    "merge_profile": merge_profile,
    "organize_profile": organize_profile,
    "summary_profile": summary_profile,
    "zh_extract_profile": zh_extract_profile,
    "zh_merge_profile": zh_merge_profile,
}
