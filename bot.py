from zerocore.app import ZeroCore
from zerocore.core.config import DISCORD_TOKEN

if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN belum diisi di .env")

ZeroCore().run(DISCORD_TOKEN)
