import os
import platform
import math
import chess.engine


file_path = os.path.dirname(os.path.abspath(__file__))

if 'Windows' in platform.system():
  engine_path = 'stockfish_10_x64_windows.exe'
elif 'Linux' in platform.system():
  engine_path = 'stockfish_10_x64_linux'
else:
  engine_path = 'stockfish_13_x64_mac'