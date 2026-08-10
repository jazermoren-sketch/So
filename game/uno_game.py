from game.deck import Deck
from game.player import Player, AIPlayer


class UnoGame:

    def __init__(self, members, host=None):

        self.host = host

        self.deck = Deck()

        self.players = []

        # اللاعبين الحقيقيين
        for member in members:

            player = Player(member)

            player.draw(
                self.deck,
                7
            )

            self.players.append(
                player
            )

        # إضافة AI
        for i in range(3):

            ai = AIPlayer(
                f"🤖 AI {i + 1}"
            )

            ai.draw(
                self.deck,
                7
            )

            self.players.append(
                ai
            )

        self.turn = 0
        self.direction = 1

        self.current_card = (
            self.deck.draw()
        )

        # منع بداية اللعبة بـ Wild
        while (
            self.current_card.color
            ==
            "wild"
        ):

            self.current_card = (
                self.deck.draw()
            )

        self.current_color = (
            self.current_card.color
        )

        self.finished = False

        self.message = None

        self.winner = None

        # مهم للـ AI
        self.ai_running = False

    @property
    def current_player(self):

        return self.players[
            self.turn
        ]

    def next_turn(self):

        self.turn = (
            self.turn
            +
            self.direction
        ) % len(
            self.players
        )

    def check_winner(self):

        for player in self.players:

            if (
                len(
                    player.hand
                )
                ==
                0
            ):

                return player

        return None

    def skip(self):

        self.next_turn()
        self.next_turn()

    def reverse(self):

        self.direction *= -1

        self.next_turn()

    def draw_two(self):

        self.next_turn()

        self.current_player.draw(
            self.deck,
            2
        )

        self.next_turn()

    def draw_four(self):

        self.next_turn()

        self.current_player.draw(
            self.deck,
            4
        )

        self.next_turn()