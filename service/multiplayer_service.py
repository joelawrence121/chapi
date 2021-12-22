import uuid
from enum import Enum

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

    def __init__(self, player_one):
        self.id = uuid.uuid4().__str__()[:4]
        self.state = GameState.WAITING
        self.player_one = player_one
        self.player_two = None
        self.board = Board()
        self.messages = [Message(self.CHEX, "Game created with id: " + self.id)]

    def connect_player_two(self, player_two):
        self.player_two = player_two
        self.state = GameState.IN_PROGRESS
        self.messages.append(Message(self.CHEX, "Player {} has joined the game!".format(player_two)))

    def add_message(self, player_name, message):
        self.messages.append(Message(player_name, message))


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
        new_game = Game(player_one)
        self.games[new_game.id] = new_game
        return self.__get_response_obj(new_game)

    def join_game(self, game_id, player_two):
        if game_id not in self.games.keys():
            return {'message': 'game_id: ' + game_id + ' does not exist.'}

        self.games[game_id].connect_player_two(player_two)
        return self.__get_response_obj(self.games[game_id])

    def post_message(self, game_id, player, message):
        if game_id not in self.games.keys():
            return {'message': 'game_id: ' + game_id + ' does not exist.'}

        self.games[game_id].add_message(player, message)
        return self.__get_response_obj(self.games[game_id])
