import requests
from typing import Optional, Dict, Any
from requests.models import Response
from .core.type import BaseResponse

PREFIX = "/api/v1"


def api_request(
    base_url: str,
    endpoint: str,
    method: str,
    headers: Optional[Dict[str, str]] = None,
    json: Optional[Dict[str, Any]] = None,
) -> BaseResponse:
    url = base_url.strip("/") + PREFIX + endpoint
    response: Response

    if method == "get":
        response = requests.get(url, headers=headers, json=json)
    elif method == "post":
        response = requests.post(url, headers=headers, json=json)
    elif method == "put":
        response = requests.put(url, headers=headers, json=json)
    elif method == "delete":
        response = requests.delete(url, headers=headers, json=json)
    else:
        raise ValueError(f"Invalid method {method}")

    response.raise_for_status()  # This will raise an HTTPError if the status is 4xx, 5xx

    return BaseResponse.model_validate(response.json())
