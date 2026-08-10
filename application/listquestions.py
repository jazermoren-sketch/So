import discord
from discord import app_commands

from application.manager import StageManager


class ListQuestions:

    def __init__(self, bot):
        self.bot = bot

    def register(self):

        @self.bot.tree.command(
            name="listquestions",
            description="عرض جميع أسئلة مرحلة"
        )
        @app_commands.checks.has_permissions(
            administrator=True
        )
        async def listquestions(
            interaction: discord.Interaction,
            stage: str
        ):

            if not StageManager.stage_exists(stage):

                return await interaction.response.send_message(
                    "❌ المرحلة غير موجودة.",
                    ephemeral=True
                )

            questions = StageManager.get_questions(stage)

            if not questions:

                return await interaction.response.send_message(
                    "❌ لا توجد أسئلة في هذه المرحلة.",
                    ephemeral=True
                )

            embed = discord.Embed(
                title=f"📋 أسئلة {stage}",
                color=discord.Color.blurple()
            )

            text = ""

            for index, question in enumerate(
                questions,
                start=1
            ):

                text += (
                    f"**{index}.** {question}\n\n"
                )

            if len(text) <= 4000:

                embed.description = text

                await interaction.response.send_message(
                    embed=embed,
                    ephemeral=True
                )

                return

            pages = []

            current = ""

            for index, question in enumerate(
                questions,
                start=1
            ):

                line = f"**{index}.** {question}\n\n"

                if len(current) + len(line) > 4000:

                    pages.append(current)

                    current = line

                else:

                    current += line

            if current:

                pages.append(current)

            await interaction.response.send_message(
                embed=discord.Embed(
                    title=f"📋 أسئلة {stage}",
                    description=pages[0],
                    color=discord.Color.blurple()
                ),
                ephemeral=True
            )

            for page in pages[1:]:

                await interaction.followup.send(
                    embed=discord.Embed(
                        description=page,
                        color=discord.Color.blurple()
                    ),
                    ephemeral=True
                )

        @listquestions.error
        async def listquestions_error(
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