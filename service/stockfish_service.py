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

    def __init__(self):
        self.engine = Engine(10)
        self.board = chess.Board()

    def get_move(self, request: PlayRequest):
        # reconfigure stockfish engine to normalised difficulty
        self.engine.reconfigure(normalise(request.difficulty))

        # load fen into chess board
        self.board.set_fen(request.fen)
        result = self.engine.play(self.board, time=self.TIME_LIMIT)
        self.board.push(result.move)

        # create result object
        stockfish_result = StockfishResult(self.board.fen(), result.move.uci())

        return stockfish_result
