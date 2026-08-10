import discord
from discord import app_commands
from discord.ui import View
from application.manager import StageManager
from application.storage import load_config, save_config, load_applications


class ApplicationConfigView(View):
    def __init__(self): super().__init__(timeout=300); self.config=load_config()
    def build_embed(self):
        cfg=self.config
        def s(k): return "🟢 مفعّل" if cfg.get(k,False) else "🔴 معطّل"
        embed=discord.Embed(title="⚙️ إعدادات نظام التقديم",description="إعدادات التقديم والاختبار والمراجعة.",color=0x5865F2)
        for name,key in [("🔒 المكرر","prevent_duplicate"),("🔄 إعادة التقديم","allow_reapply"),("📊 الحالات","application_status"),("🧪 النجاح/الرسوب","test_pass_fail"),("⏱️ Timer","test_timer"),("🔢 المحاولات","test_attempts_enabled"),("🎲 عشوائي","random_questions"),("📢 Logs","application_logs"),("🔔 DM","application_dm_notifications"),("⭐ التقييم","scoring_enabled"),("📝 تقييم الأسئلة","question_scoring"),("👥 تصويت المراجعين","reviewer_voting"),("📨 الاعتراضات","appeals_enabled")]: embed.add_field(name=name,value=s(key),inline=True)
        embed.add_field(name="🎯 الاختبار",value=f"أسئلة: **{cfg.get('test_questions',10)}** | نجاح: **{cfg.get('test_pass_percent',70)}%** | وقت: **{cfg.get('test_timer_minutes',10)} د** | محاولات: **{cfg.get('test_attempts',1)}**",inline=False)
        embed.add_field(name="⭐ التقييم",value=f"**{cfg.get('score_min',5)}/{cfg.get('score_max',10)}** حد أدنى",inline=True)
        embed.add_field(name="👥 التصويت",value=f"الموافقات المطلوبة: **{cfg.get('required_approvals',1)}**",inline=True)
        embed.add_field(name="📢 النتائج",value=f"<#{cfg['result_channel']}>" if cfg.get('result_channel') else "غير محدد",inline=True)
        embed.add_field(name="📨 الاعتراضات",value=f"<#{cfg['appeal_channel']}>" if cfg.get('appeal_channel') else "غير محدد",inline=True)
        return embed
    async def toggle(self,interaction,key):
        self.config[key]=not self.config.get(key,False); save_config(self.config); await interaction.response.edit_message(embed=self.build_embed(),view=self)
    @discord.ui.button(label="🔒 المكرر",style=discord.ButtonStyle.secondary,row=0)
    async def duplicate(self,i,b): await self.toggle(i,"prevent_duplicate")
    @discord.ui.button(label="🔄 إعادة",style=discord.ButtonStyle.secondary,row=0)
    async def reapply(self,i,b): await self.toggle(i,"allow_reapply")
    @discord.ui.button(label="📊 الحالات",style=discord.ButtonStyle.secondary,row=0)
    async def statuses(self,i,b): await self.toggle(i,"application_status")
    @discord.ui.button(label="🧪 النجاح",style=discord.ButtonStyle.secondary,row=1)
    async def pass_fail(self,i,b): await self.toggle(i,"test_pass_fail")
    @discord.ui.button(label="⏱️ Timer",style=discord.ButtonStyle.secondary,row=1)
    async def timer(self,i,b): await self.toggle(i,"test_timer")
    @discord.ui.button(label="🔢 المحاولات",style=discord.ButtonStyle.secondary,row=1)
    async def attempts(self,i,b): await self.toggle(i,"test_attempts_enabled")
    @discord.ui.button(label="🎲 عشوائي",style=discord.ButtonStyle.secondary,row=2)
    async def random(self,i,b): await self.toggle(i,"random_questions")
    @discord.ui.button(label="📢 Logs",style=discord.ButtonStyle.secondary,row=2)
    async def logs(self,i,b): await self.toggle(i,"application_logs")
    @discord.ui.button(label="🔔 DM",style=discord.ButtonStyle.secondary,row=2)
    async def dm(self,i,b): await self.toggle(i,"application_dm_notifications")
    @discord.ui.button(label="⭐ التقييم",style=discord.ButtonStyle.secondary,row=3)
    async def scoring(self,i,b): await self.toggle(i,"scoring_enabled")
    @discord.ui.button(label="📝 تقييم الأسئلة",style=discord.ButtonStyle.secondary,row=3)
    async def question_scoring(self,i,b): await self.toggle(i,"question_scoring")
    @discord.ui.button(label="👥 تصويت",style=discord.ButtonStyle.secondary,row=4)
    async def voting(self,i,b): await self.toggle(i,"reviewer_voting")
    @discord.ui.button(label="📨 اعتراضات",style=discord.ButtonStyle.secondary,row=4)
    async def appeals(self,i,b): await self.toggle(i,"appeals_enabled")


class ApplicationCommands:
    def __init__(self,bot): self.bot=bot
    def register(self):
        @self.bot.tree.command(name="setreviewchannel",description="تحديد روم مراجعة الطلبات")
        @app_commands.checks.has_permissions(administrator=True)
        async def setreviewchannel(interaction,channel:discord.TextChannel):
            c=load_config(); c["review_channel"]=channel.id; save_config(c); await interaction.response.send_message(f"✅ تم تحديد {channel.mention} كروم المراجعة.",ephemeral=True)

        @self.bot.tree.command(name="setresultchannel",description="تحديد روم نتائج التقديم")
        @app_commands.checks.has_permissions(administrator=True)
        async def setresultchannel(interaction,channel:discord.TextChannel|None=None):
            c=load_config(); c["result_channel"]=channel.id if channel else None; save_config(c); await interaction.response.send_message(f"{'✅ تم تحديد '+channel.mention if channel else '🗑️ تم إلغاء روم النتائج.'}",ephemeral=True)

        @self.bot.tree.command(name="setappealchannel",description="تحديد روم الاعتراضات")
        @app_commands.checks.has_permissions(administrator=True)
        async def setappealchannel(interaction,channel:discord.TextChannel|None=None):
            c=load_config(); c["appeal_channel"]=channel.id if channel else None; save_config(c); await interaction.response.send_message(f"{'✅ تم تحديد '+channel.mention+' كروم الاعتراضات.' if channel else '🗑️ تم إلغاء روم الاعتراضات.'}",ephemeral=True)

        @self.bot.tree.command(name="setscore",description="تحديد التقييم والحد الأدنى للقبول")
        @app_commands.checks.has_permissions(administrator=True)
        async def setscore(interaction,score_max:app_commands.Range[int,1,100],score_min:app_commands.Range[int,0,100]):
            if score_min>score_max: return await interaction.response.send_message("❌ الحد الأدنى أكبر من التقييم الأقصى.",ephemeral=True)
            c=load_config(); c.update({"score_max":score_max,"score_min":score_min}); save_config(c); await interaction.response.send_message(f"✅ **{score_min}/{score_max}** هو الحد الأدنى للقبول.",ephemeral=True)

        @self.bot.tree.command(name="setreviewvotes",description="تحديد عدد الموافقات المطلوبة")
        @app_commands.checks.has_permissions(administrator=True)
        async def setreviewvotes(interaction,approvals:app_commands.Range[int,1,20]):
            c=load_config(); c["required_approvals"]=approvals; save_config(c); await interaction.response.send_message(f"✅ عدد الموافقات المطلوبة: **{approvals}**.",ephemeral=True)

        @self.bot.tree.command(name="setreapplycooldown",description="تحديد مدة انتظار إعادة التقديم بالساعات")
        @app_commands.checks.has_permissions(administrator=True)
        async def setreapplycooldown(interaction,hours:app_commands.Range[int,0,720]):
            c=load_config(); c["reapply_cooldown_hours"]=hours; save_config(c); await interaction.response.send_message(f"✅ مدة الانتظار: **{hours} ساعة**.",ephemeral=True)

        @self.bot.tree.command(name="setappealsettings",description="إعدادات الاعتراض")
        @app_commands.checks.has_permissions(administrator=True)
        async def setappealsettings(interaction,cooldown_hours:app_commands.Range[int,1,720],limit:app_commands.Range[int,1,10]):
            c=load_config(); c.update({"appeal_cooldown_hours":cooldown_hours,"appeal_limit":limit}); save_config(c); await interaction.response.send_message(f"✅ الاعتراض: كل **{cooldown_hours} ساعة**، والحد **{limit}**.",ephemeral=True)

        @self.bot.tree.command(name="createstage",description="إنشاء مرحلة جديدة")
        @app_commands.checks.has_permissions(administrator=True)
        async def createstage(interaction,name:str): await interaction.response.send_message(f"✅ تم إنشاء المرحلة **{name}**" if StageManager.create_stage(name) else "❌ المرحلة موجودة مسبقاً.",ephemeral=True)
        @self.bot.tree.command(name="deletestage",description="حذف مرحلة")
        @app_commands.checks.has_permissions(administrator=True)
        async def deletestage(interaction,name:str): await interaction.response.send_message(f"🗑️ تم حذف المرحلة **{name}**" if StageManager.delete_stage(name) else "❌ المرحلة غير موجودة.",ephemeral=True)
        @self.bot.tree.command(name="liststages",description="عرض المراحل")
        @app_commands.checks.has_permissions(administrator=True)
        async def liststages(interaction):
            stages=StageManager.list_stages()
            if not stages: return await interaction.response.send_message("لا توجد مراحل.",ephemeral=True)
            e=discord.Embed(title="📋 المراحل",color=0x2ECC71)
            for stage,data in stages.items(): e.add_field(name=stage,value=f"الأسئلة: {len(data['questions'])}",inline=False)
            await interaction.response.send_message(embed=e,ephemeral=True)

        @self.bot.tree.command(name="setreviewer",description="إضافة مراجع")
        @app_commands.checks.has_permissions(administrator=True)
        async def setreviewer(interaction,member:discord.Member):
            c=load_config(); c["reviewer"]=member.id; c.setdefault("reviewers",[])
            if member.id not in c["reviewers"]: c["reviewers"].append(member.id)
            save_config(c); await interaction.response.send_message(f"✅ تمت إضافة {member.mention}.",ephemeral=True)
        @self.bot.tree.command(name="removereviewer",description="إزالة مراجع")
        @app_commands.checks.has_permissions(administrator=True)
        async def removereviewer(interaction,member:discord.Member):
            c=load_config(); c["reviewers"]=[x for x in c.get("reviewers",[]) if x!=member.id]
            if c.get("reviewer")==member.id: c["reviewer"]=c["reviewers"][0] if c["reviewers"] else None
            save_config(c); await interaction.response.send_message(f"🗑️ تمت إزالة {member.mention}.",ephemeral=True)

        @self.bot.tree.command(name="setacceptedrole",description="تحديد رتبة المقبولين")
        @app_commands.checks.has_permissions(administrator=True)
        async def setacceptedrole(interaction,role:discord.Role|None=None):
            c=load_config(); c["accepted_role"]=role.id if role else None; save_config(c); await interaction.response.send_message("✅ تم تحديث رتبة القبول." if role else "🗑️ تم إلغاء رتبة القبول.",ephemeral=True)
        @self.bot.tree.command(name="setrejectedrole",description="تحديد رتبة المرفوضين")
        @app_commands.checks.has_permissions(administrator=True)
        async def setrejectedrole(interaction,role:discord.Role|None=None):
            c=load_config(); c["rejected_role"]=role.id if role else None; save_config(c); await interaction.response.send_message("✅ تم تحديث رتبة الرفض." if role else "🗑️ تم إلغاء رتبة الرفض.",ephemeral=True)

        @self.bot.tree.command(name="configureapplications",description="فتح لوحة إعدادات التقديم")
        @app_commands.checks.has_permissions(administrator=True)
        @app_commands.describe(hidden="إخفاء لوحة الإعدادات")
        async def configureapplications(interaction,hidden:bool=False):
            view=ApplicationConfigView(); await interaction.response.send_message(embed=view.build_embed(),view=view,ephemeral=hidden)

        @self.bot.tree.command(name="settestsettings",description="إعدادات الاختبار")
        @app_commands.checks.has_permissions(administrator=True)
        async def settestsettings(interaction,questions:app_commands.Range[int,1,100],pass_percent:app_commands.Range[int,1,100],timer_minutes:app_commands.Range[int,1,180],attempts:app_commands.Range[int,1,20]):
            c=load_config(); c.update({"test_questions":questions,"test_pass_percent":pass_percent,"test_timer_minutes":timer_minutes,"test_attempts":attempts}); save_config(c); await interaction.response.send_message("✅ تم حفظ إعدادات الاختبار.",ephemeral=True)

        @self.bot.tree.command(name="applicationstats",description="إحصائيات التقديم")
        @app_commands.checks.has_permissions(administrator=True)
        async def applicationstats(interaction):
            apps=load_applications(); total=len(apps); accepted=sum(str(x.get("status")) in ("accepted","مقبول","approved") for x in apps.values()); rejected=sum(str(x.get("status")) in ("rejected","مرفوض","denied") for x in apps.values())
            e=discord.Embed(title="📊 إحصائيات التقديم",color=0x5865F2); e.add_field(name="📋 الإجمالي",value=str(total),inline=True); e.add_field(name="⏳ قيد المراجعة",value=str(total-accepted-rejected),inline=True); e.add_field(name="✅ مقبول",value=str(accepted),inline=True); e.add_field(name="❌ مرفوض",value=str(rejected),inline=True); await interaction.response.send_message(embed=e,ephemeral=True)

        async def permission_error(interaction,error):
            if isinstance(error,app_commands.MissingPermissions):
                if interaction.response.is_done(): await interaction.followup.send("❌ هذا الأمر للإدارة فقط.",ephemeral=True)
                else: await interaction.response.send_message("❌ هذا الأمر للإدارة فقط.",ephemeral=True)
        for command in list(self.bot.tree.get_commands()):
            if command.name in {"setreviewchannel","setresultchannel","setappealchannel","setscore","setreviewvotes","setreapplycooldown","setappealsettings","createstage","deletestage","liststages","setreviewer","removereviewer","setacceptedrole","setrejectedrole","configureapplications","settestsettings","applicationstats"}: command.error(permission_error)
