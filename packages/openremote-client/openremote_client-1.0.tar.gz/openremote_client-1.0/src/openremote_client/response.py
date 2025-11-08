from typing import TypeVar, Generic

from httpx import Response
from pydantic import BaseModel

T = TypeVar('T')

class ResponseModel(BaseModel, Generic[T]):
    status_code: int
    content: T
    response: Response

    class Config:
        arbitrary_types_allowed=True