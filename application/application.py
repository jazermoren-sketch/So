import discord
from discord import app_commands
from discord.ui import View, Button

from application.manager import StageManager
from application.storage import load_config, save_config


class ApplicationConfigView(View):
    def __init__(self):
        super().__init__(timeout=300)
        self.config = load_config()

    def status(self, key):
        return "🟢 مفعّل" if self.config.get(key, False) else "🔴 معطّل"

    def build_embed(self):
        embed = discord.Embed(
            title="⚙️ إعدادات نظام التقديم",
            description="استعمل الأزرار لتفعيل أو تعطيل الإضافات.",
            color=0x5865F2
        )
        items = [
            ("🔒 منع التقديم المكرر", "prevent_duplicate"),
            ("🔄 إعادة التقديم", "allow_reapply"),
            ("📊 حالات التقديم", "application_status"),
            ("🧪 النجاح والرسوب", "test_pass_fail"),
            ("⏱️ مدة الاختبار", "test_timer"),
            ("🔢 عدد المحاولات", "test_attempts"),
            ("🎲 الأسئلة العشوائية", "random_questions"),
            ("📢 Logs", "application_logs"),
            ("🔔 إشعارات DM", "application_dm_notifications"),
            ("📋 شروط التقديم", "application_requirements"),
        ]
        for label, key in items:
            embed.add_field(name=label, value=self.status(key), inline=True)
        return embed

    async def toggle(self, interaction, key):
        self.config[key] = not self.config.get(key, False)
        save_config(self.config)
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="🔒 منع المكرر", style=discord.ButtonStyle.secondary, row=0)
    async def duplicate(self, interaction, button):
        await self.toggle(interaction, "prevent_duplicate")

    @discord.ui.button(label="🔄 إعادة التقديم", style=discord.ButtonStyle.secondary, row=0)
    async def reapply(self, interaction, button):
        await self.toggle(interaction, "allow_reapply")

    @discord.ui.button(label="📊 الحالات", style=discord.ButtonStyle.secondary, row=0)
    async def statuses(self, interaction, button):
        await self.toggle(interaction, "application_status")

    @discord.ui.button(label="🧪 النجاح/الرسوب", style=discord.ButtonStyle.secondary, row=1)
    async def pass_fail(self, interaction, button):
        await self.toggle(interaction, "test_pass_fail")

    @discord.ui.button(label="⏱️ Timer", style=discord.ButtonStyle.secondary, row=1)
    async def timer(self, interaction, button):
        await self.toggle(interaction, "test_timer")

    @discord.ui.button(label="🔢 المحاولات", style=discord.ButtonStyle.secondary, row=1)
    async def attempts(self, interaction, button):
        await self.toggle(interaction, "test_attempts")

    @discord.ui.button(label="🎲 عشوائي", style=discord.ButtonStyle.secondary, row=2)
    async def random(self, interaction, button):
        await self.toggle(interaction, "random_questions")

    @discord.ui.button(label="📢 Logs", style=discord.ButtonStyle.secondary, row=2)
    async def logs(self, interaction, button):
        await self.toggle(interaction, "application_logs")

    @discord.ui.button(label="🔔 DM", style=discord.ButtonStyle.secondary, row=2)
    async def dm(self, interaction, button):
        await self.toggle(interaction, "application_dm_notifications")

    @discord.ui.button(label="📋 الشروط", style=discord.ButtonStyle.secondary, row=3)
    async def requirements(self, interaction, button):
        await self.toggle(interaction, "application_requirements")


class ApplicationCommands:
    def __init__(self, bot):
        self.bot = bot

    def register(self):
        @self.bot.tree.command(name="setreviewchannel", description="تحديد روم مراجعة الطلبات")
        @app_commands.checks.has_permissions(administrator=True)
        async def setreviewchannel(interaction: discord.Interaction, channel: discord.TextChannel):
            config = load_config(); config["review_channel"] = channel.id; save_config(config)
            await interaction.response.send_message(f"✅ تم تحديد {channel.mention} كروم مراجعة الطلبات.", ephemeral=True)

        @self.bot.tree.command(name="createstage", description="إنشاء مرحلة جديدة")
        @app_commands.checks.has_permissions(administrator=True)
        async def createstage(interaction: discord.Interaction, name: str):
            if StageManager.create_stage(name):
                await interaction.response.send_message(f"✅ تم إنشاء المرحلة **{name}**", ephemeral=True)
            else:
                await interaction.response.send_message("❌ هذه المرحلة موجودة مسبقًا.", ephemeral=True)

        @self.bot.tree.command(name="deletestage", description="حذف مرحلة")
        @app_commands.checks.has_permissions(administrator=True)
        async def deletestage(interaction: discord.Interaction, name: str):
            if StageManager.delete_stage(name):
                await interaction.response.send_message(f"🗑️ تم حذف المرحلة **{name}**", ephemeral=True)
            else:
                await interaction.response.send_message("❌ المرحلة غير موجودة.", ephemeral=True)

        @self.bot.tree.command(name="liststages", description="عرض جميع المراحل")
        @app_commands.checks.has_permissions(administrator=True)
        async def liststages(interaction: discord.Interaction):
            stages = StageManager.list_stages()
            if not stages:
                return await interaction.response.send_message("لا توجد مراحل.", ephemeral=True)
            embed = discord.Embed(title="📋 المراحل", color=0x2ECC71)
            for stage, data in stages.items():
                embed.add_field(name=stage, value=f"الأسئلة: {len(data['questions'])}", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)

        @self.bot.tree.command(name="setreviewer", description="تحديد المراجع")
        @app_commands.checks.has_permissions(administrator=True)
        async def setreviewer(interaction: discord.Interaction, member: discord.Member):
            config = load_config(); config["reviewer"] = member.id; save_config(config)
            await interaction.response.send_message(f"✅ تم تعيين {member.mention} كمراجع.", ephemeral=True)

        @self.bot.tree.command(name="setacceptedrole", description="تحديد رتبة المقبولين في التقديم")
        @app_commands.checks.has_permissions(administrator=True)
        async def setacceptedrole(interaction: discord.Interaction, role: discord.Role | None = None):
            config = load_config(); config["accepted_role"] = role.id if role else None; save_config(config)
            message = f"✅ تم تحديد {role.mention} كرتبة تلقائية للمقبولين." if role else "🗑️ تم إلغاء رتبة القبول."
            await interaction.response.send_message(message, ephemeral=True)

        @self.bot.tree.command(name="setrejectedrole", description="تحديد رتبة المرفوضين في التقديم")
        @app_commands.checks.has_permissions(administrator=True)
        async def setrejectedrole(interaction: discord.Interaction, role: discord.Role | None = None):
            config = load_config(); config["rejected_role"] = role.id if role else None; save_config(config)
            message = f"✅ تم تحديد {role.mention} كرتبة للمرفوضين." if role else "🗑️ تم إلغاء رتبة الرفض."
            await interaction.response.send_message(message, ephemeral=True)

        @self.bot.tree.command(name="configureapplications", description="فتح لوحة إعدادات نظام التقديم")
        @app_commands.checks.has_permissions(administrator=True)
        @app_commands.describe(hidden="إخفاء لوحة الإعدادات عن باقي الأعضاء")
        async def configureapplications(interaction: discord.Interaction, hidden: bool = False):
            view = ApplicationConfigView()
            await interaction.response.send_message(embed=view.build_embed(), view=view, ephemeral=hidden)

        @createstage.error
        @deletestage.error
        @liststages.error
        @setreviewer.error
        @setreviewchannel.error
        @setacceptedrole.error
        @setrejectedrole.error
        @configureapplications.error
        async def permission_error(interaction: discord.Interaction, error):
            if isinstance(error, app_commands.MissingPermissions):
                if interaction.response.is_done():
                    await interaction.followup.send("❌ هذا الأمر للإدارة فقط.", ephemeral=True)
                else:
                    await interaction.response.send_message("❌ هذا الأمر للإدارة فقط.", ephemeral=True)
