import random

from nltk.parse.generate import generate

import grammar_factory
from domain.client_json import DescriptionRequest
from domain.repository import Repository
from service.stockfish_service import StockfishService, Outcome


def get_random_generation(grammar):
    descriptions = []
    for description in generate(grammar):
        descriptions.append(' '.join(description))
    return [random.choice(descriptions)]


def get_move(move: str, opening: list):
    if len(opening) != 0:
        opening_name = 'the ' + opening[0]['name']
        return opening_name
    return move


def get_link(opening: list):
    if len(opening) != 0:
        return opening[0]['wiki_link']
    return None


def format_name(original_opening: list, opening: str):
    if len(original_opening) != 0:
        return opening.replace(original_opening[0]['name'] + ": ", '')
    return opening


class DescriptionService(object):
    HUMAN = "human"
    STOCKFISH = "stockfish"
    CRITICAL_BLUNDER_THRESHOLD = -0.6

    def __init__(self):
        self.repository = Repository()
        self.stockfish_service = StockfishService()

    def get_description(self, request: DescriptionRequest) -> []:
        """
        For a given DescriptionRequest : (user, moveStack, move, fen), generate an array of English descriptions
        providing insight on: the opening scenario, winning conditions, mate conditions...
        """

        response = {'descriptions': [], 'link': None, 'score': self.stockfish_service.get_relative_score(request)}

        opening_data = self.get_opening_description(request)
        response['descriptions'].extend(opening_data[0])
        response['link'] = opening_data[1]
        response['opening'] = opening_data[2]
        response['descriptions'].extend(self.get_move_suggestions(request))
        response['descriptions'].extend(self.get_mate_description(request))
        response['descriptions'].extend(self.get_end_description(request))
        response['descriptions'].extend(self.get_blunder_description(request))
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

        if request.user == self.HUMAN:
            # special case for opening move
            if len(request.moveStack) == 1:
                grammar = grammar_factory.get_user_first_opening(move)
            else:
                previous_move = get_move(request.moveStack[len(request.moveStack) - 2],
                                         self.repository.query_opening_by_move_stack(request.moveStack[:-1]))
                grammar = grammar_factory.get_user_move(move, previous_move, capture, is_check)

        elif request.user == self.STOCKFISH:
            previous_move = get_move(request.moveStack[len(request.moveStack) - 2],
                                     self.repository.query_opening_by_move_stack(request.moveStack[:-1]))
            grammar = grammar_factory.get_stockfish_move(move, previous_move, capture, is_check)

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
        Use Stockfish to analyse whether the move made was a critical blunder.
        Generate a natural language description of the blunder and why.
        """
        blunder_result = self.stockfish_service.get_blunder_result(request)
        if blunder_result is None:
            return []

        grammar = grammar_factory.get_user_blunder(request.uci, abs(round(blunder_result * 100)),
                                                   blunder_result < self.CRITICAL_BLUNDER_THRESHOLD)
        return get_random_generation(grammar)

    def get_move_suggestions(self, request):
        """
        On Stockfish's move, return suggestion moves to the player based on common openings in the database.
        """

        if request.user == self.HUMAN:
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
