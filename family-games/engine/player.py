from .key_binding import DEFAULT_BINDINGS, load_bindings

PLAYER_COLORS = [
    (66, 133, 244),
    (234, 67, 53),
    (52, 168, 83),
]

PLAYER_NAMES = [
    "Player 1",
    "Player 2",
    "Player 3",
]


class Player:
    def __init__(self, index, name=None, bindings=None):
        self.index = index
        self.name = name or f"Player {index + 1}"
        self.color = PLAYER_COLORS[index]
        self.score = 0
        if bindings:
            self.bindings = bindings
        else:
            all_bindings = load_bindings()
            self.bindings = all_bindings[index]

    def reset_score(self):
        self.score = 0
