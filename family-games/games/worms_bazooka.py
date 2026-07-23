import pygame
import random
import math
from games.base_game import BaseGame
from engine.key_binding import get_pressed_action

BLOCK = 8
MAP_W, MAP_H = 1024, 640
GW, GH = MAP_W // BLOCK, MAP_H // BLOCK

GRAVITY = 0.55
MOVE_SPEED = 2.5
JUMP_VEL = -11
DOUBLE_JUMP_VEL = -13
MAX_FALL = 18

PROJ_VX = 7
PROJ_VY = -10
PROJ_GRAV = 0.35
EXPLODE_R = 6
SHOOT_CD = 25
FALL_DMG_THRESH = 6
FALL_DMG_MULT = 2

PLAYER_W, PLAYER_H = 14, 20
COLORS = [(66, 133, 244), (234, 67, 53), (52, 168, 83)]


class WormsBazookaGame(BaseGame):
    def __init__(self, players, engine, difficulty=None):
        super().__init__(players, engine, difficulty)

        sz = self.difficulty.get('Map Size', 3)
        exp = self.difficulty.get('Explosion', 3)
        hp = self.difficulty.get('Health', 3)

        self.EXPLODE_R = 3 + exp
        self.start_hp = 2 + hp * 2
        self.terrain = self._generate(sz)
        self.players_data = []
        start_x = MAP_W // (len(players) + 1)
        for i, p in enumerate(players):
            sx = start_x * (i + 1) + random.randint(-30, 30)
            sy = self._ground_y(int(sx // BLOCK)) * BLOCK - PLAYER_H
            self.players_data.append({
                'player': p,
                'x': float(sx),
                'y': float(sy),
                'vx': 0.0,
                'vy': 0.0,
                'on_ground': True,
                'jumps': 0,
                'max_jumps': 2,
                'hp': self.start_hp,
                'max_hp': self.start_hp,
                'facing': 1,
                'shoot_cd': 0,
                'alive': True,
                'trail': [],
            })

        for pd in self.players_data:
            pd['y'] = self._ground_y(int(pd['x'] // BLOCK)) * BLOCK - PLAYER_H

        self.projectiles = []
        self.explosions = []
        self.frame = 0

    def _generate(self, size):
        t = [[1] * GW for _ in range(GH)]

        amp = 20 + size * 8
        freq = 0.03 + size * 0.005
        base = GH // 2 + 15

        for x in range(GW):
            h = int(base
                    + amp * math.sin(x * freq * 0.7 + 0.3)
                    + amp * 0.5 * math.sin(x * freq * 1.5 + 1.2)
                    + amp * 0.3 * math.sin(x * freq * 3.0 + 2.7)
                    + random.randint(-4, 4))
            h = max(8, min(GH - 4, h))
            for y in range(h, GH):
                t[y][x] = 1
            for y in range(h):
                t[y][x] = 0

        for _ in range(random.randint(2, 4)):
            cx = random.randint(10, GW - 10)
            cy = random.randint(int(base * 0.5), int(base * 0.85))
            r = random.randint(5, 10) + size
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if dx * dx + dy * dy < r * r:
                        bx, by = cx + dx, cy + dy
                        if 0 <= bx < GW and 0 <= by < GH:
                            t[by][bx] = 0

        for _ in range(random.randint(1, 3)):
            cx = random.randint(15, GW - 15)
            r = random.randint(8, 14) + size
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    d = math.sqrt(dx * dx + dy * dy)
                    if d < r and d > r * 0.5:
                        bx, by = cx + dx, int(base * 0.7) + dy
                        if 0 <= bx < GW and 0 <= by < GH:
                            t[by][bx] = 0

        for _ in range(random.randint(3, 6)):
            cx = random.randint(8, GW - 8)
            cy = random.randint(int(base * 0.4), int(base * 0.8))
            w, h = random.randint(3, 6), random.randint(2, 4)
            for dy in range(h):
                for dx in range(w):
                    bx, by = cx + dx, cy + dy
                    if 0 <= bx < GW and 0 <= by < GH and by < GH - 2:
                        t[by][bx] = 0

        return t

    def _ground_y(self, gx):
        for y in range(GH):
            if self.terrain[y][gx]:
                return y
        return GH - 1

    def _is_solid(self, px, py):
        gx, gy = int(px // BLOCK), int(py // BLOCK)
        if gx < 0 or gx >= GW or gy < 0 or gy >= GH:
            return gy >= GH
        return self.terrain[gy][gx]

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN or self.finished:
            return
        for pd in self.players_data:
            if not pd['alive']:
                continue
            action = get_pressed_action(event, pd['player'].bindings)
            if action == 'left':
                pd['vx'] = -MOVE_SPEED
                pd['facing'] = -1
            elif action == 'right':
                pd['vx'] = MOVE_SPEED
                pd['facing'] = 1
            elif action == 'up':
                if pd['on_ground']:
                    pd['vy'] = JUMP_VEL
                    pd['on_ground'] = False
                    pd['jumps'] = 1
                elif pd['jumps'] < pd['max_jumps']:
                    pd['vy'] = DOUBLE_JUMP_VEL
                    pd['jumps'] += 1
            elif action == 'btn1':
                if pd['shoot_cd'] <= 0:
                    self._fire(pd)

    def _fire(self, pd):
        cx = pd['x'] + PLAYER_W // 2 + pd['facing'] * 10
        cy = pd['y'] + PLAYER_H // 2 - 4
        self.projectiles.append({
            'x': cx, 'y': cy,
            'vx': PROJ_VX * pd['facing'],
            'vy': PROJ_VY,
            'owner': pd,
        })
        pd['shoot_cd'] = SHOOT_CD
        pd['trail'] = []

    def update(self, dt):
        self.frame += 1
        if self.finished:
            return

        for pd in self.players_data:
            if not pd['alive']:
                continue
            self._physics(pd)
            if pd['shoot_cd'] > 0:
                pd['shoot_cd'] -= 1

        for proj in self.projectiles[:]:
            proj['x'] += proj['vx']
            proj['y'] += proj['vy']
            proj['vy'] += PROJ_GRAV
            gx, gy = int(proj['x'] // BLOCK), int(proj['y'] // BLOCK)
            if gx < 0 or gx >= GW or gy < 0:
                self.projectiles.remove(proj)
                continue
            if gy >= GH or (gy >= 0 and self.terrain[gy][gx]):
                self._explode(proj['x'], proj['y'], proj['owner'])
                self.projectiles.remove(proj)
                continue

        for exp in self.explosions[:]:
            exp['timer'] -= 1
            if exp['timer'] <= 0:
                self.explosions.remove(exp)

        alive = [pd for pd in self.players_data if pd['alive']]
        if len(alive) <= 1 and len(self.players) > 1:
            self.game_over()

    def _physics(self, pd):
        pd['vy'] = min(MAX_FALL, pd['vy'] + GRAVITY)

        new_x = pd['x'] + pd['vx']
        if not self._collides(new_x, pd['y'], PLAYER_W, PLAYER_H):
            pd['x'] = new_x
        else:
            pd['vx'] = 0

        new_y = pd['y'] + pd['vy']
        if not self._collides(pd['x'], new_y, PLAYER_W, PLAYER_H):
            pd['y'] = new_y
            if pd['vy'] > FALL_DMG_THRESH:
                dmg = int((pd['vy'] - FALL_DMG_THRESH) * FALL_DMG_MULT)
                pd['hp'] -= dmg
                pd['trail'].append(('dmg', dmg))
            pd['on_ground'] = False
        else:
            if pd['vy'] > 0:
                pd['on_ground'] = True
                pd['jumps'] = 0
            pd['vy'] = 0
            snap_y = int(pd['y'] // BLOCK) * BLOCK
            pd['y'] = snap_y

        if pd['hp'] <= 0:
            pd['alive'] = False
            self.explosions.append({'x': pd['x'] + PLAYER_W // 2,
                                    'y': pd['y'] + PLAYER_H // 2,
                                    'r': 20, 'timer': 15})

        pd['vx'] *= 0.7
        if abs(pd['vx']) < 0.1:
            pd['vx'] = 0

    def _collides(self, x, y, w, h):
        steps = 4
        for iy in range(steps):
            for ix in range(steps):
                px = x + w * ix // (steps - 1) if steps > 1 else x
                py = y + h * iy // (steps - 1) if steps > 1 else y
                if self._is_solid(px, py):
                    return True
        return False

    def _explode(self, x, y, owner):
        r = self.EXPLODE_R * BLOCK
        self.explosions.append({'x': x, 'y': y, 'r': r, 'timer': 12})

        for dy in range(-r, r + 1, BLOCK // 2):
            for dx in range(-r, r + 1, BLOCK // 2):
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < r:
                    bx, by = int((x + dx) // BLOCK), int((y + dy) // BLOCK)
                    if 0 <= bx < GW and 0 <= by < GH:
                        self.terrain[by][bx] = 0

        for pd in self.players_data:
            if not pd['alive']:
                continue
            cx = pd['x'] + PLAYER_W // 2
            cy = pd['y'] + PLAYER_H // 2
            dist = math.sqrt((cx - x) ** 2 + (cy - y) ** 2)
            if dist < r:
                dmg = int((1 - dist / r) * 35)
                dmg = max(5, min(50, dmg))
                pd['hp'] -= dmg
                pd['trail'].append('boom')
                push = 8 * (1 - dist / r)
                pd['vx'] += push * (cx - x) / max(dist, 1)
                pd['vy'] += -push * 0.5
                if pd['hp'] <= 0:
                    pd['alive'] = False
                    self.explosions.append({'x': cx, 'y': cy, 'r': 20, 'timer': 15})

    def game_over(self):
        mx = max((pd['hp'] for pd in self.players_data if pd['alive']), default=0)
        self.results = []
        for pd in self.players_data:
            score = max(0, pd['hp'])
            self.results.append({
                'player': pd['player'],
                'score': score,
                'winner': pd['alive'] and pd['hp'] == mx,
            })
        self.finished = True

    def render(self, screen):
        screen.fill((25, 30, 55))
        s = screen

        for y in range(GH):
            for x in range(GW):
                if self.terrain[y][x]:
                    shade = 60 + (y * 20 // GH)
                    s.set_at((x * BLOCK, y * BLOCK), (shade, shade - 10, shade - 20))
                    s.set_at((x * BLOCK + 1, y * BLOCK), (shade, shade - 10, shade - 20))
                    s.set_at((x * BLOCK, y * BLOCK + 1), (shade, shade - 10, shade - 20))
                    s.set_at((x * BLOCK + 1, y * BLOCK + 1), (shade + 10, shade, shade - 10))

        for pd in self.players_data:
            if not pd['alive']:
                continue
            px, py = int(pd['x']), int(pd['y'])
            col = pd['player'].color
            pygame.draw.ellipse(s, col, (px, py, PLAYER_W, PLAYER_H))
            pygame.draw.ellipse(s, (min(255, col[0] + 60),
                                    min(255, col[1] + 60),
                                    min(255, col[2] + 60)),
                                (px + 2, py + 2, PLAYER_W - 4, PLAYER_H - 4), 1)
            eyex = px + (4 if pd['facing'] > 0 else PLAYER_W - 8)
            s.set_at((eyex, py + 4), (255, 255, 255))
            s.set_at((eyex + 1, py + 4), (255, 255, 255))
            s.set_at((eyex, py + 5), (255, 255, 255))
            s.set_at((eyex + 1, py + 5), (255, 255, 255))

            hp_bar_w = PLAYER_W + 6
            hp_pct = pd['hp'] / pd['max_hp']
            pygame.draw.rect(s, (80, 30, 30), (px - 3, py - 8, hp_bar_w, 4))
            if hp_pct > 0:
                hpc = (int(255 * (1 - hp_pct)), int(200 * hp_pct), 30)
                pygame.draw.rect(s, hpc, (px - 3, py - 8, int(hp_bar_w * hp_pct), 4))

        for proj in self.projectiles:
            px, py = int(proj['x']), int(proj['y'])
            pygame.draw.circle(s, (255, 200, 50), (px, py), 3)
            pygame.draw.circle(s, (255, 255, 200), (px, py), 1)
            tail = 6
            for ti in range(tail):
                a = 1.0 - ti / tail
                tx = int(px - proj['vx'] * ti * 0.3)
                ty = int(py - proj['vy'] * ti * 0.3)
                alpha = int(255 * a)
                sz = max(1, int(3 * a))
                c = (255, 200 - ti * 20, 50)
                pygame.draw.circle(s, c, (tx, ty), sz)

        for exp in self.explosions:
            intensity = exp['timer'] / 15
            r = int(exp['r'] * intensity)
            if r > 0:
                pygame.draw.circle(s, (255, 200, 50, 128), (int(exp['x']), int(exp['y'])), r)
                pygame.draw.circle(s, (255, 255, 200, 64), (int(exp['x']), int(exp['y'])), r // 2)

        for pd in self.players_data:
            for trail in pd['trail'][-3:]:
                if trail == 'boom':
                    pass
            pd['trail'] = []

        pygame.draw.rect(s, (15, 15, 40), (0, MAP_H, 1024, 128))
        for i, pd in enumerate(self.players_data):
            by = MAP_H + 10 + i * 35
            col = pd['player'].color
            nm = self.engine.fonts['tiny'].render(
                f"{pd['player'].name}: {'❤️' * max(0, pd['hp'])}"
                f"{'🖤' * max(0, pd['max_hp'] - max(0, pd['hp']))}",
                True, col if pd['alive'] else (80, 80, 80))
            screen.blit(nm, (20 + i * 340, by))

        t = self.engine.fonts['tiny'].render(
            "← → Move  |  ↑ Jump (double=backflip)  |  B1 Shoot bazooka",
            True, (100, 100, 140))
        screen.blit(t, (20, MAP_H + 110))
