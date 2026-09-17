from __future__ import annotations
import os
from pathlib import Path
import yaml
from dotenv import load_dotenv

load_dotenv()
ROOT = Path(__file__).resolve().parents[2]

def read_yaml(relative: str) -> dict:
    with open(ROOT / relative, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

CONSTITUTION = read_yaml("config/constitution.yml")
SERVER = read_yaml("config/server.yml")
MESSAGES = read_yaml("config/messages.yml")

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
DISCORD_GUILD_ID = int(os.getenv("DISCORD_GUILD_ID", "0") or 0)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
DATABASE_PATH = ROOT / os.getenv("DATABASE_PATH", "data/district_zero.db")
BACKUP_DIR = ROOT / os.getenv("BACKUP_DIR", "backups")
