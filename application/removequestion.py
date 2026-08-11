import discord
from discord import app_commands
from application.manager import StageManager

class RemoveQuestion:
    def __init__(self, bot): self.bot=bot
    def register(self):
        @self.bot.tree.command(name="removequestion",description="حذف سؤال من مرحلة")
        @app_commands.checks.has_permissions(administrator=True)
        async def removequestion(interaction:discord.Interaction,stage:str,number:int):
            if not StageManager.stage_exists(interaction.guild.id,stage): return await interaction.response.send_message("❌ المرحلة غير موجودة.",ephemeral=True)
            if not StageManager.remove_question(interaction.guild.id,stage,number-1): return await interaction.response.send_message("❌ رقم السؤال غير صحيح.",ephemeral=True)
            total=len(StageManager.get_questions(interaction.guild.id,stage)); e=discord.Embed(title="🗑️ تم حذف السؤال",color=discord.Color.red()); e.add_field(name="المرحلة",value=stage,inline=False); e.add_field(name="رقم السؤال المحذوف",value=str(number),inline=True); e.add_field(name="عدد الأسئلة المتبقية",value=str(total),inline=True); await interaction.response.send_message(embed=e,ephemeral=True)
        @removequestion.error
        async def removequestion_error(interaction,error):
            if isinstance(error,app_commands.MissingPermissions): await interaction.response.send_message("❌ هذا الأمر للإدارة فقط.",ephemeral=True)
