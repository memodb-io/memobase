from dataclasses import dataclass
from typing import TypeVar, Optional, Type, Generic
from pydantic import ValidationError
from .response import CODE, BaseResponse
from ..utils import LOG


D = TypeVar("D")
T = TypeVar("T", bound=BaseResponse)


@dataclass
class Promise(Generic[D]):
    __data: Optional[D]
    __errcode: CODE = CODE.SUCCESS
    __errmsg: str = ""

    @classmethod
    def resolve(cls, data: D) -> "Promise[D]":
        return cls(data)

    @classmethod
    def reject(cls, errcode: CODE, errmsg: str) -> "Promise":
        assert errmsg is not None, "Error Message can't be None!"
        assert errcode in CODE, f"Invalid Error Code: {errcode}"
        return cls(None, errcode, errmsg)

    def ok(self) -> bool:
        return self.__errcode == CODE.SUCCESS

    def data(self) -> Optional[D]:
        return self.__data

    def to_response(self, ResponseModel: Type[T]) -> T:
        try:
            return ResponseModel(
                data=self.__data,
                errno=self.__errcode,
                errmsg=self.__errmsg,
            )
        except ValidationError as e:
            LOG.error(f"Error while parsing response: {e}")
            return ResponseModel(
                data=None,
                errno=CODE.INTERNAL_SERVER_ERROR,
                errmsg=str(e),
            )
