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
    wait: bool


class AggregationRequest(BaseModel):
    index: int
    original: str


class OpeningRequest(BaseModel):
    move_stack: str
