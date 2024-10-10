from typing import Optional
from pydantic import BaseModel


class BaseResponse(BaseModel):
    data: Optional[dict]
    errmsg: str
    errno: int
