
# Korrigierte Version der AI mit Debug-Ausgaben und Fehlerbehebung

from random import random, choice
from game_state import game_state, Player
from game_engine import game_engine
import time

class ai:
    """
    Korrigierte hochoptimierte AI - das None-Problem wurde behoben
    """

    def __init__(self, game_engine):
        self.MAX_DEPTH=3
        self.max_search_time = 2.0
        self.game_engine = game_engine
        self.MAX_WINNER_VALUE = 10000

        # Transposition Table mit mehr Informationen
        self.transposition_table = {}
        self.table_hits = 0
        self.table_entries = 0

        # Killer Moves: 2 Killer Moves pro Tiefe
        self.killer_moves = [[None, None] for _ in range(32)]  # Max 32 Tiefen

        # History Heuristic: Bonuspunkte für gute Züge
        self.history_table = {}

        # Principal Variation aus vorheriger Iteration
        self.principal_variation = []

        # Zobrist Hashing für bessere Transposition Table
        self.zobrist_table = self._init_zobrist_table()

        # Statistiken
        self.nodes_searched = 0
        self.cutoffs = 0
        self.quiescence_nodes = 0

    def _init_zobrist_table(self):
        """Initialisiert Zobrist Hash Tabelle für bessere Position Hashing"""
        import random

        # Für jede Position auf dem Brett und jeden Spieler einen Zufallswert
        zobrist = {}
        board_size = self.game_engine.game_state.board_size

        for row in range(board_size):
            for col in range(board_size):
                for player in [Player.MAX, Player.MIN]:
                    zobrist[(row, col, player)] = random.getrandbits(64)

        # Zusätzlicher Wert für den aktuellen Spieler
        zobrist['turn'] = random.getrandbits(64)

        return zobrist

    def compute_zobrist_hash(self):
        """Berechnet Zobrist Hash für aktuelle Position"""
        hash_value = 0
        board = self.game_engine.game_state.board
        board_size = self.game_engine.game_state.board_size

        for row in range(board_size):
            for col in range(board_size):
                if board[row][col] != 0:
                    player = Player.MAX if board[row][col] == 1 else Player.MIN
                    hash_value ^= self.zobrist_table.get((row, col, player), 0)

        return hash_value

    def calc_best_move(self, maximizing_player):
        return self.pvs(maximizing_player, self.MAX_DEPTH)

    def pvs(self, maximizing_player, max_depth, cache=None):
        """
        KORRIGIERT: Hauptsuchfunktion mit Iterative Deepening
        """
        print(f"=== CALC_BEST_MOVE START: max_depth={max_depth}, player={maximizing_player} ===")

        # Erst prüfen ob überhaupt Züge verfügbar sind
        all_moves = self.game_engine.get_possible_moves()
        print(f"Verfügbare Züge: {len(all_moves)} - {all_moves}")

        if not all_moves:
            print("FEHLER: Keine Züge verfügbar!")
            return None

        start_time = time.time()
        best_move = None
        best_score = float('-inf') if maximizing_player == Player.MAX else float('inf')

        # FALLBACK: Nimm ersten verfügbaren Zug als Notlösung
        fallback_move = choice(all_moves)
        print(f"Fallback Zug gesetzt: {fallback_move}")

        # Iterative Deepening: Starte mit Tiefe 1 und erhöhe schrittweise
        for depth in range(1, max_depth + 1):  # KORREKTUR: max_depth + 1 damit max_depth erreicht wird
            if time.time() - start_time > self.max_search_time * 0.9:
                print(f"Zeitlimit erreicht vor Tiefe {depth}")
                break

            self.nodes_searched = 0
            self.cutoffs = 0
            self.quiescence_nodes = 0

            try:
                print(f"\n--- Starte Suche Tiefe {depth} ---")
                score, move = self.pvs_search(depth, float('-inf'), float('inf'),
                                            maximizing_player, start_time, True)

                print(f"Tiefe {depth}: Score={score}, Move={move}")

                if move is not None:
                    best_move = move
                    best_score = score
                    print(f"Neuer bester Zug: {best_move} mit Score {best_score}")

                    # Aktualisiere Principal Variation
                    self._update_principal_variation(move, depth)
                else:
                    print(f"WARNUNG: Tiefe {depth} lieferte None als Zug!")

                print(f"Tiefe {depth}: Bester Zug {best_move}, Score {best_score:.2f}, "
                      f"Knoten: {self.nodes_searched}, Cutoffs: {self.cutoffs}")

            except TimeoutError:
                print(f"Zeitlimit erreicht bei Tiefe {depth}")
                break
            except Exception as e:
                print(f"FEHLER in Tiefe {depth}: {e}")
                import traceback
                traceback.print_exc()
                break

        # KORREKTUR: Falls immer noch kein best_move, verwende Fallback
        if best_move is None:
            print(f"WARNUNG: Kein bester Zug gefunden, verwende Fallback: {fallback_move}")
            best_move = fallback_move

        print(f"=== FINALE ANTWORT: {best_move} ===")
        return best_move

    def pvs_search(self, depth, alpha, beta, maximizing_player, start_time, is_pv_node=False):
        """
        KORRIGIERT: Principal Variation Search mit Alpha-Beta Pruning
        """
        # Zeitkontrolle
        if time.time() - start_time > self.max_search_time:
            raise TimeoutError()

        self.nodes_searched += 1

        # Transposition Table Lookup
        hash_key = self.compute_zobrist_hash()
        tt_entry = self.transposition_table.get(hash_key)

        if tt_entry and tt_entry['depth'] >= depth and not is_pv_node:  # KORREKTUR: Nicht bei PV-Knoten
            self.table_hits += 1
            tt_score, tt_move, tt_flag = tt_entry['score'], tt_entry['move'], tt_entry['flag']

            if tt_flag == 'EXACT':
                return tt_score, tt_move
            elif tt_flag == 'LOWERBOUND' and tt_score >= beta:
                return tt_score, tt_move
            elif tt_flag == 'UPPERBOUND' and tt_score <= alpha:
                return tt_score, tt_move

        # Terminalknoten oder maximale Tiefe erreicht
        winner = self.game_engine.check_winner()
        if winner != Player.NONE or depth == 0:
            if depth == 0 and winner == Player.NONE:
                # Quiescence Search für instabile Positionen
                return self.quiescence_search(alpha, beta, maximizing_player, start_time, 0)
            else:
                score = self.evaluate_board_advanced()
                return score, None

        # Move Ordering: Sortiere Züge nach Qualität
        possible_moves = self.get_ordered_moves(depth, tt_entry)
        print(f"  Tiefe {depth}: {len(possible_moves)} geordnete Züge")

        if not possible_moves:
            print(f"  Tiefe {depth}: KEINE ZÜGE VERFÜGBAR!")
            return self.evaluate_board_advanced(), None

        best_move = None
        best_score = float('-inf') if maximizing_player == Player.MAX else float('inf')
        valid_moves_tried = 0

        # Principal Variation Search
        first_move = True

        for i, move in enumerate(possible_moves):
            print(f"    Teste Zug {i+1}/{len(possible_moves)}: {move}")

            # KORREKTUR: Prüfe Zug vor make_move
            original_board = [row[:] for row in self.game_engine.game_state.board]  # Backup

            success = self.game_engine.make_move(move, maximizing_player)
            if not success:
                print(f"      FEHLER: make_move fehlgeschlagen für {move}")
                continue

            valid_moves_tried += 1
            print(f"      Zug {move} erfolgreich gemacht")


            if first_move:
                # Vollsuche für ersten (besten) Zug
                score, _ = self.pvs_search(depth - 1, -beta, -alpha,
                                         self._switch_player(maximizing_player),
                                         start_time, is_pv_node)
                score = -score
                first_move = False
                print(f"        Erster Zug {move}: Score {score}")
            else:
                # Null-Window Search für nachfolgende Züge
                score, _ = self.pvs_search(depth - 1, -alpha-1, -alpha,
                                         self._switch_player(maximizing_player),
                                         start_time, False)
                score = -score
                print(f"        Null-Window {move}: Score {score}")

                # Re-Search mit vollem Fenster wenn nötig
                if alpha < score < beta and is_pv_node:
                    score, _ = self.pvs_search(depth - 1, -beta, -score,
                                             self._switch_player(maximizing_player),
                                             start_time, True)
                    score = -score
                    print(f"        Re-Search {move}: Score {score}")



            # WICHTIG: Zug rückgängig machen
            success_undo = self.game_engine.undo_move(move, maximizing_player)
            if not success_undo:
                print(f"      WARNUNG: undo_move fehlgeschlagen für {move}")
                # Restore backup
                self.game_engine.game_state.board = original_board

            # Alpha-Beta Update
            if maximizing_player == Player.MAX:
                if score > best_score:
                    best_score = score
                    best_move = move
                    print(f"        NEUER BESTER ZUG: {move} mit Score {score}")

                if score > alpha:
                    alpha = score

                if alpha >= beta:
                    # Beta Cutoff - speichere Killer Move
                    self._update_killer_moves(move, depth)
                    self._update_history(move, depth)
                    self.cutoffs += 1
                    print(f"        Beta Cutoff bei Zug {move}")
                    break
            else:
                if score < best_score:
                    best_score = score
                    best_move = move
                    print(f"        NEUER BESTER ZUG: {move} mit Score {score}")

                if score < beta:
                    beta = score

                if beta <= alpha:
                    # Alpha Cutoff
                    self._update_killer_moves(move, depth)
                    self._update_history(move, depth)
                    self.cutoffs += 1
                    print(f"        Alpha Cutoff bei Zug {move}")
                    break

        print(f"  Tiefe {depth}: {valid_moves_tried} gültige Züge probiert, bester: {best_move}")

        # KORREKTUR: Falls kein gültiger Zug gefunden, nimm ersten verfügbaren
        if best_move is None and possible_moves:
            print(f"  NOTFALL: Kein bester Zug gefunden, nehme ersten: {possible_moves[0]}")
            best_move = possible_moves[0]

        # Speichere in Transposition Table
        self._store_transposition(hash_key, depth, best_score, best_move, alpha, beta)

        return best_score, best_move

    # Alle anderen Methoden bleiben unverändert...
    def quiescence_search(self, alpha, beta, maximizing_player, start_time, qsearch_depth):
        """Quiescence Search für instabile Positionen"""
        if time.time() - start_time > self.max_search_time or qsearch_depth > 6:
            return self.evaluate_board_advanced(), None

        self.quiescence_nodes += 1

        # Stand Pat: Bewertung der aktuellen Position
        stand_pat = self.evaluate_board_advanced()

        if maximizing_player == Player.MAX:
            if stand_pat >= beta:
                return stand_pat, None
            if stand_pat > alpha:
                alpha = stand_pat
        else:
            if stand_pat <= alpha:
                return stand_pat, None
            if stand_pat < beta:
                beta = stand_pat

        # Nur "laute" Züge (Captures, Checks) in Quiescence
        capturing_moves = self.get_capturing_moves()

        best_score = stand_pat
        best_move = None

        for move in capturing_moves:
            success = self.game_engine.make_move(move, maximizing_player)
            if not success:
                continue

            score, _ = self.quiescence_search(-beta, -alpha,
                                            self._switch_player(maximizing_player),
                                            start_time, qsearch_depth + 1)
            score = -score

            self.game_engine.undo_move(move, maximizing_player)

            if maximizing_player == Player.MAX:
                if score > best_score:
                    best_score = score
                    best_move = move
                if score > alpha:
                    alpha = score
                if alpha >= beta:
                    break
            else:
                if score < best_score:
                    best_score = score
                    best_move = move
                if score < beta:
                    beta = score
                if beta <= alpha:
                    break

        return best_score, best_move

    def get_ordered_moves(self, depth, tt_entry=None):
        """Move Ordering: Sortiert Züge nach geschätzter Qualität"""
        moves = self.game_engine.get_possible_moves()
        if not moves:
            return []

        move_scores = []

        for move in moves:
            score = 0

            # PV Move aus vorheriger Iteration
            if self.principal_variation and move == self.principal_variation[0]:
                score += 10000

            # Transposition Table Move
            if tt_entry and tt_entry.get('move') == move:
                score += 9000

            # Killer Moves
            if depth < len(self.killer_moves) and move in self.killer_moves[depth]:
                score += 8000

            # History Heuristic
            score += self.history_table.get(move, 0)

            # Positionelle Bewertung (Zentrum bevorzugen)
            if hasattr(move, '__iter__') and len(move) == 2:
                row, col = move
                center = self.game_engine.game_state.board_size // 2
                distance_from_center = abs(row - center) + abs(col - center)
                score += 100 - distance_from_center * 10

            move_scores.append((score, move))

        # Sortiere nach Score absteigend
        move_scores.sort(reverse=True)
        return [move for _, move in move_scores]

    def get_capturing_moves(self):
        """Ermittelt Züge die Captures oder Checks sind (für Quiescence)"""
        return self.game_engine.get_possible_moves()

    def _update_killer_moves(self, move, depth):
        """Aktualisiert Killer Moves für diese Tiefe"""
        if depth < len(self.killer_moves):
            if self.killer_moves[depth][0] != move:
                self.killer_moves[depth][1] = self.killer_moves[depth][0]
                self.killer_moves[depth][0] = move

    def _update_history(self, move, depth):
        """Aktualisiert History Heuristic"""
        self.history_table[move] = self.history_table.get(move, 0) + depth * depth

    def _update_principal_variation(self, move, depth):
        """Aktualisiert Principal Variation"""
        if not self.principal_variation:
            self.principal_variation = [move]
        else:
            self.principal_variation[0] = move

    def _store_transposition(self, hash_key, depth, score, move, alpha, beta):
        """Speichert Ergebnis in Transposition Table"""
        # KORREKTUR: Nur speichern wenn move existiert
        if move is None:
            return

        if score <= alpha:
            flag = 'UPPERBOUND'
        elif score >= beta:
            flag = 'LOWERBOUND'
        else:
            flag = 'EXACT'

        self.transposition_table[hash_key] = {
            'score': score,
            'move': move,
            'depth': depth,
            'flag': flag
        }
        self.table_entries += 1

        # Begrenze Tabellengröße
        if len(self.transposition_table) > 100000:
            keys_to_remove = list(self.transposition_table.keys())[:10000]
            for key in keys_to_remove:
                del self.transposition_table[key]

    def _switch_player(self, player):
        """Wechselt zwischen MAX und MIN Spieler"""
        return Player.MIN if player == Player.MAX else Player.MAX

    def evaluate_board_advanced(self):
        """Erweiterte Evaluierungsfunktion mit mehreren Faktoren"""
        winner = self.game_engine.check_winner()
        if winner == Player.MAX:
            return self.MAX_WINNER_VALUE
        elif winner == Player.MIN:
            return -self.MAX_WINNER_VALUE

        score = 0

        # Materialbalance
        score += self._evaluate_material()

        # Positionelle Faktoren
        score += self._evaluate_position()

        # Mobilität
        score += self._evaluate_mobility()

        # Kontrolle des Zentrums
        score += self._evaluate_center_control()

        return score

    def _evaluate_material(self):
        """Evaluiert Materialbalance"""
        score = 0
        board = self.game_engine.game_state.board
        board_size = self.game_engine.game_state.board_size

        # Reihen
        for i in range(board_size):
            line = board[i]
            score += self._line_score(line)

        # Spalten
        for j in range(board_size):
            column = [board[i][j] for i in range(board_size)]
            score += self._line_score(column)

        # Diagonalen
        diag1 = [board[i][i] for i in range(board_size)]
        diag2 = [board[i][board_size - 1 - i] for i in range(board_size)]
        score += self._line_score(diag1)
        score += self._line_score(diag2)

        return score

    def _line_score(self, line):
        """Bewertet eine Linie"""
        if all(cell in (0, 1) for cell in line):
            count = line.count(Player.MAX)
            return count * count  # Quadratische Bewertung
        if all(cell in (0, 2) for cell in line):
            count = line.count(Player.MIN)
            return -count * count
        return 0

    def _evaluate_position(self):
        """Bewertet Positionsvorteile"""
        score = 0
        board = self.game_engine.game_state.board
        board_size = self.game_engine.game_state.board_size
        center = board_size // 2

        for i in range(board_size):
            for j in range(board_size):
                if board[i][j] != 0:
                    distance_from_center = abs(i - center) + abs(j - center)
                    center_value = max(0, 3 - distance_from_center)

                    if board[i][j] == Player.MAX:
                        score += center_value
                    else:
                        score -= center_value

        return score

    def _evaluate_mobility(self):
        """Bewertet Mobilität"""
        move_count = len(self.game_engine.get_possible_moves())
        return move_count * 0.1

    def _evaluate_center_control(self):
        """Bewertet Kontrolle über das Zentrum"""
        score = 0
        board = self.game_engine.game_state.board
        board_size = self.game_engine.game_state.board_size
        center = board_size // 2

        center_positions = [(center-1, center-1), (center-1, center),
                          (center, center-1), (center, center)]

        for row, col in center_positions:
            if 0 <= row < board_size and 0 <= col < board_size:
                if board[row][col] == Player.MAX:
                    score += 5
                elif board[row][col] == Player.MIN:
                    score -= 5

        return score

    def get_statistics(self):
        """Gibt Suchstatistiken zurück"""
        return {
            'nodes_searched': self.nodes_searched,
            'cutoffs': self.cutoffs,
            'quiescence_nodes': self.quiescence_nodes,
            'table_hits': self.table_hits,
            'table_entries': self.table_entries,
            'hit_rate': self.table_hits / max(1, self.nodes_searched) * 100
        }
