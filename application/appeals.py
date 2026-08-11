import discord
import time
from discord.ui import Modal, TextInput
from application.storage import load_config, load_applications, save_application

class AppealModal(Modal, title="📨 تقديم اعتراض"):
    message=TextInput(label="سبب الاعتراض",style=discord.TextStyle.paragraph,min_length=10,max_length=1000,required=True)
    def __init__(self,guild_id): super().__init__(); self.guild_id=str(guild_id)
    async def on_submit(self,interaction:discord.Interaction):
        config=load_config(self.guild_id)
        if not config.get("appeals_enabled",True): return await interaction.response.send_message("❌ نظام الاعتراضات غير مفعّل.",ephemeral=True)
        app=load_applications(self.guild_id).get(str(interaction.user.id))
        if not app or app.get("status")!="rejected": return await interaction.response.send_message("❌ لا يوجد طلب مرفوض يمكن الاعتراض عليه.",ephemeral=True)
        limit=max(1,int(config.get("appeal_limit",1)))
        if int(app.get("appeal_count",0))>=limit: return await interaction.response.send_message(f"❌ استنفدت الحد الأقصى للاعتراضات ({limit}).",ephemeral=True)
        submitted_at=float(app.get("appeal_submitted_at",0) or 0); cooldown=max(0,int(config.get("appeal_cooldown_hours",168)))*3600
        if submitted_at and cooldown and time.time()-submitted_at<cooldown: return await interaction.response.send_message("⏳ لم تنتهِ مدة انتظار الاعتراض التالي.",ephemeral=True)
        channel_id=config.get("appeal_channel"); channel=interaction.guild.get_channel(channel_id) if interaction.guild and channel_id else None
        if channel is None: return await interaction.response.send_message("❌ لم تحدد الإدارة روم الاعتراضات بعد.",ephemeral=True)
        embed=discord.Embed(title="📨 اعتراض على طلب تقديم",color=0xF1C40F); embed.add_field(name="👤 المتقدم",value=interaction.user.mention,inline=False); embed.add_field(name="📊 التقييم",value=f"{app.get('score','غير محدد')}",inline=True); embed.add_field(name="📝 سبب الرفض",value=app.get("reason") or "غير محدد",inline=False); embed.add_field(name="📨 الاعتراض",value=str(self.message),inline=False)
        msg=await channel.send(embed=embed)
        save_application(self.guild_id,interaction.user.id,{**app,"appeal_submitted":True,"appeal_message_id":msg.id,"appeal_reason":str(self.message),"appeal_submitted_at":time.time(),"appeal_count":int(app.get("appeal_count",0))+1})
        await interaction.response.send_message("✅ تم إرسال اعتراضك للإدارة.",ephemeral=True)

class AppealView(discord.ui.View):
    def __init__(self,user_id,guild_id): super().__init__(timeout=86400); self.user_id=user_id; self.guild_id=str(guild_id)
    @discord.ui.button(label="📨 تقديم اعتراض",style=discord.ButtonStyle.primary)
    async def appeal(self,interaction:discord.Interaction,button):
        if interaction.user.id!=self.user_id: return await interaction.response.send_message("❌ هذا الزر ليس موجهاً لك.",ephemeral=True)
        await interaction.response.send_modal(AppealModal(self.guild_id))
