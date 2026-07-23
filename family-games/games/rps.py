import pygame
import random
from games.base_game import BaseGame
from engine.key_binding import get_pressed_action

CHOICES = ['Rock', 'Paper', 'Scissors']
EMOJIS = {'Rock': '✊', 'Paper': '✋', 'Scissors': '✌️'}
BEATS = {'Rock': 'Scissors', 'Scissors': 'Paper', 'Paper': 'Rock'}


class RPSGame(BaseGame):
    def __init__(self, players, engine, difficulty=None):
        super().__init__(players, engine, difficulty)
        self.font = engine.fonts['small']
        self.tiny = engine.fonts['tiny']
        self.med = engine.fonts['medium']

        r = self.difficulty.get('Rounds', 5)
        t = self.difficulty.get('Timer', 5)
        self.max_rounds = max(1, 2 * r)
        self.timer = max(2, t)
        self.round_num = 0
        self.phase = 'countdown'
        self.phase_timer = 2.0
        self.player_choices = {}
        self.confirmed = set()
        self.scores = {p.index: 0 for p in players}
        self.selections = {p.index: 0 for p in players}
        self.round_results = {}
        self.ready = set()

        for p in players:
            self.player_choices[p.index] = None

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN or self.finished:
            return
        if self.phase != 'playing':
            return

        for p in self.players:
            action = get_pressed_action(event, p.bindings)
            if p.index in self.confirmed:
                continue
            if action == 'up':
                self.selections[p.index] = (self.selections[p.index] - 1) % 3
            elif action == 'down':
                self.selections[p.index] = (self.selections[p.index] + 1) % 3
            elif action == 'btn1':
                self.player_choices[p.index] = CHOICES[self.selections[p.index]]
                self.confirmed.add(p.index)

    def update(self, dt):
        if self.finished:
            return
        self.phase_timer -= dt

        if self.phase == 'countdown' and self.phase_timer <= 0:
            self.phase = 'playing'
            self.phase_timer = self.timer
            self.player_choices = {p.index: None for p in self.players}
            self.confirmed = set()
            self.ready = set()
            self.round_num += 1

        if self.phase == 'playing':
            if self.phase_timer <= 0 or len(self.confirmed) == len(self.players):
                self.phase = 'resolve'
                self.phase_timer = 3.0
                self.resolve_round()
                if self.round_num >= self.max_rounds:
                    self.finish()
                else:
                    self.start_countdown()
            elif len(self.confirmed) == len(self.players):
                pass

        if self.phase == 'resolve' and self.phase_timer <= 0:
            if self.finished:
                self.finish_results()
            else:
                self.phase = 'countdown'
                self.phase_timer = 2.0

    def start_countdown(self):
        pass

    def resolve_round(self):
        picks = [(pi, self.player_choices[pi])
                 for pi in sorted(self.player_choices.keys())
                 if self.player_choices[pi]]
        winners = []
        if len(picks) == 2:
            p1_idx, p1_choice = picks[0]
            p2_idx, p2_choice = picks[1]
            if BEATS[p1_choice] == p2_choice:
                winners.append(p1_idx)
                self.scores[p1_idx] += 1
            elif BEATS[p2_choice] == p1_choice:
                winners.append(p2_idx)
                self.scores[p2_idx] += 1
        elif len(picks) == 3:
            counts = {c: [] for c in CHOICES}
            for pi, pc in picks:
                counts[pc].append(pi)
            for choice, players_with in counts.items():
                if len(players_with) == 1:
                    beaten = BEATS[choice]
                    if len(counts[beaten]) > 0:
                        winners.append(players_with[0])
                        self.scores[players_with[0]] += 1
                    else:
                        pass
        self.round_results = {
            'picks': dict(picks),
            'winners': winners,
        }

    def finish_results(self):
        mx = max(self.scores.values())
        self.results = [
            {'player': p, 'score': self.scores[p.index],
             'winner': self.scores[p.index] == mx}
            for p in self.players
        ]
        self.finished = True

    def render(self, screen):
        screen.fill((20, 20, 50))
        f, s = self.engine.fonts, self.engine.screen

        t = self.med.render(f"✊ ROCK PAPER SCISSORS  Round {self.round_num}/{self.max_rounds}",
                            True, (255, 217, 61))
        tr = t.get_rect(center=(512, 35))
        screen.blit(t, tr)

        if self.phase == 'countdown':
            secs = max(1, int(self.phase_timer) + 1)
            ct = self.med.render(f"Round {self.round_num + 1} starts in {secs}...",
                                 True, (200, 200, 255))
            cr = ct.get_rect(center=(512, 350))
            screen.blit(ct, cr)

        for i, p in enumerate(self.players):
            bx = 60 + i * 320
            by = 100
            panel_w = 290
            panel_h = 350
            pygame.draw.rect(s, (30, 30, 65), (bx, by, panel_w, panel_h), border_radius=12)

            nm = self.font.render(p.name, True, p.color)
            screen.blit(nm, (bx + 10, by + 10))
            sc = self.tiny.render(f"Score: {self.scores[p.index]}", True, (200, 200, 200))
            screen.blit(sc, (bx + 10, by + 40))

            if p.index in self.confirmed:
                ch = self.player_choices[p.index]
                confirm_c = (107, 203, 119)
                pygame.draw.rect(s, confirm_c, (bx + 10, by + 70, panel_w - 20, 50), border_radius=8)
                em = self.font.render(EMOJIS[ch], True, (255, 255, 255))
                sr = em.get_rect(center=(bx + panel_w // 2, by + 95))
                screen.blit(em, sr)
                ct = self.tiny.render(f"Locked: {ch}", True, confirm_c)
                ctr = ct.get_rect(center=(bx + panel_w // 2, by + 130))
                screen.blit(ct, ctr)
            elif self.phase == 'playing':
                for ci, choice in enumerate(CHOICES):
                    cy = by + 80 + ci * 65
                    sel_rect = pygame.Rect(bx + 10, cy, panel_w - 20, 55)
                    if ci == self.selections[p.index]:
                        pygame.draw.rect(s, (60, 60, 120), sel_rect, border_radius=8)
                        pygame.draw.rect(s, p.color, sel_rect, width=2, border_radius=8)
                    else:
                        pygame.draw.rect(s, (40, 40, 75), sel_rect, border_radius=8)
                    em = self.tiny.render(EMOJIS[choice], True, (200, 200, 200))
                    screen.blit(em, (bx + 20, cy + 10))
                    cn = self.tiny.render(choice, True, (200, 200, 200))
                    screen.blit(cn, (bx + 55, cy + 15))

        if self.phase == 'resolve' and self.round_results:
            ry = 500
            picks = self.round_results.get('picks', {})
            winners = self.round_results.get('winners', [])
            rp = self.med.render("Results", True, (255, 217, 61))
            rr = rp.get_rect(center=(512, ry))
            screen.blit(rp, rr)

            for pi, pc in picks.items():
                pobj = next(p for p in self.players if p.index == pi)
                is_w = pi in winners
                c = (107, 203, 119) if is_w else (200, 80, 80)
                txt = f"{pobj.name}: {pc} " + ("WIN" if is_w else "Lose")
                rs = self.font.render(txt, True, c)
                rdr = rs.get_rect(center=(512, ry + 30 + list(picks.keys()).index(pi) * 30))
                screen.blit(rs, rdr)

        hlp = self.tiny.render("↑↓ Choose  |  B1 Lock  |  All lock in = resolve",
                               True, (100, 100, 140))
        hr = hlp.get_rect(center=(512, 730))
        screen.blit(hlp, hr)
