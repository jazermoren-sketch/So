import discord


class UnoButton(discord.ui.Button):

    def __init__(self, game):

        super().__init__(
            label="أونو دوس تريس هالا مدريد!",
            emoji="🔔",
            style=discord.ButtonStyle.success
        )

        self.game = game

    async def callback(
        self,
        interaction
    ):

        player = None

        for p in self.game.players:

            if p.is_ai:
                continue

            if p.member.id == interaction.user.id:
                player = p
                break

        if player is None:

            return await interaction.response.send_message(
                "❌ أنت لست لاعباً.",
                ephemeral=True
            )

        # خاص يكون عندو ورقة وحدة
        if len(player.hand) != 1:

            return await interaction.response.send_message(
                "❌ لا يمكنك قول UNO!",
                ephemeral=True
            )

        # سجل UNO
        player.said_uno = True

        await interaction.response.send_message(
            "✅ UNO!",
            ephemeral=True
        )

        await interaction.channel.send(
            f"🔔 {interaction.user.mention} قال UNO!"
        )