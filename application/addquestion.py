import discord
from discord import app_commands

from application.manager import StageManager


class AddQuestion:

    def __init__(self, bot):
        self.bot = bot

    def register(self):

        @self.bot.tree.command(
            name="addquestion",
            description="إضافة سؤال إلى مرحلة"
        )
        @app_commands.checks.has_permissions(
            administrator=True
        )
        async def addquestion(
            interaction: discord.Interaction,
            stage: str,
            question: str
        ):

            if not StageManager.stage_exists(stage):

                return await interaction.response.send_message(
                    "❌ هذه المرحلة غير موجودة.",
                    ephemeral=True
                )

            StageManager.add_question(
                stage,
                question
            )

            total = len(
                StageManager.get_questions(stage)
            )

            embed = discord.Embed(
                title="✅ تم إضافة السؤال",
                color=0x2ECC71
            )

            embed.add_field(
                name="المرحلة",
                value=stage,
                inline=False
            )

            embed.add_field(
                name="السؤال",
                value=question,
                inline=False
            )

            embed.add_field(
                name="عدد الأسئلة",
                value=str(total),
                inline=False
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

        @addquestion.error
        async def addquestion_error(
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