import discord
import time
from discord.ui import Modal, TextInput
from application.storage import load_config, load_applications, save_application


class AppealDecisionView(discord.ui.View):
    def __init__(self, guild_id, user_id):
        super().__init__(timeout=None)
        self.guild_id = int(guild_id)
        self.user_id = int(user_id)

    async def _is_reviewer(self, interaction):
        config = load_config(self.guild_id)
        reviewers = {int(x) for x in config.get("reviewers", []) if str(x).isdigit()}
        if config.get("reviewer"):
            reviewers.add(int(config["reviewer"]))
        if interaction.user.guild_permissions.administrator or interaction.user.id in reviewers:
            return True
        await interaction.response.send_message("❌ هذا الإجراء مخصص للإدارة والمراجعين فقط.", ephemeral=True)
        return False

    async def _decide(self, interaction, accepted):
        if not await self._is_reviewer(interaction):
            return
        apps = load_applications(self.guild_id)
        app = apps.get(str(self.user_id))
        if not app or not app.get("appeal_submitted"):
            return await interaction.response.send_message("❌ هذا الاعتراض غير موجود أو تمت معالجته مسبقاً.", ephemeral=True)
        if app.get("appeal_status") in ("accepted", "rejected"):
            return await interaction.response.send_message("❌ تمت معالجة هذا الاعتراض مسبقاً.", ephemeral=True)

        app["appeal_status"] = "accepted" if accepted else "rejected"
        app["appeal_decided_by"] = interaction.user.id
        app["appeal_decided_at"] = time.time()
        save_application(self.guild_id, self.user_id, app)

        member = interaction.guild.get_member(self.user_id)
        config = load_config(self.guild_id)
        if accepted and member:
            accepted_role_id = config.get("accepted_role")
            rejected_role_id = config.get("rejected_role")
            accepted_role = interaction.guild.get_role(accepted_role_id) if accepted_role_id else None
            rejected_role = interaction.guild.get_role(rejected_role_id) if rejected_role_id else None
            try:
                if accepted_role:
                    await member.add_roles(accepted_role, reason="Application appeal accepted")
                if rejected_role and rejected_role in member.roles:
                    await member.remove_roles(rejected_role, reason="Application appeal accepted")
            except (discord.Forbidden, discord.HTTPException):
                pass

        user = interaction.client.get_user(self.user_id)
        if user and config.get("application_dm_notifications", True):
            try:
                if accepted:
                    await user.send(embed=discord.Embed(title="🎉 تم قبول اعتراضك", description="بعد مراجعة اعتراضك، قررت الإدارة قبول الاعتراض.", color=discord.Color.green()))
                else:
                    await user.send(embed=discord.Embed(title="❌ تم رفض اعتراضك", description="بعد مراجعة اعتراضك، قررت الإدارة رفض الاعتراض.", color=discord.Color.red()))
            except discord.Forbidden:
                pass

        self.disable_all_items()
        status_text = "✅ تم قبول الاعتراض" if accepted else "❌ تم رفض الاعتراض"
        embed = interaction.message.embeds[0] if interaction.message and interaction.message.embeds else discord.Embed(title="📨 اعتراض على طلب تقديم")
        embed.add_field(name="🏁 قرار الاعتراض", value=f"{status_text}\n👮 بواسطة: {interaction.user.mention}", inline=False)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="قبول الاعتراض", emoji="✅", style=discord.ButtonStyle.success)
    async def accept_appeal(self, interaction, button):
        await self._decide(interaction, True)

    @discord.ui.button(label="رفض الاعتراض", emoji="❌", style=discord.ButtonStyle.danger)
    async def reject_appeal(self, interaction, button):
        await self._decide(interaction, False)


class AppealModal(Modal, title="📨 تقديم اعتراض"):
    message = TextInput(label="سبب الاعتراض", style=discord.TextStyle.paragraph, min_length=10, max_length=1000, required=True)

    def __init__(self, guild_id):
        super().__init__()
        self.guild_id = str(guild_id)

    async def on_submit(self, interaction: discord.Interaction):
        config = load_config(self.guild_id)
        if not config.get("appeals_enabled", True):
            return await interaction.response.send_message("❌ نظام الاعتراضات غير مفعّل.", ephemeral=True)
        app = load_applications(self.guild_id).get(str(interaction.user.id))
        if not app or app.get("status") != "rejected":
            return await interaction.response.send_message("❌ لا يوجد طلب مرفوض يمكن الاعتراض عليه.", ephemeral=True)
        limit = max(1, int(config.get("appeal_limit", 1)))
        if int(app.get("appeal_count", 0)) >= limit:
            return await interaction.response.send_message(f"❌ استنفدت الحد الأقصى للاعتراضات ({limit}).", ephemeral=True)
        submitted_at = float(app.get("appeal_submitted_at", 0) or 0)
        cooldown = max(0, int(config.get("appeal_cooldown_hours", 168))) * 3600
        if submitted_at and cooldown and time.time() - submitted_at < cooldown:
            return await interaction.response.send_message("⏳ لم تنتهِ مدة انتظار الاعتراض التالي.", ephemeral=True)
        channel_id = config.get("appeal_channel")
        channel = interaction.guild.get_channel(channel_id) if interaction.guild and channel_id else None
        if channel is None:
            return await interaction.response.send_message("❌ لم تحدد الإدارة روم الاعتراضات بعد.", ephemeral=True)

        embed = discord.Embed(title="📨 اعتراض على طلب تقديم", color=0xF1C40F)
        embed.add_field(name="👤 المتقدم", value=interaction.user.mention, inline=False)
        embed.add_field(name="📊 التقييم", value=f"{app.get('score', 'غير محدد')}", inline=True)
        embed.add_field(name="📝 سبب الرفض", value=(app.get("reason") or "غير محدد")[:1024], inline=False)
        embed.add_field(name="📨 الاعتراض", value=str(self.message), inline=False)
        embed.set_footer(text=f"Application ID: {interaction.user.id}")

        view = AppealDecisionView(self.guild_id, interaction.user.id)
        msg = await channel.send(embed=embed, view=view)
        save_application(self.guild_id, interaction.user.id, {
            **app,
            "appeal_submitted": True,
            "appeal_status": "pending",
            "appeal_message_id": msg.id,
            "appeal_reason": str(self.message),
            "appeal_submitted_at": time.time(),
            "appeal_count": int(app.get("appeal_count", 0)) + 1,
        })
        await interaction.response.send_message("✅ تم إرسال اعتراضك للإدارة، وغادي يتم إشعارك بالقرار فالخاص.", ephemeral=True)


class AppealView(discord.ui.View):
    def __init__(self, user_id, guild_id):
        super().__init__(timeout=86400)
        self.user_id = user_id
        self.guild_id = str(guild_id)

    @discord.ui.button(label="📨 تقديم اعتراض", style=discord.ButtonStyle.primary)
    async def appeal(self, interaction: discord.Interaction, button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ هذا الزر ليس موجهاً لك.", ephemeral=True)
        await interaction.response.send_modal(AppealModal(self.guild_id))
