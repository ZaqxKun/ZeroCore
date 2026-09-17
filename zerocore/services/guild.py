from __future__ import annotations
import re
from datetime import datetime, timedelta, timezone
import discord
from zerocore.core.config import CONSTITUTION, SERVER, MESSAGES

def slugify(s):
    s=s.lower().strip()
    s=re.sub(r"[^a-z0-9 -]+","",s)
    s=re.sub(r"[\s_]+","-",s)
    return re.sub(r"-+","-",s).strip("-")[:90] or "community-topic"

def role_permissions(mapping):
    p=discord.Permissions.none()
    allowed={k:v for k,v in mapping.items() if hasattr(p,k)}
    p.update(**allowed)
    p.administrator=False
    return p

class GuildService:
    def __init__(self,bot,db):
        self.bot=bot; self.db=db

    def text(self,guild,name):
        return discord.utils.get(guild.text_channels,name=name)

    async def audit(self,guild,title,description):
        ch=self.text(guild,CONSTITUTION["logging"]["channel"])
        if ch:
            e=discord.Embed(title=title,description=description,timestamp=datetime.now(timezone.utc))
            await ch.send(embed=e)

    async def ensure_role(self,guild,spec):
        role=discord.utils.get(guild.roles,name=spec["name"])
        if role: return role
        return await guild.create_role(
            name=spec["name"],permissions=role_permissions(spec.get("permissions",{})),
            reason="ZeroCore self-healing/setup"
        )

    async def ensure_blueprint(self,guild):
        roles={}
        for rs in SERVER["roles"]:
            roles[rs["name"]]=await self.ensure_role(guild,rs)

        for cs in SERVER["categories"]:
            cat=discord.utils.get(guild.categories,name=cs["name"])
            overwrites={}
            if cs.get("private"):
                overwrites={
                  guild.default_role:discord.PermissionOverwrite(view_channel=False),
                  roles["Admin"]:discord.PermissionOverwrite(view_channel=True),
                  roles["Moderator"]:discord.PermissionOverwrite(view_channel=True),
                }
            if not cat:
                cat=await guild.create_category(cs["name"],overwrites=overwrites,reason="ZeroCore setup")
            elif cs.get("private") and CONSTITUTION["self_healing"]["repair_private_system_category_visibility"]:
                await cat.edit(overwrites=overwrites,reason="ZeroCore permission repair")

            for ch in cs["channels"]:
                name=ch["name"]; t=ch["type"]
                if t=="text" and not discord.utils.get(guild.text_channels,name=name):
                    await guild.create_text_channel(name,category=cat,reason="ZeroCore setup/self-heal")
                elif t=="forum" and not discord.utils.get(guild.forums,name=name):
                    await guild.create_forum(name,category=cat,reason="ZeroCore setup/self-heal")
                elif t=="voice" and not discord.utils.get(guild.voice_channels,name=name):
                    await guild.create_voice_channel(name,category=cat,reason="ZeroCore setup/self-heal")
        await self.seed_core_messages(guild)

    async def seed_core_messages(self,guild):
        welcome=self.text(guild,"welcome")
        if welcome and not [m async for m in welcome.history(limit=1)]:
            await welcome.send(embed=discord.Embed(
              title=MESSAGES["welcome"]["title"],description=MESSAGES["welcome"]["body"]))
        rules=self.text(guild,"rules")
        if rules and not [m async for m in rules.history(limit=1)]:
            text="\n".join(f"{i+1}. {r}" for i,r in enumerate(MESSAGES["rules"]))
            await rules.send(embed=discord.Embed(title="District Zerø — Rules",description=text))

    async def create_trial(self,guild,d):
        name=slugify(d.suggested_channel_name or d.normalized_topic)
        existing=discord.utils.get(guild.channels,name=name)
        if existing:return existing
        cat=discord.utils.get(guild.categories,name="ACTIVITIES")
        days=CONSTITUTION["channel_lifecycle"]["trial_days"]
        ch=await guild.create_text_channel(
          name,category=cat,
          topic=(f"TRIAL {days} hari • {d.suggested_channel_topic or d.summary}")[:1024],
          reason=f"ZeroCore reversible trial: {d.reason[:300]}"
        )
        review_at=datetime.now(timezone.utc)+timedelta(days=days)
        await self.db.add_trial(ch.id,ch.name,d.normalized_topic,review_at)
        await self.db.touch_topic(d.normalized_topic)
        await ch.send(
          f"**Trial Space — {days} hari**\n"
          "Ruang ini eksperimen. Aktivitas ditinjau otomatis; jika tidak membantu, ruang diarsipkan, bukan dihapus.")
        await self.audit(guild,"ZeroCore • Trial created",
          f"#{name}\nAlasan: {d.reason}\nConfidence {d.confidence:.0%} • Structural need {d.structural_need:.0%}")
        return ch

    async def create_thread(self,guild,d):
        general=self.text(guild,"general")
        if not general:return
        msg=await general.send(
          f"Topik **{d.topic}** sedang cukup padat. ZeroCore membuat thread sementara agar #general tetap mengalir.")
        th=await msg.create_thread(
          name=(d.suggested_channel_name or d.topic)[:90],
          auto_archive_duration=1440,
          reason=f"ZeroCore lightweight organization: {d.reason[:300]}")
        await self.db.log_action("create_thread",th.name,d.reason)

    async def proposal(self,guild,d):
        forum=discord.utils.get(guild.forums,name=CONSTITUTION["suggestions"]["forum"])
        body=(
          f"**Masalah/observasi**\n{d.summary}\n\n"
          f"**Analisis ZeroCore**\n{d.reason}\n\n"
          f"Confidence: {d.confidence:.0%}\nStructural need: {d.structural_need:.0%}\n\n"
          "Diskusikan di bawah. Ini belum menjadi perubahan permanen.")
        if forum:
            await forum.create_thread(name=f"Proposal: {d.topic}"[:100],content=body,reason="ZeroCore proposal")
        else:
            ch=self.text(guild,"saran-kritik")
            if ch: await ch.send(embed=discord.Embed(title=f"Proposal: {d.topic}",description=body))

    async def apply(self,guild,d,action):
        from zerocore.core.models import Action
        if action==Action.create_trial_channel:return await self.create_trial(guild,d)
        if action==Action.create_thread:return await self.create_thread(guild,d)
        if action==Action.propose_trial_channel:return await self.proposal(guild,d)
