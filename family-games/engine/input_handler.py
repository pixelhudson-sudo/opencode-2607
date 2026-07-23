import pygame
from .key_binding import key_matches, key_to_display, ACTIONS, get_pressed_action, get_direction

NAV_ACTIONS = ['up', 'down', 'left', 'right', 'btn1', 'btn2']


def get_player_action(event, players):
    for player in players:
        action = get_pressed_action(event, player.bindings)
        if action:
            return player.index, action
    return None, None


def get_direction_any(event, players):
    for player in players:
        d = get_direction(event, player.bindings)
        if d:
            return player.index, d[0], d[1]
    return None, 0, 0


def is_button_any(event, players):
    for player in players:
        b = _is_btn(event, player.bindings)
        if b:
            return player.index, b
    return None, 0


def _is_btn(event, bindings):
    mod = event.mod if hasattr(event, 'mod') else 0
    kc1, mm1 = bindings['btn1']
    if mm1 and event.key == kc1 and (mod & mm1):
        return 1
    kc2, mm2 = bindings['btn2']
    if mm2 and event.key == kc2 and (mod & mm2):
        return 2
    if not mm1 and event.key == kc1:
        return 1
    if not mm2 and event.key == kc2:
        return 2
    return 0


def get_menu_nav(event, players):
    mod = event.mod if hasattr(event, 'mod') else 0
    for player in players:
        for action in NAV_ACTIONS:
            kc, mm = player.bindings[action]
            if mm and event.key == kc and (mod & mm):
                return action
            if not mm and event.key == kc and not (mod & pygame.KMOD_SHIFT):
                pass
        for action in NAV_ACTIONS:
            kc, mm = player.bindings[action]
            if not mm and event.key == kc:
                return action
    return None


def format_bindings_for_display(bindings, action_map=None):
    parts = []
    for act in ACTIONS:
        label = action_map.get(act, act.upper()) if action_map else act.upper()
        kc, mm = bindings[act]
        display = key_to_display(kc, mm)
        parts.append(f"{label}:{display}")
    return '  '.join(parts)


FALLBACK_NAV = [
    (pygame.K_w, 0, 'up'),
    (pygame.K_s, 0, 'down'),
    (pygame.K_a, 0, 'left'),
    (pygame.K_d, 0, 'right'),
    (pygame.K_1, 0, 'btn1'),
    (pygame.K_q, 0, 'btn2'),
    (pygame.K_ESCAPE, 0, 'esc'),
    (pygame.K_RETURN, 0, 'enter'),
    (pygame.K_UP, 0, 'up'),
    (pygame.K_DOWN, 0, 'down'),
    (pygame.K_LEFT, 0, 'left'),
    (pygame.K_RIGHT, 0, 'right'),
]


def get_menu_nav_fallback(event):
    for kc, mm, action in FALLBACK_NAV:
        if key_matches(event, kc, mm):
            return action
    return None
