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
    S -> P C'.' | P C 'in {move_count} moves.'
    P -> 'You' 
    C -> "have won" | "have beaten your opponent"
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
