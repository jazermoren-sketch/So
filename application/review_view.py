import discord
from application.storage import load_config
from application.results import ResultManager


class ScoreView(discord.ui.View):
    def __init__(self, review_view):
        super().__init__(timeout=300); self.review_view=review_view; self.score=0; self.max_score=load_config().get("score_max",10)
    @discord.ui.button(label="➕ نقطة",style=discord.ButtonStyle.primary,row=0)
    async def add(self,interaction,button):
        if not await self.review_view._check_reviewer(interaction): return
        self.score=min(self.max_score,self.score+1); await interaction.response.edit_message(content=f"⭐ التقييم الحالي: **{self.score}/{self.max_score}**",view=self)
    @discord.ui.button(label="➖ نقطة",style=discord.ButtonStyle.secondary,row=0)
    async def remove(self,interaction,button):
        if not await self.review_view._check_reviewer(interaction): return
        self.score=max(0,self.score-1); await interaction.response.edit_message(content=f"⭐ التقييم الحالي: **{self.score}/{self.max_score}**",view=self)
    @discord.ui.button(label="🏁 إنهاء التقييم",style=discord.ButtonStyle.success,row=1)
    async def finish(self,interaction,button):
        if not await self.review_view._check_reviewer(interaction): return
        config=load_config(); minimum=config.get("score_min",5); accepted=self.score>=minimum
        reason=f"⭐ التقييم: {self.score}/{self.max_score}" if accepted else f"⭐ التقييم: {self.score}/{self.max_score} (الحد الأدنى {minimum}/{self.max_score})"
        if accepted: await ResultManager.accept(interaction,self.review_view.user_id,self.review_view.stage,reason=reason,score=self.score)
        else: await ResultManager.reject(interaction,self.review_view.user_id,self.review_view.stage,reason=reason,score=self.score)
        self.review_view.disable_all(); await interaction.response.edit_message(content=f"{'✅ تم القبول' if accepted else '❌ تم الرفض'} — **{self.score}/{self.max_score}**",view=self)


class ReasonModal(discord.ui.Modal):
    def __init__(self,action,view):
        super().__init__(title="سبب قبول الطلب" if action=="accept" else "سبب رفض الطلب"); self.action=action; self.review_view=view
        self.reason=discord.ui.TextInput(label="السبب",placeholder="اكتب سبب القرار هنا...",style=discord.TextStyle.paragraph,required=True,min_length=1,max_length=1000); self.add_item(self.reason)
    async def on_submit(self,interaction):
        if not await self.review_view._check_reviewer(interaction): return
        reason=str(self.reason.value).strip()
        if self.action=="accept": await ResultManager.accept(interaction,self.review_view.user_id,self.review_view.stage,reason=reason)
        else: await ResultManager.reject(interaction,self.review_view.user_id,self.review_view.stage,reason=reason)
        self.review_view.disable_all(); await interaction.response.send_message("✅ تم تنفيذ القرار وإرسال السبب للمتقدم.",ephemeral=True)


class ReviewView(discord.ui.View):
    def __init__(self,user_id,stage): super().__init__(timeout=None); self.user_id=user_id; self.stage=stage; self.review_message=None
    def disable_all(self):
        for child in self.children: child.disabled=True
    async def _check_reviewer(self,interaction):
        config=load_config(); reviewers=set(config.get("reviewers",[]));
        if config.get("reviewer"): reviewers.add(config["reviewer"])
        if interaction.user.id not in reviewers:
            await interaction.response.send_message("❌ أنت لست من المراجعين المسموح لهم.",ephemeral=True); return False
        return True
    async def _complete(self,interaction,action,reason=None):
        if action=="accept": await ResultManager.accept(interaction,self.user_id,self.stage,reason=reason)
        else: await ResultManager.reject(interaction,self.user_id,self.stage,reason=reason)
        self.disable_all()
        if interaction.message:
            try: await interaction.message.edit(view=self)
            except (discord.NotFound,discord.HTTPException): pass
        await interaction.followup.send("✅ تم تنفيذ القرار.",ephemeral=True)
    @discord.ui.button(label="قبول",emoji="✅",style=discord.ButtonStyle.success,row=0)
    async def accept(self,interaction,button):
        if not await self._check_reviewer(interaction): return
        await interaction.response.defer(ephemeral=True); await self._complete(interaction,"accept")
    @discord.ui.button(label="قبول مع سبب",emoji="📝",style=discord.ButtonStyle.success,row=0)
    async def accept_with_reason(self,interaction,button):
        if not await self._check_reviewer(interaction): return
        self.review_message=interaction.message; await interaction.response.send_modal(ReasonModal("accept",self))
    @discord.ui.button(label="رفض",emoji="❌",style=discord.ButtonStyle.danger,row=0)
    async def reject(self,interaction,button):
        if not await self._check_reviewer(interaction): return
        await interaction.response.defer(ephemeral=True); await self._complete(interaction,"reject")
    @discord.ui.button(label="رفض مع سبب",emoji="📝",style=discord.ButtonStyle.danger,row=0)
    async def reject_with_reason(self,interaction,button):
        if not await self._check_reviewer(interaction): return
        self.review_message=interaction.message; await interaction.response.send_modal(ReasonModal("reject",self))
    @discord.ui.button(label="⭐ تقييم",emoji="⭐",style=discord.ButtonStyle.primary,row=1)
    async def scoring(self,interaction,button):
        if not await self._check_reviewer(interaction): return
        config=load_config()
        if not config.get("scoring_enabled",False): return await interaction.response.send_message("❌ نظام التقييم غير مفعّل.",ephemeral=True)
        await interaction.response.send_message(f"⭐ بدأ التقييم من **0 إلى {config.get('score_max',10)}**. الحد الأدنى: **{config.get('score_min',5)}**",view=ScoreView(self),ephemeral=True)
