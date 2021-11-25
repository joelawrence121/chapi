from typing import List

from pydantic import BaseModel


class DescriptionRequest(BaseModel):
    user: str
    moveStack: List[str]
    uci: str
    fen: str
    fenStack: List[str]


class PlayRequest(BaseModel):
    id: str
    fen: str
    difficulty: int
    time_limit: float
