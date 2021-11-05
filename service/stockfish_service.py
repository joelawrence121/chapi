from enum import Enum

import chess
import chess.engine

from client.client_json import PlayRequest, DescriptionRequest
from domain.objects import StockfishResult
from engine.stockfish import Engine


class StockfishService(object):
    TIME_LIMIT = 0.5
    MATE_LOWER_BOUND = 1
    MATE_UPPER_BOUND = 5

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
        if self.is_over(self.board.fen()) == Outcome.WHITE:
            winner = Outcome.WHITE
        elif self.is_over(self.board.fen()) == Outcome.BLACK:
            winner = Outcome.BLACK

        return StockfishResult(self.board.fen(), move, winner)

    def is_over(self, fen: str):
        self.board.set_fen(fen)
        if self.board.is_game_over():
            if self.board.is_stalemate():
                return Outcome.STALE
            elif self.board.outcome().winner:
                return Outcome.WHITE
            elif not self.board.outcome().winner:
                return Outcome.BLACK
        return None

    def get_checkmate_result(self, request: DescriptionRequest) -> dict:
        self.board.set_fen(request.fen)
        info = self.engine.engine.analyse(self.board, chess.engine.Limit(time=self.TIME_LIMIT))
        pov_score = chess.engine.PovScore(info['score'], True).pov(True)

        result = None
        if pov_score.is_mate() and abs(pov_score.relative.mate()) in range(self.MATE_LOWER_BOUND,
                                                                           self.MATE_UPPER_BOUND):
            result = {}
            relative_mate = pov_score.relative.mate()
            # user is checkmating
            if pov_score.turn:
                result['checkmating'] = Outcome.WHITE
                result['moves'] = abs(relative_mate)
            # pov is always white so this means user is being mated
            if not pov_score.turn:
                result['checkmating'] = Outcome.BLACK
                result['moves'] = abs(relative_mate)
        return result


def normalise(difficulty: int):
    if difficulty not in range(1, 10):
        raise RuntimeError("Expected difficulty value in range 1-10 but was {}.".format(difficulty))
    return difficulty * 2


class Outcome(Enum):
    WHITE = 'white'
    BLACK = 'black'
    STALE = 'stale'
