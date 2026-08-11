import discord
from application.storage import load_config, get_application, save_application
from application.results import ResultManager

class QuestionScoreView(discord.ui.View):
    def __init__(self, review_view, questions_count): super().__init__(timeout=600); self.review_view=review_view; self.questions_count=max(1,int(questions_count)); self.index=0; self.correct=0
    async def mark(self,interaction,correct):
        if not await self.review_view._check_reviewer(interaction): return
        if self.index>=self.questions_count: return await interaction.response.send_message("❌ انتهى تقييم الأسئلة.",ephemeral=True)
        if correct: self.correct+=1
        self.index+=1
        if self.index>=self.questions_count:
            cfg=load_config(self.review_view.guild_id); max_score=int(cfg.get("score_max",10)); minimum=float(cfg.get("score_min",5)); score=round((self.correct/self.questions_count)*max_score,2); accepted=score>=minimum
            reason=f"⭐ تقييم الأسئلة: {self.correct}/{self.questions_count} صحيح — {score}/{max_score}"
            if accepted: await ResultManager.accept(interaction,self.review_view.user_id,self.review_view.stage,reason=reason,score=score)
            else: await ResultManager.reject(interaction,self.review_view.user_id,self.review_view.stage,reason=reason,score=score)
            for child in self.children: child.disabled=True
            return await interaction.response.edit_message(content=f"{'✅ تم القبول' if accepted else '❌ تم الرفض'} — **{score}/{max_score}**",view=self)
        await interaction.response.edit_message(content=f"📝 السؤال **{self.index+1}/{self.questions_count}**\nاختر: **صحيح** أو **خطأ**\n\nالصحيح حتى الآن: **{self.correct}**",view=self)
    @discord.ui.button(label="صحيح",emoji="✅",style=discord.ButtonStyle.success)
    async def correct_button(self,interaction,button): await self.mark(interaction,True)
    @discord.ui.button(label="خطأ",emoji="❌",style=discord.ButtonStyle.danger)
    async def wrong_button(self,interaction,button): await self.mark(interaction,False)

class ScoreView(discord.ui.View):
    def __init__(self,review_view): super().__init__(timeout=600); self.review_view=review_view; self.score=0; self.max_score=int(load_config(review_view.guild_id).get("score_max",10))
    async def check(self,interaction): return await self.review_view._check_reviewer(interaction)
    @discord.ui.button(label="➕ نقطة",style=discord.ButtonStyle.primary,row=0)
    async def add(self,interaction,button):
        if not await self.check(interaction): return
        self.score=min(self.max_score,self.score+1); await interaction.response.edit_message(content=f"⭐ التقييم الحالي: **{self.score}/{self.max_score}**",view=self)
    @discord.ui.button(label="➖ نقطة",style=discord.ButtonStyle.secondary,row=0)
    async def remove(self,interaction,button):
        if not await self.check(interaction): return
        self.score=max(0,self.score-1); await interaction.response.edit_message(content=f"⭐ التقييم الحالي: **{self.score}/{self.max_score}**",view=self)
    @discord.ui.button(label="🏁 إنهاء التقييم",style=discord.ButtonStyle.success,row=1)
    async def finish(self,interaction,button):
        if not await self.check(interaction): return
        cfg=load_config(self.review_view.guild_id); minimum=float(cfg.get("score_min",5)); accepted=self.score>=minimum; reason=f"⭐ التقييم: {self.score}/{self.max_score}" if accepted else f"⭐ التقييم: {self.score}/{self.max_score} (الحد الأدنى {minimum:g}/{self.max_score})"
        if accepted: await ResultManager.accept(interaction,self.review_view.user_id,self.review_view.stage,reason=reason,score=self.score)
        else: await ResultManager.reject(interaction,self.review_view.user_id,self.review_view.stage,reason=reason,score=self.score)
        for child in self.children: child.disabled=True
        await interaction.response.edit_message(content=f"{'✅ تم القبول' if accepted else '❌ تم الرفض'} — **{self.score}/{self.max_score}**",view=self)

class ReasonModal(discord.ui.Modal):
    def __init__(self,action,view): super().__init__(title="سبب قبول الطلب" if action=="accept" else "سبب رفض الطلب"); self.action,self.review_view=action,view; self.reason=discord.ui.TextInput(label="السبب",placeholder="اكتب سبب القرار هنا...",style=discord.TextStyle.paragraph,required=True,min_length=1,max_length=1000); self.add_item(self.reason)
    async def on_submit(self,interaction):
        if not await self.review_view._check_reviewer(interaction): return
        await self.review_view._manual_decision(interaction,self.action,str(self.reason.value).strip())

class ReviewView(discord.ui.View):
    def __init__(self,user_id,stage,guild_id): super().__init__(timeout=None); self.user_id,self.stage,self.guild_id=user_id,stage,str(guild_id); self.review_message=None
    def disable_all(self):
        for child in self.children: child.disabled=True
    async def _check_reviewer(self,interaction):
        cfg=load_config(self.guild_id); reviewers=set(cfg.get("reviewers",[]))
        if cfg.get("reviewer"): reviewers.add(cfg["reviewer"])
        if interaction.user.id not in reviewers: await interaction.response.send_message("❌ أنت لست من المراجعين المسموح لهم.",ephemeral=True); return False
        app=get_application(self.guild_id,self.user_id)
        if not app or app.get("status") not in ("review","pending"): await interaction.response.send_message("❌ هذا الطلب لم يعد قيد المراجعة.",ephemeral=True); return False
        return True
    async def _manual_decision(self,interaction,action,reason=None):
        cfg=load_config(self.guild_id)
        if cfg.get("reviewer_voting",False):
            app=get_application(self.guild_id,self.user_id) or {}; votes=app.get("votes",{})
            if str(interaction.user.id) in votes: return await interaction.response.send_message("❌ سبق لك التصويت على هذا الطلب.",ephemeral=True)
            votes[str(interaction.user.id)]=action; app["votes"]=votes; save_application(self.guild_id,self.user_id,app)
            approvals=sum(v=="accept" for v in votes.values()); rejections=sum(v=="reject" for v in votes.values()); required=int(cfg.get("required_approvals",1))
            if approvals<required and rejections<required: return await interaction.response.send_message(f"🗳️ تم تسجيل تصويتك. قبول: **{approvals}/{required}** | رفض: **{rejections}/{required}**",ephemeral=True)
            final_reason=reason or f"🗳️ تصويت المراجعين — قبول: {approvals} | رفض: {rejections}"
            if approvals>=required: await ResultManager.accept(interaction,self.user_id,self.stage,reason=final_reason)
            else: await ResultManager.reject(interaction,self.user_id,self.stage,reason=final_reason)
            self.disable_all()
            try: await interaction.response.send_message("✅ اكتمل تصويت المراجعين وتم تنفيذ القرار.",ephemeral=True)
            except discord.InteractionResponded: pass
            if interaction.message:
                try: await interaction.message.edit(view=self)
                except (discord.NotFound,discord.HTTPException): pass
            return
        if action=="accept": await ResultManager.accept(interaction,self.user_id,self.stage,reason=reason)
        else: await ResultManager.reject(interaction,self.user_id,self.stage,reason=reason)
        self.disable_all()
        if interaction.message:
            try: await interaction.message.edit(view=self)
            except (discord.NotFound,discord.HTTPException): pass
        try: await interaction.response.send_message("✅ تم تنفيذ القرار.",ephemeral=True)
        except discord.InteractionResponded: pass
    @discord.ui.button(label="قبول",emoji="✅",style=discord.ButtonStyle.success,row=0)
    async def accept(self,interaction,button):
        if await self._check_reviewer(interaction): await self._manual_decision(interaction,"accept")
    @discord.ui.button(label="قبول مع سبب",emoji="📝",style=discord.ButtonStyle.success,row=0)
    async def accept_with_reason(self,interaction,button):
        if await self._check_reviewer(interaction): await interaction.response.send_modal(ReasonModal("accept",self))
    @discord.ui.button(label="رفض",emoji="❌",style=discord.ButtonStyle.danger,row=0)
    async def reject(self,interaction,button):
        if await self._check_reviewer(interaction): await self._manual_decision(interaction,"reject")
    @discord.ui.button(label="رفض مع سبب",emoji="📝",style=discord.ButtonStyle.danger,row=0)
    async def reject_with_reason(self,interaction,button):
        if await self._check_reviewer(interaction): await interaction.response.send_modal(ReasonModal("reject",self))
    @discord.ui.button(label="⭐ تقييم",emoji="⭐",style=discord.ButtonStyle.primary,row=1)
    async def scoring(self,interaction,button):
        if not await self._check_reviewer(interaction): return
        cfg=load_config(self.guild_id)
        if not cfg.get("scoring_enabled",False): return await interaction.response.send_message("❌ نظام التقييم غير مفعّل.",ephemeral=True)
        app=get_application(self.guild_id,self.user_id) or {}
        if cfg.get("question_scoring",False): return await interaction.response.send_message(f"📝 ابدأ تقييم **{app.get('questions_count',1)}** سؤالاً.",view=QuestionScoreView(self,app.get('questions_count',1)),ephemeral=True)
        await interaction.response.send_message(f"⭐ بدأ التقييم من **0 إلى {cfg.get('score_max',10)}**. الحد الأدنى: **{cfg.get('score_min',5)}**",view=ScoreView(self),ephemeral=True)
