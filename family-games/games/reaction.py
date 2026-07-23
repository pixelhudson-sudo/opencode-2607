import pygame
import random
import math
from games.base_game import BaseGame
from engine.key_binding import get_pressed_action

BAR_W = 300
BAR_H = 20
ZONE_H = 14


class ReactionGame(BaseGame):
    def __init__(self, players, engine, difficulty=None):
        super().__init__(players, engine, difficulty)
        self.font = engine.fonts['small']
        self.tiny = engine.fonts['tiny']
        self.med = engine.fonts['medium']

        speed = self.difficulty.get('Speed', 3)
        rounds = self.difficulty.get('Rounds', 3)
        tolerance = self.difficulty.get('Tolerance', 3)

        self.fill_rate = 40 + speed * 20
        self.max_rounds = 2 + rounds
        self.zone_width = int(ZONE_H * (0.5 + tolerance * 0.3))
        self.round_num = 0
        self.phase = 'countdown'
        self.phase_timer = 0

        self.player_states = {}
        for p in players:
            self.player_states[p.index] = {
                'fill': 0, 'locked': False, 'reacted': False,
                'score': 0, 'round_score': 0, 'perfect': False,
            }
        self.setup_round()

    def setup_round(self):
        self.round_num += 1
        if self.round_num > self.max_rounds:
            self.finish_results()
            return
        self.phase = 'countdown'
        self.phase_timer = 1.0 + random.random()
        for ps in self.player_states.values():
            ps['fill'] = 0
            ps['locked'] = False
            ps['reacted'] = False
            ps['round_score'] = 0
            ps['perfect'] = False

        zone_center = random.uniform(0.25, 0.75)
        self.zone_start = int(BAR_W * (zone_center - self.zone_width / BAR_W / 2))
        self.zone_end = int(BAR_W * (zone_center + self.zone_width / BAR_W / 2))
        self.zone_center_px = int(BAR_W * zone_center)

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN or self.finished:
            return
        if self.phase != 'reaction':
            return
        for p in self.players:
            ps = self.player_states[p.index]
            if ps['reacted'] or ps['locked']:
                continue
            action = get_pressed_action(event, p.bindings)
            if action == 'btn1':
                ps['reacted'] = True
                dist = abs(ps['fill'] - self.zone_center_px)
                if dist <= self.zone_width // 2:
                    accuracy = 1.0 - (dist / (self.zone_width // 2))
                    ps['round_score'] = int(10 * accuracy)
                    if accuracy > 0.95:
                        ps['round_score'] = 10
                        ps['perfect'] = True
                else:
                    ps['round_score'] = 0

    def update(self, dt):
        if self.finished:
            return
        self.phase_timer -= dt

        if self.phase == 'countdown' and self.phase_timer <= 0:
            self.phase = 'reaction'
            self.phase_timer = 3.0

        if self.phase == 'reaction':
            for p in self.players:
                ps = self.player_states[p.index]
                if not ps['reacted']:
                    ps['fill'] = min(BAR_W, ps['fill'] + self.fill_rate * dt)

            if all(ps['reacted'] for ps in self.player_states.values()):
                self.phase = 'results'
                self.phase_timer = 1.5

            if self.phase_timer <= 0:
                for p in self.players:
                    ps = self.player_states[p.index]
                    if not ps['reacted']:
                        ps['reacted'] = True
                        ps['round_score'] = 0
                self.phase = 'results'
                self.phase_timer = 1.5

        if self.phase == 'results':
            for ps in self.player_states.values():
                if ps['round_score'] > 0:
                    ps['score'] += ps['round_score']
                    if ps['perfect']:
                        ps['score'] += 3
            self.phase_timer -= dt
            if self.phase_timer <= 0:
                self.setup_round()

    def finish_results(self):
        mx = max(ps['score'] for ps in self.player_states.values())
        self.results = []
        for p in self.players:
            ps = self.player_states[p.index]
            self.results.append({
                'player': p, 'score': ps['score'],
                'winner': ps['score'] == mx,
            })
        self.finished = True

    def render(self, screen):
        screen.fill((20, 20, 50))
        ox, oy = 1024 // 2, 200

        if self.phase == 'countdown':
            t = self.med.render(f"Round {self.round_num}/{self.max_rounds}", True, (255, 217, 61))
            tr = t.get_rect(center=(ox, oy))
            screen.blit(t, tr)
            secs = max(1, int(self.phase_timer) + 1)
            t2 = self.font.render(f"GET READY... {secs}", True, (200, 200, 200))
            t2r = t2.get_rect(center=(ox, oy + 50))
            screen.blit(t2, t2r)
        else:
            t = self.med.render(f"Round {self.round_num}/{self.max_rounds}", True, (255, 217, 61))
            tr = t.get_rect(center=(ox, oy - 60))
            screen.blit(t, tr)

            # Zone indicator
            zx = ox - BAR_W // 2 + self.zone_start
            zy = oy + 15
            pygame.draw.rect(screen, (60, 200, 60, 80),
                             (zx, zy - 2, self.zone_end - self.zone_start, BAR_H + 4),
                             border_radius=3)

            # Bars per player
            for i, p in enumerate(self.players):
                ps = self.player_states[p.index]
                by = oy + 60 + i * 70
                pbar_x = ox - BAR_W // 2

                pygame.draw.rect(screen, (40, 40, 70),
                                 (pbar_x, by, BAR_W, BAR_H), border_radius=10)
                fill_w = max(2, int(ps['fill']))
                if fill_w > 0:
                    col = p.color if not ps['reacted'] else \
                          (107, 203, 119) if ps['round_score'] > 0 else (200, 80, 80)
                    pygame.draw.rect(screen, col,
                                     (pbar_x, by, fill_w, BAR_H), border_radius=10)

                pygame.draw.rect(screen, p.color,
                                 (pbar_x - 80, by + 2, 70, 16), border_radius=3)
                nm = self.tiny.render(p.name, True, (255, 255, 255))
                screen.blit(nm, (pbar_x - 76, by + 2))
                sc = self.tiny.render(f"{ps['score']} pts", True, (200, 200, 200))
                screen.blit(sc, (pbar_x - 76, by + BAR_H + 2))

                if ps['reacted']:
                    result = f"+{ps['round_score']}" if ps['round_score'] > 0 else "Miss!"
                    if ps['perfect']:
                        result = "PERFECT! +13"
                    rc = (107, 203, 119) if ps['round_score'] > 0 else (200, 80, 80)
                    rs = self.font.render(result, True, rc)
                    rr = rs.get_rect(midleft=(pbar_x + BAR_W + 10, by + BAR_H // 2))
                    screen.blit(rs, rr)

            # Zone markers
            zc = ox - BAR_W // 2 + self.zone_center_px
            pygame.draw.line(screen, (255, 217, 61),
                             (zc, oy + 10), (zc, oy + BAR_H + 50 + len(self.players) * 70), 1)

        ttl = self.font.render("⚡ REACTION TAP", True, (255, 217, 61))
        tr2 = ttl.get_rect(center=(ox, 50))
        screen.blit(ttl, tr2)
        hlp = self.tiny.render("Press B1 when bar reaches green zone!", True, (100, 100, 140))
        hr = hlp.get_rect(center=(ox, 720))
        screen.blit(hlp, hr)

        if self.phase == 'results' and self.finished:
            screen.fill((0, 0, 0, 160), special_flags=pygame.BLEND_RGBA_MULT)
