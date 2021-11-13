from nltk import CFG

# --------------- DEFAULT ---------------

DEFAULT_OPENING = """
    S -> U A M 
    U -> "{user}"
    A -> 'plays' | 'moves'
    M -> "{move}"
"""


def get_default_opening(user, move):
    return CFG.fromstring(DEFAULT_OPENING.format(user=user, move=move))


STALEMATE_ENDING = """
    S -> P 'in {move_count} moves.'
    P -> 'Stalemate' | 'The game has reached a stalemate' 
"""


def get_stalemate_ending(move_count):
    return CFG.fromstring(STALEMATE_ENDING.format(move_count=move_count))


# ----------------- USER -----------------

YOU_E = "    P -> 'You'"
STOCK_E = "    OP -> 'Stockfish' | 'Your opponent' | 'Black'"

USER_FIRST_OPENING = """
    S -> P A 'with' M
    A -> 'open' | 'begin' | 'start off' 
    M -> "{move}."
"""


def get_user_first_opening(move):
    return CFG.fromstring((USER_FIRST_OPENING + YOU_E).format(move=move))


USER_OPENING = """
    S -> P A M | P AC 'with' M 
    AC -> "respond to {previous_move}" | "counter {previous_move}"
    A -> 'respond with' | 'counter with' | 'play'
    M -> "{move}."
"""


def get_user_opening(move, previous_move):
    return CFG.fromstring((USER_OPENING + YOU_E).format(move=move, previous_move=previous_move))


USER_WIN_CONDITION = """
    S -> P C | P C 'in {move_count} moves.'
    C -> "have won" | "have beaten your opponent"
"""


def get_user_win_condition(move_count):
    return CFG.fromstring((USER_WIN_CONDITION + YOU_E).format(move_count=move_count))


USER_CHECKMATING = """
    S -> 'There is a checkmate available' E | 'There is a checkmate on' OP 'available' E | 'You can checkmate' OP E
    E -> 'in {move_count} moves.'
    OP -> 'Stockfish' | 'your opponent' | 'black'
"""


def get_user_checkmating(move_count):
    return CFG.fromstring(USER_CHECKMATING.format(move_count=move_count))


USER_CHECKMATED = """
    S -> 'You have checkmated' OP 
    OP -> 'Stockfish.' | 'your opponent.' | 'black.'
"""


def get_user_checkmated():
    return CFG.fromstring(USER_CHECKMATED)


# -------------- STOCKFISH --------------

STOCKFISH_OPENING = """
    S -> OP A 'with' M | OP AC 'with' M 
    AC -> "responds to  {previous_move}" | "counters {previous_move}"
    A -> 'responds' | 'counters' | 'answers' | 'comes back'
    M -> "{move}."
"""


def get_stockfish_opening(move, previous_move):
    return CFG.fromstring((STOCKFISH_OPENING + STOCK_E).format(previous_move=previous_move, move=move))


STOCKFISH_WIN_CONDITION = """
    S -> OP C 'in {move_count} moves.'
    C -> "has won" | "wins" | "has beaten you" 
"""


def get_stockfish_win_condition(move_count):
    return CFG.fromstring((STOCKFISH_WIN_CONDITION + STOCK_E).format(move_count=move_count))


STOCKFISH_CHECKMATING = """
    S -> ST | ST E | OP 'thinks they can checkmate you' E 
    ST -> OP 'is trying to checkmate you'
    E -> 'in {move_count} moves.'
"""


def get_stockfish_checkmating(move_count):
    return CFG.fromstring((STOCKFISH_CHECKMATING + STOCK_E).format(move_count=move_count))


STOCKFISH_CHECKMATED = """
    S -> OP 'has checkmated you.'
"""


def get_stockfish_checkmated():
    return CFG.fromstring(STOCKFISH_CHECKMATED + STOCK_E)
