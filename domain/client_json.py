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


class MultiplayerCreateRequest(BaseModel):
    player_name: str


class MultiplayerPlayRequest(BaseModel):
    game_id: str
    move: str


class MultiplayerJoinRequest(BaseModel):
    player_name: str
    game_id: str


class MultiplayerMessageRequest(BaseModel):
    game_id: str
    player_name: str
    message: str
