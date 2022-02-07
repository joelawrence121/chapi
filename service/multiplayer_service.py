import chess

from domain.client_json import DescriptionRequest
from domain.objects import Game, DrawResponse, GameState
from service.description_service import DescriptionService
from service.stockfish_service import StockfishService


class MultiplayerService:

    def __init__(self):
        self.games = {}
        self.stockfish_service = StockfishService()
        self.description_service = DescriptionService()

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
            'player_retired': game.player_retired,
            'messages': [{'player': m.player, 'message': m.message} for m in game.messages],
            'white_descriptions': game.white_descriptions,
            'black_descriptions': game.black_descriptions
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

    def get_perspective(self, turn: bool, white: bool):
        if (turn and white) or (not turn and not white):
            return "white"
        else:
            return "black"

    def play(self, game_id, move, descriptions_on: bool):
        if game_id not in self.games.keys():
            return {'message': 'game_id: ' + game_id + ' does not exist.'}

        uci, game = chess.Move.from_uci(move), self.games[game_id]
        game.play_move(uci)

        if descriptions_on:
            game.white_descriptions.append(self.description_service.get_description(
                DescriptionRequest(
                    user=self.get_perspective(game.board.turn, True), uci=move, fen=game.board.fen(), moveStack=game.move_stack,
                    fenStack=game.fen_stack)
            ))
            game.black_descriptions.append(self.description_service.get_description(
                DescriptionRequest(
                    user=self.get_perspective(game.board.turn, False), uci=move, fen=game.board.fen(), moveStack=game.move_stack,
                    fenStack=game.fen_stack)
            ))

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
        self.games[game_id].player_retired = player_name
        self.games[game_id].state = GameState.RETIRED
        return self.__get_response_obj(self.games[game_id])
