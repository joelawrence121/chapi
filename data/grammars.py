
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