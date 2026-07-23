import pygame
import random
import string
from games.base_game import BaseGame
from engine.key_binding import get_pressed_action

GRID_SIZES = {1: 2, 2: 3, 3: 4, 4: 4, 5: 5}

POOLS = {
    1: list('ABCDEFGH'),
    2: list('ABCDEFGHIJKL'),
    3: list('ABCDEFGHIJKLMNOP'),
    4: list(string.ascii_uppercase),
}


class LetterMatchGame(BaseGame):
    def __init__(self, players, engine, difficulty=None):
        super().__init__(players, engine, difficulty)
        self.font = engine.fonts['small']
        self.tiny = engine.fonts['tiny']
        self.med = engine.fonts['medium']

        grid_s = self.difficulty.get('Grid Size', 3)
        timer = self.difficulty.get('Timer', 3)
        pool = self.difficulty.get('Letter Pool', 2)

        self.G = GRID_SIZES.get(grid_s, 4)
        self.timer_per_round = 4 - timer * 0.5 + 3
        self.letter_pool = POOLS.get(pool, POOLS[2])
        self.CELL = min(70, 500 // self.G)
        self.BOARD_W = self.G * self.CELL
        self.BOARD_H = self.G * self.CELL
        self.OX = (1024 - self.BOARD_W) // 2
        self.OY = 200

        self.round_num = 0
        self.max_rounds = 8
        self.phase = 'playing'
        self.phase_timer = self.timer_per_round
        self.target_letter = ''
        self.grid_letters = []
        self.player_cursors = {}
        self.player_scores = {}
        self.round_winner = None
        self.answer_revealed = False

        for p in players:
            idx = random.randint(0, self.G * self.G - 1)
            self.player_cursors[p.index] = [idx // self.G, idx % self.G]
            self.player_scores[p.index] = 0
        self.setup_grid()

    def setup_grid(self):
        self.target_letter = random.choice(self.letter_pool)
        size = self.G * self.G
        letters = [self.target_letter]
        pool = [l for l in self.letter_pool if l != self.target_letter]
        letters += random.choices(pool, k=size - 1)
        random.shuffle(letters)
        self.grid_letters = [letters[i * self.G:(i + 1) * self.G]
                             for i in range(self.G)]
        self.phase_timer = self.timer_per_round
        self.round_winner = None
        self.answer_revealed = False
        self.round_num += 1

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN or self.finished:
            return
        if self.phase != 'playing' or self.round_winner:
            return

        for p in self.players:
            cursor = self.player_cursors[p.index]
            action = get_pressed_action(event, p.bindings)
            if action == 'up':
                cursor[1] = (cursor[1] - 1) % self.G
            elif action == 'down':
                cursor[1] = (cursor[1] + 1) % self.G
            elif action == 'left':
                cursor[0] = (cursor[0] - 1) % self.G
            elif action == 'right':
                cursor[0] = (cursor[0] + 1) % self.G
            elif action == 'btn1':
                lx, ly = cursor
                letter = self.grid_letters[ly][lx]
                if letter == self.target_letter:
                    self.round_winner = p
                    self.player_scores[p.index] += 10
                    self.phase = 'result'
                    self.phase_timer = 1.5
                else:

                    self.player_scores[p.index] = max(0,
                        self.player_scores[p.index] - 2)

    def update(self, dt):
        if self.finished:
            return
        self.phase_timer -= dt

        if self.phase == 'playing':
            if self.phase_timer <= 0:
                self.phase = 'result'
                self.phase_timer = 1.5
                self.answer_revealed = True

        if self.phase == 'result':
            if self.phase_timer <= 0:
                if self.round_num >= self.max_rounds:
                    self.finish_results()
                else:
                    self.phase = 'playing'
                    self.setup_grid()

    def finish_results(self):
        mx = max(self.player_scores.values())
        self.results = [
            {'player': p, 'score': self.player_scores[p.index],
             'winner': self.player_scores[p.index] == mx}
            for p in self.players
        ]
        self.finished = True

    def render(self, screen):
        screen.fill((20, 20, 50))

        t = self.med.render(f"🔤 LETTER MATCH  Round {self.round_num}/{self.max_rounds}",
                            True, (255, 217, 61))
        tr = t.get_rect(center=(512, 40))
        screen.blit(t, tr)

        target = self.font.render(f"Find:  {self.target_letter}", True,
                                  (255, 217, 61))
        tg = target.get_rect(center=(512, 85))
        screen.blit(target, tg)

        timer_w = 300
        timer_x = (1024 - timer_w) // 2
        timer_y = 115
        pygame.draw.rect(screen, (40, 40, 70), (timer_x, timer_y, timer_w, 10),
                         border_radius=5)
        fill = max(0, self.phase_timer / self.timer_per_round)
        if fill > 0:
            fc = (107, 203, 119) if fill > 0.3 else (255, 160, 60) if fill > 0.15 else (255, 80, 80)
            pygame.draw.rect(screen, fc,
                             (timer_x, timer_y, int(timer_w * fill), 10), border_radius=5)

        ox, oy = self.OX, self.OY
        c = self.CELL
        for gy in range(self.G):
            for gx in range(self.G):
                rx = ox + gx * c
                ry = oy + gy * c
                letter = self.grid_letters[gy][gx]

                pygame.draw.rect(screen, (35, 35, 68),
                                 (rx, ry, c - 2, c - 2), border_radius=6)

                # Highlight target on timeout
                if self.answer_revealed and letter == self.target_letter:
                    pygame.draw.rect(screen, (107, 203, 119),
                                     (rx, ry, c - 2, c - 2), border_radius=6)

                ls = self.font.render(letter, True, (200, 200, 200))
                lr = ls.get_rect(center=(rx + c // 2, ry + c // 2))
                screen.blit(ls, lr)

                # Draw cursors
                for pi, cur in self.player_cursors.items():
                    if cur[0] == gx and cur[1] == gy:
                        p = next(p for p in self.players if p.index == pi)
                        pygame.draw.rect(screen, p.color,
                                         (rx, ry, c - 2, c - 2), width=3, border_radius=6)

        # Score panel
        px = 15
        for p in self.players:
            py = 200 + p.index * 160
            pygame.draw.rect(screen, (30, 30, 65), (px - 5, py - 10, 120, 70),
                             border_radius=8)
            nm = self.tiny.render(p.name, True, p.color)
            screen.blit(nm, (px, py))
            sc = self.font.render(str(self.player_scores[p.index]), True, (255, 255, 255))
            screen.blit(sc, (px, py + 22))
            c_pos = self.player_cursors[p.index]
            pos_txt = self.tiny.render(f"({c_pos[0]+1},{c_pos[1]+1})", True, (100, 100, 140))
            screen.blit(pos_txt, (px, py + 46))

        if self.round_winner:
            wt = self.font.render(f"{self.round_winner.name} got it! +10",
                                  True, (107, 203, 119))
            wr = wt.get_rect(center=(512, 600))
            screen.blit(wt, wr)
        elif self.answer_revealed:
            wt = self.font.render(f"Time's up! Answer was {self.target_letter}",
                                  True, (255, 160, 60))
            wr = wt.get_rect(center=(512, 600))
            screen.blit(wt, wr)

        hlp = self.tiny.render("Move: Directional Keys  |  Select: B1",
                               True, (80, 80, 120))
        hr = hlp.get_rect(center=(512, 740))
        screen.blit(hlp, hr)
