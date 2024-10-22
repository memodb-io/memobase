import requests
from typing import Optional, Dict, Any
from requests.models import Response
from .core.type import BaseResponse

PREFIX = "/api/v1"


def unpack_response(response: Response) -> BaseResponse:
    response.raise_for_status()  # This will raise an HTTPError if the status is 4xx, 5xx
    return BaseResponse.model_validate(response.json())
