import uuid
from game.core.session import GameSession
from game.core.registry import get_game


class GameHub:

    def __init__(self):
        self.queue = []
        self.sessions = {}

    def add_to_queue(self, user):
        self.queue.append(user)

    def create_game(self, game_name, players):

        engine_class = get_game(game_name)
        engine = engine_class()

        game_id = str(uuid.uuid4())

        session = GameSession(game_id, players, engine)

        self.sessions[game_id] = session

        return session