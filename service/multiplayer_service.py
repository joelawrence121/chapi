import uuid
from enum import Enum

import chess
from chess import Board

from service.stockfish_service import StockfishService


class GameState(Enum):
    WAITING = "WAITING"
    IN_PROGRESS = "IN PROGRESS"
    PLAYER_LEFT = "PLAYER LEFT"


class Message:
    def __init__(self, player, message):
        self.player = player
        self.message = message


class Game:
    CHEX = "Chexplanations"
    PLAYER_JOINED_MSG = "Player \"{}\" has joined the game!"

    def __init__(self, player_one):
        self.id = uuid.uuid4().__str__()[:4]
        self.state = GameState.WAITING
        self.player_one = player_one
        self.player_two = None
        self.board = Board()
        self.messages = [Message(self.CHEX, "Game created with id: " + self.id),
                         Message(self.CHEX, self.PLAYER_JOINED_MSG.format(player_one))]

    def connect_player_two(self, player_two):
        self.player_two = player_two
        self.state = GameState.IN_PROGRESS
        self.messages.append(Message(self.CHEX, self.PLAYER_JOINED_MSG.format(player_two)))

    def add_message(self, player_name, message):
        self.messages.append(Message(player_name, message))

    def play_move(self, uci):
        self.board.push(uci)


class MultiplayerService:

    def __init__(self):
        self.games = {}
        self.stockfish_service = StockfishService()

    def __get_response_obj(self, game: Game):
        return {
            'game_id': game.id,
            'state': game.state.value,
            'player_one': game.player_one,
            'player_two': game.player_two,
            'fen': game.board.fen(),
            'turn': game.board.turn,
            'messages': [{'player': m.player, 'message': m.message} for m in game.messages]
        }

    def create_game(self, player_one):
        player_name = player_one
        if len(player_name) < 1:
            player_name = "Player 1"

        new_game = Game(player_name)
        self.games[new_game.id] = new_game
        return self.__get_response_obj(new_game)

    def join_game(self, game_id, player_two):
        if game_id not in self.games.keys():
            return {'message': 'game_id: ' + game_id + ' does not exist.'}
        if self.games[game_id].player_two is not None:
            return {'message': 'game_id: ' + game_id + ' is full.'}

        player_name = player_two
        if len(player_two) < 1:
            player_name = "Player 2"

        self.games[game_id].connect_player_two(player_name)
        return self.__get_response_obj(self.games[game_id])

    def post_message(self, game_id, player, message):
        if game_id not in self.games.keys():
            return {'message': 'game_id: ' + game_id + ' does not exist.'}

        self.games[game_id].add_message(player, message)
        return self.__get_response_obj(self.games[game_id])

    def poll_game(self, game_id, player):
        if game_id not in self.games.keys():
            return {'message': 'game_id: ' + game_id + ' does not exist.'}

        return self.__get_response_obj(self.games[game_id])

    def play(self, game_id, move):
        if game_id not in self.games.keys():
            return {'message': 'game_id: ' + game_id + ' does not exist.'}

        uci = chess.Move.from_uci(move)
        self.games[game_id].play_move(uci)
        return self.__get_response_obj(self.games[game_id])
