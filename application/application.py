import discord
from discord import app_commands
from discord.ui import View
from application.manager import StageManager
from application.storage import load_config, save_config


class ApplicationConfigView(View):
    def __init__(self):
        super().__init__(timeout=300)
        self.config = load_config()

    def build_embed(self):
        cfg = self.config
        def s(k): return "🟢 مفعّل" if cfg.get(k, False) else "🔴 معطّل"
        embed = discord.Embed(title="⚙️ إعدادات نظام التقديم", description="اضغط على الأزرار لتفعيل أو تعطيل الأنظمة.", color=0x5865F2)
        items = [("🔒 المكرر", "prevent_duplicate"), ("🔄 إعادة التقديم", "allow_reapply"), ("📊 الحالات", "application_status"), ("🧪 النجاح/الرسوب", "test_pass_fail"), ("⏱️ Timer", "test_timer"), ("🔢 المحاولات", "test_attempts_enabled"), ("🎲 عشوائي", "random_questions"), ("📢 Logs", "application_logs"), ("🔔 DM", "application_dm_notifications"), ("📋 الشروط", "application_requirements"), ("⭐ التقييم", "scoring_enabled"), ("📝 تقييم الأسئلة", "question_scoring")]
        for name, key in items: embed.add_field(name=name, value=s(key), inline=True)
        embed.add_field(name="🎯 الاختبار", value=f"أسئلة: **{cfg.get('test_questions', 10)}** | نجاح: **{cfg.get('test_pass_percent', 70)}%** | وقت: **{cfg.get('test_timer_minutes', 10)} د** | محاولات: **{cfg.get('test_attempts', 1)}**", inline=False)
        embed.add_field(name="⭐ التقييم", value=f"النطاق: **{cfg.get('score_max', 10)}** | الحد الأدنى: **{cfg.get('score_min', 5)}**", inline=True)
        embed.add_field(name="👥 المراجعون", value=f"**{len(cfg.get('reviewers', []))}** مراجع", inline=True)
        embed.add_field(name="📢 روم النتائج", value=f"<#{cfg['result_channel']}>" if cfg.get('result_channel') else "غير محدد", inline=False)
        return embed

    async def toggle(self, interaction, key):
        self.config[key] = not self.config.get(key, False); save_config(self.config)
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="🔒 المكرر", style=discord.ButtonStyle.secondary, row=0)
    async def duplicate(self, i, b): await self.toggle(i, "prevent_duplicate")
    @discord.ui.button(label="🔄 إعادة", style=discord.ButtonStyle.secondary, row=0)
    async def reapply(self, i, b): await self.toggle(i, "allow_reapply")
    @discord.ui.button(label="📊 الحالات", style=discord.ButtonStyle.secondary, row=0)
    async def statuses(self, i, b): await self.toggle(i, "application_status")
    @discord.ui.button(label="🧪 النجاح", style=discord.ButtonStyle.secondary, row=1)
    async def pass_fail(self, i, b): await self.toggle(i, "test_pass_fail")
    @discord.ui.button(label="⏱️ Timer", style=discord.ButtonStyle.secondary, row=1)
    async def timer(self, i, b): await self.toggle(i, "test_timer")
    @discord.ui.button(label="🔢 المحاولات", style=discord.ButtonStyle.secondary, row=1)
    async def attempts(self, i, b): await self.toggle(i, "test_attempts_enabled")
    @discord.ui.button(label="🎲 عشوائي", style=discord.ButtonStyle.secondary, row=2)
    async def random(self, i, b): await self.toggle(i, "random_questions")
    @discord.ui.button(label="📢 Logs", style=discord.ButtonStyle.secondary, row=2)
    async def logs(self, i, b): await self.toggle(i, "application_logs")
    @discord.ui.button(label="🔔 DM", style=discord.ButtonStyle.secondary, row=2)
    async def dm(self, i, b): await self.toggle(i, "application_dm_notifications")
    @discord.ui.button(label="📋 الشروط", style=discord.ButtonStyle.secondary, row=3)
    async def requirements(self, i, b): await self.toggle(i, "application_requirements")
    @discord.ui.button(label="⭐ التقييم", style=discord.ButtonStyle.secondary, row=3)
    async def scoring(self, i, b): await self.toggle(i, "scoring_enabled")
    @discord.ui.button(label="📝 تقييم الأسئلة", style=discord.ButtonStyle.secondary, row=3)
    async def question_scoring(self, i, b): await self.toggle(i, "question_scoring")


class ApplicationCommands:
    def __init__(self, bot): self.bot = bot

    def register(self):
        @self.bot.tree.command(name="setreviewchannel", description="تحديد روم مراجعة الطلبات")
        @app_commands.checks.has_permissions(administrator=True)
        async def setreviewchannel(interaction: discord.Interaction, channel: discord.TextChannel):
            config=load_config(); config["review_channel"]=channel.id; save_config(config); await interaction.response.send_message(f"✅ تم تحديد {channel.mention} كروم المراجعة.", ephemeral=True)

        @self.bot.tree.command(name="setresultchannel", description="تحديد روم نتائج التقديم")
        @app_commands.checks.has_permissions(administrator=True)
        async def setresultchannel(interaction: discord.Interaction, channel: discord.TextChannel | None = None):
            config=load_config(); config["result_channel"]=channel.id if channel else None; save_config(config)
            await interaction.response.send_message(f"{'✅ تم تحديد ' + channel.mention + ' كروم النتائج.' if channel else '🗑️ تم إلغاء روم النتائج.'}", ephemeral=True)

        @self.bot.tree.command(name="setscore", description="تحديد نطاق التقييم والحد الأدنى للقبول")
        @app_commands.checks.has_permissions(administrator=True)
        async def setscore(interaction: discord.Interaction, score_max: app_commands.Range[int, 1, 100], score_min: app_commands.Range[int, 0, 100]):
            if score_min > score_max: return await interaction.response.send_message("❌ الحد الأدنى لا يمكن أن يكون أكبر من التقييم الأقصى.", ephemeral=True)
            config=load_config(); config.update({"score_max":score_max,"score_min":score_min}); save_config(config)
            await interaction.response.send_message(f"✅ التقييم من **0 إلى {score_max}** والحد الأدنى للقبول **{score_min}/{score_max}**.", ephemeral=True)

        @self.bot.tree.command(name="createstage", description="إنشاء مرحلة جديدة")
        @app_commands.checks.has_permissions(administrator=True)
        async def createstage(interaction: discord.Interaction, name: str): await interaction.response.send_message(f"✅ تم إنشاء المرحلة **{name}**" if StageManager.create_stage(name) else "❌ هذه المرحلة موجودة مسبقًا.", ephemeral=True)
        @self.bot.tree.command(name="deletestage", description="حذف مرحلة")
        @app_commands.checks.has_permissions(administrator=True)
        async def deletestage(interaction: discord.Interaction, name: str): await interaction.response.send_message(f"🗑️ تم حذف المرحلة **{name}**" if StageManager.delete_stage(name) else "❌ المرحلة غير موجودة.", ephemeral=True)
        @self.bot.tree.command(name="liststages", description="عرض جميع المراحل")
        @app_commands.checks.has_permissions(administrator=True)
        async def liststages(interaction: discord.Interaction):
            stages=StageManager.list_stages()
            if not stages: return await interaction.response.send_message("لا توجد مراحل.", ephemeral=True)
            embed=discord.Embed(title="📋 المراحل", color=0x2ECC71)
            for stage,data in stages.items(): embed.add_field(name=stage,value=f"الأسئلة: {len(data['questions'])}",inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)

        @self.bot.tree.command(name="setreviewer", description="إضافة مراجع")
        @app_commands.checks.has_permissions(administrator=True)
        async def setreviewer(interaction: discord.Interaction, member: discord.Member):
            config=load_config(); config["reviewer"]=member.id; config.setdefault("reviewers",[])
            if member.id not in config["reviewers"]: config["reviewers"].append(member.id)
            save_config(config); await interaction.response.send_message(f"✅ تمت إضافة {member.mention} كمراجع.", ephemeral=True)
        @self.bot.tree.command(name="removereviewer", description="إزالة مراجع")
        @app_commands.checks.has_permissions(administrator=True)
        async def removereviewer(interaction: discord.Interaction, member: discord.Member):
            config=load_config(); config["reviewers"]=[x for x in config.get("reviewers",[]) if x!=member.id]
            if config.get("reviewer")==member.id: config["reviewer"]=config["reviewers"][0] if config["reviewers"] else None
            save_config(config); await interaction.response.send_message(f"🗑️ تمت إزالة {member.mention} من المراجعين.", ephemeral=True)

        @self.bot.tree.command(name="setacceptedrole", description="تحديد رتبة المقبولين")
        @app_commands.checks.has_permissions(administrator=True)
        async def setacceptedrole(interaction: discord.Interaction, role: discord.Role | None = None):
            config=load_config(); config["accepted_role"]=role.id if role else None; save_config(config); await interaction.response.send_message(f"{'✅ تم تحديد '+role.mention if role else '🗑️ تم إلغاء رتبة القبول.'}", ephemeral=True)
        @self.bot.tree.command(name="setrejectedrole", description="تحديد رتبة المرفوضين")
        @app_commands.checks.has_permissions(administrator=True)
        async def setrejectedrole(interaction: discord.Interaction, role: discord.Role | None = None):
            config=load_config(); config["rejected_role"]=role.id if role else None; save_config(config); await interaction.response.send_message(f"{'✅ تم تحديد '+role.mention if role else '🗑️ تم إلغاء رتبة الرفض.'}", ephemeral=True)

        @self.bot.tree.command(name="configureapplications", description="فتح لوحة إعدادات التقديم")
        @app_commands.checks.has_permissions(administrator=True)
        @app_commands.describe(hidden="إخفاء لوحة الإعدادات")
        async def configureapplications(interaction: discord.Interaction, hidden: bool=False):
            view=ApplicationConfigView(); await interaction.response.send_message(embed=view.build_embed(),view=view,ephemeral=hidden)

        @self.bot.tree.command(name="settestsettings", description="إعدادات الاختبار")
        @app_commands.checks.has_permissions(administrator=True)
        async def settestsettings(interaction: discord.Interaction, questions: app_commands.Range[int,1,100], pass_percent: app_commands.Range[int,1,100], timer_minutes: app_commands.Range[int,1,180], attempts: app_commands.Range[int,1,20]):
            config=load_config(); config.update({"test_questions":questions,"test_pass_percent":pass_percent,"timer_minutes":timer_minutes,"test_timer_minutes":timer_minutes,"test_attempts":attempts}); save_config(config); await interaction.response.send_message("✅ تم حفظ إعدادات الاختبار.",ephemeral=True)

        @app_commands.command
        async def _dummy(): pass

        @self.bot.tree.command(name="applicationstats", description="إحصائيات التقديم")
        @app_commands.checks.has_permissions(administrator=True)
        async def applicationstats(interaction: discord.Interaction):
            from application.storage import load_applications
            apps=load_applications(); total=len(apps); statuses={"pending":0,"accepted":0,"rejected":0}
            for d in apps.values():
                st=str(d.get("status","pending")).lower();
                if st in ("accepted","مقبول","approved"): statuses["accepted"]+=1
                elif st in ("rejected","مرفوض","denied"): statuses["rejected"]+=1
                else: statuses["pending"]+=1
            embed=discord.Embed(title="📊 إحصائيات التقديم",color=0x5865F2)
            for n,k in [("📋 الإجمالي",None),("⏳ قيد المراجعة","pending"),("✅ مقبول","accepted"),("❌ مرفوض","rejected")]: embed.add_field(name=n,value=str(total if k is None else statuses[k]),inline=True)
            await interaction.response.send_message(embed=embed,ephemeral=True)

        @createstage.error
        @deletestage.error
        @liststages.error
        @setreviewer.error
        @removereviewer.error
        @setreviewchannel.error
        @setresultchannel.error
        @setscore.error
        @setacceptedrole.error
        @setrejectedrole.error
        @configureapplications.error
        @settestsettings.error
        @applicationstats.error
        async def permission_error(interaction: discord.Interaction,error):
            if isinstance(error,app_commands.MissingPermissions):
                msg="❌ هذا الأمر للإدارة فقط."
                if interaction.response.is_done(): await interaction.followup.send(msg,ephemeral=True)
                else: await interaction.response.send_message(msg,ephemeral=True)
