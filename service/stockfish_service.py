import math
from enum import Enum

import chess
import chess.engine

from domain.client_json import PlayRequest, DescriptionRequest
from domain.entities import StockfishResult
from engine.stockfish import Engine
from util.utils import get_other_user, WHITE, BLACK


class StockfishService:
    DEFAULT_DIFFICULTY = 10
    DEFAULT_TIME_LIMIT = 0.1
    MATE_LOWER_BOUND = 1
    MATE_UPPER_BOUND = 5
    BLUNDER_THRESHOLD = -0.3
    GOOD_MOVE_LOWER_BOUND = 0.1
    GOOD_MOVE_UPPER_BOUND = 0.2

    def __init__(self):
        self.engine = Engine(10)
        self.board = chess.Board()

    def analyse_board(self, fen, user, time_limit):
        self.board.set_fen(fen)
        info = self.engine.engine.analyse(self.board, chess.engine.Limit(time=time_limit))
        pov_score = chess.engine.PovScore(info['score'], user == WHITE).pov(user == WHITE)
        return pov_score

    def get_best_move(self, fen, difficulty=DEFAULT_DIFFICULTY, time_limit=DEFAULT_TIME_LIMIT):
        self.engine.reconfigure(normalise(difficulty))
        self.board.set_fen(fen)
        return self.engine.play(self.board, time=time_limit)

    def get_stockfish_play_result(self, request: PlayRequest):
        """
        Reconfigure Stockfish's difficulty, find and return its best move for the current fen,
        assign winner if there is one.
        """
        result = self.get_best_move(request.fen, request.difficulty, request.time_limit)

        move = None
        if result.move is not None:
            self.board.push(result.move)
            move = result.move.uci()

        return StockfishResult(
            request.id,
            self.board.fen(),
            move,
            self.is_over(self.board.fen()),
            self.get_relative_score(self.board.fen(), BLACK if self.board.turn else WHITE)
        )

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
        pov_score = self.analyse_board(request.fen, request.user, self.DEFAULT_TIME_LIMIT)

        if self.board.is_checkmate():
            result = {}
            result['moves'] = 0
            if pov_score.turn:
                result['user'] = Outcome.BLACK
            if not pov_score.turn:
                result['user'] = Outcome.WHITE

        elif pov_score.is_mate() \
                and abs(pov_score.relative.mate()) in range(self.MATE_LOWER_BOUND, self.MATE_UPPER_BOUND):

            relative_mate = pov_score.relative.mate()
            if relative_mate > 0 and not pov_score.turn:
                result = {'user': Outcome.BLACK, 'moves': abs(relative_mate)}
            if relative_mate > 0 and pov_score.turn:
                result = {'user': Outcome.WHITE, 'moves': abs(relative_mate)}
        return result

    def get_advantage_change(self, fen_stack, fen, user):
        """
        Detect, using the fenStack, return the user's relative change in score.
        """

        if len(fen_stack) < 5:
            return None

        current_score = self.analyse_board(fen, user, self.DEFAULT_TIME_LIMIT)
        previous_score = self.analyse_board(fen_stack[len(fen_stack) - 2], user, self.DEFAULT_TIME_LIMIT)
        cp_current = get_cp_score(current_score)
        cp_previous = get_cp_score(previous_score)

        if cp_current is None or cp_previous is None:
            return None

        return cp_current - cp_previous

    def is_following_blunder(self, request: DescriptionRequest):
        """
        Return whether the move follows a blunder from the other player.
        """
        fen_stack = request.fenStack[:len(request.fenStack) - 1]
        fen = request.fenStack[len(request.fenStack) - 1]
        advantage_change = self.get_advantage_change(fen_stack, fen, get_other_user(request.user))
        return advantage_change is not None and advantage_change < self.BLUNDER_THRESHOLD

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

    def get_is_check(self, request: DescriptionRequest):
        """
        Return True or False depending on whether the player has put the other into check.
        """
        self.board.set_fen(request.fen)
        return self.board.is_check()

    def get_relative_score(self, fen, user):
        """
        Return a quick cp value giving an indication of the winning probability from White's perspective.
        """
        cp_score = get_cp_score(self.analyse_board(fen, WHITE, time_limit=0.1))
        if cp_score is not None and user == BLACK:
            cp_score *= -1
        return cp_score


def get_cp_score(pov_score):
    cp = pov_score.relative.score()
    raw_score = None
    if not pov_score.is_mate():
        raw_score = (2 / (1 + math.exp(-0.004 * cp)) - 1) * -1
    return raw_score


def normalise(difficulty: int):
    if difficulty not in range(1, 10):
        return 10
    return difficulty * 2


class Outcome(Enum):
    WHITE = 'white'
    BLACK = 'black'
    STALE = 'stale'
