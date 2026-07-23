import pygame
import sys
import json
import os
from .menu import MenuRenderer
from .leaderboard import Leaderboard
from .badges import BadgeSystem
from .key_binding import load_bindings, save_bindings, DEFAULT_BINDINGS
from games.registry import GAMES

W, H = 1024, 768
FPS = 60
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')


class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Family Game Fun!")
        self.clock = pygame.time.Clock()

        self.fonts = {
            'large':  pygame.font.Font(None, 72),
            'medium': pygame.font.Font(None, 48),
            'small':  pygame.font.Font(None, 36),
            'tiny':   pygame.font.Font(None, 24),
        }

        self.state = 'MAIN_MENU'
        self.prev_state = None
        self.players = []
        self.current_game_id = None
        self.current_game = None
        self.game_results = []

        self.leaderboard = Leaderboard()
        self.badges = BadgeSystem()
        self.menu = MenuRenderer(self)
        self.running = True

        self.bindings = load_bindings()
        self.difficulty_config = self._load_difficulty()
        self.selected_category = 'All'

    def _load_difficulty(self):
        path = os.path.join(DATA_DIR, 'difficulty.json')
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return {}

    def _save_difficulty(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        path = os.path.join(DATA_DIR, 'difficulty.json')
        with open(path, 'w') as f:
            json.dump(self.difficulty_config, f, indent=2)

    def get_difficulty(self, game_id):
        if game_id not in self.difficulty_config:
            self.difficulty_config[game_id] = {}
        return self.difficulty_config[game_id]

    def set_difficulty(self, game_id, key, value):
        if game_id not in self.difficulty_config:
            self.difficulty_config[game_id] = {}
        self.difficulty_config[game_id][key] = value
        self._save_difficulty()

    def run(self):
        while self.running:
            self.clock.tick(FPS)

            if self.state == 'MAIN_MENU':
                self.menu.main_menu()
            elif self.state == 'SETTINGS':
                self.menu.settings()
            elif self.state == 'PLAYER_SELECT':
                self.menu.player_select()
            elif self.state == 'GAME_SELECT':
                self.menu.game_select()
            elif self.state == 'GAME_DETAIL':
                self.menu.game_detail()
            elif self.state == 'PLAYING':
                self._run_game_loop()
            elif self.state == 'GAME_OVER':
                self.menu.game_over()
            elif self.state == 'LEADERBOARD':
                self.menu.leaderboard()
            elif self.state == 'BADGES':
                self.menu.badges()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _run_game_loop(self):
        dt = self.clock.get_time() / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = 'GAME_DETAIL'
                    return
                self.current_game.handle_event(event)

        self.current_game.update(dt)
        self.current_game.render(self.screen)

        if self.current_game.finished:
            self._on_game_over()

    def _on_game_over(self):
        self.game_results = self.current_game.get_results()
        for result in self.game_results:
            pname = result['player'].name
            score = result['score']
            self.leaderboard.add_score(self.current_game_id, pname, score)
            self.badges.track_game_played(pname, self.current_game_id)
            self.badges.award(pname, 'first_game')
            if result.get('winner'):
                self.badges.award(pname, 'first_win')
            if self.current_game_id == 'snake' and score >= 5:
                self.badges.award(pname, 'snake_5')
            if self.current_game_id == 'snake' and score >= 15:
                self.badges.award(pname, 'snake_15')
            if self.badges.get_total_games_played(pname) >= 20:
                self.badges.award(pname, 'marathon')
            if self.badges.get_unique_games_played(pname) >= 5:
                self.badges.award(pname, 'all_rounder')
            wins = sum(1 for g in self.game_results if g.get('winner'))
            if wins >= 3:
                self.badges.award(pname, 'three_peat')
        self.state = 'GAME_OVER'

    def start_game(self, game_id, players):
        if game_id not in GAMES:
            return
        self.current_game_id = game_id
        self.players = players
        game_class = GAMES[game_id]['class']
        diff = self.get_difficulty(game_id)
        self.current_game = game_class(players, self, difficulty=diff)
        self.state = 'PLAYING'

    def go_back(self):
        if self.state == 'SETTINGS':
            self.state = 'MAIN_MENU'
        elif self.state == 'GAME_DETAIL':
            self.state = 'GAME_SELECT'
        elif self.state == 'GAME_OVER':
            self.state = 'MAIN_MENU'
        else:
            self.state = 'MAIN_MENU'
