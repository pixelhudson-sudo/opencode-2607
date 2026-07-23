import pygame
import random
from games.base_game import BaseGame
from engine.key_binding import get_pressed_action

DIR_MAP = {
    'up': (0, -1), 'down': (0, 1),
    'left': (-1, 0), 'right': (1, 0),
}
OPPOSITE = {(0, -1): (0, 1), (0, 1): (0, -1), (-1, 0): (1, 0), (1, 0): (-1, 0)}

SNAKE_COLORS = [(66, 133, 244), (234, 67, 53), (52, 168, 83)]
SNAKE_HEADS = [(30, 100, 230), (210, 50, 30), (30, 140, 60)]

DIFFICULTY_PRESETS = {
    1: {'grid': (15, 11), 'interval': 0.22, 'food_count': 1},
    2: {'grid': (18, 13), 'interval': 0.18, 'food_count': 1},
    3: {'grid': (20, 15), 'interval': 0.15, 'food_count': 1},
    4: {'grid': (22, 17), 'interval': 0.12, 'food_count': 2},
    5: {'grid': (25, 19), 'interval': 0.09, 'food_count': 2},
}


class SnakeGame(BaseGame):
    def __init__(self, players, engine, difficulty=None):
        super().__init__(players, engine, difficulty)
        self.font = engine.fonts['small']
        self.tiny = engine.fonts['tiny']

        bs = self.difficulty.get('Board Size', 3)
        sp = self.difficulty.get('Speed', 3)
        ff = self.difficulty.get('Food Frequency', 1)

        preset = DIFFICULTY_PRESETS.get(bs, DIFFICULTY_PRESETS[3])
        self.GRID_W, self.GRID_H = preset['grid']
        speed_factor = {1: 0.75, 2: 0.85, 3: 1.0, 4: 1.2, 5: 1.4}.get(sp, 1.0)
        self.move_interval = preset['interval'] / speed_factor
        self.food_count = preset['food_count'] + (ff - 1)

        self.CELL = max(20, min(36, 640 // self.GRID_W))
        self.BOARD_W = self.GRID_W * self.CELL
        self.BOARD_H = self.GRID_H * self.CELL
        self.GRID_OFFSET_X = (1024 - self.BOARD_W) // 2 + 60
        self.GRID_OFFSET_Y = (768 - self.BOARD_H) // 2

        self.move_timer = 0
        self.setup()

    def setup(self):
        spacing_x = self.GRID_W // (len(self.players) + 1)
        spacing_y = self.GRID_H // (len(self.players) + 1)
        dirs = [(1, 0), (-1, 0), (0, 1)]

        self.snakes = []
        for i, player in enumerate(self.players):
            sx = spacing_x * (i + 1)
            sy = spacing_y * (i + 1)
            sx = max(3, min(sx, self.GRID_W - 3))
            sy = max(3, min(sy, self.GRID_H - 3))
            dx, dy = dirs[i]
            segs = [(sx - dx * j, sy - dy * j) for j in range(3)]
            self.snakes.append({
                'player': player,
                'segments': segs,
                'direction': (dx, dy),
                'next_dir': (dx, dy),
                'color': SNAKE_COLORS[i],
                'head_color': SNAKE_HEADS[i],
                'alive': True,
                'score': 0,
                'grow': 0,
            })
        self.foods = []
        for _ in range(self.food_count):
            self.spawn_food()

    def spawn_food(self):
        occ = set()
        for s in self.snakes:
            for seg in s['segments']:
                occ.add(seg)
        for f in self.foods:
            occ.add(f)
        avail = [(x, y) for x in range(self.GRID_W) for y in range(self.GRID_H)
                 if (x, y) not in occ]
        if avail:
            self.foods.append(random.choice(avail))

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        for i, s in enumerate(self.snakes):
            if not s['alive']:
                continue
            action = get_pressed_action(event, s['player'].bindings)
            if action in DIR_MAP:
                nd = DIR_MAP[action]
                if nd != OPPOSITE.get(s['direction']):
                    s['next_dir'] = nd

    def update(self, dt):
        if self.finished:
            return
        self.move_timer += dt
        if self.move_timer < self.move_interval:
            return
        self.move_timer = 0

        alive = [s for s in self.snakes if s['alive']]
        if not alive:
            return self.finish_results()
        if len(alive) == 1 and len(self.players) > 1:
            alive[0]['score'] += 5
            return self.finish_results()

        new_segs = {}
        for s in self.snakes:
            if not s['alive']:
                continue
            s['direction'] = s['next_dir']
            dx, dy = s['direction']
            hx, hy = s['segments'][0]
            nh = (hx + dx, hy + dy)

            if nh[0] < 0 or nh[0] >= self.GRID_W or nh[1] < 0 or nh[1] >= self.GRID_H:
                s['alive'] = False
                continue

            if nh in self.foods:
                s['grow'] += 3
                s['score'] += 1
                self.foods.remove(nh)
                self.spawn_food()

            segs = [nh] + s['segments']
            if s['grow'] > 0:
                s['grow'] -= 1
            else:
                segs.pop()
            new_segs[id(s)] = segs

        for s in self.snakes:
            if not s['alive']:
                continue
            ns = new_segs.get(id(s), s['segments'])
            if ns[0] in ns[1:]:
                s['alive'] = False
                continue
            for other in self.snakes:
                if other is s or not other['alive']:
                    continue
                if ns[0] in new_segs.get(id(other), other['segments']):
                    s['alive'] = False
                    break

        for s in self.snakes:
            if id(s) in new_segs:
                s['segments'] = new_segs[id(s)]

    def finish_results(self):
        mx = max(s['score'] for s in self.snakes)
        winners = [s for s in self.snakes if s['score'] == mx]
        self.results = [
            {'player': s['player'], 'score': s['score'], 'winner': s in winners}
            for s in self.snakes
        ]
        self.finished = True

    def render(self, screen):
        screen.fill((20, 20, 50))
        ox, oy = self.GRID_OFFSET_X, self.GRID_OFFSET_Y
        c = self.CELL
        gw, gh = self.GRID_W, self.GRID_H

        pygame.draw.rect(screen, (30, 30, 60), (ox - 4, oy - 4, self.BOARD_W + 8, self.BOARD_H + 8),
                         border_radius=8)
        pygame.draw.rect(screen, (40, 40, 70), (ox, oy, self.BOARD_W, self.BOARD_H))

        for x in range(gw + 1):
            pygame.draw.line(screen, (36, 36, 66), (ox + x * c, oy), (ox + x * c, oy + self.BOARD_H))
        for y in range(gh + 1):
            pygame.draw.line(screen, (36, 36, 66), (ox, oy + y * c), (ox + self.BOARD_W, oy + y * c))

        for food in self.foods:
            fx = ox + food[0] * c + c // 2
            fy = oy + food[1] * c + c // 2
            pygame.draw.circle(screen, (255, 217, 61), (fx, fy), c // 2 - 2)
            pygame.draw.circle(screen, (255, 200, 50), (fx - 3, fy - 3), c // 5)

        for s in self.snakes:
            if not s['alive']:
                continue
            for j, seg in enumerate(s['segments']):
                sx = ox + seg[0] * c
                sy = oy + seg[1] * c
                if j == 0:
                    col = s['head_color']
                    pygame.draw.rect(screen, col, (sx + 1, sy + 1, c - 2, c - 2), border_radius=5)
                    dx, dy = s['direction']
                    cx2, cy2 = sx + c // 2, sy + c // 2
                    off = 5
                    pygame.draw.circle(screen, (255, 255, 255),
                                       (cx2 + dx * off - 4 + dy * 3, cy2 + dy * off - 4 + dx * 3), 3)
                    pygame.draw.circle(screen, (255, 255, 255),
                                       (cx2 + dx * off + 4 - dy * 3, cy2 + dy * off + 4 - dx * 3), 3)
                else:
                    bright = max(0.6, 1.0 - j * 0.015)
                    col = tuple(int(v * bright) for v in s['color'])
                    pygame.draw.rect(screen, col, (sx + 2, sy + 2, c - 4, c - 4), border_radius=3)

        px = 8
        for i, s in enumerate(self.snakes):
            yb = 50 + i * 80
            p = s['player']
            nm = self.font.render(p.name, True, p.color)
            screen.blit(nm, (px, yb))
            sc = self.tiny.render(f"{s['score']}", True, (200, 200, 200))
            screen.blit(sc, (px, yb + 26))
            st = "●" if s['alive'] else "✕"
            sc2 = self.tiny.render(st, True, (107, 203, 119) if s['alive'] else (150, 100, 100))
            screen.blit(sc2, (px + 40, yb + 26))
            pygame.draw.rect(screen, p.color, (px, yb - 6, 8, 8), border_radius=2)

        ttl = self.font.render("🐍 SNAKE", True, (255, 217, 61))
        tr = ttl.get_rect(midtop=(ox + self.BOARD_W // 2, oy - 34))
        screen.blit(ttl, tr)
