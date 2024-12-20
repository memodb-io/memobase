import re
import json
from ..env import LOG, CONFIG
from ..models.response import AIUserProfiles, AIUserProfile
from ..models.blob import Blob
from ..utils import get_blob_str

LIST_INT_PATTERN = re.compile(r"\[\d+(?:,\s*\d+)*\]")
INT_INT_PATTERN = re.compile(r"\[(\d+)\]")


def tag_blobs_in_order_xml(
    blobs: list[Blob],
    tag_name: str = "doc",
):
    dates = [
        b.created_at.strftime("%Y/%m/%d %I:%M%p") if b.created_at else None
        for b in blobs
    ]
    return "\n".join(
        f'<{tag_name} date="{d}">\n{get_blob_str(b)}\n</{tag_name}>'
        for b, d in zip(blobs, dates)
    )


def attribute_unify(attr: str):
    return attr.lower().strip().replace(" ", "_")


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
    CONFIG.llm_tab_separator
    return f"- {action['action']}{CONFIG.llm_tab_separator}{action['memo']}"


def parse_string_into_merge_action(results: str) -> dict | None:
    lines = results.split("\n")[0]
    lines = [l for l in lines.split("\n") if l.strip()]
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


def pack_profiles_into_string(profiles: AIUserProfiles) -> str:
    lines = [
        f"- {attribute_unify(p.topic)}{CONFIG.llm_tab_separator}{attribute_unify(p.sub_topic)}{CONFIG.llm_tab_separator}{p.memo.strip()}"
        for p in profiles.facts
    ]
    if not len(lines):
        return "NONE"
    return "\n".join(lines)


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
    return AIUserProfile(
        topic=attribute_unify(topic),
        sub_topic=attribute_unify(sub_topic),
        memo=memo.strip(),
    )


if __name__ == "__main__":
    print(parse_line_into_profile("- basic_info::name::Gus"))
    print(parse_string_into_merge_action("- REPLACE::G"))
