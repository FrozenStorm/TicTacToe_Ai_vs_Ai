import tkinter as tk
import threading
import time
from game_engine import game_engine
from game_state import Player
from ui import ui
from ai import ai

def make_ai_move():
    score, best_move = ai.minimax(depth=5, maximizing_player=game_engine.game_state.current_player)
    if best_move is not None:
        game_engine.make_move(best_move, game_engine.game_state.current_player)
    game_engine.end_turn()
    print(f"KI (Spieler {game_engine.game_state.current_player}) setzt Stein bei {best_move}")

def game_loop():
    while True:
        while not game_engine.game_state.game_over:
            if game_engine.game_state.current_player == Player.MAX:
                make_ai_move()
            else:
                make_ai_move()

            # Nach jedem Zug Sieger prüfen (eigentlich schon in place_stone)
            if game_engine.game_state.game_over:
                print(f"Spiel beendet. Gewinner: Spieler {game_engine.game_state.winner}")
                break
            time.sleep(0.2)

if __name__ == "__main__":
    root = tk.Tk()
    game_engine = game_engine()
    ui = ui(root, game_engine)
    ai = ai(game_engine)

    game_thread = threading.Thread(target=game_loop, daemon=True)
    game_thread.start()

    root.mainloop()
