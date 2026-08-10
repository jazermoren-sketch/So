import discord

from application.session import active_sessions
from application.storage import load_answers, save_answers, load_config, save_application
from application.review_view import ReviewView


class MessageListener:
    def __init__(self, bot):
        self.bot = bot
        bot.application_message_listener = self

    async def send_application_to_review_channel(self, message, session):
        config = load_config()
        review_channel_id = config.get("review_channel")
        if not review_channel_id:
            return
        channel = self.bot.get_channel(review_channel_id)
        if channel is None:
            return

        embed = discord.Embed(title="📋 طلب تقديم جديد", color=0x2ECC71)
        embed.add_field(name="👤 المتقدم", value=message.author.mention, inline=False)
        embed.add_field(name="📌 المرحلة", value=session.stage, inline=False)
        embed.add_field(name="📊 النتيجة", value=f"تمت الإجابة على **{len(session.answers)}/{len(session.questions)}** سؤال", inline=False)

        for question, answer in zip(session.questions, session.answers):
            embed.add_field(name=question[:256], value=(answer or "لا توجد إجابة")[:1024], inline=False)

        reviewers = list(config.get("reviewers", []))
        if config.get("reviewer") and config["reviewer"] not in reviewers:
            reviewers.append(config["reviewer"])
        if reviewers:
            embed.add_field(name="👥 المراجعون", value=" ".join(f"<@{rid}>" for rid in reviewers), inline=False)

        view = ReviewView(message.author.id, session.stage)
        review_message = await channel.send(embed=embed, view=view)
        view.review_message = review_message

    def register(self):
        @self.bot.event
        async def on_message(message: discord.Message):
            if message.author.bot:
                return

            if isinstance(message.channel, discord.DMChannel):
                session = active_sessions.get(message.author.id)
                if session:
                    session.answers.append(message.content)
                    answers = load_answers()
                    answers.setdefault(str(message.author.id), {})[session.stage] = session.answers
                    save_answers(answers)
                    session.index += 1

                    if session.index >= len(session.questions):
                        await self.send_application_to_review_channel(message, session)
                        save_application(message.author.id, {
                            "status": "review", "stage": session.stage,
                            "attempts": session.attempt_number,
                            "questions_count": len(session.questions),
                            "answered": len(session.answers), "passed": None,
                        })
                        try:
                            await message.author.send(embed=discord.Embed(
                                title="✅ انتهى الاختبار",
                                description="تم إرسال جميع الإجابات للإدارة للمراجعة.",
                                color=0x2ECC71
                            ))
                        except discord.Forbidden:
                            pass
                        if session.timeout_task:
                            session.timeout_task.cancel()
                        active_sessions.pop(message.author.id, None)
                    else:
                        await session.ask_question()
                    return

            await self.bot.process_commands(message)
