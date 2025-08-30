import tkinter as tk
import threading
import time
from game_engine import game_engine
from game_state import Player
from ui import ui
from ai import ai

def make_ai_move():
    score, best_move = ai.minimax(depth=9, maximizing_player=game_engine.game_state.current_player)
    if best_move is not None:
        game_engine.make_move(best_move, game_engine.game_state.current_player)
    game_engine.end_turn()
    print(f"KI (Spieler {game_engine.game_state.current_player}) setzt Stein bei {best_move}")

def game_loop():
    while not game_engine.game_state.game_over:
        if game_engine.game_state.current_player == Player.MAX:
            # KI macht Zug
            make_ai_move()
        else:
            make_ai_move()
            # Für Spieler 2 wartet die Schleife auf menschliche Eingabe über GUI oder Eingabefeld
            # Hier einfach kurze Pause, die wirkliche Eingabe geschieht außerhalb dieser Schleife
            print("Spieler 2 am Zug, bitte Eingabe über GUI machen...")
            while game_engine.game_state.current_player == Player.MIN and not game_engine.game_state.game_over:
                time.sleep(0.5)  # Warte auf Benutzerzug

        # Nach jedem Zug Sieger prüfen (eigentlich schon in place_stone)
        if game_engine.game_state.game_over:
            print(f"Spiel beendet. Gewinner: Spieler {game_engine.game_state.winner}")
            break

if __name__ == "__main__":
    root = tk.Tk()
    game_engine = game_engine()
    ui = ui(root, game_engine)
    ai = ai(game_engine)

    game_thread = threading.Thread(target=game_loop, daemon=True)
    game_thread.start()

    root.mainloop()
