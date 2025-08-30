import tkinter as tk
import threading
import time
from game_engine import game_engine
from game_state import Player
from ui import ui
import ai
import ai_perplexity

def make_ai_min_max_move():
    score, best_move = ai_min_max.calc_best_move(max_depth=3, maximizing_player=game_engine.game_state.current_player)
    if best_move is not None:
        game_engine.make_move(best_move, game_engine.game_state.current_player)
    print(f"KI (Spieler {game_engine.game_state.current_player}) setzt Stein bei {best_move}")
    game_engine.end_turn()

def make_ai_perplexety():
    best_move = ai_perplexity.calc_best_move(max_depth=3, maximizing_player=game_engine.game_state.current_player)
    if best_move is not None:
        game_engine.make_move(best_move, game_engine.game_state.current_player)
    print(f"KI (Spieler {game_engine.game_state.current_player}) setzt Stein bei {best_move}")
    game_engine.end_turn()

def game_loop():
    while True:
        while not game_engine.game_state.game_over:
            if game_engine.game_state.current_player == Player.MAX:
                make_ai_perplexety()
            else:
                make_ai_min_max_move()

            # Nach jedem Zug Sieger prüfen (eigentlich schon in place_stone)
            if game_engine.game_state.game_over:
                print(f"Spiel beendet. Gewinner: Spieler {game_engine.game_state.winner}")
                break
            time.sleep(0.2)

if __name__ == "__main__":
    root = tk.Tk()
    game_engine = game_engine()
    ui = ui(root, game_engine)
    ai_min_max = ai.ai(game_engine)
    ai_perplexity = ai_perplexity.ai(game_engine)

    game_thread = threading.Thread(target=game_loop, daemon=True)
    game_thread.start()

    root.mainloop()
