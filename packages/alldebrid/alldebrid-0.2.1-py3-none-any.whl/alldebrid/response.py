from typing import Generic, Literal, Optional, TypeVar, Union, cast

from pydantic import BaseModel

from .models.error import ErrorMessage

T = TypeVar("T")


class ApiError(Exception):
    pass


class Response(BaseModel, Generic[T]):
    status: Union[Literal["success"], Literal["error"]]
    data: Optional[T] = None
    error: Optional[ErrorMessage] = None

    def unwrap(self) -> T:
        if self.status == "success":
            return cast(T, self.data)
        else:
            raise ApiError(self.error)
