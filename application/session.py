import discord

from application.manager import StageManager

active_sessions = {}


class TestSession:

    def __init__(
        self,
        interaction,
        stage
    ):

        self.interaction = interaction
        self.user = interaction.user
        self.stage = stage

        self.questions = StageManager.get_questions(stage)

        self.answers = []

        self.index = 0

    async def start(self):

        if self.user.id in active_sessions:

            return await self.interaction.response.send_message(
                "❌ لديك اختبار مفتوح بالفعل.",
                ephemeral=True
            )

        if not self.questions:

            return await self.interaction.response.send_message(
                "❌ لا توجد أسئلة لهذه المرحلة.",
                ephemeral=True
            )

        active_sessions[self.user.id] = self

        await self.interaction.response.send_message(
            "✅ بدأ الاختبار.",
            ephemeral=True
        )

        await self.ask_question()

    async def ask_question(self):

        if self.index >= len(self.questions):

            return await self.finish()

        question = self.questions[self.index]

        await self.user.send(
            embed=discord.Embed(
                title=f"السؤال {self.index+1}",
                description=question,
                color=0x3498DB
            )
        )

async def finish(self):

    active_sessions.pop(
        self.user.id,
        None
    )

    await self.user.send(
        "✅ انتهيت من الاختبار."
    )