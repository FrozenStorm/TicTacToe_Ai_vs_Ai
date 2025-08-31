import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import importlib
import os
from game_engine import game_engine
from game_state import Player
from ui import ui

def load_ai_module(module_name):
    # Dynamisch ein AI-Modul importieren
    module = importlib.import_module(module_name)
    return module.ai(game_engine)

def start_game():
    ai_max_name = player_max_ai_var.get()
    ai_min_name = player_min_ai_var.get()
    if not ai_max_name or not ai_min_name:
        messagebox.showerror("Fehler", "Bitte beide KIs auswählen.")
        return
    global ai_player
    ai_player = {Player.MAX: load_ai_module(ai_max_name),
                 Player.MIN: load_ai_module(ai_min_name)}

    selection_window.destroy()

    # UI und Fenster zeigen
    root.deiconify()
    global ui
    ui = ui(root, game_engine)

    def game_loop():
        while True:
            while not game_engine.game_state.game_over:
                best_move = ai_player[game_engine.game_state.current_player].calc_best_move(game_engine.game_state.current_player)

                if best_move is not None:
                    game_engine.make_move(best_move, game_engine.game_state.current_player)
                    print(f"Spieler {game_engine.game_state.current_player} setzt Stein bei {best_move}")
                    game_engine.end_turn()

                if game_engine.game_state.game_over:
                    print(f"Spiel beendet. Gewinner: Spieler {game_engine.game_state.winner}")
                    break
                time.sleep(0.2)

    game_thread = threading.Thread(target=game_loop, daemon=True)
    game_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hauptfenster zunächst verstecken

    game_engine = game_engine()
    ai_player_max = None
    ai_player_min = None

    # Alle ai_*.py Module im Verzeichnis auflisten (ohne .py)
    ai_files = [f[:-3] for f in os.listdir('.') if f.startswith('ai_') and f.endswith('.py')]

    selection_window = tk.Toplevel()
    selection_window.title("KI Auswahl")

    tk.Label(selection_window, text="KI für Spieler MAX:").grid(row=0, column=0, padx=10, pady=10)
    player_max_ai_var = tk.StringVar()
    player_max_ai_combo = ttk.Combobox(selection_window, values=ai_files, textvariable=player_max_ai_var, state="readonly")
    player_max_ai_combo.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(selection_window, text="KI für Spieler MIN:").grid(row=1, column=0, padx=10, pady=10)
    player_min_ai_var = tk.StringVar()
    player_min_ai_combo = ttk.Combobox(selection_window, values=ai_files, textvariable=player_min_ai_var, state="readonly")
    player_min_ai_combo.grid(row=1, column=1, padx=10, pady=10)

    start_button = tk.Button(selection_window, text="Spiel Starten", command=start_game)
    start_button.grid(row=2, column=0, columnspan=2, pady=20)

    root.mainloop()
