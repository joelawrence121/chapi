import chess
import chess.engine

from client.client_json import PlayRequest
from domain.objects import StockfishResult
from engine.stockfish import Engine


def normalise(difficulty: int):
    if difficulty not in range(1, 10):
        raise RuntimeError("Expecte difficulty value in range 1-10 but was {}.".format(difficulty))
    return difficulty * 2


class StockfishService(object):
    TIME_LIMIT = 0.5
    WHITE = 'white'
    BLACK = 'black'

    def __init__(self):
        self.engine = Engine(10)
        self.board = chess.Board()

    def get_stockfish_result(self, request: PlayRequest):
        # reconfigure stockfish engine to normalised difficulty
        self.engine.reconfigure(normalise(request.difficulty))

        # load fen into chess board
        self.board.set_fen(request.fen)
        result = self.engine.play(self.board, time=self.TIME_LIMIT)

        # determine if there was a move made
        move = None
        if result.move is not None:
            self.board.push(result.move)
            move = result.move.uci()

        # assign winner if there is one
        winner = None
        if self.has_won(self.board.fen()) == self.WHITE:
            winner = self.WHITE
        elif self.has_won(self.board.fen()) == self.BLACK:
            winner = self.BLACK

        stockfish_result = StockfishResult(self.board.fen(), move, winner)

        return stockfish_result

    def has_won(self, fen: str):
        self.board.set_fen(fen)

        if self.board.is_game_over():
            if self.board.outcome().winner:
                return self.WHITE
            elif not self.board.outcome().winner:
                return self.BLACK
        return None
