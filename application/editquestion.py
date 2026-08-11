import discord
from discord import app_commands
from application.manager import StageManager

class EditQuestion:
    def __init__(self, bot): self.bot=bot
    def register(self):
        @self.bot.tree.command(name="editquestion",description="تعديل سؤال في مرحلة")
        @app_commands.checks.has_permissions(administrator=True)
        async def editquestion(interaction:discord.Interaction,stage:str,number:int,question:str):
            if not StageManager.stage_exists(interaction.guild.id,stage): return await interaction.response.send_message("❌ المرحلة غير موجودة.",ephemeral=True)
            if not StageManager.edit_question(interaction.guild.id,stage,number-1,question): return await interaction.response.send_message("❌ رقم السؤال غير صحيح.",ephemeral=True)
            e=discord.Embed(title="✏️ تم تعديل السؤال",color=0xF1C40F); e.add_field(name="المرحلة",value=stage,inline=False); e.add_field(name="رقم السؤال",value=str(number),inline=True); e.add_field(name="السؤال الجديد",value=question,inline=False)
            await interaction.response.send_message(embed=e,ephemeral=True)
        @editquestion.error
        async def editquestion_error(interaction,error):
            if isinstance(error,app_commands.MissingPermissions): await interaction.response.send_message("❌ هذا الأمر للإدارة فقط.",ephemeral=True)
