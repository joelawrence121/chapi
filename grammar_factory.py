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
STOCK_E_LC = "    OP -> 'stockfish' | 'your opponent' | 'black'"

USER_FIRST_OPENING = """
    S -> P A 'with' M
    A -> 'open' | 'begin' | 'start off' 
    M -> "{move}."
"""


def get_user_first_opening(move):
    return CFG.fromstring((USER_FIRST_OPENING + YOU_E).format(move=move))


ATCK_ADJ = """    ADJ -> 'capturing' | 'taking' | 'attacking'
"""
USER_MOVE = """
    S -> P A M | P AC M 
    AC -> "respond to {previous_move}" | "counter {previous_move}"
"""
NO_CAPTURE_AM = """    
    A -> 'respond' | 'counter'
"""
CAPTURE_AM = """    
    A -> W 'by' C | ADJ_P "{piece}"
    W -> 'respond' | 'counter'
    ADJ_P -> 'capture' | 'attack' | 'take'
    C -> ADJ ADJ_OP_C "{piece}"
    ADJ_OP_C -> 'their' | "Stockfish's" | "black's" | 'the' 
""" + ATCK_ADJ
NO_CHECK_M = """    M -> 'with' "{move}." 
"""
CHECK_M = """   
    M -> 'with' "{move}," M_D
    M_D -> 'which is now check.' | 'putting' OP 'into check.' | 'checking' OP 
"""


def get_user_move(move, previous_move, capture, is_check):
    grammar = USER_MOVE + YOU_E

    if capture is not None:
        grammar += CAPTURE_AM.format(piece=capture)
    else:
        grammar += NO_CAPTURE_AM

    if is_check:
        grammar += CHECK_M
        grammar += STOCK_E_LC
    else:
        grammar += NO_CHECK_M

    return CFG.fromstring(grammar.format(move=move, previous_move=previous_move))


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


USER_BLUNDER = """
    S -> I C 'a' ADJ 'blunder,' ES | SS I C 'a blunder.' | "You've blundered." SS I C 'a' ADJ 'blunder.'
    I -> 'This move' | '{move}' | 'This'
    ES -> 'you' D
    SS -> 'You' D 
    D -> VL 'a {loss} point advantage.'
    VL -> 'have lost' | 'are down' | 'have dropped' | 'have cost yourself'
"""
NORMAL_CS = """    C -> V 'be' VP 
    V -> 'could' | 'may' | 'might'
    VP -> 'considered' | 'conceivably thought of as' | 'thought of as'
    ADJ -> 'fair' | 'considerable'
"""
CRITICAL_CS = """    C -> 'is' V 
     V -> 'definitely' | 'certainly' | 'without doubt' | 'absolutely' | 'decidedly' | 'undeniably'
     ADJ -> 'critical' | 'huge'
"""


def get_user_blunder(move, loss, critical: bool):
    if critical:
        return CFG.fromstring((USER_BLUNDER + CRITICAL_CS).format(move=move, loss=str(loss)))
    return CFG.fromstring((USER_BLUNDER + NORMAL_CS).format(move=move, loss=str(loss)))


# -------------- STOCKFISH --------------

STOCKFISH_MOVE = """
    S -> OP A M | OP AC M 
    AC -> "responds to  {previous_move}" | "counters {previous_move}"
"""
NO_CAPTURE_S_AM = """    
    A -> 'responds' | 'counters' | 'answers' | 'comes back'
"""
CAPTURE_S_AM = """    
    A -> W 'by' C | ADJ_P "{piece}"
    ADJ_P -> 'captures' | 'takes' | 'attacks'
    W -> 'responds' | 'counters' | 'answers' | 'comes back'
    C -> ADJ ADJ_OP_C "{piece}"
    ADJ_OP_C -> 'your' | 'the' | "white's" 
""" + ATCK_ADJ
NO_CHECK_S_M = """    M -> 'with' "{move}." 
"""
CHECK_S_M = """   
    M -> 'with' "{move}," M_D
    M_D -> 'which is now check.' | 'putting you into check.' | 'checking you.'  
"""


def get_stockfish_move(move, previous_move, capture, is_check):
    grammar = STOCKFISH_MOVE + STOCK_E

    if capture is not None:
        grammar += CAPTURE_S_AM.format(piece=capture)
    else:
        grammar += NO_CAPTURE_S_AM

    if is_check:
        grammar += CHECK_S_M
    else:
        grammar += NO_CHECK_S_M

    return CFG.fromstring(grammar.format(move=move, previous_move=previous_move))


STOCKFISH_WIN_CONDITION = """
    S -> OP C 'in {move_count} moves.'
    C -> "has won" | "wins" | "has beaten you" 
"""


def get_stockfish_win_condition(move_count):
    return CFG.fromstring((STOCKFISH_WIN_CONDITION + STOCK_E).format(move_count=move_count))


STOCKFISH_CHECKMATING = """
    S -> OP V_D E | OP V_P 'they can checkmate you' E 
    V_P -> 'thinks' | 'believes' | 'predicts' 
    V_D -> 'is' V_T 'to checkmate you' | 'is' V_S 'a mate'
    V_S -> 'setting up for' | 'is steering you into' | 'creating a' 
    V_T -> 'trying' | 'attempting' 
    E -> 'in {move_count} moves.'
"""


def get_stockfish_checkmating(move_count):
    return CFG.fromstring((STOCKFISH_CHECKMATING + STOCK_E).format(move_count=move_count))


STOCKFISH_CHECKMATED = """
    S -> OP 'has checkmated you.'
"""


def get_stockfish_checkmated():
    return CFG.fromstring(STOCKFISH_CHECKMATED + STOCK_E)
