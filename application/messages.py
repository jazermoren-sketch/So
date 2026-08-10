import discord

from application.session import active_sessions
from application.storage import (
    load_answers,
    save_answers,
    load_config
)
from application.review_view import ReviewView


class MessageListener:

    def __init__(self, bot):
        self.bot = bot

    async def send_application_to_review_channel(
        self,
        message,
        session
    ):
        config = load_config()

        review_channel_id = config.get(
            "review_channel"
        )

        if not review_channel_id:
            return

        channel = self.bot.get_channel(
            review_channel_id
        )

        if channel is None:
            return

        embed = discord.Embed(
            title="📋 طلب تقديم جديد",
            color=0x2ECC71
        )

        embed.add_field(
            name="👤 المتقدم",
            value=message.author.mention,
            inline=False
        )

        embed.add_field(
            name="📌 المرحلة",
            value=session.stage,
            inline=False
        )

        for question, answer in zip(
            session.questions,
            session.answers
        ):
            embed.add_field(
                name=question,
                value=answer or "لا توجد إجابة",
                inline=False
            )

        await channel.send(
            embed=embed,
            view=ReviewView(
                message.author.id,
                session.stage
            )
        )

    def register(self):

        @self.bot.event
        async def on_message(
            message: discord.Message
        ):

            if message.author.bot:
                return

            if isinstance(
                message.channel,
                discord.DMChannel
            ):
                session = active_sessions.get(
                    message.author.id
                )

                if session:
                    session.answers.append(
                        message.content
                    )

                    answers = load_answers()

                    answers.setdefault(
                        str(message.author.id),
                        {}
                    )

                    answers[
                        str(message.author.id)
                    ][
                        session.stage
                    ] = session.answers

                    save_answers(
                        answers
                    )

                    session.index += 1

                    if session.index >= len(
                        session.questions
                    ):
                        config = load_config()

                        reviewer = None

                        if config.get("reviewer"):
                            reviewer = self.bot.get_user(
                                config["reviewer"]
                            )

                        embed = discord.Embed(
                            title="✅ انتهى الاختبار",
                            description="تم إرسال جميع الإجابات.",
                            color=0x2ECC71
                        )

                        if reviewer:
                            embed.add_field(
                                name="المراجع",
                                value=reviewer.mention,
                                inline=False
                            )

                        await message.author.send(
                            embed=embed
                        )

                        await self.send_application_to_review_channel(
                            message,
                            session
                        )

                        active_sessions.pop(
                            message.author.id,
                            None
                        )
                    else:
                        await session.ask_question()

                    return

            await self.bot.process_commands(
                message
            )
