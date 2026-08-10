class Tournament:

    def __init__(
        self,
        players
    ):

        self.players = players

    async def start(
        self
    ):

        while (
            len(
                self.players
            ) > 1
        ):

            pass
            class Tournament:

    def __init__(
        self,
        players
    ):

        self.players = players

    async def start(
        self
    ):

        while (
            len(
                self.players
            ) > 1
        ):

            winners = []

            for i in range(
                0,
                len(self.players),
                2
            ):

                winners.append(
                    self.players[i]
                )

            self.players = winners

        return self.players[0]