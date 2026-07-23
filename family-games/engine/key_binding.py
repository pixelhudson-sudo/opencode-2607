import pygame
import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

ACTIONS = ['up', 'down', 'left', 'right', 'btn1', 'btn2']

DEFAULT_BINDINGS = [
    {'up': (pygame.K_w, 0), 'down': (pygame.K_s, 0), 'left': (pygame.K_a, 0),
     'right': (pygame.K_d, 0), 'btn1': (pygame.K_1, 0), 'btn2': (pygame.K_q, 0)},
    {'up': (pygame.K_j, 0), 'down': (pygame.K_n, 0), 'left': (pygame.K_m, 0),
     'right': (pygame.K_COMMA, 0), 'btn1': (pygame.K_v, 0), 'btn2': (pygame.K_b, 0)},
    {'up': (pygame.K_9, pygame.KMOD_SHIFT), 'down': (pygame.K_0, pygame.KMOD_SHIFT),
     'left': (pygame.K_EQUALS, 0), 'right': (pygame.K_3, pygame.KMOD_SHIFT),
     'btn1': (pygame.K_0, 0), 'btn2': (pygame.K_MINUS, 0)},
]

KEY_NAMES = {
    pygame.K_w: 'W', pygame.K_a: 'A', pygame.K_s: 'S', pygame.K_d: 'D',
    pygame.K_1: '1', pygame.K_q: 'Q',
    pygame.K_j: 'J', pygame.K_n: 'N', pygame.K_m: 'M',
    pygame.K_COMMA: ',', pygame.K_v: 'V', pygame.K_b: 'B',
    pygame.K_EQUALS: '=', pygame.K_9: '9', pygame.K_0: '0',
    pygame.K_3: '3', pygame.K_MINUS: '-',
    pygame.K_UP: '↑', pygame.K_DOWN: '↓', pygame.K_LEFT: '←', pygame.K_RIGHT: '→',
    pygame.K_SPACE: 'Space', pygame.K_RETURN: 'Enter', pygame.K_ESCAPE: 'Esc',
    pygame.K_TAB: 'Tab', pygame.K_LSHIFT: 'LShift', pygame.K_RSHIFT: 'RShift',
    pygame.K_LCTRL: 'LCtrl', pygame.K_RCTRL: 'RCtrl',
    pygame.K_LALT: 'LAlt', pygame.K_RALT: 'RAlt',
    pygame.K_2: '2', pygame.K_3: '3', pygame.K_4: '4', pygame.K_5: '5',
    pygame.K_6: '6', pygame.K_7: '7', pygame.K_8: '8',
}

SHIFT_NAMES = {
    pygame.K_9: '(', pygame.K_0: ')', pygame.K_3: '#',
    pygame.K_1: '!', pygame.K_2: '@', pygame.K_4: '$',
    pygame.K_5: '%', pygame.K_6: '^', pygame.K_7: '&', pygame.K_8: '*',
    pygame.K_MINUS: '_', pygame.K_EQUALS: '+',
    pygame.K_COMMA: '<', pygame.K_PERIOD: '>', pygame.K_SLASH: '?',
    pygame.K_SEMICOLON: ':', pygame.K_QUOTE: '"',
    pygame.K_LEFTBRACKET: '{', pygame.K_RIGHTBRACKET: '}',
    pygame.K_BACKSLASH: '|', pygame.K_BACKQUOTE: '~',
}


def key_matches(event, key_code, mod_mask):
    if event.key != key_code:
        return False
    mod = event.mod if hasattr(event, 'mod') else 0
    if mod_mask:
        return (mod & mod_mask) == mod_mask
    return True


def get_pressed_action(event, bindings):
    mod = event.mod if hasattr(event, 'mod') else 0
    for action in ACTIONS:
        kc, mm = bindings[action]
        if mm and event.key == kc and (mod & mm):
            return action
    for action in ACTIONS:
        kc, mm = bindings[action]
        if not mm and event.key == kc:
            return action
    return None


def get_direction(event, bindings):
    mod = event.mod if hasattr(event, 'mod') else 0
    dirs = [('up', 0, -1), ('down', 0, 1), ('left', -1, 0), ('right', 1, 0)]
    for action, dx, dy in dirs:
        kc, mm = bindings[action]
        if mm and event.key == kc and (mod & mm):
            return dx, dy
    for action, dx, dy in dirs:
        kc, mm = bindings[action]
        if not mm and event.key == kc:
            return dx, dy
    return None


def is_button(event, bindings):
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


def key_to_display(key_code, mod_mask):
    if mod_mask and key_code in SHIFT_NAMES:
        return SHIFT_NAMES[key_code]
    return KEY_NAMES.get(key_code, chr(key_code).upper() if 32 <= key_code < 127 else f'K_{key_code}')


def bindings_to_dict(bindings):
    return {a: [k, m] for a, (k, m) in bindings.items()}


def dict_to_bindings(d):
    return {a: (k, m) for a, (k, m) in d.items()}


def save_bindings(bindings_list):
    path = os.path.join(DATA_DIR, 'keybindings.json')
    os.makedirs(DATA_DIR, exist_ok=True)
    data = [bindings_to_dict(b) for b in bindings_list]
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def load_bindings():
    path = os.path.join(DATA_DIR, 'keybindings.json')
    if not os.path.exists(path):
        return [dict(b) for b in DEFAULT_BINDINGS]
    with open(path) as f:
        data = json.load(f)
    return [dict_to_bindings(d) for d in data]
