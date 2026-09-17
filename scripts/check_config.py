import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from zerocore.core.config import CONSTITUTION, SERVER
assert CONSTITUTION["identity"]["name"]=="District Zerø"
assert CONSTITUTION["autonomy"]["permanently_forbidden"]
assert CONSTITUTION["social"]["frequency_never_creates_channel"] is True
assert CONSTITUTION["channel_lifecycle"]["delete_automatically"] is False
assert all(r["name"] for r in SERVER["roles"])
print("Configuration check: OK")
