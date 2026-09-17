from __future__ import annotations
from types import SimpleNamespace
import discord
from discord.ext import commands, tasks

from zerocore.core.config import CONSTITUTION, DISCORD_GUILD_ID
from zerocore.core.database import Database
from zerocore.core.policy import PolicyEngine
from zerocore.services.ai import AIService
from zerocore.services.guild import GuildService
from zerocore.services.backup import BackupService
from zerocore.services.lifecycle import LifecycleService
from zerocore.services.continuity import ContinuityService

class ZeroCore(commands.Bot):
    def __init__(self):
        intents=discord.Intents.default()
        intents.guilds=True
        intents.message_content=True
        super().__init__(command_prefix="!",intents=intents)

        self.db=Database()
        self.ai=AIService()
        self.policy=PolicyEngine(self.db)
        self.guild_service=GuildService(self,self.db)
        self.backup_service=BackupService()
        self.lifecycle=LifecycleService(self.db,self.guild_service)
        self.continuity=ContinuityService(self.db,self.guild_service)

        self.ctx=SimpleNamespace(
          db=self.db,
          guild=self.guild_service,
          backup=self.backup_service,
          lifecycle=self.lifecycle,
          continuity=self.continuity,
          run_review=self.run_review,
        )

    def target_guild(self):
        return self.get_guild(DISCORD_GUILD_ID) if DISCORD_GUILD_ID else None

    async def setup_hook(self):
        await self.db.init()
        from zerocore.cogs.management import setup as setup_management
        await setup_management(self,self.ctx)
        if DISCORD_GUILD_ID:
            obj=discord.Object(id=DISCORD_GUILD_ID)
            self.tree.copy_global_to(guild=obj)
            await self.tree.sync(guild=obj)

    async def on_ready(self):
        if not self.review_loop.is_running(): self.review_loop.start()
        if not self.self_heal_loop.is_running(): self.self_heal_loop.start()
        if not self.backup_loop.is_running(): self.backup_loop.start()
        if not self.lifecycle_loop.is_running(): self.lifecycle_loop.start()
        if not self.privacy_loop.is_running(): self.privacy_loop.start()
        if not self.continuity_loop.is_running(): self.continuity_loop.start()
        print(f"ZeroCore online as {self.user}")

    async def on_message(self,message):
        if message.author.bot or not message.guild:return
        if getattr(message.channel,"name","") not in {"zero-log","mod-queue","continuity-room"}:
            await self.db.add_message(message)
        await self.process_commands(message)

    async def run_review(self,guild):
        cfg=CONSTITUTION["analysis"]
        rows=await self.db.recent_messages(
          cfg["lookback_days"],cfg["max_messages_per_review"],
          excluded_channels={"zero-log","mod-queue","continuity-room"})
        if len(rows)<cfg["minimum_messages_before_ai_review"]:
            return f"Belum cukup data: {len(rows)} pesan."

        review=await self.ai.review(rows,{c.name for c in guild.channels})
        if not review:return "Gemini API belum dikonfigurasi."

        applied=0
        for d in review.decisions[:10]:
            result=await self.policy.validate(d)
            await self.db.log_action("community_decision",d.normalized_topic,result.reason,{
              "ai_action":d.action.value,"effective_action":result.action.value,
              "allowed":result.allowed,"confidence":d.confidence,"structural_need":d.structural_need})
            if result.allowed:
                await self.guild_service.apply(guild,d,result.action)
                applied+=1

        await self.guild_service.audit(
          guild,"ZeroCore • Community review",
          f"{review.health_summary}\nKeputusan: {len(review.decisions)} • tindakan: {applied}")
        return f"Review selesai: {len(review.decisions)} keputusan, {applied} tindakan."

    @tasks.loop(hours=12)
    async def review_loop(self):
        g=self.target_guild()
        if g:
            try: await self.run_review(g)
            except Exception as e: print("review_loop:",repr(e))

    @tasks.loop(hours=6)
    async def self_heal_loop(self):
        g=self.target_guild()
        if g and CONSTITUTION["self_healing"]["enabled"]:
            try: await self.guild_service.ensure_blueprint(g)
            except Exception as e: print("self_heal_loop:",repr(e))

    @tasks.loop(hours=24)
    async def backup_loop(self):
        g=self.target_guild()
        if g and CONSTITUTION["backup"]["enabled"]:
            try: await self.backup_service.create(g)
            except Exception as e: print("backup_loop:",repr(e))

    @tasks.loop(hours=6)
    async def lifecycle_loop(self):
        g=self.target_guild()
        if g:
            try: await self.lifecycle.review_due_trials(g)
            except Exception as e: print("lifecycle_loop:",repr(e))

    @tasks.loop(hours=24)
    async def privacy_loop(self):
        try: await self.db.purge_old_messages(CONSTITUTION["privacy"]["raw_message_retention_days"])
        except Exception as e: print("privacy_loop:",repr(e))

    @tasks.loop(hours=24)
    async def continuity_loop(self):
        g=self.target_guild()
        if g:
            try: await self.continuity.check(g)
            except Exception as e: print("continuity_loop:",repr(e))

    @review_loop.before_loop
    @self_heal_loop.before_loop
    @backup_loop.before_loop
    @lifecycle_loop.before_loop
    @privacy_loop.before_loop
    @continuity_loop.before_loop
    async def before_loops(self):
        await self.wait_until_ready()
