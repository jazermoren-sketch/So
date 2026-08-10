import discord
from discord import app_commands

from application.manager import StageManager


class EditQuestion:

    def __init__(self, bot):
        self.bot = bot

    def register(self):

        @self.bot.tree.command(
            name="editquestion",
            description="تعديل سؤال في مرحلة"
        )
        @app_commands.checks.has_permissions(
            administrator=True
        )
        async def editquestion(
            interaction: discord.Interaction,
            stage: str,
            number: int,
            question: str
        ):

            if not StageManager.stage_exists(stage):

                return await interaction.response.send_message(
                    "❌ المرحلة غير موجودة.",
                    ephemeral=True
                )

            success = StageManager.edit_question(
                stage,
                number - 1,
                question
            )

            if not success:

                return await interaction.response.send_message(
                    "❌ رقم السؤال غير صحيح.",
                    ephemeral=True
                )

            embed = discord.Embed(
                title="✏️ تم تعديل السؤال",
                color=0xF1C40F
            )

            embed.add_field(
                name="المرحلة",
                value=stage,
                inline=False
            )

            embed.add_field(
                name="رقم السؤال",
                value=str(number),
                inline=True
            )

            embed.add_field(
                name="السؤال الجديد",
                value=question,
                inline=False
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

        @editquestion.error
        async def editquestion_error(
            interaction: discord.Interaction,
            error
        ):

            if isinstance(
                error,
                app_commands.MissingPermissions
            ):

                if interaction.response.is_done():

                    await interaction.followup.send(
                        "❌ هذا الأمر للإدارة فقط.",
                        ephemeral=True
                    )

                else:

                    await interaction.response.send_message(
                        "❌ هذا الأمر للإدارة فقط.",
                        ephemeral=True
                    )