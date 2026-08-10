import discord


class LobbyView(discord.ui.View):

    def __init__(self, host):
        super().__init__(timeout=None)

        self.host = host
        self.players = [host]
        self.locked = False
        self.seconds = 30
        self.message = None

    def make_embed(self):
        embed = discord.Embed(
            title="🎮 غرفة UNO",
            description=(
                "✅ اضغط للدخول\n"
                "❌ اضغط للخروج"
            ),
            color=0xFFD700
        )

        embed.add_field(
            name="👥 اللاعبون",
            value="\n".join(
                p.mention
                for p in self.players
            ),
            inline=False
        )

        embed.add_field(
            name="👑 صاحب الغرفة",
            value=self.host.mention,
            inline=False
        )

        embed.add_field(
            name="📊 العدد",
            value=f"{len(self.players)}/8",
            inline=False
        )

        embed.set_footer(
            text=f"⏳ {self.seconds} ثانية"
        )

        return embed

    @discord.ui.button(
        label="دخول",
        emoji="✅",
        style=discord.ButtonStyle.success
    )
    async def join(
        self,
        interaction,
        button
    ):

        await interaction.response.defer(
            ephemeral=True
        )

        if self.locked:
            return await interaction.followup.send(
                "🔒 اللوبي مقفل",
                ephemeral=True
            )

        if interaction.user not in self.players:
            self.players.append(
                interaction.user
            )

            await self.message.edit(
                embed=self.make_embed(),
                view=self
            )

    @discord.ui.button(
        label="خروج",
        emoji="❌",
        style=discord.ButtonStyle.danger
    )
    async def leave(
        self,
        interaction,
        button
    ):

        await interaction.response.defer(
            ephemeral=True
        )

        if interaction.user == self.host:
            return

        if interaction.user in self.players:
            self.players.remove(
                interaction.user
            )

            await self.message.edit(
                embed=self.make_embed(),
                view=self
            )