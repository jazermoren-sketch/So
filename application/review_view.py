import discord

from application.storage import load_config
from application.results import ResultManager


class ReviewView(discord.ui.View):

    def __init__(self, user_id: int, stage: str):
        super().__init__(timeout=None)

        self.user_id = user_id
        self.stage = stage

    async def _check_reviewer(
        self,
        interaction: discord.Interaction
    ):

        config = load_config()

        reviewer = config.get("reviewer")

        if reviewer != interaction.user.id:

            await interaction.response.send_message(
                "❌ أنت لست المراجع.",
                ephemeral=True
            )

            return False

        return True

    @discord.ui.button(
        label="قبول",
        emoji="✅",
        style=discord.ButtonStyle.success
    )
    async def accept(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not await self._check_reviewer(interaction):
            return

        for child in self.children:
            child.disabled = True

        await interaction.message.edit(
            view=self
        )

        await ResultManager.accept(
            interaction,
            self.user_id,
            self.stage
        )

        await interaction.response.send_message(
            "✅ تم قبول الطلب.",
            ephemeral=True
        )

    @discord.ui.button(
        label="رفض",
        emoji="❌",
        style=discord.ButtonStyle.danger
    )
    async def reject(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not await self._check_reviewer(interaction):
            return

        for child in self.children:
            child.disabled = True

        await interaction.message.edit(
            view=self
        )

        await ResultManager.reject(
            interaction,
            self.user_id,
            self.stage
        )

        await interaction.response.send_message(
            "❌ تم رفض الطلب.",
            ephemeral=True
        )