import math
from enum import Enum

import chess
import chess.engine

from domain.client_json import PlayRequest, DescriptionRequest
from domain.entities import StockfishResult
from engine.stockfish import Engine


class StockfishService(object):
    TIME_LIMIT = 0.5
    MATE_LOWER_BOUND = 1
    MATE_UPPER_BOUND = 5
    BLUNDER_THRESHOLD = -0.3

    def __init__(self):
        self.engine = Engine(10)
        self.board = chess.Board()

    def analyse_board(self, fen, user):
        self.board.set_fen(fen)
        info = self.engine.engine.analyse(self.board, chess.engine.Limit(time=self.TIME_LIMIT))
        pov_score = chess.engine.PovScore(info['score'], user == "human").pov(user == "human")
        return pov_score

    def get_stockfish_play_result(self, request: PlayRequest):
        """
        Reconfigure Stockfish's difficulty, find and return its best move for the current fen,
        assign winner if there is one.
        """

        self.engine.reconfigure(normalise(request.difficulty))
        self.board.set_fen(request.fen)
        result = self.engine.play(self.board, time=request.time_limit)

        move = None
        if result.move is not None:
            self.board.push(result.move)
            move = result.move.uci()

        winner = None
        if self.is_over(self.board.fen()) == Outcome.WHITE:
            winner = Outcome.WHITE
        elif self.is_over(self.board.fen()) == Outcome.BLACK:
            winner = Outcome.BLACK

        return StockfishResult(request.id, self.board.fen(), move, winner)

    def is_over(self, fen: str):
        """
        Determine the end state of the board.
        """

        self.board.set_fen(fen)
        if self.board.is_game_over():
            if self.board.is_stalemate():
                return Outcome.STALE
            elif self.board.outcome().winner:
                return Outcome.WHITE
            elif not self.board.outcome().winner:
                return Outcome.BLACK
        return None

    def get_mate_result(self, request: DescriptionRequest) -> dict:
        """
        Analyse the board to determine mate results: who has checkmated, who is trying to checkmate and how many moves
        until they do.
        """

        result = None
        pov_score = self.analyse_board(request.fen, request.user)

        if self.board.is_checkmate():
            result = {}
            result['moves'] = 0
            if pov_score.turn:
                result['user'] = Outcome.BLACK
            if not pov_score.turn:
                result['user'] = Outcome.WHITE

        elif pov_score.is_mate() \
                and abs(pov_score.relative.mate()) in range(self.MATE_LOWER_BOUND, self.MATE_UPPER_BOUND):

            result = {}
            relative_mate = pov_score.relative.mate()
            if pov_score.turn:
                result['user'] = Outcome.WHITE
                result['moves'] = abs(relative_mate)
            if not pov_score.turn:
                result['user'] = Outcome.BLACK
                result['moves'] = abs(relative_mate)
        return result

    def get_blunder_result(self, request: DescriptionRequest):
        """
        Detect, using the fenStack, whether the given move was a blunder (a move resulting in a substantial loss
        in advantage).
        """

        if len(request.fenStack) < 5:
            return None

        current_score = self.analyse_board(request.fen, request.user)
        previous_score = self.analyse_board(request.fenStack[len(request.fenStack) - 2], request.user)
        cp_current = get_cp_score(current_score)
        cp_previous = get_cp_score(previous_score)

        if cp_current is None or cp_previous is None:
            return None

        if cp_current - cp_previous < self.BLUNDER_THRESHOLD:
            return cp_current - cp_previous

    def get_capture_result(self, request: DescriptionRequest):
        """
        Analyse the move and determine whether the move was a capture, and if it was what piece was captured.
        """

        if len(request.fenStack) < 2:
            return None

        result = None
        previous_fen = request.fenStack[-2]
        move = chess.Move.from_uci(request.uci)

        self.board.set_fen(previous_fen)
        if self.board.is_capture(move):
            # dealing with unreliable results from is_capture
            if self.board.piece_type_at(move.to_square) is None:
                self.board.set_fen(request.fenStack[-1])
            if self.board.piece_type_at(move.to_square) is not None:
                result = chess.PIECE_NAMES[self.board.piece_type_at(move.to_square)]
        return result


def get_cp_score(pov_score):
    cp = pov_score.relative.score()
    raw_score = None
    if not pov_score.is_mate():
        raw_score = (2 / (1 + math.exp(-0.004 * cp)) - 1) * -1
    return raw_score


def normalise(difficulty: int):
    if difficulty not in range(1, 10):
        raise RuntimeError("Expected difficulty value in range 1-10 but was {}.".format(difficulty))
    return difficulty * 2


class Outcome(Enum):
    WHITE = 'white'
    BLACK = 'black'
    STALE = 'stale'
