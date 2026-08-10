GAMES = {}

def register_game(name, engine):
    GAMES[name] = engine

def get_game(name):
    return GAMES[name]