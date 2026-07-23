import pygame
import math
from .player import Player
from .key_binding import key_to_display, ACTIONS, DEFAULT_BINDINGS, key_matches
from .input_handler import get_menu_nav, get_menu_nav_fallback

W, H = 1024, 768

C = {
    'bg_top': (15, 15, 45),
    'bg_bot': (25, 25, 65),
    'panel': (30, 30, 70, 200),
    'panel_border': (60, 60, 110),
    'accent': (255, 107, 107),
    'accent_glow': (255, 80, 80),
    'gold': (255, 217, 61),
    'gold_dim': (200, 170, 50),
    'green': (107, 203, 119),
    'blue': (77, 150, 255),
    'purple': (147, 112, 219),
    'text': (240, 240, 255),
    'text_dim': (130, 130, 170),
    'orange': (255, 160, 60),
}

PLAYER_COLORS = [(66, 133, 244), (234, 67, 53), (52, 168, 83)]


def draw_gradient(screen, top, bot, rect):
    h = rect.height
    for y in range(h):
        t = y / h
        r = int(top[0] * (1 - t) + bot[0] * t)
        g = int(top[1] * (1 - t) + bot[1] * t)
        b = int(top[2] * (1 - t) + bot[2] * t)
        pygame.draw.line(screen, (r, g, b), (rect.x, rect.y + y),
                         (rect.x + rect.width, rect.y + y))


def draw_panel(screen, rect, color=C['panel'], border=C['panel_border'], bw=2, radius=12):
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(s, color, (0, 0, rect.width, rect.height), border_radius=radius)
    screen.blit(s, (rect.x, rect.y))
    pygame.draw.rect(screen, border, rect, width=bw, border_radius=radius)


def draw_glow_selection(screen, rect, color, pulse=0):
    glow = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
    alpha = int(50 + 30 * math.sin(pulse))
    for i in range(8, 0, -1):
        a = alpha // (9 - i)
        r = rect.width + i * 2
        h2 = rect.height + i * 2
        pygame.draw.rect(glow, (*color, a),
                         (10 - i, 10 - i, r, h2),
                         border_radius=12)
    screen.blit(glow, (rect.x - 10, rect.y - 10))
    pygame.draw.rect(screen, color, rect, width=3, border_radius=12)


def draw_selector_arrow(screen, x, y, color, pulse):
    offset = int(4 * math.sin(pulse))
    points = [(x, y + 10 + offset), (x + 15, y + offset), (x + 15, y + 20 + offset)]
    pygame.draw.polygon(screen, color, points)


def render_text(screen, font, text, color, center=None, topleft=None, shadow=False):
    if shadow:
        s = font.render(text, True, (0, 0, 0, 80))
        sr = s.get_rect(center=(center[0] + 2, center[1] + 2)) if center else \
             s.get_rect(topleft=(topleft[0] + 2, topleft[1] + 2))
        s.set_alpha(80)
        screen.blit(s, sr)
    surf = font.render(text, True, color)
    if center:
        r = surf.get_rect(center=center)
    else:
        r = surf.get_rect(topleft=topleft)
    screen.blit(surf, r)
    return r


class MenuRenderer:
    def __init__(self, engine):
        self.engine = engine
        self.sel = 0
        self.pulse = 0
        self.frame = 0

        self.sel_player = 0
        self.sel_binding = 0
        self.remap_waiting = False
        self.scroll_offset = 0

    def _nav(self, event):
        if event.type != pygame.KEYDOWN:
            return None
        action = get_menu_nav(event, self.engine.players)
        if action:
            return action
        return get_menu_nav_fallback(event)

    def _nav_any(self, event):
        nav = self._nav(event)
        if nav:
            return nav
        return None

    def _bg(self):
        draw_gradient(self.engine.screen, C['bg_top'], C['bg_bot'],
                      pygame.Rect(0, 0, W, H))

    def _stars(self):
        s = self.engine.screen
        for i in range(40):
            x = (i * 137 + 50) % W
            y = (i * 97 + 30) % (H // 2)
            b = 40 + (i * 13) % 80
            s.set_at((x, y), (b, b, b + 20))

    def _decorated_title(self, text, y=50, icon=None):
        s = self.engine.screen
        f = self.engine.fonts
        if icon:
            isurf = f['medium'].render(icon, True, C['gold'])
            ir = isurf.get_rect(center=(W // 2 - 180, y))
            s.blit(isurf, ir)
        render_text(s, f['large'], text, C['gold'],
                    center=(W // 2, y), shadow=True)

    def _footer(self, text):
        render_text(self.engine.screen, self.engine.fonts['tiny'], text, C['text_dim'],
                    center=(W // 2, H - 25))

    def _opt(self, i, text, y_start=190, line_h=60):
        s = self.engine.screen
        f = self.engine.fonts
        y = y_start + i * line_h
        panel_rect = pygame.Rect(W // 2 - 180, y - 15, 360, 44)

        if i == self.sel:
            draw_glow_selection(s, panel_rect, C['accent'], self.pulse)
            render_text(s, f['small'], f"  {text}", C['text'],
                        center=(W // 2, y + 7))
        else:
            pygame.draw.rect(s, (40, 40, 75), panel_rect, border_radius=8)
            render_text(s, f['small'], f"  {text}", C['text_dim'],
                        center=(W // 2, y + 7))
        return y

    def _process_nav(self, event, options):
        nav = self._nav_any(event)
        if nav == 'up':
            self.sel = (self.sel - 1) % len(options)
        elif nav == 'down':
            self.sel = (self.sel + 1) % len(options)
        elif nav == 'btn1' or nav == 'enter':
            return options[self.sel][1]
        elif nav == 'btn2' or nav == 'esc':
            return 'BACK'
        return None

    def main_menu(self):
        self.frame += 1
        self.pulse = self.frame * 0.05
        s = self.engine.screen
        f = self.engine.fonts
        self._bg()
        self._stars()

        draw_panel(s, pygame.Rect(200, 30, 624, 140), border=C['gold_dim'])
        render_text(s, f['large'], "FAMILY GAME FUN!", C['gold'],
                    center=(W // 2, 75), shadow=True)
        render_text(s, f['tiny'], "Educational Mini-Games for 1-3 Players",
                    C['text_dim'], center=(W // 2, 125))

        opts = [("Play Games", 'PLAY'), ("Leaderboard", 'LEAD'),
                ("Badges & Stickers", 'BADGE'), ("Settings", 'SET'),
                ("Quit", 'QUIT')]

        for i, (txt, action) in enumerate(opts):
            self._opt(i, txt, 200, 65)

        self._footer("↑↓ Navigate  |  B1 Select  |  B2 / Esc Back")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.engine.running = False
                return
            r = self._process_nav(event, opts)
            if r == 'PLAY':
                self.sel = 0
                self.engine.state = 'PLAYER_SELECT'
            elif r == 'LEAD':
                self.sel = 0
                self.engine.state = 'LEADERBOARD'
            elif r == 'BADGE':
                self.sel = 0
                if not self.engine.players:
                    self.engine.players = [Player(0)]
                self.engine.state = 'BADGES'
            elif r == 'SET':
                self.sel = 0
                self.engine.state = 'SETTINGS'
            elif r == 'QUIT':
                self.engine.running = False

    def settings(self):
        self.frame += 1
        self.pulse = self.frame * 0.05
        s = self.engine.screen
        f = self.engine.fonts
        self._bg()
        self._stars()
        self._decorated_title("Settings - Key Bindings", 40)

        pidx = self.sel_player
        names = ["Player 1 (WASD+1,Q)", "Player 2 (JNM,+V,B)", "Player 3 (=()#+0,-)"]
        colors = PLAYER_COLORS

        # Player tabs
        for i in range(3):
            tx = 80 + i * 300
            ty = 100
            tab_rect = pygame.Rect(tx, ty, 260, 36)
            if i == pidx:
                draw_glow_selection(s, tab_rect, colors[i], self.pulse)
                render_text(s, f['tiny'], names[i], (255, 255, 255), center=(tx + 130, ty + 18))
            else:
                pygame.draw.rect(s, (40, 40, 70), tab_rect, border_radius=6)
                render_text(s, f['tiny'], names[i], C['text_dim'], center=(tx + 130, ty + 18))

        bindings = self.engine.bindings[pidx]
        action_labels = {'up': 'Up', 'down': 'Down', 'left': 'Left', 'right': 'Right',
                         'btn1': 'Button 1', 'btn2': 'Button 2'}

        if self.remap_waiting:
            render_text(s, f['medium'], "Press a key for: " + action_labels[ACTIONS[self.sel_binding]],
                        C['gold'], center=(W // 2, 370))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.engine.running = False
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.remap_waiting = False
                    else:
                        mod_mask = event.mod & pygame.KMOD_SHIFT
                        self.engine.bindings[pidx][ACTIONS[self.sel_binding]] = (event.key, mod_mask)
                        from .key_binding import save_bindings
                        save_bindings(self.engine.bindings)
                        self.remap_waiting = False
                        for p in self.engine.players:
                            if p.index == pidx:
                                p.bindings = self.engine.bindings[pidx]
            return

        for i, act in enumerate(ACTIONS):
            row = i // 2
            col = i % 2
            bx = 120 + col * 420
            by = 150 + row * 70
            kc, mm = bindings[act]
            display = key_to_display(kc, mm)
            bg_rect = pygame.Rect(bx, by, 380, 48)

            if i == self.sel_binding and self.sel_player == pidx:
                draw_glow_selection(s, bg_rect, C['accent'], self.pulse)
            else:
                pygame.draw.rect(s, (35, 35, 68), bg_rect, border_radius=8)

            render_text(s, f['tiny'], action_labels[act], C['text'], topleft=(bx + 15, by + 6))
            render_text(s, f['small'], f"[ {display} ]", colors[pidx],
                        topleft=(bx + 15, by + 22))

        render_text(s, f['tiny'], "Select a key → press Enter to remap  |  B2: Back",
                    C['text_dim'], center=(W // 2, H - 80))

        # Also show controls info
        render_text(s, f['tiny'],
                    "P1: W/A/S/D + 1/Q  |  P2: J/N/M/, + V/B  |  P3: =(=)/# + 0/-",
                    C['text_dim'], center=(W // 2, H - 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.engine.running = False
                return
            nav = self._nav_any(event)
            if nav == 'up':
                self.sel_binding = (self.sel_binding - 1) % len(ACTIONS)
            elif nav == 'down':
                self.sel_binding = (self.sel_binding + 1) % len(ACTIONS)
            elif nav == 'left':
                self.sel_player = (self.sel_player - 1) % 3
                self.sel_binding = 0
            elif nav == 'right':
                self.sel_player = (self.sel_player + 1) % 3
                self.sel_binding = 0
            elif nav == 'btn1' or nav == 'enter':
                self.remap_waiting = True
            elif nav == 'btn2' or nav == 'esc':
                self.sel = 0
                self.engine.state = 'MAIN_MENU'

    def player_select(self):
        self.frame += 1
        self.pulse = self.frame * 0.05
        s = self.engine.screen
        f = self.engine.fonts
        self._bg()
        self._stars()
        self._decorated_title("How Many Players?", 60)

        names = ["1 Player", "2 Players", "3 Players"]
        descs = ["Play solo", "Head-to-head", "Family battle!"]
        icons = ["👤", "👥", "👨‍👩‍👧"]

        for i in range(3):
            bx = 100 + i * 290
            by = 190
            panel = pygame.Rect(bx, by, 250, 300)
            if i == self.sel:
                draw_glow_selection(s, panel, C['accent'], self.pulse)
            else:
                draw_panel(s, panel)

            render_text(s, f['large'], icons[i], C['gold'], center=(bx + 125, by + 60))
            render_text(s, f['small'], names[i], C['text'], center=(bx + 125, by + 130))
            render_text(s, f['tiny'], descs[i], C['text_dim'], center=(bx + 125, by + 165))

            # Key info
            if i == 0:
                keys_info = ["WASD + 1,Q"]
            elif i == 1:
                keys_info = ["P1: WASD+1,Q", "P2: JNM,+V,B"]
            else:
                keys_info = ["P1: WASD+1,Q", "P2: JNM,+V,B", "P3: =()#+0,-"]
            for j, ki in enumerate(keys_info):
                render_text(s, f['tiny'], ki, PLAYER_COLORS[j],
                            center=(bx + 125, by + 200 + j * 22))

        self._footer("↑↓←→ Navigate  |  B1 Select  |  B2 Back")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.engine.running = False
                return
            nav = self._nav_any(event)
            if nav == 'left':
                self.sel = (self.sel - 1) % 3
            elif nav == 'right':
                self.sel = (self.sel + 1) % 3
            elif nav == 'up' or nav == 'down':
                pass
            elif nav == 'btn1' or nav == 'enter':
                count = self.sel + 1
                self.engine.players = [Player(i, bindings=self.engine.bindings[i])
                                       for i in range(count)]
                self.sel = 0
                self.engine.state = 'GAME_SELECT'
            elif nav == 'btn2' or nav == 'esc':
                self.sel = 0
                self.engine.state = 'MAIN_MENU'

    def game_select(self):
        self.frame += 1
        self.pulse = self.frame * 0.05
        s = self.engine.screen
        f = self.engine.fonts
        from games.registry import get_games_by_category, GAMES
        self._bg()
        self._stars()
        self._decorated_title("Select a Game", 40)

        cats = get_games_by_category()
        cat_names = ['All'] + sorted(cats.keys())

        # Category tabs
        tab_y = 95
        tab_h = 32
        total_tab_w = sum(f['tiny'].render(cn, True, (0, 0, 0)).get_width() + 40
                         for cn in cat_names)
        start_x = max(20, (W - total_tab_w) // 2)
        cx = start_x
        cat_rects = []
        for ci, cn in enumerate(cat_names):
            tw = f['tiny'].render(cn, True, (0, 0, 0)).get_width() + 40
            tr = pygame.Rect(cx, tab_y, tw, tab_h)
            cat_rects.append((tr, cn, ci))
            if cn == self.engine.selected_category:
                pygame.draw.rect(s, C['accent'], tr, border_radius=16)
                render_text(s, f['tiny'], cn, (255, 255, 255), center=tr.center)
            else:
                pygame.draw.rect(s, (40, 40, 75), tr, border_radius=16)
                render_text(s, f['tiny'], cn, C['text_dim'], center=tr.center)
            cx += tw + 8

        # Filtered games
        all_games = [(gid, info) for gid, info in GAMES.items()]
        if self.engine.selected_category == 'All':
            filtered = all_games
        else:
            filtered = [(gid, info) for gid, info in all_games
                       if info['category'] == self.engine.selected_category]

        if not filtered:
            render_text(s, f['medium'], "No games in this category yet!",
                        C['text_dim'], center=(W // 2, 400))
        else:
            self.sel = min(self.sel, len(filtered) - 1)
            list_start_y = 145
            item_h = 55
            max_visible = min(len(filtered), 8)
            self.scroll_offset = max(0, min(self.scroll_offset,
                                            len(filtered) - max_visible))
            self.sel = max(0, min(self.sel, len(filtered) - 1))

            for vi in range(max_visible):
                gi = vi + self.scroll_offset
                if gi >= len(filtered):
                    break
                gid, info = filtered[gi]
                iy = list_start_y + vi * item_h
                panel_r = pygame.Rect(80, iy, 600, item_h - 4)

                if gi == self.sel:
                    draw_glow_selection(s, panel_r, C['accent'], self.pulse)
                else:
                    pygame.draw.rect(s, (35, 35, 68), panel_r, border_radius=8)

                render_text(s, f['tiny'], f"{info['icon']}  {info['name']}",
                            C['text'], topleft=(panel_r.x + 15, panel_r.y + 6))
                players_str = f"{info['min_players']}-{info['max_players']}p"
                render_text(s, f['tiny'], players_str, C['text_dim'],
                            topleft=(panel_r.x + 15, panel_r.y + 26))

            # Preview panel on the right
            if filtered:
                gid, info = filtered[self.sel]
                preview_x = 710
                preview_y = 145
                preview_w = 280
                preview_h = 400
                preview_r = pygame.Rect(preview_x, preview_y, preview_w, preview_h)
                draw_panel(s, preview_r)

                render_text(s, f['tiny'], f"{info['icon']}  {info['name']}",
                            C['gold'], center=(preview_x + preview_w // 2, preview_y + 25))
                render_text(s, f['tiny'], info['category'], C['blue'],
                            center=(preview_x + preview_w // 2, preview_y + 50))

                # Game preview drawing
                preview = info.get('preview')
                if preview:
                    lines = preview.split('\n')
                    for li, line in enumerate(lines):
                        render_text(s, f['tiny'], line, C['text_dim'],
                                    center=(preview_x + preview_w // 2,
                                           preview_y + 85 + li * 18))

                render_text(s, f['tiny'], info['description'], C['text_dim'],
                            center=(preview_x + preview_w // 2, preview_y + preview_h - 40))

        # Scroll indicators
        if self.scroll_offset > 0:
            render_text(s, f['tiny'], "▲ More above", C['text_dim'],
                        center=(380, 135))
        if self.scroll_offset + max_visible < len(filtered):
            render_text(s, f['tiny'], "▼ More below", C['text_dim'],
                        center=(380, list_start_y + max_visible * item_h + 5))

        self._footer("↑↓ Navigate  |  ←→ Categories  |  B1 Details  |  B2 Back")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.engine.running = False
                return
            nav = self._nav_any(event)

            if event.type == pygame.KEYDOWN:
                # Tab selection via direct key
                for ci, (tr, cn, _) in enumerate(cat_rects):
                    if tr.collidepoint(W // 2, tab_y) and ci != 0:  # Simplified
                        pass
                # Handle 1-9 shortcuts
                if pygame.K_1 <= event.key <= pygame.K_9:
                    idx = event.key - pygame.K_1
                    if idx < len(cat_names):
                        self.engine.selected_category = cat_names[idx]
                        self.sel = 0
                        self.scroll_offset = 0

            if nav == 'up':
                self.sel = max(0, self.sel - 1)
                if self.sel < self.scroll_offset:
                    self.scroll_offset = self.sel
            elif nav == 'down':
                self.sel = min(len(filtered) - 1, self.sel + 1) if filtered else 0
                if self.sel >= self.scroll_offset + max_visible:
                    self.scroll_offset = self.sel - max_visible + 1
            elif nav == 'left':
                cats_list = list(cats.keys())
                cur = self.engine.selected_category
                if cur == 'All':
                    self.engine.selected_category = cats_list[-1] if cats_list else 'All'
                else:
                    idx = cats_list.index(cur)
                    self.engine.selected_category = cats_list[idx - 1] if idx > 0 else 'All'
                self.sel = 0
                self.scroll_offset = 0
            elif nav == 'right':
                cats_list = list(cats.keys())
                cur = self.engine.selected_category
                if cur == 'All':
                    self.engine.selected_category = cats_list[0] if cats_list else 'All'
                else:
                    idx = cats_list.index(cur)
                    self.engine.selected_category = cats_list[(idx + 1) % len(cats_list)]
                self.sel = 0
                self.scroll_offset = 0
            elif nav == 'btn1' or nav == 'enter':
                if filtered:
                    gid = filtered[self.sel][0]
                    self.engine.pending_game_id = gid
                    self.sel = 0
                    self.engine.state = 'GAME_DETAIL'
            elif nav == 'btn2' or nav == 'esc':
                self.sel = 0
                self.scroll_offset = 0
                self.engine.selected_category = 'All'
                self.engine.state = 'MAIN_MENU'

    def game_detail(self):
        self.frame += 1
        self.pulse = self.frame * 0.05
        s = self.engine.screen
        f = self.engine.fonts
        from games.registry import GAMES
        self._bg()
        self._stars()

        gid = getattr(self.engine, 'pending_game_id', None)
        if not gid or gid not in GAMES:
            self.engine.state = 'GAME_SELECT'
            return

        info = GAMES[gid]
        diff = self.engine.get_difficulty(gid)

        # Title + icon
        draw_panel(s, pygame.Rect(50, 20, 924, 100))
        render_text(s, f['large'], f"{info['icon']}  {info['name']}", C['gold'],
                    center=(W // 2, 50), shadow=True)
        render_text(s, f['tiny'], info['description'], C['text_dim'],
                    center=(W // 2, 90))

        # LEFT PANEL: Goal + Controls
        draw_panel(s, pygame.Rect(50, 135, 450, 280))
        goal = info.get('goal', 'Be the player with the highest score!')
        render_text(s, f['small'], "Goal", C['gold'], topleft=(70, 150))
        render_text(s, f['tiny'], goal, C['text'], topleft=(70, 185))

        render_text(s, f['small'], "Controls", C['gold'], topleft=(70, 260))
        for pi in range(len(self.engine.players)):
            p = self.engine.players[pi]
            b = p.bindings
            up = key_to_display(*b['up'])
            dn = key_to_display(*b['down'])
            lf = key_to_display(*b['left'])
            rt = key_to_display(*b['right'])
            b1 = key_to_display(*b['btn1'])
            b2 = key_to_display(*b['btn2'])
            c = PLAYER_COLORS[pi]
            render_text(s, f['tiny'],
                        f"P{pi+1}: [{up}{dn}{lf}{rt}] + [{b1}] [{b2}]",
                        c, topleft=(70, 285 + pi * 22))

        # RIGHT PANEL: Last 3 scores
        draw_panel(s, pygame.Rect(530, 135, 444, 280))
        render_text(s, f['small'], "Recent High Scores", C['gold'],
                    center=(752, 150))
        entries = self.engine.leaderboard.get_top(gid, 3)
        if entries:
            for ei, entry in enumerate(entries):
                ey = 185 + ei * 55
                medal = ["🥇", "🥈", "🥉"][ei]
                render_text(s, f['medium'], medal, C['gold'],
                            topleft=(555, ey))
                render_text(s, f['tiny'], entry['player'], C['text'],
                            topleft=(600, ey))
                render_text(s, f['tiny'], f"{entry['score']} pts",
                            C['gold'], topleft=(600, ey + 20))
                render_text(s, f['tiny'], entry['date'], C['text_dim'],
                            topleft=(700, ey + 20))
        else:
            render_text(s, f['tiny'], "No scores yet! Be the first!",
                        C['text_dim'], center=(752, 280))

        # BOTTOM: Difficulty settings
        draw_panel(s, pygame.Rect(50, 430, 924, 200))
        render_text(s, f['small'], "Difficulty Settings", C['gold'],
                    center=(W // 2, 445))

        diff_vars = info.get('difficulty_vars', {})
        diff_keys = list(diff_vars.keys())
        if diff_keys:
            for di, dk in enumerate(diff_keys):
                dv = diff_vars[dk]
                cur_val = diff.get(dk, dv['default'])
                min_v, max_v = dv['min'], dv['max']
                dy = 480 + di * 55

                render_text(s, f['tiny'], f"{dk}: {cur_val}",
                            C['text'], topleft=(70, dy))

                # Bar
                bar_x, bar_y = 220, dy + 5
                bar_w, bar_h = 400, 18
                pygame.draw.rect(s, (40, 40, 70),
                                 (bar_x, bar_y, bar_w, bar_h), border_radius=9)
                fill = (cur_val - min_v) / (max_v - min_v)
                fill_w = int(bar_w * fill)
                if fill_w > 0:
                    fill_color = (C['green'] if fill > 0.6
                                  else C['orange'] if fill > 0.3
                                  else C['accent'])
                    pygame.draw.rect(s, fill_color,
                                     (bar_x, bar_y, fill_w, bar_h), border_radius=9)

                # Buttons
                btn_minus = pygame.Rect(bar_x - 40, bar_y - 3, 30, 24)
                btn_plus = pygame.Rect(bar_x + bar_w + 10, bar_y - 3, 30, 24)
                pygame.draw.rect(s, C['panel_border'], btn_minus, border_radius=4)
                pygame.draw.rect(s, C['panel_border'], btn_plus, border_radius=4)
                render_text(s, f['tiny'], "-", C['text'],
                            center=btn_minus.center)
                render_text(s, f['tiny'], "+", C['text'],
                            center=btn_plus.center)

                # Active difficulty var for changing
                if di == self.sel:
                    # Highlight
                    pygame.draw.rect(s, C['accent'],
                                     (bar_x, bar_y, bar_w, bar_h), width=2, border_radius=9)

        # Bottom buttons
        btn_play = pygame.Rect(W // 2 - 150, 650, 140, 50)
        btn_back = pygame.Rect(W // 2 + 10, 650, 140, 50)
        draw_glow_selection(s, btn_play, C['green'], self.pulse)
        render_text(s, f['small'], "▶  Play", C['text'], center=btn_play.center)
        pygame.draw.rect(s, (50, 50, 85), btn_back, border_radius=8)
        render_text(s, f['tiny'], "Back", C['text'], center=btn_back.center)

        self._footer("←→ Adjust Difficulty  |  ↑↓ Select Variable  |  B1 Play  |  B2 Back")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.engine.running = False
                return
            nav = self._nav_any(event)

            if event.type == pygame.KEYDOWN:
                if nav == 'up' and diff_keys:
                    self.sel = (self.sel - 1) % len(diff_keys)
                elif nav == 'down' and diff_keys:
                    self.sel = (self.sel + 1) % len(diff_keys)
                elif nav == 'left' and diff_keys:
                    dk = diff_keys[self.sel]
                    cv = diff.get(dk, diff_vars[dk]['default'])
                    if cv > diff_vars[dk]['min']:
                        diff[dk] = cv - 1
                        self.engine.set_difficulty(gid, dk, diff[dk])
                elif nav == 'right' and diff_keys:
                    dk = diff_keys[self.sel]
                    cv = diff.get(dk, diff_vars[dk]['default'])
                    if cv < diff_vars[dk]['max']:
                        diff[dk] = cv + 1
                        self.engine.set_difficulty(gid, dk, diff[dk])
                elif nav == 'btn1' or nav == 'enter':
                    if self.engine.players:
                        self.engine.start_game(gid, self.engine.players[:])
                elif nav == 'btn2' or nav == 'esc':
                    self.sel = 0
                    self.engine.state = 'GAME_SELECT'

    def game_over(self):
        self.frame += 1
        self.pulse = self.frame * 0.05
        s = self.engine.screen
        f = self.engine.fonts
        results = self.engine.game_results
        if not results:
            self.sel = 0
            self.engine.state = 'MAIN_MENU'
            return

        self._bg()
        self._stars()
        draw_panel(s, pygame.Rect(200, 25, 624, 90))
        render_text(s, f['large'], "Game Over!", C['gold'],
                    center=(W // 2, 50), shadow=True)

        winners = [r for r in results if r.get('winner')]
        if winners:
            names = " & ".join(r['player'].name for r in winners)
            render_text(s, f['medium'], f"🏆  {names} wins!  🏆", C['gold'],
                        center=(W // 2, 110))

        # Score cards
        for i, r in enumerate(results):
            cx = 130 + i * 270
            cy = 160
            card_w = 240
            card_h = 180
            p = r['player']
            card_rect = pygame.Rect(cx, cy, card_w, card_h)
            if r.get('winner'):
                draw_glow_selection(s, card_rect, C['gold'], self.pulse)
            else:
                draw_panel(s, card_rect)

            pygame.draw.rect(s, p.color, (cx + 10, cy + 10, 20, 20), border_radius=5)
            render_text(s, f['small'], p.name, p.color,
                        topleft=(cx + 40, cy + 10))
            render_text(s, f['large'], str(r['score']), C['gold'] if r.get('winner') else C['text'],
                        center=(cx + card_w // 2, cy + 80))
            render_text(s, f['tiny'], "points", C['text_dim'],
                        center=(cx + card_w // 2, cy + 115))

        # New badges
        new_badges = []
        for r in results:
            bs = self.engine.badges.get_badges(r['player'].name)
            nb = [b for b in bs if b['name'] not in getattr(self, '_shown_badges', set())]
            new_badges.extend(nb)
        if new_badges:
            by = 370
            render_text(s, f['tiny'], "New Badges Earned!", C['gold'],
                        center=(W // 2, by))
            for bi, badge in enumerate(new_badges[:4]):
                bx = 250 + bi * 140
                render_text(s, f['medium'], badge['emoji'], C['text'],
                            center=(bx, by + 35))
                render_text(s, f['tiny'], badge['name'], C['text_dim'],
                            center=(bx, by + 60))
        self._shown_badges = set()
        for r in results:
            for b in self.engine.badges.get_badges(r['player'].name):
                self._shown_badges.add(b['name'])

        opts = [("Play Again", 'AGAIN'), ("Leaderboard", 'LEAD'), ("Main Menu", 'MENU')]
        for i, (txt, act) in enumerate(opts):
            self._opt(i, txt, 450, 60)

        self._footer("↑↓ Navigate  |  B1 Select  |  B2 Back")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.engine.running = False
                return
            r = self._process_nav(event, opts)
            if r == 'AGAIN':
                self.engine.start_game(
                    self.engine.current_game_id,
                    self.engine.players[:])
            elif r == 'LEAD':
                self.sel = 0
                self.engine.state = 'LEADERBOARD'
            elif r in ('MENU', 'BACK'):
                self.sel = 0
                self.engine.state = 'MAIN_MENU'

    def leaderboard(self):
        self.frame += 1
        self.pulse = self.frame * 0.05
        s = self.engine.screen
        f = self.engine.fonts
        from games.registry import GAMES
        self._bg()
        self._stars()
        self._decorated_title("Leaderboard", 40)

        lb = self.engine.leaderboard
        game_ids = lb.get_all_game_ids()
        if not game_ids:
            draw_panel(s, pygame.Rect(250, 200, 524, 200))
            render_text(s, f['medium'], "No scores yet!", C['gold'],
                        center=(W // 2, 280))
            render_text(s, f['tiny'], "Play some games to see rankings here.",
                        C['text_dim'], center=(W // 2, 330))
        else:
            gid_idx = self.sel % len(game_ids)
            gid = game_ids[gid_idx]
            gname = GAMES.get(gid, {}).get('name', gid)
            gicon = GAMES.get(gid, {}).get('icon', '🎮')

            render_text(s, f['small'], f"{gicon}  {gname}", C['blue'],
                        center=(W // 2, 90))

            entries = lb.get_top(gid, 10)
            # Header
            header_y = 120
            render_text(s, f['tiny'], "Rank", C['gold'], topleft=(150, header_y))
            render_text(s, f['tiny'], "Player", C['gold'], topleft=(250, header_y))
            render_text(s, f['tiny'], "Score", C['gold'], topleft=(550, header_y))
            render_text(s, f['tiny'], "Date", C['gold'], topleft=(680, header_y))

            for ei, entry in enumerate(entries):
                ey = header_y + 30 + ei * 34
                row_bg = pygame.Rect(130, ey - 4, 760, 30)
                if ei % 2 == 0:
                    pygame.draw.rect(s, (30, 30, 65), row_bg, border_radius=4)

                medal = ["🥇", "🥈", "🥉"][ei] if ei < 3 else f" {ei + 1}. "
                render_text(s, f['tiny'], medal, C['gold'] if ei < 3 else C['text_dim'],
                            topleft=(150, ey))
                render_text(s, f['tiny'], entry['player'],
                            C['gold'] if ei < 3 else C['text'],
                            topleft=(250, ey))
                render_text(s, f['tiny'], str(entry['score']),
                            C['gold'] if ei < 3 else C['text'],
                            topleft=(560, ey))
                render_text(s, f['tiny'], entry['date'], C['text_dim'],
                            topleft=(690, ey))

            if len(game_ids) > 1:
                nav_txt = f"← → Switch Game ({gid_idx + 1}/{len(game_ids)})"
                render_text(s, f['tiny'], nav_txt, C['text_dim'],
                            center=(W // 2, H - 65))

        self._footer("← → Switch Game  |  B2 Back")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.engine.running = False
                return
            nav = self._nav_any(event)
            if nav == 'left' and game_ids:
                self.sel = (self.sel - 1) % len(game_ids)
            elif nav == 'right' and game_ids:
                self.sel = (self.sel + 1) % len(game_ids)
            elif nav == 'btn2' or nav == 'esc':
                self.sel = 0
                self.engine.state = 'MAIN_MENU'

    def badges(self):
        self.frame += 1
        self.pulse = self.frame * 0.05
        s = self.engine.screen
        f = self.engine.fonts
        self._bg()
        self._stars()
        self._decorated_title("Badges & Stickers", 40)

        players = self.engine.players
        if not players:
            draw_panel(s, pygame.Rect(250, 200, 524, 150))
            render_text(s, f['medium'], "Play a game first!", C['gold'],
                        center=(W // 2, 270))
            render_text(s, f['tiny'], "Earn badges by playing games and winning.",
                        C['text_dim'], center=(W // 2, 320))
        else:
            pidx = self.sel % len(players)
            p = players[pidx]
            pname = p.name
            pcolor = p.color

            draw_panel(s, pygame.Rect(50, 80, 924, 60), border=pcolor)
            render_text(s, f['small'], f"Showing: {pname}", pcolor,
                        center=(W // 2, 105))
            stats = f"Games Played: {self.engine.badges.get_total_games_played(pname)}"
            render_text(s, f['tiny'], stats, C['text_dim'],
                        center=(W // 2, 125))

            badges = self.engine.badges.get_all_badges(pname)
            cols = 4
            badge_w = 180
            gap = 20
            start_x = (W - (cols * badge_w + (cols - 1) * gap)) // 2
            for i, badge in enumerate(badges):
                col = i % cols
                row = i // cols
                bx = start_x + col * (badge_w + gap)
                by = 160 + row * 105

                bgr = pygame.Rect(bx, by, badge_w, 85)
                if badge['earned']:
                    pygame.draw.rect(s, (40, 40, 75), bgr, border_radius=10)
                    pygame.draw.rect(s, badge['color'], bgr, width=2, border_radius=10)
                    render_text(s, f['small'], badge['emoji'], C['text'],
                                topleft=(bx + 10, by + 10))
                    render_text(s, f['tiny'], badge['name'], C['gold'],
                                topleft=(bx + 55, by + 10))
                    render_text(s, f['tiny'], badge['desc'], C['text_dim'],
                                topleft=(bx + 55, by + 35))
                else:
                    pygame.draw.rect(s, (25, 25, 50), bgr, border_radius=10)
                    pygame.draw.rect(s, (40, 40, 70), bgr, width=1, border_radius=10)
                    render_text(s, f['small'], "🔒", C['text_dim'],
                                topleft=(bx + 10, by + 10))
                    render_text(s, f['tiny'], badge['name'], C['text_dim'],
                                topleft=(bx + 55, by + 10))
                    render_text(s, f['tiny'], badge['desc'], C['text_dim'],
                                topleft=(bx + 55, by + 35))

        nav_txt = "← → Switch Player  |  " if len(players) > 1 else ""
        nav_txt += "B2 Back"
        self._footer(nav_txt)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.engine.running = False
                return
            nav = self._nav_any(event)
            if nav == 'left' and len(self.engine.players) > 1:
                self.sel = (self.sel - 1) % len(self.engine.players)
            elif nav == 'right' and len(self.engine.players) > 1:
                self.sel = (self.sel + 1) % len(self.engine.players)
            elif nav == 'btn2' or nav == 'esc':
                self.sel = 0
                self.engine.state = 'MAIN_MENU'
