import pygame
from games.base_game import BaseGame
from engine.key_binding import get_pressed_action

ACTIONS_LIST = ['Reload', 'Protect', 'Shoot']
ACTION_EMOJI = {'Reload': '🔃', 'Protect': '🛡️', 'Shoot': '🔫'}


class GunDuelGame(BaseGame):
    def __init__(self, players, engine, difficulty=None):
        super().__init__(players, engine, difficulty)
        self.font = engine.fonts['small']
        self.tiny = engine.fonts['tiny']
        self.med = engine.fonts['medium']

        h = self.difficulty.get('Health', 3)
        self.start_health = max(1, h)
        self.round_num = 0
        self.phase = 'playing'
        self.phase_timer = 0

        self.bullets = {p.index: 0 for p in players}
        self.health = {p.index: self.start_health for p in players}
        self.shielded = {p.index: False for p in players}
        self.chosen_action = {p.index: None for p in players}
        self.confirmed = set()
        self.selections = {p.index: 0 for p in players}
        self.log = []
        self.round_num = 0

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN or self.finished:
            return
        if self.phase != 'playing':
            return

        for p in self.players:
            if p.index in self.confirmed:
                continue
            action = get_pressed_action(event, p.bindings)
            if action == 'up':
                self.selections[p.index] = (self.selections[p.index] - 1) % 3
            elif action == 'down':
                self.selections[p.index] = (self.selections[p.index] + 1) % 3
            elif action == 'btn1':
                sel = self.selections[p.index]
                self.chosen_action[p.index] = ACTIONS_LIST[sel]
                self.confirmed.add(p.index)

    def update(self, dt):
        if self.finished:
            return

        if self.phase == 'playing' and len(self.confirmed) == len(self.players):
            self.resolve_round()
            return

    def resolve_round(self):
        self.round_num += 1
        self.shielded = {p.index: False for p in self.players}

        # Reset shields and apply reloads first
        for p in self.players:
            action = self.chosen_action[p.index]
            if action == 'Reload':
                self.bullets[p.index] = 1
            elif action == 'Protect':
                self.shielded[p.index] = True

        # Then resolve shots
        shooters_targets = []
        for p in self.players:
            action = self.chosen_action[p.index]
            if action == 'Shoot':
                if self.bullets[p.index] > 0:
                    self.bullets[p.index] = 0
                    targets = [op for op in self.players if op.index != p.index]
                    for t in targets:
                        shooters_targets.append((p, t))

        for shooter, target in shooters_targets:
            if self.health[target.index] <= 0:
                continue
            if self.shielded[target.index]:
                self.log.append(f"{shooter.name} shot {target.name} but shield blocked!")
            else:
                self.health[target.index] -= 1
                self.log.append(f"{shooter.name} hit {target.name}!")
                if self.health[target.index] <= 0:
                    self.log.append(f"{target.name} is eliminated!")

        self.confirmed = set()
        self.chosen_action = {p.index: None for p in self.players}

        alive = [p for p in self.players if self.health[p.index] > 0]
        if len(alive) <= 1:
            self.finish_results()
            return

        self.phase = 'playing'

    def finish_results(self):
        mx = max(self.health.values())
        self.results = [
            {'player': p, 'score': self.health[p.index],
             'winner': self.health[p.index] == mx and self.health[p.index] > 0}
            for p in self.players
        ]
        self.finished = True

    def render(self, screen):
        screen.fill((20, 20, 50))
        s, f = self.engine.screen, self.engine.fonts

        t = self.med.render("🔫 GUN DUEL  —  Choose your action!", True, (255, 217, 61))
        tr = t.get_rect(center=(512, 35))
        screen.blit(t, tr)

        round_text = self.tiny.render(f"Round {self.round_num}", True, (200, 200, 200))
        rt = round_text.get_rect(center=(512, 65))
        screen.blit(round_text, rt)

        for i, p in enumerate(self.players):
            bx = 60 + i * 310
            by = 100
            pw = 280
            ph = 320
            pygame.draw.rect(s, (30, 30, 65), (bx, by, pw, ph), border_radius=12)

            nm = self.font.render(p.name, True, p.color)
            screen.blit(nm, (bx + 10, by + 10))

            hearts = "❤️" * self.health[p.index] + "🖤" * (self.start_health - self.health[p.index])
            ht = self.tiny.render(hearts, True, (200, 200, 200))
            screen.blit(ht, (bx + 10, by + 40))

            bt = self.tiny.render(f"Bullets: {'●' * self.bullets[p.index] + '○' * (1 - self.bullets[p.index])}",
                                  True, (255, 217, 61))
            screen.blit(bt, (bx + 10, by + 60))

            if p.index in self.confirmed:
                act = self.chosen_action[p.index]
                c = {'Reload': (100, 100, 200), 'Protect': (100, 200, 100), 'Shoot': (200, 100, 100)}
                pygame.draw.rect(s, c[act], (bx + 10, by + 85, pw - 20, 50), border_radius=8)
                em = self.tiny.render(f"{ACTION_EMOJI[act]} {act}", True, (255, 255, 255))
                er = em.get_rect(center=(bx + pw // 2, by + 110))
                screen.blit(em, er)
            else:
                for ai, action in enumerate(ACTIONS_LIST):
                    ay = by + 90 + ai * 60
                    ar = pygame.Rect(bx + 10, ay, pw - 20, 50)
                    sel = ai == self.selections[p.index]
                    if sel:
                        pygame.draw.rect(s, (60, 60, 120), ar, border_radius=8)
                        pygame.draw.rect(s, p.color, ar, width=2, border_radius=8)
                    else:
                        pygame.draw.rect(s, (40, 40, 75), ar, border_radius=8)
                    em = self.tiny.render(ACTION_EMOJI[action], True, (200, 200, 200))
                    screen.blit(em, (bx + 20, ay + 10))
                    an = self.tiny.render(action, True, (200, 200, 200))
                    screen.blit(an, (bx + 55, ay + 15))

        # Log panel
        log_y = 460
        pygame.draw.rect(s, (25, 25, 55), (30, log_y, 964, 200), border_radius=8)
        lt = self.tiny.render("Combat Log", True, (255, 217, 61))
        screen.blit(lt, (40, log_y + 8))
        for li, log_entry in enumerate(self.log[-6:]):
            lc = (200, 200, 200)
            ls = self.tiny.render(log_entry, True, lc)
            screen.blit(ls, (50, log_y + 32 + li * 22))

        hlp = self.tiny.render("↑↓ Select  |  B1 Confirm  |  All confirm = resolve",
                               True, (100, 100, 140))
        screen.blit(hlp, (512 - 200, 720))
