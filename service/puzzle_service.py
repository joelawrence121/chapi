import random

from domain.repository import Repository


class PuzzleService(object):

    def __init__(self):
        self.repository = Repository()

    def get_single_move_puzzle(self, type_name: str):
        single_move_puzzles = self.repository.query_single_move_by_type(type_name)
        return random.choice(single_move_puzzles)
