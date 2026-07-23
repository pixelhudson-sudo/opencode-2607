import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')


class Leaderboard:
    def __init__(self):
        self.filepath = os.path.join(DATA_DIR, 'leaderboard.json')
        self.scores = self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath) as f:
                return json.load(f)
        return {}

    def _save(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(self.filepath, 'w') as f:
            json.dump(self.scores, f, indent=2)

    def add_score(self, game_id, player_name, score):
        if game_id not in self.scores:
            self.scores[game_id] = []
        self.scores[game_id].append({
            'player': player_name,
            'score': score,
            'date': datetime.now().strftime('%Y-%m-%d'),
        })
        self.scores[game_id].sort(key=lambda x: x['score'], reverse=True)
        self.scores[game_id] = self.scores[game_id][:50]
        self._save()

    def get_top(self, game_id, n=10):
        return self.scores.get(game_id, [])[:n]

    def get_all_game_ids(self):
        return list(self.scores.keys())
