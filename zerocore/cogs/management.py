import discord
from discord import app_commands
from discord.ext import commands

class Management(commands.Cog):
    def __init__(self,bot,ctx):
        self.bot=bot; self.ctx=ctx

    @app_commands.command(name="setup",description="Bangun/repair blueprint inti District Zerø.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setup(self,interaction:discord.Interaction):
        await interaction.response.defer(ephemeral=True,thinking=True)
        guild = interaction.guild
        me = guild.me
        if me is None:
          await interaction.followup.send(
              "Data role bot belum tersedia. Coba jalankan command lagi.",
              ephemeral=True)
          return

        required = {
          "manage_roles": "Manage Roles",
          "manage_channels": "Manage Channels",
          "view_channel": "View Channels",
          "send_messages": "Send Messages",
          "read_message_history": "Read Message History",
        }
        missing = [label for permission, label in required.items()
                 if not getattr(me.guild_permissions, permission)]
        if missing:
          await interaction.followup.send(
              "Permission bot kurang: " + ", ".join(missing) + ".",
              ephemeral=True)
          return

        if me.top_role.is_default():
          await interaction.followup.send(
              "Role bot belum dibuat atau belum memiliki posisi yang valid.",
              ephemeral=True)
          return

        try:
          await self.ctx.guild.ensure_blueprint(guild)
        except discord.Forbidden:
          await interaction.followup.send(
              "Discord menolak perubahan. Pastikan role ZeroCore berada di "
              "atas role yang ingin dibuat/dikelola.",
              ephemeral=True)
          return
        except discord.HTTPException as error:
          await interaction.followup.send(
              f"Discord API gagal saat setup (HTTP {error.status}). "
              "Periksa permission dan coba lagi.",
              ephemeral=True)
          return
        await interaction.followup.send(
          "Blueprint inti sudah dicek dan diperbaiki. ZeroCore tidak membuat Administrator.",
          ephemeral=True)

    @app_commands.command(name="review-now",description="Jalankan review komunitas sekarang.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def review_now(self,interaction:discord.Interaction):
        await interaction.response.defer(ephemeral=True,thinking=True)
        out=await self.ctx.run_review(interaction.guild)
        await interaction.followup.send(out,ephemeral=True)

    @app_commands.command(name="backup",description="Buat snapshot konfigurasi server sekarang.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def backup(self,interaction:discord.Interaction):
        await interaction.response.defer(ephemeral=True,thinking=True)
        path=await self.ctx.backup.create(interaction.guild)
        await interaction.followup.send(f"Backup dibuat: `{path.name}`",ephemeral=True)

    @app_commands.command(name="heartbeat",description="Catat bahwa founder/owner aktif.")
    async def heartbeat(self,interaction:discord.Interaction):
        if interaction.guild.owner_id != interaction.user.id:
            await interaction.response.send_message("Command ini khusus server owner.",ephemeral=True)
            return
        await self.ctx.db.set_heartbeat("owner-command")
        await interaction.response.send_message("Heartbeat founder diperbarui.",ephemeral=True)

    @app_commands.command(name="status",description="Status ZeroCore.")
    async def status(self,interaction:discord.Interaction):
        from zerocore.core.config import CONSTITUTION
        c=CONSTITUTION
        await interaction.response.send_message(
          "**ZeroCore ONLINE**\n"
          f"Mode: `{c['autonomy']['mode']}`\n"
          f"Review: `{c['analysis']['interval_hours']}h`\n"
          f"Trial: `{c['channel_lifecycle']['trial_days']} hari`\n"
          "Ajakan sosial: `#general`\n"
          f"AI ban: `{c['moderation']['ai_can_ban']}`\n"
          f"AI timeout: `{c['moderation']['ai_can_timeout']}`\n"
          f"Auto-delete channel: `{c['channel_lifecycle']['delete_automatically']}`",
          ephemeral=True)

async def setup(bot,ctx):
    await bot.add_cog(Management(bot,ctx))
