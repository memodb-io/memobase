import re
import json
from ..env import LOG


def tag_strings_in_order_xml(
    strings: list[str], tag_name: str = "doc", index_offset: int = 0
):
    return "\n".join(
        f"<{tag_name} data_index={i+index_offset}>\n{s}\n</{tag_name}>"
        for i, s in enumerate(strings)
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


def extract_values_from_json(
    json_string, keys=["reasoning", "answer", "data"], allow_no_quotes=False
):
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
