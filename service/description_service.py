import random

from nltk import CFG
from nltk.parse.generate import generate

from client.client_json import OpeningRequest
from data.grammars import DEFAULT_G, STOCKFISH_G, USER_G, OPENING_G
from domain.repository import Repository


class DescriptionService(object):
    HUMAN = "human"
    STOCKFISH = "stockfish"

    def __init__(self):
        self.repository = Repository()

    def get_description(self, request: OpeningRequest) -> str:
        '''
        :OpeningRequest request :
        :str description:
        For a given OpeningRequest : (user, moveStack, move, fen), generate an human readable description based on:
        opening scenario, winning conditions, mate conditions...
        '''

        grammar = CFG.fromstring(DEFAULT_G.format(user=request.user, move=request.move))
        opening = self.repository.query_opening_by_move_stack(request.moveStack)
        move = get_move(request.move, opening)

        if request.user == self.HUMAN:
            # special case for opening move
            if len(request.moveStack) == 1:
                grammar = CFG.fromstring(OPENING_G.format(move=move))
            else:
                previous_move = get_move(request.moveStack[len(request.moveStack) - 2],
                                         self.repository.query_opening_by_move_stack(request.moveStack[:-1]))
                grammar = CFG.fromstring(USER_G.format(previous_move=previous_move, move=move))

        elif request.user == self.STOCKFISH:
            previous_move = get_move(request.moveStack[len(request.moveStack) - 2],
                                     self.repository.query_opening_by_move_stack(request.moveStack[:-1]))
            grammar = CFG.fromstring(STOCKFISH_G.format(previous_move=previous_move, move=move))

        descriptions = []
        for description in generate(grammar, n=10):
            descriptions.append(' '.join(description))
        return random.choice(descriptions)


def get_move(move: str, opening: list):
    if len(opening) != 0:
        opening_name = 'the ' + opening[0]['name']
        return opening_name
    return move
