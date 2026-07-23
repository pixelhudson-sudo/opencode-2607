#!/usr/bin/env python3
from games.registry import register_game
from games.snake import SnakeGame
from games.reaction import ReactionGame
from games.letter_match import LetterMatchGame
from games.rps import RPSGame
from games.gun_duel import GunDuelGame
from games.worms_bazooka import WormsBazookaGame

register_game('snake', SnakeGame,
    name='Snake', icon='🐍',
    description='Eat food, grow longer, survive longer than your opponents!',
    category='Agility & Timing',
    min_players=1, max_players=3,
    goal='Control your snake to eat food and grow. Avoid walls and other snakes. '
         'Last snake standing (or highest score) wins!',
    difficulty_vars={
        'Board Size': {'min': 1, 'max': 5, 'default': 3},
        'Speed': {'min': 1, 'max': 5, 'default': 3},
        'Food Frequency': {'min': 1, 'max': 3, 'default': 1},
    },
    preview='🐍 Snake game on a grid, eat food, grow, avoid walls!')

register_game('reaction', ReactionGame,
    name='Reaction Tap', icon='⚡',
    description='Press the button when the bar reaches the green zone!',
    category='Agility & Timing',
    min_players=1, max_players=3,
    goal='Watch the filling bar and press your B1 button when it reaches the '
         'green target zone. Closer to center = more points!',
    difficulty_vars={
        'Speed': {'min': 1, 'max': 5, 'default': 3},
        'Rounds': {'min': 1, 'max': 5, 'default': 3},
        'Tolerance': {'min': 1, 'max': 5, 'default': 3},
    },
    preview='⚡ Bar fills up, press B1 in the green zone!')

register_game('letter_match', LetterMatchGame,
    name='Letter Match', icon='🔤',
    description='Navigate to the correct letter and press B1 to select it!',
    category='Letters & Reading',
    min_players=1, max_players=3,
    goal='Use your directional keys to move your cursor to the target letter '
         'on the grid. First player to press B1 on the correct letter wins!',
    difficulty_vars={
        'Grid Size': {'min': 1, 'max': 5, 'default': 3},
        'Timer': {'min': 1, 'max': 5, 'default': 3},
        'Letter Pool': {'min': 1, 'max': 3, 'default': 2},
    },
    preview='🔤 Find the target letter on the grid!')

register_game('rps', RPSGame,
    name='Rock Paper Scissors', icon='✊',
    description='Classic Rock Paper Scissors. Best of N rounds!',
    category='Logic & Strategy',
    min_players=2, max_players=3,
    goal='Choose Rock, Paper, or Scissors each round. Rock beats Scissors, '
         'Scissors beats Paper, Paper beats Rock. Most wins at the end wins!',
    difficulty_vars={
        'Rounds': {'min': 2, 'max': 10, 'default': 5},
        'Timer': {'min': 3, 'max': 10, 'default': 5},
    },
    preview='✊ Rock beats Scissors, Scissors beats Paper, Paper beats Rock')

register_game('gun_duel', GunDuelGame,
    name='Gun Duel', icon='🔫',
    description='Reload, Protect, or Shoot each turn. Last one standing wins!',
    category='Logic & Strategy',
    min_players=2, max_players=3,
    goal='Each turn choose: Reload (gain a bullet), Protect (block next shot), '
         'or Shoot (fire at opponents if you have a bullet). Strategic thinking wins!',
    difficulty_vars={
        'Health': {'min': 1, 'max': 5, 'default': 3},
    },
    preview='🔫 Tactical turn-based duel: Reload, Protect, or Shoot!')

register_game('worms', WormsBazookaGame,
    name='Worms Bazooka', icon='💥',
    description='Real-time bazooka battle on destructible terrain!',
    category='Agility & Timing',
    min_players=2, max_players=3,
    goal='Move, jump, and fire your bazooka at opponents. Destroy terrain to '
         'create cover. Last worm standing wins!',
    difficulty_vars={
        'Map Size': {'min': 1, 'max': 5, 'default': 3},
        'Explosion': {'min': 1, 'max': 5, 'default': 3},
        'Health': {'min': 1, 'max': 5, 'default': 3},
    },
    preview='💥 Real-time bazooka fight on destructible terrain! Walls crumble, '
            'bombs fly, last worm wins!')


def main():
    from engine.game_engine import GameEngine
    engine = GameEngine()
    engine.run()


if __name__ == '__main__':
    main()
