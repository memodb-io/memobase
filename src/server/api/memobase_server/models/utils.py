from dataclasses import dataclass
from typing import TypeVar, Optional, Type, Generic
from pydantic import ValidationError
from fastapi import Response
from .response import CODE, BaseResponse
from ..env import LOG


class PromiseUnpackError(Exception):
    pass


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
        if not self.ok():
            raise PromiseUnpackError(self.msg())
        return self.__data

    def code(self) -> CODE:
        return self.__errcode

    def msg(self) -> str:
        if not self.ok():
            return f"CODE {self.__errcode}; ERROR {self.__errmsg}"
        return ""

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
