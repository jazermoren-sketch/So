import discord
from application.storage import load_answers, save_answers, load_config, save_application


class ResultManager:
    @staticmethod
    async def _get_member(interaction, user_id):
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
    async def _set_role(interaction, user_id, role_key, remove_role_key=None):
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
            await member.add_roles(role, reason="Application result")
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
                        await member.remove_roles(old_role, reason="Application result")
                    except (discord.Forbidden, discord.HTTPException):
                        pass
        return member, None

    @staticmethod
    async def _finish_application(user_id, stage, status, reason=None, moderator_id=None):
        old = load_answers()
        answers = old.get(str(user_id), {}).get(stage, [])
        # Keep the latest application metadata even after removing temporary answers.
        from application.storage import get_application
        previous = get_application(user_id) or {}
        save_application(user_id, {
            **previous,
            "status": status,
            "stage": stage,
            "reason": reason,
            "finished_by": moderator_id,
            "answered": len(answers),
        })
        if str(user_id) in old:
            old[str(user_id)].pop(stage, None)
            if not old[str(user_id)]:
                old.pop(str(user_id))
            save_answers(old)

    @staticmethod
    async def _notify_log(interaction, user_id, title, description, color):
        config = load_config()
        if not config.get("application_logs", True):
            return
        channel_id = config.get("review_channel")
        channel = interaction.guild.get_channel(channel_id) if interaction.guild and channel_id else None
        if channel:
            try:
                await channel.send(embed=discord.Embed(title=title, description=description, color=color))
            except discord.HTTPException:
                pass

    @staticmethod
    async def accept(interaction, user_id, stage, reason=None):
        user = interaction.client.get_user(user_id)
        _, role_error = await ResultManager._set_role(interaction, user_id, "accepted_role", "rejected_role")
        description = f"تم قبولك في مرحلة **{stage}**.\nسيتم التواصل معك إذا كانت هناك مراحل أخرى."
        if reason:
            description += f"\n\n📝 **ملاحظة الإدارة:**\n{reason}"
        if role_error:
            description += f"\n\n⚠️ **ملاحظة:** {role_error}"
        if user and load_config().get("application_dm_notifications", True):
            try:
                await user.send(embed=discord.Embed(title="🎉 تم قبول طلبك", description=description, color=discord.Color.green()))
            except discord.Forbidden:
                pass
        await ResultManager._finish_application(user_id, stage, "accepted", reason, interaction.user.id)
        await ResultManager._notify_log(interaction, user_id, "✅ تم قبول طلب التقديم", f"المتقدم: <@{user_id}>\nالمرحلة: **{stage}**\nبواسطة: {interaction.user.mention}", discord.Color.green())

    @staticmethod
    async def reject(interaction, user_id, stage, reason=None):
        user = interaction.client.get_user(user_id)
        _, role_error = await ResultManager._set_role(interaction, user_id, "rejected_role", "accepted_role")
        description = f"تم رفض طلبك في مرحلة **{stage}**.\nيمكنك إعادة التقديم لاحقًا إذا سمحت الإدارة بذلك."
        if reason:
            description += f"\n\n📝 **سبب الرفض:**\n{reason}"
        if role_error:
            description += f"\n\n⚠️ **ملاحظة:** {role_error}"
        if user and load_config().get("application_dm_notifications", True):
            try:
                await user.send(embed=discord.Embed(title="❌ تم رفض طلبك", description=description, color=discord.Color.red()))
            except discord.Forbidden:
                pass
        await ResultManager._finish_application(user_id, stage, "rejected", reason, interaction.user.id)
        await ResultManager._notify_log(interaction, user_id, "❌ تم رفض طلب التقديم", f"المتقدم: <@{user_id}>\nالمرحلة: **{stage}**\nبواسطة: {interaction.user.mention}", discord.Color.red())
