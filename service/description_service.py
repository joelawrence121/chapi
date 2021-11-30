import random

import chess

from service import grammar_service
from domain.client_json import DescriptionRequest
from domain.repository import Repository
from service.stockfish_service import StockfishService, Outcome
from util.utils import get_move, get_random_generation, get_link, format_name, get_piece_name, get_to_square, WHITE, \
    BLACK


class DescriptionService(object):
    CRITICAL_BLUNDER_THRESHOLD = -0.6

    def __init__(self):
        self.repository = Repository()
        self.stockfish_service = StockfishService()

    def get_description(self, request: DescriptionRequest) -> []:
        """
        For a given DescriptionRequest : (user, moveStack, move, fen), generate an array of English descriptions
        providing insight on: the opening scenario, winning conditions, mate conditions...
        """

        response = {'descriptions': [], 'link': None,
                    'score': self.stockfish_service.get_relative_score(request.fen, request.user)}

        opening_data = self.get_opening_description(request)
        response['descriptions'].extend(opening_data[0])
        response['link'] = opening_data[1]
        response['opening'] = opening_data[2]
        response['descriptions'].extend(self.get_positional_description(request))
        response['descriptions'].extend(self.get_move_suggestions(request))
        response['descriptions'].extend(self.get_mate_description(request))
        response['descriptions'].extend(self.get_end_description(request))
        response['descriptions'].extend(self.get_blunder_description(request))
        response['descriptions'].extend(self.get_gain_description(request))
        return response

    def get_opening_description(self, request: DescriptionRequest):
        """
        Queries the database to determine if the board is in a particular opening scenario. Returns a relevant
        CFG generated description with Wikipedia link if it exists.
        """

        grammar = grammar_factory.get_default_opening(request.user, request.uci)
        opening = self.repository.query_opening_by_move_stack(request.moveStack)
        capture = self.stockfish_service.get_capture_result(request)
        is_check = self.stockfish_service.get_is_check(request)
        move = get_move(request.uci, opening)

        if request.user == WHITE:
            # special case for opening move
            if len(request.moveStack) == 1:
                grammar = grammar_factory.get_user_first_opening(move)
            else:
                previous_move = get_move(request.moveStack[len(request.moveStack) - 2],
                                         self.repository.query_opening_by_move_stack(request.moveStack[:-1]))
                grammar = grammar_factory.get_user_move(move, previous_move, capture, is_check)

        elif request.user == BLACK:
            is_following_blunder = self.stockfish_service.is_following_blunder(request)
            previous_move = get_move(request.moveStack[len(request.moveStack) - 2],
                                     self.repository.query_opening_by_move_stack(request.moveStack[:-1]))
            grammar = grammar_factory.get_stockfish_move(move, previous_move, capture, is_check, is_following_blunder)

        # return the description, link and move name for rendering on front end
        return get_random_generation(grammar), get_link(opening), move

    def get_end_description(self, request: DescriptionRequest):
        """
        Uses Stockfish to analyse the board for end conditions: won, lost, stalemate.
        Generates a POV appropriate description if the conditions are met.
        """

        end_result = self.stockfish_service.is_over(request.fen)
        if end_result is None:
            return []

        grammar = ""
        move_count = len(request.moveStack) // 2
        if self.stockfish_service.is_over(request.fen) == Outcome.WHITE:
            grammar = grammar_factory.get_user_win_condition(move_count)
        elif self.stockfish_service.is_over(request.fen) == Outcome.BLACK:
            grammar = grammar_factory.get_stockfish_win_condition(move_count)
        elif self.stockfish_service.is_over(request.fen) == Outcome.STALE:
            grammar = grammar_factory.get_stalemate_ending(move_count)
        return get_random_generation(grammar)

    def get_mate_description(self, request: DescriptionRequest):
        """
        Use Stockfish to analyse whether a Checkmate is available or if the user is being checkmated.
        Generates a natural language description if the conditions are met.
        """

        checkmate_result = self.stockfish_service.get_mate_result(request)
        if checkmate_result is None:
            return []

        grammar = ""
        if checkmate_result['user'] == Outcome.WHITE:
            if checkmate_result['moves'] == 0:
                grammar = grammar_factory.get_user_checkmated()
            else:
                grammar = grammar_factory.get_user_checkmating(checkmate_result['moves'])

        if checkmate_result['user'] == Outcome.BLACK:
            if checkmate_result['moves'] == 0:
                grammar = grammar_factory.get_stockfish_checkmated()
            else:
                grammar = grammar_factory.get_stockfish_checkmating(checkmate_result['moves'])

        return get_random_generation(grammar)

    def get_blunder_description(self, request: DescriptionRequest):
        """
        Use Stockfish to detect whether a move made was a fair or critical blunder and return a description if it is.
        """
        advantage_change = self.stockfish_service.get_advantage_change(request.fenStack, request.fen, request.user)
        if request.user == BLACK or advantage_change is None or advantage_change > self.stockfish_service.BLUNDER_THRESHOLD:
            return []

        grammar = grammar_factory.get_user_blunder(request.uci, abs(round(advantage_change * 100)),
                                                   advantage_change < self.CRITICAL_BLUNDER_THRESHOLD)
        return get_random_generation(grammar)

    def get_move_suggestions(self, request):
        """
        On Stockfish's move, return suggestion moves to the player based on common openings in the database.
        """

        if request.user == WHITE:
            return []

        move_stack_string = ' '.join(request.moveStack)
        openings = self.repository.query_opening_by_move_stack_subset(move_stack_string)
        original_opening = self.repository.query_opening_by_move_stack(request.moveStack)
        if len(openings) > 3:
            openings = random.sample(openings, 3)
        moves = [opening['move_stack'].replace(move_stack_string, '').replace(' ', '') for opening in openings]
        names = [format_name(original_opening, opening['name']) for opening in openings]

        if len(moves) == 0:
            return []

        grammar = grammar_factory.get_move_suggestion(moves, names)
        return get_random_generation(grammar)

    def get_positional_description(self, request):
        """
        Describes the move's relative positional information. Moving forward/backwards, moving from an original
        position, advancing/retreating.
        """

        grammar = None
        move = chess.Move.from_uci(request.uci)
        piece = get_piece_name(request.uci, request.fen)
        rel_from_square = chess.SQUARE_NAMES[move.from_square if request.user == WHITE else move.to_square]
        rel_to_square = chess.SQUARE_NAMES[move.to_square if request.user == WHITE else move.from_square]

        # piece moves forward / backward
        if rel_from_square[1] != rel_to_square[1] and int(rel_from_square[1]) < int(rel_to_square[1]) - 1:
            grammar = grammar_factory.get_positional_description(request.user, piece, get_to_square(move), None, None,
                                                                 1)
        if rel_from_square[1] != rel_to_square[1] and int(rel_from_square[1]) + 1 > int(rel_to_square[1]):
            grammar = grammar_factory.get_positional_description(request.user, piece, get_to_square(move), None, None,
                                                                 -1)

        # piece moves within same column
        if rel_from_square[0] == rel_to_square[0]:
            if int(rel_from_square[1]) < int(rel_to_square[1]):
                grammar = grammar_factory.get_positional_description(request.user, piece, get_to_square(move), None, 1)
            else:
                grammar = grammar_factory.get_positional_description(request.user, piece, get_to_square(move), None, -1)

        # moving from starting row
        if request.user == BLACK and rel_to_square[1] == '8':
            grammar = grammar_factory.get_positional_description(request.user, piece, get_to_square(move), True)
        if request.user == WHITE and rel_from_square[1] == '1':
            grammar = grammar_factory.get_positional_description(request.user, piece, get_to_square(move), True)

        if grammar is None:
            return []

        return get_random_generation(grammar)

    def get_gain_description(self, request: DescriptionRequest):
        """
        Use Stockfish to detect whether the move made was a good, great or fantastic move. Return an explanation back
        to the user depending on the outcome.
        """

        advantage_change = self.stockfish_service.get_advantage_change(request.fenStack, request.fen, request.user)
        if advantage_change is None or advantage_change < self.stockfish_service.GOOD_MOVE_LOWER_BOUND:
            return []

        rounded_advantage_change = abs(round(advantage_change * 100))
        grammar = grammar_factory.get_good_move(request.uci, rounded_advantage_change)
        if advantage_change > self.stockfish_service.GOOD_MOVE_UPPER_BOUND:
            play_result = self.stockfish_service.get_best_move(request.fen)
            grammar = grammar_factory.get_fantastic_move(request.uci, rounded_advantage_change)
            if request.uci == play_result.move.uci() or request.uci == play_result.ponder.uci():
                grammar = grammar_factory.get_fantastic_move(request.uci, rounded_advantage_change)

        return get_random_generation(grammar)
