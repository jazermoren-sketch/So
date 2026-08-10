import uuid
from game.core.session import GameSession
from game.core.registry import get_game


class GamePlatform:

    def __init__(self):
        self.queue = []
        self.sessions = {}

    def add_to_queue(self, user):
        if user not in self.queue:
            self.queue.append(user)

    def remove_from_queue(self, user):
        if user in self.queue:
            self.queue.remove(user)

    def create_session(self, game_name, players):

        engine_class = get_game(game_name)
        engine = engine_class()

        session_id = str(uuid.uuid4())

        session = GameSession(session_id, players, engine)

        self.sessions[session_id] = session

        return session