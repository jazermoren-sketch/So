import discord


class WildView(discord.ui.View):

    def __init__(
        self,
        game,
        callback
    ):

        super().__init__(
            timeout=20
        )

        self.game = game
        self.callback = callback
        self.used = False

    async def disable_all(
        self
    ):

        for item in self.children:
            item.disabled = True

    async def choose(
        self,
        interaction,
        color
    ):

        # منع الاختيار مرتين
        if self.used:

            return await interaction.response.send_message(
                "❌ تم اختيار اللون بالفعل.",
                ephemeral=True
            )

        self.used = True

        await self.disable_all()

        await interaction.response.defer()

        try:

            await self.callback(
                interaction,
                color
            )

        finally:

            self.stop()

    # 🔴
    @discord.ui.button(
        label="🔴",
        style=discord.ButtonStyle.danger
    )
    async def red(
        self,
        interaction,
        button
    ):

        await self.choose(
            interaction,
            "red"
        )

    # 🟢
    @discord.ui.button(
        label="🟢",
        style=discord.ButtonStyle.success
    )
    async def green(
        self,
        interaction,
        button
    ):

        await self.choose(
            interaction,
            "green"
        )

    # 🔵
    @discord.ui.button(
        label="🔵",
        style=discord.ButtonStyle.primary
    )
    async def blue(
        self,
        interaction,
        button
    ):

        await self.choose(
            interaction,
            "blue"
        )

    # 🟡
    @discord.ui.button(
        label="🟡",
        style=discord.ButtonStyle.secondary
    )
    async def yellow(
        self,
        interaction,
        button
    ):

        await self.choose(
            interaction,
            "yellow"
        )

    async def on_timeout(
        self
    ):

        await self.disable_all()

        self.stop()