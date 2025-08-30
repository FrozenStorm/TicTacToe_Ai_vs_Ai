from game_state import game_state, Player
from game_engine import game_engine

class ai:
    def __init__(self, game_engine):
        self.game_engine = game_engine
        self.MAX_WINNER_VALUE = 10000

    def minimax(self, depth, maximizing_player, cache=None):
        if cache is None:
            cache = {}

        board_key = self._board_to_key()
        if board_key in cache:
            return cache[board_key]

        winner = self.game_engine.check_winner()
        if winner != Player.NONE or depth == 0:
            score = self.evaluate_board()
            cache[board_key] = (score, None)
            return score, None

        possible_moves = self.game_engine.get_possible_moves()

        if maximizing_player == Player.MAX:
            max_eval = float('-inf')
            best_move = None
            for move in possible_moves:
                success = self.game_engine.make_move(move, Player.MAX)
                if not success:
                    continue
                eval_score, _ = self.minimax(depth - 1, Player.MIN, cache)
                self.game_engine.undo_move(move, Player.MAX)  # Zum zurückstellen aktuellen Zug wieder entfernen
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
            cache[board_key] = (max_eval, best_move)
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            for move in possible_moves:
                success = self.game_engine.make_move(move, Player.MIN)
                if not success:
                    continue
                eval_score, _ = self.minimax(depth - 1, Player.MAX, cache)
                self.game_engine.undo_move(move, Player.MIN)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
            cache[board_key] = (min_eval, best_move)
            return min_eval, best_move

    def _board_to_key(self):
        return ''.join(str(cell) for row in self.game_engine.game_state.board for cell in row)

    def evaluate_board(self):
        winner = self.game_engine.check_winner()
        if winner == Player.MAX:
            return self.MAX_WINNER_VALUE  # Spieler 1 (max) hat gewonnen
        elif winner == Player.MIN:
            return -self.MAX_WINNER_VALUE  # Spieler 2 (min) hat gewonnen

        def line_score(line):
            # +1 für jeden Stein von Spieler 1 in einer Linie ohne Spieler 2 Steine,
            # -1 für jeden Stein von Spieler 2 in einer Linie ohne Spieler 1 Steine,
            # 0 bei gemischten Linien
            if all(cell in (0, 1) for cell in line):
                return line.count(Player.MAX)
            if all(cell in (0, 2) for cell in line):
                return -line.count(Player.MIN)
            return 0

        score = 0
        b = self.game_engine.game_state.board
        size = self.game_engine.game_state.board_size

        for i in range(size):
            score += line_score(b[i])

        for j in range(size):
            column = [b[i][j] for i in range(size)]
            score += line_score(column)

        diag1 = [b[i][i] for i in range(size)]
        diag2 = [b[i][size - 1 - i] for i in range(size)]
        score += line_score(diag1)
        score += line_score(diag2)

        return score