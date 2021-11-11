import random

from nltk import CFG
from nltk.parse.generate import generate

from domain.client_json import DescriptionRequest
from data.grammars import DEFAULT_OPENING, STOCKFISH_OPENING, USER_OPENING, USER_FIRST_OPENING, USER_WIN_CONDITION, \
    STOCKFISH_WIN_CONDITION, STALEMATE_ENDING, USER_CHECKMATING, STOCKFISH_CHECKMATING, USER_CHECKMATED, \
    STOCKFISH_CHECKMATED
from domain.repository import Repository
from service.stockfish_service import StockfishService, Outcome


def get_random_generation(grammar):
    descriptions = []
    for description in generate(grammar, n=10):
        descriptions.append(' '.join(description))
    return [random.choice(descriptions)]


def get_move(move: str, opening: list):
    if len(opening) != 0:
        opening_name = 'the ' + opening[0]['name']
        return opening_name
    return move


class DescriptionService(object):
    HUMAN = "human"
    STOCKFISH = "stockfish"

    def __init__(self):
        self.repository = Repository()
        self.stockfish_service = StockfishService()

    def get_description(self, request: DescriptionRequest) -> []:
        """
        :param request :
        :return description:
        For a given DescriptionRequest : (user, moveStack, move, fen), generate an human readable description based on:
        opening scenario, winning conditions, mate conditions...
        """

        descriptions = []
        descriptions.extend(self.get_opening_description(request))
        descriptions.extend(self.get_mate_description(request))
        descriptions.extend(self.get_end_description(request))
        return descriptions

    def get_opening_description(self, request: DescriptionRequest):
        """
        :param request :
        :return description:
        Queries the database to determine if the board is in a particular opening scenario. Returns a relevant
        generated description with Wikipedia link if it exists.
        """

        grammar = CFG.fromstring(DEFAULT_OPENING.format(user=request.user, move=request.move))
        opening = self.repository.query_opening_by_move_stack(request.moveStack)
        move = get_move(request.move, opening)

        if request.user == self.HUMAN:
            # special case for opening move
            if len(request.moveStack) == 1:
                grammar = CFG.fromstring(USER_FIRST_OPENING.format(move=move))
            else:
                previous_move = get_move(request.moveStack[len(request.moveStack) - 2],
                                         self.repository.query_opening_by_move_stack(request.moveStack[:-1]))
                grammar = CFG.fromstring(USER_OPENING.format(previous_move=previous_move, move=move))

        elif request.user == self.STOCKFISH:
            previous_move = get_move(request.moveStack[len(request.moveStack) - 2],
                                     self.repository.query_opening_by_move_stack(request.moveStack[:-1]))
            grammar = CFG.fromstring(STOCKFISH_OPENING.format(previous_move=previous_move, move=move))

        return get_random_generation(grammar)

    def get_end_description(self, request: DescriptionRequest):
        """
        :param request:
        :return description:
        Uses Stockfish to analyse the board for end conditions: won, lost, stalemate.
        Generates a natural language description if the conditions are met.
        """

        end_result = self.stockfish_service.is_over(request.fen)
        if end_result is None:
            return []

        grammar = ""
        if self.stockfish_service.is_over(request.fen) == Outcome.WHITE:
            grammar = CFG.fromstring(USER_WIN_CONDITION.format(move_count=(len(request.moveStack) // 2)))
        elif self.stockfish_service.is_over(request.fen) == Outcome.BLACK:
            grammar = CFG.fromstring(STOCKFISH_WIN_CONDITION.format(move_count=(len(request.moveStack) // 2)))
        elif self.stockfish_service.is_over(request.fen) == Outcome.STALE:
            grammar = CFG.fromstring(STALEMATE_ENDING.format(move_count=(len(request.moveStack) // 2)))
        return get_random_generation(grammar)

    def get_mate_description(self, request: DescriptionRequest):
        """
        :param request:
        :return description:
        Use Stockfish to analyse whether a Checkmate is available or if the user is being checkmated.
        Generates a natural language description if the conditions are met.
        """

        checkmate_result = self.stockfish_service.get_checkmate_result(request)
        if checkmate_result is None:
            return []

        grammar = ""
        if checkmate_result['user'] == Outcome.WHITE:
            if checkmate_result['moves'] == 0:
                grammar = CFG.fromstring(USER_CHECKMATED)
            else:
                grammar = CFG.fromstring(USER_CHECKMATING.format(move_count=(checkmate_result['moves'])))

        if checkmate_result['user'] == Outcome.BLACK:
            if checkmate_result['moves'] == 0:
                grammar = CFG.fromstring(STOCKFISH_CHECKMATED)
            else:
                grammar = CFG.fromstring(STOCKFISH_CHECKMATING.format(move_count=(checkmate_result['moves'])))

        return get_random_generation(grammar)
