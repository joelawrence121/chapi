import uuid
from enum import Enum

import chess
from chess import Board, WHITE

from service.stockfish_service import StockfishService


class GameState(Enum):
    WAITING = "WAITING"
    IN_PROGRESS = "IN PROGRESS"
    PLAYER_LEFT = "PLAYER LEFT"
    RETIRED = "RETIRED"
    FINISHED = "FINISHED"


class DrawResponse(Enum):
    UNKNOWN = "UNKNOWN"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class Message:
    def __init__(self, player, message):
        self.player = player
        self.message = message


class Game:
    CHEX = "Chexplanations"
    PLAYER_JOINED_MSG = "Player \"{}\" has joined the game!"

    def __init__(self, player_one):
        self.stockfish_service = StockfishService()
        self.id = uuid.uuid4().__str__()[:4]
        self.state = GameState.WAITING
        self.player_one = player_one
        self.player_two = None
        self.board = Board()
        self.fen_stack = []
        self.move_stack = []
        self.score_stack = []
        self.draw_offered = False
        self.draw_response = DrawResponse.UNKNOWN
        self.retired = False
        self.player_retired = None
        self.messages = [Message(self.CHEX, "Game created with id: " + self.id),
                         Message(self.CHEX, self.PLAYER_JOINED_MSG.format(player_one))]
        self.white_descriptions = []
        self.black_descriptions = []

    def connect_player_two(self, player_two):
        self.player_two = player_two
        self.state = GameState.IN_PROGRESS
        self.messages.append(Message(self.CHEX, self.PLAYER_JOINED_MSG.format(player_two)))

    def add_message(self, player_name, message):
        self.messages.append(Message(player_name, message))

    def play_move(self, uci: chess.Move):
        self.fen_stack.append(self.board.fen())
        self.move_stack.append(uci.uci())
        self.score_stack.append(self.stockfish_service.get_relative_score(self.board.fen(), WHITE))
        self.board.push(uci)

    def offer_player_draw(self):
        self.draw_offered = True

