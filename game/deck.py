import random
from game.card import Card

COLORS = [
    "red",
    "green",
    "blue",
    "yellow"
]

SPECIAL = [
    "skip",
    "reverse",
    "draw2"
]


class Deck:

    def __init__(self):

        self.cards = []
        self.create()

    def create(self):

        for color in COLORS:

            self.cards.append(
                Card(color, 0)
            )

            for n in range(1, 10):

                self.cards.append(
                    Card(color, n)
                )

                self.cards.append(
                    Card(color, n)
                )

        for color in COLORS:

            for special in SPECIAL:

                self.cards.append(
                    Card(color, special)
                )

                self.cards.append(
                    Card(color, special)
                )

        for _ in range(4):

            self.cards.append(
                Card("wild", "wild")
            )

            self.cards.append(
                Card("wild", "wild4")
            )

        random.shuffle(
            self.cards
        )

    def draw(self):

        if len(self.cards) == 0:
            self.create()

        return self.cards.pop()