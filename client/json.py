from typing import List

from pydantic import BaseModel


class OpeningRequest(BaseModel):
    user: str
    moveStack: List[str]
    move: str
    fen: str

