import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

BADGE_DEFS = {
    'first_game':     {'name': 'First Steps',       'desc': 'Play your first game',           'emoji': '🎮', 'color': (107, 203, 119)},
    'first_win':      {'name': 'Champion',           'desc': 'Win your first game',            'emoji': '🏆', 'color': (255, 217, 61)},
    'snake_5':        {'name': 'Snake Rookie',       'desc': 'Score 5 or more in Snake',       'emoji': '🐍', 'color': (52, 168, 83)},
    'snake_15':       {'name': 'Snake Master',       'desc': 'Score 15 or more in Snake',      'emoji': '🐍', 'color': (66, 133, 244)},
    'three_peat':     {'name': 'Threepeat',          'desc': 'Win any game 3 times total',     'emoji': '⭐', 'color': (255, 107, 107)},
    'all_rounder':    {'name': 'All-Rounder',        'desc': 'Play 5 different games',         'emoji': '🌟', 'color': (147, 112, 219)},
    'perfect_score':  {'name': 'Perfect Score',      'desc': 'Get the maximum possible score', 'emoji': '💯', 'color': (255, 215, 0)},
    'speed_demon':    {'name': 'Speed Demon',        'desc': 'Win a game in record time',      'emoji': '⚡', 'color': (255, 255, 0)},
    'marathon':       {'name': 'Marathon',           'desc': 'Play 20 games total',            'emoji': '🏃', 'color': (255, 140, 0)},
    'family_fun':     {'name': 'Family Fun',         'desc': 'Play with 3 players',            'emoji': '👨‍👩‍👧', 'color': (255, 182, 193)},
}


class BadgeSystem:
    def __init__(self):
        self.filepath = os.path.join(DATA_DIR, 'badges.json')
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath) as f:
                return json.load(f)
        return {'players': {}, 'game_count': {}}

    def _save(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(self.filepath, 'w') as f:
            json.dump(self.data, f, indent=2)

    def award(self, player_name, badge_id):
        if player_name not in self.data['players']:
            self.data['players'][player_name] = []
        if badge_id not in self.data['players'][player_name]:
            self.data['players'][player_name].append(badge_id)
            self._save()
            return True
        return False

    def track_game_played(self, player_name, game_id):
        if player_name not in self.data['game_count']:
            self.data['game_count'][player_name] = {}
        self.data['game_count'][player_name][game_id] = \
            self.data['game_count'][player_name].get(game_id, 0) + 1
        self._save()

    def has_badge(self, player_name, badge_id):
        return badge_id in self.data['players'].get(player_name, [])

    def get_badges(self, player_name):
        return [BADGE_DEFS[b] for b in self.data['players'].get(player_name, []) if b in BADGE_DEFS]

    def get_all_badges(self, player_name):
        earned = set(self.data['players'].get(player_name, []))
        result = []
        for bid, bdef in BADGE_DEFS.items():
            result.append({**bdef, 'id': bid, 'earned': bid in earned})
        return result

    def get_total_games_played(self, player_name):
        counts = self.data['game_count'].get(player_name, {})
        return sum(counts.values())

    def get_unique_games_played(self, player_name):
        return len(self.data['game_count'].get(player_name, {}))
