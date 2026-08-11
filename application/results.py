import time
import discord
from application.storage import load_answers, save_answers, load_config, save_application, get_application
from application.appeals import AppealView
from application.audit import log

class ResultManager:
    @staticmethod
    async def _get_member(interaction,user_id):
        if interaction.guild is None: return None
        member=interaction.guild.get_member(user_id)
        if member is None:
            try: member=await interaction.guild.fetch_member(user_id)
            except (discord.NotFound,discord.Forbidden,discord.HTTPException): return None
        return member
    @staticmethod
    async def _set_role(interaction,user_id,role_key,remove_role_key=None):
        config=load_config(interaction.guild.id); member=await ResultManager._get_member(interaction,user_id)
        if member is None: return None,"لم أتمكن من العثور على العضو داخل السيرفر."
        role_id=config.get(role_key)
        if not role_id: return member,None
        role=interaction.guild.get_role(role_id)
        if role is None: return member,"الرتبة المحددة غير موجودة أو تم حذفها."
        try: await member.add_roles(role,reason="Application result")
        except discord.Forbidden: return member,"لا أملك صلاحية إعطاء هذه الرتبة."
        except discord.HTTPException: return member,"حدث خطأ أثناء إعطاء الرتبة."
        if remove_role_key:
            old_id=config.get(remove_role_key); old=interaction.guild.get_role(old_id) if old_id else None
            if old and old.id!=role.id and old in member.roles:
                try: await member.remove_roles(old,reason="Application result")
                except (discord.Forbidden,discord.HTTPException): pass
        return member,None
    @staticmethod
    async def _apply_score_role(interaction,user_id,score):
        if score is None or not interaction.guild: return None
        config=load_config(interaction.guild.id); rules=config.get("auto_roles_by_score",[]) or []
        if not rules: return None
        member=await ResultManager._get_member(interaction,user_id)
        if not member: return None
        selected=None; best=-1
        for rule in rules:
            try: minimum=float(rule.get("min",0)); role_id=int(rule.get("role_id"))
            except (TypeError,ValueError,AttributeError): continue
            if float(score)>=minimum and minimum>=best: selected=role_id; best=minimum
        if selected:
            role=interaction.guild.get_role(selected)
            if role:
                try: await member.add_roles(role,reason="Application score role")
                except (discord.Forbidden,discord.HTTPException): pass
        return selected
    @staticmethod
    async def _finish_application(interaction,user_id,stage,status,reason=None,moderator_id=None,score=None):
        old=load_answers(interaction.guild.id); answers=old.get(str(user_id),{}).get(stage,[]); previous=get_application(interaction.guild.id,user_id) or {}
        attempt=previous.get("attempt",1); finished=time.time()
        snapshot={"attempt":attempt,"status":status,"stage":stage,"reason":reason,"finished_by":moderator_id,"answered":len(answers),"score":score,"finished_at":finished}
        history=list(previous.get("applications_history",[])); history.append(snapshot)
        save_application(interaction.guild.id,user_id,{**previous,**snapshot,"applications_history":history[-20:],"locked_by":None,"locked_at":None,"assigned_reviewer":previous.get("assigned_reviewer")})
        log(interaction.guild.id,user_id,"application_finished",moderator_id,{"status":status,"stage":stage,"score":score,"reason":reason})
        if str(user_id) in old:
            old[str(user_id)].pop(stage,None)
            if not old[str(user_id)]: old.pop(str(user_id))
            save_answers(interaction.guild.id,old)
    @staticmethod
    async def _notify_log(interaction,user_id,title,description,color):
        config=load_config(interaction.guild.id)
        if not config.get("application_logs",True): return
        channel_id=config.get("review_channel"); channel=interaction.guild.get_channel(channel_id) if interaction.guild and channel_id else None
        if channel:
            try: await channel.send(embed=discord.Embed(title=title,description=description,color=color))
            except discord.HTTPException: pass
    @staticmethod
    async def _send_result_channel(interaction,user_id,status,stage,reason,score):
        config=load_config(interaction.guild.id); channel_id=config.get("result_channel"); channel=interaction.guild.get_channel(channel_id) if interaction.guild and channel_id else None
        if not channel: return
        label="مقبول" if status=="accepted" else "مرفوض"; embed=discord.Embed(title="📋 نتيجة التقديم",color=discord.Color.green() if status=="accepted" else discord.Color.red())
        embed.add_field(name="👤 المتقدم",value=f"<@{user_id}>",inline=True); embed.add_field(name="📌 النتيجة",value=f"{'✅' if status=='accepted' else '❌'} {label}",inline=True); embed.add_field(name="📊 التقييم",value=str(score) if score is not None else "غير محدد",inline=True); embed.add_field(name="👮 المراجع",value=interaction.user.mention,inline=True)
        if reason: embed.add_field(name="📝 الملاحظات",value=reason[:1024],inline=False)
        await channel.send(embed=embed)
    @staticmethod
    async def accept(interaction,user_id,stage,reason=None,score=None):
        user=interaction.client.get_user(user_id); _,role_error=await ResultManager._set_role(interaction,user_id,"accepted_role","rejected_role"); await ResultManager._apply_score_role(interaction,user_id,score)
        description=f"تم قبولك في مرحلة **{stage}**."
        if reason: description+=f"\n\n📝 **ملاحظة الإدارة:**\n{reason}"
        if score is not None: description+=f"\n\n⭐ **التقييم:** {score}"
        if role_error: description+=f"\n\n⚠️ **ملاحظة:** {role_error}"
        if user and load_config(interaction.guild.id).get("application_dm_notifications",True):
            try: await user.send(embed=discord.Embed(title="🎉 تم قبول طلبك",description=description,color=discord.Color.green()))
            except discord.Forbidden: pass
        await ResultManager._finish_application(interaction,user_id,stage,"accepted",reason,interaction.user.id,score); await ResultManager._send_result_channel(interaction,user_id,"accepted",stage,reason,score); await ResultManager._notify_log(interaction,user_id,"✅ تم قبول طلب التقديم",f"المتقدم: <@{user_id}>\nالمرحلة: **{stage}**\nبواسطة: {interaction.user.mention}",discord.Color.green())
    @staticmethod
    async def reject(interaction,user_id,stage,reason=None,score=None):
        user=interaction.client.get_user(user_id); _,role_error=await ResultManager._set_role(interaction,user_id,"rejected_role","accepted_role")
        description=f"تم رفض طلبك في مرحلة **{stage}**.\nيمكنك الاعتراض إذا كانت الإدارة مفعلة لنظام الاعتراضات."
        if reason: description+=f"\n\n📝 **سبب الرفض:**\n{reason}"
        if score is not None: description+=f"\n\n⭐ **التقييم:** {score}"
        if role_error: description+=f"\n\n⚠️ **ملاحظة:** {role_error}"
        if user and load_config(interaction.guild.id).get("application_dm_notifications",True):
            try:
                cfg=load_config(interaction.guild.id); view=AppealView(user_id,interaction.guild.id) if cfg.get("appeals_enabled",True) and cfg.get("appeal_channel") else None
                await user.send(embed=discord.Embed(title="❌ تم رفض طلبك",description=description,color=discord.Color.red()),view=view)
            except discord.Forbidden: pass
        await ResultManager._finish_application(interaction,user_id,stage,"rejected",reason,interaction.user.id,score); await ResultManager._send_result_channel(interaction,user_id,"rejected",stage,reason,score); await ResultManager._notify_log(interaction,user_id,"❌ تم رفض طلب التقديم",f"المتقدم: <@{user_id}>\nالمرحلة: **{stage}**\nبواسطة: {interaction.user.mention}",discord.Color.red())
