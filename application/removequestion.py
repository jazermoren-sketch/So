import discord
from discord import app_commands

from application.manager import StageManager


class RemoveQuestion:

    def __init__(self, bot):
        self.bot = bot

    def register(self):

        @self.bot.tree.command(
            name="removequestion",
            description="حذف سؤال من مرحلة"
        )
        @app_commands.checks.has_permissions(
            administrator=True
        )
        async def removequestion(
            interaction: discord.Interaction,
            stage: str,
            number: int
        ):

            if not StageManager.stage_exists(stage):

                return await interaction.response.send_message(
                    "❌ المرحلة غير موجودة.",
                    ephemeral=True
                )

            success = StageManager.remove_question(
                stage,
                number - 1
            )

            if not success:

                return await interaction.response.send_message(
                    "❌ رقم السؤال غير صحيح.",
                    ephemeral=True
                )

            total = len(
                StageManager.get_questions(stage)
            )

            embed = discord.Embed(
                title="🗑️ تم حذف السؤال",
                color=discord.Color.red()
            )

            embed.add_field(
                name="المرحلة",
                value=stage,
                inline=False
            )

            embed.add_field(
                name="رقم السؤال المحذوف",
                value=str(number),
                inline=True
            )

            embed.add_field(
                name="عدد الأسئلة المتبقية",
                value=str(total),
                inline=True
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

        @removequestion.error
        async def removequestion_error(
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