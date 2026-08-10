import discord

from application.storage import (
    load_answers,
    save_answers
)


class ResultManager:

    @staticmethod
    async def accept(
        interaction: discord.Interaction,
        user_id: int,
        stage: str
    ):

        user = interaction.client.get_user(user_id)

        if user:

            embed = discord.Embed(
                title="🎉 تم قبول طلبك",
                description=(
                    f"تم قبولك في مرحلة **{stage}**.\n"
                    "سيتم التواصل معك إذا كانت هناك مراحل أخرى."
                ),
                color=discord.Color.green()
            )

            try:
                await user.send(embed=embed)
            except discord.Forbidden:
                pass

        answers = load_answers()

        if str(user_id) in answers:

            answers[str(user_id)].pop(stage, None)

            if not answers[str(user_id)]:
                answers.pop(str(user_id))

            save_answers(answers)

    @staticmethod
    async def reject(
        interaction: discord.Interaction,
        user_id: int,
        stage: str
    ):

        user = interaction.client.get_user(user_id)

        if user:

            embed = discord.Embed(
                title="❌ تم رفض طلبك",
                description=(
                    f"تم رفض طلبك في مرحلة **{stage}**.\n"
                    "يمكنك إعادة التقديم لاحقًا إذا سمحت الإدارة بذلك."
                ),
                color=discord.Color.red()
            )

            try:
                await user.send(embed=embed)
            except discord.Forbidden:
                pass

        answers = load_answers()

        if str(user_id) in answers:

            answers[str(user_id)].pop(stage, None)

            if not answers[str(user_id)]:
                answers.pop(str(user_id))

            save_answers(answers)