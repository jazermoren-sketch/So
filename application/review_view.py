import discord
from application.storage import load_config
from application.results import ResultManager


class ReasonModal(discord.ui.Modal):
    def __init__(self, action: str, view: "ReviewView"):
        super().__init__(title="سبب قبول الطلب" if action == "accept" else "سبب رفض الطلب")
        self.action = action
        self.review_view = view
        self.reason = discord.ui.TextInput(label="السبب", placeholder="اكتب سبب القرار هنا...", style=discord.TextStyle.paragraph, required=True, min_length=1, max_length=1000)
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        if not await self.review_view._check_reviewer(interaction):
            return
        reason = str(self.reason.value).strip()
        try:
            if self.action == "accept":
                await ResultManager.accept(interaction, self.review_view.user_id, self.review_view.stage, reason=reason)
                message = "✅ تم قبول الطلب وإرسال السبب للمتقدم."
            else:
                await ResultManager.reject(interaction, self.review_view.user_id, self.review_view.stage, reason=reason)
                message = "❌ تم رفض الطلب وإرسال سبب الرفض للمتقدم."
            self.review_view.disable_all()
            if self.review_view.review_message:
                try:
                    await self.review_view.review_message.edit(view=self.review_view)
                except (discord.NotFound, discord.HTTPException):
                    pass
            await interaction.response.send_message(message, ephemeral=True)
        except Exception:
            if not interaction.response.is_done():
                await interaction.response.send_message("❌ حدث خطأ أثناء تنفيذ القرار.", ephemeral=True)
            else:
                await interaction.followup.send("❌ حدث خطأ أثناء تنفيذ القرار.", ephemeral=True)


class ReviewView(discord.ui.View):
    def __init__(self, user_id: int, stage: str):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.stage = stage
        self.review_message = None

    def disable_all(self):
        for child in self.children:
            child.disabled = True

    async def _check_reviewer(self, interaction: discord.Interaction):
        config = load_config()
        reviewers = set(config.get("reviewers", []))
        if config.get("reviewer"):
            reviewers.add(config["reviewer"])
        if interaction.user.id not in reviewers:
            await interaction.response.send_message("❌ أنت لست من المراجعين المسموح لهم.", ephemeral=True)
            return False
        return True

    async def _complete(self, interaction, action, reason=None):
        if action == "accept":
            await ResultManager.accept(interaction, self.user_id, self.stage, reason=reason)
            message = "✅ تم قبول الطلب." if reason is None else "✅ تم قبول الطلب وإرسال السبب للمتقدم."
        else:
            await ResultManager.reject(interaction, self.user_id, self.stage, reason=reason)
            message = "❌ تم رفض الطلب." if reason is None else "❌ تم رفض الطلب وإرسال سبب الرفض للمتقدم."
        self.disable_all()
        if interaction.message:
            try:
                await interaction.message.edit(view=self)
            except (discord.NotFound, discord.HTTPException):
                pass
        await interaction.followup.send(message, ephemeral=True)

    @discord.ui.button(label="قبول", emoji="✅", style=discord.ButtonStyle.success, row=0)
    async def accept(self, interaction, button):
        if not await self._check_reviewer(interaction): return
        await interaction.response.defer(ephemeral=True)
        await self._complete(interaction, "accept")

    @discord.ui.button(label="قبول مع سبب", emoji="📝", style=discord.ButtonStyle.success, row=0)
    async def accept_with_reason(self, interaction, button):
        if not await self._check_reviewer(interaction): return
        self.review_message = interaction.message
        await interaction.response.send_modal(ReasonModal("accept", self))

    @discord.ui.button(label="رفض", emoji="❌", style=discord.ButtonStyle.danger, row=0)
    async def reject(self, interaction, button):
        if not await self._check_reviewer(interaction): return
        await interaction.response.defer(ephemeral=True)
        await self._complete(interaction, "reject")

    @discord.ui.button(label="رفض مع سبب", emoji="📝", style=discord.ButtonStyle.danger, row=0)
    async def reject_with_reason(self, interaction, button):
        if not await self._check_reviewer(interaction): return
        self.review_message = interaction.message
        await interaction.response.send_modal(ReasonModal("reject", self))
