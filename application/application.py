import discord
from discord import app_commands

from application.manager import StageManager
from application.storage import (
    load_config,
    save_config
)


class ApplicationCommands:

    def __init__(self, bot):
        self.bot = bot

    def register(self):

        # =========================
        # SET REVIEW CHANNEL
        # =========================

        @self.bot.tree.command(
            name="setreviewchannel",
            description="تحديد روم مراجعة الطلبات"
        )
        @app_commands.checks.has_permissions(administrator=True)
        async def setreviewchannel(
            interaction: discord.Interaction,
            channel: discord.TextChannel
        ):

            config = load_config()

            config["review_channel"] = channel.id

            save_config(config)

            await interaction.response.send_message(
                f"✅ تم تحديد {channel.mention} كروم مراجعة الطلبات.",
                ephemeral=True
            )

        # =========================
        # CREATE STAGE
        # =========================

        @self.bot.tree.command(
            name="createstage",
            description="إنشاء مرحلة جديدة"
        )
        @app_commands.checks.has_permissions(administrator=True)
        async def createstage(
            interaction: discord.Interaction,
            name: str
        ):

            if StageManager.create_stage(name):

                await interaction.response.send_message(
                    f"✅ تم إنشاء المرحلة **{name}**",
                    ephemeral=True
                )

            else:

                await interaction.response.send_message(
                    "❌ هذه المرحلة موجودة مسبقًا.",
                    ephemeral=True
                )
        @self.bot.tree.command(
            name="deletestage",
            description="حذف مرحلة"
        )
        @app_commands.checks.has_permissions(administrator=True)
        async def deletestage(
            interaction: discord.Interaction,
            name: str
        ):

            if StageManager.delete_stage(name):

                await interaction.response.send_message(
                    f"🗑️ تم حذف المرحلة **{name}**",
                    ephemeral=True
                )

            else:

                await interaction.response.send_message(
                    "❌ المرحلة غير موجودة.",
                    ephemeral=True
                )

        @self.bot.tree.command(
            name="liststages",
            description="عرض جميع المراحل"
        )
        @app_commands.checks.has_permissions(administrator=True)
        async def liststages(
            interaction: discord.Interaction
        ):

            stages = StageManager.list_stages()

            if not stages:

                return await interaction.response.send_message(
                    "لا توجد مراحل.",
                    ephemeral=True
                )

            embed = discord.Embed(
                title="📋 المراحل",
                color=0x2ECC71
            )

            for stage, data in stages.items():

                embed.add_field(
                    name=stage,
                    value=f"الأسئلة: {len(data['questions'])}",
                    inline=False
                )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

        @self.bot.tree.command(
            name="setreviewer",
            description="تحديد المراجع"
        )
        @app_commands.checks.has_permissions(administrator=True)
        async def setreviewer(
            interaction: discord.Interaction,
            member: discord.Member
        ):

            config = load_config()

            config["reviewer"] = member.id

            save_config(config)

            await interaction.response.send_message(
                f"✅ تم تعيين {member.mention} كمراجع.",
                ephemeral=True
            )

        @createstage.error
        @deletestage.error
        @liststages.error
        @setreviewer.error
        @setreviewchannel.error
        async def permission_error(
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