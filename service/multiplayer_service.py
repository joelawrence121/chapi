import uuid
from enum import Enum

import chess
from chess import Board

from service.stockfish_service import StockfishService
from util.utils import WHITE


class GameState(Enum):
    WAITING = "WAITING"
    IN_PROGRESS = "IN PROGRESS"
    PLAYER_LEFT = "PLAYER LEFT"
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
        self.messages = [Message(self.CHEX, "Game created with id: " + self.id),
                         Message(self.CHEX, self.PLAYER_JOINED_MSG.format(player_one))]

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
            'winner': self.stockfish_service.is_over(game.board.fen()),
            'move_stack': game.move_stack,
            'fen_stack': game.fen_stack,
            'score_stack': game.score_stack,
            'draw_offered': game.draw_offered,
            'draw_response': game.draw_response,
            'retired': game.retired,
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

    def poll_game(self, game_id):
        if game_id not in self.games.keys():
            return {'message': 'game_id: ' + game_id + ' does not exist.'}

        return self.__get_response_obj(self.games[game_id])

    def play(self, game_id, move):
        if game_id not in self.games.keys():
            return {'message': 'game_id: ' + game_id + ' does not exist.'}

        uci = chess.Move.from_uci(move)
        self.games[game_id].play_move(uci)
        return self.__get_response_obj(self.games[game_id])

    def offer_draw(self, game_id):
        if game_id not in self.games.keys():
            return {'message': 'game_id: ' + game_id + ' does not exist.'}

        self.games[game_id].offer_player_draw()
        return self.__get_response_obj(self.games[game_id])

    def answer_draw(self, game_id, draw_answer):
        if game_id not in self.games.keys():
            return {'message': 'game_id: ' + game_id + ' does not exist.'}

        # draw rejected
        if not draw_answer:
            self.games[game_id].draw_response = DrawResponse.REJECTED
            self.games[game_id].draw_offered = False
        # draw accepted
        else:
            self.games[game_id].draw_response = DrawResponse.ACCEPTED
            self.games[game_id].state = GameState.FINISHED

        return self.__get_response_obj(self.games[game_id])

    def reset_draw(self, game_id):
        if game_id not in self.games.keys():
            return {'message': 'game_id: ' + game_id + ' does not exist.'}

        self.games[game_id].draw_response = DrawResponse.UNKNOWN
        self.games[game_id].draw_offered = False

        return self.__get_response_obj(self.games[game_id])

    def retire(self, game_id, player_name):
        if game_id not in self.games.keys():
            return {'message': 'game_id: ' + game_id + ' does not exist.'}

        self.games[game_id].retired = True
        return self.__get_response_obj(self.games[game_id])
