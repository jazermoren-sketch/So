class GameSession:

    def __init__(self, id, players, engine, club=None):

        self.id = id
        self.players = players
        self.engine = engine

        self.club = club

        self.finished = False
        self.winner = None

        self.message = None
        self.lock = False