import discord

from ui.hand_select import HandSelect
from ui.game_embed import create_game_embed
from game.ai import play_ai
from ui.uno_button import UnoButton
from ui.catch_uno_button import CatchUnoButton


class DrawButton(discord.ui.Button):

    def __init__(self, game):

        super().__init__(
            label="📥 سحب ورقة",
            style=discord.ButtonStyle.primary
        )

        self.game = game

    async def callback(
        self,
        interaction
    ):

        current = self.game.current_player

        if self.game.finished:

            return await interaction.response.send_message(
                "❌ المباراة انتهت.",
                ephemeral=True
            )

        if current.is_ai:

            return await interaction.response.send_message(
                "❌ دور البوت.",
                ephemeral=True
            )

        if interaction.user.id != current.member.id:

            return await interaction.response.send_message(
                "❌ ليس دورك.",
                ephemeral=True
            )

        current.draw(
            self.game.deck,
            1
        )

        card = current.hand[-1]

        await interaction.response.send_message(
            f"📥 سحبت {card}",
            ephemeral=True
        )

        can_play = (

            card.color == self.game.current_color

            or

            card.value == self.game.current_card.value

            or

            card.color == "wild"

        )

        if not can_play:

            self.game.next_turn()

            await play_ai(
                self.game
            )

        embed, file = create_game_embed(
            self.game
        )

        await self.game.message.edit(
            embed=embed,
            attachments=[file],
            view=GameView(
                self.game
            )
        )


class GameView(discord.ui.View):

    def __init__(
        self,
        game
    ):

        super().__init__(
            timeout=None
        )

        self.game = game

        self.update_components()

    def update_components(
        self
    ):

        self.clear_items()

        self.add_item(
            UnoButton(
                self.game
            )
        )

        self.add_item(
            CatchUnoButton(
                self.game
            )
        )

        if self.game.finished:
            return

        current = self.game.current_player

        if not current.is_ai:

            self.add_item(
                HandSelect(
                    self.game,
                    current
                )
            )

            self.add_item(
                DrawButton(
                    self.game
                )
            )

    async def refresh(
        self
    ):

        self.update_components()

        if self.game.message:

            embed, file = create_game_embed(
                self.game
            )

            await self.game.message.edit(
                embed=embed,
                attachments=[file],
                view=self
            )

    async def interaction_check(
        self,
        interaction
    ):

        if self.game.finished:

            await interaction.response.send_message(
                "❌ المباراة انتهت.",
                ephemeral=True
            )

            return False

        current = self.game.current_player

        if current.is_ai:

            await interaction.response.send_message(
                "❌ دور البوت حالياً.",
                ephemeral=True
            )

            return False

        if interaction.user.id != current.member.id:

            await interaction.response.send_message(
                "❌ ليس دورك.",
                ephemeral=True
            )

            return False

        return True

    async def on_timeout(
        self
    ):

        self.stop()