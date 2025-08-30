import threading
from enum import Enum

class Player(Enum):
    NONE = 0
    MAX = 1
    MIN = 2
    TIE = 3

class game_state:
    def __init__(self):
        self.board_size = 5
        self.board = [[Player.NONE for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = Player.MAX
        self.game_over = False
        self.winner = Player.NONE
        self.lock = threading.Lock()
