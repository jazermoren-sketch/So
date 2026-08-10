import discord

from application.storage import (
    load_answers,
    save_answers,
    load_config
)


class ResultManager:

    @staticmethod
    async def _get_member(
        interaction: discord.Interaction,
        user_id: int
    ):
        if interaction.guild is None:
            return None

        member = interaction.guild.get_member(user_id)

        if member is None:
            try:
                member = await interaction.guild.fetch_member(user_id)
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                return None

        return member

    @staticmethod
    async def _set_role(
        interaction: discord.Interaction,
        user_id: int,
        role_key: str,
        remove_role_key: str | None = None
    ):
        config = load_config()
        member = await ResultManager._get_member(interaction, user_id)

        if member is None:
            return None, "لم أتمكن من العثور على العضو داخل السيرفر."

        role_id = config.get(role_key)
        if not role_id:
            return member, None

        role = interaction.guild.get_role(role_id)

        if role is None:
            return member, "الرتبة المحددة غير موجودة أو تم حذفها."

        try:
            await member.add_roles(
                role,
                reason="Application result"
            )
        except discord.Forbidden:
            return member, "لا أملك صلاحية إعطاء هذه الرتبة، أو أن الرتبة أعلى من أعلى رتبة للبوت."
        except discord.HTTPException:
            return member, "حدث خطأ أثناء إعطاء الرتبة."

        if remove_role_key:
            old_role_id = config.get(remove_role_key)

            if old_role_id and old_role_id != role.id:
                old_role = interaction.guild.get_role(old_role_id)

                if old_role and old_role in member.roles:
                    try:
                        await member.remove_roles(
                            old_role,
                            reason="Application result"
                        )
                    except (discord.Forbidden, discord.HTTPException):
                        pass

        return member, None

    @staticmethod
    async def _finish_application(
        user_id: int,
        stage: str
    ):
        answers = load_answers()

        if str(user_id) in answers:
            answers[str(user_id)].pop(stage, None)

            if not answers[str(user_id)]:
                answers.pop(str(user_id))

            save_answers(answers)

    @staticmethod
    async def accept(
        interaction: discord.Interaction,
        user_id: int,
        stage: str,
        reason: str | None = None
    ):
        user = interaction.client.get_user(user_id)

        _, role_error = await ResultManager._set_role(
            interaction,
            user_id,
            "accepted_role",
            "rejected_role"
        )

        description = (
            f"تم قبولك في مرحلة **{stage}**.\n"
            "سيتم التواصل معك إذا كانت هناك مراحل أخرى."
        )

        if reason:
            description += f"\n\n📝 **سبب/ملاحظة الإدارة:**\n{reason}"

        if role_error:
            description += f"\n\n⚠️ **ملاحظة:** {role_error}"

        if user:
            embed = discord.Embed(
                title="🎉 تم قبول طلبك",
                description=description,
                color=discord.Color.green()
            )

            try:
                await user.send(embed=embed)
            except discord.Forbidden:
                pass

        await ResultManager._finish_application(user_id, stage)

    @staticmethod
    async def reject(
        interaction: discord.Interaction,
        user_id: int,
        stage: str,
        reason: str | None = None
    ):
        user = interaction.client.get_user(user_id)

        _, role_error = await ResultManager._set_role(
            interaction,
            user_id,
            "rejected_role",
            "accepted_role"
        )

        description = (
            f"تم رفض طلبك في مرحلة **{stage}**.\n"
            "يمكنك إعادة التقديم لاحقًا إذا سمحت الإدارة بذلك."
        )

        if reason:
            description += f"\n\n📝 **سبب الرفض:**\n{reason}"

        if role_error:
            description += f"\n\n⚠️ **ملاحظة:** {role_error}"

        if user:
            embed = discord.Embed(
                title="❌ تم رفض طلبك",
                description=description,
                color=discord.Color.red()
            )

            try:
                await user.send(embed=embed)
            except discord.Forbidden:
                pass

        await ResultManager._finish_application(user_id, stage)
