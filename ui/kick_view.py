import discord


class KickSelect(
    discord.ui.Select
):

    def __init__(
        self,
        lobby
    ):

        self.lobby = lobby

        options = []

        for player in lobby.players:

            if player != lobby.host:

                options.append(
                    discord.SelectOption(
                        label=str(player),
                        value=str(
                            player.id
                        )
                    )
                )

        super().__init__(
            placeholder=
            "اختر لاعب",
            options=options
        )

    async def callback(
        self,
        interaction
    ):

        uid = int(
            self.values[0]
        )

        for p in self.lobby.players:

            if p.id == uid:

                self.lobby.players.remove(
                    p
                )

                break

        await interaction.response.send_message(
            "👢 تم الطرد.",
            ephemeral=True
        )