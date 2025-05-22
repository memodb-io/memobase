import re
import json

JSON_BODY_REGEX = re.compile(r"({[\s\S]*})")


def try_json_loads(content: str) -> dict | None:
    try:
        return json.loads(JSON_BODY_REGEX.search(content).group(1))
    except Exception:
        return None
