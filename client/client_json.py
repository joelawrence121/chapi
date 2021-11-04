from typing import List

from pydantic import BaseModel


class DescriptionRequest(BaseModel):
    user: str
    moveStack: List[str]
    move: str
    fen: str


class PlayRequest(BaseModel):
    fen: str
    difficulty: int
