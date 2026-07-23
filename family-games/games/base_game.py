class BaseGame:
    def __init__(self, players, engine, difficulty=None):
        self.players = players
        self.engine = engine
        self.difficulty = difficulty or {}
        self.finished = False
        self.results = []

    def handle_event(self, event):
        raise NotImplementedError

    def update(self, dt):
        raise NotImplementedError

    def render(self, screen):
        raise NotImplementedError

    def get_results(self):
        return self.results

    def finish(self):
        self.finished = True

    def cleanup(self):
        pass
