import discord
from application.session import TestSession
from application.storage import load_config


class StartApplicationView(discord.ui.View):
    def __init__(self, stage_name, guild_id):
        super().__init__(timeout=None); self.stage_name=stage_name; self.guild_id=str(guild_id)

    @discord.ui.button(label="▶ ابدأ", style=discord.ButtonStyle.success, emoji="📝")
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        config=load_config(self.guild_id); rejected_role_id=config.get("rejected_role")
        if rejected_role_id and interaction.guild:
            rejected_role=interaction.guild.get_role(rejected_role_id)
            if rejected_role and rejected_role in interaction.user.roles:
                return await interaction.response.send_message("❌ أنت مرفوض من التقديم للإدارة.", ephemeral=True)
        try: await interaction.user.send("📨 سيتم إرسال الأسئلة في الخاص.")
        except discord.Forbidden: return await interaction.response.send_message("❌ افتح الرسائل الخاصة (DM) ثم أعد المحاولة.", ephemeral=True)
        await TestSession(interaction,self.stage_name,self.guild_id).start()
