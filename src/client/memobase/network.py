from httpx import Response
from .core.type import BaseResponse

PREFIX = "/api/v1"


def unpack_response(response: Response) -> BaseResponse:
    response.raise_for_status()  # This will raise an HTTPError if the status is 4xx, 5xx
    r = BaseResponse.model_validate(response.json())
    r.raise_for_status()
    return r
