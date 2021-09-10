import chess


class Client(object):

    def __init__(self, level):
        self.board = chess.Board()

    def get_fen(self):
        return self.board.fen()