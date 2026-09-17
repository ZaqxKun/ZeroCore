from datetime import datetime
from zerocore.core.config import CONSTITUTION

class LifecycleService:
    def __init__(self,db,guild_service):
        self.db=db; self.gs=guild_service

    async def review_due_trials(self,guild):
        cfg=CONSTITUTION["channel_lifecycle"]["trial_keep"]
        due=await self.db.due_trials()
        outcomes=[]
        for t in due:
            ch=guild.get_channel(int(t["channel_id"]))
            if not ch:
                await self.db.set_trial_state(t["channel_id"],"missing")
                continue

            after=datetime.fromisoformat(t["created_at"])
            messages=[]; authors=set(); days=set()
            async for m in ch.history(limit=1000,after=after):
                if m.author.bot: continue
                messages.append(m); authors.add(m.author.id); days.add(m.created_at.date())

            keep=(len(authors)>=cfg["minimum_unique_users"]
                  and len(messages)>=cfg["minimum_messages"]
                  and len(days)>=cfg["minimum_active_days"])

            if keep:
                await ch.edit(topic=((ch.topic or "").replace("TRIAL","ESTABLISHED"))[:1024],
                              reason="ZeroCore trial passed")
                await self.db.set_trial_state(ch.id,"kept")
                await self.gs.audit(guild,"ZeroCore • Trial kept",
                  f"#{ch.name}: {len(authors)} pengguna unik, {len(messages)} pesan, {len(days)} hari aktif.")
                outcomes.append((ch.name,"kept"))
            else:
                ow=ch.overwrites_for(guild.default_role)
                ow.send_messages=False
                await ch.set_permissions(guild.default_role,overwrite=ow,reason="ZeroCore archive trial")
                await ch.edit(name=("archive-"+ch.name)[:100],
                              reason="ZeroCore trial did not meet keep threshold")
                await self.db.set_trial_state(ch.id,"archived")
                await self.gs.audit(guild,"ZeroCore • Trial archived",
                  f"#{ch.name}: tidak memenuhi threshold. Channel tidak dihapus.")
                outcomes.append((ch.name,"archived"))
        return outcomes
