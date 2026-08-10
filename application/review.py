import discord

from application.storage import (
    load_answers,
    load_config
)


class ReviewManager:

    @staticmethod
    def create_review_embed(bot, user_id, stage):

        answers = load_answers()

        if str(user_id) not in answers:
            return None

        if stage not in answers[str(user_id)]:
            return None

        member = bot.get_user(user_id)

        embed = discord.Embed(
            title="📝 مراجعة الاختبار",
            color=0x3498DB
        )

        if member:

            embed.add_field(
                name="👤 المتقدم",
                value=member.mention,
                inline=False
            )

        embed.add_field(
            name="📋 المرحلة",
            value=stage,
            inline=False
        )

        questions = answers[str(user_id)][stage]

        for index, answer in enumerate(
            questions,
            start=1
        ):

            embed.add_field(
                name=f"السؤال {index}",
                value=answer,
                inline=False
            )

        embed.set_footer(
            text=f"User ID: {user_id}"
        )

        return embed

    @staticmethod
    def get_reviewer(bot):

        config = load_config()

        reviewer = config.get("reviewer")

        if reviewer is None:
            return None

        return bot.get_user(reviewer)