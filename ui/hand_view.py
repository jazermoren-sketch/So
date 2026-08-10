import discord
from ui.hand_select import HandSelect


class HandView(discord.ui.View):

    def __init__(self, game, player):
        super().__init__(timeout=60)

        self.game = game
        self.player = player

        if len(player.hand) > 0:
            self.add_item(
                HandSelect(
                    game,
                    player
                )
            )