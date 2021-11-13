# --------------- DEFAULT ---------------

DEFAULT_OPENING = """
    S -> U A M 
    U -> "{user}"
    A -> 'plays' | 'moves'
    M -> "{move}"
"""

STALEMATE_ENDING = """
    S -> P 'in {move_count} moves.'
    P -> 'Stalemate' | 'The game has reached a stalemate' 
"""

# ----------------- USER -----------------

USER_FIRST_OPENING = """
    S -> P A 'with' M
    P -> 'You'
    A -> 'open' | 'begin' | 'start off' 
    M -> "{move}."
"""

USER_OPENING = """
    S -> P A M | P AC 'with' M 
    P -> 'You' 
    AC -> "respond to {previous_move}" | "counter {previous_move}"
    A -> 'respond with' | 'counter with' | 'play'
    M -> "{move}."
"""

USER_WIN_CONDITION = """
    S -> P C | P C 'in {move_count} moves.'
    P -> 'You' 
    C -> "have won" | "have beaten your opponent"
"""

USER_CHECKMATING = """
    S -> 'There is a checkmate available' E | 'There is a checkmate on' OP 'available' E | 'You can checkmate' OP E
    E -> 'in {move_count} moves.'
    OP -> 'Stockfish' | 'your opponent' | 'black'
"""

USER_CHECKMATED = """
    S -> 'You have checkmated' OP 
    OP -> 'Stockfish.' | 'your opponent.' | 'black.'
"""

# -------------- STOCKFISH --------------

STOCKFISH_OPENING = """
    S -> P A 'with' M | P AC 'with' M 
    P -> 'Stockfish' | 'Your opponent' | 'Black'
    AC -> "responds to  {previous_move}" | "counters {previous_move}"
    A -> 'responds' | 'counters' | 'answers' | 'comes back'
    M -> "{move}."
"""

STOCKFISH_WIN_CONDITION = """
    S -> P C 'in {move_count} moves.'
    P -> 'Stockfish' | 'Your opponent' | 'Black' 
    C -> "has won" | "wins" | "has beaten you" 
"""

STOCKFISH_CHECKMATING = """
    S -> ST | ST E | OP 'thinks they can checkmate you' E 
    ST -> OP 'is trying to checkmate you'
    OP -> 'Stockfish' | 'Your opponent' | 'Black'
    E -> 'in {move_count} moves.'
"""

STOCKFISH_CHECKMATED = """
    S -> OP 'has checkmated you.'
    OP -> 'Stockfish' | 'Your opponent' | 'Black'
"""
