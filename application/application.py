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
        embed = discord.Embed(title="⚙️ إعدادات نظام التقديم", description="اضغط على الأزرار لتفعيل/تعطيل الأنظمة أو تعديل إعدادات الاختبار.", color=0x5865F2)
        for name, key in [
            ("🔒 منع المكرر", "prevent_duplicate"), ("🔄 إعادة التقديم", "allow_reapply"),
            ("📊 حالات التقديم", "application_status"), ("🧪 النجاح/الرسوب", "test_pass_fail"),
            ("⏱️ Timer", "test_timer"), ("🔢 المحاولات", "test_attempts_enabled"),
            ("🎲 أسئلة عشوائية", "random_questions"), ("📢 Logs", "application_logs"),
            ("🔔 DM", "application_dm_notifications"), ("📋 الشروط", "application_requirements")]:
            embed.add_field(name=name, value=s(key), inline=True)
        embed.add_field(name="🎯 إعدادات الاختبار", value=f"أسئلة: **{cfg.get('test_questions', 10)}** | نجاح: **{cfg.get('test_pass_percent', 70)}%** | وقت: **{cfg.get('test_timer_minutes', 10)} د** | محاولات: **{cfg.get('test_attempts', 1)}**", inline=False)
        embed.add_field(name="👥 المراجعون", value=f"**{len(cfg.get('reviewers', []))}** مراجع(ين)", inline=False)
        return embed

    async def toggle(self, interaction, key):
        self.config[key] = not self.config.get(key, False)
        save_config(self.config)
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    async def noop(self, interaction):
        await interaction.response.send_message("استخدم أوامر إعدادات الاختبار والمراجعين لتعديل القيم.", ephemeral=True)

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


class ApplicationCommands:
    def __init__(self, bot): self.bot = bot

    def register(self):
        @self.bot.tree.command(name="setreviewchannel", description="تحديد روم مراجعة الطلبات")
        @app_commands.checks.has_permissions(administrator=True)
        async def setreviewchannel(interaction: discord.Interaction, channel: discord.TextChannel):
            config = load_config(); config["review_channel"] = channel.id; save_config(config)
            await interaction.response.send_message(f"✅ تم تحديد {channel.mention} كروم مراجعة الطلبات.", ephemeral=True)

        @self.bot.tree.command(name="createstage", description="إنشاء مرحلة جديدة")
        @app_commands.checks.has_permissions(administrator=True)
        async def createstage(interaction: discord.Interaction, name: str):
            await interaction.response.send_message(f"✅ تم إنشاء المرحلة **{name}**" if StageManager.create_stage(name) else "❌ هذه المرحلة موجودة مسبقًا.", ephemeral=True)

        @self.bot.tree.command(name="deletestage", description="حذف مرحلة")
        @app_commands.checks.has_permissions(administrator=True)
        async def deletestage(interaction: discord.Interaction, name: str):
            await interaction.response.send_message(f"🗑️ تم حذف المرحلة **{name}**" if StageManager.delete_stage(name) else "❌ المرحلة غير موجودة.", ephemeral=True)

        @self.bot.tree.command(name="liststages", description="عرض جميع المراحل")
        @app_commands.checks.has_permissions(administrator=True)
        async def liststages(interaction: discord.Interaction):
            stages = StageManager.list_stages()
            if not stages: return await interaction.response.send_message("لا توجد مراحل.", ephemeral=True)
            embed = discord.Embed(title="📋 المراحل", color=0x2ECC71)
            for stage, data in stages.items(): embed.add_field(name=stage, value=f"الأسئلة: {len(data['questions'])}", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)

        @self.bot.tree.command(name="setreviewer", description="تعيين مراجع للتقديم")
        @app_commands.checks.has_permissions(administrator=True)
        async def setreviewer(interaction: discord.Interaction, member: discord.Member):
            config = load_config(); config["reviewer"] = member.id
            if member.id not in config.setdefault("reviewers", []): config["reviewers"].append(member.id)
            save_config(config); await interaction.response.send_message(f"✅ تمت إضافة {member.mention} كمراجع.", ephemeral=True)

        @self.bot.tree.command(name="removereviewer", description="إزالة مراجع")
        @app_commands.checks.has_permissions(administrator=True)
        async def removereviewer(interaction: discord.Interaction, member: discord.Member):
            config = load_config(); config["reviewers"] = [x for x in config.get("reviewers", []) if x != member.id]
            if config.get("reviewer") == member.id: config["reviewer"] = config["reviewers"][0] if config["reviewers"] else None
            save_config(config); await interaction.response.send_message(f"🗑️ تمت إزالة {member.mention} من المراجعين.", ephemeral=True)

        @self.bot.tree.command(name="setacceptedrole", description="تحديد رتبة المقبولين في التقديم")
        @app_commands.checks.has_permissions(administrator=True)
        async def setacceptedrole(interaction: discord.Interaction, role: discord.Role | None = None):
            config = load_config(); config["accepted_role"] = role.id if role else None; save_config(config)
            await interaction.response.send_message(f"{'✅ تم تحديد ' + role.mention if role else '🗑️ تم إلغاء رتبة القبول.'}", ephemeral=True)

        @self.bot.tree.command(name="setrejectedrole", description="تحديد رتبة المرفوضين في التقديم")
        @app_commands.checks.has_permissions(administrator=True)
        async def setrejectedrole(interaction: discord.Interaction, role: discord.Role | None = None):
            config = load_config(); config["rejected_role"] = role.id if role else None; save_config(config)
            await interaction.response.send_message(f"{'✅ تم تحديد ' + role.mention if role else '🗑️ تم إلغاء رتبة الرفض.'}", ephemeral=True)

        @self.bot.tree.command(name="configureapplications", description="فتح لوحة إعدادات نظام التقديم")
        @app_commands.checks.has_permissions(administrator=True)
        @app_commands.describe(hidden="إخفاء لوحة الإعدادات")
        async def configureapplications(interaction: discord.Interaction, hidden: bool = False):
            await interaction.response.send_message(embed=ApplicationConfigView().build_embed(), view=ApplicationConfigView(), ephemeral=hidden)

        @self.bot.tree.command(name="settestsettings", description="إعدادات الاختبار")
        @app_commands.checks.has_permissions(administrator=True)
        @app_commands.describe(questions="عدد الأسئلة", pass_percent="نسبة النجاح", timer_minutes="مدة الاختبار بالدقائق", attempts="عدد المحاولات")
        async def settestsettings(interaction: discord.Interaction, questions: app_commands.Range[int, 1, 100], pass_percent: app_commands.Range[int, 1, 100], timer_minutes: app_commands.Range[int, 1, 180], attempts: app_commands.Range[int, 1, 20]):
            config = load_config(); config.update({"test_questions": questions, "test_pass_percent": pass_percent, "test_timer_minutes": timer_minutes, "test_attempts": attempts}); save_config(config)
            await interaction.response.send_message(f"✅ تم حفظ إعدادات الاختبار: **{questions}** سؤال، نجاح **{pass_percent}%**، وقت **{timer_minutes} دقيقة**، محاولات **{attempts}**.", ephemeral=True)

        @self.bot.tree.command(name="applicationstats", description="إحصائيات نظام التقديم")
        @app_commands.checks.has_permissions(administrator=True)
        async def applicationstats(interaction: discord.Interaction):
            from application.storage import load_applications
            apps = load_applications(); total = len(apps); pending = accepted = rejected = 0
            for data in apps.values():
                status = str(data.get("status", "pending")).lower()
                pending += status in ("pending", "review", "قيد المراجعة")
                accepted += status in ("accepted", "مقبول", "approved")
                rejected += status in ("rejected", "مرفوض", "denied")
            embed = discord.Embed(title="📊 إحصائيات التقديم", color=0x5865F2)
            embed.add_field(name="📋 الإجمالي", value=str(total), inline=True)
            embed.add_field(name="⏳ قيد المراجعة", value=str(pending), inline=True)
            embed.add_field(name="✅ مقبول", value=str(accepted), inline=True)
            embed.add_field(name="❌ مرفوض", value=str(rejected), inline=True)
            await interaction.response.send_message(embed=embed, ephemeral=True)

        @createstage.error
        @deletestage.error
        @liststages.error
        @setreviewer.error
        @removereviewer.error
        @setreviewchannel.error
        @setacceptedrole.error
        @setrejectedrole.error
        @configureapplications.error
        @settestsettings.error
        @applicationstats.error
        async def permission_error(interaction: discord.Interaction, error):
            if isinstance(error, app_commands.MissingPermissions):
                msg = "❌ هذا الأمر للإدارة فقط."
                if interaction.response.is_done(): await interaction.followup.send(msg, ephemeral=True)
                else: await interaction.response.send_message(msg, ephemeral=True)
