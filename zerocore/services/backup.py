from __future__ import annotations
import json, zipfile
from datetime import datetime, timezone
from zerocore.core.config import BACKUP_DIR, ROOT, CONSTITUTION

def overwrite_to_dict(ow):
    allow,deny=ow.pair()
    return {"allow":allow.value,"deny":deny.value}

class BackupService:
    async def create(self,guild):
        BACKUP_DIR.mkdir(parents=True,exist_ok=True)
        stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base=BACKUP_DIR/f"district-zero-{stamp}"
        snapshot={
          "generated_at":datetime.now(timezone.utc).isoformat(),
          "guild":{"id":guild.id,"name":guild.name},
          "roles":[{
            "id":r.id,"name":r.name,"position":r.position,
            "permissions":r.permissions.value,"managed":r.managed
          } for r in guild.roles],
          "channels":[{
            "id":c.id,"name":c.name,"type":str(c.type),"position":c.position,
            "category":getattr(c.category,"name",None),
            "topic":getattr(c,"topic",None),
            "overwrites":{
              str(target.id):overwrite_to_dict(ow)
              for target,ow in c.overwrites.items()
            }
          } for c in guild.channels],
        }
        json_path=base.with_suffix(".json")
        json_path.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2),encoding="utf-8")
        zip_path=base.with_suffix(".zip")
        with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as z:
            z.write(json_path,json_path.name)
            for rel in ["config/constitution.yml","config/server.yml","config/messages.yml"]:
                z.write(ROOT/rel,rel)
        json_path.unlink(missing_ok=True)
        self._rotate()
        return zip_path

    def _rotate(self):
        keep=CONSTITUTION["backup"]["keep_last"]
        backups=sorted(BACKUP_DIR.glob("district-zero-*.zip"),key=lambda p:p.stat().st_mtime,reverse=True)
        for old in backups[keep:]:
            old.unlink(missing_ok=True)
