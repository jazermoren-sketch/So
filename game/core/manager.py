import uuid
from game.core.game_session import GameSession
from game.core.registry import get_game


class GameManager:

    def __init__(self):
        self.lobbies = {}
        self.games = {}

    def create_game(self, game_name, players):

        engine_class = get_game(game_name)
        engine = engine_class()

        game_id = str(uuid.uuid4())

        session = GameSession(game_id, players, engine)

        self.games[game_id] = session

        return session