import random

import chess
from nltk.parse.generate import generate

HUMAN = "human"
STOCKFISH = "stockfish"


def get_piece_name(uci, fen):
    move = chess.Move.from_uci(uci)
    board = chess.Board(fen)
    return chess.PIECE_NAMES[board.piece_type_at(move.to_square)]


def get_other_user(user):
    if user == HUMAN:
        return STOCKFISH
    else:
        return HUMAN


def get_link(opening: list):
    if len(opening) != 0:
        return opening[0]['wiki_link']
    return None


def get_move(move: str, opening: list):
    if len(opening) != 0:
        opening_name = 'the ' + opening[0]['name']
        return opening_name
    return move


def format_name(original_opening: list, opening: str):
    if len(original_opening) != 0:
        return opening.replace(original_opening[0]['name'] + ": ", '')
    return opening


def get_random_generation(grammar):
    descriptions = []
    for description in generate(grammar):
        descriptions.append(' '.join(description))
    return [random.choice(descriptions)]
