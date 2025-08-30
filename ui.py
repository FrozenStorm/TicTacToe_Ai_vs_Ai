from game_engine import game_engine
from game_state import Player
import tkinter as tk


class ui:
    def __init__(self, root, game_engine):
        self.game_engine = game_engine
        self.root = root
        self.root.title("TicTacToe mit Benutzer Eingabe")

        self.symbols = {Player.NONE: ' ', Player.MAX: 'X', Player.MIN: '-'}
        self.labels = []
        for i in range(game_engine.game_state.board_size):
            row_labels = []
            for j in range(game_engine.game_state.board_size):
                label = tk.Label(root, text=' ', font=('Arial', 32), width=3, height=1,
                                 borderwidth=1, relief='solid')
                label.grid(row=i, column=j)
                row_labels.append(label)
            self.labels.append(row_labels)

        self.status_label = tk.Label(root, text="Spiel läuft...", font=('Arial', 16))
        self.status_label.grid(row=game_engine.game_state.board_size, column=0, columnspan=game_engine.game_state.board_size)

        # Eingabefeld und Button für Benutzerzug
        self.entry = tk.Entry(root, width=10, font=('Arial', 16))
        self.entry.grid(row=game_engine.game_state.board_size+1, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        self.button = tk.Button(root, text="Stein setzen", command=self.handle_input)
        self.button.grid(row=game_engine.game_state.board_size+1, column=2, columnspan=1, sticky='e', padx=5, pady=5)
        self.button_reset = tk.Button(root, text="Reset Game", command=self.handle_reset)
        self.button_reset.grid(row=game_engine.game_state.board_size + 1, column=3, columnspan=1, sticky='e', padx=5, pady=5)

        self.update_gui()

    def handle_input(self):
        pos_str = self.entry.get()
        if self.game_engine.make_move(pos_str, Player.MIN):
            self.game_engine.end_turn()
            self.status_label.config(text="Stein gesetzt!")
        else:
            self.status_label.config(text="Ungültiger Zug! Bitte 'row,col' eingeben.")
        self.entry.delete(0, tk.END)

    def handle_reset(self):
        self.game_engine.reset_game()

    def update_gui(self):
        with self.game_engine.game_state.lock:
            size = self.game_engine.game_state.board_size
            for i in range(size):
                for j in range(size):
                    self.labels[i][j]['text'] = self.symbols.get(self.game_engine.game_state.board[i][j], ' ')
            if self.game_engine.game_state.game_over:
                if self.game_engine.game_state.winner != Player.TIE:
                    self.status_label['text'] = f"Spieler {self.game_engine.game_state.winner}!"
                else:
                    self.status_label['text'] = f"Unentschieden!"
            else:
                self.status_label['text'] = f"Spieler am Zug: {self.symbols.get(self.game_engine.game_state.current_player, ' ')}"
        self.root.after(200, self.update_gui)