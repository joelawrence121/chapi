import random

from nltk import CFG
from nltk.parse.generate import generate

from client.client_json import DescriptionRequest
from data.grammars import DEFAULT_OPENING, STOCKFISH_OPENING, USER_OPENING, USER_FIRST_OPENING, USER_WIN_CONDITION, \
    STOCKFISH_WIN_CONDITION
from domain.repository import Repository
from service.stockfish_service import StockfishService


class DescriptionService(object):
    HUMAN = "human"
    STOCKFISH = "stockfish"

    def __init__(self):
        self.repository = Repository()
        self.stockfish_service = StockfishService()

    def get_description(self, request: DescriptionRequest) -> str:
        '''
        :DescriptionRequest request :
        :str description:
        For a given DescriptionRequest : (user, moveStack, move, fen), generate an human readable description based on:
        opening scenario, winning conditions, mate conditions...
        '''

        descriptions = []
        descriptions.extend(self.get_opening_description(request))
        descriptions.extend(self.get_mate_description(request))
        descriptions.extend(self.get_end_description(request))
        return ' '.join(descriptions)

    def get_opening_description(self, request: DescriptionRequest):
        '''
        :DescriptionRequest request :
        :[str] description:
        Queries the database to determine if the board is in a particular opening scenario. Returns a relevant
        description if so.
        '''

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

        return self.get_random_generation(grammar)

    def get_mate_description(self, request: DescriptionRequest):
        # TODO: Generate mate descriptions: 'You are being checkmated', 'There's a checkmate in 3 available.' ...
        return []

    def get_end_description(self, request: DescriptionRequest):
        end_result = self.stockfish_service.has_won(request.fen)
        if end_result is None:
            return []

        grammar = ""
        if self.stockfish_service.has_won(request.fen) == 'white':
            grammar = CFG.fromstring(USER_WIN_CONDITION.format(move_count=(len(request.moveStack) // 2)))
        elif self.stockfish_service.has_won(request.fen) == 'black':
            grammar = CFG.fromstring(STOCKFISH_WIN_CONDITION.format(move_count=(len(request.moveStack) // 2)))

        return self.get_random_generation(grammar)

    def get_random_generation(self, grammar):
        descriptions = []
        for description in generate(grammar, n=10):
            descriptions.append(' '.join(description))
        return [random.choice(descriptions)]


def get_move(move: str, opening: list):
    if len(opening) != 0:
        opening_name = 'the ' + opening[0]['name']
        return opening_name
    return move
