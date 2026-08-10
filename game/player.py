class Player:

    def __init__(self, member):
        self.member = member
        self.hand = []
        self.said_uno = False
        self.uno_timer = None
        self.is_ai = False

    def draw(self, deck, amount=1):
        for _ in range(amount):
            self.hand.append(deck.draw())

    def remove(self, index):
        return self.hand.pop(index)


class AIPlayer:

    def __init__(self, name):
        self.name = name
        self.hand = []
        self.said_uno = False
        self.uno_timer = None
        self.is_ai = True

    def draw(self, deck, amount=1):
        for _ in range(amount):
            self.hand.append(deck.draw())

    @property
    def member(self):
        return self

    @property
    def mention(self):
        return self.name

    @property
    def id(self):
        return -1

    def __str__(self):
        return self.name