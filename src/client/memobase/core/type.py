from typing import Optional
from pydantic import BaseModel
from ..error import ServerError


class BaseResponse(BaseModel):
    data: Optional[dict]
    errmsg: str
    errno: int

    def raise_for_status(self):
        if self.errno != 0:
            raise ServerError(self.errmsg)
