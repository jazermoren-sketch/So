import discord
from discord.ui import Modal, TextInput
from application.storage import load_config, load_applications, save_application


class AppealModal(Modal, title="📨 تقديم اعتراض"):
    message = TextInput(label="سبب الاعتراض", style=discord.TextStyle.paragraph, min_length=10, max_length=1000, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        config = load_config()
        if not config.get("appeals_enabled", True):
            return await interaction.response.send_message("❌ نظام الاعتراضات غير مفعّل.", ephemeral=True)
        app = load_applications().get(str(interaction.user.id))
        if not app or app.get("status") != "rejected":
            return await interaction.response.send_message("❌ لا يوجد طلب مرفوض يمكن الاعتراض عليه.", ephemeral=True)
        if app.get("appeal_submitted"):
            return await interaction.response.send_message("❌ سبق لك تقديم اعتراض لهذا الطلب.", ephemeral=True)
        channel_id = config.get("appeal_channel")
        channel = interaction.guild.get_channel(channel_id) if interaction.guild and channel_id else None
        if channel is None:
            return await interaction.response.send_message("❌ لم تحدد الإدارة روم الاعتراضات بعد.", ephemeral=True)
        embed = discord.Embed(title="📨 اعتراض على طلب تقديم", color=0xF1C40F)
        embed.add_field(name="👤 المتقدم", value=interaction.user.mention, inline=False)
        embed.add_field(name="📊 التقييم", value=f"{app.get('score', 'غير محدد')}", inline=True)
        embed.add_field(name="📝 سبب الرفض", value=app.get("reason") or "غير محدد", inline=False)
        embed.add_field(name="📨 الاعتراض", value=str(self.message), inline=False)
        msg = await channel.send(embed=embed)
        save_application(interaction.user.id, {**app, "appeal_submitted": True, "appeal_message_id": msg.id, "appeal_reason": str(self.message)})
        await interaction.response.send_message("✅ تم إرسال اعتراضك للإدارة.", ephemeral=True)


class AppealView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=86400)
        self.user_id = user_id

    @discord.ui.button(label="📨 تقديم اعتراض", style=discord.ButtonStyle.primary)
    async def appeal(self, interaction: discord.Interaction, button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ هذا الزر ليس موجهاً لك.", ephemeral=True)
        await interaction.response.send_modal(AppealModal())
