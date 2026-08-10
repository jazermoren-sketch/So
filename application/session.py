import asyncio
import random
import discord

from application.manager import StageManager
from application.storage import load_config, save_application, get_application

active_sessions = {}


class TestSession:
    def __init__(self, interaction, stage):
        self.interaction = interaction
        self.user = interaction.user
        self.stage = stage
        self.all_questions = StageManager.get_questions(stage)
        self.questions = []
        self.answers = []
        self.index = 0
        self.started_at = None
        self.timeout_task = None
        self.attempt_number = 1
        self.message_listener = None

    async def start(self):
        config = load_config()
        self.message_listener = getattr(self.interaction.client, "application_message_listener", None)
        existing = get_application(self.user.id)
        existing_status = str(existing.get("status", "")).lower() if existing else ""

        if config.get("prevent_duplicate", True) and (self.user.id in active_sessions or existing_status in ("pending", "review", "قيد المراجعة", "testing")):
            return await self.interaction.response.send_message("❌ لديك تقديم قيد المراجعة أو اختبار مفتوح بالفعل.", ephemeral=True)
        if not self.all_questions:
            return await self.interaction.response.send_message("❌ لا توجد أسئلة لهذه المرحلة.", ephemeral=True)

        if existing_status in ("rejected", "مرفوض", "denied"):
            if not config.get("allow_reapply", True):
                return await self.interaction.response.send_message("❌ إعادة التقديم غير مفعلة حالياً.", ephemeral=True)
            self.attempt_number = int(existing.get("attempts", 0)) + 1
            max_attempts = int(config.get("test_attempts", 1))
            if config.get("test_attempts_enabled", True) and self.attempt_number > max_attempts:
                return await self.interaction.response.send_message(f"❌ استنفدت الحد الأقصى للمحاولات ({max_attempts}).", ephemeral=True)

        count = min(int(config.get("test_questions", len(self.all_questions))), len(self.all_questions))
        self.questions = random.sample(self.all_questions, count) if config.get("random_questions", True) else list(self.all_questions[:count])
        active_sessions[self.user.id] = self
        self.started_at = asyncio.get_running_loop().time()
        save_application(self.user.id, {"status": "testing", "stage": self.stage, "attempts": self.attempt_number, "started_at": self.started_at, "questions_count": len(self.questions)})

        await self.interaction.response.send_message(f"✅ بدأ الاختبار. عدد الأسئلة: **{len(self.questions)}**.", ephemeral=True)
        if config.get("test_timer", True):
            self.timeout_task = asyncio.create_task(self._timeout(max(1, int(config.get("test_timer_minutes", 10))) * 60))
        await self.ask_question()

    async def _timeout(self, seconds):
        try:
            await asyncio.sleep(seconds)
            if active_sessions.get(self.user.id) is self:
                await self.finish(timed_out=True)
        except asyncio.CancelledError:
            pass

    async def ask_question(self):
        if self.index >= len(self.questions):
            return await self.finish()
        embed = discord.Embed(title=f"📝 السؤال {self.index + 1}/{len(self.questions)}", description=self.questions[self.index], color=0x3498DB)
        try:
            await self.user.send(embed=embed)
        except discord.Forbidden:
            await self.finish(dm_error=True)

    async def finish(self, timed_out=False, dm_error=False):
        if active_sessions.get(self.user.id) is not self:
            return
        active_sessions.pop(self.user.id, None)
        if self.timeout_task:
            self.timeout_task.cancel()
        save_application(self.user.id, {"status": "failed" if dm_error else "review", "stage": self.stage, "attempts": self.attempt_number, "questions_count": len(self.questions), "answered": len(self.answers), "passed": None, "timed_out": timed_out})
        if timed_out and self.answers and self.message_listener:
            await self.message_listener.send_application_to_review_channel(self.user, self)
        text = "❌ تعذر إرسال الرسائل الخاصة. افتح DM وحاول مرة أخرى." if dm_error else ("⏱️ انتهى وقت الاختبار وتم إرسال الإجابات الحالية للمراجعة." if timed_out else "✅ انتهيت من الاختبار. تم إرسال إجاباتك للمراجعة.")
        try:
            await self.user.send(text)
        except discord.Forbidden:
            pass
