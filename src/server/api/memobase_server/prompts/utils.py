import re
import json
import difflib
from typing import TypedDict
from ..env import LOG, CONFIG
from ..types import attribute_unify
from ..models.response import AIUserProfiles, AIUserProfile
from ..models.blob import ChatBlob
from ..utils import get_blob_str

UpdateResponse = TypedDict("UpdateResponse", {"action": str, "memo": str})


ORDER_LIST_PATTERN = r"^(\d+)\.(.*)"
MERGE_ACTION_SPACE = {
    "APPEND",
    "UPDATE",
    "ABORT",
}
EXCLUDE_PROFILE_VALUES = [
    # Chinese variations
    "无",
    "未提及",
    "不清楚",
    "用户未提及",
    "对话未提及",
    "未知",
    "不详",
    "没有提到",
    "没有说明",
    "无法确定",
    "无相关内容",
    "未明确提及",
    "无明确信息",
    "无符合信息",
    # English variations
    "none",
    "unknown",
    "not mentioned",
    "not mentioned by user",
    "not mentioned in the conversation",
    "unclear",
    "unspecified",
    "not specified",
    "not determined",
    "no information",
    "n/a",
    "no related content",
    "no related information",
    "no matched information",
]


def tag_chat_blobs_in_order_xml(
    blobs: list[ChatBlob],
):
    return "\n".join(get_blob_str(b) for b in blobs)


def extract_first_complete_json(s: str):
    """Extract the first complete JSON object from the string using a stack to track braces."""
    stack = []
    first_json_start = None

    for i, char in enumerate(s):
        if char == "{":
            stack.append(i)
            if first_json_start is None:
                first_json_start = i
        elif char == "}":
            if stack:
                start = stack.pop()
                if not stack:
                    first_json_str = s[first_json_start : i + 1]
                    try:
                        # Attempt to parse the JSON string
                        return json.loads(first_json_str.replace("\n", ""))
                    except json.JSONDecodeError as e:
                        LOG.error(
                            f"JSON decoding failed: {e}. Attempted string: {first_json_str[:50]}..."
                        )
                        return None
                    finally:
                        first_json_start = None
    LOG.warning("No complete JSON object found in the input string.")
    return None


def parse_value(value: str):
    """Convert a string value to its appropriate type (int, float, bool, None, or keep as string). Work as a more broad 'eval()'"""
    value = value.strip()

    if value == "null":
        return None
    elif value == "true":
        return True
    elif value == "false":
        return False
    else:
        # Try to convert to int or float
        try:
            if "." in value:  # If there's a dot, it might be a float
                return float(value)
            else:
                return int(value)
        except ValueError:
            # If conversion fails, return the value as-is (likely a string)
            return value.strip('"')  # Remove surrounding quotes if they exist


def extract_values_from_json(json_string, allow_no_quotes=False):
    """Extract key values from a non-standard or malformed JSON string, handling nested objects."""
    extracted_values = {}

    # Enhanced pattern to match both quoted and unquoted values, as well as nested objects
    regex_pattern = r'(?P<key>"?\w+"?)\s*:\s*(?P<value>{[^}]*}|".*?"|[^,}]+)'

    for match in re.finditer(regex_pattern, json_string, re.DOTALL):
        key = match.group("key").strip('"')  # Strip quotes from key
        value = match.group("value").strip()

        # If the value is another nested JSON (starts with '{' and ends with '}'), recursively parse it
        if value.startswith("{") and value.endswith("}"):
            extracted_values[key] = extract_values_from_json(value)
        else:
            # Parse the value into the appropriate type (int, float, bool, etc.)
            extracted_values[key] = parse_value(value)

    if not extracted_values:
        LOG.warning("No values could be extracted from the string.")

    return extracted_values


def convert_response_to_json(response: str) -> dict:
    """Convert response string to JSON, with error handling and fallback to non-standard JSON extraction."""
    prediction_json = extract_first_complete_json(response)

    if prediction_json is None:
        LOG.info("Attempting to extract values from a non-standard JSON string...")
        prediction_json = extract_values_from_json(response, allow_no_quotes=True)

    if prediction_json is None:
        LOG.error("JSON extract failed.")

    return prediction_json


def pack_merge_action_into_string(action: dict) -> str:
    return f"- {action['action']}{CONFIG.llm_tab_separator}{action['memo']}"


def parse_string_into_merge_action(results: str) -> dict | None:
    lines = [l for l in results.split("\n") if l.strip()]
    lines = [l for l in lines if l.startswith("- ")]
    if not len(lines):
        return None
    line = lines[0][2:]
    parts = line.split(CONFIG.llm_tab_separator)
    if not len(parts) == 2:
        return None
    return {
        "action": parts[0].upper().strip(),
        "memo": parts[1].strip(),
    }


def parse_string_into_merge_yolo_action(results: str) -> dict[int, UpdateResponse]:
    action_section = results
    memo_results = {}
    lines = [l.strip() for l in action_section.split("\n") if l.strip()]
    for l in lines:
        m = re.match(ORDER_LIST_PATTERN, l)
        if not m:
            continue
        order = int(m.group(1))
        clean_line = m.group(2).strip()
        parse_line = clean_line.split(CONFIG.llm_tab_separator)
        if len(parse_line) < 2:
            continue
        action = parse_line[0].upper().strip()
        memo = CONFIG.llm_tab_separator.join(parse_line[1:]).strip()
        if action not in MERGE_ACTION_SPACE:
            continue
        memo_results[order] = UpdateResponse(action=action, memo=memo)
    return memo_results


def pack_profiles_into_string(profiles: AIUserProfiles) -> str:
    lines = [
        f"- {attribute_unify(p.topic)}{CONFIG.llm_tab_separator}{attribute_unify(p.sub_topic)}{CONFIG.llm_tab_separator}{p.memo.strip()}"
        for p in profiles.facts
    ]
    if not len(lines):
        return "NONE"
    return "\n".join(lines)


def meaningless_profile_memo(memo: str) -> bool:
    maybe_meaningless = difflib.get_close_matches(
        memo.strip().lower(), EXCLUDE_PROFILE_VALUES
    )
    if len(maybe_meaningless) > 0:
        LOG.info(f"Meaningless profile memo: {memo}")
        return True
    return False


def parse_string_into_profiles(response: str) -> AIUserProfiles:
    lines = response.split("\n")
    lines = [l.strip() for l in lines if l.strip()]
    facts = [parse_line_into_profile(l) for l in lines]
    facts = [f for f in facts if f is not None]
    return AIUserProfiles(facts=facts)


def parse_line_into_profile(line: str) -> AIUserProfile | None:
    if not line.startswith("- "):
        return None
    line = line[2:]
    parts = line.split(CONFIG.llm_tab_separator)
    if not len(parts) == 3:
        return None
    topic, sub_topic, memo = parts
    if meaningless_profile_memo(memo):
        return None
    return AIUserProfile(
        topic=attribute_unify(topic),
        sub_topic=attribute_unify(sub_topic),
        memo=memo.strip(),
    )


def parse_string_into_subtopics(response: str) -> list:
    lines = response.split("\n")
    lines = [l.strip() for l in lines if l.strip()]
    facts = [parse_line_into_subtopic(l) for l in lines]
    facts = [f for f in facts if f is not None]
    return facts


def parse_line_into_subtopic(line: str) -> dict:
    if not line.startswith("- "):
        return None
    line = line[2:]
    parts = line.split(CONFIG.llm_tab_separator)
    if not len(parts) == 2:
        return None
    if meaningless_profile_memo(parts[1].strip()):
        return None
    return {"sub_topic": attribute_unify(parts[0].strip()), "memo": parts[1].strip()}


if __name__ == "__main__":
    print(
        parse_string_into_merge_yolo_action(
            """TTT
---
1. ABORT::ABORT
2. ABORT::ABORT
3. ABORT::ABORT
4. ABORT::ABORT
5. APPEND::APPEND
6. APPEND::APPEND"""
        )
    )
