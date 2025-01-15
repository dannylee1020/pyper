from typing import List

from pydantic import BaseModel


class Response(BaseModel):
    instruction: str
    input: str
    output: str


class ResponseModel(BaseModel):
    tasks: List[Response]
