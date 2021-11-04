import random

from domain.repository import Repository


class PuzzleService(object):

    def __init__(self):
        self.repository = Repository()

    def get_single_move_puzzle(self, type_name: str):
        single_move_puzzles = self.repository.query_single_move_by_type(type_name)
        return random.choice(single_move_puzzles)

    def get_type_statistics(self):
        type_statistics = self.repository.get_type_statistics()
        statistics = {'types': [row['type'] for row in type_statistics],
                      'counts': [row['count'] for row in type_statistics]}
        return statistics

    def get_mate_in_n_puzzle(self, n: int):
        mate_puzzles = self.repository.query_mate_in_n_by_n(n)
        return random.choice(mate_puzzles)
