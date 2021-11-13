from typing import List

from pydantic import BaseModel


class DescriptionRequest(BaseModel):
    user: str
    moveStack: List[str]
    move: str
    fen: str


class PlayRequest(BaseModel):
    id: str
    fen: str
    difficulty: int
    time_limit: float
