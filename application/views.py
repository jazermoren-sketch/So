import discord

from application.session import TestSession
from application.storage import load_config


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
        config = load_config()

        rejected_role_id = config.get("rejected_role")

        if rejected_role_id:
            rejected_role = (
                interaction.guild.get_role(rejected_role_id)
                if interaction.guild
                else None
            )

            if rejected_role and rejected_role in interaction.user.roles:
                return await interaction.response.send_message(
                    "❌ أنت مرفوض من التقديم للإدارة.",
                    ephemeral=True
                )

        try:
            await interaction.user.send(
                "📨 سيتم إرسال الأسئلة في الخاص."
            )
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
