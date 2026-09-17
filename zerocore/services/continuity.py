from datetime import datetime, timezone
from zerocore.core.config import CONSTITUTION, MESSAGES

class ContinuityService:
    def __init__(self,db,guild_service):
        self.db=db; self.gs=guild_service

    async def check(self,guild):
        cfg=CONSTITUTION["continuity"]
        if not cfg["enabled"]: return "disabled"
        hb=await self.db.get_heartbeat()
        if not hb: return "no-heartbeat"

        last,_=hb
        days=(datetime.now(timezone.utc)-last).days
        if days>=cfg["heartbeat_days_emergency"]: level="EMERGENCY"
        elif days>=cfg["heartbeat_days_continuity"]: level="CONTINUITY"
        elif days>=cfg["heartbeat_days_warning"]: level="WARNING"
        else: return "active"

        ch=self.gs.text(guild,cfg["continuity_channel"])
        await self.db.log_action("continuity_check",level,f"Founder heartbeat {days} hari lalu",{"days":days})
        if ch:
            mention=[]
            if level in {"CONTINUITY","EMERGENCY"}:
                for k in ["primary_successor_user_id","secondary_successor_user_id"]:
                    uid=cfg.get(k,0)
                    if uid: mention.append(f"<@{uid}>")
            if level=="EMERGENCY":
                uid=cfg.get("emergency_successor_user_id",0)
                if uid: mention.append(f"<@{uid}>")
            await ch.send(
              f"**ZEROCORE CONTINUITY — {level}**\n"
              f"Heartbeat founder terakhir: **{days} hari lalu**.\n"
              f"{' '.join(mention)}\n\n{MESSAGES['continuity_notice']}")
        return level
