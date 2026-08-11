import discord
from discord import app_commands
from application.manager import StageManager
from application.views import StartApplicationView

class SendStage:
    def __init__(self, bot): self.bot=bot
    def register(self):
        @self.bot.tree.command(name="sendstage",description="إرسال مرحلة الاختبار")
        @app_commands.checks.has_permissions(administrator=True)
        async def sendstage(interaction:discord.Interaction,stage:str):
            if not StageManager.stage_exists(interaction.guild.id,stage): return await interaction.response.send_message("❌ المرحلة غير موجودة.",ephemeral=True)
            questions=StageManager.get_questions(interaction.guild.id,stage)
            embed=discord.Embed(title=f"📋 {stage}",description=f"اضغط على الزر بالأسفل لبدء الاختبار.\n\n📌 عدد الأسئلة: **{len(questions)}**",color=0x2ECC71); embed.set_footer(text="بمجرد الضغط على ابدأ سيبدأ الاختبار.")
            await interaction.channel.send(embed=embed,view=StartApplicationView(stage,interaction.guild.id)); await interaction.response.send_message("✅ تم إرسال الاختبار.",ephemeral=True)
        @sendstage.error
        async def sendstage_error(interaction,error):
            if isinstance(error,app_commands.MissingPermissions): await interaction.response.send_message("❌ هذا الأمر للإدارة فقط.",ephemeral=True)
