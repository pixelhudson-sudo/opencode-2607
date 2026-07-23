GAMES = {}


def register_game(game_id, game_class, name, description, category,
                  min_players=1, max_players=3, icon='🎮',
                  goal='Be the player with the highest score!',
                  difficulty_vars=None, preview=''):
    GAMES[game_id] = {
        'class': game_class,
        'name': name,
        'description': description,
        'category': category,
        'min_players': min_players,
        'max_players': max_players,
        'icon': icon,
        'goal': goal,
        'difficulty_vars': difficulty_vars or {},
        'preview': preview,
    }


def get_game_info(game_id):
    return GAMES.get(game_id)


def get_games_by_category():
    cats = {}
    for gid, info in GAMES.items():
        cat = info['category']
        if cat not in cats:
            cats[cat] = []
        cats[cat].append((gid, info))
    return cats


def get_games_list():
    return [(gid, info) for gid, info in GAMES.items()]
