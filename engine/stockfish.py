import os
import platform

import chess.engine

file_path = os.path.dirname(os.path.abspath(__file__))

if 'Windows' in platform.system():
    engine_path = 'stockfish_10_x64_windows.exe'
elif 'Linux' in platform.system():
    engine_path = 'stockfish_10_x64_linux'
else:
    engine_path = 'stockfish_13_x64_mac'


class Engine:
    def __init__(self, level):
        self.engine = chess.engine.SimpleEngine.popen_uci(os.path.join(file_path, engine_path))
        self.engine.configure({'Skill Level': level})

    def reconfigure(self, level):
        self.engine.configure({'Skill Level': level})

    def play(self, board, time=0.1):
        return self.engine.play(board, chess.engine.Limit(time))
