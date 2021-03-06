import logging
import random

import chess
from fastapi import FastAPI
from nltk.parse.generate import generate
from starlette.middleware.cors import CORSMiddleware

BLACK = "black"
WHITE = "white"

ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
]


def configure_app(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def get_piece_name(uci, fen):
    move = chess.Move.from_uci(uci)
    board = chess.Board(fen)
    return chess.PIECE_NAMES[board.piece_type_at(move.to_square)]


def get_to_square(move: chess.Move):
    return chess.SQUARE_NAMES[move.to_square]


def get_other_user(user):
    if user == BLACK:
        return WHITE
    else:
        return BLACK


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
    try:
        descriptions = []
        for description in generate(grammar):
            descriptions.append(' '.join(description))
        return [random.choice(descriptions)]
    except Exception as e:
        print(e)
        return []
