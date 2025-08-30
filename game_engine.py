import threading
from game_state import game_state,Player
import copy

class game_engine:
    def __init__(self):
        self.game_state = game_state()

    def make_move(self, pos_str, player):
        try:
            row, col = map(int, pos_str.split(','))
            with self.game_state.lock:
                if 0 <= row < self.game_state.board_size and 0 <= col < self.game_state.board_size:
                    if self.game_state.board[row][col] == Player.NONE:
                        self.game_state.board[row][col] = player
                        return True
            return False
        except Exception:
            return False

    def undo_move(self, pos_str, player):
        try:
            row, col = map(int, pos_str.split(','))
            with self.game_state.lock:
                if 0 <= row < self.game_state.board_size and 0 <= col < self.game_state.board_size:
                    if self.game_state.board[row][col] != Player.NONE:
                        self.game_state.board[row][col] = Player.NONE
                        return True
            return False
        except Exception:
            return False

    def end_turn(self):
        if self.game_state.current_player == Player.MAX:
            self.game_state.current_player = Player.MIN
        else:
            self.game_state.current_player = Player.MAX
        if self.check_winner() != Player.NONE:
            self.game_state.winner = self.check_winner()
            self.game_state.game_over = True


    def check_winner(self):
        b = self.game_state.board
        size = self.game_state.board_size

        # Reihen prüfen
        for i in range(size):
            if b[i][0] != Player.NONE and all(b[i][j] == b[i][0] for j in range(size)):
                return b[i][0]

        # Spalten prüfen
        for j in range(size):
            if b[0][j] != Player.NONE and all(b[i][j] == b[0][j] for i in range(size)):
                return b[0][j]

        # Diagonale von links oben nach rechts unten
        if b[0][0] != Player.NONE and all(b[i][i] == b[0][0] for i in range(size)):
            return b[0][0]

        # Diagonale von rechts oben nach links unten
        if b[0][size - 1] != Player.NONE and all(b[i][size - 1 - i] == b[0][size - 1] for i in range(size)):
            return b[0][size - 1]

        if all(b[i][j] != Player.NONE for i in range(size) for j in range(size)):
            return Player.TIE

        return Player.NONE  # kein Gewinner

    def get_possible_moves(self):
        moves = []
        for i in range(self.game_state.board_size):
            for j in range(self.game_state.board_size):
                if self.game_state.board[i][j] == Player.NONE:
                    moves.append(f"{i},{j}")
        return moves