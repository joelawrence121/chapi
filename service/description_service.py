import random

from nltk import CFG
from nltk.parse.generate import generate

from client.client_json import OpeningRequest
from domain.repository import Repository


class DescriptionService(object):
    HUMAN = "human"
    STOCKFISH = "stockfish"
    DEFAULT_G = """
        S -> U A M 
        U -> "{user}"
        A -> 'plays' | 'moves'
        M -> "{move}"
    """
    OPENING_G = """
        S -> P A 'with' M
        P -> 'You'
        A -> 'open' | 'begin' | 'start off' 
        M -> "{move}."
    """
    USER_G = """
        S -> P A M | P AC 'with' M 
        P -> 'You' 
        AC -> "respond to {previous_move}" | "counter {previous_move}"
        A -> 'respond with' | 'counter with' | 'play'
        M -> "{move}."
    """
    STOCKFISH_G = """
        S -> P A 'with' M | P AC 'with' M 
        P -> 'Stockfish' | 'Your opponent' | 'Black'
        AC -> "responds to  {previous_move}" | "counters {previous_move}"
        A -> 'responds' | 'counters' | 'answers' | 'comes back'
        M -> "{move}."
    """

    def __init__(self):
        self.repository = Repository()

    def get_description(self, request: OpeningRequest) -> str:

        grammar = CFG.fromstring(self.DEFAULT_G.format(user=request.user, move=request.move))
        opening = self.repository.query_opening_by_move_stack(request.moveStack)
        move = get_move(request.move, opening)

        if request.user == self.HUMAN:
            # special case for opening move
            if len(request.moveStack) == 1:
                grammar = CFG.fromstring(self.OPENING_G.format(move=move))
            else:
                previous_move = get_move(request.moveStack[len(request.moveStack) - 2],
                                         self.repository.query_opening_by_move_stack(request.moveStack[:-1]))
                grammar = CFG.fromstring(self.USER_G.format(previous_move=previous_move, move=move))

        elif request.user == self.STOCKFISH:
            previous_move = get_move(request.moveStack[len(request.moveStack) - 1],
                                     self.repository.query_opening_by_move_stack(request.moveStack[:-1]))
            grammar = CFG.fromstring(self.STOCKFISH_G.format(previous_move=previous_move, move=move))

        descriptions = []
        for description in generate(grammar, n=10):
            descriptions.append(' '.join(description))
        return random.choice(descriptions)


def get_move(move: str, opening: list):
    if len(opening) != 0:
        opening_name = 'the ' + opening[0]['name']
        return opening_name
    return move
