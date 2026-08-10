import discord

from application.session import TestSession


class StartApplicationView(discord.ui.View):

    def __init__(self, stage_name):
        super().__init__(timeout=None)
        self.stage_name = stage_name

    @discord.ui.button(
        label="▶ ابدأ",
        style=discord.ButtonStyle.success,
        emoji="📝"
    )
    async def start_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        try:
            await interaction.user.send("📨 سيتم إرسال الأسئلة في الخاص.")
        except discord.Forbidden:
            return await interaction.response.send_message(
                "❌ افتح الرسائل الخاصة (DM) ثم أعد المحاولة.",
                ephemeral=True
            )

        session = TestSession(
            interaction,
            self.stage_name
        )

        await session.start()