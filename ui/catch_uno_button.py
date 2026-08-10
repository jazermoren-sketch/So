import discord


class CatchUnoButton(discord.ui.Button):

    def __init__(self, game):

        super().__init__(
            label="راح تاكل بطاقتين اذا ما قلت اونو",
            emoji="🚨",
            style=discord.ButtonStyle.danger
        )

        self.game = game

    async def callback(
        self,
        interaction
    ):

        target = None

        for p in self.game.players:

            if len(p.hand) == 1 and not p.said_uno:
                target = p
                break

        if target is None:

            return await interaction.response.send_message(
                "❌ لا يوجد لاعب يمكن معاقبته.",
                ephemeral=True
            )

        target.draw(
            self.game.deck,
            2
        )

        target.said_uno = True

        name = (
            target.name
            if target.is_ai
            else target.member.mention
        )

        await interaction.response.send_message(
            f"🚨 تم الإمساك بـ {name} (+2)",
            ephemeral=False
        )